# 📋 DEPLOYMENT CHECKLIST & PRODUCTION GUIDE

## ✅ Pre-Deployment Checklist

### Code Quality
- [ ] All files have docstrings
- [ ] Type hints used throughout
- [ ] No hardcoded credentials
- [ ] Logging implemented for key operations
- [ ] Error handling for all edge cases
- [ ] No print() statements (use logging)
- [ ] Code follows PEP 8 style guide
- [ ] No deprecated functions used

### Security
- [ ] SECRET_KEY set via environment variable
- [ ] All inputs validated
- [ ] SQL queries parameterized
- [ ] CORS origins configured
- [ ] Session cookies are HttpOnly/Secure
- [ ] No sensitive data in logs
- [ ] Password requirements documented
- [ ] HTTPS enforced in production

### Database
- [ ] Schema optimized with indexes
- [ ] Backups configured
- [ ] Migrations documented
- [ ] Connection pooling enabled
- [ ] Query performance tested
- [ ] Data retention policy defined

### Testing
- [ ] Health endpoint tested
- [ ] All API endpoints tested
- [ ] Error responses validated
- [ ] Input validation tested
- [ ] Rate limiting tested (if enabled)
- [ ] Database operations tested

### Documentation
- [ ] API documentation complete
- [ ] Configuration documented
- [ ] Deployment guide written
- [ ] Troubleshooting guide included
- [ ] Architecture diagrams present
- [ ] Code comments clear and helpful

---

## 🚀 Deployment Steps

### 1. Prepare Server (Ubuntu/Linux)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Install system dependencies
sudo apt install build-essential -y
```

### 2. Clone Application
```bash
cd /var/www
git clone <your-repo> email-scanner
cd email-scanner

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Create .env file
nano .env

# Add production settings:
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=<generate-strong-secret-key>
DB_PATH=/var/www/email-scanner/data/scan_history.db
CORS_ORIGINS=https://yourdomain.com
```

### 4. Create Data Directory
```bash
mkdir -p /var/www/email-scanner/data
chmod 755 /var/www/email-scanner/data
```

### 5. Install Gunicorn (Production Server)
```bash
pip install gunicorn
```

### 6. Create Systemd Service
```bash
sudo nano /etc/systemd/system/email-scanner.service
```

Add:
```ini
[Unit]
Description=Email Scanner API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/email-scanner
Environment="PATH=/var/www/email-scanner/venv/bin"
ExecStart=/var/www/email-scanner/venv/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:5000 \
    --timeout 60 \
    "app:create_app()"

[Install]
WantedBy=multi-user.target
```

### 7. Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable email-scanner
sudo systemctl start email-scanner
sudo systemctl status email-scanner
```

### 8. Configure Nginx (Reverse Proxy)
```bash
sudo nano /etc/nginx/sites-available/email-scanner
```

Add:
```nginx
upstream email_scanner {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    location / {
        proxy_pass http://email_scanner;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 9. Enable Nginx Site
```bash
sudo ln -s /etc/nginx/sites-available/email-scanner \
    /etc/nginx/sites-enabled/

sudo nginx -t
sudo systemctl restart nginx
```

### 10. SSL Certificate (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx -y

sudo certbot certonly --nginx -d yourdomain.com
```

---

## 📊 Monitoring & Maintenance

### View Logs
```bash
# Application logs
sudo journalctl -u email-scanner -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# App logs
tail -f /var/www/email-scanner/app.log
```

### Monitor Resources
```bash
# Check process
ps aux | grep gunicorn

# Check port
sudo netstat -tlnp | grep 5000

# Check disk space
df -h /var/www/email-scanner/data

# Check memory
free -h
```

### Restart Service
```bash
sudo systemctl restart email-scanner

# Reload without dropping connections
sudo systemctl reload email-scanner
```

### Update Application
```bash
cd /var/www/email-scanner

# Pull latest code
git pull origin main

# Activate venv
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart email-scanner
```

---

## 🔒 Security Hardening

### File Permissions
```bash
# Set correct permissions
sudo chown -R www-data:www-data /var/www/email-scanner
sudo chmod 755 /var/www/email-scanner
sudo chmod 755 /var/www/email-scanner/data
sudo chmod 600 /var/www/email-scanner/.env
```

### Firewall
```bash
# UFW firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Fail2Ban (Prevent brute force)
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Database Backup
```bash
# Create backup script
cat > /var/www/email-scanner/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/email-scanner"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp /var/www/email-scanner/data/scan_history.db \
   $BACKUP_DIR/scan_history_$DATE.db

# Keep only last 30 backups
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
EOF

chmod +x /var/www/email-scanner/backup.sh

# Add to crontab
sudo crontab -e
# Add: 0 2 * * * /var/www/email-scanner/backup.sh
```

---

## 📈 Performance Tuning

### Gunicorn Workers
```bash
# Calculate workers = (2 × CPU cores) + 1
# For 4 cores: 9 workers
# For 2 cores: 5 workers

# Edit service file:
--workers 9
```

### Database Connection Pool
```bash
# In production config
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

### Caching
```bash
# Install Redis
sudo apt install redis-server -y

# Configure in app
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379/0'
```

---

## 🎯 Health Checks

### Endpoint Monitoring
```bash
# Test health endpoint
curl https://yourdomain.com/health

# Monitor response time
while true; do
  curl -w "@curl-format.txt" -o /dev/null -s https://yourdomain.com/health
  sleep 5
done
```

### Uptime Monitoring Services
- ✅ Uptime Robot (free)
- ✅ Pingdom
- ✅ StatusCake
- ✅ Monitoring.net

---

## 🐛 Troubleshooting Production

### Application Won't Start
```bash
# Check logs
sudo journalctl -u email-scanner -n 50

# Check configuration
cat /var/www/email-scanner/.env

# Test manually
cd /var/www/email-scanner
source venv/bin/activate
python run.py
```

### High Memory Usage
```bash
# Check memory
ps aux | grep gunicorn

# Reduce workers
# Edit service and restart
sudo systemctl restart email-scanner
```

### Database Locked
```bash
# Check if process is running
lsof /var/www/email-scanner/data/scan_history.db

# Kill stuck process if necessary
kill -9 <PID>

# Restart service
sudo systemctl restart email-scanner
```

### SSL Certificate Issues
```bash
# Renew certificate
sudo certbot renew --dry-run

# Check expiration
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal
```

---

## 📊 Production Metrics

Track these metrics:
- ✅ Request latency (target: <500ms)
- ✅ Error rate (target: <1%)
- ✅ Uptime (target: >99.5%)
- ✅ Database size
- ✅ CPU usage (target: <70%)
- ✅ Memory usage (target: <500MB)
- ✅ Disk space (alert: <10% free)

---

## 🚨 Incident Response

### Service Down
1. Check status: `sudo systemctl status email-scanner`
2. Check logs: `sudo journalctl -u email-scanner -n 100`
3. Restart: `sudo systemctl restart email-scanner`
4. Verify: `curl https://yourdomain.com/health`

### High Error Rate
1. Check application logs
2. Check database connectivity
3. Review recent changes
4. Rollback if necessary

### Performance Degradation
1. Check resource usage
2. Check database performance
3. Review slow queries
4. Scale horizontally if needed

---

## 📝 Deployment Runbook Template

```
Date: [YYYY-MM-DD]
Version: [VERSION]
Changes: [LIST CHANGES]
Rollback Plan: [ROLLBACK STEPS]

Pre-Deployment:
- [ ] Code reviewed
- [ ] Tests passed
- [ ] Security scan complete

Deployment:
- [ ] Pull latest code
- [ ] Update dependencies
- [ ] Run migrations
- [ ] Restart service

Post-Deployment:
- [ ] Health check passing
- [ ] No error logs
- [ ] Response time normal
- [ ] Database backups current

Issues Encountered: [IF ANY]
```

---

**Your application is now ready for production! 🚀**
