"""
Scanbox SIEM/SOAR Integration
- Connectors for Splunk, QRadar, and other security platforms
"""
import requests
from flask import Blueprint, request, jsonify
from app.auth.utils import require_auth

siem_bp = Blueprint('siem', __name__)

class SIEMConnector:
    def __init__(self):
        self.splunk_url = None
        self.splunk_token = None
        self.qradar_url = None
        self.qradar_token = None
    
    def configure_splunk(self, url, token):
        self.splunk_url = url
        self.splunk_token = token
    
    def configure_qradar(self, url, token):
        self.qradar_url = url
        self.qradar_token = token
    
    def send_to_splunk(self, event):
        if not self.splunk_url or not self.splunk_token:
            return False
        try:
            resp = requests.post(
                f'{self.splunk_url}/services/collector/event',
                headers={'Authorization': f'Splunk {self.splunk_token}'},
                json={'event': event}
            )
            return resp.ok
        except:
            return False
    
    def send_to_qradar(self, event):
        if not self.qradar_url or not self.qradar_token:
            return False
        try:
            resp = requests.post(
                f'{self.qradar_url}/api/ariel/searches',
                headers={'SEC': self.qradar_token},
                json=event
            )
            return resp.ok
        except:
            return False

siem_connector = SIEMConnector()

@siem_bp.route('/siem/configure/splunk', methods=['POST'])
@require_auth
def configure_splunk(request):
    url = request.json.get('url')
    token = request.json.get('token')
    siem_connector.configure_splunk(url, token)
    return jsonify({'success': True, 'message': 'Splunk configured'})

@siem_bp.route('/siem/configure/qradar', methods=['POST'])
@require_auth
def configure_qradar(request):
    url = request.json.get('url')
    token = request.json.get('token')
    siem_connector.configure_qradar(url, token)
    return jsonify({'success': True, 'message': 'QRadar configured'})

@siem_bp.route('/siem/send', methods=['POST'])
@require_auth
def send_to_siem(request):
    event = request.json.get('event')
    platform = request.json.get('platform', 'splunk')
    
    if platform == 'splunk':
        success = siem_connector.send_to_splunk(event)
    elif platform == 'qradar':
        success = siem_connector.send_to_qradar(event)
    else:
        return jsonify({'success': False, 'error': 'Unknown platform'})
    
    return jsonify({'success': success})
