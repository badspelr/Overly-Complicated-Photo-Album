# Production Deployment Cheat Sheet

## 📋 Pre-Deployment Checklist

```bash
# Run readiness check
./scripts/check_production_ready.sh

# Required changes in .env:
SECRET_KEY='generate-new-50-char-random-string'
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_PASSWORD='strong-password-not-postgres123'
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

## 🚀 Deploy (3 Commands)

```bash
# 1. Build and push image
./scripts/deploy_to_production.sh

# 2. Copy to production
scp -r deploy_package user@server:~/photo_album

# 3. Deploy on server
ssh user@server
cd ~/photo_album && ./deploy.sh
```

## 🔧 First Time Setup

```bash
# Create superuser
docker-compose exec web python manage.py createsuperuser

# Test health
curl http://localhost:8000/health/
```

## 📊 Monitoring

```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f web
docker-compose logs -f celery-worker

# Check health
curl http://localhost:8000/health/
```

## 🔄 Update Application

```bash
# On dev machine
./scripts/deploy_to_production.sh  # Build and push new version

# On production
docker-compose pull
docker-compose up -d
docker-compose exec web python manage.py migrate
```

## 💾 Backup

```bash
# Manual backup
docker-compose exec -T db pg_dump -U postgres postgres > backup_$(date +%Y%m%d).sql

# Automated (add to crontab)
0 2 * * * cd ~/photo_album && docker-compose exec -T db pg_dump -U postgres postgres > /backups/backup_$(date +\%Y\%m\%d).sql
```

## 🔍 Troubleshooting

```bash
# Restart services
docker-compose restart

# Rebuild and restart
docker-compose up -d --build

# Check specific service
docker-compose logs service_name

# Fix permissions
sudo chown -R 1000:1000 media/ logs/
```

## 🔒 Security Quick Wins

```bash
# Firewall (Ubuntu/Debian)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# SSL with Certbot
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 📞 Emergency Commands

```bash
# Stop everything
docker-compose down

# Nuclear option (removes volumes - DANGEROUS)
docker-compose down -v

# Restore from backup
cat backup.sql | docker-compose exec -T db psql -U postgres postgres
```

## 📚 Documentation

- Full Guide: `docs/deployment/DOCKER.md` section 8
- Quick Start: `docs/deployment/PRODUCTION_QUICK_START.md`
- Troubleshooting: `docs/deployment/DOCKER.md` section 7
