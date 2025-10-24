# Celery Deployment Checklist

Quick checklist for deploying Celery background processing to production.

## ☐ Pre-Deployment Checks

- [ ] Redis is installed and running
  ```bash
  redis-cli ping  # Should return: PONG
  ```

- [ ] Application is working correctly
  ```bash
  python manage.py check
  python manage.py migrate
  ```

- [ ] All dependencies installed
  ```bash
  pip install -r requirements.txt
  ```

- [ ] `.env` file configured with Redis URL
  ```env
  CELERY_BROKER_URL=redis://localhost:6379/0
  ```

## ☐ Deployment Steps

- [ ] Review configuration in deployment script
  ```bash
  nano deployment/setup_celery_systemd.sh
  # Check: APP_DIR, VENV_DIR, APP_USER, APP_GROUP
  ```

- [ ] Run automated setup script
  ```bash
  sudo ./deployment/setup_celery_systemd.sh
  ```

- [ ] Verify services are installed
  ```bash
  systemctl list-unit-files | grep photo-album-celery
  # Should show: photo-album-celery-worker.service enabled
  #              photo-album-celery-beat.service enabled
  ```

## ☐ Post-Deployment Verification

- [ ] Check worker service status
  ```bash
  sudo systemctl status photo-album-celery-worker
  # Should show: Active: active (running)
  ```

- [ ] Check beat service status
  ```bash
  sudo systemctl status photo-album-celery-beat
  # Should show: Active: active (running)
  ```

- [ ] View worker logs
  ```bash
  sudo tail -20 /var/log/celery/worker.log
  # Should show: [INFO] celery@hostname ready
  ```

- [ ] View beat logs
  ```bash
  sudo tail -20 /var/log/celery/beat.log
  # Should show: beat: Starting...
  ```

- [ ] Test with photo upload
  ```bash
  # Upload a photo through the web interface
  # Then check: sudo tail -f /var/log/celery/worker.log
  # Should show: Processing photo X: filename.jpg
  ```

## ☐ Configuration (Optional)

- [ ] Adjust worker concurrency if needed
  ```bash
  sudo nano /etc/systemd/system/photo-album-celery-worker.service
  # Edit: --concurrency=X
  sudo systemctl daemon-reload
  sudo systemctl restart photo-album-celery-worker
  ```

- [ ] Configure AI processing settings
  ```
  # Visit: /admin/album/aiprocessingsettings/
  # Adjust: auto-process, batch size, schedule time
  ```

- [ ] Set up log rotation
  ```bash
  sudo nano /etc/logrotate.d/celery
  # Copy config from DEPLOYMENT_SYSTEMD.md
  ```

## ☐ Monitoring Setup

- [ ] Bookmark monitoring commands
  ```bash
  # Status check
  sudo systemctl status photo-album-celery-worker
  
  # View logs
  sudo tail -f /var/log/celery/worker.log
  
  # Check active tasks
  celery -A photo_album inspect active
  ```

- [ ] Test service restart
  ```bash
  sudo systemctl restart photo-album-celery-worker
  sudo systemctl status photo-album-celery-worker
  # Should show: Active: active (running)
  ```

- [ ] Verify auto-start on boot
  ```bash
  systemctl is-enabled photo-album-celery-worker
  # Should return: enabled
  ```

## ☐ Documentation Review

- [ ] Read CELERY_QUICKREF.md (quick command reference)
- [ ] Bookmark DEPLOYMENT_SYSTEMD.md (troubleshooting guide)
- [ ] Review CELERY_SETUP.md (configuration details)

## ☐ Final Checks

- [ ] Upload test photo - verify AI processing works
- [ ] Check pending items count
  ```bash
  python manage.py shell -c "
  from album.models import Photo
  print(Photo.objects.filter(processing_status='pending').count())
  "
  ```

- [ ] Verify scheduled tasks are configured
  ```bash
  celery -A photo_album inspect scheduled
  # Should show scheduled beat tasks
  ```

- [ ] Document any custom configuration changes
- [ ] Update any deployment documentation for your environment

## ✅ Deployment Complete!

Once all checkboxes are ticked, your Celery workers are:
- ✅ Running in production
- ✅ Starting automatically on boot
- ✅ Processing photos/videos in background
- ✅ Running scheduled batch processing at 2 AM

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `sudo systemctl status photo-album-celery-worker` | Check worker status |
| `sudo systemctl restart photo-album-celery-worker` | Restart after code updates |
| `sudo tail -f /var/log/celery/worker.log` | View live logs |
| `celery -A photo_album inspect active` | See active tasks |

For detailed help, see: **DEPLOYMENT_SYSTEMD.md**
