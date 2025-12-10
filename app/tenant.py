"""
Scanbox Multi-Tenant Support
- Enable MSPs and large organizations to manage multiple clients securely
"""
import sqlite3
from flask import Blueprint, request, jsonify
from app.auth.utils import require_auth
from datetime import datetime

tenant_bp = Blueprint('tenant', __name__)

def get_db():
    conn = sqlite3.connect('scan_history.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_tenant_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS tenants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        domain TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL,
        status TEXT DEFAULT 'active'
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS tenant_users (
        tenant_id INTEGER NOT NULL,
        user_email TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (tenant_id) REFERENCES tenants (id),
        PRIMARY KEY (tenant_id, user_email)
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS tenant_scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tenant_id INTEGER NOT NULL,
        scan_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (tenant_id) REFERENCES tenants (id)
    )''')
    conn.commit()
    conn.close()

init_tenant_db()

@tenant_bp.route('/tenants', methods=['GET'])
@require_auth
def list_tenants():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tenants ORDER BY created_at DESC')
    tenants = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({'tenants': tenants})

@tenant_bp.route('/tenants', methods=['POST'])
@require_auth
def create_tenant():
    name = request.json.get('name')
    domain = request.json.get('domain')
    
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute('''INSERT INTO tenants (name, domain, created_at)
                       VALUES (?, ?, ?)''',
                    (name, domain, datetime.utcnow().isoformat()))
        tenant_id = cur.lastrowid
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'tenant_id': tenant_id})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'error': 'Domain already exists'})

@tenant_bp.route('/tenants/<int:tenant_id>/users', methods=['POST'])
@require_auth
def add_tenant_user(tenant_id):
    user_email = request.json.get('user_email')
    role = request.json.get('role', 'member')
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''INSERT OR REPLACE INTO tenant_users (tenant_id, user_email, role, created_at)
                   VALUES (?, ?, ?, ?)''',
                (tenant_id, user_email, role, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@tenant_bp.route('/tenants/<int:tenant_id>/stats', methods=['GET'])
@require_auth
def get_tenant_stats(tenant_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) as total_scans FROM tenant_scans WHERE tenant_id = ?', (tenant_id,))
    total_scans = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) as total_users FROM tenant_users WHERE tenant_id = ?', (tenant_id,))
    total_users = cur.fetchone()[0]
    conn.close()
    
    return jsonify({
        'tenant_id': tenant_id,
        'total_scans': total_scans,
        'total_users': total_users
    })

@tenant_bp.route('/tenants/<int:tenant_id>', methods=['DELETE'])
@require_auth
def delete_tenant(tenant_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM tenants WHERE id = ?', (tenant_id,))
    cur.execute('DELETE FROM tenant_users WHERE tenant_id = ?', (tenant_id,))
    cur.execute('DELETE FROM tenant_scans WHERE tenant_id = ?', (tenant_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})
