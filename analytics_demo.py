import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('scan_history.db')
cursor = conn.cursor()

print("=" * 70)
print("ANALYTICS DASHBOARD - REAL DATA FROM DATABASE")
print("=" * 70)

# Get all scans
cursor.execute("SELECT id, created_at, result_json FROM scans ORDER BY created_at DESC")
scans = cursor.fetchall()

print(f"\n✅ TOTAL SCANS: {len(scans)}")
print("=" * 70)

# Parse and analyze
all_threats = []
risk_distribution = {"SAFE": 0, "SUSPICIOUS": 0, "DANGER": 0}
threat_counts = {}
daily_stats = {}

for scan_id, created_at, result_json in scans:
    try:
        emails = json.loads(result_json)
        scan_date = created_at.split('T')[0]  # YYYY-MM-DD
        
        # Initialize daily stats
        if scan_date not in daily_stats:
            daily_stats[scan_date] = {"count": 0, "threats": 0}
        daily_stats[scan_date]["count"] += 1
        
        for email in emails:
            risk_level = email.get("risk_level", "SAFE")
            risk_score = email.get("risk_score", 0)
            subject = email.get("subject", "N/A")
            from_addr = email.get("from", "N/A")
            
            # Count risk levels
            if risk_level == "SAFE":
                risk_distribution["SAFE"] += 1
            elif risk_level == "SUSPICIOUS":
                risk_distribution["SUSPICIOUS"] += 1
                daily_stats[scan_date]["threats"] += 1
                threat_counts[subject] = threat_counts.get(subject, 0) + 1
            elif risk_level in ["DANGER", "HIGH"]:
                risk_distribution["DANGER"] += 1
                daily_stats[scan_date]["threats"] += 1
                threat_counts[subject] = threat_counts.get(subject, 0) + 1
            
            all_threats.append({
                "subject": subject,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "from": from_addr,
                "scan_date": scan_date
            })
    except json.JSONDecodeError:
        pass

# Display Analytics
print("\n📊 THREAT DISTRIBUTION:")
print("-" * 70)
total_emails = sum(risk_distribution.values())
for level, count in risk_distribution.items():
    pct = (count / total_emails * 100) if total_emails > 0 else 0
    bar = "█" * int(pct / 5)
    print(f"  {level:12} {count:3} emails  {pct:5.1f}%  {bar}")

print("\n🔍 TOP 10 THREATS DETECTED:")
print("-" * 70)
top_threats = sorted(threat_counts.items(), key=lambda x: x[1], reverse=True)[:10]
for i, (subject, count) in enumerate(top_threats, 1):
    preview = subject[:60] + "..." if len(subject) > 60 else subject
    print(f"  {i:2}. [{count}] {preview}")

print("\n📅 DAILY STATISTICS:")
print("-" * 70)
for date in sorted(daily_stats.keys()):
    stats = daily_stats[date]
    threat_pct = (stats["threats"] / stats["count"] * 100) if stats["count"] > 0 else 0
    print(f"  {date}: {stats['count']} scans, {stats['threats']} threats ({threat_pct:.1f}%)")

print("\n🎯 THREAT TRENDS:")
print("-" * 70)
suspicious_emails = [t for t in all_threats if t["risk_level"] in ["SUSPICIOUS", "DANGER", "HIGH"]]
safe_emails = [t for t in all_threats if t["risk_level"] == "SAFE"]
print(f"  Safe Emails:      {len(safe_emails)} ({len(safe_emails)/len(all_threats)*100:.1f}%)")
print(f"  Suspicious:       {len(suspicious_emails)} ({len(suspicious_emails)/len(all_threats)*100:.1f}%)")

print("\n📧 SAMPLE EMAILS ANALYZED:")
print("-" * 70)
# Show a few examples
for threat in suspicious_emails[:3]:
    print(f"\n  ⚠️  [{threat['risk_level']}] Risk Score: {threat['risk_score']}/10")
    print(f"      From: {threat['from'][:50]}")
    print(f"      Subject: {threat['subject'][:60]}")

print("\n" + "=" * 70)
print("✅ ANALYTICS DASHBOARD READY FOR DISPLAY IN UI")
print("=" * 70)

conn.close()
