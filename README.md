# Telegram Drug Monitor 🚨

A comprehensive software solution for detecting drug-related activities in Telegram channels using advanced NLP and keyword analysis. Built for law enforcement and security professionals to monitor and identify potential drug trafficking operations.

## 🎯 Features

### Core Functionality
- **Real-Time Channel Monitoring**: Continuously scan Telegram channels for drug-related content
- **Advanced Detection**: Combines NLP (BART-large-mnli) with extensive keyword databases
- **Multi-User Support**: Secure user registration and authentication system
- **Telegram Integration**: Direct OTP-based phone verification and channel access

### Detection Capabilities
- **Drug Keywords Database**: Comprehensive list including MDMA, LSD, Mephedrone, Cannabis, and Indian slang
- **Sales Pattern Detection**: Identifies delivery terms, pricing discussions, and transaction language
- **Emoji Analysis**: Detects drug-related emojis and symbols commonly used in trafficking
- **Confidence Scoring**: Provides reliability percentages for each detection

### User Interface
- **Interactive Dashboard**: Clean, responsive interface with real-time updates
- **Alert System**: Immediate notifications for suspicious activities
- **Data Export**: CSV export functionality for law enforcement reports
- **Statistics & Analytics**: Comprehensive monitoring statistics and trends

## 🏗️ Architecture

```
├── app.py                 # Main Flask application
├── database.py           # MongoDB Atlas integration
├── telegram_monitor.py   # Core monitoring and NLP analysis
├── async_helper.py      # Telegram API async operations handler
├── templates/           # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── results.html
│   ├── alerts.html
│   └── error.html
├── static/             # CSS/JS assets
├── requirements.txt    # Python dependencies
└── .env               # Environment configuration
```

## 🚀 Quick Start

### Prerequisites
1. **Python 3.8+** installed on your system
2. **Telegram API Credentials** from [my.telegram.org](https://my.telegram.org)
3. **MongoDB Atlas Account** (provided connection string included)

### Installation

1. **Clone and Setup**
```bash
cd C:\Users\ASUS\DARK
python setup.py
```

2. **Get Telegram API Credentials**
   - Visit [my.telegram.org](https://my.telegram.org)
   - Log in with your phone number
   - Create a new application
   - Note down your `API_ID` and `API_Hash`

3. **Run the Application**
```bash
python app.py
```

4. **Access the Dashboard**
   - Open your browser to `http://localhost:5000`
   - Register a new account with your Telegram API credentials
   - Link your Telegram account using phone verification
   - Start monitoring channels!

## 📋 Usage Guide

### Step 1: Registration
- Create account with unique username and strong password
- Enter your Telegram API ID and API Hash
- These credentials are required for accessing Telegram channels

### Step 2: Link Telegram Account
- Enter your phone number in international format (+91XXXXXXXXXX)
- Receive OTP via Telegram app
- Enter verification code to complete linking

### Step 3: Add Channels
- Paste Telegram channel links (https://t.me/channelname)
- Click "Start Monitoring" to add to watchlist
- System will begin analyzing messages automatically

### Step 4: Monitor Results
- View real-time alerts on dashboard
- Click "Results" to see detailed analysis
- Export data as CSV for reporting
- Filter and sort messages by confidence and type

## 🔍 Detection Algorithm

### Keyword Analysis
The system includes an extensive database of drug-related terms:
- **Common Drugs**: MDMA, LSD, Mephedrone, Cannabis, Cocaine, Heroin
- **Indian Slang**: Maal, Charas, Ganja, Brown Sugar
- **Sales Terms**: Home delivery, Bulk discount, Quality guarantee
- **Emojis**: 💊🌿💉🔥⚡💯 and more

### NLP Classification
- Uses Facebook's BART-large-mnli model for zero-shot classification
- Categories: Drug Sale, Normal, Spam, Other
- Confidence scoring from 0-100%
- Enhanced accuracy through combined keyword + AI analysis

### Alert Generation
- Automatic alerts for messages classified as "drug sale"
- Confidence thresholds and keyword matching
- Real-time notifications in dashboard
- Historical alert tracking and management

## 🛡️ Security Features

- **Password Hashing**: Bcrypt encryption for user passwords
- **Session Management**: Secure Flask sessions with timeout
- **API Key Protection**: Encrypted storage of Telegram credentials
- **User Isolation**: Each user only sees their own channels and data

## 🗄️ Database Schema

### Users Collection
```json
{
  "username": "unique_username",
  "password": "bcrypt_hashed_password",
  "api_id": 12345678,
  "api_hash": "telegram_api_hash",
  "telegram_linked": true,
  "phone_number": "+91XXXXXXXXXX",
  "created_at": "datetime"
}
```

### Channels Collection
```json
{
  "username": "owner_username",
  "channel_link": "https://t.me/channelname",
  "channel_name": "Channel Display Name",
  "status": "active|monitored|error",
  "added_at": "datetime",
  "last_monitored": "datetime"
}
```

### Monitoring Results Collection
```json
{
  "channel_id": "channel_object_id",
  "message_id": 12345,
  "sender_id": 67890,
  "date": "datetime",
  "message_text": "Message content",
  "prediction": "drug sale|normal|spam|other",
  "confidence": 0.85,
  "keyword_matches": ["mdma", "delivery"],
  "is_suspicious": true,
  "processed_at": "datetime"
}
```

### Alerts Collection
```json
{
  "channel_id": "channel_object_id",
  "message_id": 12345,
  "alert_type": "drug_sale_detected",
  "confidence": 0.85,
  "message_text": "Suspicious message content",
  "status": "new|dismissed",
  "created_at": "datetime"
}
```

## 🔧 Configuration

### Environment Variables (.env)
```env
MONGODB_URI=mongodb+srv://your_connection_string
SECRET_KEY=your_secret_key_for_sessions
DATABASE_NAME=telegram_drug_monitor
```

### Customization Options
- **Keyword Database**: Modify `drug_keywords` in `telegram_monitor.py`
- **NLP Model**: Change model in `TelegramMonitor.__init__()`
- **Confidence Thresholds**: Adjust in `analyze_message()` method
- **Message Limits**: Modify `limit` parameter in monitoring functions

## ⚠️ Important Notes

### Legal Compliance
- This tool is designed for law enforcement and authorized security personnel
- Ensure compliance with local privacy and surveillance laws
- Use only for legitimate investigation purposes

### API Limitations
- Telegram API has rate limits - avoid excessive requests
- Public channels only (private channels require membership)
- Some channels may have access restrictions

### Performance Considerations
- NLP model requires significant computational resources
- First run may be slow due to model download
- Consider GPU acceleration for large-scale monitoring

## 🚧 Troubleshooting

### Common Issues

**"Invalid API credentials"**
- Verify API_ID and API_Hash from my.telegram.org
- Ensure credentials are from the same Telegram account

**"Phone code invalid"**
- Check that you're using the correct phone number
- Ensure the OTP code is entered within the time limit
- Try requesting a new code

**"Session expired"**
- Re-link your Telegram account
- Clear browser cache and cookies
- Restart the application

**"Channel not found"**
- Verify the channel link format (https://t.me/channelname)
- Ensure the channel is public
- Check if the channel still exists

### Database Connection Issues
- Verify MongoDB Atlas connection string
- Check network connectivity
- Ensure database permissions are correct

## 📈 Future Enhancements

- Real-time WebSocket notifications
- Machine learning model training on custom datasets
- Multi-language support for regional slang
- Integration with law enforcement databases
- Automated reporting and evidence collection
- Image and video content analysis
- Bot detection algorithms
- Network analysis of related channels

## 🤝 Contributing

This project was developed for law enforcement and security research purposes. Contributions should focus on:
- Improving detection accuracy
- Adding new drug-related keywords
- Enhancing user interface
- Performance optimizations

## 📞 Support

For technical support or questions about implementation:
- Check the troubleshooting section above
- Review the application logs for error details
- Ensure all dependencies are properly installed

---

**⚖️ Legal Disclaimer**: This software is intended for law enforcement and authorized security professionals only. Users are responsible for compliance with local laws and regulations regarding surveillance and privacy.
