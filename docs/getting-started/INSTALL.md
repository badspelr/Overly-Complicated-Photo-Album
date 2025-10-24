# Django Photo Album - Installation Guide

## Installation Methods

### Method 1: Docker (Recommended) 🐳

**No virtual environment needed!** Docker provides complete isolation and matches production exactly.

#### Prerequisites
- **Docker** - Latest version
- **Docker Compose** - Latest version
- **Git** - For cloning the repository

#### Installation Steps

```bash
# 1. Clone the repository
git clone <repository-url>
cd photo_album

# 2. Configure environment
cp .env.example .env
# Edit .env if needed (defaults work for development)

# 3. Start all services
docker-compose -f docker-compose.light.yml up -d

# 4. Create superuser
docker-compose -f docker-compose.light.yml exec web python manage.py createsuperuser

# 5. Access application
# Open: http://localhost:8000
```

**That's it!** PostgreSQL, Redis, Celery, and the web server are all running in isolated containers.

#### Why Docker?

- ✅ No virtual environment setup needed
- ✅ Automatic dependency isolation
- ✅ Matches production environment exactly
- ✅ One command starts everything
- ✅ No manual PostgreSQL/Redis setup
- ✅ Easy cleanup with `docker-compose down`

See [`docs/deployment/DOCKER.md`](../deployment/DOCKER.md) for complete Docker guide.

---

### Method 2: Local Development (Without Docker)

⚠️ **Only use this if Docker is not available.** This method requires manual setup of PostgreSQL, Redis, and Celery.

#### Prerequisites

Before installing Django Photo Album locally, ensure you have:

**Required Software:**
- **Python 3.11+** - The application requires Python 3.11 or higher
- **PostgreSQL 14+** - Database with pgvector extension support
- **Redis** - For caching, session storage, and Celery message broker
- **Git** - For cloning the repository

**Optional Components:**
- **NVIDIA GPU with CUDA** - For faster AI processing (optional, CPU works too)

**System Dependencies:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib redis-server git

# Fedora
sudo dnf install python3 python3-pip postgresql-server redis git

# Arch Linux
sudo pacman -Syu python python-pip postgresql redis git

# macOS (using Homebrew)
brew install python postgresql redis git

# Windows
# Install Python from python.org
# Install PostgreSQL from postgresql.org
# Install Redis from redis.io
```

#### Installation Steps

##### 1. Clone the Repository
```bash
git clone <repository-url>
cd photo_album
```

##### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

##### 3. Install Python Dependencies

There are two separate files for dependencies: one for production and one for development.

**For a production environment (running the application):**
```bash
pip install -r requirements.txt
```

**For a development environment (running tests, etc.):**
```bash
pip install -r requirements-dev.txt
```

### 4. Database Setup

#### PostgreSQL Installation and Configuration
```bash
# Install pgvector extension
sudo apt install postgresql-14-pgvector  # Ubuntu/Debian

# Create database and user
sudo -u postgres psql
```

```sql
-- In PostgreSQL shell
CREATE DATABASE photo_album;
CREATE USER photo_album_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE photo_album TO photo_album_user;

-- Connect to the database and enable extensions
\c photo_album
CREATE EXTENSION IF NOT EXISTS pgvector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
\q
```

### 5. Environment Configuration

Create a `.env` file in the project root:
```bash
cp .env.example .env  # If example exists, or create new file
```

Configure your `.env` file:
```env
# Database Configuration
DATABASE_URL=postgresql://photo_album_user:your_secure_password@localhost:5432/photo_album
DB_NAME=photo_album
DB_USER=photo_album_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Django Settings
SECRET_KEY=your-very-long-random-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# AI Configuration
AI_ENABLED=True
AI_MODEL_CACHE_DIR=./ai_models
AI_BATCH_SIZE=4
AI_MAX_WORKERS=2

# Media Storage
MEDIA_ROOT=./media
MEDIA_URL=/media/
```

### 6. Django Setup

#### Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Create Superuser
```bash
python manage.py createsuperuser
```

#### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 7. AI Model Setup (Optional but Recommended)

Download and initialize AI models for intelligent search:
```bash
# This will download BLIP and CLIP models (~2GB)
python manage.py shell -c "
from album.services.ai_analysis_service import AIAnalysisService
service = AIAnalysisService()
print('AI models initialized successfully')
"
```

### 8. Background Processing Setup (Celery)

Celery handles background AI processing tasks, allowing photos to be analyzed asynchronously without blocking uploads.

#### Development Setup

For development, you need to run **3 separate terminal processes**:

**Terminal 1: Django Server**
```bash
python manage.py runserver 0.0.0.0:8000
```

**Terminal 2: Celery Worker**
```bash
celery -A photo_album worker --loglevel=info
```

**Terminal 3: Celery Beat (Scheduler)**
```bash
celery -A photo_album beat --loglevel=info
```

#### Production Setup

For production, use the automated systemd setup:

```bash
# One-command setup (creates and starts systemd services)
sudo ./deployment/setup_celery_systemd.sh
```

This will:
- ✅ Create systemd service files
- ✅ Enable auto-start on boot
- ✅ Start Celery worker and beat scheduler
- ✅ Set up logging to `/var/log/celery/`

**Verify Celery is running:**
```bash
# Check service status
sudo systemctl status photo-album-celery-worker
sudo systemctl status photo-album-celery-beat

# Test worker connection
celery -A photo_album inspect ping
```

**Configure AI Processing:**
- Visit `/ai-settings/` (admin only) to configure automatic processing
- Or edit settings in Django admin: `/admin/album/aiprocessingsettings/`

> 📚 **See [Celery Guide](../admin-guides/CELERY.md)** for detailed configuration and troubleshooting

### 9. Start the Application

#### Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

#### Production Setup (using Gunicorn)
```bash
pip install gunicorn
gunicorn photo_album.wsgi:application --bind 0.0.0.0:8000
```

## Verification

### Test the Installation
1. Navigate to `http://localhost:8000`
2. Log in with your superuser credentials
3. Create a test album
4. Upload a few photos
5. Test the AI search functionality

### Run System Checks
```bash
python manage.py check
python manage.py test album.tests
```

## Troubleshooting

### Common Issues

#### pgvector Extension Not Found
```bash
# Install pgvector for your PostgreSQL version
sudo apt install postgresql-14-pgvector

# Or compile from source
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

#### AI Models Download Issues
```bash
# Clear model cache and retry
rm -rf ./ai_models
python manage.py shell -c "
from album.services.ai_analysis_service import AIAnalysisService
service = AIAnalysisService()
"
```

#### Permission Issues with Media Files
```bash
# Ensure proper permissions
chmod -R 755 media/
chown -R $USER:$USER media/
```

#### Redis Connection Issues
```bash
# Check Redis status
redis-cli ping  # Should return PONG

# Start Redis if not running
sudo systemctl start redis-server  # Linux
brew services start redis  # macOS
```

### Performance Optimization

#### Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_photo_album_id ON album_photo(album_id);
CREATE INDEX IF NOT EXISTS idx_photo_ai_processed ON album_photo(ai_processed);
CREATE INDEX IF NOT EXISTS idx_photo_embedding ON album_photo USING hnsw (embedding vector_cosine_ops);
```

#### AI Processing
```bash
# Process existing photos with AI (using local BLIP models)
python manage.py analyze_photos

# Process videos (requires thumbnails to be generated first)
python manage.py generate_video_thumbnails
python manage.py analyze_videos

# Generate embeddings for search
python manage.py generate_embeddings
```

**Web Interface Access:**
- Photo AI Processing: `http://localhost:8000/process-photos-ai/`
- Video AI Processing: `http://localhost:8000/process-videos-ai/`
- Requires Album Admin or Site Admin permissions

## Docker Installation (Alternative)

If you prefer Docker deployment:

```dockerfile
# Create Dockerfile (basic example)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "photo_album.wsgi:application", "--bind", "0.0.0.0:8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/photo_album
      - REDIS_URL=redis://redis:6379/0
  
  db:
    image: pgvector/pgvector:pg14
    environment:
      - POSTGRES_DB=photo_album
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine

volumes:
  postgres_data:
```

## Deployment Considerations

### Running on a Server Without a GPU

The application is designed to be fully functional on a standard cloud server without a dedicated GPU. The AI features will automatically detect the absence of a GPU and fall back to using the CPU.

**Performance Implications:**
- **Core Application:** The web server, database, and caching are entirely CPU-based and will not be affected.
- **AI Processing:** AI tasks (image analysis, embedding generation) are significantly faster on a GPU. On a CPU, these tasks will be slower. The initial processing of a large library may take a considerable amount of time, and analysis of new uploads will have a noticeable delay.

**Recommendations for a CPU-Only Environment:**
1.  **Background Processing:** Use the provided management commands (`analyze_photos`, `generate_embeddings`) to process your media. It is highly recommended to run these commands as background tasks or cron jobs during off-peak hours to avoid slowing down the web server for users.
2.  **Server Resources:** Ensure your server has a capable multi-core CPU and sufficient RAM (8GB is a good starting point, 16GB+ is recommended for large libraries) to handle the AI models.

## Next Steps

After successful installation:
1. Read the [Overview and Features](OVERVIEW.md) document
2. Review the [User Manual](../user-guides/USER_MANUAL.md) for detailed usage instructions
3. **Set up [Celery Background Processing](../admin-guides/CELERY.md)** for automatic AI analysis
4. Consult the [Management Commands Guide](../admin-guides/MANAGEMENT_COMMANDS.md) for setup and maintenance tasks
5. Configure AI processing settings at `/ai-settings/` (admin only)
6. Set up regular backups of your database and media files

> ⚠️ **Important:** Without Celery, photos will not be automatically analyzed by AI. You'll need to manually run `python manage.py analyze_photos` to process uploaded photos.

## Support

For installation issues:
- Check the troubleshooting section above
- Review Django and PostgreSQL logs
- Ensure all prerequisites are properly installed
- Verify environment variables are correctly set