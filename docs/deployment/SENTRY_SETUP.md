# Sentry Setup Guide

## What is Sentry?

Sentry is an error tracking and performance monitoring platform that helps you monitor and fix crashes in real-time. When your application encounters an error, Sentry captures:
- Full stack trace with exact line numbers
- User context (who experienced the error)
- Request data and environment info
- Frequency and impact analysis
- Breadcrumbs (what led to the error)

## Quick Start

### 1. Sign Up for Sentry (Free Tier)

1. Go to https://sentry.io/signup/
2. Sign up for a free account (5,000 errors/month)
3. Create a new project
4. Select **Django** as your platform
5. Copy your DSN (Data Source Name) - looks like:
   ```
   https://examplePublicKey@o0.ingest.sentry.io/0
   ```

### 2. Add DSN to Environment Configuration

Open your `.env` file and add:

```bash
# Sentry Configuration
SENTRY_DSN=https://your-actual-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
```

**Important:** 
- Replace `https://your-actual-dsn@sentry.io/project-id` with your actual DSN from step 1
- Use `production` for production, `development` for dev environments
- Sample rates (0.1 = 10%) control performance monitoring overhead

### 3. Rebuild Docker Container

Since we added `sentry-sdk` to `requirements.txt`, rebuild the container:

```bash
docker-compose build web
docker-compose up -d
```

This installs the Sentry SDK and restarts your application.

### 4. Verify Sentry is Active

Check your application logs:

```bash
docker-compose logs web | grep -i sentry
```

You should see a log entry indicating Sentry initialization (only when DEBUG=False).

## Configuration Details

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SENTRY_DSN` | Your project's DSN from sentry.io | `https://abc123@sentry.io/123456` |
| `SENTRY_ENVIRONMENT` | Environment name for filtering | `production`, `staging`, `development` |
| `SENTRY_TRACES_SAMPLE_RATE` | % of transactions to monitor (0.0-1.0) | `0.1` (10%) |
| `SENTRY_PROFILES_SAMPLE_RATE` | % of transactions to profile (0.0-1.0) | `0.1` (10%) |

### What Gets Monitored?

**Automatic:**
- Django view errors (500 errors)
- Celery task failures
- Redis connection issues
- Unhandled exceptions
- Database errors

**Privacy Protected:**
- Passwords are automatically scrubbed
- PII (Personally Identifiable Information) is not sent
- Sensitive headers are filtered

### Sample Rates

Sample rates control how much data is sent to Sentry:

- `0.0` = Disabled (no performance monitoring)
- `0.1` = 10% of requests (recommended for production)
- `1.0` = 100% of requests (use cautiously, may exceed quota)

**Free Tier Limits:**
- 5,000 errors per month
- Performance monitoring data separate from error quota

## Testing Sentry Integration

### Option 1: Trigger a Test Error (Safe)

Create a temporary view to test Sentry:

```python
# In album/views.py (temporary, remove after testing)
def sentry_test(request):
    division_by_zero = 1 / 0
```

Add to `album/urls.py`:
```python
path('sentry-test/', views.sentry_test, name='sentry_test'),
```

Visit: `http://yourdomain.com/sentry-test/`

### Option 2: Use Sentry CLI Test Command

```bash
docker-compose exec web python manage.py shell
>>> import sentry_sdk
>>> sentry_sdk.capture_message("Test message from Django")
```

### Option 3: Check Sentry Dashboard

1. Log in to https://sentry.io
2. Go to your project
3. Navigate to **Issues** tab
4. You should see test errors appear within seconds

## How to Use Sentry

### 1. Monitor Real-Time Errors

When an error occurs:
1. **Email Alert:** You'll receive an email immediately
2. **Dashboard:** View error in Sentry dashboard
3. **Stack Trace:** See exact file and line number
4. **User Context:** See which user experienced the error
5. **Request Data:** View request headers, parameters, etc.

### 2. Analyze Error Trends

- **Frequency:** How often does this error occur?
- **Impact:** How many users are affected?
- **Release Tracking:** Which version introduced the bug?
- **Breadcrumbs:** What actions led to the error?

### 3. Mark as Resolved

Once fixed:
1. Deploy the fix
2. Mark issue as "Resolved" in Sentry
3. Sentry will alert you if the error reoccurs

## Advanced Features

### Custom Error Context

Add custom context to errors:

```python
import sentry_sdk

with sentry_sdk.push_scope() as scope:
    scope.set_context("custom_data", {
        "user_id": user.id,
        "action": "photo_upload",
        "album_id": album.id
    })
    # Your code here
```

### Performance Monitoring

View slow database queries and endpoint performance:
- Navigate to **Performance** tab in Sentry
- See slowest transactions
- Identify bottlenecks

### Release Tracking

Track errors by version:

```bash
# In your deployment script
export SENTRY_RELEASE="photo-album@1.3.0"
```

## Troubleshooting

### Sentry Not Capturing Errors

**Check 1:** Verify DSN is set correctly
```bash
docker-compose exec web python manage.py shell
>>> from django.conf import settings
>>> print(settings.SENTRY_DSN)
```

**Check 2:** Ensure DEBUG=False (Sentry only runs in production mode)
```bash
docker-compose exec web python manage.py shell
>>> from django.conf import settings
>>> print(settings.DEBUG)  # Should be False
```

**Check 3:** Check Sentry initialization logs
```bash
docker-compose logs web | grep -i sentry
```

### Too Many Errors Being Sent

Lower the sample rates in `.env`:
```bash
SENTRY_TRACES_SAMPLE_RATE=0.05  # 5% instead of 10%
SENTRY_PROFILES_SAMPLE_RATE=0.05
```

### Privacy Concerns

Sentry is configured with privacy protections:
- `send_default_pii=False` (no user data sent)
- Password scrubbing enabled
- Sensitive headers filtered

To disable Sentry entirely:
```bash
# Remove or comment out SENTRY_DSN
# SENTRY_DSN=
```

## Cost Management

**Free Tier:** 5,000 errors/month

**Tips to stay within limits:**
1. Use sample rates (10% = 90% savings on performance data)
2. Set up alert rules to only notify for critical errors
3. Resolve recurring errors quickly
4. Use error grouping to consolidate similar issues

**Paid Plans:** Start at $26/month for more errors and features

## Documentation

- **Official Docs:** https://docs.sentry.io/platforms/python/guides/django/
- **Django Integration:** https://docs.sentry.io/platforms/python/guides/django/configuration/
- **Performance Monitoring:** https://docs.sentry.io/product/performance/

## Next Steps

1. ✅ Sign up for Sentry account
2. ✅ Get your DSN
3. ✅ Add DSN to `.env` file
4. ✅ Rebuild Docker container
5. ✅ Test error capture
6. ✅ Monitor production errors
7. ⏩ Set up email alerts (automatic)
8. ⏩ Configure release tracking (optional)
9. ⏩ Explore performance monitoring

---

**Questions?**
- Sentry Support: https://sentry.io/support/
- Django Photo Album Docs: `docs/`
