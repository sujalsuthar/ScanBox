"""
Scanbox AI-Powered Phishing Detection
- Uses NLP and sender reputation to flag suspicious emails
"""
import re
import string
from collections import Counter

# Example suspicious keywords and patterns
SUSPICIOUS_KEYWORDS = [
    "urgent", "verify", "account", "password", "login", "reset", "bank", "invoice", "payment", "click", "update", "security", "alert", "confirm", "limited", "suspend", "locked", "otp", "transfer"
]

SENDER_REPUTATION_BLACKLIST = [
    "mail.ru", "163.com", "qq.com", "outlook.com", "yandex.com", "protonmail.com"
]

class AIDetector:
    def __init__(self):
        pass

    def nlp_phishing_score(self, subject, body):
        text = f"{subject} {body}".lower()
        # Keyword frequency
        keyword_hits = sum(text.count(k) for k in SUSPICIOUS_KEYWORDS)
        # Exclamation marks, all-caps, and links
        exclam = text.count("!")
        all_caps = sum(1 for w in text.split() if w.isupper() and len(w) > 3)
        links = len(re.findall(r'https?://', text))
        # Simple scoring
        score = keyword_hits * 2 + exclam + all_caps + links * 2
        # Suspicious phrases
        if "click here" in text:
            score += 3
        if "verify your account" in text:
            score += 3
        return score

    def sender_reputation_score(self, sender):
        sender = sender.lower()
        for bad_domain in SENDER_REPUTATION_BLACKLIST:
            if bad_domain in sender:
                return -5
        return 0

    def is_phishing(self, subject, body, sender):
        nlp_score = self.nlp_phishing_score(subject, body)
        sender_score = self.sender_reputation_score(sender)
        total_score = nlp_score + sender_score
        return total_score >= 6, total_score

ai_detector = AIDetector()
