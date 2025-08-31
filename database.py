import os
from pymongo import MongoClient
from datetime import datetime
import bcrypt
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client[os.getenv('DATABASE_NAME')]
        self.users = self.db.users
        self.channels = self.db.channels
        self.monitoring_results = self.db.monitoring_results
        self.alerts = self.db.alerts

    def create_user(self, username, password, api_id, api_hash):
        """Create a new user with hashed password"""
        if self.users.find_one({"username": username}):
            return False, "Username already exists"
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_doc = {
            "username": username,
            "password": hashed_password,
            "api_id": api_id,
            "api_hash": api_hash,
            "telegram_linked": False,
            "phone_number": None,
            "created_at": datetime.utcnow()
        }
        
        result = self.users.insert_one(user_doc)
        return True, str(result.inserted_id)

    def verify_user(self, username, password):
        """Verify user login credentials"""
        user = self.users.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return True, user
        return False, None

    def update_telegram_link(self, username, phone_number):
        """Update user's Telegram linking status"""
        self.users.update_one(
            {"username": username},
            {
                "$set": {
                    "telegram_linked": True,
                    "phone_number": phone_number,
                    "linked_at": datetime.utcnow()
                }
            }
        )

    def get_user_by_username(self, username):
        """Get user document by username"""
        return self.users.find_one({"username": username})

    def add_channel(self, username, channel_link, channel_name=None):
        """Add a channel to monitor"""
        # Check if channel already exists for this user
        existing = self.channels.find_one({
            "username": username,
            "channel_link": channel_link
        })
        
        if existing:
            return str(existing['_id'])
        
        # Extract channel name from link if not provided
        if not channel_name:
            channel_name = channel_link.split('/')[-1]
            if channel_name.startswith('@'):
                channel_name = channel_name[1:]
        
        channel_doc = {
            "username": username,
            "channel_link": channel_link,
            "channel_name": channel_name,
            "status": "active",
            "added_at": datetime.utcnow(),
            "last_monitored": None
        }
        
        result = self.channels.insert_one(channel_doc)
        return str(result.inserted_id)

    def get_user_channels(self, username):
        """Get all channels for a user"""
        return list(self.channels.find({"username": username}))

    def save_monitoring_result(self, channel_id, message_data):
        """Save monitoring results"""
        result_doc = {
            "channel_id": channel_id,
            "message_id": message_data.get("message_id"),
            "sender_id": message_data.get("sender_id"),
            "date": message_data.get("date"),
            "message_text": message_data.get("message_text"),
            "prediction": message_data.get("prediction"),
            "confidence": message_data.get("confidence"),
            "is_suspicious": message_data.get("prediction") == "drug sale",
            "processed_at": datetime.utcnow()
        }
        
        result = self.monitoring_results.insert_one(result_doc)
        
        # Create alert if suspicious
        if message_data.get("prediction") == "drug sale":
            self.create_alert(channel_id, result_doc)
        
        return str(result.inserted_id)

    def create_alert(self, channel_id, message_data):
        """Create an alert for suspicious activity"""
        alert_doc = {
            "channel_id": channel_id,
            "message_id": message_data.get("message_id"),
            "alert_type": "drug_sale_detected",
            "confidence": message_data.get("confidence"),
            "message_text": message_data.get("message_text"),
            "status": "new",
            "created_at": datetime.utcnow()
        }
        
        return self.alerts.insert_one(alert_doc)

    def get_monitoring_results(self, channel_id, limit=100):
        """Get monitoring results for a channel"""
        return list(self.monitoring_results.find(
            {"channel_id": channel_id}
        ).sort("processed_at", -1).limit(limit))

    def get_alerts(self, username, status="new"):
        """Get alerts for user's channels"""
        user_channels = self.get_user_channels(username)
        channel_ids = [str(channel['_id']) for channel in user_channels]
        
        query = {"channel_id": {"$in": channel_ids}}
        if status:
            query["status"] = status
            
        return list(self.alerts.find(query).sort("created_at", -1))

    def update_channel_status(self, channel_id, status, last_monitored=None):
        """Update channel monitoring status"""
        update_doc = {"status": status}
        if last_monitored:
            update_doc["last_monitored"] = last_monitored
            
        self.channels.update_one(
            {"_id": channel_id},
            {"$set": update_doc}
        )

# Initialize database connection
db = Database()
