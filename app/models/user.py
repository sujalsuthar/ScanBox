"""User model for authentication"""

import sqlite3
from datetime import datetime
from app.models.database import DatabaseManager
from app.auth.utils import AuthUtils
import logging

logger = logging.getLogger(__name__)

class User:
    """User model for storing and managing user accounts"""
    
    @staticmethod
    def init_table():
        """Initialize users table"""
        import sqlite3
        db_path = 'scan_history.db'
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        try:
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_admin INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    profile_data TEXT
                )
            """)
            conn.commit()
            logger.info("Users table initialized")
        except sqlite3.OperationalError as e:
            if "already exists" not in str(e):
                logger.error(f"Error creating users table: {e}")
        finally:
            conn.close()

    @staticmethod
    def create_user(email: str, password: str, is_admin: bool = False) -> dict:
        """Create a new user"""
        try:
            password_hash = AuthUtils.hash_password(password)
            
            db_path = 'scan_history.db'
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            c.execute("""
                INSERT INTO users (email, password_hash, is_admin)
                VALUES (?, ?, ?)
            """, (email, password_hash, 1 if is_admin else 0))
            
            conn.commit()
            user_id = c.lastrowid
            conn.close()
            
            logger.info(f"User created: {email}")
            return {'id': user_id, 'email': email, 'success': True}
            
        except sqlite3.IntegrityError:
            logger.warning(f"User already exists: {email}")
            return {'error': 'User already exists', 'success': False}
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return {'error': str(e), 'success': False}

    @staticmethod
    def get_user_by_email(email: str) -> dict:
        """Get user by email"""
        try:
            db_path = 'scan_history.db'
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            c.execute("""
                SELECT id, email, password_hash, is_admin, is_active, created_at, last_login
                FROM users WHERE email = ?
            """, (email,))
            
            row = c.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'email': row[1],
                    'password_hash': row[2],
                    'is_admin': bool(row[3]),
                    'is_active': bool(row[4]),
                    'created_at': row[5],
                    'last_login': row[6]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    @staticmethod
    def verify_credentials(email: str, password: str) -> dict:
        """Verify user credentials"""
        user = User.get_user_by_email(email)
        
        if not user:
            return {'success': False, 'error': 'Invalid email or password'}
        
        if not user['is_active']:
            return {'success': False, 'error': 'Account is inactive'}
        
        if not AuthUtils.verify_password(user['password_hash'], password):
            return {'success': False, 'error': 'Invalid email or password'}
        
        # Update last login
        try:
            db_path = 'scan_history.db'
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user['id'],))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
        
        return {
            'success': True,
            'user_id': user['id'],
            'email': user['email'],
            'is_admin': user['is_admin']
        }

    @staticmethod
    def update_password(user_id: int, new_password: str) -> bool:
        """Update user password"""
        try:
            password_hash = AuthUtils.hash_password(new_password)
            
            db_path = 'scan_history.db'
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
            conn.commit()
            conn.close()
            
            logger.info(f"Password updated for user ID: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating password: {e}")
            return False

    @staticmethod
    def get_user_by_id(user_id: int) -> dict:
        """Get user by ID"""
        try:
            db_path = 'scan_history.db'
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            c.execute("""
                SELECT id, email, is_admin, is_active, created_at, last_login
                FROM users WHERE id = ?
            """, (user_id,))
            
            row = c.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'email': row[1],
                    'is_admin': bool(row[2]),
                    'is_active': bool(row[3]),
                    'created_at': row[4],
                    'last_login': row[5]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
