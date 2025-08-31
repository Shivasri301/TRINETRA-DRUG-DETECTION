import os
import asyncio
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from telethon.errors import PhoneCodeInvalidError, SessionPasswordNeededError
from database import db
from telegram_monitor import monitor
from async_helper import telegram_helper
from simple_auth import simple_auth
from bson import ObjectId
from datetime import datetime
import json
import glob
import tempfile

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# Configure for cloud deployment
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            api_id_str = request.form.get('api_id', '')
            api_hash = request.form.get('api_hash', '').strip()
            
            # Validate inputs
            if not username or not password or not api_id_str or not api_hash:
                flash('All fields are required!', 'error')
                return render_template('register.html')
            
            # Validate API ID is numeric
            try:
                api_id = int(api_id_str)
                if api_id <= 0:
                    raise ValueError("API ID must be positive")
            except ValueError:
                flash('API ID must be a valid positive number!', 'error')
                return render_template('register.html')
            
            # Validate username format
            if len(username) < 3 or len(username) > 50:
                flash('Username must be between 3 and 50 characters!', 'error')
                return render_template('register.html')
            
            # Validate password strength
            if len(password) < 6:
                flash('Password must be at least 6 characters long!', 'error')
                return render_template('register.html')
            
            # Create user
            success, message = db.create_user(username, password, api_id, api_hash)
            
            if success:
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash(message, 'error')
                
        except Exception as e:
            print(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        success, user = db.verify_user(username, password)
        
        if success:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear Telegram authentication for this user
    if 'username' in session:
        username = session['username']
        
        print(f"DEBUG: Logging out user {username}")
        
        # Reset telegram_linked status in database
        result = db.users.update_one(
            {"username": username},
            {"$set": {"telegram_linked": False, "phone_number": None}}
        )
        print(f"DEBUG: Database update result: {result.modified_count} documents modified")
        
        # Clean up session files with absolute paths
        current_dir = os.getcwd()
        session_patterns = [
            f"temp_{username}.session",
            f"auth_{username}.session", 
            f"monitor_session_{username}.session",
            f"real_session_{username}.session",
            "authenticated_session.session"  # Also remove the main auth session
        ]
        
        files_removed = 0
        for pattern in session_patterns:
            # Check in current directory
            full_path = os.path.join(current_dir, pattern)
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                    print(f"🗑️ Removed session file: {full_path}")
                    files_removed += 1
                except Exception as e:
                    print(f"❌ Failed to remove {full_path}: {e}")
            
            # Also check with glob for any other matches
            for session_file in glob.glob(pattern):
                try:
                    os.remove(session_file)
                    print(f"🗑️ Removed session file: {session_file}")
                    files_removed += 1
                except Exception as e:
                    print(f"❌ Failed to remove {session_file}: {e}")
        
        print(f"🔐 Cleared Telegram authentication for user: {username} (removed {files_removed} session files)")
    
    session.clear()
    flash('Logged out successfully! You will need to re-authenticate with Telegram on next login.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = db.get_user_by_username(username)
    
    if not user:
        flash('User not found. Please login again.', 'error')
        return redirect(url_for('login'))
    
    print(f"DEBUG: User {username} telegram_linked status: {user.get('telegram_linked', False)}")
    
    # FORCE authentication check if not linked
    if not user.get('telegram_linked', False):
        print(f"DEBUG: User {username} is NOT telegram linked, forcing authentication")
        flash('You must authenticate your Telegram account to access the dashboard.', 'warning')
        return redirect(url_for('link_telegram'))
    
    print(f"DEBUG: User {username} is telegram linked, loading dashboard")
    
    channels = db.get_user_channels(username)
    alerts = db.get_alerts(username)
    
    # Add suspicious count to each channel
    for channel in channels:
        suspicious_results = db.get_monitoring_results(str(channel['_id']))
        channel['suspicious_count'] = sum(1 for r in suspicious_results if r.get('prediction') == 'drug sale')
    
    return render_template('dashboard.html', user=user, channels=channels, alerts=alerts)

@app.route('/link_telegram', methods=['GET', 'POST'])
def link_telegram():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = db.get_user_by_username(username)
    
    if request.method == 'POST':
        if 'resend' in request.form:
            # Reset OTP session
            session.pop('otp_sent', None)
            session.pop('phone_number', None)
            session.pop('temp_client', None)
            return redirect(url_for('link_telegram'))
        
        if 'otp_code' in request.form:
            # Verify OTP
            otp_code = request.form['otp_code']
            phone_number = request.form['phone_number']
            
            success, message = telegram_helper.verify_otp(username, phone_number, otp_code)
            
            if success:
                # Update database
                db.update_telegram_link(username, phone_number)
                
                # Clean up session
                session.pop('otp_sent', None)
                session.pop('phone_number', None)
                
                flash('Telegram account linked successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash(message, 'error')
        
        else:
            # Send OTP
            phone_number = request.form['phone_number']
            
            success, message = telegram_helper.send_otp(
                user['api_id'], 
                user['api_hash'], 
                phone_number, 
                username
            )
            
            if success:
                session['otp_sent'] = True
                session['phone_number'] = phone_number
                flash('OTP sent to your Telegram account!', 'success')
            else:
                flash(f'Error sending OTP: {message}', 'error')
    
    return render_template('link_telegram.html')

@app.route('/add_channel', methods=['POST'])
def add_channel():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = db.get_user_by_username(username)
    
    if not user:
        flash('User not found. Please login again.', 'error')
        return redirect(url_for('login'))
    
    try:
        channel_link = request.form.get('channel_link', '').strip()
        
        # Validate channel link format
        if not channel_link:
            flash('Channel link is required!', 'error')
            return redirect(url_for('dashboard'))
        
        if not channel_link.startswith('https://t.me/'):
            flash('Invalid Telegram channel link! Must start with https://t.me/', 'error')
            return redirect(url_for('dashboard'))
        
        # Validate channel link has actual channel name
        channel_name = channel_link.split('/')[-1]
        if not channel_name or len(channel_name) < 2:
            flash('Invalid channel link! Channel name too short.', 'error')
            return redirect(url_for('dashboard'))
        
        # Check if user has Telegram linked
        if not user.get('telegram_linked', False):
            flash('Please link your Telegram account first!', 'warning')
            return redirect(url_for('link_telegram'))
        
        # Add channel to database
        channel_id = db.add_channel(username, channel_link, channel_name)
        flash('Channel added successfully! Click "Monitor" to start analysis.', 'success')
        
    except Exception as e:
        print(f"Error adding channel: {str(e)}")
        flash('An error occurred while adding the channel. Please try again.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/monitor_channel/<channel_id>', methods=['POST'])
def monitor_channel_route(channel_id):
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    username = session['username']
    user = db.get_user_by_username(username)
    
    try:
        # Check if user has Telegram linked
        if not user.get('telegram_linked', False):
            return jsonify({'success': False, 'message': 'Please link your Telegram account first'})
        
        # Get channel info
        channel = db.channels.find_one({'_id': ObjectId(channel_id), 'username': username})
        if not channel:
            return jsonify({'success': False, 'message': 'Channel not found'})
        
        # Run monitoring using the monitor instance directly with asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(
                monitor.analyze_channel(
                    user['api_id'], 
                    user['api_hash'], 
                    channel['channel_link'], 
                    channel_id,
                    user.get('phone_number')  # Use stored phone number
                )
            )
        finally:
            loop.close()
        
        return jsonify({
            'success': True, 
            'message': f'Monitored successfully! Found {len(results)} messages.',
            'results_count': len(results),
            'suspicious_count': sum(1 for r in results if r['prediction'] == 'drug sale')
        })
        
    except Exception as e:
        print(f"Monitoring error: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/view_results/<channel_id>')
def view_results(channel_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = db.get_user_by_username(username)
    
    # Get channel info
    channel = db.channels.find_one({'_id': ObjectId(channel_id), 'username': username})
    if not channel:
        flash('Channel not found!', 'error')
        return redirect(url_for('dashboard'))
    
    # Get monitoring results
    results = db.get_monitoring_results(channel_id)
    
    # Calculate statistics
    suspicious_count = sum(1 for r in results if r.get('prediction') == 'drug sale')
    normal_count = sum(1 for r in results if r.get('prediction') == 'normal')
    spam_count = sum(1 for r in results if r.get('prediction') == 'spam')
    other_count = sum(1 for r in results if r.get('prediction') == 'other')
    
    return render_template('results.html', 
                         user=user,
                         channel=channel, 
                         results=results,
                         suspicious_count=suspicious_count,
                         normal_count=normal_count,
                         spam_count=spam_count,
                         other_count=other_count)

@app.route('/export_csv/<channel_id>')
def export_csv(channel_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    # Verify channel ownership
    channel = db.channels.find_one({'_id': ObjectId(channel_id), 'username': username})
    if not channel:
        flash('Channel not found!', 'error')
        return redirect(url_for('dashboard'))
    
    # Export results
    from real_monitor_v2 import real_monitor_v2
    filename = real_monitor_v2.export_results_to_csv(channel_id)
    
    return send_file(filename, as_attachment=True, download_name=f"channel_results_{channel_id}.csv")

@app.route('/remove_channel/<channel_id>', methods=['DELETE'])
def remove_channel(channel_id):
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    username = session['username']
    
    try:
        # Remove channel and its data
        result = db.channels.delete_one({'_id': ObjectId(channel_id), 'username': username})
        
        if result.deleted_count > 0:
            # Also remove monitoring results and alerts
            db.monitoring_results.delete_many({'channel_id': channel_id})
            db.alerts.delete_many({'channel_id': channel_id})
            
            return jsonify({'success': True, 'message': 'Channel removed successfully'})
        else:
            return jsonify({'success': False, 'message': 'Channel not found'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/view_alerts')
def view_alerts():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = db.get_user_by_username(username)
    alerts = db.get_alerts(username)
    
    return render_template('alerts.html', user=user, alerts=alerts)

@app.route('/dismiss_alert/<alert_id>', methods=['POST'])
def dismiss_alert(alert_id):
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    try:
        db.alerts.update_one(
            {'_id': ObjectId(alert_id)},
            {'$set': {'status': 'dismissed', 'dismissed_at': datetime.utcnow()}}
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/send_otp_dashboard', methods=['POST'])
def send_otp_dashboard():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    username = session['username']
    user = db.get_user_by_username(username)
    
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        
        print(f"DEBUG: send_otp_dashboard called for user {username} with phone {phone_number}")
        
        if not phone_number:
            return jsonify({'success': False, 'message': 'Phone number is required'})
        
        # Send OTP using telegram helper and get phone_code_hash
        success, message_or_hash = telegram_helper.send_otp_with_hash(
            user['api_id'], 
            user['api_hash'], 
            phone_number, 
            username
        )
        
        print(f"DEBUG: OTP send result - Success: {success}")
        
        if success:
            # Store phone number and hash in Flask session for verification
            session['dashboard_phone_number'] = phone_number
            session['dashboard_phone_code_hash'] = message_or_hash  # This is the hash
            print(f"DEBUG: Stored in session - Phone: {phone_number}, Hash: {message_or_hash[:20]}...")
            return jsonify({'success': True, 'message': 'OTP sent successfully'})
        else:
            return jsonify({'success': False, 'message': message_or_hash})
            
    except Exception as e:
        print(f"ERROR in send_otp_dashboard: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/verify_otp_dashboard', methods=['POST'])
def verify_otp_dashboard():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    username = session['username']
    
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        otp_code = data.get('otp_code')
        
        print(f"DEBUG: Received verification request - Phone: {phone_number}, OTP: {otp_code}")
        
        if not phone_number or not otp_code:
            return jsonify({'success': False, 'message': 'Phone number and OTP code are required'})
        
        # Get phone_code_hash from session
        phone_code_hash = session.get('dashboard_phone_code_hash')
        stored_phone = session.get('dashboard_phone_number')
        
        print(f"DEBUG: Session data - Stored phone: {stored_phone}, Has hash: {bool(phone_code_hash)}")
        
        if not phone_code_hash or not stored_phone:
            return jsonify({'success': False, 'message': 'Session expired. Please request a new OTP.'})
        
        if stored_phone != phone_number:
            return jsonify({'success': False, 'message': 'Phone number mismatch. Please request a new OTP.'})
        
        # Verify OTP using telegram helper with phone_code_hash
        success, message = telegram_helper.verify_otp_with_hash(username, phone_number, otp_code, phone_code_hash)
        
        print(f"DEBUG: Verification result - Success: {success}, Message: {message}")
        
        if success:
            # Update database to mark Telegram as linked
            db.update_telegram_link(username, phone_number)
            
            # Clean up session
            session.pop('dashboard_phone_number', None)
            session.pop('dashboard_phone_code_hash', None)
            
            return jsonify({'success': True, 'message': 'Telegram account linked successfully'})
        else:
            return jsonify({'success': False, 'message': message})
            
    except Exception as e:
        print(f"ERROR in verify_otp_dashboard: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/check_existing_session', methods=['POST'])
def check_existing_session():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    username = session['username']
    user = db.get_user_by_username(username)
    
    try:
        # Check for existing authenticated sessions
        success, message = telegram_helper.check_existing_session(
            user['api_id'], 
            user['api_hash'], 
            username
        )
        
        if success:
            # Auto-link the account since we found a valid session
            db.update_telegram_link(username, "auto-detected")
            return jsonify({'success': True, 'message': f'Found existing session! {message}'})
        else:
            return jsonify({'success': False, 'message': message})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Health check endpoint for Render
@app.route('/health')
def health_check():
    """Health check endpoint for cloud deployment monitoring"""
    try:
        # Check database connection
        db.users.find_one()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'Telegram Drug Monitor',
            'version': '1.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Internal server error"), 500

# Make app available for gunicorn app:app (Render auto-detection)
application = app

# Production configuration for Render
if os.getenv('FLASK_ENV') == 'production':
    app.config['ENV'] = 'production'
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
