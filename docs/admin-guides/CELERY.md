# Celery Background Processing - Complete Guide

> Comprehensive guide for Celery setup, configuration, and troubleshooting for async AI processing

## Table of Contents
1. [Quick Start](#quick-start)
2. [How It Works](#how-it-works)
3. [Development Setup](#development-setup)
4. [Production Deployment](#production-deployment)
5. [Configuration](#configuration)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
7. [Common Tasks](#common-tasks)

---

## 🚀 Quick Start

### One-Command Production Setup ⭐
```bash
sudo ./deployment/setup_celery_systemd.sh
```

This automated script will:
- ✅ Check prerequisites (Redis, directories, permissions)
- ✅ Create systemd service files
- ✅ Enable services to start on boot
- ✅ Start Celery worker and beat scheduler
- ✅ Verify everything is running

### Verify Setup
```bash
# Check service status
sudo systemctl status photo-album-celery-worker
sudo systemctl status photo-album-celery-beat

# View logs
sudo tail -f /var/log/celery/worker.log
```

---

## 🧠 How It Works

### Overview
The Photo Album uses Celery for scheduled batch AI processing of photos and videos. Processing happens during low-traffic hours (2 AM daily) using efficient batch commands that load AI models once and process multiple items.

### Processing Flow

#### On Upload (Fast - Recommended)
1. User uploads photo/video
2. File is saved immediately to database with metadata
3. No AI processing - instant upload completion
4. Status: **Pending** (waiting for scheduled processing)
5. AI processing happens later via scheduled batch or on-demand

#### Scheduled Batch Processing (Daily - Primary Method)
- **2:00 AM**: Process up to 500 pending photos (batch command)
- **2:30 AM**: Process up to 500 pending videos (batch command)
- Much faster: Loads AI model once, processes all items
- More stable: No worker crashes from individual tasks

#### On-Demand Processing (Manual)
- Visit `/process-photos-ai/` or `/process-videos-ai/`
- Album admins: Process up to 50 items at once
- Site admins: No limit
- Uses same efficient batch processing
- Catches any items that failed during upload
- Configurable via AI Settings interface

### Processing Status
All media items have a `processing_status` field:
- **Pending**: Waiting for AI processing
- **Processing**: Currently being analyzed
- **Completed**: AI description and tags generated
- **Failed**: Processing failed (will retry on next scheduled run)

### Architecture
```
Upload → Django → Redis Queue → Celery Worker → AI Models → Database
                     ↑
                     |
              Celery Beat (Scheduler)
              Runs at 2 AM daily
```

---

## 💻 Development Setup

### Requirements
- Redis server running on `localhost:6379`
- Celery installed (included in `requirements.txt`)
- Python 3.11+

### Starting Services

You need **3 separate terminal processes**:

#### Terminal 1: Django Development Server
```bash
python manage.py runserver
```

#### Terminal 2: Celery Worker (Processes Tasks)
```bash
celery -A photo_album worker --loglevel=info
```

Expected output:
```
 -------------- celery@hostname v5.x.x
---- **** -----
--- * ***  * -- Linux-x.x.x
-- * - **** ---
- ** ---------- [config]
- ** ---------- .> app:         photo_album:0x...
- ** ---------- .> transport:   redis://localhost:6379/0
- *** --- * --- .> results:     redis://localhost:6379/0
-- ******* ---- .> concurrency: 4 (prefork)
--- ***** -----
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery

[tasks]
  . album.tasks.process_pending_photos_batch
  . album.tasks.process_pending_videos_batch
  . album.tasks.process_photo_ai
  . album.tasks.process_video_ai
```

#### Terminal 3: Celery Beat (Scheduler)
```bash
celery -A photo_album beat --loglevel=info
```

Expected output:
```
celery beat v5.x.x is starting.
LocalTime -> 2025-10-18 10:30:00
Configuration:
    . broker -> redis://localhost:6379/0
    . app -> photo_album
    . loader -> celery.loaders.app.AppLoader
    . scheduler -> celery.beat.PersistentScheduler
    . logfile -> [stderr]@%INFO
    . maxinterval -> 5.00 minutes (300s)
```

### Alternative: Using Screen/Tmux
```bash
# Create screen session
screen -S celery

# Start worker
celery -A photo_album worker --loglevel=info

# Detach: Ctrl+A, D

# Create another screen for beat
screen -S celery-beat
celery -A photo_album beat --loglevel=info

# List sessions
screen -ls

# Reattach to session
screen -r celery
```

---

## 🏭 Production Deployment

### Using Systemd (Recommended)

#### Automated Setup
```bash
sudo ./deployment/setup_celery_systemd.sh
```

#### Manual Setup

**1. Create Celery Worker Service**

File: `/etc/systemd/system/photo-album-celery-worker.service`
```ini
[Unit]
Description=Photo Album Celery Worker
After=network.target redis.service postgresql.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/photo_album
Environment="PATH=/var/www/photo_album/venv/bin"

ExecStart=/var/www/photo_album/venv/bin/celery -A photo_album worker \
    --loglevel=info \
    --logfile=/var/log/celery/worker.log \
    --pidfile=/var/run/celery/worker.pid \
    --detach

ExecStop=/var/www/photo_album/venv/bin/celery -A photo_album control shutdown
ExecReload=/bin/kill -s HUP $MAINPID

Restart=always
RestartSec=10s

StandardOutput=append:/var/log/celery/worker.log
StandardError=append:/var/log/celery/worker.log

[Install]
WantedBy=multi-user.target
```

**2. Create Celery Beat Service**

File: `/etc/systemd/system/photo-album-celery-beat.service`
```ini
[Unit]
Description=Photo Album Celery Beat Scheduler
After=network.target redis.service photo-album-celery-worker.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/photo_album
Environment="PATH=/var/www/photo_album/venv/bin"

ExecStart=/var/www/photo_album/venv/bin/celery -A photo_album beat \
    --loglevel=info \
    --logfile=/var/log/celery/beat.log \
    --pidfile=/var/run/celery/beat.pid

Restart=always
RestartSec=10s

StandardOutput=append:/var/log/celery/beat.log
StandardError=append:/var/log/celery/beat.log

[Install]
WantedBy=multi-user.target
```

**3. Create Directories**
```bash
sudo mkdir -p /var/log/celery /var/run/celery
sudo chown www-data:www-data /var/log/celery /var/run/celery
```

**4. Enable and Start Services**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable photo-album-celery-worker
sudo systemctl enable photo-album-celery-beat

# Start services
sudo systemctl start photo-album-celery-worker
sudo systemctl start photo-album-celery-beat

# Verify status
sudo systemctl status photo-album-celery-worker
sudo systemctl status photo-album-celery-beat
```

---

## ⚙️ Configuration

### Environment Variables

Add to `.env` file:
```env
# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# AI Processing Configuration (Recommended Settings)
AI_PROCESSING_ENABLED=True
AI_AUTO_PROCESS_ON_UPLOAD=False    # Disabled: Use batch processing (faster, more stable)
AI_SCHEDULED_PROCESSING=True       # Enable 2 AM batch processing (recommended)
AI_BATCH_SIZE=500                  # Process 500 photos per scheduled run
AI_PROCESSING_TIMEOUT=600          # 10 minutes timeout for batch processing
AI_SCHEDULE_HOUR=2                 # Batch processing hour (2 AM)
AI_SCHEDULE_MINUTE=0               # Batch processing minute (on the hour)
```

**Note:** `AI_AUTO_PROCESS_ON_UPLOAD=False` is recommended because:
- Batch processing is 50x faster (loads model once)
- More stable (no worker crashes)
- Better resource usage
- Instant uploads for users

### Web-Based Configuration (Preferred)

Configure via Django admin interface at `/ai-settings/`:

1. Navigate to `/ai-settings/` (admin only)
2. Adjust settings:
   - **Auto-process on upload**: ⚠️ OFF (recommended - use batch processing)
   - **Scheduled processing**: ✅ ON (recommended - primary method)
   - **Batch size**: 500 (20-10,000 items)
   - **Processing timeout**: 600 seconds (10 minutes for batches)
   - **Schedule hour**: 2 (0-23, 24-hour format)
   - **Schedule minute**: 0 (0-59)

Changes take effect immediately without restart!

### Hardware-Specific Recommendations

**Low-end Systems (Raspberry Pi, 2GB RAM):**
```env
AI_BATCH_SIZE=20
AI_PROCESSING_TIMEOUT=60
CELERY_WORKER_CONCURRENCY=1
```

**Mid-range Systems (4-8GB RAM):**
```env
AI_BATCH_SIZE=100
AI_PROCESSING_TIMEOUT=30
CELERY_WORKER_CONCURRENCY=2
```

**High-end Systems (16GB+ RAM, GPU):**
```env
AI_BATCH_SIZE=500
AI_PROCESSING_TIMEOUT=10
CELERY_WORKER_CONCURRENCY=4
```

---

## 📊 Monitoring & Troubleshooting

### Service Management

```bash
# Check status
sudo systemctl status photo-album-celery-worker
sudo systemctl status photo-album-celery-beat

# Start services
sudo systemctl start photo-album-celery-worker
sudo systemctl start photo-album-celery-beat

# Stop services
sudo systemctl stop photo-album-celery-worker
sudo systemctl stop photo-album-celery-beat

# Restart services (after code updates or config changes)
sudo systemctl restart photo-album-celery-worker
sudo systemctl restart photo-album-celery-beat

# Enable/disable auto-start on boot
sudo systemctl enable photo-album-celery-worker
sudo systemctl disable photo-album-celery-worker

# Reload systemd after editing service files
sudo systemctl daemon-reload
```

### Viewing Logs

```bash
# View logs in real-time
sudo tail -f /var/log/celery/worker.log
sudo tail -f /var/log/celery/beat.log

# View systemd journal
sudo journalctl -u photo-album-celery-worker -f
sudo journalctl -u photo-album-celery-beat -f

# View last 50 entries
sudo journalctl -u photo-album-celery-worker -n 50 --no-pager

# View logs for specific date
sudo journalctl -u photo-album-celery-worker --since "2025-10-18"
sudo journalctl -u photo-album-celery-worker --since "today"

# Search for errors
sudo journalctl -u photo-album-celery-worker | grep ERROR
```

### Celery Inspection Commands

```bash
# Check active tasks (currently running)
celery -A photo_album inspect active

# Check worker statistics
celery -A photo_album inspect stats

# Check scheduled tasks (queued)
celery -A photo_album inspect scheduled

# Check registered tasks
celery -A photo_album inspect registered

# Check worker availability
celery -A photo_album inspect ping

# Check reserved tasks
celery -A photo_album inspect reserved

# Revoke a task
celery -A photo_album control revoke <task-id>
```

### Common Issues

#### 1. Worker Not Starting
```bash
# Check Redis is running
redis-cli ping  # Should return: PONG

# Check service logs
sudo journalctl -u photo-album-celery-worker -n 100

# Check permissions
ls -la /var/log/celery/
ls -la /var/run/celery/

# Verify Python environment
/var/www/photo_album/venv/bin/python -c "import celery; print(celery.__version__)"
```

#### 2. Tasks Not Processing
```bash
# Check if worker is connected
celery -A photo_album inspect ping

# Check active tasks
celery -A photo_album inspect active

# Check if tasks are queued in Redis
redis-cli
> LLEN celery
> LRANGE celery 0 -1

# Restart worker
sudo systemctl restart photo-album-celery-worker
```

#### 3. Tasks Stuck in "Processing"
```bash
# Reset stuck tasks via Django shell
python manage.py shell

from album.models import Photo, Video

# Reset stuck photos
Photo.objects.filter(processing_status='processing').update(processing_status='pending')

# Reset stuck videos
Video.objects.filter(processing_status='processing').update(processing_status='pending')

# Check counts
print(f"Pending photos: {Photo.objects.filter(processing_status='pending').count()}")
print(f"Pending videos: {Video.objects.filter(processing_status='pending').count()}")
```

#### 4. Scheduled Tasks Not Running
```bash
# Check Beat is running
sudo systemctl status photo-album-celery-beat

# Check Beat logs
sudo tail -f /var/log/celery/beat.log

# Verify schedule in Django admin
# Go to /admin/album/aiprocessingsettings/

# Test scheduled task manually
python manage.py shell
from album.tasks import process_pending_photos_batch
result = process_pending_photos_batch.delay()
print(result.get())
```

#### 5. High Memory Usage
```bash
# Check worker memory
ps aux | grep celery

# Reduce concurrency
# Edit /etc/systemd/system/photo-album-celery-worker.service
# Add: --concurrency=1

sudo systemctl daemon-reload
sudo systemctl restart photo-album-celery-worker

# Or set environment variable
echo "CELERY_WORKER_CONCURRENCY=1" >> .env
```

#### 6. Redis Connection Issues
```bash
# Test Redis connection
redis-cli ping

# Check Redis is listening
sudo netstat -tulpn | grep 6379

# Restart Redis
sudo systemctl restart redis

# Check Redis logs
sudo journalctl -u redis -n 50
```

---

## 🎯 Common Tasks

### Testing Celery Setup

```bash
# Test photo processing task
python manage.py shell

from album.tasks import process_photo_ai
from album.models import Photo

# Get a photo ID
photo = Photo.objects.filter(processing_status='pending').first()
if photo:
    result = process_photo_ai.delay(photo.id)
    print(f"Task ID: {result.id}")
    print(f"Result: {result.get(timeout=60)}")  # Wait up to 60 seconds
```

### Manual Batch Processing

```bash
# Process pending photos manually
python manage.py shell

from album.tasks import process_pending_photos_batch
result = process_pending_photos_batch.delay()
print(result.get())

# Process pending videos manually
from album.tasks import process_pending_videos_batch
result = process_pending_videos_batch.delay()
print(result.get())
```

### Checking Processing Statistics

```bash
python manage.py shell

from album.models import Photo, Video

# Photo statistics
pending_photos = Photo.objects.filter(processing_status='pending').count()
processing_photos = Photo.objects.filter(processing_status='processing').count()
completed_photos = Photo.objects.filter(processing_status='completed').count()
failed_photos = Photo.objects.filter(processing_status='failed').count()

print(f"Photos - Pending: {pending_photos}, Processing: {processing_photos}, Completed: {completed_photos}, Failed: {failed_photos}")

# Video statistics
pending_videos = Video.objects.filter(processing_status='pending').count()
processing_videos = Video.objects.filter(processing_status='processing').count()
completed_videos = Video.objects.filter(processing_status='completed').count()
failed_videos = Video.objects.filter(processing_status='failed').count()

print(f"Videos - Pending: {pending_videos}, Processing: {processing_videos}, Completed: {completed_videos}, Failed: {failed_videos}")
```

### Reprocessing Failed Items

```bash
# Reset failed items to pending
python manage.py shell

from album.models import Photo, Video

Photo.objects.filter(processing_status='failed').update(processing_status='pending')
Video.objects.filter(processing_status='failed').update(processing_status='pending')

print("Failed items reset to pending")
```

### Force Process All Items

```bash
# Use management commands
python manage.py analyze_photos --all
python manage.py analyze_videos --all

# Or via web interface
# Navigate to /process-photos-ai/ or /process-videos-ai/
```

### Clearing the Queue

```bash
# Purge all pending tasks (⚠️ careful!)
celery -A photo_album purge

# Or via Redis CLI
redis-cli
> DEL celery
> QUIT
```

### After Code Updates

```bash
# Always restart worker and beat after code changes
sudo systemctl restart photo-album-celery-worker
sudo systemctl restart photo-album-celery-beat

# Or during development
# Stop worker (Ctrl+C) and restart with:
celery -A photo_album worker --loglevel=info
```

---

## 📚 Additional Resources

- **[AI Settings Guide](ADMIN_GUIDE_AI_SETTINGS.md)** - Configure AI processing settings
- **[Production Deployment](../deployment/DEPLOYMENT_SYSTEMD.md)** - Full production setup
- **[Docker Guide](../deployment/DOCKER.md)** - Container deployment with Celery

---

## 🎉 Success Indicators

Your Celery setup is working correctly when:

```bash
# Services are running
$ sudo systemctl status photo-album-celery-worker
Active: active (running)

$ sudo systemctl status photo-album-celery-beat
Active: active (running)

# Worker responds
$ celery -A photo_album inspect ping
-> celery@hostname: OK

# Tasks are processing
$ celery -A photo_album inspect active
celery@hostname:
  - process_photo_ai[task-id]
  
# Logs show activity
$ sudo tail -f /var/log/celery/worker.log
[INFO] Task album.tasks.process_photo_ai succeeded
```

---

**Version:** 1.2.0  
**Last Updated:** October 18, 2025  
**Maintained By:** Photo Album Development Team
