# Quick Start Guide - MailShield Pro API

## Prerequisites
- Python 3.7+
- pip

## Installation & Setup

### 1. Install Dependencies
```bash
pip install flask flask-cors pyjwt requests
```

### 2. Start the Server
```bash
python run.py
```

Server will start at: **http://127.0.0.1:5000**

### 3. Test the API
```bash
python test_api.py
```

---

## API Usage Examples

### Authentication

**Register a new user:**
```bash
curl -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "myemail@example.com",
    "password": "MySecurePassword123!"
  }'
```

Response:
```json
{
  "user_id": 1,
  "email": "myemail@example.com",
  "message": "User registered successfully",
  "success": true
}
```

**Login:**
```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "myemail@example.com",
    "password": "MySecurePassword123!"
  }'
```

Response (save the `access_token`):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 1,
  "email": "myemail@example.com",
  "is_admin": false,
  "message": "Login successful",
  "success": true
}
```

### URL Intelligence

**Check a single URL for phishing threats:**
```bash
curl -X POST http://127.0.0.1:5000/api/url-check \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://verify-account-urgent.secure-update.com"
  }'
```

Response:
```json
{
  "url": "https://verify-account-urgent.secure-update.com",
  "threat_score": 7.5,
  "risk_level": "DANGER",
  "threats_detected": [
    "Phishing keywords detected",
    "Suspicious TLD (.com mimicking)",
    "Homograph characters detected"
  ],
  "domain_age_days": 15,
  "success": true
}
```

**Check multiple URLs (batch):**
```bash
curl -X POST http://127.0.0.1:5000/api/url-check/batch \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://verify-account.com",
      "https://secure-login.xyz",
      "https://google.com"
    ]
  }'
```

### Analytics

**Get daily statistics:**
```bash
curl -X GET http://127.0.0.1:5000/api/analytics/daily \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
{
  "success": true,
  "statistics": {
    "total_scans": 15,
    "successful_scans": 14,
    "unique_emails": 300,
    "safe_emails": 290,
    "suspicious_emails": 8,
    "dangerous_emails": 2
  }
}
```

**Get threat trends (last 30 days):**
```bash
curl -X GET "http://127.0.0.1:5000/api/analytics/trends?days=30" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Get risk distribution:**
```bash
curl -X GET http://127.0.0.1:5000/api/analytics/distribution \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
{
  "success": true,
  "distribution": {
    "critical": 2,
    "high": 5,
    "medium": 12,
    "low": 45,
    "minimal": 236
  }
}
```

**Get top threats:**
```bash
curl -X GET "http://127.0.0.1:5000/api/analytics/threats?limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Email Scheduler

**Create a recurring scan schedule:**
```bash
curl -X POST http://127.0.0.1:5000/api/scheduler/create \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "gmail_account": "myemail@gmail.com",
    "frequency": "daily",
    "app_password": "xxxx xxxx xxxx xxxx"
  }'
```

Frequency options: `daily`, `weekly`, `monthly`, `every_2_hours`

Response:
```json
{
  "success": true,
  "schedule_id": 1,
  "frequency": "daily",
  "next_scan": "2025-11-29T12:30:00"
}
```

**List your schedules:**
```bash
curl -X GET http://127.0.0.1:5000/api/scheduler/list \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Update a schedule:**
```bash
curl -X PUT http://127.0.0.1:5000/api/scheduler/1/update \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "frequency": "weekly",
    "is_active": true
  }'
```

**Delete a schedule:**
```bash
curl -X DELETE http://127.0.0.1:5000/api/scheduler/1/delete \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Dashboard

**Get complete dashboard summary:**
```bash
curl -X GET http://127.0.0.1:5000/api/dashboard/summary \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Key Features

✅ **User Authentication** - Secure JWT token-based auth  
✅ **URL Intelligence** - Phishing & malware detection  
✅ **Analytics** - Comprehensive threat analytics  
✅ **Email Scheduler** - Automated recurring scans  
✅ **Slack Integration** - Real-time threat alerts  
✅ **Protected Endpoints** - All require authentication  
✅ **Batch Operations** - Check up to 50 URLs at once  
✅ **Production Ready** - Error handling & logging  

---

## Token Management

Tokens expire after 24 hours. Use the refresh token to get a new access token:

```bash
curl -X POST http://127.0.0.1:5000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

---

## Troubleshooting

**"Port 5000 already in use"**
- Change the port in run.py: `app.run(port=5001)`

**"No module named 'jwt'"**
- Install: `pip install pyjwt`

**"401 Unauthorized"**
- Include Authorization header: `-H "Authorization: Bearer YOUR_TOKEN"`

**"404 Not Found"**
- Check endpoint URL spelling
- Verify Flask is running

---

## Database

SQLite database: `scan_history.db` (auto-created on first run)

Tables:
- `users` - User accounts and profiles
- `scheduled_scans` - Email scan schedules
- `scans` - Historical scan results
- `scan_emails` - Email details from scans

---

## Security Notes

- Never commit your access tokens
- Change the SECRET_KEY in production
- Use HTTPS in production
- Store app passwords securely (use environment variables)
- Rate limit public endpoints
- Enable CORS only for trusted domains

---

## Support

For issues or questions, check:
- IMPLEMENTATION_COMPLETE.md (detailed feature documentation)
- test_api.py (example API calls)
- app logs for debugging

---

**Version:** 1.0.0  
**Last Updated:** November 28, 2025
