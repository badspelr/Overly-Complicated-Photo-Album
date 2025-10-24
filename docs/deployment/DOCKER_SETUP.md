# Docker Setup Guide

This guide explains how to run the Photo Album application using Docker containers, eliminating the need for a virtual environment.

## Prerequisites

- Docker (version 20.10 or later)
- Docker Compose (version 2.0 or later)

## Quick Start

### 1. Copy and Configure Environment File

```bash
cp .env.example .env
```

Edit `.env` and update the following required values:
- `SECRET_KEY`: Generate a new secret key (use `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `HF_TOKEN`: Your Hugging Face API token (if using AI features)
- Database credentials (optional, defaults are provided)

### 2. Build and Start All Services

```bash
# Build the Docker images
docker-compose build

# Start all services (db, redis, web, celery-worker, celery-beat)
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Create Superuser (First Time Only)

```bash
docker-compose exec web python manage.py createsuperuser
```

Or set these environment variables in `.env` for automatic creation:
```
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=your-secure-password
```

### 4. Access the Application

- **Web Interface**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

## Services Overview

The application runs as 5 separate containers:

| Service | Description | Port |
|---------|-------------|------|
| **db** | PostgreSQL with pgvector | 5432 |
| **redis** | Redis for Celery broker | 6379 |
| **web** | Django application (Gunicorn) | 8000 |
| **celery-worker** | Background task processor | - |
| **celery-beat** | Scheduled task scheduler | - |

## Common Commands

### Start/Stop Services

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data!)
docker-compose down -v

# Restart a specific service
docker-compose restart web
docker-compose restart celery-worker
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f celery-worker
docker-compose logs -f celery-beat

# Last 100 lines
docker-compose logs --tail=100 web
```

### Database Management

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create database backup
docker-compose exec db pg_dump -U postgres photo_album > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U postgres photo_album

# Access database shell
docker-compose exec db psql -U postgres photo_album
```

### Django Management Commands

```bash
# Run any Django management command
docker-compose exec web python manage.py <command>

# Examples:
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py dbshell
docker-compose exec web python manage.py collectstatic
docker-compose exec web python manage.py createsuperuser
```

### Celery Management

```bash
# View Celery worker status
docker-compose exec celery-worker celery -A photo_album inspect active

# View scheduled tasks
docker-compose exec celery-beat celery -A photo_album inspect scheduled

# Restart workers (to reload code changes)
docker-compose restart celery-worker celery-beat
```

### Container Shell Access

```bash
# Access web container shell
docker-compose exec web bash

# Access database container shell
docker-compose exec db bash

# Run Python shell in Django context
docker-compose exec web python manage.py shell
```

## Development Workflow

### Code Changes

When you make code changes:

```bash
# Rebuild and restart affected services
docker-compose build web celery-worker celery-beat
docker-compose restart web celery-worker celery-beat
```

### Installing New Python Packages

1. Add package to `requirements.txt`
2. Rebuild the containers:
```bash
docker-compose build
docker-compose up -d
```

### Database Schema Changes

```bash
# Create migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate
```

## Volumes and Data Persistence

Data is persisted in the following locations:

- **Database**: Docker volume `photo_album_postgres_data`
- **Redis**: Docker volume `photo_album_redis_data`
- **Media Files**: `./media` directory on host
- **Static Files**: `./staticfiles` directory on host
- **Logs**: `./logs` directory on host

### Backup Data

```bash
# Backup database
docker-compose exec db pg_dump -U postgres photo_album > backup_$(date +%Y%m%d).sql

# Backup media files
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
```

## Troubleshooting

### Container Won't Start

```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs web

# Check health status
docker inspect photo_album_web --format='{{.State.Health.Status}}'
```

### Database Connection Issues

```bash
# Ensure database is healthy
docker-compose ps db

# Test database connection
docker-compose exec db pg_isready -U postgres

# View database logs
docker-compose logs db
```

### Redis Connection Issues

```bash
# Test Redis connection
docker-compose exec redis redis-cli ping

# Should return: PONG
```

### Port Already in Use

If ports 5432, 6379, or 8000 are already in use, update `.env`:

```
WEB_PORT=8080
DB_PORT=5433
REDIS_PORT=6380
```

### Clear Everything and Start Fresh

```bash
# Stop and remove everything
docker-compose down -v

# Remove images
docker-compose rm -f
docker rmi photo_album-web

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

## Production Deployment

### Environment Configuration

For production, update `.env`:

```bash
DEBUG=False
SECRET_KEY=<generate-strong-secret-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Use strong database credentials
DB_PASSWORD=<strong-password>

# Configure email
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=<email-password>
```

### Add Nginx Reverse Proxy (Optional)

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./staticfiles:/app/staticfiles
      - ./media:/app/media
    depends_on:
      - web
    networks:
      - photo_album_network
```

Run with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Migrating from Virtual Environment

If you were previously running with a virtual environment:

1. **Stop local services**:
   ```bash
   # Stop Django dev server, Celery, etc.
   pkill -f "python manage.py runserver"
   pkill -f "celery.*photo_album"
   ```

2. **Backup your database** (if using local PostgreSQL):
   ```bash
   pg_dump photo_album > backup_before_docker.sql
   ```

3. **Update database credentials** in `.env` to match Docker service

4. **Start Docker services**:
   ```bash
   docker-compose up -d
   ```

5. **Import your data** (if needed):
   ```bash
   cat backup_before_docker.sql | docker-compose exec -T db psql -U postgres photo_album
   ```

6. **Verify everything works**, then remove the virtual environment:
   ```bash
   rm -rf venv/
   ```

## Monitoring

### Health Checks

All services have health checks configured. Check status:

```bash
docker-compose ps
```

### View Resource Usage

```bash
docker stats
```

### Log Rotation

Logs are written to `./logs/` directory. Configure log rotation on your host system.

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review environment variables in `.env`
- Ensure all services are healthy: `docker-compose ps`
