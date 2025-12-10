# How to Login - Quick Guide

## Where is the Login?

The **Login/Register form** is in the **⚙️ Settings Tab** on the right side navigation.

## Steps to Login:

### 1. Open the App
```
http://127.0.0.1:5000
```

### 2. Click Settings Tab
Look at the top navigation tabs or left sidebar:
- 🔍 Scanner
- 📊 Analytics
- ⏰ Scheduler  
- 📜 History
- **⚙️ Settings** ← CLICK HERE

### 3. Find Authentication Section
Under Settings tab, you'll see:

```
🔐 Authentication

[Email input field]
[Password input field]

[Login Button]  [Register Button]
```

### 4. First Time? Register
- Click **📝 Register** button
- Enter your email: `yourname@example.com`
- Enter a password: `MySecurePassword123!`
- Click Register
- You'll be automatically logged in

### 5. Already Have Account? Login
- Enter your email
- Enter your password
- Click **🔓 Login**
- You're now authenticated!

---

## After Login

Once logged in, the Settings tab shows:

```
✓ You are logged in
Session is active and all features are available.

[🔓 Logout Button]
```

Now you can access:
- ✅ **Analytics Tab** - View threat data
- ✅ **Scheduler Tab** - Create recurring scans
- ✅ **Slack Integration** - Configure webhooks
- ✅ **All protected endpoints**

---

## Token Persistence

Your login token is automatically saved to **browser localStorage**, so:
- You stay logged in when you refresh the page
- Token is included in all API requests
- Logout clears the token

---

## Troubleshooting

**"Please login to view analytics"**
- Go to Settings tab (⚙️)
- Register or Login first
- Then access Analytics tab

**"Missing or invalid authorization header"**
- Your token expired or wasn't saved
- Logout and login again from Settings tab

**Can't find Settings tab?**
- It's the last tab on the right: ⚙️
- Or scroll horizontally if on mobile

---

## Full Navigation Map

```
SIDEBAR (Left)                  TOP TABS
┌─────────────────┐            ┌────────────────────────────────┐
│ 🛡️ MailShield   │            │🔍  📊  ⏰  📜  ⚙️              │
│                 │            │Scanner Analytics Scheduler... Settings│
│ 🔍 Scanner      │──────────→ │                                │
│ 📊 Analytics    │            │Content Area                    │
│ ⏰ Scheduler     │            │                                │
│ 📜 History      │            │LOGIN FORM (in Settings Tab):   │
│ ⚙️ Settings ◄───┼────────────┤                                │
└─────────────────┘            │ Email: [________]              │
                               │ Password: [________]           │
                               │ [Login] [Register]             │
                               └────────────────────────────────┘
```

---

## Quick Test

1. Open http://127.0.0.1:5000
2. Click ⚙️ Settings in the navigation
3. You'll see the login form
4. Register with: 
   - Email: `test@example.com`
   - Password: `Test123!`
5. Click Login
6. Now go to 📊 Analytics tab
7. You should see your threat data!

---

**Login is Ready!** Start by clicking the ⚙️ Settings tab.
