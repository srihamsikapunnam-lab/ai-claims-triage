import sqlite3
import os

print("🔍 Checking your database...")

# Check if database exists
if not os.path.exists("claims.db"):
    print("❌ claims.db file not found!")
    print("💡 Current directory files:")
    for file in os.listdir("."):
        if file.endswith(".db") or file.endswith(".sqlite"):
            print(f"   - {file}")
    exit()

try:
    # Connect to database
    conn = sqlite3.connect("claims.db")
    cursor = conn.cursor()
    
    print("✅ Connected to claims.db successfully!")
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"\n📊 Found {len(tables)} tables:")
    for table in tables:
        print(f"   - {table[0]}")
    
    # Check each table structure
    for table in tables:
        table_name = table[0]
        print(f"\n🔍 Table: {table_name}")
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        if columns:
            print("   Columns:")
            for col in columns:
                print(f"     - {col[1]} ({col[2]})")
        else:
            print("   No columns found")
        
        # Show row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"   Rows: {count}")
        
        # Show first row if exists
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            first_row = cursor.fetchone()
            print(f"   First row sample: {first_row}")
    
    conn.close()
    print("\n🎉 Database check completed!")
    
except Exception as e:
    print(f"❌ Error: {e}")