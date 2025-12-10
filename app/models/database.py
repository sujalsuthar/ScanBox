# app/models/database.py
"""
Database management and initialization.
"""

import sqlite3
import logging
from flask import g, Flask
from typing import Optional

logger = logging.getLogger(__name__)


def get_db() -> sqlite3.Connection:
    """
    Get database connection for current request context.
    Connections are cached in Flask's g object.
    
    Returns:
        SQLite3 connection object
    """
    from flask import current_app
    
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DB_PATH'],
            detect_types=sqlite3.PARSE_DECLTYPES,
            timeout=5,
            check_same_thread=False
        )
        g.db.execute('PRAGMA journal_mode=WAL;')
        g.db.execute('PRAGMA foreign_keys=ON;')
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None) -> None:
    """
    Close database connection at end of request.
    
    Args:
        e: Exception that occurred (if any)
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app: Flask) -> None:
    """
    Initialize database with schema on application startup.
    Handles schema migrations for existing databases.
    
    Args:
        app: Flask application instance
    """
    from flask import current_app
    
    db_path = app.config['DB_PATH']
    
    # Create connection
    conn = sqlite3.connect(db_path, timeout=5, check_same_thread=False)
    c = conn.cursor()
    c.execute('PRAGMA journal_mode=WAL;')
    c.execute('PRAGMA foreign_keys=ON;')
    
    # Create tables
    c.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        scanned_email TEXT NOT NULL,
        created_at TEXT NOT NULL,
        result_json TEXT NOT NULL
    );
    """)
    
    # Migration: Add status and error_message columns if they don't exist
    try:
        c.execute("ALTER TABLE scans ADD COLUMN status TEXT DEFAULT 'completed';")
        logger.info("Added 'status' column to scans table")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        c.execute("ALTER TABLE scans ADD COLUMN error_message TEXT;")
        logger.info("Added 'error_message' column to scans table")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS scan_emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER NOT NULL,
        subject TEXT,
        sender TEXT,
        date_received TEXT,
        risk_level TEXT,
        risk_score INTEGER,
        urls_json TEXT,
        attachments_json TEXT,
        snippet TEXT,
        FOREIGN KEY (scan_id) REFERENCES scans(id)
    );
    """)
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS api_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        endpoint TEXT NOT NULL,
        method TEXT NOT NULL,
        status_code INTEGER,
        response_time_ms REAL,
        user_agent TEXT,
        remote_addr TEXT
    );
    """)
    
    # Create indexes for performance
    c.execute("CREATE INDEX IF NOT EXISTS idx_scans_user ON scans(user_email);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_scans_created ON scans(created_at);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_scan_emails_scan ON scan_emails(scan_id);")
    
    conn.commit()
    conn.close()
    
    logger.info(f"Database initialized at {db_path}")


class DatabaseManager:
    """Manages database operations with connection pooling."""
    
    def __init__(self, db_path: str):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a new database connection."""
        conn = sqlite3.connect(self.db_path, timeout=5, check_same_thread=False)
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.execute('PRAGMA foreign_keys=ON;')
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL SELECT query
            params: Query parameters
        
        Returns:
            List of rows as dictionaries
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """
        Execute an INSERT query and return last row ID.
        
        Args:
            query: SQL INSERT query
            params: Query parameters
        
        Returns:
            ID of inserted row
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute an UPDATE query and return number of affected rows.
        
        Args:
            query: SQL UPDATE query
            params: Query parameters
        
        Returns:
            Number of rows affected
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()


# For Flask request context
def get_db_from_context() -> sqlite3.Connection:
    """Get database connection from Flask request context."""
    from flask import g, current_app
    
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DB_PATH'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db
