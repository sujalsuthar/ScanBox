# 🚀 QUICK COMMAND REFERENCE

## Starting the Application

### Development Mode
```bash
python run.py
```
- Auto-reload on changes
- Debug toolbar enabled
- Full logging
- Open: http://127.0.0.1:5000

### Production Mode
```bash
set FLASK_ENV=production
python run.py
```

---

## Testing Endpoints

### Health Check (Always Works)
```bash
curl http://127.0.0.1:5000/health
```

### Get History (No Credentials Needed)
```bash
curl http://127.0.0.1:5000/api/history
```

### Scan Emails (Requires Gmail Credentials)
```bash
curl -X POST http://127.0.0.1:5000/api/scan ^
  -H "Content-Type: application/json" ^
  -d {\"gmail\":\"your@gmail.com\",\"app_password\":\"xxxx xxxx xxxx xxxx\",\"limit\":10}
```

### Get Scan Details
```bash
curl http://127.0.0.1:5000/api/history/1
```

### Get Statistics
```bash
curl http://127.0.0.1:5000/api/stats
```

---

## Common Issues & Solutions

### Server won't start
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Or use different port
set FLASK_PORT=5001
python run.py
```

### Template not found
- Ensure `templates/index.html` exists
- Server should find it automatically

### Database error
```bash
# Reset database
del scan_history.db

# Restart server
python run.py
```

### Module not found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

---

## Project Structure Quick Reference

```
📁 newproject/
├─ app/                    # Main application code
│  ├─ __init__.py         # Flask factory
│  ├─ config.py           # Configuration
│  ├─ api/routes.py       # API endpoints
│  ├─ services/           # Business logic
│  ├─ models/             # Database layer
│  └─ utils/              # Validation
├─ templates/             # Web UI
│  └─ index.html
├─ run.py                 # Start script
├─ scanner_imap.py        # Scanner module
├─ requirements.txt       # Dependencies
└─ scan_history.db        # SQLite database
```

---

## Environment Variables

```bash
# View current settings
set FLASK_ENV         # development|production|testing
set FLASK_HOST        # 127.0.0.1
set FLASK_PORT        # 5000
set SECRET_KEY        # Your secret (production only)
set DB_PATH           # Path to database
set CORS_ORIGINS      # Allowed origins
```

---

## Development Workflow

1. **Start server**
   ```bash
   python run.py
   ```

2. **Edit code** (auto-reload happens automatically)
   ```bash
   # Edit any file in app/
   # Changes reflected immediately
   ```

3. **Test in browser**
   ```
   http://127.0.0.1:5000
   ```

4. **Check logs**
   ```bash
   # Logs appear in terminal
   # Also saved to app.log
   ```

---

## Useful Commands

```bash
# Check Python version
python --version

# Activate virtual environment
.venv\Scripts\activate

# Deactivate virtual environment
deactivate

# Install dependencies
pip install -r requirements.txt

# Update requirements
pip freeze > requirements.txt

# List installed packages
pip list

# Check syntax errors
python -m py_compile app/__init__.py
```

---

## API Quick Reference

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/` | Web UI | No |
| GET | `/health` | Health check | No |
| POST | `/api/scan` | Scan emails | Credentials in body |
| GET | `/api/history` | Get history | No |
| GET | `/api/history/<id>` | Get details | No |
| GET | `/api/stats` | Get statistics | No |

---

## Configuration Files

- **`.env`** - Local overrides (add to .gitignore)
- **`.env.example`** - Template for users
- **`.env.development`** - Dev defaults
- **`app/config.py`** - Python config classes

---

## Performance Tips

- Close browser tab when not in use
- Increase `limit` carefully (max 100)
- Use `/api/history` instead of full scan when possible
- Database auto-optimizes on startup

---

## Monitoring

Watch the logs for:
- `INFO` - Normal operations
- `WARNING` - Potential issues
- `ERROR` - Problems to fix

Example from logs:
```
[2025-11-28 11:54:11] app - INFO: Flask app created
[2025-11-28 11:54:11] werkzeug - INFO: Running on http://127.0.0.1:5000
[2025-11-28 11:54:15] werkzeug - INFO: GET / - 200 OK
```

---

**Questions? Check PROFESSIONAL_README.md for full documentation!**
