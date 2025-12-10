from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from scanner_imap import scan_email_account
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__, template_folder='templates')
CORS(app)  # Allow frontend (React/HTML) calls

DB_PATH = "scan_history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        scanned_email TEXT,
        created_at TEXT,
        result_json TEXT
    );
    """)
    conn.commit()
    conn.close()

# Serve the HTML UI
@app.route("/", methods=["GET"])
def serve_ui():
    return render_template("index.html")

@app.route("/api/scan", methods=["POST"])
def api_scan():
    data = request.json
    gmail = data.get("gmail")
    app_password = data.get("app_password")
    limit = int(data.get("limit", 10))
    user_email = data.get("user_email") or gmail  # later: real login user

    if not gmail or not app_password:
        return jsonify({"error": "gmail and app_password are required"}), 400

    try:
        results = scan_email_account(gmail, app_password, limit=limit)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Save to DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO scans (user_email, scanned_email, created_at, result_json) VALUES (?, ?, ?, ?)",
        (user_email, gmail, datetime.utcnow().isoformat(), json.dumps(results))
    )
    conn.commit()
    conn.close()

    return jsonify({"results": results})

@app.route("/api/history", methods=["GET"])
def api_history():
    user_email = request.args.get("user_email")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if user_email:
        c.execute("SELECT id, scanned_email, created_at FROM scans WHERE user_email=? ORDER BY id DESC LIMIT 20", (user_email,))
    else:
        c.execute("SELECT id, scanned_email, created_at FROM scans ORDER BY id DESC LIMIT 20")
    rows = c.fetchall()
    conn.close()
    items = [
        {"id": r[0], "scanned_email": r[1], "created_at": r[2]}
        for r in rows
    ]
    return jsonify({"history": items})

@app.route("/api/history/<int:scan_id>", methods=["GET"])
def api_history_detail(scan_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT result_json FROM scans WHERE id=?", (scan_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify({"results": json.loads(row[0])})

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized")
    print("🚀 Flask app running at http://127.0.0.1:5000")
    print("📧 Open your browser and go to http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
