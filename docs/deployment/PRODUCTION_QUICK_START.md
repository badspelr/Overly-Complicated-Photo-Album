# Production Deployment Quick Start

**5-minute guide to deploy Photo Album to production if you already have it running in development.**

## Prerequisites ✓
- [ ] Photo Album working in Docker development environment
- [ ] Production server with Docker and Docker Compose installed
- [ ] Domain name pointed to production server (optional but recommended)

## Quick Deploy (3 Steps)

### Step 1: Prepare Image (On Dev Machine)
```bash
# Tag your working image
docker tag photo_album-web:latest your-registry.com/photo_album:v1.0

# Push to registry (Docker Hub, GHCR, etc.)
docker push your-registry.com/photo_album:v1.0
```

### Step 2: Copy Config (On Dev Machine)
```bash
# Copy files to production
scp .env docker-compose.light.yml user@production-server:~/photo_album/
```

### Step 3: Deploy (On Production Server)
```bash
cd ~/photo_album

# Update .env for production
nano .env  # Change: SECRET_KEY, ALLOWED_HOSTS, DB_PASSWORD

# Update docker-compose.light.yml image reference
nano docker-compose.light.yml  # Change build: . to image: your-registry.com/photo_album:v1.0

# Start services
docker-compose -f docker-compose.light.yml up -d

# Initial setup (first time only)
docker-compose -f docker-compose.light.yml exec web python manage.py migrate
docker-compose -f docker-compose.light.yml exec web python manage.py collectstatic --noinput
docker-compose -f docker-compose.light.yml exec web python manage.py createsuperuser
```

**Done! Access at http://your-server-ip:8000**

---

## Critical Production Settings

### Environment Variables (.env)
```bash
# Generate new secret key
SECRET_KEY='generate-new-random-50-char-string-here'

# Your domain
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,123.45.67.89

# Strong database password
DB_PASSWORD=use-strong-password-here-not-postgres123

# Your domain with protocol
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Disable debug
DEBUG=False
```

### Security Checklist
- [ ] Changed `SECRET_KEY` from default
- [ ] Changed `DB_PASSWORD` from `postgres123`
- [ ] Set `DEBUG=False`
- [ ] Updated `ALLOWED_HOSTS` with your domain
- [ ] Updated `CSRF_TRUSTED_ORIGINS` with your domain
- [ ] Firewall configured (only 80/443 exposed)
- [ ] SSL certificate installed (see SSL Setup below)

---

## Optional: SSL Setup (Recommended)

### Using Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate (stops nginx temporarily)
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Add nginx reverse proxy
docker-compose -f docker-compose.prod.yml up -d
```

See `DOCKER.md` section 8 for full nginx configuration.

---

## Health Check

```bash
# Check services
docker-compose -f docker-compose.light.yml ps

# Check health endpoint
curl http://localhost:8000/health/

# Expected response:
# {"status": "healthy", "timestamp": "2024-10-18T12:34:56.789Z"}

# Check logs
docker-compose -f docker-compose.light.yml logs web
docker-compose -f docker-compose.light.yml logs celery-worker
```

---

## Backup Setup

```bash
# Create backup directory
sudo mkdir -p /backups/photo_album

# Add to crontab (daily 2 AM backup)
sudo crontab -e

# Add this line:
0 2 * * * cd /home/user/photo_album && docker-compose -f docker-compose.light.yml exec -T db pg_dump -U postgres postgres > /backups/photo_album/backup_$(date +\%Y\%m\%d).sql
```

---

## Update Procedure

```bash
# On dev machine: build and push new version
docker tag photo_album-web:latest your-registry.com/photo_album:v1.1
docker push your-registry.com/photo_album:v1.1

# On production: pull and restart
cd ~/photo_album
docker-compose -f docker-compose.light.yml pull
docker-compose -f docker-compose.light.yml up -d
docker-compose -f docker-compose.light.yml exec web python manage.py migrate
docker-compose -f docker-compose.light.yml exec web python manage.py collectstatic --noinput
```

---

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose -f docker-compose.light.yml logs

# Restart services
docker-compose -f docker-compose.light.yml restart
```

### Database connection errors
```bash
# Check database is running
docker-compose -f docker-compose.light.yml ps db

# Check database logs
docker-compose -f docker-compose.light.yml logs db
```

### Permission errors
```bash
# Fix media/logs permissions
sudo chown -R 1000:1000 media/ logs/
```

### Out of memory
```bash
# Check resource usage
docker stats

# See DOCKER.md section 5 for optimization
```

---

## Support

- Full Documentation: `docs/deployment/DOCKER.md`
- Deployment Checklist: `docs/deployment/DEPLOYMENT_CHECKLIST.md`
- Troubleshooting: `docs/deployment/DOCKER.md` section 7
