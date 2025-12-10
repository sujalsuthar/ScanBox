import sqlite3

conn = sqlite3.connect('scan_history.db')
cursor = conn.cursor()

print("=== SCANS TABLE SCHEMA ===")
cursor.execute("PRAGMA table_info(scans)")
cols = cursor.fetchall()
for col in cols:
    print(f"  {col[1]}: {col[2]}")

print("\n=== FIRST 2 SCANS (for preview) ===")
cursor.execute("SELECT * FROM scans LIMIT 2")
rows = cursor.fetchall()
print(f"Found {len(rows)} rows")

# Get actual column names
cursor.execute("PRAGMA table_info(scans)")
col_names = [row[1] for row in cursor.fetchall()]
print(f"Columns: {col_names}")

for i, row in enumerate(rows, 1):
    print(f"\nScan {i}:")
    for name, value in zip(col_names, row):
        if value and len(str(value)) > 100:
            print(f"  {name}: {str(value)[:100]}...")
        else:
            print(f"  {name}: {value}")

conn.close()
