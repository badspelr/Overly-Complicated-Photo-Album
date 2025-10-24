# First Time Setup Guide

## 🎯 Overview

This guide walks you through the essential first-time setup steps after deploying the Django Photo Album application. Follow these steps in order to ensure a secure and properly configured installation.

## ⏱️ Time Required

- **Minimum:** 10-15 minutes
- **Complete setup with SSL:** 30-45 minutes

---

## 📋 Pre-Deployment Checklist

Before starting the application, ensure you have:

- [ ] Cloned the repository
- [ ] Copied `.env.example` to `.env`
- [ ] Configured all required environment variables (see below)
- [ ] Docker and Docker Compose installed (if using Docker)
- [ ] PostgreSQL and Redis installed (if running without Docker)

---

## 🔧 Step 1: Configure Environment Variables

Edit your `.env` file with proper production values:

### Required Settings

```bash
# 1. Generate a unique secret key
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# 2. Set production mode
DEBUG=False

# 3. Configure your domain
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# 4. Database settings
DB_NAME=photo_album_db
DB_USER=photo_album_user
DB_PASSWORD=$(openssl rand -base64 32)  # Generate strong password
DB_HOST=db
DB_PORT=5432

# 5. CORS settings (your frontend domains)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_ALLOW_ALL_ORIGINS=False

# 6. Redis
REDIS_URL=redis://redis:6379/0
```

### Security Critical Variables

**⚠️ NEVER use these example values in production:**

- `SECRET_KEY` - Must be unique and secret
- `DB_PASSWORD` - Strong random password
- `ALLOWED_HOSTS` - Only your actual domains
- `CORS_ALLOWED_ORIGINS` - Only trusted domains

---

## 🚀 Step 2: Start the Application

### Using Docker (Recommended)

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check all services are running
docker-compose ps

# Expected output:
# NAME                STATUS
# photo_album-web-1         running
# photo_album-db-1          running
# photo_album-redis-1       running
# photo_album-celery-worker-1  running
# photo_album-celery-beat-1    running
```

### Using Systemd (Traditional)

See [Deployment Systemd Guide](../deployment/DEPLOYMENT_SYSTEMD.md)

---

## 🗄️ Step 3: Initialize Database

Run Django migrations to create database tables:

```bash
# Docker
docker-compose exec web python manage.py migrate

# Non-Docker
python manage.py migrate
```

**Expected output:**
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying album.0001_initial... OK
  ...
```

---

## 👤 Step 4: Create Admin Account

**⚠️ CRITICAL: There is NO default admin account. You must create one.**

```bash
# Docker
docker-compose exec web python manage.py createsuperuser

# Non-Docker
python manage.py createsuperuser
```

**Interactive prompts:**
```
Username: admin
Email address: admin@yourdomain.com
Password: ****************
Password (again): ****************
Superuser created successfully.
```

**Password Requirements:**
- ✅ At least 8 characters
- ✅ Not entirely numeric
- ✅ Not too similar to other personal information
- ✅ Not a commonly used password

**Recommended:** Use a password manager to generate a strong password (20+ characters).

---

## 📁 Step 5: Collect Static Files

Gather all static files (CSS, JS, images) into one directory:

```bash
# Docker
docker-compose exec web python manage.py collectstatic --noinput

# Non-Docker
python manage.py collectstatic --noinput
```

---

## ⚙️ Step 6: Configure Initial Settings

### 6.1 Access Admin Panel

1. Visit `https://yourdomain.com/admin/` (or `http://localhost:8000/admin/` for local testing)
2. Login with the superuser account you created

### 6.2 Site Settings

Navigate to: **Admin Panel → Site Settings**

Configure:
- **Site Name:** Your Photo Album Name
- **Allow Registration:** Check if you want users to register, uncheck for invitation-only
- **Default Album Privacy:** Public or Private

### 6.3 AI Processing Settings

Navigate to: **Admin Panel → AI Processing Settings**

Configure based on your server capabilities:

**For servers WITH GPU:**
```
Enable AI Processing: ✅ Checked
Batch Processing: ✅ Checked
Batch Size: 32
Max Concurrent Tasks: 4
Use GPU: ✅ Checked
```

**For servers WITHOUT GPU (CPU only):**
```
Enable AI Processing: ✅ Checked
Batch Processing: ✅ Checked
Batch Size: 8
Max Concurrent Tasks: 2
Use GPU: ⬜ Unchecked
```

**For low-resource servers:**
```
Enable AI Processing: ⬜ Unchecked
(Users can still use the app, just without AI features)
```

See [AI Settings Guide](../admin-guides/ADMIN_GUIDE_AI_SETTINGS.md) for details.

---

## 🔒 Step 7: Security Verification

Run through this security checklist:

### 7.1 Environment Check

```bash
# Docker
docker-compose exec web python manage.py check --deploy

# Non-Docker
python manage.py check --deploy
```

**Expected:** No critical warnings (some warnings about SSL are OK if behind reverse proxy)

### 7.2 Verify Settings

```bash
# Test that DEBUG is False
docker-compose exec web python -c "from photo_album.settings import DEBUG; print(f'DEBUG={DEBUG}')"
# Should output: DEBUG=False

# Check ALLOWED_HOSTS
docker-compose exec web python -c "from photo_album.settings import ALLOWED_HOSTS; print(f'ALLOWED_HOSTS={ALLOWED_HOSTS}')"
# Should show your domain, not ['*']

# Check SECRET_KEY is unique
docker-compose exec web python -c "from photo_album.settings import SECRET_KEY; print(f'Unique: {SECRET_KEY != \"django-insecure-example-key\"}')"
# Should output: Unique: True
```

### 7.3 Test Login

1. Visit admin panel
2. Verify you can login with your superuser account
3. Try accessing without login - should redirect to login page
4. Verify registration page (if enabled) works correctly

---

## 🌐 Step 8: Setup Reverse Proxy (Production)

### Option A: Nginx (Recommended)

Follow the comprehensive [Nginx Setup Guide](../deployment/NGINX_SETUP.md)

**Quick start:**
```bash
# Use our automated script
cd scripts
sudo bash setup_nginx.sh
```

This will:
- Install Nginx
- Configure reverse proxy
- Set up SSL with Let's Encrypt
- Configure security headers

### Option B: Apache

See [Apache Setup Guide](../deployment/APACHE_SETUP.md) (if available)

---

## ✅ Step 9: Verification Tests

### 9.1 Service Health Check

```bash
# Check all Docker containers are healthy
docker-compose ps

# Check web application responds
curl -I https://yourdomain.com
# Should return: HTTP/2 200

# Check admin panel
curl -I https://yourdomain.com/admin/
# Should return: HTTP/2 200 or 302 (redirect to login)

# Check Redis connection
docker-compose exec web python -c "from django.core.cache import cache; cache.set('test', 'ok'); print(cache.get('test'))"
# Should output: ok

# Check Celery workers
docker-compose exec web python manage.py celery inspect active
# Should show worker is online
```

### 9.2 Upload Test

1. Login to web interface
2. Create a test album
3. Upload a test photo
4. Verify photo displays correctly
5. If AI enabled, wait 1-2 minutes and verify AI description appears

### 9.3 Search Test

1. Upload several photos with different subjects
2. Wait for AI processing to complete
3. Try semantic search: "sunset" or "people" or "car"
4. Verify results are relevant

---

## 📊 Step 10: Monitoring Setup (Optional)

### 10.1 Enable Logging

Logs are written to `/app/logs/` (or `logs/` in your project root)

```bash
# View application logs
docker-compose logs -f web

# View Celery worker logs
docker-compose logs -f celery-worker

# View error logs
tail -f logs/error.log
```

### 10.2 Setup Log Rotation

Create `/etc/logrotate.d/photo_album`:

```
/path/to/photo_album/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

### 10.3 Monitoring Tools (Optional)

Consider setting up:
- **Prometheus + Grafana** - Metrics and dashboards
- **Sentry** - Error tracking
- **Uptime Robot** - Availability monitoring

---

## 🎉 Congratulations!

Your Photo Album is now fully set up and secured. 

### Next Steps

- [ ] Read the [User Manual](../user-guides/USER_MANUAL.md)
- [ ] Invite users or enable registration
- [ ] Configure backup strategy ([Backup Guide](../deployment/BACKUP_RESTORE.md))
- [ ] Set up monitoring and alerts
- [ ] Review [Best Practices](../admin-guides/BEST_PRACTICES.md)

### Quick Reference

| Task | Command |
|------|---------|
| Start services | `docker-compose up -d` |
| Stop services | `docker-compose down` |
| View logs | `docker-compose logs -f web` |
| Run migrations | `docker-compose exec web python manage.py migrate` |
| Create user | `docker-compose exec web python manage.py createsuperuser` |
| Restart web | `docker-compose restart web` |
| Restart Celery | `docker-compose restart celery-worker celery-beat` |
| Shell access | `docker-compose exec web bash` |
| Django shell | `docker-compose exec web python manage.py shell` |

---

## 🆘 Troubleshooting

### Services won't start

```bash
# Check Docker status
docker-compose ps

# Check logs for errors
docker-compose logs

# Try rebuilding
docker-compose down
docker-compose up -d --build
```

### Can't login to admin

```bash
# Reset admin password
docker-compose exec web python manage.py changepassword admin
```

### Photos not uploading

```bash
# Check media directory permissions
docker-compose exec web ls -la /app/media/

# Check Celery worker is running
docker-compose ps celery-worker

# Check Celery logs
docker-compose logs celery-worker
```

### AI processing not working

```bash
# Check AI settings in admin panel
# Verify Celery worker has access to models

# Check model downloads
docker-compose exec web ls -la /root/.cache/

# Restart Celery workers
docker-compose restart celery-worker celery-beat
```

### SSL/HTTPS issues

```bash
# Check Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Check Let's Encrypt renewal
sudo certbot renew --dry-run
```

---

## 📞 Getting Help

- **Documentation:** [Main docs](../README.md)
- **Admin Guides:** [Admin guides](../admin-guides/)
- **GitHub Issues:** [Report issues](https://github.com/badspelr/Overly-Complicated-Photo-Album/issues)

---

**Setup Time:** ~15-45 minutes  
**Difficulty:** Beginner to Intermediate  
**Last Updated:** October 24, 2025
