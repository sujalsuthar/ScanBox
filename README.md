# ScanBox - Enterprise Email Security Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**ScanBox** is an advanced email security platform that detects phishing attacks, malware, trojans, and email-based threats in real-time. Built with Python/Flask and featuring a professional web interface.

## 🚀 Features

- ✅ **Real-time Email Scanning** - IMAP integration with Gmail, Outlook, Yahoo
- ✅ **Advanced Threat Detection** - Phishing, malware, trojans, archive files
- ✅ **File-Sharing Analysis** - Detects Google Drive/Dropbox/OneDrive threats
- ✅ **Archive Scanning** - ZIP/RAR/7z malware detection
- ✅ **Risk Scoring** - 0-100 scale with SAFE/WARNING/DANGER classification
- ✅ **Professional Dashboard** - Responsive web UI with real-time updates
- ✅ **RESTful API** - JSON endpoints for integration

## Quick Start

**Step 1: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 2: Run Application**
```bash
python app.py
```

**Step 3: Open Browser**
```
http://127.0.0.1:5000
```

**Step 2: Open Browser**
- Go to: `http://127.0.0.1:5000`
- Enter your Gmail and App Password
- Click "Scan Now"

That's it! The HTML UI will call the Flask API in the background.

---

## Project Structure

```
newproject/
├── scanner_imap.py          # Core scanning logic (reusable)
├── app.py                   # Flask API (no UI template)
├── app_full.py              # Flask API + serves HTML template
├── templates/
│   └── index.html           # Beautiful web UI
├── scan_history.db          # Auto-created SQLite database
└── README.md                # This file
```

---

## API Endpoints

All endpoints are available at `http://127.0.0.1:5000`

### 1. **POST /api/scan** - Scan emails
```json
POST /api/scan
{
  "gmail": "your@gmail.com",
  "app_password": "xxxx xxxx xxxx xxxx",
  "limit": 10,
  "user_email": "your@gmail.com"
}

Response:
{
  "results": [
    {
      "subject": "Verify your account",
      "from": "noreply@bank.com",
      "date": "Mon, 28 Nov 2025 12:34:56",
      "urls": ["https://phishing.com"],
      "attachments": [{"name": "invoice.pdf", "sha256": "abc123..."}],
      "risk_score": 8,
      "risk_level": "DANGEROUS",
      "snippet": "Please click here to verify your account..."
    }
  ]
}
```

### 2. **GET /api/history** - Get scan history
```
GET /api/history?user_email=your@gmail.com
GET /api/history  (all scans)

Response:
{
  "history": [
    {"id": 1, "scanned_email": "your@gmail.com", "created_at": "2025-11-28T12:34:56"},
    {"id": 2, "scanned_email": "your@gmail.com", "created_at": "2025-11-28T12:45:00"}
  ]
}
```

### 3. **GET /api/history/<id>** - Get scan details
```
GET /api/history/1

Response:
{
  "results": [
    { /* full email scan result */ }
  ]
}
```

---

## Risk Scoring

| Score | Level | Indicators |
|-------|-------|-----------|
| 0-3 | SAFE | No red flags |
| 4-7 | SUSPICIOUS | Contains verify/password/login keywords or URLs |
| 8+ | DANGEROUS | Multiple risk factors (phishing keywords + URLs + attachments) |

---

## Features

✅ **Scan Gmail inbox** with app password
✅ **Detect phishing** emails (keywords: verify, password, login, bank, reset, otp)
✅ **Extract URLs** from email bodies
✅ **Hash attachments** (SHA256)
✅ **Beautiful web UI** with risk level badges
✅ **SQLite history** - all scans are saved
✅ **CORS enabled** - ready for React frontend
✅ **Responsive design** - works on desktop & mobile

---

## Next Steps

### Want React Dashboard?
Create a React app:
```bash
npx create-react-app email-scanner-frontend
```
Then the React app can call the same `http://127.0.0.1:5000/api/...` endpoints.

### Want Login System?
The database is already ready. You can add:
- User table with hashed passwords
- Session/JWT tokens
- User-specific scan history
- Email verification

### Want to Deploy?
- **Backend**: Deploy `app_full.py` to Heroku/Railway/etc (keep it running)
- **Frontend**: Deploy React build to Vercel/Netlify

---

## Troubleshooting

**"Connection refused" error?**
- Make sure Flask is running: `python app_full.py`
- Check it's on `http://127.0.0.1:5000` (not `localhost`)

**"Invalid app password" error?**
- Generate a 16-character App Password from Google Account (not your Gmail password)
- Gmail → Security → App passwords

**"No emails found"?**
- Your inbox might be empty, or the limit is too high
- Try limit=5 first

---

## Security Notes

- Your Gmail password is only sent to Gmail's IMAP server, never stored
- Scan results are stored locally in `scan_history.db`
- For production, use environment variables for credentials
- Consider adding HTTPS when deploying

---

Enjoy! 🎉
