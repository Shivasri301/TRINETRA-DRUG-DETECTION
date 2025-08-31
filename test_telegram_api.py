import asyncio
from telethon import TelegramClient
from database import db
import os
import glob

async def test_telegram_connection():
    """Test if Telegram API credentials are working"""
    
    # Get user credentials
    user = db.get_user_by_username('Devesh')
    if not user:
        print("❌ User 'Devesh' not found in database!")
        return
    
    api_id = user['api_id']
    api_hash = user['api_hash']
    
    print(f"🔍 Testing NEW Telegram API connection...")
    print(f"NEW API ID: {api_id}")
    print(f"NEW API Hash: {api_hash[:10]}...")
    
    # Clean up any existing session files
    session_files = glob.glob("*.session")
    for session_file in session_files:
        try:
            os.remove(session_file)
            print(f"🧹 Removed old session file: {session_file}")
        except:
            pass
    
    try:
        # Create a test client
        client = TelegramClient('test_session', api_id, api_hash)
        
        print("📡 Attempting to connect...")
        await client.connect()
        
        print("✅ Connection successful!")
        
        # Try to get basic info
        me = await client.get_me()
        if me:
            print(f"✅ Authorized as: {me.first_name} (ID: {me.id})")
        else:
            print("⚠️ Not authorized, but connection works")
        
        # Test accessing a public channel
        try:
            print("🔍 Testing channel access...")
            # Try accessing a well-known public channel
            test_channel = await client.get_entity('https://t.me/telegram')
            print(f"✅ Successfully accessed test channel: {test_channel.title}")
        except Exception as channel_error:
            print(f"⚠️ Channel access issue: {channel_error}")
        
        await client.disconnect()
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Possible solutions:")
        print("1. Verify your API ID and Hash at https://my.telegram.org")
        print("2. Check if your API credentials are active")
        print("3. Ensure you have internet connection")
        print("4. Try creating new API credentials if needed")

if __name__ == "__main__":
    asyncio.run(test_telegram_connection())
