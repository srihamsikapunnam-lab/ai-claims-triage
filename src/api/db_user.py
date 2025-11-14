import sqlite3
import hashlib
import os

class DBUser:
    def __init__(self):
        # Find the database file in the project root
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(os.path.dirname(current_dir))
        self.db_path = os.path.join(project_root, "claims.db")
        print(f"🔍 Database path: {self.db_path}")
    
    def hash_password(self, password: str) -> str:
        """Simple password hashing"""
        salt = "ai_claims_salt_2024"
        combined = password + salt
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def create_user(self, username: str, email: str, password: str, role: str = "user"):
        """Create a new user in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, role))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"✅ User {username} saved to database with ID: {user_id}")
            return user_id
            
        except sqlite3.IntegrityError:
            raise Exception("Username or email already exists")
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")
    
    def get_user_by_username(self, username: str):
        """Get user by username"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, password_hash, role, created_at, is_active
                FROM users WHERE username = ?
            ''', (username,))
            
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                return {
                    "id": user_data[0],
                    "username": user_data[1],
                    "email": user_data[2],
                    "password_hash": user_data[3],
                    "role": user_data[4],
                    "created_at": user_data[5],
                    "is_active": bool(user_data[6])
                }
            return None
            
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")
    
    def verify_user(self, username: str, password: str):
        """Verify user credentials"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        
        input_hash = self.hash_password(password)
        if input_hash == user["password_hash"]:
            return user
        return None

# Global database user instance
db_user = DBUser()