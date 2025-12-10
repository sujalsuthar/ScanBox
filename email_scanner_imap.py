import imaplib
import email
import re
import json
import hashlib
from email.header import decode_header
from dateutil import parser as dt_parser

# ----------- COLORS -----------
RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
CYAN = "\033[36m"
BOLD = "\033[1m"
RESET = "\033[0m"

# ----------- URL REGEX -----------
URL_REGEX = re.compile(r'https?://[^\s"\'<>]+', re.IGNORECASE)

# ----------- FUNCTIONS -----------

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
    return URL_REGEX.findall(text)

def get_sha256(data):
    return hashlib.sha256(data).hexdigest()

def connect_imap(email_user, password):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(email_user, password)
    mail.select("INBOX")
    return mail

def risk_level(score):
    if score >= 8:
        return "DANGEROUS", RED
    elif score >= 4:
        return "SUSPICIOUS", YELLOW
    return "SAFE", GREEN

def scan_emails(mail, limit=10):
    status, data = mail.search(None, "ALL")
    email_ids = data[0].split()[-limit:]

    results = []

    for msg_id in email_ids:
        status, msg_data = mail.fetch(msg_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        subject = decode_header_value(msg.get("Subject"))
        sender = decode_header_value(msg.get("From"))
        date = decode_header_value(msg.get("Date"))

        body = ""
        urls = []
        attachments = []

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
        else:
            body = msg.get_payload(decode=True).decode("utf-8", "ignore")

        urls = extract_urls(body)

        # ----------- RISK SCORING -----------
        score = 0
        if any(x in body.lower() for x in ["verify", "password", "login", "bank", "update"]):
            score += 3
        if urls:
            score += 2
        if attachments:
            score += 4
        if "reset" in body.lower():
            score += 2

        level, color = risk_level(score)

        results.append({
            "subject": subject,
            "from": sender,
            "date": date,
            "urls": urls,
            "attachments": attachments,
            "risk_score": score,
            "risk_level": level
        })

        # ----------- TERMINAL OUTPUT -----------
        print("\n" + CYAN + "─" * 70 + RESET)
        print(f"{color}{BOLD}{level}{RESET}  |  Subject: {subject}")
        print(f"From: {sender}")
        print(f"Date: {date}")
        print(f"Risk Score: {score}")

        if urls:
            print(YELLOW + "\nURLs Found:" + RESET)
            for u in urls:
                print("  →", u)
        else:
            print(GREEN + "\nNo URLs found" + RESET)

        if attachments:
            print(RED + "\nAttachments Detected:" + RESET)
            for a in attachments:
                print(f"  → {a['name']} | SHA256: {a['sha256'][:12]}...")
        else:
            print(GREEN + "\nNo Attachments" + RESET)

        print(CYAN + "─" * 70 + RESET)

    return results

# ----------- MAIN -----------

if __name__ == "__main__":
    print(BOLD + CYAN + "\n=== ADVANCED IMAP EMAIL SCANNER ===\n" + RESET)

    email_user = input("Enter Gmail: ")
    app_password = input("Enter App Password: ")

    mail = connect_imap(email_user, app_password)
    print(GREEN + "\nConnected to inbox successfully!" + RESET)

    results = scan_emails(mail, limit=10)

    with open("final_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(BOLD + GREEN + "\nScan Complete! Results saved in final_results.json\n" + RESET)
