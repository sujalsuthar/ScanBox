"""Email Scheduler for automated recurring scans"""

import sqlite3
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Scheduler:
    """Manage scheduled email scans"""
    
    FREQUENCY_OPTIONS = ['daily', 'weekly', 'monthly', 'every_2_hours']
    
    @staticmethod
    def init_table():
        """Initialize scheduled_scans table"""
        db_path = 'scan_history.db'
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        try:
            c.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    user_email TEXT NOT NULL,
                    gmail_account TEXT NOT NULL,
                    frequency TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    next_scan TIMESTAMP,
                    last_scan TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)
            conn.commit()
            logger.info("scheduled_scans table initialized")
        except sqlite3.OperationalError as e:
            if "already exists" not in str(e):
                logger.error(f"Error creating scheduled_scans table: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def create_schedule(user_id: int, user_email: str, gmail_account: str, 
                       frequency: str, app_password: str) -> dict:
        """Create a new scheduled scan"""
        try:
            if frequency not in Scheduler.FREQUENCY_OPTIONS:
                return {'success': False, 'error': f'Invalid frequency. Must be one of: {Scheduler.FREQUENCY_OPTIONS}'}
            
            conn = sqlite3.connect('scan_history.db')
            c = conn.cursor()
            
            # Calculate next scan time
            next_scan = Scheduler._calculate_next_scan(frequency)
            
            c.execute("""
                INSERT INTO scheduled_scans 
                (user_id, user_email, gmail_account, frequency, next_scan)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, user_email, gmail_account, frequency, next_scan))
            
            conn.commit()
            schedule_id = c.lastrowid
            conn.close()
            
            logger.info(f"Schedule created: {schedule_id} for {gmail_account}")
            return {
                'success': True,
                'schedule_id': schedule_id,
                'next_scan': next_scan,
                'frequency': frequency
            }
            
        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_user_schedules(user_id: int) -> dict:
        """Get all schedules for a user"""
        try:
            conn = sqlite3.connect('scan_history.db')
            c = conn.cursor()
            
            c.execute("""
                SELECT id, user_email, gmail_account, frequency, is_active, 
                       created_at, next_scan, last_scan
                FROM scheduled_scans
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
            
            schedules = []
            for row in c.fetchall():
                schedules.append({
                    'id': row[0],
                    'user_email': row[1],
                    'gmail_account': row[2],
                    'frequency': row[3],
                    'is_active': bool(row[4]),
                    'created_at': row[5],
                    'next_scan': row[6],
                    'last_scan': row[7]
                })
            
            conn.close()
            return {'success': True, 'schedules': schedules}
            
        except Exception as e:
            logger.error(f"Error getting schedules: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def update_schedule(schedule_id: int, frequency: str = None, 
                       is_active: bool = None) -> dict:
        """Update a schedule"""
        try:
            conn = sqlite3.connect('scan_history.db')
            c = conn.cursor()
            
            updates = []
            params = []
            
            if frequency:
                if frequency not in Scheduler.FREQUENCY_OPTIONS:
                    return {'success': False, 'error': f'Invalid frequency'}
                updates.append("frequency = ?")
                params.append(frequency)
                
                # Recalculate next scan
                next_scan = Scheduler._calculate_next_scan(frequency)
                updates.append("next_scan = ?")
                params.append(next_scan)
            
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)
            
            if not updates:
                return {'success': False, 'error': 'No updates provided'}
            
            params.append(schedule_id)
            query = f"UPDATE scheduled_scans SET {', '.join(updates)} WHERE id = ?"
            
            c.execute(query, params)
            conn.commit()
            conn.close()
            
            logger.info(f"Schedule updated: {schedule_id}")
            return {'success': True, 'message': 'Schedule updated'}
            
        except Exception as e:
            logger.error(f"Error updating schedule: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def delete_schedule(schedule_id: int) -> dict:
        """Delete a schedule"""
        try:
            conn = sqlite3.connect('scan_history.db')
            c = conn.cursor()
            
            c.execute("DELETE FROM scheduled_scans WHERE id = ?", (schedule_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"Schedule deleted: {schedule_id}")
            return {'success': True, 'message': 'Schedule deleted'}
            
        except Exception as e:
            logger.error(f"Error deleting schedule: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_pending_scans() -> list:
        """Get all schedules that are due for scanning"""
        try:
            conn = sqlite3.connect('scan_history.db')
            c = conn.cursor()
            
            current_time = datetime.now().isoformat()
            
            c.execute("""
                SELECT id, user_id, user_email, gmail_account
                FROM scheduled_scans
                WHERE is_active = 1 AND next_scan <= ?
                ORDER BY next_scan ASC
            """, (current_time,))
            
            pending = []
            for row in c.fetchall():
                pending.append({
                    'schedule_id': row[0],
                    'user_id': row[1],
                    'user_email': row[2],
                    'gmail_account': row[3]
                })
            
            conn.close()
            return pending
            
        except Exception as e:
            logger.error(f"Error getting pending scans: {e}")
            return []
    
    @staticmethod
    def mark_scan_complete(schedule_id: int) -> bool:
        """Mark a scheduled scan as complete"""
        try:
            conn = sqlite3.connect('scan_history.db')
            c = conn.cursor()
            
            # Get current frequency
            c.execute("SELECT frequency FROM scheduled_scans WHERE id = ?", (schedule_id,))
            row = c.fetchone()
            
            if not row:
                return False
            
            frequency = row[0]
            next_scan = Scheduler._calculate_next_scan(frequency)
            
            c.execute("""
                UPDATE scheduled_scans 
                SET last_scan = CURRENT_TIMESTAMP, next_scan = ?
                WHERE id = ?
            """, (next_scan, schedule_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Schedule marked complete: {schedule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error marking scan complete: {e}")
            return False
    
    @staticmethod
    def _calculate_next_scan(frequency: str) -> str:
        """Calculate next scan time based on frequency"""
        now = datetime.now()
        
        if frequency == 'daily':
            next_scan = now + timedelta(days=1)
        elif frequency == 'weekly':
            next_scan = now + timedelta(weeks=1)
        elif frequency == 'monthly':
            next_scan = now + timedelta(days=30)
        elif frequency == 'every_2_hours':
            next_scan = now + timedelta(hours=2)
        else:
            next_scan = now + timedelta(days=1)
        
        return next_scan.isoformat()
