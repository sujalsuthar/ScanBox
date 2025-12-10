"""
Scanbox Admin Dashboard
- User management, audit logs, and enterprise controls
"""
import sqlite3
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.auth.utils import require_auth

admin_bp = Blueprint('admin', __name__)

def get_db():
    conn = sqlite3.connect('scan_history.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create admin tables
def init_admin_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        user_email TEXT NOT NULL,
        action TEXT NOT NULL,
        details TEXT,
        ip_address TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS user_roles (
        user_email TEXT PRIMARY KEY,
        role TEXT NOT NULL,
        created_at TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

init_admin_db()

def log_audit(user_email, action, details='', ip=''):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''INSERT INTO audit_logs (timestamp, user_email, action, details, ip_address)
                   VALUES (?, ?, ?, ?, ?)''', 
                (datetime.utcnow().isoformat(), user_email, action, details, ip))
    conn.commit()
    conn.close()

@admin_bp.route('/admin/users', methods=['GET'])
@require_auth
def list_users():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''SELECT u.email, u.created_at, u.last_login, u.is_active,
                   COALESCE(r.role, 'user') as role,
                   COUNT(s.id) as total_scans
                   FROM users u
                   LEFT JOIN user_roles r ON u.email = r.user_email
                   LEFT JOIN scans s ON u.email = s.user_email
                   GROUP BY u.email
                   ORDER BY u.created_at DESC''')
    users = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({'success': True, 'users': users})

@admin_bp.route('/admin/users/<email>/role', methods=['PUT'])
@require_auth
def set_user_role(email):
    role = request.json.get('role', 'user')
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT OR REPLACE INTO user_roles (user_email, role, created_at) VALUES (?, ?, ?)',
                (email, role, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    log_audit(request.user_email, 'SET_ROLE', f'Set {email} to {role}', request.remote_addr)
    return jsonify({'success': True})

@admin_bp.route('/admin/users/<email>/toggle', methods=['PUT'])
@require_auth
def toggle_user_status(email):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE users SET is_active = NOT is_active WHERE email = ?', (email,))
    conn.commit()
    cur.execute('SELECT is_active FROM users WHERE email = ?', (email,))
    result = cur.fetchone()
    conn.close()
    
    status = 'activated' if result[0] else 'deactivated'
    log_audit(request.user_email, 'TOGGLE_USER', f'{status} {email}', request.remote_addr)
    return jsonify({'success': True, 'is_active': bool(result[0])})

@admin_bp.route('/admin/audit-logs', methods=['GET'])
@require_auth
def get_audit_logs():
    limit = request.args.get('limit', 100, type=int)
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?', (limit,))
    logs = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({'success': True, 'logs': logs})

@admin_bp.route('/admin/stats', methods=['GET'])
@require_auth
def get_admin_stats():
    conn = get_db()
    cur = conn.cursor()
    
    # Total users
    cur.execute('SELECT COUNT(*) FROM users')
    total_users = cur.fetchone()[0]
    
    # Active users (logged in last 30 days)
    cur.execute("SELECT COUNT(*) FROM users WHERE last_login >= datetime('now', '-30 days')")
    active_users = cur.fetchone()[0]
    
    # Total scans
    cur.execute('SELECT COUNT(*) FROM scans')
    total_scans = cur.fetchone()[0]
    
    # Scans today
    cur.execute("SELECT COUNT(*) FROM scans WHERE DATE(created_at) = DATE('now')")
    scans_today = cur.fetchone()[0]
    
    # Total threats
    cur.execute("SELECT COUNT(*) FROM scans WHERE result_json LIKE '%DANGER%'")
    total_threats = cur.fetchone()[0]
    
    # Recent activity
    cur.execute('SELECT COUNT(*) FROM audit_logs WHERE timestamp >= datetime("now", "-24 hours")')
    recent_activity = cur.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_users': total_users,
            'active_users': active_users,
            'total_scans': total_scans,
            'scans_today': scans_today,
            'total_threats': total_threats,
            'recent_activity': recent_activity
        }
    })
