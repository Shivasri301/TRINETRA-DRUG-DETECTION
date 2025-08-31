#!/usr/bin/env python3
"""
Simple Telegram authentication utility
Handles OTP verification with proper session management
"""

import asyncio
from telethon import TelegramClient
from telethon.errors import PhoneCodeInvalidError, SessionPasswordNeededError
from database import db

class SimpleTelegramAuth:
    def __init__(self):
        self.clients = {}
    
    async def send_otp(self, api_id, api_hash, phone_number, username):
        """Send OTP to phone number"""
        try:
            session_name = f"auth_{username}"
            client = TelegramClient(session_name, api_id, api_hash)
            await client.connect()
            
            # Send OTP
            await client.send_code_request(phone_number)
            
            # Store the client session name for later
            self.clients[username] = session_name
            
            # Don't disconnect - keep session for verification
            print(f"✅ OTP sent to {phone_number} for user {username}")
            return True, "OTP sent successfully"
            
        except Exception as e:
            print(f"❌ Error sending OTP: {str(e)}")
            return False, str(e)
    
    async def verify_otp(self, api_id, api_hash, phone_number, otp_code, username):
        """Verify OTP and complete authentication"""
        try:
            session_name = f"auth_{username}"
            client = TelegramClient(session_name, api_id, api_hash)
            await client.connect()
            
            # Sign in with OTP
            await client.sign_in(phone_number, otp_code)
            
            # Test if authentication worked
            if await client.is_user_authorized():
                # Test channel access
                test_entity = await client.get_entity('https://t.me/telegram')
                
                await client.disconnect()
                print(f"✅ Successfully authenticated user {username}")
                return True, "Successfully linked Telegram account"
            else:
                await client.disconnect()
                return False, "Authentication failed"
                
        except PhoneCodeInvalidError:
            print(f"❌ Invalid OTP code for {username}")
            return False, "Invalid verification code"
        except SessionPasswordNeededError:
            print(f"❌ 2FA enabled for {username}")
            return False, "Two-factor authentication enabled. Please disable it temporarily."
        except Exception as e:
            print(f"❌ Error verifying OTP: {str(e)}")
            return False, str(e)

# Global instance
simple_auth = SimpleTelegramAuth()

async def test_auth():
    """Test the authentication system"""
    # Get a user from database
    user = db.get_user_by_username('devesh041')  # Replace with actual username
    if not user:
        print("❌ User not found")
        return
    
    api_id = user['api_id']
    api_hash = user['api_hash']
    
    phone = input("Enter phone number: ")
    
    # Send OTP
    success, message = await simple_auth.send_otp(api_id, api_hash, phone, 'devesh041')
    if not success:
        print(f"❌ Failed to send OTP: {message}")
        return
    
    print("✅ OTP sent! Check your Telegram.")
    otp = input("Enter OTP code: ")
    
    # Verify OTP
    success, message = await simple_auth.verify_otp(api_id, api_hash, phone, otp, 'devesh041')
    if success:
        print("✅ Authentication successful!")
        # Update database
        db.update_telegram_link('devesh041', phone)
    else:
        print(f"❌ Authentication failed: {message}")

if __name__ == "__main__":
    asyncio.run(test_auth())
