"""
Scanbox URL Detonation
- Simulates secure analysis of URLs for malicious behavior
- (For real deployment, integrate with urlscan.io or a headless browser)
"""
import random

class URLDetonator:
    def __init__(self):
        pass

    def detonate(self, url):
        # Simulate: flag as suspicious if URL contains known bad patterns
        bad_patterns = ["login", "verify", "update", "bank", "secure", "account", "reset", "download"]
        is_suspicious = any(p in url.lower() for p in bad_patterns)
        # Simulate random detection for demo
        detected = is_suspicious or (url.startswith("http://") and random.random() < 0.3)
        result = {
            'url': url,
            'detonated': True,
            'suspicious': is_suspicious,
            'detected': detected,
            'verdict': 'malicious' if detected else 'clean'
        }
        return result

url_detonator = URLDetonator()
