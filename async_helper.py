import asyncio
import threading
import tempfile
import os
from telethon import TelegramClient
from telethon.errors import PhoneCodeInvalidError, SessionPasswordNeededError

class AsyncTelegramHelper:
    def __init__(self):
        self.active_clients = {}
    
    def run_async(self, coro):
        """Run async coroutine in a new event loop"""
        try:
            # Try to get existing loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create new thread
                result = None
                exception = None
                
                def run_in_thread():
                    nonlocal result, exception
                    try:
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        result = new_loop.run_until_complete(coro)
                        new_loop.close()
                    except Exception as e:
                        exception = e
                
                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()
                
                if exception:
                    raise exception
                return result
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # No event loop, create new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(coro)
            loop.close()
            return result
    
    async def send_otp_async(self, api_id, api_hash, phone_number, username):
        """Send OTP to phone number"""
        try:
            # Clean up any existing temp client
            client_key = f"{username}_temp"
            if client_key in self.active_clients:
                try:
                    client_data = self.active_clients[client_key]
                    if isinstance(client_data, dict):
                        await client_data['client'].disconnect()
                    else:
                        await client_data.disconnect()
                except:
                    pass
                del self.active_clients[client_key]
            
            # Use temporary directory for cloud compatibility
            session_dir = tempfile.gettempdir()
            session_path = os.path.join(session_dir, f"temp_{username}")
            client = TelegramClient(session_path, api_id, api_hash)
            await client.connect()
            
            result = await client.send_code_request(phone_number)
            print(f"✅ OTP sent successfully to {phone_number}")
            print(f"📱 Phone code hash: {result.phone_code_hash}")
            
            # Store client AND phone_code_hash for later use
            self.active_clients[client_key] = {
                'client': client,
                'phone_code_hash': result.phone_code_hash,
                'phone_number': phone_number
            }
            
            return True, "OTP sent successfully"
        except Exception as e:
            print(f"❌ Error sending OTP: {str(e)}")
            return False, str(e)
    
    async def verify_otp_async(self, username, phone_number, otp_code):
        """Verify OTP and complete authentication"""
        try:
            client_key = f"{username}_temp"
            
            # Try to use existing client first
            if client_key in self.active_clients:
                try:
                    client_data = self.active_clients[client_key]
                    
                    # Handle both old format (direct client) and new format (dict with client)
                    if isinstance(client_data, dict):
                        client = client_data['client']
                        phone_code_hash = client_data['phone_code_hash']
                        stored_phone = client_data['phone_number']
                        
                        print(f"📱 Using stored phone_code_hash for verification")
                        
                        # Verify the phone number matches
                        if stored_phone != phone_number:
                            print(f"⚠️ Phone number mismatch: stored {stored_phone}, provided {phone_number}")
                            return False, "Phone number mismatch. Please request a new OTP."
                        
                        # Sign in with phone_code_hash
                        await client.sign_in(phone_number, otp_code, phone_code_hash=phone_code_hash)
                    else:
                        # Old format - direct client
                        client = client_data
                        await client.sign_in(phone_number, otp_code)
                    
                    # Save as authenticated session
                    await client.disconnect()
                    
                    # Copy to authenticated session
                    import shutil
                    import os
                    
                    temp_session = f"temp_{username}.session"
                    auth_session = "authenticated_session.session"
                    
                    if os.path.exists(temp_session):
                        shutil.copy2(temp_session, auth_session)
                        print(f"✅ Copied session from {temp_session} to {auth_session}")
                    
                    # Clean up temp client
                    del self.active_clients[client_key]
                    
                    print(f"✅ OTP verified successfully using existing client for {username}")
                    return True, "Successfully linked Telegram account"
                except Exception as e:
                    print(f"⚠️ Existing client failed, trying fallback: {e}")
                    # Clean up failed client
                    try:
                        client_to_disconnect = self.active_clients[client_key]
                        if isinstance(client_to_disconnect, dict) and 'client' in client_to_disconnect:
                            await client_to_disconnect['client'].disconnect()
                        elif hasattr(client_to_disconnect, 'disconnect'):
                            await client_to_disconnect.disconnect()
                    except Exception as disconnect_error:
                        print(f"Warning: Failed to disconnect client: {disconnect_error}")
                    if client_key in self.active_clients:
                        del self.active_clients[client_key]
            
            # Fallback: This shouldn't happen with proper phone_code_hash flow
            print(f"❌ No active client found for {username}. Please request a new OTP.")
            return False, "Session expired. Please request a new OTP."
            
        except PhoneCodeInvalidError:
            print(f"❌ Invalid verification code for {username}")
            return False, "Invalid verification code"
        except SessionPasswordNeededError:
            print(f"❌ Two-factor authentication enabled for {username}")
            return False, "Two-factor authentication enabled. Please disable it temporarily."
        except Exception as e:
            print(f"❌ Error in verify_otp_async: {str(e)}")
            return False, str(e)
    
    def send_otp(self, api_id, api_hash, phone_number, username):
        """Sync wrapper for sending OTP"""
        return self.run_async(self.send_otp_async(api_id, api_hash, phone_number, username))
    
    def send_otp_with_hash(self, api_id, api_hash, phone_number, username):
        """Send OTP and return phone_code_hash for session storage"""
        return self.run_async(self.send_otp_with_hash_async(api_id, api_hash, phone_number, username))
    
    async def send_otp_with_hash_async(self, api_id, api_hash, phone_number, username):
        """Send OTP and return phone_code_hash"""
        try:
            client = TelegramClient(f"temp_{username}", api_id, api_hash)
            await client.connect()
            
            result = await client.send_code_request(phone_number)
            print(f"✅ OTP sent successfully to {phone_number}")
            print(f"📱 Phone code hash: {result.phone_code_hash}")
            
            await client.disconnect()
            
            # Return the phone_code_hash directly
            return True, result.phone_code_hash
        except Exception as e:
            print(f"❌ Error sending OTP: {str(e)}")
            return False, str(e)
    
    def verify_otp(self, username, phone_number, otp_code):
        """Sync wrapper for verifying OTP"""
        return self.run_async(self.verify_otp_async(username, phone_number, otp_code))
    
    def verify_otp_with_hash(self, username, phone_number, otp_code, phone_code_hash):
        """Verify OTP with provided phone_code_hash"""
        return self.run_async(self.verify_otp_with_hash_async(username, phone_number, otp_code, phone_code_hash))
    
    async def verify_otp_with_hash_async(self, username, phone_number, otp_code, phone_code_hash):
        """Verify OTP with phone_code_hash"""
        try:
            # Get user data for API credentials
            from database import db
            user = db.get_user_by_username(username)
            if not user:
                return False, "User not found"
            
            client = TelegramClient(f"temp_{username}", user['api_id'], user['api_hash'])
            await client.connect()
            
            print(f"📱 Verifying OTP with phone_code_hash")
            
            # Sign in with phone_code_hash
            await client.sign_in(phone_number, otp_code, phone_code_hash=phone_code_hash)
            
            # Save as authenticated session
            await client.disconnect()
            
            # Copy to authenticated session
            import shutil
            import os
            
            temp_session = f"temp_{username}.session"
            auth_session = "authenticated_session.session"
            
            if os.path.exists(temp_session):
                shutil.copy2(temp_session, auth_session)
                print(f"✅ Copied session from {temp_session} to {auth_session}")
            
            print(f"✅ OTP verified successfully for {username}")
            return True, "Successfully linked Telegram account"
            
        except PhoneCodeInvalidError:
            print(f"❌ Invalid verification code for {username}")
            return False, "Invalid verification code"
        except SessionPasswordNeededError:
            print(f"❌ Two-factor authentication enabled for {username}")
            return False, "Two-factor authentication enabled. Please disable it temporarily."
        except Exception as e:
            print(f"❌ Error in verify_otp_with_hash_async: {str(e)}")
            return False, str(e)
    
    def check_existing_session(self, api_id, api_hash, username):
        """Check if there's already an authenticated session"""
        return self.run_async(self.check_existing_session_async(api_id, api_hash, username))
    
    async def check_existing_session_async(self, api_id, api_hash, username):
        """Check if there's already an authenticated session"""
        try:
            # Try multiple session names that might exist
            session_names = [
                'authenticated_session',
                f'temp_{username}',
                f'monitor_session_{username}',
                f'real_session_{username}'
            ]
            
            for session_name in session_names:
                try:
                    client = TelegramClient(session_name, api_id, api_hash)
                    await client.connect()
                    
                    if await client.is_user_authorized():
                        # Test if we can actually access channels
                        try:
                            test_entity = await client.get_entity('https://t.me/telegram')
                            await client.disconnect()
                            print(f"✅ Found valid session: {session_name}")
                            return True, f"Using existing session: {session_name}"
                        except Exception as test_error:
                            print(f"⚠️ Session {session_name} exists but can't access channels: {test_error}")
                            await client.disconnect()
                            continue
                    else:
                        await client.disconnect()
                        continue
                        
                except Exception as e:
                    print(f"⚠️ Session {session_name} check failed: {e}")
                    try:
                        await client.disconnect()
                    except:
                        pass
                    continue
            
            return False, "No valid authenticated session found"
            
        except Exception as e:
            return False, f"Error checking sessions: {str(e)}"
    
    def monitor_channel(self, api_id, api_hash, channel_link, channel_id, phone_number):
        """Sync wrapper for monitoring channel - REAL DATA ONLY"""
        return self.run_async(self.monitor_real_channel(api_id, api_hash, channel_link, channel_id))
    
    async def monitor_real_channel(self, api_id, api_hash, channel_link, channel_id):
        """Monitor real channel using authenticated session"""
        from real_monitor_v2 import real_monitor_v2
        
        # Use the authenticated session
        session_name = 'authenticated_session'
        
        print(f"🔍 Using authenticated session for REAL DATA")
        
        client = TelegramClient(session_name, api_id, api_hash)
        await client.connect()
        
        if not await client.is_user_authorized():
            raise Exception("Session not authenticated. Run authenticate_telegram.py first.")
        
        print(f"✅ Using authenticated access for channel: {channel_link}")
        
        # Extract channel identifier
        channel_identifier = channel_link.split('/')[-1]
        if channel_identifier.startswith('@'):
            channel_identifier = channel_identifier[1:]
        
        try:
            # Get channel entity
            channel_entity = await client.get_entity(f"@{channel_identifier}")
            print(f"✅ Accessing real channel: {getattr(channel_entity, 'title', 'Unknown')}")
            
            results = []
            message_count = 0
            suspicious_count = 0
            
            # Fetch real messages
            async for message in client.iter_messages(channel_entity, limit=50):
                if message.text and message.text.strip():
                    message_count += 1
                    text = message.text.strip()
                    
                    print(f"📝 Real message {message_count}: {text[:60]}...")
                    
                    # Analyze message
                    analysis_result = await real_monitor_v2.analyze_message_real(text)
                    
                    message_data = {
                        "message_id": message.id,
                        "sender_id": message.sender_id,
                        "date": message.date,
                        "message_text": text,
                        "prediction": analysis_result["prediction"],
                        "confidence": analysis_result["confidence"],
                        "keyword_matches": analysis_result["keyword_matches"]
                    }
                    
                    results.append(message_data)
                    
                    # Save real data to database
                    from database import db
                    db.save_monitoring_result(channel_id, message_data)
                    
                    if analysis_result["prediction"] == "drug sale":
                        suspicious_count += 1
                        print(f"🚨 REAL DRUG SALE DETECTED: {text[:80]}")
                        print(f"   Keywords: {', '.join(analysis_result['keyword_matches'])}")
            
            print(f"✅ REAL DATA COMPLETE: {message_count} messages, {suspicious_count} drug sales")
            
            # Update status
            from database import db
            from datetime import datetime
            db.update_channel_status(channel_id, "monitored", datetime.utcnow())
            
            await client.disconnect()
            return results
            
        except Exception as e:
            await client.disconnect()
            raise e

# Global instance
telegram_helper = AsyncTelegramHelper()
