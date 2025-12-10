# scanner_imap.py
import imaplib
import email
import re
import hashlib
import math
from email.header import decode_header
from dateutil import parser as dt_parser

# Use advanced analyzer for consistent scoring with UI
from app.services.advanced_email_analyzer import AdvancedEmailAnalyzer

URL_REGEX = re.compile(r'https?://[^\s"\'<>]+', re.IGNORECASE)

def decode_header_value(value):
    if not value:
        return ""
    decoded = decode_header(value)
    text = ""
    for part, enc in decoded:
        if isinstance(part, bytes):
            text += part.decode(enc or "utf-8", errors="ignore")
        else:
            text += part
    return text

def extract_urls(text):
    return URL_REGEX.findall(text or "")

def get_sha256(data):
    return hashlib.sha256(data).hexdigest()

def connect_imap(email_user, password):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(email_user, password)
    mail.select("INBOX")
    return mail

def risk_level_from_threat(threat_level: str) -> str:
    """Map analyzer threat_level to UI risk_level (UI expects DANGER/SUSPICIOUS/SAFE)."""
    mapping = {
        'danger': 'DANGER',
        'warning': 'SUSPICIOUS',
        'safe': 'SAFE'
    }
    return mapping.get(threat_level, 'SAFE')

def scan_emails_imap(mail, limit=10):
    # Lazy import app modules to avoid circular import at startup
    from app.threat_intel import threat_intel
    from app.ai_phishing import ai_detector
    from app.sandbox import sandbox
    from app.url_detonation import url_detonator
    status, data = mail.search(None, "ALL")
    email_ids = data[0].split()[-limit:]

    results = []

    analyzer = AdvancedEmailAnalyzer()

    for msg_id in email_ids:
        status, msg_data = mail.fetch(msg_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        subject = decode_header_value(msg.get("Subject"))
        sender = decode_header_value(msg.get("From"))
        date = decode_header_value(msg.get("Date"))

        body = ""
        urls = []
        attachments = []
        sandbox_results = []
        url_detonation_results = []

        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()

                if ctype == "text/plain":
                    try:
                        body += part.get_payload(decode=True).decode("utf-8", "ignore")
                    except:
                        pass

                if part.get("Content-Disposition"):
                    fname = decode_header_value(part.get_filename())
                    data = part.get_payload(decode=True)
                    if data:
                        sha = get_sha256(data)
                        attachments.append({"name": fname, "sha256": sha})
                        # Sandbox analysis
                        verdict = sandbox.analyze(data, fname)
                        sandbox_results.append(verdict)
        else:
            payload = msg.get_payload(decode=True)
            if isinstance(payload, bytes):
                body = payload.decode("utf-8", "ignore")

        urls = extract_urls(body)

        # Run advanced analyzer for full threat scoring
        analysis = analyzer.analyze_email({
            'from': sender,
            'subject': subject,
            'body_preview': body,
            'has_attachment': bool(attachments),
            'attachments': [a['name'] for a in attachments]
        })

        # Map to legacy risk_level/risk_score expected by UI (0-10 scale)
        risk_score_100 = analysis.get('risk_score', 0)
        risk_level = risk_level_from_threat(analysis.get('threat_level', 'safe'))
        # Use ceiling so 100/100 becomes 10/10 and dangers surface clearly
        risk_score = min(10, max(0, math.ceil(risk_score_100 / 10)))

        # Threat intelligence checks (keep existing intel for context)
        ti_flags = []
        for url in urls:
            if threat_intel.is_phishing_url(url):
                ti_flags.append(f"Phishing URL: {url}")
            if threat_intel.is_safe_browsing(url):
                ti_flags.append(f"Unsafe (Google Safe Browsing): {url}")

        # AI phishing detection (existing)
        is_phish, ai_score = ai_detector.is_phishing(subject, body, sender)

        # URL detonation
        for url in urls:
            detonation = url_detonator.detonate(url)
            url_detonation_results.append(detonation)

        results.append({
            "subject": subject,
            "from": sender,
            "date": date,
            "urls": urls,
            "attachments": attachments,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "snippet": (body[:160] + "...") if len(body) > 160 else body,
            "threats": analysis.get('threats_detected', []),
            "ai_explanation": analysis.get('ai_explanation', ''),
            "threat_intel_flags": ti_flags,
            "ai_phishing": {
                "is_phishing": is_phish,
                "ai_score": ai_score
            },
            "sandbox_results": sandbox_results,
            "url_detonation_results": url_detonation_results
        })

    return results

def scan_email_account(gmail, app_password, limit=10):
    mail = connect_imap(gmail, app_password)
    results = scan_emails_imap(mail, limit=limit)
    mail.logout()
    return results
