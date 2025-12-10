"""
Scanbox Automated Reporting
- Generate scheduled PDF/CSV reports and email them to admins
"""
import csv
import io
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, send_file
from app.auth.utils import require_auth
import sqlite3

reporting_bp = Blueprint('reporting', __name__)

def get_db():
    conn = sqlite3.connect('scan_history.db')
    conn.row_factory = sqlite3.Row
    return conn

@reporting_bp.route('/reports/csv', methods=['GET'])
@require_auth
def generate_csv_report(request):
    days = request.args.get('days', 7, type=int)
    since = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''SELECT timestamp, email_from, email_subject, risk_score, risk_level, urls, attachments
                   FROM scans WHERE timestamp >= ? ORDER BY timestamp DESC''', (since,))
    rows = cur.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'From', 'Subject', 'Risk Score', 'Risk Level', 'URLs', 'Attachments'])
    for row in rows:
        writer.writerow([row['timestamp'], row['email_from'], row['email_subject'], 
                        row['risk_score'], row['risk_level'], row['urls'], row['attachments']])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'scanbox_report_{datetime.utcnow().strftime("%Y%m%d")}.csv'
    )

@reporting_bp.route('/reports/summary', methods=['GET'])
@require_auth
def get_summary_report(request):
    days = request.args.get('days', 7, type=int)
    since = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) as total FROM scans WHERE timestamp >= ?', (since,))
    total = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) as dangerous FROM scans WHERE timestamp >= ? AND risk_level = "DANGEROUS"', (since,))
    dangerous = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) as suspicious FROM scans WHERE timestamp >= ? AND risk_level = "SUSPICIOUS"', (since,))
    suspicious = cur.fetchone()[0]
    conn.close()
    
    return jsonify({
        'period_days': days,
        'total_scans': total,
        'dangerous': dangerous,
        'suspicious': suspicious,
        'safe': total - dangerous - suspicious
    })

@reporting_bp.route('/reports/schedule', methods=['POST'])
@require_auth
def schedule_report(request):
    # Placeholder: In production, integrate with a task scheduler (Celery, APScheduler)
    frequency = request.json.get('frequency', 'weekly')
    email = request.json.get('email')
    return jsonify({'success': True, 'message': f'Report scheduled {frequency} to {email}'})
