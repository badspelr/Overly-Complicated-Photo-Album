# Production Deployment Guide - Celery with Systemd

This guide walks you through setting up Celery workers as system services that start automatically on boot and run in the background.

## Prerequisites

- Linux server (Ubuntu/Debian/RHEL/CentOS)
- Redis installed and running
- PostgreSQL installed and running
- Photo Album application installed at `/var/www/photo_album` (adjust paths as needed)
- Python virtual environment at `/var/www/photo_album/venv`
- Application running as user `www-data` (adjust as needed)

## Step 1: Install Required Packages

```bash
# Install Redis (if not already installed)
sudo apt update
sudo apt install redis-server

# Start and enable Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

## Step 2: Create Required Directories

```bash
# Create directories for PID files and logs
sudo mkdir -p /var/run/celery
sudo mkdir -p /var/log/celery

# Set ownership to the application user
sudo chown www-data:www-data /var/run/celery
sudo chown www-data:www-data /var/log/celery

# Set permissions
sudo chmod 755 /var/run/celery
sudo chmod 755 /var/log/celery
```

## Step 3: Customize Service Files

The service files are located in `deployment/systemd/`. You may need to adjust these paths:

| Setting | Default Value | Description |
|---------|---------------|-------------|
| `WorkingDirectory` | `/var/www/photo_album` | Your application directory |
| `Environment="PATH=..."` | `/var/www/photo_album/venv/bin` | Your Python virtual environment |
| `User` | `www-data` | User to run Celery as |
| `Group` | `www-data` | Group to run Celery as |
| `--concurrency` | `2` | Number of parallel workers (adjust for CPU) |

### Edit the service files if your paths differ:

```bash
cd /var/www/photo_album/deployment/systemd

# Edit worker service
sudo nano photo-album-celery-worker.service

# Edit beat service
sudo nano photo-album-celery-beat.service
```

### Performance Tuning

**Low-end hardware (1-2 CPU cores):**
```bash
--concurrency=1          # One task at a time
--time-limit=600         # 10 minute timeout
```

**Mid-range hardware (4 CPU cores):**
```bash
--concurrency=2          # Two parallel tasks (default)
--time-limit=300         # 5 minute timeout
```

**High-end hardware (8+ CPU cores, GPU):**
```bash
--concurrency=4          # Four parallel tasks
--time-limit=180         # 3 minute timeout
```

## Step 4: Install Service Files

```bash
# Copy service files to systemd directory
sudo cp /var/www/photo_album/deployment/systemd/photo-album-celery-worker.service \
    /etc/systemd/system/

sudo cp /var/www/photo_album/deployment/systemd/photo-album-celery-beat.service \
    /etc/systemd/system/

# Set correct permissions
sudo chmod 644 /etc/systemd/system/photo-album-celery-worker.service
sudo chmod 644 /etc/systemd/system/photo-album-celery-beat.service

# Reload systemd to recognize new services
sudo systemctl daemon-reload
```

## Step 5: Enable Services (Start on Boot)

```bash
# Enable services to start automatically on boot
sudo systemctl enable photo-album-celery-worker
sudo systemctl enable photo-album-celery-beat
```

You should see output like:
```
Created symlink /etc/systemd/system/multi-user.target.wants/photo-album-celery-worker.service
Created symlink /etc/systemd/system/multi-user.target.wants/photo-album-celery-beat.service
```

## Step 6: Start Services

```bash
# Start the Celery worker
sudo systemctl start photo-album-celery-worker

# Start the Celery beat scheduler
sudo systemctl start photo-album-celery-beat
```

## Step 7: Verify Services are Running

```bash
# Check worker status
sudo systemctl status photo-album-celery-worker

# Check beat status
sudo systemctl status photo-album-celery-beat
```

Expected output:
```
● photo-album-celery-worker.service - Photo Album Celery Worker
   Loaded: loaded (/etc/systemd/system/photo-album-celery-worker.service; enabled)
   Active: active (running) since Fri 2025-10-17 14:30:00 UTC; 5s ago
   ...
```

## Step 8: Check Logs

```bash
# View worker logs
sudo tail -f /var/log/celery/worker.log

# View beat logs
sudo tail -f /var/log/celery/beat.log

# View systemd journal logs
sudo journalctl -u photo-album-celery-worker -f
sudo journalctl -u photo-album-celery-beat -f
```

## Step 9: Test AI Processing

### Test Automatic Processing

1. Upload a photo through the web interface
2. Check the worker log:
   ```bash
   sudo tail -f /var/log/celery/worker.log
   ```
3. You should see:
   ```
   [INFO] Task album.tasks.process_photo_ai[abc-123] received
   [INFO] Processing photo 456: filename.jpg
   [INFO] Successfully processed photo 456
   [INFO] Task album.tasks.process_photo_ai[abc-123] succeeded
   ```

### Test Scheduled Processing

You can manually trigger the scheduled task to test without waiting until 2 AM:

```bash
# In Django shell
python manage.py shell

>>> from album.tasks import process_pending_photos_batch
>>> result = process_pending_photos_batch.delay()
>>> print(result.get())
{'status': 'success', 'queued': 10}
```

## Managing Services

### Start/Stop/Restart

```bash
# Stop services
sudo systemctl stop photo-album-celery-worker
sudo systemctl stop photo-album-celery-beat

# Start services
sudo systemctl start photo-album-celery-worker
sudo systemctl start photo-album-celery-beat

# Restart services (after code updates)
sudo systemctl restart photo-album-celery-worker
sudo systemctl restart photo-album-celery-beat
```

### Disable Services (Don't start on boot)

```bash
sudo systemctl disable photo-album-celery-worker
sudo systemctl disable photo-album-celery-beat
```

### View Service Configuration

```bash
sudo systemctl cat photo-album-celery-worker
sudo systemctl cat photo-album-celery-beat
```

## Monitoring and Maintenance

### Check Service Status

```bash
# Quick status check
sudo systemctl is-active photo-album-celery-worker
sudo systemctl is-active photo-album-celery-beat

# Detailed status
sudo systemctl status photo-album-celery-worker
sudo systemctl status photo-album-celery-beat
```

### Monitor Active Tasks

```bash
# Check active tasks
celery -A photo_album inspect active

# Check scheduled tasks
celery -A photo_album inspect scheduled

# Check worker stats
celery -A photo_album inspect stats
```

### Log Rotation

Create log rotation config to prevent logs from growing too large:

```bash
sudo nano /etc/logrotate.d/celery
```

Add:
```
/var/log/celery/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
    sharedscripts
    postrotate
        systemctl reload photo-album-celery-worker > /dev/null 2>&1 || true
        systemctl reload photo-album-celery-beat > /dev/null 2>&1 || true
    endscript
}
```

## Troubleshooting

### Services Won't Start

1. **Check systemd status:**
   ```bash
   sudo systemctl status photo-album-celery-worker -l
   ```

2. **Check journal logs:**
   ```bash
   sudo journalctl -u photo-album-celery-worker -n 50
   ```

3. **Verify paths:**
   - Check `WorkingDirectory` exists
   - Check virtual environment path is correct
   - Check user `www-data` has permissions

4. **Verify dependencies:**
   ```bash
   # Check Redis is running
   sudo systemctl status redis-server
   
   # Check PostgreSQL is running
   sudo systemctl status postgresql
   ```

### Tasks Not Processing

1. **Check worker is running:**
   ```bash
   sudo systemctl status photo-album-celery-worker
   ```

2. **Check for errors in logs:**
   ```bash
   sudo tail -100 /var/log/celery/worker.log
   ```

3. **Verify Redis connection:**
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

4. **Check Django settings:**
   ```python
   # In Django shell
   from django.conf import settings
   print(settings.CELERY_BROKER_URL)
   print(settings.AI_AUTO_PROCESS_ON_UPLOAD)
   ```

### Permission Errors

```bash
# Fix ownership of application directory
sudo chown -R www-data:www-data /var/www/photo_album

# Fix ownership of log directory
sudo chown -R www-data:www-data /var/log/celery

# Fix ownership of PID directory
sudo chown -R www-data:www-data /var/run/celery
```

### High Memory Usage

If Celery workers are using too much memory:

1. **Reduce concurrency:**
   Edit `/etc/systemd/system/photo-album-celery-worker.service`:
   ```
   --concurrency=1
   ```

2. **Reduce max tasks per child:**
   ```
   --max-tasks-per-child=25
   ```

3. **Reload and restart:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart photo-album-celery-worker
   ```

### Tasks Stuck in "Processing"

If tasks crash without updating status:

```python
# In Django shell
from album.models import Photo, Video

# Reset stuck photos
stuck_photos = Photo.objects.filter(processing_status='processing').count()
print(f"Found {stuck_photos} stuck photos")
Photo.objects.filter(processing_status='processing').update(processing_status='pending')

# Reset stuck videos
stuck_videos = Video.objects.filter(processing_status='processing').count()
print(f"Found {stuck_videos} stuck videos")
Video.objects.filter(processing_status='processing').update(processing_status='pending')
```

## Updating the Application

When you update the code, restart Celery services:

```bash
# Pull latest code
cd /var/www/photo_album
git pull

# Activate virtual environment and update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart photo-album-celery-worker
sudo systemctl restart photo-album-celery-beat

# If you use Gunicorn for Django
sudo systemctl restart gunicorn
```

## Security Best Practices

1. **Run as non-privileged user:**
   - Never run as `root`
   - Use `www-data` or create dedicated user

2. **Restrict file permissions:**
   ```bash
   # Application files
   sudo chmod 755 /var/www/photo_album
   sudo chmod 644 /var/www/photo_album/*.py
   
   # Environment file
   sudo chmod 600 /var/www/photo_album/.env
   ```

3. **Secure Redis:**
   ```bash
   # Edit Redis config
   sudo nano /etc/redis/redis.conf
   
   # Add password
   requirepass your-strong-password
   
   # Restart Redis
   sudo systemctl restart redis-server
   ```
   
   Update Django settings:
   ```python
   CELERY_BROKER_URL = 'redis://:your-strong-password@localhost:6379/0'
   ```

4. **Firewall rules:**
   ```bash
   # Only allow Redis connections from localhost
   sudo ufw deny 6379
   sudo ufw allow from 127.0.0.1 to any port 6379
   ```

## Performance Monitoring

### Install Flower (Celery monitoring tool)

```bash
# Install Flower
pip install flower

# Create systemd service
sudo nano /etc/systemd/system/photo-album-flower.service
```

Add:
```ini
[Unit]
Description=Photo Album Flower Celery Monitor
After=network.target photo-album-celery-worker.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/photo_album
Environment="PATH=/var/www/photo_album/venv/bin"
ExecStart=/var/www/photo_album/venv/bin/celery \
    --app=photo_album \
    flower \
    --port=5555 \
    --address=127.0.0.1
Restart=always

[Install]
WantedBy=multi-user.target
```

Start Flower:
```bash
sudo systemctl enable photo-album-flower
sudo systemctl start photo-album-flower
```

Access at: http://127.0.0.1:5555

## Summary

After completing this guide, you should have:

- ✅ Celery worker running as a system service
- ✅ Celery beat scheduler running as a system service
- ✅ Services start automatically on server boot
- ✅ Services restart automatically if they crash
- ✅ Proper logging and monitoring in place
- ✅ AI processing working automatically on photo/video uploads
- ✅ Scheduled batch processing at 2 AM daily

Your photo album application now has fully automated background AI processing! 🎉
