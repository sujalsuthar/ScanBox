#!/usr/bin/env python
"""Reset test user passwords"""

import sqlite3
from app.auth.utils import AuthUtils

# Test accounts and their passwords
test_accounts = [
    ('test@example.com', 'test123'),
    ('testuser@example.com', 'password123'),
    ('uitest@example.com', 'password123'),
    ('admin@example.com', 'admin123'),  # Create an admin user
]

conn = sqlite3.connect('scan_history.db')
c = conn.cursor()

for email, password in test_accounts:
    hashed_password = AuthUtils.hash_password(password)
    
    # Try to update existing user
    c.execute("UPDATE users SET password_hash = ? WHERE email = ?", (hashed_password, email))
    
    if c.rowcount == 0:
        # User doesn't exist, create them
        is_admin = 1 if 'admin' in email else 0
        c.execute("""
            INSERT INTO users (email, password_hash, is_admin, is_active)
            VALUES (?, ?, ?, 1)
        """, (email, hashed_password, is_admin))
        print(f"✓ Created user: {email} (password: {password})")
    else:
        print(f"✓ Updated user: {email} (password: {password})")

conn.commit()
conn.close()

# Verify the logins work
print("\n--- Testing logins ---")
from app.models.user import User
User.init_table()

for email, password in test_accounts:
    result = User.verify_credentials(email, password)
    status = "✓ SUCCESS" if result['success'] else "✗ FAILED"
    print(f"{status}: {email} / {password}")
    if not result['success']:
        print(f"  Error: {result['error']}")
