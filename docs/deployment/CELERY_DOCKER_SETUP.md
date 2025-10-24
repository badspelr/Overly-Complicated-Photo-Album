# Celery in Docker - No Manual Setup Required! 🎉

**Date:** October 19, 2025  
**Status:** ✅ Configured and Running

## Overview

Celery is now **fully integrated into the Docker setup**. You don't need to manually start Celery workers anymore - they start automatically with the other services!

## What Changed

### Before (Manual Setup Required)
```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Celery worker (had to start manually)
celery -A photo_album worker --loglevel=info

# Terminal 3: Celery beat (scheduler)
celery -A photo_album beat --loglevel=info
```

### After (Automatic with Docker)
```bash
# One command starts everything!
./dev.sh up

# or
docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml up -d
```

## Services Included

When you run `./dev.sh up`, you get:

1. **photo_album-db-1** - PostgreSQL 15 with pgvector extension
2. **photo_album-redis-1** - Redis for caching and Celery message broker
3. **photo_album-web-1** - Django web server (Gunicorn)
4. **photo_album-celery-worker-1** - Background AI task processor ✨

## What Celery Does

The Celery worker automatically handles:

### AI Processing Tasks
- 🤖 **Face Detection** - Identifies faces in uploaded photos
- 🔍 **Image Embeddings** - Generates AI vectors for smart search
- 🎬 **Video Thumbnails** - Creates preview images for videos
- 📊 **EXIF Analysis** - Extracts camera metadata

### Background Operations
- 📧 **Email Sending** - Notification emails sent asynchronously
- 🔄 **Batch Processing** - Large operations don't block uploads
- ⏰ **Scheduled Tasks** - Cleanup, maintenance, periodic jobs

## Configuration Files

### docker-compose.light.yml
```yaml
celery-worker:
  build:
    context: .
    dockerfile: Dockerfile.light
  command: celery-worker
  environment:
    - CELERY_BROKER_URL=redis://redis:6379/0
    - CELERY_RESULT_BACKEND=redis://redis:6379/0
    - AI_ENABLE_GPU=False
  depends_on:
    - db
    - redis
```

### docker-compose.dev.yml
```yaml
celery-worker:
  volumes:
    # Code is mounted for live editing
    - ./album:/app/album
    - ./photo_album:/app/photo_album
  environment:
    - DEBUG=True
```

## Monitoring Celery

### Check if Running
```bash
./dev.sh ps
```

You should see:
```
photo_album-celery-worker-1  Up
```

### View Celery Logs
```bash
# Real-time logs
./dev.sh logs celery-worker

# Last 50 lines
docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml logs celery-worker --tail=50
```

### Check Celery Status
```bash
# Get shell in web container
./dev.sh shell

# Check worker status
celery -A photo_album inspect active

# Check registered tasks
celery -A photo_album inspect registered

# Ping workers
celery -A photo_album inspect ping
```

## Development Workflow

### Making Changes to Tasks

1. **Edit task code** in `album/tasks.py`:
   ```python
   @shared_task
   def process_photo(photo_id):
       # Your changes here
       pass
   ```

2. **Save the file** - changes are immediately available (code is mounted as volume)

3. **Restart Celery** to pick up changes:
   ```bash
   docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml restart celery-worker
   ```

### Testing AI Processing

Upload a photo through the web interface and watch the Celery logs:

```bash
./dev.sh logs celery-worker --follow
```

You'll see:
```
[2025-10-19 01:45:23,123: INFO] Task album.tasks.process_photo_embeddings started
[2025-10-19 01:45:25,456: INFO] Generated embeddings for photo ID: 123
[2025-10-19 01:45:25,789: INFO] Task album.tasks.process_photo_embeddings succeeded
```

## Troubleshooting

### Celery Not Starting?

Check the logs:
```bash
./dev.sh logs celery-worker
```

Common issues:
- **Redis not available** - Make sure Redis container is healthy
- **Import errors** - Check your task imports in `album/tasks.py`
- **Configuration issues** - Verify environment variables

### Tasks Not Being Processed?

1. **Check Redis connection:**
   ```bash
   docker-compose exec redis redis-cli ping
   # Should return: PONG
   ```

2. **Verify broker URL:**
   ```bash
   docker-compose exec web printenv | grep CELERY
   # Should show: CELERY_BROKER_URL=redis://redis:6379/0
   ```

3. **Restart the worker:**
   ```bash
   docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml restart celery-worker
   ```

### Worker Crashes?

Check for:
- **Memory issues** - Reduce concurrency (currently set to 2)
- **Task errors** - Check logs for exceptions
- **Model loading failures** - AI models need sufficient RAM

View detailed logs:
```bash
docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml logs celery-worker --tail=100
```

## Performance Tuning

### Adjust Worker Concurrency

In `docker-compose.light.yml`, the worker runs with 2 concurrent processes. You can adjust this:

```yaml
celery-worker:
  environment:
    - CELERY_WORKER_CONCURRENCY=4  # Increase for more parallel processing
```

**Guidelines:**
- **Development:** 2 workers (less resource intensive)
- **Production:** 4-8 workers (depends on CPU cores)
- **GPU enabled:** 1-2 workers (GPU memory limited)

### Memory Considerations

Each Celery worker loads the AI models into memory:
- **Without GPU:** ~500MB per worker
- **With GPU:** ~2GB per worker (GPU VRAM)

Adjust `CELERY_WORKER_CONCURRENCY` based on available RAM.

## Production Deployment

For production, use the full `docker-compose.yml` which includes:
- **celery-worker** - Background task processing
- **celery-beat** - Scheduled task scheduler

```bash
docker-compose up -d
```

This starts both the worker and beat scheduler automatically.

## Key Differences: Development vs Production

| Feature | Development (light.yml) | Production (full yml) |
|---------|-------------------------|----------------------|
| **Celery Worker** | ✅ 2 workers | ✅ 4 workers |
| **Celery Beat** | ❌ Not included | ✅ Included |
| **Code Volumes** | ✅ Mounted (dev.yml) | ❌ Baked into image |
| **Debug Mode** | ✅ Enabled | ❌ Disabled |
| **GPU Support** | ❌ CPU only | ✅ Optional GPU |

## Summary

✅ **Celery is fully automated** - No manual commands needed  
✅ **Starts with other services** - Just run `./dev.sh up`  
✅ **Code changes reflected** - Edit tasks, restart worker  
✅ **AI features work** - Face detection, smart search, etc.  
✅ **Easy monitoring** - `./dev.sh logs celery-worker`  

**You can now focus on development without worrying about Celery setup!** 🎉
