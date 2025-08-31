#!/usr/bin/env python3
"""
Test database connection
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

def test_connection():
    """Test MongoDB Atlas connection"""
    load_dotenv()
    
    try:
        print("🔍 Testing MongoDB connection...")
        
        # Get connection string from environment
        mongodb_uri = os.getenv('MONGODB_URI')
        database_name = os.getenv('DATABASE_NAME')
        
        print(f"📁 Database: {database_name}")
        print(f"🔗 URI: {mongodb_uri[:50]}...")
        
        # Create client
        client = MongoClient(mongodb_uri)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        
        # Test database access
        db = client[database_name]
        collections = db.list_collection_names()
        print(f"📊 Available collections: {collections}")
        
        # Test basic operation
        test_collection = db.test
        result = test_collection.insert_one({"test": "connection", "timestamp": "2024"})
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Clean up test document
        test_collection.delete_one({"_id": result.inserted_id})
        print("🧹 Test document cleaned up")
        
        client.close()
        print("✅ Database connection test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    if test_connection():
        print("\n🚀 Ready to start the application!")
    else:
        print("\n⚠️  Please check your MongoDB credentials and try again.")
