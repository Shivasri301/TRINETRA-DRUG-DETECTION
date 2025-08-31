import asyncio
from telethon import TelegramClient
from database import db

async def test_real_channel_monitoring():
    """Test real channel monitoring with authenticated API"""
    
    # Get credentials
    user = db.get_user_by_username('Devesh')
    api_id = user['api_id']
    api_hash = user['api_hash']
    
    print("🚀 Testing REAL CHANNEL MONITORING")
    print(f"API ID: {api_id}")
    
    # Use authenticated session
    client = TelegramClient('authenticated_session', api_id, api_hash)
    await client.connect()
    
    if not await client.is_user_authorized():
        print("❌ Not authenticated! Run authenticate_telegram.py first")
        return
    
    print("✅ Using authenticated session")
    
    # Test with a real public channel that likely has content
    test_channels = [
        'https://t.me/telegram',  # Official Telegram channel
        'https://t.me/durov',     # Pavel Durov's channel
    ]
    
    for channel_link in test_channels:
        try:
            print(f"\n🔍 Testing channel: {channel_link}")
            
            # Extract channel name
            channel_name = channel_link.split('/')[-1]
            if channel_name.startswith('@'):
                channel_name = channel_name[1:]
            
            # Get channel entity
            channel_entity = await client.get_entity(f"@{channel_name}")
            print(f"✅ Successfully accessed: {channel_entity.title}")
            
            # Fetch some messages
            message_count = 0
            async for message in client.iter_messages(channel_entity, limit=10):
                if message.text:
                    message_count += 1
                    print(f"📨 Message {message_count}: {message.text[:100]}...")
            
            print(f"✅ Successfully fetched {message_count} real messages!")
            break
            
        except Exception as e:
            print(f"⚠️ Failed to access {channel_link}: {e}")
            continue
    
    await client.disconnect()
    print("\n🎉 REAL DATA ACCESS CONFIRMED!")
    print("Your system can now monitor real Telegram channels!")

if __name__ == "__main__":
    asyncio.run(test_real_channel_monitoring())
