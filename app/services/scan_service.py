# app/services/scan_service.py
"""
Email scanning service with professional error handling.
"""

import logging
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from app.utils.validators import ValidationError
from app.models.database import DatabaseManager

logger = logging.getLogger(__name__)


class ScanService:
    """Handles email scanning operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize scan service.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
    
    def perform_scan(
        self,
        gmail: str,
        app_password: str,
        limit: int = 10,
        user_email: Optional[str] = None
    ) -> Tuple[Dict, int, Optional[str]]:
        """
        Perform email scan and save results to database.
        
        Args:
            gmail: Gmail account to scan
            app_password: Gmail app password
            limit: Number of recent emails to scan
            user_email: User performing the scan (for multi-user support)
        
        Returns:
            Tuple of (results_dict, scan_id, error_message)
        """
        user_email = user_email or gmail
        scan_id = None
        
        try:
            logger.info(f"Starting scan for user: {user_email}, gmail: {gmail}")
            
            # Perform the actual scan
            from scanner_imap import scan_email_account  # local import to avoid circular
            email_results = scan_email_account(gmail, app_password, limit=limit)
            
            # Save to database
            scan_id = self._save_scan_results(
                user_email=user_email,
                scanned_email=gmail,
                results=email_results
            )
            
            logger.info(f"Scan completed successfully. Scan ID: {scan_id}, Emails found: {len(email_results)}")
            
            return {
                'scan_id': scan_id,
                'results': email_results,
                'count': len(email_results),
                'timestamp': datetime.utcnow().isoformat()
            }, 200, None
        
        except ConnectionError as e:
            error_msg = f"Connection error: Failed to connect to Gmail IMAP server"
            logger.error(f"{error_msg} - {str(e)}")
            return {
                'error': error_msg,
                'details': str(e)
            }, 503, error_msg
        
        except PermissionError as e:
            error_msg = f"Authentication failed: Invalid Gmail or App Password"
            logger.error(f"{error_msg} - {str(e)}")
            return {
                'error': error_msg,
                'details': 'Please verify your Gmail and 16-character App Password'
            }, 401, error_msg
        
        except ValueError as e:
            error_msg = f"Invalid parameter: {str(e)}"
            logger.error(f"{error_msg}")
            return {
                'error': error_msg
            }, 400, error_msg
        
        except Exception as e:
            error_msg = f"Unexpected error during scan: {str(e)}"
            logger.error(f"{error_msg}", exc_info=True)
            
            # Save error to database if scan was created
            if scan_id:
                self._update_scan_status(
                    scan_id=scan_id,
                    status='error',
                    error_message=error_msg
                )
            
            return {
                'error': 'Internal server error',
                'message': error_msg
            }, 500, error_msg
    
    def get_scan_history(
        self,
        user_email: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get scan history for a user.
        
        Args:
            user_email: Email of user to filter by (None = all users)
            limit: Maximum number of records to return
        
        Returns:
            List of scan records
        """
        try:
            if limit > 100:
                limit = 100
            
            if user_email:
                query = """
                    SELECT id, scanned_email, created_at, status
                    FROM scans
                    WHERE user_email = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """
                results = self.db.execute_query(query, (user_email, limit))
            else:
                query = """
                    SELECT id, scanned_email, created_at, status
                    FROM scans
                    ORDER BY created_at DESC
                    LIMIT ?
                """
                results = self.db.execute_query(query, (limit,))
            
            logger.info(f"Retrieved {len(results)} scan records")
            return results
        
        except Exception as e:
            logger.error(f"Error retrieving scan history: {str(e)}", exc_info=True)
            return []
    
    def get_scan_details(self, scan_id: int) -> Optional[Dict]:
        """
        Get detailed results for a specific scan.
        
        Args:
            scan_id: ID of the scan
        
        Returns:
            Scan details or None if not found
        """
        try:
            query = "SELECT result_json FROM scans WHERE id = ?"
            results = self.db.execute_query(query, (scan_id,))
            
            if not results:
                logger.warning(f"Scan not found: {scan_id}")
                return None
            
            result_json = results[0]['result_json']
            return json.loads(result_json)
        
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding scan results: {str(e)}")
            return None
        
        except Exception as e:
            logger.error(f"Error retrieving scan details: {str(e)}", exc_info=True)
            return None
    
    def _save_scan_results(
        self,
        user_email: str,
        scanned_email: str,
        results: List[Dict]
    ) -> int:
        """
        Save scan results to database.
        
        Args:
            user_email: User performing the scan
            scanned_email: Email account being scanned
            results: Scan results from scanner
        
        Returns:
            ID of created scan record
        """
        # Try with status column first (new schema)
        try:
            query = """
                INSERT INTO scans (user_email, scanned_email, created_at, result_json, status)
                VALUES (?, ?, ?, ?, 'completed')
            """
            
            scan_id = self.db.execute_insert(
                query,
                (
                    user_email,
                    scanned_email,
                    datetime.utcnow().isoformat(),
                    json.dumps(results)
                )
            )
        except Exception as e:
            # Fallback to old schema without status column
            if "no column named status" in str(e):
                query = """
                    INSERT INTO scans (user_email, scanned_email, created_at, result_json)
                    VALUES (?, ?, ?, ?)
                """
                
                scan_id = self.db.execute_insert(
                    query,
                    (
                        user_email,
                        scanned_email,
                        datetime.utcnow().isoformat(),
                        json.dumps(results)
                    )
                )
            else:
                raise
        
        logger.debug(f"Saved scan results to database. Scan ID: {scan_id}")
        return scan_id
    
    def _update_scan_status(
        self,
        scan_id: int,
        status: str,
        error_message: Optional[str] = None
    ) -> None:
        """
        Update scan status in database.
        
        Args:
            scan_id: ID of scan to update
            status: New status ('completed', 'error', 'pending')
            error_message: Error message if applicable
        """
        query = """
            UPDATE scans
            SET status = ?, error_message = ?
            WHERE id = ?
        """
        
        self.db.execute_update(query, (status, error_message, scan_id))
        logger.debug(f"Updated scan {scan_id} status to {status}")


class RiskAnalyzer:
    """Analyzes and summarizes risk data."""
    
    @staticmethod
    def get_risk_summary(results: List[Dict]) -> Dict:
        """
        Analyze scan results and provide risk summary.
        
        Args:
            results: List of email scan results
        
        Returns:
            Risk summary statistics
        """
        if not results:
            return {
                'total_emails': 0,
                'safe_emails': 0,
                'suspicious_emails': 0,
                'dangerous_emails': 0,
                'average_risk_score': 0
            }
        
        risk_levels = {level: 0 for level in ['SAFE', 'SUSPICIOUS', 'DANGEROUS']}
        total_score = 0
        emails_with_urls = 0
        emails_with_attachments = 0
        
        for email in results:
            raw_level = (email.get('risk_level') or 'SAFE').upper()
            # Normalize incoming levels to expected buckets
            normalized = {
                'DANGER': 'DANGEROUS',
                'DANGEROUS': 'DANGEROUS',
                'WARNING': 'SUSPICIOUS',
                'SUSPICIOUS': 'SUSPICIOUS',
                'SAFE': 'SAFE'
            }.get(raw_level, 'SAFE')
            risk_levels[normalized] += 1
            total_score += email.get('risk_score', 0)
            
            if email.get('urls'):
                emails_with_urls += 1
            if email.get('attachments'):
                emails_with_attachments += 1
        
        return {
            'total_emails': len(results),
            'safe_emails': risk_levels['SAFE'],
            'suspicious_emails': risk_levels['SUSPICIOUS'],
            'dangerous_emails': risk_levels['DANGEROUS'],
            'average_risk_score': round(total_score / len(results), 2),
            'emails_with_urls': emails_with_urls,
            'emails_with_attachments': emails_with_attachments
        }
