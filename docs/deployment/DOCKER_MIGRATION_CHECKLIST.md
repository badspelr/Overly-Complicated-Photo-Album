# Migration to Docker - Checklist

This checklist will guide you through migrating from the virtual environment setup to a fully containerized Docker deployment.

## Pre-Migration Checklist

- [ ] Ensure Docker and Docker Compose are installed
  ```bash
  docker --version    # Should be 20.10+
  docker-compose --version  # Should be 2.0+
  ```

- [ ] Backup current database
  ```bash
  pg_dump photo_album > backup_$(date +%Y%m%d_%H%M%S).sql
  ```

- [ ] Backup media files
  ```bash
  tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/
  ```

- [ ] Note current environment variables from existing `.env` file
  ```bash
  cat .env > .env.backup
  ```

- [ ] Stop all running services
  ```bash
  pkill -f "python manage.py runserver"
  pkill -f "celery.*photo_album"
  ```

## Migration Steps

### Step 1: Configure Docker Environment

- [ ] Copy the example environment file
  ```bash
  cp .env.example .env
  ```

- [ ] Update `.env` with your values:
  - [ ] `SECRET_KEY` - Generate new: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
  - [ ] `DB_NAME`, `DB_USER`, `DB_PASSWORD` - Match your current database or use defaults
  - [ ] `HF_TOKEN` - Your Hugging Face token (if using AI features)
  - [ ] `DEBUG` - Set to `False` for production
  - [ ] `ALLOWED_HOSTS` - Add your domain(s)
  - [ ] Email settings (if configured)
  - [ ] Superuser credentials (optional, for auto-creation)

### Step 2: Build Docker Images

- [ ] Build all containers
  ```bash
  docker-compose build
  ```
  
  *This will take 5-10 minutes the first time*

- [ ] Verify images were created
  ```bash
  docker images | grep photo_album
  ```

### Step 3: Start Services

- [ ] Start all services
  ```bash
  docker-compose up -d
  ```

- [ ] Check that all services are running
  ```bash
  docker-compose ps
  ```
  
  *All services should show "Up (healthy)" status*

- [ ] View logs to ensure no errors
  ```bash
  docker-compose logs -f
  ```
  
  *Press Ctrl+C to exit logs*

### Step 4: Database Migration

Choose **Option A** if starting fresh, or **Option B** if migrating existing data:

#### Option A: Fresh Database

- [ ] Migrations are run automatically, verify:
  ```bash
  docker-compose logs web | grep "Running migrations"
  ```

- [ ] Create superuser
  ```bash
  docker-compose exec web python manage.py createsuperuser
  ```

#### Option B: Migrate Existing Data

- [ ] Stop the database container
  ```bash
  docker-compose stop db
  ```

- [ ] Import your backup
  ```bash
  cat backup_YYYYMMDD_HHMMSS.sql | docker-compose exec -T db psql -U postgres photo_album
  ```

- [ ] Restart all services
  ```bash
  docker-compose restart
  ```

- [ ] Run migrations to ensure schema is up-to-date
  ```bash
  docker-compose exec web python manage.py migrate
  ```

### Step 5: Verify Application

- [ ] Access web interface at http://localhost:8000
- [ ] Log in with admin credentials
- [ ] Access admin panel at http://localhost:8000/admin
- [ ] Upload a test photo
- [ ] Verify photo processing (check Celery logs)
  ```bash
  docker-compose logs celery-worker | grep "process_media"
  ```
- [ ] Test search functionality
- [ ] Check that scheduled tasks are configured
  ```bash
  docker-compose exec celery-beat celery -A photo_album inspect scheduled
  ```

### Step 6: Performance Testing

- [ ] Monitor resource usage
  ```bash
  docker stats
  ```

- [ ] Check response times
  ```bash
  curl -o /dev/null -s -w 'Total: %{time_total}s\n' http://localhost:8000/
  ```

- [ ] Verify logs are being written
  ```bash
  ls -lh logs/
  ```

### Step 7: Clean Up Old Environment

**Only after verifying everything works!**

- [ ] Stop old PostgreSQL service (if running locally)
  ```bash
  sudo systemctl stop postgresql
  sudo systemctl disable postgresql  # Optional: prevent auto-start
  ```

- [ ] Stop old Redis service (if running locally)
  ```bash
  sudo systemctl stop redis
  sudo systemctl disable redis  # Optional
  ```

- [ ] Remove virtual environment
  ```bash
  rm -rf venv/
  ```

- [ ] Remove old helper scripts (now obsolete)
  ```bash
  # These are no longer needed with Docker
  # rm start_celery.sh  # Keep for reference or delete
  ```

- [ ] Update development documentation
  - [ ] Update README.md to reference Docker setup
  - [ ] Update INSTALL.md with Docker instructions

## Post-Migration Verification

### Daily Operations

- [ ] Test starting services
  ```bash
  docker-compose down
  docker-compose up -d
  docker-compose ps  # All should be healthy
  ```

- [ ] Test viewing logs
  ```bash
  docker-compose logs --tail=50 web
  docker-compose logs --tail=50 celery-worker
  ```

- [ ] Test running management commands
  ```bash
  docker-compose exec web python manage.py shell
  ```

### Backup Procedures

- [ ] Test database backup
  ```bash
  docker-compose exec db pg_dump -U postgres photo_album > test_backup.sql
  ```

- [ ] Test database restore
  ```bash
  docker-compose exec db psql -U postgres -d photo_album -c "SELECT count(*) FROM album_photo;"
  ```

### Development Workflow

- [ ] Make a test code change
- [ ] Rebuild and restart
  ```bash
  docker-compose build web
  docker-compose restart web
  ```
- [ ] Verify change is reflected

## Troubleshooting Common Issues

### Issue: Port Already in Use

**Solution**: Update ports in `.env`
```bash
WEB_PORT=8080
DB_PORT=5433
REDIS_PORT=6380
```

### Issue: Database Connection Refused

**Check**:
```bash
docker-compose ps db  # Should be "Up (healthy)"
docker-compose logs db | tail -20
docker-compose exec db pg_isready -U postgres
```

### Issue: Celery Worker Not Processing Tasks

**Check**:
```bash
docker-compose ps celery-worker
docker-compose logs celery-worker | tail -50
docker-compose exec celery-worker celery -A photo_album inspect active
```

### Issue: Permission Errors on Media/Static Files

**Solution**: Fix permissions on host
```bash
sudo chown -R $(whoami):$(whoami) media/ staticfiles/ logs/
chmod -R 755 media/ staticfiles/ logs/
```

### Issue: Out of Disk Space

**Check Docker disk usage**:
```bash
docker system df
```

**Clean up**:
```bash
docker system prune -a  # WARNING: Removes unused containers and images
```

## Rollback Plan

If something goes wrong and you need to rollback:

1. **Stop Docker services**
   ```bash
   docker-compose down
   ```

2. **Restore local PostgreSQL**
   ```bash
   sudo systemctl start postgresql
   createdb photo_album  # If needed
   psql photo_album < backup_YYYYMMDD_HHMMSS.sql
   ```

3. **Restore local Redis**
   ```bash
   sudo systemctl start redis
   ```

4. **Recreate virtual environment**
   ```bash
   python3.13 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Start application manually**
   ```bash
   python manage.py runserver
   ./start_celery.sh  # or manual celery commands
   ```

## Success Criteria

Migration is successful when:

- ✅ All 5 containers are running and healthy
- ✅ Web interface is accessible and responsive
- ✅ Can log in and perform all operations
- ✅ Media upload and AI processing works
- ✅ Celery tasks are processing
- ✅ Scheduled tasks are running (check at 2 AM UTC)
- ✅ Database queries work correctly
- ✅ Logs are being written to `./logs/`
- ✅ No errors in any service logs
- ✅ Old virtual environment removed

## Next Steps

After successful migration:

1. **Update documentation**
   - Add Docker commands to README
   - Update development guidelines
   - Document new deployment process

2. **Configure production settings**
   - Set up SSL/TLS certificates
   - Configure Nginx reverse proxy (optional)
   - Set up log rotation
   - Configure monitoring

3. **Set up CI/CD**
   - Automate Docker builds
   - Set up automated testing
   - Configure deployment pipelines

4. **Monitor performance**
   - Set up monitoring tools (Prometheus, Grafana)
   - Configure alerts
   - Review resource usage

## Reference

- Full Docker documentation: `docs/deployment/DOCKER_SETUP.md`
- Docker Compose file: `docker-compose.yml`
- Dockerfile: `Dockerfile`
- Entrypoint script: `docker-entrypoint.sh`

---

**Date Migrated**: _________________

**Migrated By**: _________________

**Notes**: _________________
