"""Email account management with IMAP integration"""

import logging
import imaplib
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from email.parser import Parser
from email.header import decode_header
import sqlite3

logger = logging.getLogger(__name__)


class EmailAccountManager:
    """Manage user email accounts with IMAP connection"""
    
    def __init__(self, db_path: str):
        """Initialize email account manager"""
        self.db_path = db_path
        self._init_db_schema()
    
    def _init_db_schema(self):
        """Create email account tables if they don't exist"""
        conn = sqlite3.connect(self.db_path, timeout=5, check_same_thread=False)
        c = conn.cursor()
        
        # Email accounts table
        c.execute("""
        CREATE TABLE IF NOT EXISTS email_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            email_address TEXT NOT NULL UNIQUE,
            email_provider TEXT DEFAULT 'gmail',
            imap_password TEXT NOT NULL,
            last_scan_time TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)
        
        # Real emails table
        c.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            email_uid TEXT NOT NULL,
            from_address TEXT,
            subject TEXT,
            body_preview TEXT,
            received_date TEXT,
            has_attachment INTEGER DEFAULT 0,
            attachment_names TEXT,
            raw_headers TEXT,
            fetched_at TEXT NOT NULL,
            FOREIGN KEY (account_id) REFERENCES email_accounts(id) ON DELETE CASCADE,
            UNIQUE(account_id, email_uid)
        );
        """)
        
        # Email analysis results table
        c.execute("""
        CREATE TABLE IF NOT EXISTS email_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id INTEGER NOT NULL,
            threat_level TEXT,
            risk_score INTEGER,
            threats_detected TEXT,
            ai_explanation TEXT,
            recommendations TEXT,
            analyzed_at TEXT NOT NULL,
            user_reviewed INTEGER DEFAULT 0,
            FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
        );
        """)
        
        # Create indexes
        c.execute("CREATE INDEX IF NOT EXISTS idx_emails_account ON emails(account_id);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_analysis_email ON email_analysis(email_id);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_accounts_user ON email_accounts(user_id);")
        
        conn.commit()
        conn.close()
        logger.info("Email account schema initialized")
    
    def add_email_account(self, user_id: int, email_address: str, imap_password: str, 
                         email_provider: str = 'gmail') -> Tuple[bool, Optional[int], str]:
        """
        Add email account for user
        
        Args:
            user_id: User ID
            email_address: Email address (e.g., user@gmail.com)
            imap_password: IMAP password or app password
            email_provider: Email provider (gmail, outlook, yahoo, etc)
        
        Returns:
            (success, account_id, message)
        """
        try:
            # Test IMAP connection first
            success, msg = self._test_imap_connection(email_address, imap_password, email_provider)
            if not success:
                return False, None, f"Connection failed: {msg}"
            
            # Store in database
            conn = sqlite3.connect(self.db_path, timeout=5, check_same_thread=False)
            c = conn.cursor()
            
            c.execute("""
            INSERT INTO email_accounts 
            (user_id, email_address, email_provider, imap_password, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (user_id, email_address, email_provider, imap_password, datetime.utcnow().isoformat()))
            
            conn.commit()
            account_id = c.lastrowid
            conn.close()
            
            logger.info(f"Email account added for user {user_id}: {email_address}")
            return True, account_id, "Email account connected successfully"
        
        except sqlite3.IntegrityError:
            return False, None, "This email address is already connected"
        except Exception as e:
            logger.error(f"Error adding email account: {str(e)}")
            return False, None, f"Error: {str(e)}"
    
    def _test_imap_connection(self, email_address: str, password: str, 
                             provider: str = 'gmail') -> Tuple[bool, str]:
        """Test IMAP connection"""
        try:
            imap_servers = {
                'gmail': 'imap.gmail.com',
                'outlook': 'outlook.office365.com',
                'yahoo': 'imap.mail.yahoo.com',
                'hotmail': 'outlook.office365.com'
            }
            
            server = imap_servers.get(provider, 'imap.gmail.com')
            
            mail = imaplib.IMAP4_SSL(server, 993)
            mail.login(email_address, password)
            mail.logout()
            
            return True, "Connection successful"
        
        except imaplib.IMAP4.error as e:
            return False, f"IMAP error: {str(e)}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def fetch_emails(self, account_id: int, limit: int = 20) -> Tuple[bool, List[Dict], str]:
        """
        Fetch recent emails from account
        
        Args:
            account_id: Email account ID
            limit: Number of recent emails to fetch
        
        Returns:
            (success, emails, message)
        """
        try:
            # Get account details
            conn = sqlite3.connect(self.db_path, timeout=5, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT email_address, imap_password, email_provider FROM email_accounts WHERE id = ?", 
                     (account_id,))
            row = c.fetchone()
            conn.close()
            
            if not row:
                return False, [], "Account not found"
            
            email_address, password, provider = row
            
            # Connect to IMAP
            imap_servers = {
                'gmail': 'imap.gmail.com',
                'outlook': 'outlook.office365.com',
                'yahoo': 'imap.mail.yahoo.com'
            }
            server = imap_servers.get(provider, 'imap.gmail.com')
            
            mail = imaplib.IMAP4_SSL(server, 993)
            mail.login(email_address, password)
            mail.select('INBOX')
            
            # Fetch email UIDs
            status, messages = mail.search(None, 'ALL')
            email_uids = messages[0].split()[-limit:]  # Get last 'limit' emails
            
            emails = []
            parser = Parser()
            
            for uid in reversed(email_uids):  # Reverse to get newest first
                status, msg_data = mail.fetch(uid, '(RFC822)')
                
                if status == 'OK':
                    msg = parser.parsestr(msg_data[0][1].decode('utf-8', errors='ignore'))
                    
                    # Extract email info
                    from_addr = msg.get('From', 'Unknown')
                    subject = msg.get('Subject', '(No Subject)')
                    
                    # Decode subject if needed
                    if isinstance(subject, bytes):
                        subject = subject.decode('utf-8', errors='ignore')
                    
                    # Get body preview
                    body = ""
                    if msg.is_multipart():
                        for part in msg.get_payload():
                            if part.get_content_type() == 'text/plain':
                                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                break
                    else:
                        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                    
                    body_preview = body[:200] if body else ""
                    
                    # Get attachments
                    attachments = []
                    has_attachment = 0
                    for part in msg.walk():
                        if part.get_content_disposition() == 'attachment':
                            has_attachment = 1
                            attachments.append(part.get_filename())
                    
                    email_obj = {
                        'uid': uid.decode('utf-8'),
                        'from': from_addr,
                        'subject': subject,
                        'body_preview': body_preview,
                        'date': msg.get('Date', ''),
                        'has_attachment': has_attachment,
                        'attachments': attachments
                    }
                    
                    # Store in database
                    conn = sqlite3.connect(self.db_path, timeout=5, check_same_thread=False)
                    c = conn.cursor()
                    
                    try:
                        c.execute("""
                        INSERT INTO emails 
                        (account_id, email_uid, from_address, subject, body_preview, 
                         received_date, has_attachment, attachment_names, fetched_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (account_id, email_obj['uid'], from_addr, subject, 
                              body_preview, email_obj['date'], has_attachment,
                              json.dumps(attachments), datetime.utcnow().isoformat()))
                        conn.commit()
                    except sqlite3.IntegrityError:
                        pass  # Email already exists
                    finally:
                        conn.close()
                    
                    emails.append(email_obj)
            
            mail.close()
            mail.logout()
            
            logger.info(f"Fetched {len(emails)} emails for account {account_id}")
            return True, emails, f"Fetched {len(emails)} emails"
        
        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}", exc_info=True)
            return False, [], f"Error: {str(e)}"
    
    def get_user_accounts(self, user_id: int) -> List[Dict]:
        """Get all email accounts for user"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=5, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            c.execute("""
            SELECT id, email_address, email_provider, last_scan_time, is_active, created_at
            FROM email_accounts WHERE user_id = ? AND is_active = 1
            """, (user_id,))
            
            accounts = [dict(row) for row in c.fetchall()]
            conn.close()
            
            return accounts
        except Exception as e:
            logger.error(f"Error getting user accounts: {str(e)}")
            return []
    
    def disconnect_account(self, account_id: int) -> bool:
        """Disconnect email account"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=5, check_same_thread=False)
            c = conn.cursor()
            
            c.execute("UPDATE email_accounts SET is_active = 0 WHERE id = ?", (account_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"Disconnected email account {account_id}")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting account: {str(e)}")
            return False
    
    def get_analysis_stats(self, account_id: int) -> Dict:
        """Get analysis statistics for account"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=5, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            # Total emails
            c.execute("SELECT COUNT(*) as count FROM emails WHERE account_id = ?", (account_id,))
            total = c.fetchone()['count']
            
            # Threat levels
            c.execute("""
            SELECT threat_level, COUNT(*) as count 
            FROM email_analysis ea
            JOIN emails e ON ea.email_id = e.id
            WHERE e.account_id = ?
            GROUP BY threat_level
            """, (account_id,))
            
            threat_counts = {row['threat_level']: row['count'] for row in c.fetchall()}
            
            # Average risk score
            c.execute("""
            SELECT AVG(risk_score) as avg_score
            FROM email_analysis ea
            JOIN emails e ON ea.email_id = e.id
            WHERE e.account_id = ?
            """, (account_id,))
            
            avg_score = c.fetchone()['avg_score'] or 0
            
            conn.close()
            
            return {
                'total_emails': total,
                'threat_breakdown': threat_counts,
                'average_risk_score': round(avg_score, 1),
                'security_score': round(100 - (avg_score if avg_score else 0), 1)
            }
        except Exception as e:
            logger.error(f"Error getting analysis stats: {str(e)}")
            return {}
