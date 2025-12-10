# 📧 Email Scanner API - Professional Edition

A production-ready Flask API for scanning Gmail inboxes for phishing and malware threats.

## ✨ Features

### Core Scanning
- 🔍 **Advanced Email Analysis** - Detects phishing, malware, and suspicious content
- 🎯 **Risk Scoring** - Automatic risk level classification (SAFE/SUSPICIOUS/DANGEROUS)
- 🔗 **URL Extraction** - Identifies and flags suspicious URLs
- 📎 **Attachment Analysis** - Computes SHA256 hashes for malware detection
- 🔐 **Secure Credentials** - App password only, never stored

### API & Database
- 🏗️ **RESTful API** - Professional endpoints with proper status codes
- 📊 **SQLite Database** - Built-in history and audit logging
- 📈 **Scan Analytics** - Risk summary and statistics
- ⚡ **Optimized Queries** - Database indexes for performance

### Professional Quality
- 🛡️ **Error Handling** - Comprehensive exception handling and logging
- ✅ **Input Validation** - Strict validation for all inputs
- 📝 **Full Documentation** - Type hints and docstrings throughout
- 🧪 **Production Ready** - Config management, environment variables
- 🎨 **Beautiful UI** - Responsive web interface included

---

## 🚀 Quick Start

### Installation

```bash
# Clone/setup project
cd newproject

# Create virtual environment (if not done)
python -m venv .venv
.venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

#### Development Mode (Recommended)
```bash
python run.py
```

Then open in browser: **http://127.0.0.1:5000**

#### Production Mode
```bash
set FLASK_ENV=production
python run.py
```

---

## 📚 API Documentation

### Base URL
```
http://127.0.0.1:5000
```

### Endpoints

#### 1. **POST /api/scan** - Scan Emails
Scan a Gmail account for threats.

**Request:**
```json
{
  "gmail": "user@gmail.com",
  "app_password": "xxxx xxxx xxxx xxxx",
  "limit": 10,
  "user_email": "user@gmail.com"
}
```

**Response (200):**
```json
{
  "scan_id": 1,
  "results": [
    {
      "subject": "Verify your account",
      "from": "noreply@bank.com",
      "date": "Mon, 28 Nov 2025 12:34:56",
      "risk_level": "DANGEROUS",
      "risk_score": 8,
      "urls": ["https://phishing.com"],
      "attachments": [{"name": "invoice.pdf", "sha256": "abc123..."}],
      "snippet": "Click here to verify..."
    }
  ],
  "summary": {
    "total_emails": 10,
    "safe_emails": 7,
    "suspicious_emails": 2,
    "dangerous_emails": 1,
    "average_risk_score": 3.5
  }
}
```

**Error Response (400):**
```json
{
  "error": "Validation Error",
  "message": "Invalid app_password: App password must be 16 characters"
}
```

---

#### 2. **GET /api/history** - Get Scan History
Retrieve past scans.

**Query Parameters:**
- `user_email` (optional): Filter by user
- `limit` (optional): Max records (default: 20, max: 100)

**Example:**
```
GET /api/history?user_email=user@gmail.com&limit=10
```

**Response:**
```json
{
  "history": [
    {
      "id": 1,
      "scanned_email": "target@gmail.com",
      "created_at": "2025-11-28T12:34:56.123456",
      "status": "completed"
    }
  ],
  "count": 1
}
```

---

#### 3. **GET /api/history/<id>** - Get Scan Details
Retrieve full results of a specific scan.

**Example:**
```
GET /api/history/1
```

**Response:**
```json
{
  "scan_id": 1,
  "results": [
    {
      "subject": "...",
      "from": "...",
      "risk_level": "...",
      "risk_score": 5,
      "urls": [],
      "attachments": [],
      "snippet": "..."
    }
  ],
  "summary": {
    "total_emails": 10,
    "safe_emails": 8,
    "suspicious_emails": 2,
    "dangerous_emails": 0,
    "average_risk_score": 2.0
  }
}
```

---

#### 4. **GET /api/stats** - Get Statistics
Overall scanning statistics.

**Query Parameters:**
- `user_email` (optional): Filter by user

**Response:**
```json
{
  "total_scans": 42,
  "user_email": "user@gmail.com"
}
```

---

#### 5. **GET /health** - Health Check
Check API status.

**Response:**
```json
{
  "status": "healthy",
  "service": "email-scanner-api",
  "version": "1.0.0",
  "timestamp": 1701173696.123
}
```

---

## 🔒 Security Notes

### Gmail Setup
1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Generate **16-character App Password**
4. Use this password, NOT your Gmail password

### Best Practices
- ✅ **Never share** app passwords
- ✅ Use **environment variables** for credentials
- ✅ Set strong **SECRET_KEY** in production
- ✅ Enable **HTTPS** when deployed
- ✅ Use database encryption for sensitive data
- ✅ Implement **rate limiting** on endpoints
- ✅ Log all access for **audit trails**

---

## 📊 Risk Scoring System

| Score | Level | Indicators |
|-------|-------|-----------|
| 0-3 | 🟢 **SAFE** | No red flags detected |
| 4-7 | 🟡 **SUSPICIOUS** | Phishing keywords or URLs present |
| 8-10 | 🔴 **DANGEROUS** | Multiple risk factors combined |

### Risk Indicators
- **+3 points**: Contains "verify", "password", "login", "bank", "update", "otp"
- **+2 points**: Contains "reset"
- **+2 points**: Contains URLs
- **+4 points**: Has attachments

---

## 🏗️ Project Structure

```
newproject/
├── app/
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py            # API endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py          # Database management
│   ├── services/
│   │   ├── __init__.py
│   │   └── scan_service.py      # Business logic
│   └── utils/
│       ├── __init__.py
│       └── validators.py        # Input validation
├── templates/
│   └── index.html               # Web UI
├── scanner_imap.py              # Scanner module
├── run.py                        # Entry point
├── requirements.txt             # Dependencies
├── .env.example                 # Example env file
├── .env.development             # Dev config
└── README.md                    # This file
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Server
FLASK_ENV=development              # development|production|testing
FLASK_HOST=127.0.0.1
FLASK_PORT=5000

# Security
SECRET_KEY=your-secret-key-here

# Database
DB_PATH=scan_history.db

# CORS
CORS_ORIGINS=*                     # Or specific origins separated by commas
```

### Configuration Files

- **`app/config.py`** - Python configuration classes
- **`.env`** - Local environment overrides
- **`.env.development`** - Development defaults
- **`.env.example`** - Example template

---

## 🧪 Testing

### Test the API with curl

```bash
# Health check
curl http://127.0.0.1:5000/health

# Scan emails (replace with real credentials)
curl -X POST http://127.0.0.1:5000/api/scan \
  -H "Content-Type: application/json" \
  -d '{
    "gmail": "your@gmail.com",
    "app_password": "xxxx xxxx xxxx xxxx",
    "limit": 10
  }'

# Get history
curl http://127.0.0.1:5000/api/history

# Get scan details
curl http://127.0.0.1:5000/api/history/1
```

### Using test_api.py
```bash
python test_api.py
```

---

## 🐛 Troubleshooting

### "Connection refused"
- Check Flask is running: `python run.py`
- Verify URL: `http://127.0.0.1:5000`

### "Invalid app password"
- Go to Google Account → Security → App passwords
- Generate NEW 16-character password
- Don't use your Gmail password

### "No emails found"
- Check mailbox is not empty
- Try increasing limit: `"limit": 50`
- Check IMAP is enabled in Gmail settings

### Database errors
- Delete `scan_history.db` to reset
- Ensure write permissions to directory
- Check disk space

### Import errors
- Reinstall dependencies: `pip install -r requirements.txt`
- Verify virtual environment is activated
- Check Python version (3.7+ required)

---

## 📖 Developer Guide

### Adding New Endpoints

1. Create handler in `app/api/routes.py`
2. Add validation in `app/utils/validators.py`
3. Add business logic in `app/services/`
4. Test with curl or Postman

Example:
```python
@app.route("/api/new-endpoint", methods=["POST"])
def new_endpoint():
    """Endpoint documentation."""
    data = request.get_json()
    # Validate, process, respond
    return jsonify({...}), 200
```

### Adding Database Tables

1. Update schema in `app/models/database.py`
2. Add migration documentation
3. Use `DatabaseManager` for queries

### Extending Services

Services in `app/services/` handle business logic:

```python
class NewService:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def do_something(self, param):
        # Use self.db for database operations
        pass
```

---

## 📦 Deployment

### Local Testing
```bash
python run.py
```

### Production Server (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Docker (Coming Soon)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:create_app()"]
```

---

## 📝 Logging

Logs are written to:
- **Console** - All environments
- **app.log** - Production only

View logs:
```bash
# Real-time (Linux/Mac)
tail -f app.log

# Search logs
grep ERROR app.log
```

---

## 🤝 Contributing

Improvements welcome! Focus areas:
- [ ] React frontend
- [ ] User authentication
- [ ] Advanced threat detection
- [ ] Email scheduling
- [ ] Slack notifications
- [ ] API rate limiting
- [ ] Performance optimization

---

## 📄 License

MIT License - Feel free to use for personal/commercial projects

---

## 🆘 Support

Issues? Check:
1. **Logs** - Check app.log or console output
2. **Health check** - `curl http://127.0.0.1:5000/health`
3. **Database** - Ensure `scan_history.db` is readable/writable
4. **Credentials** - Verify Gmail and app password are correct

---

**Happy scanning! 🔒🚀**
