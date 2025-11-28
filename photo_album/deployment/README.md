# Deployment Files

This directory contains production deployment configurations for the Photo Album application.

## Directory Structure

```
deployment/
├── systemd/                              # Systemd service files
│   ├── photo-album-celery-worker.service # Celery worker service
│   └── photo-album-celery-beat.service   # Celery beat scheduler service
└── setup_celery_systemd.sh               # Automated setup script
```

## Quick Start

### Automatic Setup (Recommended)

Run the automated setup script:

```bash
sudo ./deployment/setup_celery_systemd.sh
```

This will:
1. Check all prerequisites
2. Create required directories
3. Customize service files for your system
4. Install and enable services
5. Start Celery workers

### Manual Setup

If you prefer manual setup or need to customize:

1. **Review the documentation:**
   - See `../DEPLOYMENT_SYSTEMD.md` for detailed instructions
   - See `../CELERY_QUICKREF.md` for quick command reference

2. **Customize service files:**
   ```bash
   cd systemd/
   # Edit paths, user, and concurrency in service files
   nano photo-album-celery-worker.service
   nano photo-album-celery-beat.service
   ```

3. **Install services:**
   ```bash
   sudo cp systemd/*.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable photo-album-celery-worker
   sudo systemctl enable photo-album-celery-beat
   sudo systemctl start photo-album-celery-worker
   sudo systemctl start photo-album-celery-beat
   ```

## Service Files

### photo-album-celery-worker.service

Runs the Celery worker process that handles background AI processing tasks.

**Key settings:**
- `--concurrency=2` - Number of parallel workers (adjust for CPU cores)
- `--max-tasks-per-child=50` - Restart worker after N tasks (prevents memory leaks)
- `--time-limit=300` - Kill tasks running longer than 5 minutes

### photo-album-celery-beat.service

Runs the Celery beat scheduler for automated batch processing.

**Schedule:**
- 2:00 AM daily - Process pending photos (up to 500)
- 2:30 AM daily - Process pending videos (up to 500)

## Customization

### Paths

Default paths in service files:
- Application: `/var/www/photo_album`
- Virtual Environment: `/var/www/photo_album/venv`
- User: `www-data`
- Group: `www-data`

**To change:** Edit the service files before installing.

### Performance Tuning

**Low-end hardware (1-2 CPU cores):**
```
--concurrency=1
--time-limit=600
```

**High-end hardware (8+ CPU cores, GPU):**
```
--concurrency=4
--time-limit=180
```

## Verification

After setup, verify services are running:

```bash
# Check status
sudo systemctl status photo-album-celery-worker
sudo systemctl status photo-album-celery-beat

# View logs
sudo tail -f /var/log/celery/worker.log
sudo tail -f /var/log/celery/beat.log
```

## Troubleshooting

See full troubleshooting guide in `../DEPLOYMENT_SYSTEMD.md`.

Common issues:

1. **Services won't start:**
   ```bash
   sudo journalctl -u photo-album-celery-worker -n 50
   ```

2. **Permission errors:**
   ```bash
   sudo chown -R www-data:www-data /var/www/photo_album
   sudo chown -R www-data:www-data /var/log/celery
   sudo chown -R www-data:www-data /var/run/celery
   ```

3. **Redis not running:**
   ```bash
   sudo systemctl start redis-server
   redis-cli ping
   ```

## Documentation

- **DEPLOYMENT_SYSTEMD.md** - Comprehensive production deployment guide
- **CELERY_SETUP.md** - Celery basics and development setup  
- **CELERY_QUICKREF.md** - Quick reference for common commands

## Support

For issues or questions:
1. Check logs: `/var/log/celery/*.log`
2. Review documentation in parent directory
3. Test with: `python manage.py shell` and import tasks manually
