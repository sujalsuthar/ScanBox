"""Analytics module for advanced reporting and insights"""

import json
import sqlite3
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Analytics:
    """Advanced analytics for email scanning data"""
    
    @staticmethod
    def get_threat_trends(days: int = 30) -> dict:
        """Get threat trends over time"""
        try:
            conn = sqlite3.connect('scan_history.db')
            c = conn.cursor()
            
            # Get scans from last N days
            date_threshold = (datetime.now() - timedelta(days=days)).isoformat()
            
            c.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as total_scans,
                       SUM(CASE WHEN result_json LIKE '%SAFE%' THEN 1 ELSE 0 END) as safe,
                       SUM(CASE WHEN result_json LIKE '%SUSPICIOUS%' THEN 1 ELSE 0 END) as suspicious,
                       SUM(CASE WHEN result_json LIKE '%DANGER%' THEN 1 ELSE 0 END) as danger
                FROM scans
                WHERE created_at >= ?
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """, (date_threshold,))
            
            rows = c.fetchall()
            conn.close()
            
            trends = []
            for row in rows:
                trends.append({
                    'date': row[0],
                    'total_scans': row[1],
                    'safe': row[2] or 0,
                    'suspicious': row[3] or 0,
                    'danger': row[4] or 0
                })
            
            return {'success': True, 'trends': trends}
            
        except Exception as e:
            logger.error(f"Error getting threat trends: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_risk_distribution() -> dict:
        """Get distribution of risk scores"""
        try:
            conn = sqlite3.connect('scan_history.db')
            c = conn.cursor()
            
            c.execute("""
                SELECT 
                    SUM(CASE WHEN result_json LIKE '%"risk_score": 1%' OR result_json LIKE '%"risk_score": 2%' THEN 1 ELSE 0 END) as critical,
                    SUM(CASE WHEN result_json LIKE '%"risk_score": 3%' OR result_json LIKE '%"risk_score": 4%' THEN 1 ELSE 0 END) as high,
                    SUM(CASE WHEN result_json LIKE '%"risk_score": 5%' OR result_json LIKE '%"risk_score": 6%' THEN 1 ELSE 0 END) as medium,
                    SUM(CASE WHEN result_json LIKE '%"risk_score": 7%' OR result_json LIKE '%"risk_score": 8%' THEN 1 ELSE 0 END) as low,
                    SUM(CASE WHEN result_json LIKE '%"risk_score": 9%' OR result_json LIKE '%"risk_score": 10%' THEN 1 ELSE 0 END) as minimal
                FROM scans
            """)
            
            row = c.fetchone()
            conn.close()
            
            return {
                'success': True,
                'distribution': {
                    'critical': row[0] or 0,
                    'high': row[1] or 0,
                    'medium': row[2] or 0,
                    'low': row[3] or 0,
                    'minimal': row[4] or 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting risk distribution: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_top_threats(limit: int = 10) -> dict:
        """Get most common threat types"""
        try:
            conn = sqlite3.connect('scan_history.db')
            c = conn.cursor()
            
            c.execute("""
                SELECT result_json FROM scans
                WHERE result_json IS NOT NULL
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit * 5,))
            
            rows = c.fetchall()
            conn.close()
            
            threat_counts = {}
            
            for row in rows:
                try:
                    data = json.loads(row[0])
                    emails = data.get('emails', [])
                    
                    for email in emails:
                        risk_level = email.get('risk_level', 'UNKNOWN')
                        threat_counts[risk_level] = threat_counts.get(risk_level, 0) + 1
                except:
                    pass
            
            sorted_threats = sorted(threat_counts.items(), key=lambda x: x[1], reverse=True)
            
            return {
                'success': True,
                'threats': [{'type': t[0], 'count': t[1]} for t in sorted_threats[:limit]]
            }
            
        except Exception as e:
            logger.error(f"Error getting top threats: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_daily_statistics(user_id: int = None) -> dict:
        """Get daily statistics for dashboard"""
        try:
            conn = sqlite3.connect('scan_history.db')
            c = conn.cursor()
            
            query = """
                SELECT 
                    COUNT(*) as total_scans,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_scans,
                    COUNT(DISTINCT scanned_email) as unique_emails
                FROM scans
                WHERE DATE(created_at) = DATE('now')
            """
            params = []
            
            if user_id:
                query += " AND user_email = (SELECT email FROM users WHERE id = ?)"
                params.append(user_id)
            
            c.execute(query, params)
            row = c.fetchone()
            
            # Get threat count from today
            threat_query = """
                SELECT 
                    SUM(CASE WHEN result_json LIKE '%SAFE%' THEN 1 ELSE 0 END) as safe,
                    SUM(CASE WHEN result_json LIKE '%SUSPICIOUS%' THEN 1 ELSE 0 END) as suspicious,
                    SUM(CASE WHEN result_json LIKE '%DANGER%' THEN 1 ELSE 0 END) as danger
                FROM scans
                WHERE DATE(created_at) = DATE('now')
            """
            
            if user_id:
                threat_query += " AND user_email = (SELECT email FROM users WHERE id = ?)"
            
            c.execute(threat_query, params)
            threat_row = c.fetchone()
            conn.close()
            
            return {
                'success': True,
                'statistics': {
                    'total_scans': row[0] or 0,
                    'successful_scans': row[1] or 0,
                    'unique_emails': row[2] or 0,
                    'safe_emails': threat_row[0] or 0,
                    'suspicious_emails': threat_row[1] or 0,
                    'dangerous_emails': threat_row[2] or 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting daily statistics: {e}")
            return {'success': False, 'error': str(e)}
