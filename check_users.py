from database import db

print("Checking users in database...")
users = list(db.users.find())

if not users:
    print("No users found in database!")
else:
    for user in users:
        print(f"Username: {user['username']}")
        print(f"API ID: {user.get('api_id', 'Not set')}")
        api_hash = user.get('api_hash', 'Not set')
        if api_hash != 'Not set':
            print(f"API Hash: {api_hash[:10]}... (truncated)")
        else:
            print(f"API Hash: {api_hash}")
        print(f"Telegram Linked: {user.get('telegram_linked', False)}")
        print("---")
