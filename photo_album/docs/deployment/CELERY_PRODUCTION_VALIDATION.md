# Celery Production Validation Checklist

> Complete validation guide for testing Celery workers in production environment

## Pre-Validation Checklist

### 1. Prerequisites
- [ ] Redis server running and accessible
- [ ] Celery worker systemd service created and enabled
- [ ] Celery beat scheduler systemd service created and enabled
- [ ] Log directories created with proper permissions
- [ ] AI models downloaded and accessible
- [ ] PostgreSQL database configured

### 2. Service Status Check
```bash
# Check all services are active
sudo systemctl status photo-album-celery-worker
sudo systemctl status photo-album-celery-beat
sudo systemctl status redis

# Expected output: All should show "active (running)"
```

### 3. Configuration Verification
```bash
# Verify Django settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.CELERY_BROKER_URL)  # Should be redis://localhost:6379/0
>>> print(settings.AI_AUTO_PROCESS_ON_UPLOAD)  # True or False
>>> print(settings.AI_SCHEDULED_PROCESSING_ENABLED)  # True or False
>>> exit()
```

---

## Validation Tests

### Test 1: Worker Connectivity
**Goal**: Verify Celery worker can connect to Redis broker

```bash
# In Django shell
python manage.py shell

from photo_album.celery import app
result = app.control.inspect().active()
print(result)  # Should show worker node(s)
```

**Expected**: Dictionary showing active worker nodes
**If Failed**: Check Redis connection, verify CELERY_BROKER_URL setting

---

### Test 2: Simple Task Execution
**Goal**: Test basic task queuing and execution

```bash
# In Django shell
python manage.py shell

from photos.tasks import test_celery_task
result = test_celery_task.delay()
print(f"Task ID: {result.id}")
print(f"Status: {result.status}")

# Wait a few seconds
import time
time.sleep(3)
print(f"Result: {result.get()}")
```

**Expected**: 
- Task ID returned immediately
- Status: PENDING → SUCCESS
- Result: "Celery is working!"

**If Failed**: 
- Check worker logs: `sudo tail -f /var/log/celery/worker.log`
- Verify worker service is running
- Check for task routing errors

---

### Test 3: Photo Upload with Auto-Processing
**Goal**: Verify automatic AI processing on photo upload

#### 3.1 Enable Auto-Processing
1. Login as admin
2. Navigate to `/ai-settings/`
3. Enable "Auto-process on upload"
4. Save settings

#### 3.2 Upload Test Photo
1. Go to any album
2. Upload a single test photo (use a simple, recognizable image)
3. Note the photo ID from URL

#### 3.3 Monitor Processing
```bash
# Watch worker logs in real-time
sudo tail -f /var/log/celery/worker.log

# In Django shell (separate terminal)
python manage.py shell

from photos.models import Photo
photo = Photo.objects.get(id=YOUR_PHOTO_ID)
print(f"Status: {photo.processing_status}")
print(f"Description: {photo.ai_description}")
print(f"Tags: {[tag.name for tag in photo.tags.all()]}")
```

**Expected Timeline**:
- **Immediately after upload**: `processing_status = "pending"`
- **Within 10-30 seconds**: `processing_status = "processing"`
- **Within 1-3 minutes**: `processing_status = "completed"`
- AI description generated (text description of image)
- AI tags created (5-10 relevant tags)

**Expected Worker Log Output**:
```
[INFO] Task photos.tasks.process_photo_ai[...] received
[INFO] Processing photo ID: YOUR_PHOTO_ID
[INFO] Loading AI models...
[INFO] Generating description...
[INFO] Extracting tags...
[INFO] Task photos.tasks.process_photo_ai[...] succeeded
```

**If Failed**:
- Check worker logs for errors (CUDA, model loading, permissions)
- Verify AI models are accessible: `python manage.py check_ai_models`
- Check photo file exists and is readable
- Verify processing_status field in database

---

### Test 4: Video Upload with Auto-Processing
**Goal**: Verify automatic AI processing on video upload

#### 4.1 Upload Test Video
1. Upload a short test video (< 1 minute recommended)
2. Note the video ID

#### 4.2 Monitor Processing
```bash
# Watch worker logs
sudo tail -f /var/log/celery/worker.log

# Check video status
python manage.py shell
from photos.models import Video
video = Video.objects.get(id=YOUR_VIDEO_ID)
print(f"Status: {video.processing_status}")
print(f"Description: {video.ai_description}")
print(f"Tags: {[tag.name for tag in video.tags.all()]}")
```

**Expected**:
- Video processing takes 2-5 minutes (extracts middle frame)
- Description and tags generated from extracted frame
- Status progresses: pending → processing → completed

---

### Test 5: Manual Processing Command
**Goal**: Test manual batch processing (bypassing Celery)

```bash
# Process 10 pending photos manually
python manage.py process_photos_ai --limit 10

# Process 5 pending videos manually
python manage.py process_videos_ai --limit 5
```

**Expected**:
- Progress output showing each item being processed
- Success messages
- Items marked as "completed" in database

**Use Case**: Fallback if Celery has issues, or for manual control

---

### Test 6: Scheduled Processing (Beat Scheduler)
**Goal**: Verify scheduled batch processing runs at 2 AM

#### 6.1 Check Schedule Configuration
```bash
# In Django shell
python manage.py shell

from photo_album.celery import app
schedule = app.conf.beat_schedule
print(schedule)
```

**Expected**: Shows `process_pending_photos` and `process_pending_videos` tasks

#### 6.2 Force Immediate Execution (Testing)
```bash
# In Django shell
from photos.tasks import process_pending_photos_task, process_pending_videos_task

# Trigger tasks immediately
result1 = process_pending_photos_task.delay()
result2 = process_pending_videos_task.delay()

print(f"Photos task: {result1.id}")
print(f"Videos task: {result2.id}")
```

**Expected**:
- Tasks execute successfully
- Up to 500 pending photos processed
- Up to 500 pending videos processed
- Worker logs show batch processing activity

#### 6.3 Verify 2 AM Scheduled Run
- Leave system running overnight
- Check logs next morning:

```bash
# Check beat scheduler sent tasks at 2 AM
sudo grep "Scheduler: Sending" /var/log/celery/beat.log | grep "02:00"

# Check worker processed tasks
sudo grep "process_pending_photos_task\|process_pending_videos_task" /var/log/celery/worker.log | tail -20
```

---

### Test 7: Error Handling
**Goal**: Verify graceful error handling and recovery

#### 7.1 Test with Invalid Photo
1. Create a photo record with missing file
2. Trigger processing
3. Verify it marks as "failed" without crashing worker

#### 7.2 Test Resource Exhaustion
1. Upload 20+ photos at once
2. Monitor worker doesn't crash
3. Verify queue processes all items eventually

#### 7.3 Test Worker Restart
```bash
# Restart worker mid-processing
sudo systemctl restart photo-album-celery-worker

# Check tasks resume after restart
sudo tail -f /var/log/celery/worker.log
```

**Expected**: Tasks retry automatically, no data loss

---

### Test 8: Performance & Resource Monitoring
**Goal**: Monitor system resources during processing

```bash
# Monitor CPU/Memory while processing
htop  # or top

# Watch Redis memory usage
redis-cli INFO memory

# Check queue length
python manage.py shell
from photo_album.celery import app
inspect = app.control.inspect()
print(inspect.active_queues())
```

**Expected Baseline (Single Photo)**:
- CPU: 50-90% spike during processing (2-3 minutes)
- Memory: 2-4 GB (AI models loaded)
- Redis: Minimal (<100 MB)

**Red Flags**:
- Memory leak (continuously growing)
- Worker crashes under load
- Queue length growing indefinitely

---

## Production Health Monitoring

### Daily Checks
```bash
# Quick health check
sudo systemctl is-active photo-album-celery-worker
sudo systemctl is-active photo-album-celery-beat

# Check for failed items in last 24 hours
python manage.py shell
from photos.models import Photo, Video
from django.utils import timezone
from datetime import timedelta

yesterday = timezone.now() - timedelta(days=1)
failed_photos = Photo.objects.filter(processing_status='failed', uploaded_at__gte=yesterday).count()
failed_videos = Video.objects.filter(processing_status='failed', uploaded_at__gte=yesterday).count()
print(f"Failed in last 24h: {failed_photos} photos, {failed_videos} videos")
```

### Weekly Checks
```bash
# Check log sizes (rotate if needed)
du -h /var/log/celery/

# Check for pending items older than 1 week
python manage.py shell
from photos.models import Photo, Video
from django.utils import timezone
from datetime import timedelta

week_ago = timezone.now() - timedelta(days=7)
old_pending_photos = Photo.objects.filter(processing_status='pending', uploaded_at__lte=week_ago).count()
old_pending_videos = Video.objects.filter(processing_status='pending', uploaded_at__lte=week_ago).count()
print(f"Stuck pending (>7 days): {old_pending_photos} photos, {old_pending_videos} videos")

# If found, reprocess:
# python manage.py process_photos_ai --limit 100
```

---

## Troubleshooting Guide

### Worker Not Starting
```bash
# Check logs for errors
sudo journalctl -u photo-album-celery-worker -n 50

# Common issues:
# - Redis not running
# - Python environment wrong
# - Permissions on log directory
# - DJANGO_SETTINGS_MODULE not set
```

### Tasks Not Processing
1. **Check worker is running**: `sudo systemctl status photo-album-celery-worker`
2. **Check Redis connection**: `redis-cli ping` (should return "PONG")
3. **Check queue has tasks**: See monitoring section above
4. **Check worker logs**: `sudo tail -f /var/log/celery/worker.log`

### AI Processing Failures
- **CUDA errors**: Verify GPU drivers, consider CPU fallback
- **Model loading errors**: Run `python manage.py check_ai_models`
- **Memory errors**: Reduce batch size in AI Settings
- **Timeout errors**: Increase timeout in AI Settings

### Performance Issues
- **Slow processing**: Check AI_PROCESSING_TIMEOUT, consider GPU
- **Memory leaks**: Restart worker daily via cron
- **High CPU**: Limit concurrent tasks (worker `-c 1` flag)

---

## Sign-Off Checklist

Mark each item as complete before declaring production-ready:

- [ ] All 8 validation tests passed successfully
- [ ] Worker and beat services start automatically on boot
- [ ] Logs are being written and rotated properly
- [ ] Auto-processing on upload works (Test 3)
- [ ] Scheduled processing runs at 2 AM (Test 6)
- [ ] Error handling graceful (Test 7)
- [ ] Performance acceptable under load (Test 8)
- [ ] Monitoring commands documented and tested
- [ ] Team trained on troubleshooting procedures
- [ ] Backup plan documented (manual processing commands)

---

## Success Criteria

✅ **Production validation complete when**:
1. Users can upload photos/videos and see AI descriptions within 3 minutes
2. Worker processes 500+ items overnight without intervention
3. Services recover automatically after server reboot
4. No processing failures for 7 consecutive days
5. Performance metrics within acceptable ranges

---

## Additional Resources

- **Comprehensive Celery Guide**: `docs/admin-guides/CELERY.md`
- **Installation Guide**: `docs/getting-started/INSTALL.md` (Section 8)
- **AI Settings Interface**: `/ai-settings/` (admin only)
- **Management Commands**: `python manage.py help process_photos_ai`

---

**Document Version**: 1.0  
**Last Updated**: October 18, 2025  
**Validation Lead**: [Your Name]  
**Production Deployment Date**: [Date]
