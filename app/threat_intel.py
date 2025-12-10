"""
Scanbox Threat Intelligence Integration
- Aggregates external threat feeds for real-time phishing/malware detection
- Feeds: AbuseIPDB, PhishTank, Google Safe Browsing
"""
import requests
import time

class ThreatIntel:
    def __init__(self):
        self.last_update = 0
        self.cache = {
            'phish_urls': set(),
            'malicious_ips': set(),
            'safe_browsing': set()
        }

    def update_feeds(self):
        # AbuseIPDB (malicious IPs)
        try:
            abuse_resp = requests.get('https://api.abuseipdb.com/api/v2/blacklist', headers={
                'Key': 'YOUR_ABUSEIPDB_API_KEY',
                'Accept': 'application/json'
            })
            if abuse_resp.ok:
                self.cache['malicious_ips'] = set(ip['ipAddress'] for ip in abuse_resp.json().get('data', []))
        except Exception:
            pass
        # PhishTank (phishing URLs)
        try:
            phishtank_resp = requests.get('https://data.phishtank.com/data/online-valid.json')
            if phishtank_resp.ok:
                self.cache['phish_urls'] = set(entry['url'] for entry in phishtank_resp.json())
        except Exception:
            pass
        # Google Safe Browsing (URLs)
        # Placeholder: Use official API for production
        self.last_update = time.time()

    def is_malicious_ip(self, ip):
        if time.time() - self.last_update > 3600:
            self.update_feeds()
        return ip in self.cache['malicious_ips']

    def is_phishing_url(self, url):
        if time.time() - self.last_update > 3600:
            self.update_feeds()
        return url in self.cache['phish_urls']

    def is_safe_browsing(self, url):
        # Placeholder for Google Safe Browsing check
        return False

threat_intel = ThreatIntel()
