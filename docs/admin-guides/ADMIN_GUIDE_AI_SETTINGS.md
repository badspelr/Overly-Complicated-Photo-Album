# Admin Guide: Managing AI Processing Settings

## Quick Access

**URL**: `/admin/album/aiprocessingsettings/1/change/`

or

1. Go to Django Admin: `/admin/`
2. Click **Album** section
3. Click **AI Processing Settings**
4. Click the settings row to edit

---

## Available Settings

### Auto-process on Upload
**Toggle**: ☑️ ON / ☐ OFF

When **enabled**:
- Photos/videos are processed immediately after upload (one at a time)
- Individual Celery task per photo/video
- May slow down uploads and cause worker crashes under load

When **disabled** (recommended):
- Photos/videos upload instantly - no processing delay
- Items remain in "Pending" status
- Processed via scheduled batches (2 AM daily) or on-demand

**Recommended**: ⚠️ **OFF** (use scheduled batch processing instead)
**Why?** Batch processing is 50x faster, more stable, and doesn't crash workers

---

### Scheduled Processing
**Toggle**: ☑️ ON / ☐ OFF

When **enabled** (recommended):
- Batch processing runs daily at configured time (default 2 AM)
- Processes up to configured batch size (default 500 items)
- Much faster than individual task processing (50x speedup)
- Stable - no worker crashes

When **disabled**:
- No automatic batch processing
- Items must be processed manually via `/process-photos-ai/` or `/process-videos-ai/`

**Recommended**: ✅ **ON** (primary processing method)

---

### Batch Size
**Default**: 500
**Range**: 1 - 10,000

Maximum number of photos/videos to process in each scheduled run.

**Recommendations by hardware:**
- **Low-end (Raspberry Pi)**: 20-50
- **Mid-range (standard VPS)**: 100-200  
- **High-end (GPU server)**: 500-1000

---

### Processing Timeout
**Default**: 30 seconds
**Range**: 10 - 300 seconds

Maximum time allowed for processing each item before it's killed.

**Recommendations:**
- **CPU processing**: 30-60 seconds
- **GPU processing**: 10-30 seconds

---

### Schedule Hour
**Default**: 2 (2 AM)
**Range**: 0-23 (24-hour format)

Hour of the day to run scheduled batch processing.

**Recommendations:**
- Choose **low-traffic hours** (typically 2-4 AM)
- Avoid peak usage times

---

### Schedule Minute
**Default**: 0 (on the hour)
**Range**: 0-59

Minute within the hour to start processing.

**Example**: Hour=2, Minute=30 → Runs at 2:30 AM

---

### Album Admin Processing Limit
**Default**: 50
**Range**: 1 - unlimited

Maximum number of photos/videos an album admin can process in one batch via the web interface (`/process-photos-ai/` or `/process-videos-ai/`).

**Note**: This limit only applies to **album admins** (users who own albums). **Site admins** (superusers) have no limits.

**Recommendations:**
- **Small installations**: 50-100 (prevents accidental overload)
- **Medium installations**: 100-500 (balance between flexibility and control)
- **Large installations with GPU**: 500-1000 (album admins can process more efficiently)
- **Unlimited processing needed**: Set to a very high number (e.g., 999999)

**Use Cases:**
- **Limit resource usage**: Prevent album admins from submitting huge batch jobs
- **Fair resource allocation**: Ensure multiple album admins can use the system
- **Testing**: Lower limit during testing, raise for production
- **GPU optimization**: Higher limits work well with GPU acceleration

**Security Note**: Site admins always have unlimited processing regardless of this setting.

---

## Common Scenarios

### Scenario 1: Disable Auto-Processing for Testing
1. Uncheck **Auto-process on upload**
2. Keep **Scheduled processing** enabled
3. Click **Save**
4. Test uploads without immediate processing
5. Items will be processed at 2 AM

### Scenario 2: Process Only Manually
1. Uncheck **Auto-process on upload**
2. Uncheck **Scheduled processing**
3. Click **Save**
4. Use manual tools: `/process-photos-ai/` or management commands

### Scenario 3: Change Schedule to 3 AM
1. Change **Schedule hour** to `3`
2. Change **Schedule minute** to `0`
3. Click **Save**
4. Restart Celery Beat:
   ```bash
   sudo systemctl restart photo-album-celery-beat
   ```

### Scenario 4: Reduce Batch Size for Low-End Server
1. Change **Batch size** to `50`
2. Click **Save**
3. No restart needed

### Scenario 5: Increase Album Admin Processing Limit
**Use Case**: You want album admins to be able to process more photos at once (e.g., for GPU-accelerated systems)

1. Change **Album admin processing limit** to `200` (or desired value)
2. Click **Save**
3. No restart needed
4. Album admins can now process up to 200 photos/videos per batch

### Scenario 6: Restrict Album Admin Processing
**Use Case**: You want to limit resource usage during peak hours

1. Change **Album admin processing limit** to `25`
2. Click **Save**
3. Album admins are now limited to 25 photos/videos per batch
4. Site admins remain unlimited

---

## Checking if Settings are Active

### Via Django Admin
- Green checkmark = Setting is ON
- Empty checkbox = Setting is OFF

### Via Terminal (on server)
```bash
python manage.py shell -c "
from django.conf import settings
print('Auto-process:', settings.AI_AUTO_PROCESS_ON_UPLOAD)
print('Scheduled:', settings.AI_SCHEDULED_PROCESSING)
print('Batch size:', settings.AI_BATCH_SIZE)
"
```

### Via Database Settings
```bash
python manage.py shell -c "
from album.models import AIProcessingSettings
s = AIProcessingSettings.load()
print(f'Auto-process: {s.auto_process_on_upload}')
print(f'Scheduled: {s.scheduled_processing}')
print(f'Batch size: {s.batch_size}')
print(f'Album admin limit: {s.album_admin_processing_limit}')
"
```

**Example Output:**
```
Auto-process: False
Scheduled: True
Batch size: 500
Album admin limit: 50
```

---

## Environment Variables Override

**Note**: Environment variables in `.env` file take precedence over database settings.

If you have in `.env`:
```env
AI_AUTO_PROCESS_ON_UPLOAD=False
```

This will override the database setting. To use database settings, remove or comment out the environment variable.

---

## Monitoring Processing Status

### Check Pending Items
```bash
python manage.py shell -c "
from album.models import Photo, Video
pending_photos = Photo.objects.filter(processing_status='pending').count()
pending_videos = Video.objects.filter(processing_status='pending').count()
print(f'Pending photos: {pending_photos}')
print(f'Pending videos: {pending_videos}')
"
```

### Check Processing Logs
```bash
# Worker logs
sudo tail -f /var/log/celery/worker.log

# Beat scheduler logs
sudo tail -f /var/log/celery/beat.log
```

### Verify Celery is Running
```bash
sudo systemctl status photo-album-celery-worker
sudo systemctl status photo-album-celery-beat
```

---

## Troubleshooting

### Settings Don't Take Effect

1. **Check environment variables**:
   ```bash
   grep AI_ /var/www/photo_album/.env
   ```
   If variables are set, they override database settings.

2. **Restart Celery services**:
   ```bash
   sudo systemctl restart photo-album-celery-worker
   sudo systemctl restart photo-album-celery-beat
   ```

3. **Check Celery is running**:
   ```bash
   celery -A photo_album inspect active
   ```

### Processing Not Working Even When Enabled

1. **Verify Celery workers are running**:
   ```bash
   sudo systemctl status photo-album-celery-worker
   ```

2. **Check Redis is running**:
   ```bash
   redis-cli ping  # Should return: PONG
   ```

3. **View error logs**:
   ```bash
   sudo tail -100 /var/log/celery/worker.log
   ```

### Want to Process Pending Items Immediately

Instead of waiting for scheduled run:

```bash
python manage.py shell -c "
from album.tasks import process_pending_photos_batch
result = process_pending_photos_batch.delay()
print('Queued batch processing')
"
```

---

## Best Practices (Updated October 2025)

1. ⚠️ **Keep auto-processing OFF** for stability and performance
2. ✅ **Enable scheduled processing** as primary method (2 AM daily)
3. ✅ **Use on-demand processing** at `/process-photos-ai/` for immediate needs
4. **Adjust batch size** based on server capacity (500 default)
5. **Monitor logs regularly** to catch issues early
6. **Set schedule during low-traffic hours** (typically 2-4 AM)

---

## Quick Reference

| Setting | Recommended | Why |
|---------|-------------|-----|
| Auto-process on upload | ⚠️ **OFF** | Batch processing is 50x faster and more stable |
| Scheduled processing | ✅ **ON** | Primary processing method |
| Batch size | 500 | Good balance for most servers |
| Schedule hour | 2 | Low traffic time |
| Processing timeout | 600 | Allows batch processing to complete |

### Processing Methods Priority:
1. **Scheduled batches** (2 AM daily) - Primary method
2. **On-demand batches** (`/process-photos-ai/`) - For immediate needs
3. ~~Auto-process on upload~~ - Deprecated (slow, crashes workers)

---

For detailed troubleshooting, see: **DEPLOYMENT_SYSTEMD.md**

