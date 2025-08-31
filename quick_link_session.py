#!/usr/bin/env python3
"""
Quick utility to link existing authenticated Telegram sessions
This bypasses the OTP process if sessions already exist
"""

import os
from database import db
from telethon import TelegramClient
import asyncio

async def link_existing_sessions():
    """Check for existing sessions and link them to users"""
    
    # Get all users who haven't linked Telegram yet
    users = list(db.users.find({"telegram_linked": {"$ne": True}}))
    
    if not users:
        print("✅ All users already have Telegram linked")
        return
    
    print(f"🔍 Found {len(users)} users without Telegram linking")
    
    # Check for session files
    session_files = []
    for file in os.listdir('.'):
        if file.endswith('.session'):
            session_files.append(file)
    
    print(f"📁 Found session files: {session_files}")
    
    for user in users:
        username = user['username']
        api_id = user['api_id']
        api_hash = user['api_hash']
        
        print(f"\n👤 Checking sessions for user: {username}")
        
        # Try different session names
        session_names = [
            'authenticated_session',
            f'temp_{username}',
            f'monitor_session_{username}',
            f'real_session_{username}'
        ]
        
        for session_name in session_names:
            if f"{session_name}.session" in session_files:
                try:
                    print(f"   🔍 Testing session: {session_name}")
                    
                    client = TelegramClient(session_name, api_id, api_hash)
                    await client.connect()
                    
                    if await client.is_user_authorized():
                        # Test channel access
                        try:
                            test_entity = await client.get_entity('https://t.me/telegram')
                            
                            # Link this session to the user
                            db.update_telegram_link(username, "auto-linked-session")
                            print(f"   ✅ Successfully linked {username} to session {session_name}")
                            
                            await client.disconnect()
                            break
                            
                        except Exception as test_error:
                            print(f"   ⚠️ Session exists but can't access channels: {test_error}")
                            await client.disconnect()
                            continue
                    else:
                        print(f"   ❌ Session {session_name} not authorized")
                        await client.disconnect()
                        continue
                        
                except Exception as e:
                    print(f"   ❌ Error testing session {session_name}: {e}")
                    try:
                        await client.disconnect()
                    except:
                        pass
                    continue
        else:
            print(f"   ❌ No valid sessions found for {username}")

if __name__ == "__main__":
    asyncio.run(link_existing_sessions())
