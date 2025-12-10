#!/usr/bin/env python3
"""View database contents - quick script to inspect scan results"""

import sqlite3
import json
from pathlib import Path

db_path = Path(__file__).parent / "scan_history.db"

if not db_path.exists():
    print(f"❌ Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("\n" + "="*80)
print("📊 EMAIL SCANNER DATABASE CONTENTS")
print("="*80)

# Get all scans
c.execute("SELECT * FROM scans ORDER BY created_at DESC")
scans = c.fetchall()

print(f"\n✅ Total Scans: {len(scans)}\n")

for scan in scans:
    print(f"📌 Scan ID: {scan['id']}")
    print(f"   User Email: {scan['user_email']}")
    print(f"   Scanned Email: {scan['scanned_email']}")
    print(f"   Created: {scan['created_at']}")
    print(f"   Status: {scan['status']}")
    
    if scan['error_message']:
        print(f"   ⚠️  Error: {scan['error_message']}")
    
    try:
        result = json.loads(scan['result_json'])
        print(f"   📧 Emails Found: {result.get('total_emails', 0)}")
        print(f"   ⚠️  Suspicious URLs: {result.get('suspicious_urls', 0)}")
        print(f"   🔴 Risk Level: {result.get('risk_level', 'Unknown')}")
    except:
        pass
    
    print()

# Show table structure
print("\n" + "="*80)
print("🗂️  DATABASE SCHEMA")
print("="*80 + "\n")

c.execute("PRAGMA table_info(scans)")
columns = c.fetchall()
for col in columns:
    print(f"  • {col[1]}: {col[2]}")

conn.close()
print("\n" + "="*80)
