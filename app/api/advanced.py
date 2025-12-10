"""Advanced API routes for new features (analytics, scheduler, integrations)"""

from flask import Blueprint, request, jsonify
from app.auth.utils import require_auth
from app.services.analytics import Analytics
from app.services.scheduler import Scheduler
from app.integrations.url_intelligence import URLIntelligence
from scanner_imap import scan_emails_imap
import logging

logger = logging.getLogger(__name__)

advanced_bp = Blueprint('advanced', __name__, url_prefix='/api')
bulk_api = Blueprint('bulk_api', __name__)

# Initialize scheduler tables
Scheduler.init_table()

# ==================== ANALYTICS ENDPOINTS ====================

@advanced_bp.route('/analytics/trends', methods=['GET'])
@require_auth
def get_threat_trends():
    """Get threat trends over time"""
    try:
        days = request.args.get('days', 30, type=int)
        result = Analytics.get_threat_trends(min(days, 90))
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        return jsonify({'error': str(e)}), 500

@advanced_bp.route('/analytics/distribution', methods=['GET'])
@require_auth
def get_risk_distribution():
    """Get risk score distribution"""
    try:
        result = Analytics.get_risk_distribution()
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error getting distribution: {e}")
        return jsonify({'error': str(e)}), 500

@advanced_bp.route('/analytics/threats', methods=['GET'])
@require_auth
def get_top_threats():
    """Get top threats detected"""
    try:
        limit = request.args.get('limit', 10, type=int)
        result = Analytics.get_top_threats(min(limit, 50))
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error getting top threats: {e}")
        return jsonify({'error': str(e)}), 500

@advanced_bp.route('/analytics/daily', methods=['GET'])
@require_auth
def get_daily_stats():
    """Get daily statistics"""
    try:
        result = Analytics.get_daily_statistics(request.user_id)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error getting daily stats: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== SCHEDULER ENDPOINTS ====================

@advanced_bp.route('/scheduler/create', methods=['POST'])
@require_auth
def create_scheduled_scan():
    """Create a scheduled scan"""
    try:
        data = request.get_json()
        
        gmail_account = data.get('gmail_account')
        frequency = data.get('frequency')
        app_password = data.get('app_password')
        
        if not all([gmail_account, frequency, app_password]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        result = Scheduler.create_schedule(
            request.user_id,
            request.user_email,
            gmail_account,
            frequency,
            app_password
        )
        
        status_code = 201 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error creating schedule: {e}")
        return jsonify({'error': str(e)}), 500

@advanced_bp.route('/scheduler/list', methods=['GET'])
@require_auth
def list_schedules():
    """List all scheduled scans for user"""
    try:
        result = Scheduler.get_user_schedules(request.user_id)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error listing schedules: {e}")
        return jsonify({'error': str(e)}), 500

@advanced_bp.route('/scheduler/<int:schedule_id>/update', methods=['PUT'])
@require_auth
def update_schedule(schedule_id):
    """Update a scheduled scan"""
    try:
        data = request.get_json()
        
        frequency = data.get('frequency')
        is_active = data.get('is_active')
        
        result = Scheduler.update_schedule(schedule_id, frequency, is_active)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error updating schedule: {e}")
        return jsonify({'error': str(e)}), 500

@advanced_bp.route('/scheduler/<int:schedule_id>/delete', methods=['DELETE'])
@require_auth
def delete_schedule(schedule_id):
    """Delete a scheduled scan"""
    try:
        result = Scheduler.delete_schedule(schedule_id)
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error deleting schedule: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== URL INTELLIGENCE ENDPOINTS ====================

@advanced_bp.route('/url-check', methods=['POST'])
@require_auth
def check_url():
    """Check URL reputation"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL required'}), 400
        
        result = URLIntelligence.check_url_reputation(url)
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error checking URL: {e}")
        return jsonify({'error': str(e)}), 500

@advanced_bp.route('/url-check/batch', methods=['POST'])
@require_auth
def check_urls_batch():
    """Check multiple URLs"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls or not isinstance(urls, list):
            return jsonify({'error': 'URLs list required'}), 400
        
        results = []
        for url in urls[:50]:  # Limit to 50 URLs per request
            result = URLIntelligence.check_url_reputation(url)
            results.append(result)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error checking batch URLs: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== DASHBOARD ENDPOINTS ====================

@advanced_bp.route('/dashboard/summary', methods=['GET'])
@require_auth
def get_dashboard_summary():
    """Get complete dashboard summary"""
    try:
        daily_stats = Analytics.get_daily_statistics(request.user_id)
        threat_trends = Analytics.get_threat_trends(7)
        risk_dist = Analytics.get_risk_distribution()
        
        return jsonify({
            'success': True,
            'daily_stats': daily_stats.get('statistics', {}),
            'weekly_trends': threat_trends.get('trends', []),
            'risk_distribution': risk_dist.get('distribution', {})
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== BULK SCAN ENDPOINTS ====================

@bulk_api.route('/bulk-scan', methods=['POST'])
def bulk_scan():
    """Scan a batch of emails (uploaded as .eml files or raw RFC822 strings)"""
    files = request.files.getlist('emails')
    results = []
    for file in files:
        try:
            import email
            msg = email.message_from_bytes(file.read())
            # Simulate IMAP scan for each uploaded email
            # Reuse scan_emails_imap logic for single message
            scan_result = scan_emails_imap_for_message(msg)
            results.append(scan_result)
        except Exception as e:
            results.append({'error': str(e), 'filename': file.filename})
    return jsonify({'results': results})

def scan_emails_imap_for_message(msg):
    # Minimal wrapper to reuse scan_emails_imap logic for a single message
    subject = msg.get('Subject', '')
    sender = msg.get('From', '')
    date = msg.get('Date', '')
    body = msg.get_payload(decode=True)
    if isinstance(body, bytes):
        body = body.decode('utf-8', 'ignore')
    urls = []
    attachments = []
    # ...existing scan logic (reuse from scan_emails_imap)...
    # For brevity, call scan_emails_imap with a mock IMAP object if needed
    # Or copy scan logic here for single message
    return {
        'subject': subject,
        'from': sender,
        'date': date,
        'urls': urls,
        'attachments': attachments,
        # Add threat intel, AI, sandbox, detonation, etc.
    }
