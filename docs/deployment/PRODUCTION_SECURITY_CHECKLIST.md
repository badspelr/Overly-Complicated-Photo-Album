# Production Security Checklist

## ⚠️ CRITICAL: Before Deploying to Production

This checklist ensures your Django Photo Album deployment is secure and production-ready.

---

## 🔒 Security Settings (REQUIRED)

### 1. Environment Variables

**Location:** `.env` file (or environment configuration)

#### ✅ MUST BE SET TO THESE VALUES IN PRODUCTION:

```bash
# CRITICAL: Disable debug mode
DEBUG=False

# CRITICAL: Enable SSL/HTTPS security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

#### ⚠️ Development vs Production Settings

| Setting | Development | Production | Why? |
|---------|-------------|------------|------|
| `DEBUG` | `True` | `False` | Debug mode exposes sensitive info (stack traces, settings) |
| `SECURE_SSL_REDIRECT` | `False` | `True` | Forces HTTPS for all requests |
| `SESSION_COOKIE_SECURE` | `False` | `True` | Session cookies only sent over HTTPS |
| `CSRF_COOKIE_SECURE` | `False` | `True` | CSRF tokens only sent over HTTPS |

---

## 📋 Pre-Deployment Checklist

### ☑️ Step 1: Environment Configuration

- [ ] Copy `.env.production` to `.env`:
  ```bash
  cp .env.production .env
  ```

- [ ] Generate a NEW `SECRET_KEY`:
  ```bash
  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
  ```

- [ ] Update `ALLOWED_HOSTS` with your domain(s):
  ```bash
  ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
  ```

- [ ] Set strong database credentials:
  ```bash
  DB_USER=your_production_user
  DB_PASSWORD=<generate-strong-password>
  ```

- [ ] Configure email settings (required for notifications):
  ```bash
  EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
  EMAIL_HOST=smtp.yourprovider.com
  EMAIL_HOST_USER=your-smtp-username
  EMAIL_HOST_PASSWORD=your-smtp-password
  ```

- [ ] Verify security settings are enabled:
  ```bash
  DEBUG=False
  SECURE_SSL_REDIRECT=True
  SESSION_COOKIE_SECURE=True
  CSRF_COOKIE_SECURE=True
  ```

### ☑️ Step 2: SSL/HTTPS Setup

- [ ] Obtain SSL certificate (Let's Encrypt recommended)
- [ ] Configure Nginx/Apache reverse proxy for HTTPS
- [ ] Test HTTPS is working: `https://yourdomain.com`
- [ ] Verify HTTP redirects to HTTPS automatically

**Important:** The security settings above (`SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`) **ONLY work if HTTPS is properly configured**. Without HTTPS, they will break your application.

### ☑️ Step 3: Database Security

- [ ] Use PostgreSQL (not SQLite) in production
- [ ] Change default PostgreSQL password
- [ ] Restrict database access to application server only
- [ ] Enable database backups
- [ ] Test database connection

### ☑️ Step 4: File Permissions

- [ ] Set proper file permissions:
  ```bash
  chmod 600 .env
  chmod 755 media/
  chmod 755 static_root/
  ```

- [ ] Ensure `.env` is not readable by web server
- [ ] Verify media files are served securely

### ☑️ Step 5: Security Headers

- [ ] Verify these are set in `settings.py` (already configured):
  ```python
  SECURE_HSTS_SECONDS = 31536000  # 1 year
  SECURE_HSTS_INCLUDE_SUBDOMAINS = True
  SECURE_HSTS_PRELOAD = True
  SECURE_CONTENT_TYPE_NOSNIFF = True
  SECURE_BROWSER_XSS_FILTER = True
  X_FRAME_OPTIONS = 'DENY'
  ```

### ☑️ Step 6: CORS Configuration

- [ ] Update `CORS_ALLOWED_ORIGINS` with your frontend domain(s):
  ```bash
  CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
  ```

- [ ] Do NOT use `CORS_ALLOW_ALL_ORIGINS=True` in production

### ☑️ Step 7: Static Files

- [ ] Run `python manage.py collectstatic`
- [ ] Configure Nginx/Apache to serve static files
- [ ] Verify static files load: `https://yourdomain.com/static/`

### ☑️ Step 8: Admin Account

- [ ] Create superuser with strong password:
  ```bash
  docker-compose exec web python manage.py createsuperuser
  ```

- [ ] Use complex password (20+ characters)
- [ ] Enable 2FA (if configured)
- [ ] Do NOT use "admin" as username

### ☑️ Step 9: AI Services (Optional)

- [ ] Configure AI processing settings in admin
- [ ] Test CLIP/BLIP models are loading
- [ ] Verify GPU access (if using CUDA)
- [ ] Monitor resource usage

### ☑️ Step 10: Monitoring & Logging

- [ ] Configure logging to file (not console)
- [ ] Set up error monitoring (Sentry recommended)
- [ ] Configure health check endpoint
- [ ] Test error notifications

---

## 🧪 Security Testing

### Run Django Security Check

```bash
docker-compose exec web python manage.py check --deploy
```

**Expected output:** No warnings or errors.

### Test HTTPS Redirect

```bash
# Should redirect to HTTPS
curl -I http://yourdomain.com

# Should return 200 OK
curl -I https://yourdomain.com
```

### Test Security Headers

```bash
curl -I https://yourdomain.com | grep -E "Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options"
```

**Expected headers:**
```
strict-transport-security: max-age=31536000; includeSubDomains; preload
x-frame-options: DENY
x-content-type-options: nosniff
```

### Verify Cookie Security

Open browser DevTools → Application → Cookies:

- [ ] Session cookie has `Secure` flag
- [ ] CSRF cookie has `Secure` flag
- [ ] Both cookies have `SameSite=Lax` or `Strict`

---

## 🚨 Common Production Mistakes

### ❌ DO NOT:

1. **Leave `DEBUG=True` in production**
   - Exposes sensitive information
   - Shows full stack traces to users
   - Displays settings and environment variables

2. **Use weak `SECRET_KEY`**
   - Never use the default key
   - Must be random and complex
   - Never commit to git

3. **Skip HTTPS setup**
   - Without HTTPS, cookies are sent in plain text
   - Man-in-the-middle attacks possible
   - Google penalizes non-HTTPS sites

4. **Use SQLite in production**
   - Not designed for concurrent writes
   - No backup/replication features
   - Performance issues

5. **Set `ALLOWED_HOSTS=['*']`**
   - Opens security vulnerabilities
   - Must list specific domains

6. **Use `CORS_ALLOW_ALL_ORIGINS=True`**
   - Allows any website to access your API
   - Major security risk

7. **Commit `.env` file to git**
   - Exposes all secrets publicly
   - Keep `.env` in `.gitignore`

---

## 📊 Security Scoring Guide

Rate your deployment:

| Category | Points | Your Score |
|----------|--------|------------|
| DEBUG=False | 20 | __ / 20 |
| HTTPS Enabled | 20 | __ / 20 |
| Secure Cookies (all 3) | 15 | __ / 15 |
| Strong SECRET_KEY | 10 | __ / 10 |
| Database Security | 10 | __ / 10 |
| CORS Configured | 10 | __ / 10 |
| File Permissions | 5 | __ / 5 |
| Static Files Served | 5 | __ / 5 |
| Strong Admin Password | 5 | __ / 5 |
| **TOTAL** | **100** | __ / 100 |

### Scoring:
- **90-100:** ✅ Production Ready
- **70-89:** ⚠️ Needs Improvement
- **Below 70:** ❌ NOT Production Ready

---

## 🔐 Environment File Examples

### Development (`.env`)
```bash
DEBUG=True
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Production (`.env`)
```bash
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourprovider.com
```

---

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [Let's Encrypt (Free SSL)](https://letsencrypt.org/)
- [Security Headers Test](https://securityheaders.com/)

---

## 🆘 Troubleshooting

### "Site can't be reached" after setting SECURE_SSL_REDIRECT=True

**Cause:** HTTPS not configured.

**Solution:**
1. Set up SSL certificate first
2. Configure Nginx/Apache for HTTPS
3. Then enable `SECURE_SSL_REDIRECT=True`

### Login doesn't work after enabling secure cookies

**Cause:** Accessing site via HTTP instead of HTTPS.

**Solution:** Use `https://yourdomain.com` (not `http://`)

### CSRF verification failed

**Cause:** Cookie security mismatch or wrong domain.

**Solution:**
1. Ensure HTTPS is working
2. Check `ALLOWED_HOSTS` includes your domain
3. Verify `CSRF_TRUSTED_ORIGINS` if using different domains

---

## ✅ Final Verification

Before going live, run this complete check:

```bash
# 1. Security check
docker-compose exec web python manage.py check --deploy

# 2. Run tests
docker-compose exec web pytest

# 3. Check environment
docker-compose exec web python -c "
import os
from django.conf import settings
print('DEBUG:', settings.DEBUG)
print('SECURE_SSL_REDIRECT:', settings.SECURE_SSL_REDIRECT)
print('SESSION_COOKIE_SECURE:', settings.SESSION_COOKIE_SECURE)
print('CSRF_COOKIE_SECURE:', settings.CSRF_COOKIE_SECURE)
print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)
"

# Expected output:
# DEBUG: False
# SECURE_SSL_REDIRECT: True
# SESSION_COOKIE_SECURE: True
# CSRF_COOKIE_SECURE: True
# ALLOWED_HOSTS: ['yourdomain.com', 'www.yourdomain.com']
```

---

**Version:** 1.3.0  
**Last Updated:** October 24, 2025  
**Status:** Production Security Guide

---

## 🎯 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│  PRODUCTION SECURITY ESSENTIALS                     │
├─────────────────────────────────────────────────────┤
│  DEBUG=False                          ✅ REQUIRED   │
│  SECURE_SSL_REDIRECT=True             ✅ REQUIRED   │
│  SESSION_COOKIE_SECURE=True           ✅ REQUIRED   │
│  CSRF_COOKIE_SECURE=True              ✅ REQUIRED   │
│  Strong SECRET_KEY                    ✅ REQUIRED   │
│  HTTPS Configured                     ✅ REQUIRED   │
│  ALLOWED_HOSTS=your-domain.com        ✅ REQUIRED   │
│  PostgreSQL (not SQLite)              ✅ REQUIRED   │
├─────────────────────────────────────────────────────┤
│  Without these: NOT PRODUCTION READY ❌             │
└─────────────────────────────────────────────────────┘
```
