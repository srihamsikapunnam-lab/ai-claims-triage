import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_enhanced_database():
    """Initialize enhanced database with all required tables"""
    try:
        conn = sqlite3.connect('claims.db')
        cursor = conn.cursor()
        
        # Users table with enhanced fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'customer',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Enhanced claims table with workflow fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS claims (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'submitted',
                current_stage TEXT DEFAULT 'submission',
                patient_age INTEGER,
                diagnosis TEXT,
                admission_date TEXT,
                discharge_date TEXT,
                claimed_amount REAL,
                description TEXT,
                risk_score REAL,
                risk_category TEXT,
                prediction TEXT,
                explanation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                document_type TEXT NOT NULL,
                file_size INTEGER,
                uploaded_by INTEGER NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                FOREIGN KEY (claim_id) REFERENCES claims(id),
                FOREIGN KEY (uploaded_by) REFERENCES users(id)
            )
        ''')
        
        # Claim status history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS claim_status_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_id TEXT NOT NULL,
                status TEXT NOT NULL,
                notes TEXT,
                changed_by INTEGER NOT NULL,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (claim_id) REFERENCES claims(id),
                FOREIGN KEY (changed_by) REFERENCES users(id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_claims_user ON claims(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_claims_risk ON claims(risk_score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_claim ON documents(claim_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_claim ON claim_status_history(claim_id)')
        
        conn.commit()
        logger.info("✅ Enhanced database initialized successfully")
        
        # Create demo users if table is empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            from auth.utils import get_password_hash
            
            demo_users = [
                ('customer@demo.com', 'John Doe', get_password_hash('password123'), 'customer'),
                ('admin@demo.com', 'Admin User', get_password_hash('admin123'), 'company_admin'),
                ('staff@demo.com', 'Staff User', get_password_hash('staff123'), 'company_staff')
            ]
            
            cursor.executemany('''
                INSERT INTO users (email, full_name, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', demo_users)
            
            conn.commit()
            logger.info("✅ Demo users created:")
            logger.info("   Customer: customer@demo.com / password123")
            logger.info("   Admin: admin@demo.com / admin123")
            logger.info("   Staff: staff@demo.com / staff123")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {str(e)}")
        raise

if __name__ == "__main__":
    init_enhanced_database()
