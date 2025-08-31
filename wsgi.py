#!/usr/bin/env python3
"""
WSGI entry point for Render deployment
Production-ready configuration for cloud hosting
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure application for production
os.environ['FLASK_ENV'] = 'production'

# Import app after environment setup
from app import app

# Production configuration
app.config['ENV'] = 'production'
app.config['DEBUG'] = False
app.config['TESTING'] = False
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

# For Gunicorn compatibility
application = app

if __name__ == "__main__":
    # Development fallback
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🚀 Starting Telegram Drug Monitor on port {port}")
    print("🔐 Production mode - Debug disabled")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )
