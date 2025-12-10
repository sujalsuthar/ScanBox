"""
Scanbox Attachment Sandboxing
- Simulates safe analysis of attachments for malware/ransomware
- (For real deployment, integrate with Cuckoo Sandbox or VirusTotal)
"""
import hashlib
import random

class Sandbox:
    def __init__(self):
        pass

    def analyze(self, file_bytes, filename):
        # Simulate analysis: flag as suspicious if file is executable or has known bad hash
        sha256 = hashlib.sha256(file_bytes).hexdigest()
        suspicious_ext = ['.exe', '.bat', '.js', '.vbs', '.scr', '.dll', '.ps1', '.jar']
        is_suspicious = any(filename.lower().endswith(ext) for ext in suspicious_ext)
        # Simulate random detection for demo
        detected = is_suspicious or (sha256.startswith('00') and random.random() < 0.5)
        result = {
            'filename': filename,
            'sha256': sha256,
            'is_suspicious': is_suspicious,
            'sandbox_detected': detected,
            'verdict': 'malicious' if detected else 'clean'
        }
        return result

sandbox = Sandbox()
