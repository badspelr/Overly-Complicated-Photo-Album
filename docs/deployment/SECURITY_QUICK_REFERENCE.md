# 🔒 Production Security Quick Reference

## ⚠️ STOP! Read This Before Deploying

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   🚨 CRITICAL: 4 SETTINGS REQUIRED FOR PRODUCTION 🚨            │
│                                                                 │
│   Without these, your deployment is INSECURE                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## The 4 Critical Settings

| Setting | Development | Production | Risk Level |
|---------|-------------|------------|------------|
| `DEBUG` | ✅ `True` | ❌ **`False`** | 🔴 CRITICAL |
| `SECURE_SSL_REDIRECT` | ✅ `False` | ❌ **`True`** | 🔴 CRITICAL |
| `SESSION_COOKIE_SECURE` | ✅ `False` | ❌ **`True`** | 🔴 CRITICAL |
| `CSRF_COOKIE_SECURE` | ✅ `False` | ❌ **`True`** | 🔴 CRITICAL |

---

## Copy-Paste for Production (.env file)

```bash
# CRITICAL PRODUCTION SETTINGS
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## Verification Command

```bash
docker-compose exec web python -c "
from django.conf import settings
print('✅ PASS' if not settings.DEBUG else '❌ FAIL: DEBUG is True')
print('✅ PASS' if settings.SECURE_SSL_REDIRECT else '❌ FAIL: SSL redirect disabled')
print('✅ PASS' if settings.SESSION_COOKIE_SECURE else '❌ FAIL: Session cookies insecure')
print('✅ PASS' if settings.CSRF_COOKIE_SECURE else '❌ FAIL: CSRF cookies insecure')
"
```

**Expected Output:**
```
✅ PASS
✅ PASS
✅ PASS
✅ PASS
```

---

## What Each Setting Does

### `DEBUG=False`
- ❌ **If True:** Exposes secrets, stack traces, and internal code
- ✅ **If False:** Shows generic error pages, keeps secrets hidden

### `SECURE_SSL_REDIRECT=True`
- ❌ **If False:** Traffic can be intercepted (man-in-the-middle)
- ✅ **If True:** All traffic forced to HTTPS (encrypted)
- ⚠️ **Requires:** HTTPS configured via Nginx/Apache

### `SESSION_COOKIE_SECURE=True`
- ❌ **If False:** Session cookies sent over HTTP (can be stolen)
- ✅ **If True:** Session cookies only sent over HTTPS (encrypted)
- ⚠️ **Requires:** HTTPS configured

### `CSRF_COOKIE_SECURE=True`
- ❌ **If False:** CSRF tokens sent over HTTP (can be stolen)
- ✅ **If True:** CSRF tokens only sent over HTTPS (encrypted)
- ⚠️ **Requires:** HTTPS configured

---

## Pre-Deployment Checklist

```
□ Copy .env.production to .env
□ Set DEBUG=False
□ Set SECURE_SSL_REDIRECT=True
□ Set SESSION_COOKIE_SECURE=True
□ Set CSRF_COOKIE_SECURE=True
□ Generate new SECRET_KEY
□ Update ALLOWED_HOSTS with your domain
□ Configure HTTPS (SSL certificate)
□ Use PostgreSQL (not SQLite)
□ Run: python manage.py check --deploy
□ Test all 4 settings with verification command
```

---

## Common Mistakes

| ❌ Mistake | ✅ Correct |
|-----------|-----------|
| `DEBUG=True` in production | `DEBUG=False` |
| No HTTPS/SSL | Configure HTTPS first |
| Using SQLite | Use PostgreSQL |
| Weak SECRET_KEY | Generate strong random key |
| `ALLOWED_HOSTS=['*']` | List specific domains |
| Committing .env to git | Keep .env in .gitignore |

---

## If You Get Errors

### "Site can't be reached"
**Cause:** Set `SECURE_SSL_REDIRECT=True` without HTTPS  
**Fix:** Configure HTTPS first, then enable redirect

### "Login doesn't work"
**Cause:** Secure cookies enabled but using HTTP  
**Fix:** Use `https://yourdomain.com` (not `http://`)

### "CSRF verification failed"
**Cause:** Cookie settings don't match protocol  
**Fix:** Ensure HTTPS is working, check ALLOWED_HOSTS

---

## Quick Test Commands

### Check Django Security
```bash
docker-compose exec web python manage.py check --deploy
```

### Check Environment Variables
```bash
docker-compose exec web python manage.py shell -c "
import os; 
print('DEBUG =', os.getenv('DEBUG'));
print('SECURE_SSL_REDIRECT =', os.getenv('SECURE_SSL_REDIRECT'))
"
```

### Check Security Headers
```bash
curl -I https://yourdomain.com
```

Look for:
- `strict-transport-security: max-age=31536000`
- `x-frame-options: DENY`
- `x-content-type-options: nosniff`

---

## Development vs Production

### 🟢 Development (Local)
```bash
DEBUG=True                    # Shows errors for debugging
SECURE_SSL_REDIRECT=False     # No HTTPS on localhost
SESSION_COOKIE_SECURE=False   # Works without HTTPS
CSRF_COOKIE_SECURE=False      # Works without HTTPS
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 🔴 Production (Server)
```bash
DEBUG=False                   # Hides sensitive info
SECURE_SSL_REDIRECT=True      # Forces HTTPS
SESSION_COOKIE_SECURE=True    # Requires HTTPS
CSRF_COOKIE_SECURE=True       # Requires HTTPS
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

---

## Security Scoring

Rate your deployment:

| Score | Status | Action |
|-------|--------|--------|
| 100 | 🟢 Perfect | Deploy |
| 90-99 | 🟢 Excellent | Deploy |
| 70-89 | 🟡 Good | Fix issues first |
| 50-69 | 🟠 Risky | Do NOT deploy |
| <50 | 🔴 Insecure | Do NOT deploy |

**Score 20 points for each:**
1. DEBUG=False
2. SECURE_SSL_REDIRECT=True
3. SESSION_COOKIE_SECURE=True
4. CSRF_COOKIE_SECURE=True
5. Strong SECRET_KEY

---

## Need Help?

📖 **Full Documentation:**  
`docs/deployment/PRODUCTION_SECURITY_CHECKLIST.md`

📧 **Support:**  
GitHub Issues: https://github.com/badspelr/Overly-Complicated-Photo-Album/issues

---

## Remember

```
┌───────────────────────────────────────────────────────┐
│                                                       │
│  If you see ANY ❌ FAIL in verification:             │
│                                                       │
│       DO NOT DEPLOY TO PRODUCTION                     │
│                                                       │
│  Fix the issues first, then verify again.             │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

**Version:** 1.3.0  
**Last Updated:** October 24, 2025  
**Status:** Production Security Reference

---

## Print This Card

Print this document and keep it visible during deployment:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                    ┃
┃  PRODUCTION DEPLOYMENT CHECKLIST                   ┃
┃                                                    ┃
┃  □ DEBUG=False                                     ┃
┃  □ SECURE_SSL_REDIRECT=True                        ┃
┃  □ SESSION_COOKIE_SECURE=True                      ┃
┃  □ CSRF_COOKIE_SECURE=True                         ┃
┃  □ HTTPS Configured                                ┃
┃  □ Strong SECRET_KEY                               ┃
┃  □ ALLOWED_HOSTS Set                               ┃
┃  □ Using PostgreSQL                                ┃
┃  □ All Tests Pass                                  ┃
┃  □ Verification Command Returns All ✅             ┃
┃                                                    ┃
┃  Ready to deploy: □ YES  □ NO                      ┃
┃                                                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```
