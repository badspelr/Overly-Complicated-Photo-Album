
# Docker Quick Reference

Quick command reference for running Photo Album with Docker.

## Production Deployment

### Standard (CPU-only)
```bash
docker compose -f docker-compose.prod.yml up -d
```

### With GPU Support (Optional)
```bash
# If you have NVIDIA GPU + drivers + Container Toolkit
docker compose -f docker-compose.prod.yml -f docker-compose.gpu.yml up -d
```

> **Note:** GPU support is optional. See [GPU_SUPPORT.md](GPU_SUPPORT.md) for details.

## Essential Commands

### Start/Stop
```bash
docker-compose up -d          # Start all services
docker-compose down           # Stop all services
docker-compose restart        # Restart all services
docker-compose ps             # View status
```

### Logs
```bash
docker-compose logs -f                    # All services (follow)
docker-compose logs -f web                # Web service only
docker-compose logs --tail=100 celery-worker  # Last 100 lines
```

### Django Commands
```bash
docker-compose exec web python manage.py <command>

# Common examples:
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py collectstatic
```

### Database
```bash
# Backup
docker-compose exec db pg_dump -U postgres photo_album > backup.sql

# Restore
cat backup.sql | docker-compose exec -T db psql -U postgres photo_album

# Shell access
docker-compose exec db psql -U postgres photo_album
```

### Celery
```bash
# View active tasks
docker-compose exec celery-worker celery -A photo_album inspect active

# View scheduled tasks
docker-compose exec celery-beat celery -A photo_album inspect scheduled

# Restart workers
docker-compose restart celery-worker celery-beat
```

### Rebuild After Code Changes
```bash
docker-compose build              # Rebuild all
docker-compose build web          # Rebuild specific service
docker-compose up -d --build      # Rebuild and restart
```

### Shell Access
```bash
docker-compose exec web bash      # Web container shell
docker-compose exec db bash       # Database container shell
```

### Clean Up
```bash
docker-compose down -v            # Stop and remove volumes (deletes data!)
docker system prune -a            # Remove unused Docker resources
```

## Service URLs

- **Web App**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **Database**: localhost:5432
- **Redis**: localhost:6379

## File Locations

- **Media**: `./media/`
- **Static**: `./staticfiles/`
- **Logs**: `./logs/`
- **Config**: `.env`

## Troubleshooting

```bash
# Check health
docker-compose ps

# View all logs
docker-compose logs

# Restart specific service
docker-compose restart web

# Check resource usage
docker stats

# Fix permissions
sudo chown -R $USER:$USER media/ staticfiles/ logs/
```

## Initial Setup

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env with your values
nano .env

# 3. Build and start
docker-compose build
docker-compose up -d

# 4. Create superuser
docker-compose exec web python manage.py createsuperuser

# 5. Access app
open http://localhost:8000
```

---

For full documentation see: `docs/deployment/DOCKER_SETUP.md`
