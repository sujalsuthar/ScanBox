# Scanbox – User Manual (Windows)

A concise, step‑by‑step guide to set up, run, and use Scanbox — the advanced email security scanner with a web UI and API.

---

## 1) Prerequisites
- Python 3.10+ installed (check with `python --version`)
- Internet access (for Gmail IMAP)
- A Gmail account with App Password enabled (2‑Step Verification required)

Useful links:
- Create a Gmail App Password: https://support.google.com/accounts/answer/185833

---

## 2) Project Setup (PowerShell)
Run these from the project folder: `C:\Users\TUF\Desktop\newproject`

```powershell
# 1) Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 3) Create an .env file from the example
Copy-Item .env.example .env

# 4) (Optional) Adjust .env values
# - FLASK_ENV=development (keep for local dev)
# - FLASK_PORT=5000
# - SECRET_KEY=change-this-in-production
# - DB_PATH=scan_history.db
```

---

## 3) Start the Web App
```powershell
# From the project root with venv activated
python run.py
```
If successful, you’ll see logs indicating:
- Server: http://127.0.0.1:5000
- Debugger is active (in development)

Open the web UI in your browser:
- http://127.0.0.1:5000/

---

## 4) Using the Web UI
The UI lives at `http://127.0.0.1:5000/` and includes tabs in the sidebar/top:

- Scanner: Scan your Gmail with your Gmail address and App Password. Choose how many recent emails to scan.
- Analytics: View trends, distribution, and top threats (requires login).
- Scheduler: Create recurring scans (requires login).
- History: Browse previous scans and results.
- Bulk Scan: Upload multiple `.eml` files for batch scanning.
- Admin: Manage users, view audit logs (requires admin role).
- Reports: Download CSV summary; schedule PDF/CSV (requires login).
- Policies: Create block/allow rules (requires login).
- Tenants: Manage multiple client orgs (requires login).
- Settings: Register/Login and manage authentication.

Quick flow:
1. Go to Settings → Register or Login.
2. Return to Scanner, enter Gmail + App Password, set `Emails to Scan`, click Scan Now.
3. View results (risk level, URLs, attachments). Check Analytics, History, and Reports as needed.

---

## 5) REST API Quick Examples (PowerShell)
Use `Invoke-RestMethod` for quick API calls. Replace values as needed.

- Health check
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/health" -Method GET
```

- Register
```powershell
$body = @{ email = "you@example.com"; password = "StrongPass123" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/auth/register" -Method POST -ContentType "application/json" -Body $body
```

- Login (returns `access_token`)
```powershell
$body = @{ email = "you@example.com"; password = "StrongPass123" } | ConvertTo-Json
$login = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/auth/login" -Method POST -ContentType "application/json" -Body $body
$token = $login.access_token
```

- Scan (Gmail + App Password, optional `limit`)
```powershell
$scanBody = @{ gmail = "yourname@gmail.com"; app_password = "xxxx xxxx xxxx xxxx"; limit = 20 } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/scan" -Method POST -ContentType "application/json" -Body $scanBody
```

- History
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/history?limit=20" -Method GET
```

- Reports (CSV – requires login token)
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:5000/reports/csv?days=7" -Headers @{ Authorization = "Bearer $token" } -OutFile "scanbox_report.csv"
```

---

## 6) Command‑Line Scanner (IMAP)
If you want a quick console scan without the web app:

```powershell
# With venv activated
python .\email_scanner_imap.py
```
You’ll be prompted for Gmail and App Password. Results are saved to `final_results.json` and printed in color in the terminal.

---

## 7) Where Results Are Stored
- Web app: Results stored in SQLite DB `scan_history.db`, with endpoints to fetch history and details.
- CLI IMAP script: Writes JSON to `final_results.json` after each run.
- Logs: `app.log` (when not in development) or console output in development.

---

## 8) Troubleshooting
- Exit Code 1 when starting:
  - Ensure venv is activated and deps installed: `pip install -r requirements.txt`
  - Verify Python version: `python --version` (3.10+)
  - Delete stale `__pycache__/` and retry.
  - Check port 5000 isn’t in use; if it is, set a new port in `.env` (`FLASK_PORT=5001`).

- Can’t connect to Gmail:
  - You must use an App Password (not your normal password). Enable 2‑Step Verification, then create an App Password in Google Account → Security.

- CORS or Auth errors in UI:
  - Make sure you are accessing `http://127.0.0.1:5000/` directly.
  - If using tokens, ensure `Authorization: Bearer <token>` header is set for protected endpoints.

- Database issues:
  - Delete `scan_history.db` to reset (you’ll lose history) or set a new `DB_PATH` in `.env`.

- Change server host/port:
  - Edit `.env` (`FLASK_HOST`, `FLASK_PORT`) and restart `python run.py`.

---

## 9) Useful Scripts/Files
- `run.py`: Starts the Flask web app (UI + API)
- `templates/index.html`: The Scanbox web UI
- `app/`: Backend modules, routes, services, models
- `email_scanner_imap.py`: Standalone IMAP scanner (CLI)
- `.env.example`: Environment template (copy to `.env`)
- `requirements.txt`: Python dependencies

---

## 10) Quick Start (TL;DR)
```powershell
cd C:\Users\TUF\Desktop\newproject
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
# Open http://127.0.0.1:5000/ in your browser
```
