# app/api/routes.py
"""
API route definitions and handlers.
"""

import logging
import time
import json
from flask import Flask, request, jsonify, render_template, g
from functools import wraps
from app.utils.validators import Validator, ValidationError
from app.services.scan_service import ScanService, RiskAnalyzer
from app.models.database import DatabaseManager, get_db_from_context

logger = logging.getLogger(__name__)


def register_routes(app: Flask) -> None:
    """
    Register all API routes.
    
    Args:
        app: Flask application instance
    """
    
    # Register advanced features blueprint
    from app.api.advanced import advanced_bp, bulk_api
    app.register_blueprint(advanced_bp)
    app.register_blueprint(bulk_api)
    
    # Initialize service layer
    db_manager = DatabaseManager(app.config['DB_PATH'])
    scan_service = ScanService(db_manager)
    
    # Middleware for request logging
    @app.before_request
    def before_request():
        """Log request start time."""
        g.start_time = time.time()
        g.user_agent = request.headers.get('User-Agent', 'Unknown')
        g.remote_addr = request.remote_addr
    
    @app.after_request
    def after_request(response):
        """Log request details."""
        if hasattr(g, 'start_time'):
            elapsed = (time.time() - g.start_time) * 1000  # Convert to ms
            logger.info(
                f"{request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Time: {elapsed:.2f}ms"
            )
        return response
    
    # ==================== UI Routes ====================
    
    @app.route("/", methods=["GET"])
    def serve_ui():
        """
        Serve the main web UI.
        
        Returns:
            Rendered HTML template
        """
        return render_template("index.html")
    
    # ==================== Health Check ====================
    
    @app.route("/health", methods=["GET"])
    def health_check():
        """
        Health check endpoint for monitoring.
        
        Returns:
            JSON with health status
        """
        return jsonify({
            'status': 'healthy',
            'service': 'email-scanner-api',
            'version': '1.0.0',
            'timestamp': time.time()
        }), 200
    
    # ==================== Scan API ====================
    
    @app.route("/api/scan", methods=["POST"])
    def api_scan():
        """
        Scan emails from a Gmail account.
        
        Request JSON:
            {
                "gmail": "user@gmail.com",
                "app_password": "xxxx xxxx xxxx xxxx",
                "limit": 10 (optional, default 10, max 100),
                "user_email": "user@gmail.com" (optional, for multi-user support)
            }
        
        Returns:
            JSON with scan results or error
        """
        try:
            # Get request data
            data = request.get_json() or {}
            
            # Validate request
            is_valid, error_msg = Validator.validate_scan_request(data)
            if not is_valid:
                logger.warning(f"Invalid scan request: {error_msg}")
                return jsonify({
                    'error': 'Validation Error',
                    'message': error_msg
                }), 400
            
            # Extract and validate parameters
            gmail = data.get('gmail', '').strip()
            app_password = data.get('app_password', '').strip()
            limit = int(data.get('limit', 10))
            user_email = data.get('user_email', '').strip() or gmail
            
            # Perform scan
            results, status_code, error = scan_service.perform_scan(
                gmail=gmail,
                app_password=app_password,
                limit=limit,
                user_email=user_email
            )
            
            # Add risk summary
            if 'results' in results and not error:
                results['summary'] = RiskAnalyzer.get_risk_summary(results['results'])
            
            return jsonify(results), status_code
        
        except Exception as e:
            logger.error(f"Unhandled error in /api/scan: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred'
            }), 500
    
    # ==================== History API ====================
    
    @app.route("/api/history", methods=["GET"])
    def api_history():
        """
        Get scan history.
        
        Query Parameters:
            user_email: Filter by user email (optional)
            limit: Maximum records to return (default 20, max 100)
        
        Returns:
            JSON list of scan records
        """
        try:
            user_email = request.args.get('user_email', '').strip() or None
            limit = min(int(request.args.get('limit', 20)), 100)
            
            # Return scans with result_json to match UI expectations
            if user_email:
                query = """
                    SELECT id, scanned_email, created_at, status, result_json
                    FROM scans
                    WHERE user_email = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """
                scans = db_manager.execute_query(query, (user_email, limit))
            else:
                query = """
                    SELECT id, scanned_email, created_at, status, result_json
                    FROM scans
                    ORDER BY created_at DESC
                    LIMIT ?
                """
                scans = db_manager.execute_query(query, (limit,))

            return jsonify({
                'scans': scans,
                'count': len(scans)
            }), 200
        
        except ValueError:
            return jsonify({
                'error': 'Invalid Parameters',
                'message': 'limit must be an integer'
            }), 400
        
        except Exception as e:
            logger.error(f"Error retrieving history: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'Internal Server Error'
            }), 500
    
    # ==================== Scan Details API ====================
    
    @app.route("/api/history/<int:scan_id>", methods=["GET"])
    def api_history_detail(scan_id):
        """
        Get detailed results for a specific scan.
        
        Parameters:
            scan_id: ID of the scan to retrieve
        
        Returns:
            JSON with full scan results or error
        """
        try:
            results = scan_service.get_scan_details(scan_id)
            
            if results is None:
                return jsonify({
                    'error': 'Not Found',
                    'message': f'Scan with ID {scan_id} not found'
                }), 404
            
            return jsonify({
                'scan_id': scan_id,
                'results': results,
                'summary': RiskAnalyzer.get_risk_summary(results)
            }), 200
        
        except Exception as e:
            logger.error(f"Error retrieving scan {scan_id}: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'Internal Server Error'
            }), 500
    
    # ==================== Stats API ====================
    
    @app.route("/api/stats", methods=["GET"])
    def api_stats():
        """
        Get overall statistics about scans.
        
        Returns:
            JSON with statistics
        """
        try:
            user_email = request.args.get('user_email', '').strip() or None
            
            if user_email:
                query = "SELECT COUNT(*) as count FROM scans WHERE user_email = ?"
                results = db_manager.execute_query(query, (user_email,))
            else:
                query = "SELECT COUNT(*) as count FROM scans"
                results = db_manager.execute_query(query)
            
            total_scans = results[0]['count'] if results else 0
            
            return jsonify({
                'total_scans': total_scans,
                'user_email': user_email
            }), 200
        
        except Exception as e:
            logger.error(f"Error retrieving stats: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'Internal Server Error'
            }), 500
    
    # ====== EMAIL ACCOUNT MANAGEMENT ENDPOINTS ======
    
    @app.route('/api/email-accounts/connect', methods=['POST'])
    def connect_email_account():
        """Connect a new email account"""
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                return jsonify({'error': 'Missing token'}), 401
            
            from app.auth.utils import decode_token
            payload = decode_token(token)
            if not payload:
                return jsonify({'error': 'Invalid token'}), 401
            
            user_id = payload.get('id')
            data = request.get_json()
            
            email_address = data.get('email_address', '').strip()
            imap_password = data.get('imap_password', '')
            email_provider = data.get('email_provider', 'gmail')
            
            if not email_address or not imap_password:
                return jsonify({'error': 'Missing email or password'}), 400
            
            from app.services.email_account_manager import EmailAccountManager
            manager = EmailAccountManager(app.config['DB_PATH'])
            
            success, account_id, message = manager.add_email_account(
                user_id, email_address, imap_password, email_provider
            )
            
            if not success:
                return jsonify({'error': message}), 400
            
            return jsonify({
                'success': True,
                'account_id': account_id,
                'message': message
            }), 201
        
        except Exception as e:
            logger.error(f"Error connecting email account: {str(e)}")
            return jsonify({'error': 'Internal Server Error'}), 500
    
    @app.route('/api/email-accounts', methods=['GET'])
    def get_email_accounts():
        """Get all email accounts for user"""
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                return jsonify({'error': 'Missing token'}), 401
            
            from app.auth.utils import decode_token
            payload = decode_token(token)
            if not payload:
                return jsonify({'error': 'Invalid token'}), 401
            
            user_id = payload.get('id')
            
            from app.services.email_account_manager import EmailAccountManager
            manager = EmailAccountManager(app.config['DB_PATH'])
            
            accounts = manager.get_user_accounts(user_id)
            
            return jsonify({
                'accounts': accounts,
                'total': len(accounts)
            }), 200
        
        except Exception as e:
            logger.error(f"Error getting email accounts: {str(e)}")
            return jsonify({'error': 'Internal Server Error'}), 500
    
    @app.route('/api/email-accounts/<int:account_id>/scan', methods=['POST'])
    def scan_email_account(account_id):
        """Scan emails from an account and analyze"""
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                return jsonify({'error': 'Missing token'}), 401
            
            from app.auth.utils import decode_token
            payload = decode_token(token)
            if not payload:
                return jsonify({'error': 'Invalid token'}), 401
            
            from app.services.email_account_manager import EmailAccountManager
            from app.services.advanced_email_analyzer import AdvancedEmailAnalyzer
            import sqlite3
            
            manager = EmailAccountManager(app.config['DB_PATH'])
            analyzer = AdvancedEmailAnalyzer()
            
            # Fetch emails
            success, emails, msg = manager.fetch_emails(account_id, limit=20)
            if not success:
                return jsonify({'error': msg}), 400
            
            # Analyze each email
            analyzed_emails = []
            conn = sqlite3.connect(app.config['DB_PATH'], timeout=5, check_same_thread=False)
            c = conn.cursor()
            
            for email in emails:
                # Analyze
                analysis = analyzer.analyze_email({
                    'from': email['from'],
                    'subject': email['subject'],
                    'body_preview': email['body_preview'],
                    'has_attachment': email['has_attachment'],
                    'attachments': email['attachments']
                })
                
                # Save analysis to database
                try:
                    c.execute("""
                    SELECT id FROM emails WHERE account_id = ? AND email_uid = ?
                    """, (account_id, email['uid']))
                    
                    result = c.fetchone()
                    if result:
                        email_id = result[0]
                        
                        c.execute("""
                        INSERT INTO email_analysis 
                        (email_id, threat_level, risk_score, threats_detected, 
                         ai_explanation, recommendations, analyzed_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (email_id, analysis['threat_level'], analysis['risk_score'],
                              json.dumps(analysis['threats_detected']),
                              analysis['ai_explanation'],
                              json.dumps(analysis['recommendations']),
                              analysis['analyzed_at']))
                except:
                    pass
                
                analyzed_emails.append({
                    'from': email['from'],
                    'subject': email['subject'],
                    'threat_level': analysis['threat_level'],
                    'risk_score': analysis['risk_score'],
                    'threats': analysis['threats_detected'][:2],
                    'explanation': analysis['ai_explanation'],
                    'recommendations': analysis['recommendations']
                })
            
            conn.commit()
            conn.close()
            
            # Get stats
            stats = manager.get_analysis_stats(account_id)
            
            return jsonify({
                'emails_analyzed': len(analyzed_emails),
                'emails': analyzed_emails,
                'stats': stats
            }), 200
        
        except Exception as e:
            logger.error(f"Error scanning emails: {str(e)}", exc_info=True)
            return jsonify({'error': 'Internal Server Error'}), 500
    
    @app.route('/api/email-accounts/<int:account_id>/dashboard', methods=['GET'])
    def get_email_dashboard(account_id):
        """Get email account dashboard with security score"""
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                return jsonify({'error': 'Missing token'}), 401
            
            from app.auth.utils import decode_token
            payload = decode_token(token)
            if not payload:
                return jsonify({'error': 'Invalid token'}), 401
            
            from app.services.email_account_manager import EmailAccountManager
            import sqlite3
            
            manager = EmailAccountManager(app.config['DB_PATH'])
            
            # Get stats
            stats = manager.get_analysis_stats(account_id)
            
            # Get recent threats
            conn = sqlite3.connect(app.config['DB_PATH'], timeout=5, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            c.execute("""
            SELECT e.from_address, e.subject, ea.threat_level, ea.risk_score
            FROM email_analysis ea
            JOIN emails e ON ea.email_id = e.id
            WHERE e.account_id = ?
            ORDER BY e.fetched_at DESC
            LIMIT 10
            """, (account_id,))
            
            recent_emails = [dict(row) for row in c.fetchall()]
            conn.close()
            
            return jsonify({
                'security_score': stats.get('security_score', 0),
                'total_emails': stats.get('total_emails', 0),
                'threat_breakdown': stats.get('threat_breakdown', {}),
                'average_risk_score': stats.get('average_risk_score', 0),
                'recent_emails': recent_emails
            }), 200
        
        except Exception as e:
            logger.error(f"Error getting dashboard: {str(e)}")
            return jsonify({'error': 'Internal Server Error'}), 500
    
    @app.route('/api/email-accounts/<int:account_id>/disconnect', methods=['POST'])
    def disconnect_email_account(account_id):
        """Disconnect email account"""
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                return jsonify({'error': 'Missing token'}), 401
            
            from app.auth.utils import decode_token
            payload = decode_token(token)
            if not payload:
                return jsonify({'error': 'Invalid token'}), 401
            
            from app.services.email_account_manager import EmailAccountManager
            manager = EmailAccountManager(app.config['DB_PATH'])
            
            success = manager.disconnect_account(account_id)
            
            if success:
                return jsonify({'success': True}), 200
            else:
                return jsonify({'error': 'Failed to disconnect'}), 400
        
        except Exception as e:
            logger.error(f"Error disconnecting account: {str(e)}")
            return jsonify({'error': 'Internal Server Error'}), 500
