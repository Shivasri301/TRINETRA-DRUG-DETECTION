# 🚀 Trinetra - Deployment Guide

## 📋 Pre-Deployment Checklist

### ✅ System Requirements
- **Python 3.8+** with pip
- **4GB+ RAM** (for NLP model)
- **10GB+ Disk Space** (for models and data)
- **Stable Internet Connection**
- **MongoDB Atlas Account** (or self-hosted MongoDB)

### ✅ Security Requirements
- **Secure server environment**
- **HTTPS certificate** (for production)
- **Firewall configuration**
- **Access control policies**

---

## 🔧 Installation Steps

### 1. Download and Setup
```bash
# Clone or download the project
cd DARKFINFINALEEE

# Install dependencies
python setup.py

# OR manual installation:
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Edit .env file with your credentials
MONGODB_URI=your_mongodb_connection_string
SECRET_KEY=your_secure_secret_key_change_this
DATABASE_NAME=telegram_drug_monitor
```

### 3. Database Setup
- **MongoDB Atlas**: Use provided connection string
- **Self-hosted**: Update MONGODB_URI in .env
- **Collections**: Will be created automatically

### 4. Telegram API Setup
- Visit [my.telegram.org](https://my.telegram.org)
- Create new application
- Note API ID and API Hash
- Users will enter these during registration

---

## 🚀 Starting the Application

### Development Mode
```bash
python app.py
# Access: http://localhost:5000
```

### Production Mode
```bash
python start_production.py
# Includes health checks and proper error handling
```

### Using systemd (Linux Production)
```bash
# Create service file: /etc/systemd/system/telegram-monitor.service
[Unit]
Description=Trinetra
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/DARKFINFINALEEE
ExecStart=/usr/bin/python3 start_production.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable telegram-monitor
sudo systemctl start telegram-monitor
```

---

## 🔐 Security Configuration

### 1. Environment Variables
```env
# CRITICAL: Change these for production
SECRET_KEY=your-very-secure-secret-key-here
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=telegram_drug_monitor_prod

# Optional: Rate limiting
RATE_LIMIT_PER_MINUTE=60
MAX_CHANNELS_PER_USER=50
```

### 2. Firewall Rules
```bash
# Allow only necessary ports
ufw allow 5000/tcp  # Application port
ufw allow 22/tcp    # SSH (if needed)
ufw enable
```

### 3. HTTPS Setup (Production)
```bash
# Using nginx reverse proxy
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📊 Monitoring and Maintenance

### Health Checks
```bash
# Database connectivity
python -c "from database import db; print('DB OK' if db.users.find_one() is not None else 'DB FAIL')"

# Model loading
python -c "from transformers import pipeline; print('Model OK')"

# Application status
curl http://localhost:5000/ -o /dev/null -w "%{http_code}"
```

### Log Monitoring
```bash
# Application logs
tail -f /var/log/telegram-monitor.log

# System logs
journalctl -u telegram-monitor -f
```

### Backup Strategy
```bash
# Daily database backup
mongodump --uri="your_mongodb_uri" --out="/backup/$(date +%Y%m%d)"

# Weekly full backup including sessions
tar -czf "/backup/full_$(date +%Y%m%d).tar.gz" /path/to/DARKFINFINALEEE
```

---

## 🎯 User Onboarding

### For Law Enforcement Officers

1. **Registration Process**
   - Visit application URL
   - Click "Register" 
   - Enter unique username and strong password
   - Get Telegram API credentials from my.telegram.org
   - Enter API ID and API Hash

2. **Telegram Account Linking**
   - Enter phone number in international format
   - Receive OTP via Telegram
   - Enter verification code
   - Account successfully linked

3. **Channel Monitoring**
   - Add channel links (https://t.me/channelname)
   - Click "Monitor" to analyze messages
   - View results and alerts in dashboard
   - Export data as CSV for reports

### Demo Mode (For Testing)
- Username: `demo_user`
- Password: `demo123`
- API ID: `12345678`
- API Hash: `demo_hash_123456789`

---

## 🔧 Troubleshooting

### Common Issues

**"Database connection failed"**
- Check MongoDB URI in .env
- Verify network connectivity
- Ensure MongoDB Atlas IP whitelist includes your server

**"Model loading errors"**
- Ensure sufficient RAM (4GB+)
- Check internet connection for model download
- Clear Python cache: `rm -rf __pycache__`

**"Telegram API errors"**
- Verify API credentials at my.telegram.org
- Check rate limits (avoid excessive requests)
- Ensure phone number format is correct (+country code)

**"Session expired errors"**
- Users need to re-authenticate Telegram
- Clear session files: `rm *.session`
- Restart application

### Performance Optimization

**For High Traffic**
```bash
# Use gunicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**For Large Scale**
- Consider Redis for session storage
- Implement connection pooling
- Use database indexing
- Set up load balancing

---

## 📈 Scaling Considerations

### Horizontal Scaling
- Multiple application instances
- Load balancer (nginx/HAProxy)
- Shared MongoDB cluster
- Redis session store

### Vertical Scaling
- Increase RAM for NLP model
- SSD storage for faster I/O
- Multi-core CPU for concurrent processing

### Monitoring Tools
- **Application**: Prometheus + Grafana
- **Database**: MongoDB Compass
- **System**: New Relic, DataDog
- **Alerts**: PagerDuty, Slack integration

---

## ⚖️ Legal and Compliance

### Data Protection
- Implement data retention policies
- Ensure GDPR compliance (if applicable)
- Regular security audits
- Access logging and monitoring

### Law Enforcement Use
- Verify legal authority for monitoring
- Maintain chain of custody for evidence
- Regular backup and data integrity checks
- Compliance with local surveillance laws

---

## 🔄 Updates and Maintenance

### Regular Tasks
- **Daily**: Check logs and alerts
- **Weekly**: Database backup and cleanup
- **Monthly**: Security updates and patches
- **Quarterly**: Performance review and optimization

### Version Updates
```bash
# Backup before updates
cp -r DARKFINFINALEEE DARKFINFINALEEE_backup_$(date +%Y%m%d)

# Update code
git pull origin main  # If using git

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
systemctl restart telegram-monitor
```

---

## 📞 Support and Documentation

### Technical Support
- Check application logs first
- Review troubleshooting section
- Verify all dependencies are installed
- Test database connectivity

### Performance Monitoring
- Monitor RAM usage (should be < 8GB)
- Check disk space regularly
- Monitor network traffic
- Track response times

---

## 🎯 Success Metrics

### Application Health
- ✅ Uptime > 99%
- ✅ Response time < 2 seconds
- ✅ Zero data loss
- ✅ Successful authentication rate > 95%

### Detection Accuracy
- ✅ False positive rate < 5%
- ✅ Detection confidence > 80%
- ✅ Processing time < 1 second per message
- ✅ Alert response time < 30 seconds

---

**🏆 Your Trinetra is now ready for production deployment!**

For additional support or custom configuration, refer to the technical documentation or contact your system administrator.
