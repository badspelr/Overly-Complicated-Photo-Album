# Django Photo Album - Complete Docker Guide

> Comprehensive guide for Docker deployment including quick commands, resource optimization, and production best practices

## Table of Contents
1. [Quick Start](#quick-start)
2. [Resource Optimization](#resource-optimization)
3. [Docker Commands](#docker-commands)
4. [Production Deployment](#production-deployment)
5. [Troubleshooting](#troubleshooting)
6. [Performance & Security](#performance--security)

---

## 🚀 Quick Start

### Starting the Application
```bash
cd photo_album

# Option 1: Lightweight CPU-only (Recommended for development)
docker-compose -f docker-compose.light.yml up -d --build

# Option 2: Full version with GPU support (Production)
docker-compose up -d --build

# Start in foreground to see logs
docker-compose up
```

### Accessing the Application
- **Web Interface**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **Default Login**: admin / admin123 (⚠️ change immediately!)

### Stopping the Application
```bash
# Stop lightweight version
docker-compose -f docker-compose.light.yml down

# Stop full version
docker-compose down

# Stop and remove volumes (⚠️ DANGER: deletes all data)
docker-compose down -v
```

---

## 🐳 Resource Optimization

### The Challenge
- Original Docker build downloads **~1.5GB** of ML packages (PyTorch + CUDA)
- Can crash systems with limited resources (< 4GB RAM)
- Takes **10-15 minutes** to build
- Downloads 900MB PyTorch + 600MB CUDA libraries

### The Solution: Multiple Configurations

#### **Option 1: Lightweight CPU-Only** ⭐ Recommended

**Files:**
- `requirements-docker.txt` - CPU-only dependencies (~200MB PyTorch)
- `Dockerfile.light` - Optimized container build
- `docker-compose.light.yml` - Lightweight service configuration

**Usage:**
```bash
# Build and start (3-5 minutes vs 15+ minutes)
docker-compose -f docker-compose.light.yml up -d --build

# View logs
docker-compose -f docker-compose.light.yml logs -f

# Stop
docker-compose -f docker-compose.light.yml down
```

**Resource Savings:**
- PyTorch: 200MB (CPU) vs 900MB (GPU)
- No CUDA: Saves additional 600MB  
- Build time: 3-5 min vs 10-15 min
- Memory usage: Much lower during build

**Features:**
- ✅ All Django functionality
- ✅ Photo/video uploads (including MOV support)
- ✅ AI features (CPU-only, slower but functional)
- ✅ Database & Redis
- ❌ GPU acceleration (CPU processing only)

#### **Option 2: Full GPU Version**

For production deployments with GPU servers:
```bash
docker-compose up -d --build
```

**Features:**
- ✅ GPU-accelerated AI processing
- ✅ Faster image analysis (~0.4s per photo)
- ✅ CUDA support
- ⚠️ Requires NVIDIA GPU with CUDA
- ⚠️ Large download size (1.5GB+)

#### **Option 3: Minimal Build** (Infrastructure Testing)

For testing without AI features:
```bash
# Disable AI features temporarily
echo "AI_FEATURES_ENABLED=False" >> .env

# Build without ML packages
# Edit requirements-docker.txt to remove PyTorch/CLIP/BLIP
docker-compose up -d --build
```

### Resource Comparison

| Configuration | PyTorch Size | Total Download | Build Time | Memory Peak | AI Features |
|---------------|-------------|----------------|------------|-------------|-------------|
| **Full GPU** | 900MB | ~1.5GB | 10-15 min | High | GPU accelerated |
| **Light CPU** ⭐ | 200MB | ~400MB | 3-5 min | Medium | CPU only |
| **Minimal** | 0MB | ~100MB | 1-2 min | Low | Disabled |

### When to Use Each Option

**Lightweight CPU Version:**
- ✅ Development and testing
- ✅ Low-resource systems (< 8GB RAM)
- ✅ CI/CD pipelines
- ✅ Quick deployments
- ✅ Learning and experimentation

**Full GPU Version:**
- ✅ Production with GPU servers
- ✅ High-volume AI processing
- ✅ Performance-critical deployments
- ✅ Processing 1000+ photos regularly

**Minimal Version:**
- ✅ Infrastructure testing only
- ✅ Database migrations
- ✅ Static file serving
- ✅ UI/UX development without AI

---

## 🔧 Docker Commands Reference

### Container Management
```bash
# Check container status
docker-compose ps

# Restart a specific service
docker-compose restart web
docker-compose restart db

# Execute commands in running container
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### Viewing Logs
```bash
# View all logs
docker-compose logs -f

# View only web application logs
docker-compose logs -f web

# View only database logs
docker-compose logs -f db

# View last 100 lines
docker-compose logs --tail=100 web
```

### Database Operations
```bash
# Connect to PostgreSQL
docker-compose exec db psql -U dniel -d photo_album

# Backup database
docker-compose exec db pg_dump -U dniel photo_album > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T db psql -U dniel photo_album < backup.sql

# Check database size
docker-compose exec db psql -U dniel photo_album -c "SELECT pg_size_pretty(pg_database_size('photo_album'));"
```

### File Management
```bash
# Copy files from container
docker cp $(docker-compose ps -q web):/app/media ./media_backup

# Copy files to container
docker cp ./media $(docker-compose ps -q web):/app/

# Fix file permissions
docker-compose exec web chown -R app:app /app/media
docker-compose exec web chmod -R 755 /app/staticfiles
```

### Cleanup Commands
```bash
# Clean up Docker system
docker system prune -f

# Remove unused images
docker image prune -f

# Remove unused volumes (⚠️ DANGER: may delete data)
docker volume prune -f

# See disk usage
docker system df
```

---

## 🏭 Production Deployment

### Pre-Deployment Checklist

#### 1. Change Default Passwords
```bash
# Edit .env.production file
DJANGO_SUPERUSER_PASSWORD=your-secure-password-here
SECRET_KEY=your-super-secret-key-at-least-50-chars
DB_PASSWORD=secure-database-password
```

#### 2. Update Environment Variables
```bash
# Security settings
DEBUG=False
SECRET_KEY=<generate-new-secret-key>

# Domain configuration
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database credentials
DB_PASSWORD=<secure-password>

# AI Settings
AI_ENABLE_GPU=True  # or False for CPU-only
```

#### 3. SSL/HTTPS Setup
Use nginx reverse proxy with Let's Encrypt:

```nginx
# /etc/nginx/sites-available/photo-album
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/photo_album/staticfiles/;
    }

    location /media/ {
        alias /path/to/photo_album/media/;
    }
}
```

#### 4. Monitoring Setup
```bash
# Monitor resource usage
docker stats

# Check application health
curl http://localhost:8000/health/

# Monitor logs in real-time
docker-compose logs -f web | grep ERROR
```

#### 5. Automated Backups
```bash
# Create backup script: /usr/local/bin/backup-photo-album.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/photo-album"

mkdir -p "$BACKUP_DIR"

# Backup database
docker-compose exec -T db pg_dump -U dniel photo_album > "$BACKUP_DIR/db_$DATE.sql"

# Backup media files
docker cp $(docker-compose ps -q web):/app/media "$BACKUP_DIR/media_$DATE"

# Compress
tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz" "$BACKUP_DIR/db_$DATE.sql" "$BACKUP_DIR/media_$DATE"

# Remove uncompressed backups
rm -rf "$BACKUP_DIR/db_$DATE.sql" "$BACKUP_DIR/media_$DATE"

# Keep only last 30 days of backups
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +30 -delete

echo "Backup completed: backup_$DATE.tar.gz"
```

Add to crontab:
```bash
# Run daily at 2 AM
0 2 * * * /usr/local/bin/backup-photo-album.sh >> /var/log/photo-album-backup.log 2>&1
```

### Environment Variables Reference

| Variable | Description | Default | Production Value |
|----------|-------------|---------|------------------|
| `DEBUG` | Django debug mode | `False` | `False` |
| `SECRET_KEY` | Django secret key | Required | 50+ char random |
| `DB_HOST` | Database host | `db` | `db` |
| `DB_NAME` | Database name | `photo_album` | `photo_album` |
| `DB_USER` | Database user | `dniel` | Custom user |
| `DB_PASSWORD` | Database password | `jbsacer` | Secure password |
| `ALLOWED_HOSTS` | Allowed host names | `localhost` | Your domain(s) |
| `AI_ENABLE_GPU` | Enable GPU for AI | `False` | `True` (if GPU available) |
| `REDIS_URL` | Redis connection | `redis://redis:6379/0` | Same |
| `EMAIL_HOST` | SMTP server | - | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | - | `587` |

---

## 🔍 Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker-compose logs web

# Check if ports are available
sudo netstat -tulpn | grep :8000
sudo lsof -i :8000

# Restart with fresh build
docker-compose down
docker-compose up -d --build

# Check container health
docker inspect $(docker-compose ps -q web) | grep Health
```

### Database Connection Issues

```bash
# Check database status
docker-compose logs db

# Test database connection
docker-compose exec web python manage.py dbshell

# Verify database credentials
docker-compose exec db psql -U dniel -d photo_album -c "SELECT version();"

# Check network connectivity
docker-compose exec web ping db
```

### Permission Issues

```bash
# Fix file permissions
docker-compose exec web chown -R app:app /app/media
docker-compose exec web chmod -R 755 /app/staticfiles

# Check current permissions
docker-compose exec web ls -la /app/media

# Run migrations as correct user
docker-compose exec web python manage.py migrate
```

### Out of Disk Space

```bash
# Check Docker disk usage
docker system df

# Clean up Docker system
docker system prune -a -f

# Remove specific images
docker images | grep photo_album
docker rmi <image-id>

# Remove unused volumes
docker volume ls
docker volume prune -f

# Check host disk space
df -h
```

### Build Running Out of Memory

```bash
# Check available memory
free -h

# Limit build memory
docker build --memory=2g -f Dockerfile.light .

# Use swap if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make swap permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Slow Downloads During Build

```bash
# Use different PyPI mirror
docker-compose build --build-arg PIP_INDEX_URL=https://pypi.douban.com/simple/

# Pre-download packages
pip download -r requirements-docker.txt -d ./wheels/

# Use Docker BuildKit for caching
DOCKER_BUILDKIT=1 docker-compose build
```

### AI Processing Not Working

```bash
# Check AI model availability
docker-compose exec web python manage.py shell
>>> from album.ai_utils import test_ai_setup
>>> test_ai_setup()

# Verify GPU availability (if using full version)
docker-compose exec web nvidia-smi

# Check AI settings
docker-compose exec web python manage.py shell -c "from album.models import AIProcessingSettings; print(AIProcessingSettings.load())"

# Test manual AI processing
docker-compose exec web python manage.py analyze_photos --limit 1
```

---

## ⚡ Performance & Security

### Performance Optimization

#### 1. Scale Workers
```yaml
# In docker-compose.yml
web:
  deploy:
    replicas: 3  # Multiple web containers
  command: gunicorn --workers 4 --bind 0.0.0.0:8000 photo_album.wsgi:application
```

#### 2. Configure Gunicorn
```bash
# Calculate workers: (2 * CPU cores) + 1
# For 4 cores: (2 * 4) + 1 = 9 workers

# In docker-entrypoint.sh:
gunicorn --workers 9 \
         --worker-class gthread \
         --threads 2 \
         --timeout 120 \
         --bind 0.0.0.0:8000 \
         photo_album.wsgi:application
```

#### 3. Redis Caching
Already configured in docker-compose.yml - improves performance significantly:
- Session storage
- Cache backend
- Celery message broker

#### 4. Build Optimization
```bash
# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1

# Use layer caching effectively
docker-compose build --pull

# Multi-stage builds (already in Dockerfile.light)
```

### Security Best Practices

#### 1. Use Secrets Management
```yaml
# docker-compose.production.yml
services:
  web:
    secrets:
      - db_password
      - secret_key

secrets:
  db_password:
    file: ./secrets/db_password.txt
  secret_key:
    file: ./secrets/secret_key.txt
```

#### 2. Network Security
```yaml
# docker-compose.yml
networks:
  backend:
    internal: true  # No external access
  frontend:
    # Exposed to internet
```

#### 3. Run as Non-Root User
```dockerfile
# Already implemented in Dockerfile.light
RUN adduser --disabled-password --gecos '' app
USER app
```

#### 4. Security Headers
Add to nginx configuration:
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

#### 5. Regular Security Updates
```bash
# Update base images regularly
docker pull python:3.13-slim

# Rebuild containers
docker-compose build --no-cache

# Update Python packages
docker-compose exec web pip install --upgrade pip
docker-compose exec web pip list --outdated
```

### Maintenance Commands

```bash
# Update dependencies
docker-compose exec web pip install -r requirements.txt --upgrade

# Run Django management commands
docker-compose exec web python manage.py collectstatic --noinput
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py analyze_photos --all
docker-compose exec web python manage.py analyze_videos --all

# Clean up orphaned files
docker-compose exec web python manage.py cleanup_unused_media

# Check system health
docker-compose exec web python manage.py check --deploy
```

---

## 📁 File Locations

```
photo_album/
├── Dockerfile                    # Original full version
├── Dockerfile.light             # CPU-only lightweight version ⭐
├── docker-compose.yml           # Full GPU configuration  
├── docker-compose.light.yml     # Lightweight configuration ⭐
├── docker-entrypoint.sh         # Container startup script
├── requirements.txt             # Full development requirements
├── requirements-docker.txt      # Lightweight Docker requirements
├── .env.production             # Production environment variables
└── docs/deployment/DOCKER.md   # This guide
```

---

## 🎯 Quick Decision Guide

**Choose Lightweight CPU if:**
- You're developing locally
- You have < 8GB RAM
- You don't have a GPU
- You want fast builds
- AI speed is not critical

**Choose Full GPU if:**
- You have a production GPU server
- You process 100+ photos daily
- AI performance is critical
- You have 16GB+ RAM
- You have NVIDIA GPU with CUDA

**Choose Minimal if:**
- You're testing infrastructure only
- You don't need AI features
- You're doing UI/UX development
- You have very limited resources

---

## 🎉 Success Indicators

Your Docker deployment is successful when:

```bash
# All containers are running
$ docker-compose ps
NAME                STATUS
photo_album-db      Up (healthy)
photo_album-redis   Up
photo_album-web     Up (healthy)

# Application responds
$ curl http://localhost:8000/
HTTP/1.1 200 OK

# Database is accessible
$ docker-compose exec db psql -U dniel -d photo_album -c "SELECT COUNT(*) FROM auth_user;"
 count 
-------
     1

# Logs show no errors
$ docker-compose logs web | grep ERROR
(no output = success)
```

---

## 💡 Key Takeaways

1. **Start with lightweight** - `docker-compose.light.yml` is perfect for 90% of use cases
2. **Backup regularly** - Automate database and media backups
3. **Monitor resources** - Use `docker stats` and application monitoring
4. **Security first** - Change default passwords, use HTTPS, keep updated
5. **Test before production** - Always test in development environment first

---

**Need Help?**
- Check [Deployment Checklist](DEPLOYMENT_CHECKLIST.md) for pre-flight checks
- See [Production Deployment Guide](DEPLOYMENT_SYSTEMD.md) for systemd setup
- Review [Admin Guides](../admin-guides/) for configuration details

**Version:** 1.2.0  
**Last Updated:** October 18, 2025
