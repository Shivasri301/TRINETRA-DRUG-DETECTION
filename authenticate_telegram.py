import asyncio
from telethon import TelegramClient
from database import db

async def authenticate_telegram():
    """Authenticate your Telegram API with phone number for full access"""
    
    # Get your new credentials
    user = db.get_user_by_username('Devesh')
    api_id = user['api_id']
    api_hash = user['api_hash']
    
    print(f"🔐 Authenticating Telegram API for REAL DATA ACCESS")
    print(f"API ID: {api_id}")
    print(f"API Hash: {api_hash[:10]}...")
    
    # Create authenticated session
    client = TelegramClient('authenticated_session', api_id, api_hash)
    await client.connect()
    
    if not await client.is_user_authorized():
        print("\n📞 Phone authentication required for real data access")
        phone = input("Enter your phone number (with country code, e.g., +91xxxxxxxxxx): ")
        
        await client.send_code_request(phone)
        print("📱 Verification code sent to your Telegram app")
        
        code = input("Enter the verification code: ")
        await client.sign_in(phone, code)
        
        print("✅ Successfully authenticated!")
        
        # Test channel access
        try:
            print("🔍 Testing real channel access...")
            test_channel = await client.get_entity('https://t.me/telegram')
            print(f"✅ SUCCESS! Can access channels: {test_channel.title}")
            
            # Save phone number to database for future use
            db.users.update_one(
                {"username": "Devesh"},
                {"$set": {"phone_number": phone, "telegram_linked": True}}
            )
            print("✅ Phone number saved for future sessions")
            
        except Exception as e:
            print(f"❌ Still can't access channels: {e}")
    else:
        print("✅ Already authenticated!")
        
        # Test channel access
        try:
            test_channel = await client.get_entity('https://t.me/telegram')
            print(f"✅ Can access channels: {test_channel.title}")
        except Exception as e:
            print(f"❌ Channel access error: {e}")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(authenticate_telegram())
