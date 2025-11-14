import sqlite3
import os

print("🔧 Setting up users table in your database...")

try:
    # Connect to your existing database
    conn = sqlite3.connect("claims.db")
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    print("✅ Users table created successfully!")
    
    # Show all tables now
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\n📊 All tables in your database:")
    for table in tables:
        print(f"   - {table[0]}")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Users table setup complete!")
    print("   Now we can store users in the database!")
    
except Exception as e:
    print(f"❌ Error: {e}")