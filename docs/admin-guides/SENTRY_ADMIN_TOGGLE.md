# Sentry Admin Toggle Guide

## Overview

You can now enable or disable Sentry error tracking directly from the Django Admin panel without touching code or environment variables. This makes it easy to test Sentry, troubleshoot issues, or temporarily disable monitoring.

## Accessing Sentry Settings

1. **Log in to Django Admin:**
   ```
   http://localhost:8000/admin/
   ```

2. **Navigate to Site Settings:**
   - Click on "Site Settings" in the admin home page
   - Or go directly to: `http://localhost:8000/admin/album/sitesettings/1/change/`

3. **Find Sentry Section:**
   - Look for "🔔 Sentry Error Tracking" section
   - Click to expand if collapsed

## Sentry Settings

### 1. Enable Sentry (Checkbox)

**Field:** `sentry_enabled`

- ✅ **Checked** = Sentry is enabled (when conditions are met)
- ❌ **Unchecked** = Sentry is completely disabled

**Important:** Sentry will only actually run when ALL of these conditions are met:
- ✅ Checkbox is enabled
- ✅ `SENTRY_DSN` is configured in environment variables
- ✅ `DEBUG=False` (production mode)

### 2. Traces Sample Rate

**Field:** `sentry_traces_sample_rate`  
**Default:** `0.1` (10%)  
**Range:** `0.0` to `1.0`

Controls what percentage of requests are monitored for performance:
- `0.0` = Disabled (no performance monitoring)
- `0.1` = 10% of requests (recommended for production)
- `0.5` = 50% of requests
- `1.0` = 100% of requests (only for testing, uses quota quickly)

**Example:** If you get 1,000 requests per day and set this to `0.1`, Sentry will monitor 100 requests.

### 3. Profiles Sample Rate

**Field:** `sentry_profiles_sample_rate`  
**Default:** `0.1` (10%)  
**Range:** `0.0` to `1.0`

Controls what percentage of transactions are profiled (detailed performance analysis):
- `0.0` = Disabled (no profiling)
- `0.1` = 10% of monitored transactions (recommended)
- `1.0` = 100% of monitored transactions

**Note:** Profiling is applied to already-sampled traces. If `traces_sample_rate=0.1` and `profiles_sample_rate=0.1`, then 1% of total requests will be profiled (0.1 × 0.1 = 0.01).

## Status Indicators

In the admin list view, you'll see a "Sentry Status" column with color-coded indicators:

| Status | Meaning |
|--------|---------|
| <span style="color: green;">✅ Active</span> | Sentry is running and capturing errors |
| <span style="color: orange;">⚠️ Enabled (DSN missing)</span> | Enabled but `SENTRY_DSN` not configured |
| <span style="color: orange;">⚠️ Enabled (DEBUG=True)</span> | Enabled but in development mode |
| <span style="color: gray;">❌ Disabled</span> | Sentry is turned off |

## Usage Examples

### Example 1: Enable Sentry in Production

**Scenario:** You want to start monitoring production errors.

**Steps:**
1. Make sure `SENTRY_DSN` is in your `.env` file
2. Make sure `DEBUG=False` in production
3. Go to Site Settings in admin
4. Check "Enable Sentry"
5. Set sample rates (default 0.1 is good)
6. Click "Save"

**Result:** You'll see a green success message: "✅ Sentry is now active! Tracking 10% of requests."

### Example 2: Temporarily Disable Sentry

**Scenario:** You're troubleshooting and don't want Sentry capturing test errors.

**Steps:**
1. Go to Site Settings
2. Uncheck "Enable Sentry"
3. Click "Save"

**Result:** Message: "Sentry error tracking is disabled."

### Example 3: Increase Monitoring for Investigation

**Scenario:** You're debugging a specific issue and want more data.

**Steps:**
1. Go to Site Settings
2. Change `traces_sample_rate` to `1.0` (100%)
3. Change `profiles_sample_rate` to `1.0` (100%)
4. Click "Save"
5. **Remember to lower these back to 0.1 after investigation!**

**Warning:** High sample rates use your Sentry quota quickly. Free tier is 5,000 errors/month.

### Example 4: Development Testing

**Scenario:** You want to test Sentry in development.

**Current Behavior:** Sentry won't activate while `DEBUG=True`

**Workaround (Temporary):**
```bash
# In .env file, temporarily:
DEBUG=False
SENTRY_DSN=your-test-dsn
```

Then enable Sentry in admin. **Remember to set `DEBUG=True` again for development!**

## Admin Messages

After saving Site Settings, you'll see helpful messages:

### Success Messages

✅ **"Sentry is now active! Tracking 10% of requests. Environment: production"**
- Sentry is working correctly
- Shows current sample rate and environment

### Warning Messages

⚠️ **"Sentry is enabled but SENTRY_DSN is not configured"**
- Action needed: Add `SENTRY_DSN` to `.env` file
- See: `docs/deployment/SENTRY_SETUP.md`

⚠️ **"Sentry is enabled but will only activate in production (DEBUG=False)"**
- Currently in development mode
- Sentry will activate when you deploy to production

### Info Messages

ℹ️ **"Sentry error tracking is disabled"**
- Sentry is turned off
- No errors will be captured

## How It Works

When you save the Site Settings:

1. **Database Update:** Your choices are saved to the database
2. **Automatic Reinitialization:** Sentry is automatically reinitialized with new settings
3. **No Restart Needed:** Changes take effect immediately (no container restart!)
4. **Privacy Protected:** All sensitive data is still scrubbed (passwords, tokens, etc.)

## Troubleshooting

### Sentry Not Capturing Errors

**Check 1: Is it enabled?**
```
Admin → Site Settings → Sentry enabled? ✓
```

**Check 2: Is DSN configured?**
```bash
docker-compose exec web python manage.py shell
>>> from django.conf import settings
>>> print(settings.SENTRY_DSN)
# Should show your DSN, not empty string
```

**Check 3: Is DEBUG=False?**
```bash
docker-compose exec web python manage.py shell
>>> from django.conf import settings
>>> print(settings.DEBUG)
# Should be False for Sentry to work
```

**Check 4: Check admin status**
- Go to Site Settings in admin
- Look at "Sentry Status" column
- Should be green "✅ Active"

### Still Not Working?

**Check logs:**
```bash
docker-compose logs web | grep -i sentry
```

**Test manually:**
```bash
docker-compose exec web python manage.py shell
>>> import sentry_sdk
>>> sentry_sdk.capture_message("Test from admin toggle")
```

Check your Sentry dashboard for the test message.

## Best Practices

### Production

- ✅ Enable Sentry
- ✅ Use `traces_sample_rate=0.1` (10%)
- ✅ Use `profiles_sample_rate=0.1` (10%)
- ✅ Monitor your Sentry quota
- ✅ Review errors weekly

### Staging/Testing

- ✅ Enable Sentry (separate Sentry project)
- ✅ Can use higher sample rates (0.5)
- ✅ Test error capture before production

### Development

- ❌ Usually keep Sentry disabled
- ❌ DEBUG=True prevents Sentry anyway
- ✅ Only enable for testing Sentry itself

## Sample Rate Calculator

Use this to estimate your Sentry usage:

```
Daily Requests: ___________
Traces Sample Rate: 0.1 (10%)
Profiles Sample Rate: 0.1 (10%)

Estimated Daily Usage:
- Traced Requests: Daily Requests × 0.1 = _______
- Profiled Requests: Daily Requests × 0.01 = _______

Monthly (30 days):
- Traced: Daily × 30 = _______
- Profiled: Daily × 30 = _______
```

**Free Tier Limit:** 5,000 errors/month

### Example Calculation

```
Daily Requests: 10,000
Traces Sample Rate: 0.1 (10%)
Profiles Sample Rate: 0.1 (10%)

Estimated Daily Usage:
- Traced Requests: 10,000 × 0.1 = 1,000
- Profiled Requests: 10,000 × 0.01 = 100

Monthly (30 days):
- Traced: 1,000 × 30 = 30,000 transactions
- Profiled: 100 × 30 = 3,000 profiles
```

**Note:** Error quota is separate from performance monitoring.

## Quick Reference

| Action | Steps |
|--------|-------|
| **Enable Sentry** | Admin → Site Settings → ✓ Enable Sentry → Save |
| **Disable Sentry** | Admin → Site Settings → ✗ Enable Sentry → Save |
| **Check Status** | Admin → Site Settings → Look at "Sentry Status" |
| **Adjust Monitoring** | Admin → Site Settings → Change sample rates → Save |
| **Test Sentry** | Enable → Trigger error → Check Sentry dashboard |

## Related Documentation

- **Setup Guide:** `docs/deployment/SENTRY_SETUP.md`
- **Environment Variables:** `.env.example`
- **Production Checklist:** `docs/deployment/PRODUCTION_SECURITY_CHECKLIST.md`

---

**Questions or Issues?**
- Check logs: `docker-compose logs web`
- Sentry Dashboard: https://sentry.io
- Django Admin: http://localhost:8000/admin/
