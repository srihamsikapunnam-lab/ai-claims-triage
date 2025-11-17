"""
Add LIME explanation and length_of_stay fields to claims table
"""
import sqlite3
import json
from pathlib import Path

# Connect to database
db_path = Path("claims.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🔧 Adding new fields to claims table...")

try:
    # Add lime_explanation column (stores JSON array)
    try:
        cursor.execute("ALTER TABLE claims ADD COLUMN lime_explanation TEXT")
        print("✅ Added lime_explanation column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print("ℹ️  lime_explanation column already exists")
        else:
            raise
    
    # Add model_version column
    try:
        cursor.execute("ALTER TABLE claims ADD COLUMN model_version TEXT")
        print("✅ Added model_version column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print("ℹ️  model_version column already exists")
        else:
            raise
    
    # Add length_of_stay column
    try:
        cursor.execute("ALTER TABLE claims ADD COLUMN length_of_stay INTEGER DEFAULT 1")
        print("✅ Added length_of_stay column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print("ℹ️  length_of_stay column already exists")
        else:
            raise
    
    # Calculate length_of_stay for existing claims
    cursor.execute("""
        UPDATE claims
        SET length_of_stay = (
            julianday(discharge_date) - julianday(admission_date)
        )
        WHERE length_of_stay IS NULL AND admission_date IS NOT NULL AND discharge_date IS NOT NULL
    """)
    updated = cursor.rowcount
    print(f"✅ Updated length_of_stay for {updated} existing claims")
    
    conn.commit()
    print("\n✅ Database migration completed successfully!")
    
except Exception as e:
    conn.rollback()
    print(f"\n❌ Migration failed: {e}")
    raise

finally:
    conn.close()

print("\n📊 Verifying schema...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(claims)")
columns = cursor.fetchall()
print("\nClaims table columns:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")
conn.close()
