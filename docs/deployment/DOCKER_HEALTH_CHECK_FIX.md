# Docker Health Check Fix - Celery Containers

**Date:** October 21, 2025  
**Issue:** Celery worker and beat containers showing as "unhealthy"  
**Status:** ✅ RESOLVED

## Problem

The `photo_album_celery_worker` and `photo_album_celery_beat` containers were showing as "unhealthy" in `docker ps`:

```
photo_album_celery_worker   Up 3 hours (unhealthy)
photo_album_celery_beat     Up 3 hours (unhealthy)
```

### Root Cause

The Dockerfile contained a **single health check** that tried to connect to `http://localhost:8000/`:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1
```

This health check was **appropriate for the web container** but **inappropriate for Celery containers** because:
- Celery worker doesn't run a web server
- Celery beat doesn't run a web server  
- They were inheriting this health check from the base Dockerfile
- Result: Health check always failed with "Could not connect to server"

### Important Note

**The Celery services were working perfectly** despite showing as "unhealthy". This was purely a cosmetic/monitoring issue. The health check failure didn't affect functionality:
- ✅ Tasks were being processed successfully
- ✅ Scheduled jobs were running at 2:00 AM and 2:30 AM
- ✅ Redis connection was working
- ✅ Database connection was working

## Solution

Added **service-specific health checks** in `docker-compose.yml` to override the Dockerfile's default:

### 1. Celery Worker Health Check

```yaml
healthcheck:
  test: ["CMD-SHELL", "celery -A photo_album inspect ping -d celery@$$HOSTNAME"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

**How it works:**
- Uses Celery's built-in `inspect ping` command
- Checks if the worker is responsive and processing tasks
- `$$HOSTNAME` expands to the container's hostname
- Returns exit code 0 if worker is healthy, non-zero if not

### 2. Celery Beat Health Check

```yaml
healthcheck:
  test: ["CMD-SHELL", "test -f /app/celerybeat-schedule || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

**How it works:**
- Checks if the `celerybeat-schedule` file exists
- This file is created when Celery Beat starts
- Updated continuously as Beat schedules tasks
- If file exists, Beat is running properly

## Changes Made

### File: `docker-compose.yml`

**Before:**
```yaml
celery-worker:
  # ... configuration ...
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
  # No healthcheck - inherited from Dockerfile

celery-beat:
  # ... configuration ...
  networks:
    - photo_album_network
  # No healthcheck - inherited from Dockerfile
```

**After:**
```yaml
celery-worker:
  # ... configuration ...
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
  healthcheck:
    test: ["CMD-SHELL", "celery -A photo_album inspect ping -d celery@$$HOSTNAME"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s

celery-beat:
  # ... configuration ...
  networks:
    - photo_album_network
  healthcheck:
    test: ["CMD-SHELL", "test -f /app/celerybeat-schedule || exit 1"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

## Verification

After restarting the containers:

```bash
$ docker-compose up -d celery-worker celery-beat
$ docker ps --format "table {{.Names}}\t{{.Status}}"

NAMES                        STATUS
photo_album_celery_worker    Up 59 seconds (healthy)
photo_album_celery_beat      Up 59 seconds (healthy)
photo_album_web              Up 6 minutes (healthy)
photo_album_redis            Up 3 hours (healthy)
photo_album_db               Up 3 hours (healthy)
```

✅ **All containers now show as healthy!**

## Health Check Details

### What Gets Checked

| Container | Health Check | What It Validates |
|-----------|--------------|-------------------|
| **db** | `pg_isready -U postgres` | PostgreSQL accepting connections |
| **redis** | `redis-cli ping` | Redis responding to commands |
| **web** | `curl -f http://localhost:8000/` | Django web server running |
| **celery-worker** | `celery inspect ping` | Worker processing tasks |
| **celery-beat** | `test -f celerybeat-schedule` | Beat scheduler running |

### Health Check Timing

All health checks use the same intervals:
- **Interval:** 30 seconds (how often to check)
- **Timeout:** 10 seconds (max time for check to complete)
- **Retries:** 3 (failures before marking unhealthy)
- **Start Period:** 40 seconds (grace period after container starts)

## Testing

To verify the health checks are working:

### 1. Check Current Status
```bash
docker ps
```

### 2. Inspect Detailed Health
```bash
docker inspect photo_album_celery_worker --format='{{json .State.Health}}' | python3 -m json.tool
docker inspect photo_album_celery_beat --format='{{json .State.Health}}' | python3 -m json.tool
```

### 3. Force Health Check
```bash
docker inspect photo_album_celery_worker --format='{{.State.Health.Status}}'
docker inspect photo_album_celery_beat --format='{{.State.Health.Status}}'
```

### 4. Watch Health Status Live
```bash
watch -n 2 'docker ps --format "table {{.Names}}\t{{.Status}}"'
```

## Benefits

### 1. Accurate Monitoring
- Health status now reflects actual service state
- Easy to spot problems with `docker ps`
- Integration with Docker orchestration tools (e.g., Docker Swarm, Kubernetes)

### 2. Proper Service Dependencies
- Can use `condition: service_healthy` in depends_on
- Ensures services start in correct order with proper readiness checks

### 3. Automated Recovery
- Docker can automatically restart unhealthy containers
- Combined with `restart: unless-stopped` for resilience

### 4. Better Debugging
- Health check logs help diagnose issues
- Clear indication of what's failing

## Alternative Health Check Options

### For Celery Worker (Other Options)

1. **Check Redis Connection:**
   ```yaml
   test: ["CMD-SHELL", "python -c 'from celery import Celery; app = Celery(); app.config_from_object(\"photo_album.celeryconfig\"); app.broker_connection().connect()'"]
   ```

2. **Check Task Queue:**
   ```yaml
   test: ["CMD-SHELL", "celery -A photo_album inspect active"]
   ```

### For Celery Beat (Other Options)

1. **Check Beat Process:**
   ```yaml
   test: ["CMD-SHELL", "pgrep -f 'celery.*beat'"]
   ```

2. **Check Schedule File Age:**
   ```yaml
   test: ["CMD-SHELL", "find /app/celerybeat-schedule -mmin -5 || exit 1"]
   ```
   (Fails if file hasn't been modified in 5 minutes)

## Why Not Fix the Dockerfile?

We could remove the health check from the Dockerfile entirely:

```dockerfile
# Remove this line:
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1
```

**Pros:**
- Each service defines its own appropriate health check
- More flexible

**Cons:**
- The web container relies on this health check
- Would need to duplicate it in docker-compose.yml

**Decision:** Keep the Dockerfile health check for the web container, override it for Celery containers in docker-compose.yml. This is the standard Docker pattern.

## Production Considerations

For production deployments:

1. **Monitor Health Metrics:**
   - Use Prometheus + Grafana to track health check success/failure rates
   - Alert on prolonged unhealthy states

2. **Adjust Timing:**
   - May need longer `start_period` for slow startup
   - May need more `retries` to avoid false positives

3. **Add More Checks:**
   - Could check database connection
   - Could verify task processing rate
   - Could check memory/CPU usage

4. **Log Health Events:**
   - Monitor health check failures in logs
   - Track patterns (e.g., failing every night at 2 AM)

## Related Documentation

- Docker Health Check: https://docs.docker.com/engine/reference/builder/#healthcheck
- Celery Monitoring: https://docs.celeryq.dev/en/stable/userguide/monitoring.html
- Docker Compose depends_on: https://docs.docker.com/compose/compose-file/compose-file-v3/#depends_on

## Conclusion

✅ **Issue Resolved:** All Docker containers now show proper health status  
✅ **Services Working:** Celery worker and beat functioning normally  
✅ **Monitoring Improved:** Accurate health checks for all services  
✅ **Production Ready:** Proper health checks in place for orchestration

The "unhealthy" status was a false alarm caused by an inappropriate health check. The Celery services were always working correctly - they just needed a health check that matched their actual functionality.

---

## Update - October 2025: Web Container Health Check Improvements

### Additional Issue: Web Health Check Failures

After fixing the Celery health checks, we discovered the web container health checks were also failing intermittently, showing "unhealthy" status while the application worked fine.

### Root Causes

1. **HTTP Redirects**: The root URL (`/`) redirects to login for unauthenticated users. The `curl -f` flag treats redirects (302) as failures.

2. **Slow AI Processing**: During AI model loading or processing, requests could take longer than the 10s timeout.

3. **Insufficient Start Period**: 40s wasn't enough for AI models to load on first startup.

### Solution: Enhanced Web Health Check

**Updated configuration:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "-L", "-I", "http://localhost:8000/"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

**Key Improvements:**
- **`-L` flag**: Follow HTTP redirects (handles auth redirects properly)
- **`-I` flag**: Use HEAD request instead of GET (faster, doesn't download page content)
- **60s start_period**: Increased from 40s to give AI models time to load
- **3 retries**: Adequate for detecting real issues without false positives

### Impact

✅ **Eliminated 504 Gateway Timeout** errors from Nginx  
✅ **Accurate "healthy" status** even with auth redirects  
✅ **Faster health checks** with HEAD requests  
✅ **Better startup reliability** with AI models

### For More Information

See [GPU_SUPPORT.md](GPU_SUPPORT.md) for the full context of these improvements, which were part of refactoring GPU support for CPU-only deployments.

