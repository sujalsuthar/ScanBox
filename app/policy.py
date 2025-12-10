"""
Scanbox Custom Policy Engine
- Allow admins to set block/allow rules and compliance policies
"""
import sqlite3
from flask import Blueprint, request, jsonify
from app.auth.utils import require_auth

policy_bp = Blueprint('policy', __name__)

def get_db():
    conn = sqlite3.connect('scan_history.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_policy_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS policies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        rule TEXT NOT NULL,
        action TEXT NOT NULL,
        enabled INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

init_policy_db()

class PolicyEngine:
    def __init__(self):
        self.policies = []
        self.load_policies()
    
    def load_policies(self):
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM policies WHERE enabled = 1')
        self.policies = [dict(row) for row in cur.fetchall()]
        conn.close()
    
    def evaluate(self, email_data):
        actions = []
        for policy in self.policies:
            if self._match_policy(policy, email_data):
                actions.append({
                    'policy': policy['name'],
                    'action': policy['action']
                })
        return actions
    
    def _match_policy(self, policy, email_data):
        rule_type = policy['type']
        rule_value = policy['rule']
        
        if rule_type == 'sender_domain':
            sender = email_data.get('from', '').lower()
            return rule_value.lower() in sender
        elif rule_type == 'subject_keyword':
            subject = email_data.get('subject', '').lower()
            return rule_value.lower() in subject
        elif rule_type == 'risk_level':
            return email_data.get('risk_level') == rule_value
        elif rule_type == 'attachment_extension':
            attachments = email_data.get('attachments', [])
            return any(att['name'].lower().endswith(rule_value.lower()) for att in attachments)
        
        return False

policy_engine = PolicyEngine()

@policy_bp.route('/policies', methods=['GET'])
@require_auth
def list_policies():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM policies ORDER BY created_at DESC')
    policies = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({'policies': policies})

@policy_bp.route('/policies', methods=['POST'])
@require_auth
def create_policy():
    from datetime import datetime
    name = request.json.get('name')
    policy_type = request.json.get('type')
    rule = request.json.get('rule')
    action = request.json.get('action', 'block')
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''INSERT INTO policies (name, type, rule, action, created_at)
                   VALUES (?, ?, ?, ?, ?)''',
                (name, policy_type, rule, action, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    
    policy_engine.load_policies()
    return jsonify({'success': True})

@policy_bp.route('/policies/<int:policy_id>', methods=['DELETE'])
@require_auth
def delete_policy(policy_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM policies WHERE id = ?', (policy_id,))
    conn.commit()
    conn.close()
    
    policy_engine.load_policies()
    return jsonify({'success': True})

@policy_bp.route('/policies/<int:policy_id>/toggle', methods=['PUT'])
@require_auth
def toggle_policy(policy_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE policies SET enabled = NOT enabled WHERE id = ?', (policy_id,))
    conn.commit()
    conn.close()
    
    policy_engine.load_policies()
    return jsonify({'success': True})
