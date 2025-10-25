# Getting Started with Docker - Step by Step

Follow these exact commands to get your Photo Album application running with Docker.

## Prerequisites Check

```bash
# Check Docker is installed
docker --version
# Expected: Docker version 20.10.x or higher

# Check Docker Compose is installed  
docker-compose --version
# Expected: Docker Compose version 2.x.x or higher

# Check Docker is running
docker ps
# Should show running containers or empty table (not an error)
```

---

## Step 1: Configure Environment

```bash
# Navigate to project directory
cd photo_album

# Copy example environment file
cp .env.example .env

# Generate a new SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Copy the output

# Edit .env and paste the SECRET_KEY
nano .env
# or
vim .env

# Update these required values in .env:
# - SECRET_KEY=<paste-generated-key-here>
# - HF_TOKEN=<your-huggingface-token>
# - DB_PASSWORD=<choose-a-strong-password>
# - DJANGO_SUPERUSER_USERNAME=admin
# - DJANGO_SUPERUSER_EMAIL=admin@example.com
# - DJANGO_SUPERUSER_PASSWORD=<choose-admin-password>

# Save and exit (Ctrl+X, then Y, then Enter for nano)
```

---

## Step 2: Build Docker Images

```bash
# Build all services (this takes 5-10 minutes first time)
docker-compose build

# You should see progress bars and "Successfully tagged" messages
```

---

## Step 3: Start All Services

```bash
# Start all containers in detached mode (background)
docker-compose up -d

# Expected output:
# Creating network "photo_album_network" ... done
# Creating volume "photo_album_postgres_data" ... done
# Creating volume "photo_album_redis_data" ... done
# Creating photo_album_db ... done
# Creating photo_album_redis ... done
# Creating photo_album_web ... done
# Creating photo_album_celery_worker ... done
# Creating photo_album_celery_beat ... done
```

---

## Step 4: Verify Services

```bash
# Check all containers are running and healthy
docker-compose ps

# You should see 5 services all with "Up" status:
# - photo_album_db (Up and healthy)
# - photo_album_redis (Up and healthy)
# - photo_album_web (Up and healthy)
# - photo_album_celery_worker (Up)
# - photo_album_celery_beat (Up)
```

---

## Step 5: Watch Startup Logs

```bash
# View logs from all services
docker-compose logs -f

# You should see:
# - Database migrations running
# - Static files collected
# - Gunicorn starting
# - Celery workers connecting
# - No ERROR messages

# Press Ctrl+C to exit log view (services keep running)
```

---

## Step 6: Access the Application

```bash
# Open in browser
xdg-open http://localhost:8000
# or manually navigate to: http://localhost:8000

# Admin panel
xdg-open http://localhost:8000/admin
# Log in with credentials from .env file
```

---

## Step 7: Create Superuser (If Not Auto-Created)

```bash
# If you didn't set superuser env vars, create one now:
docker-compose exec web python manage.py createsuperuser

# Follow the prompts:
# Username: admin
# Email: admin@example.com
# Password: (enter secure password)
# Password (again): (confirm)
```

---

## Step 8: Test Upload and Processing

1. **Log in** to http://localhost:8000
2. **Create an album** (if prompted)
3. **Upload a photo**
4. **Watch Celery logs** to see AI processing:
   ```bash
   docker-compose logs -f celery-worker
   ```
5. **Verify photo appears** with AI-generated tags

---

## Verify Everything is Working

```bash
# 1. Check all services healthy
docker-compose ps

# 2. Check web server responding
curl -I http://localhost:8000
# Should return: HTTP/1.1 200 OK

# 3. Check database connection
docker-compose exec db psql -U postgres photo_album -c "SELECT COUNT(*) FROM django_migrations;"
# Should return a count (number of migrations)

# 4. Check Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG

# 5. Check Celery worker
docker-compose exec celery-worker celery -A photo_album inspect active
# Should return worker status

# 6. Check Celery beat scheduler
docker-compose exec celery-beat celery -A photo_album inspect scheduled
# Should return scheduled tasks (daily at 02:00 and 02:30)
```

---

## Common First-Run Commands

```bash
# View specific service logs
docker-compose logs -f web
docker-compose logs -f celery-worker
docker-compose logs -f db

# Run Django management commands
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py showmigrations
docker-compose exec web python manage.py check

# Access database shell
docker-compose exec db psql -U postgres photo_album

# Restart a specific service
docker-compose restart web
docker-compose restart celery-worker
```

---

## Stop Services (When Done)

```bash
# Stop all services (data is preserved)
docker-compose down

# To remove everything including data:
# docker-compose down -v
# WARNING: This deletes the database!
```

---

## Restart Services

```bash
# Start again
docker-compose up -d

# Services will:
# - Use existing data
# - Run any new migrations
# - Restart where they left off
```

---

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 8000
sudo lsof -i :8000

# Option 1: Stop the conflicting service
# Option 2: Change port in .env
echo "WEB_PORT=8080" >> .env
docker-compose down
docker-compose up -d
# Access at http://localhost:8080
```

### Services Not Healthy

```bash
# Check specific service logs
docker-compose logs db
docker-compose logs redis
docker-compose logs web

# Common fixes:
docker-compose restart <service-name>
# or
docker-compose down
docker-compose up -d
```

### Database Connection Issues

```bash
# Verify database is ready
docker-compose exec db pg_isready -U postgres

# Check database exists
docker-compose exec db psql -U postgres -l | grep photo_album

# Recreate database (if needed)
docker-compose exec db psql -U postgres -c "CREATE DATABASE photo_album;"
docker-compose restart web
```

### Permission Errors

```bash
# Fix file permissions
sudo chown -R $USER:$USER media/ staticfiles/ logs/
chmod -R 755 media/ staticfiles/ logs/
```

---

## Success! 🎉

If you can:
- ✅ Access http://localhost:8000
- ✅ Log in to admin panel
- ✅ Upload a photo
- ✅ See it processed by Celery
- ✅ Search for photos

Then your Docker setup is working perfectly!

---

## Next: Clean Up Old Environment

**ONLY after verifying everything works:**

```bash
# Stop old services (if running)
pkill -f "python manage.py runserver"
pkill -f "celery.*photo_album"

# Remove virtual environment
rm -rf venv/

# Optional: Stop local PostgreSQL/Redis
sudo systemctl stop postgresql
sudo systemctl stop redis
```

---

## Quick Reference

**Start**: `docker compose up -d`  
**Stop**: `docker compose down`  
**Logs**: `docker compose logs -f`  
**Status**: `docker compose ps`  
**Shell**: `docker compose exec web bash`  
**Django**: `docker compose exec web python manage.py <command>`

**Full docs**: See `docs/deployment/DOCKER_SETUP.md`

---

**Need help?** Check logs first: `docker compose logs -f`
