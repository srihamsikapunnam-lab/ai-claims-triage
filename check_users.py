import sqlite3
import os

print("🔍 Checking users in database...")

# Use the same path logic
current_dir = os.path.dirname(__file__)
db_path = os.path.join(current_dir, "claims.db")

print(f"📁 Database path: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Count users
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"📊 Total users in database: {user_count}")
    
    # Show all users
    if user_count > 0:
        cursor.execute("SELECT id, username, email, role, created_at FROM users")
        users = cursor.fetchall()
        print("\n👥 All users:")
        for user in users:
            print(f"   - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Role: {user[3]}")
    
    conn.close()
    print("\n🎉 Database check complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")