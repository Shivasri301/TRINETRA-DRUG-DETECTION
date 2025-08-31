from database import db
from datetime import datetime

# Update Devesh's API credentials with the NEWEST ones (Desktop platform)
new_api_id = 24748004
new_api_hash = "67a1e3c7ea60479f708baf3ad52dc0cf"

print("🔄 Updating API credentials for user 'Devesh'...")

result = db.users.update_one(
    {"username": "Devesh"},
    {
        "$set": {
            "api_id": new_api_id,
            "api_hash": new_api_hash,
            "credentials_updated_at": datetime.utcnow()
        }
    }
)

if result.modified_count > 0:
    print("✅ Credentials updated successfully!")
    
    # Verify the update
    user = db.get_user_by_username("Devesh")
    print(f"✅ Verified - New API ID: {user['api_id']}")
    print(f"✅ Verified - New API Hash: {user['api_hash'][:10]}...")
else:
    print("❌ Failed to update credentials")

print("🧹 Cleaning up old session files...")
import glob
import os

session_files = glob.glob("*.session")
for session_file in session_files:
    try:
        os.remove(session_file)
        print(f"🗑️ Removed: {session_file}")
    except:
        pass

print("✅ Update complete!")
