import sqlite3
import logging
from threading import local

logger = logging.getLogger(__name__)

# Thread-local storage for database connections
_thread_local = local()

def get_db_connection():
    """Get a database connection with proper error handling"""
    try:
        # Check if connection already exists for this thread
        if hasattr(_thread_local, 'db_connection'):
            conn = _thread_local.db_connection
            try:
                # Test if connection is still alive
                conn.execute("SELECT 1")
                return conn
            except sqlite3.ProgrammingError:
                # Connection is closed, create new one
                pass
            except sqlite3.Error:
                # Connection has error, create new one
                pass
        
        # Create new connection
        conn = sqlite3.connect('claims.db', timeout=30)
        conn.row_factory = sqlite3.Row
        _thread_local.db_connection = conn
        logger.info("Created new database connection")
        return conn
        
    except Exception as e:
        logger.error(f"Failed to create database connection: {str(e)}")
        raise

def close_db_connection():
    """Close the database connection for this thread"""
    if hasattr(_thread_local, 'db_connection'):
        try:
            _thread_local.db_connection.close()
            delattr(_thread_local, 'db_connection')
            logger.info("Closed database connection")
        except Exception as e:
            logger.error(f"Error closing database connection: {str(e)}")

def init_db():
    """Initialize the database with required tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create claims table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS claims (
                id TEXT PRIMARY KEY,
                status TEXT DEFAULT 'pending',
                amount REAL,
                description TEXT,
                user_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP NULL,
                error_message TEXT NULL
            )
        ''')
        
        # Create users table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        close_db_connection()