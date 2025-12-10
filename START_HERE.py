#!/usr/bin/env python
"""
Quick start script for Email Scanner Project
Run this to get everything running!
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def main():
    print_header("📧 EMAIL SCANNER - QUICK START")
    
    print("🎯 Project Setup Complete!\n")
    print("Your project now includes:\n")
    print("  ✅ scanner_imap.py      - Core scanning logic (reusable module)")
    print("  ✅ app.py                - Flask API (bare endpoints)")
    print("  ✅ app_full.py           - Flask API + serves HTML UI")
    print("  ✅ templates/index.html  - Beautiful web interface")
    print("  ✅ test_api.py           - API testing script")
    print("  ✅ scan_history.db       - SQLite database (auto-created)")
    
    print_header("🚀 TO START THE PROJECT")
    
    print("Option 1: RUN WITH HTML UI (Recommended!)\n")
    print("  $ python app_full.py")
    print("  Then open: http://127.0.0.1:5000\n")
    
    print("Option 2: RUN API ONLY\n")
    print("  $ python app.py")
    print("  Then call API endpoints from React/Postman/etc\n")
    
    print_header("📚 WHAT TO DO NEXT")
    
    print("1️⃣  Start the Flask server:")
    print("    python app_full.py\n")
    
    print("2️⃣  Open your browser:")
    print("    http://127.0.0.1:5000\n")
    
    print("3️⃣  Enter your Gmail credentials:")
    print("    - Gmail: your@gmail.com")
    print("    - App Password: 16-character password from Google Account\n")
    
    print("4️⃣  Click 'Scan Now' and see results!\n")
    
    print_header("🔗 API ENDPOINTS")
    
    print("POST /api/scan - Scan emails")
    print("  Input: {gmail, app_password, limit, user_email}")
    print("  Returns: {results: [{subject, from, date, urls, ...}]}\n")
    
    print("GET /api/history - Get scan history")
    print("  Query: ?user_email=your@gmail.com (optional)")
    print("  Returns: {history: [{id, scanned_email, created_at}]}\n")
    
    print("GET /api/history/<id> - Get scan details")
    print("  Returns: {results: [...]}\n")
    
    print_header("❓ NEED HELP?")
    
    print("Connection refused?")
    print("  → Make sure Flask is running: python app_full.py")
    print("  → Check URL: http://127.0.0.1:5000\n")
    
    print("Invalid app password?")
    print("  → Go to: Google Account → Security → App passwords")
    print("  → Generate 16-character App Password (NOT your Gmail password)\n")
    
    print("Want React Dashboard?")
    print("  → Create: npx create-react-app frontend")
    print("  → Call same /api/... endpoints from React\n")
    
    print_header("🎉 YOU'RE READY!")
    
    print("Your complete project stack is ready to run.")
    print("Start Flask and open http://127.0.0.1:5000\n")

if __name__ == "__main__":
    main()
