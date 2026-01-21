

# ScanBox

### Enterprise Email Security & Phishing Detection Platform

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**ScanBox** is an enterprise-ready email security platform designed to detect **phishing attacks, malicious links, trojans, and suspicious attachments** in real time.
It integrates directly with email inboxes via **IMAP (read-only)** and provides actionable risk scoring through a professional web dashboard and REST APIs.

---

## 🔐 Why ScanBox?

Email remains the **#1 attack vector** for cyber threats. ScanBox helps individuals, startups, and organizations:

* Detect phishing attempts before users click
* Identify malicious URLs and file attachments
* Analyze inboxes without modifying or deleting emails
* Maintain an auditable scan history
* Integrate security scanning into existing systems via APIs

---

## 🚀 Key Features

### Email Security

* **Real-time Inbox Scanning** via IMAP (Gmail, Outlook, Yahoo)
* **Read-only Access** – emails are never modified or deleted
* **Phishing Detection** using keyword and URL analysis
* **Malicious Attachment Detection** with SHA-256 hashing
* **Archive Scanning** (ZIP / RAR / 7z)
* **Cloud Link Analysis** (Google Drive, Dropbox, OneDrive)

### Risk Intelligence

* **Dynamic Risk Scoring (0–100)**
* **Threat Classification**: SAFE / SUSPICIOUS / DANGEROUS
* **Contextual Indicators** (keywords, links, attachments)

### Platform Capabilities

* **Professional Web Dashboard**
* **RESTful API** for system integration
* **SQLite-based Scan History**
* **CORS Enabled** (React / frontend-ready)
* **Responsive UI** (desktop & mobile)

---

## 🧠 Risk Scoring Model

| Score Range | Risk Level | Description                            |
| ----------- | ---------- | -------------------------------------- |
| 0 – 3       | SAFE       | No suspicious indicators               |
| 4 – 7       | SUSPICIOUS | Phishing keywords or suspicious URLs   |
| 8+          | DANGEROUS  | Multiple high-risk indicators detected |

---

## 🏗️ Project Architecture

```
newproject/
├── scanner_imap.py          # Core email scanning engine (reusable)
├── app.py                   # Flask REST API (headless)
├── app_full.py              # Flask API + HTML dashboard
├── templates/
│   └── index.html           # Web dashboard UI
├── scan_history.db          # Auto-generated SQLite database
└── README.md                # Documentation
```

---

## ⚙️ Quick Start

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Run the Application

```bash
python app_full.py
```

### 3️⃣ Access the Dashboard

```
http://127.0.0.1:5000
```

### 4️⃣ Scan Emails

* Enter your email address
* Use a **Gmail App Password** (not your actual password)
* Click **Scan Now**

---

## 🔌 API Documentation

Base URL:

```
http://127.0.0.1:5000
```

### ▶ POST `/api/scan` – Scan Emails

```json
{
  "gmail": "your@gmail.com",
  "app_password": "xxxx xxxx xxxx xxxx",
  "limit": 10,
  "user_email": "your@gmail.com"
}
```

**Response**

```json
{
  "results": [
    {
      "subject": "Verify your account",
      "from": "noreply@bank.com",
      "date": "Mon, 28 Nov 2025 12:34:56",
      "urls": ["https://phishing.com"],
      "attachments": [
        {
          "name": "invoice.pdf",
          "sha256": "abc123..."
        }
      ],
      "risk_score": 8,
      "risk_level": "DANGEROUS",
      "snippet": "Please click here to verify your account..."
    }
  ]
}
```

---

### ▶ GET `/api/history` – Scan History

```
/api/history
/api/history?user_email=your@gmail.com
```

### ▶ GET `/api/history/<id>` – Scan Details

```
/api/history/1
```

---

## 🛡️ Security & Privacy

* Credentials are used **only for IMAP authentication**
* No email content is altered or deleted
* Passwords are **never stored**
* Scan results are stored locally in SQLite
* Production deployments should use:

  * Environment variables
  * HTTPS
  * Encrypted storage

---

## 🚀 Deployment Options

### Backend

* Railway
* Render
* Heroku
* VPS (Docker-ready)

### Frontend

* React + Vercel
* Netlify
* Any REST-compatible client

---

## 🔮 Roadmap

* 🔐 User Authentication (JWT)
* 📊 Phishing Analytics Dashboard
* ⚛ React Admin Panel
* ☁ Cloud Deployment
* 🧪 AI-based Phishing Detection
* 🏢 Multi-tenant Enterprise Mode

---

## 🎯 Ideal Use Cases

* Cybersecurity students & researchers
* SOC & security teams
* Startups needing email threat analysis
* Academic demonstrations
* Resume & portfolio projects

---

## 📜 License

This project is licensed under the **MIT License**.

---

## ✨ Final Note

**ScanBox demonstrates real-world email security concepts, backend API design, and threat analysis workflows used in modern cybersecurity platforms.**

