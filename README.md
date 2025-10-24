# Django Photo Album

> Modern, AI-powered photo management system built with Django 5.2

[![Django](https://img.shields.io/bad## 📚 Documentation

- **[Quick Start Guide](docs/getting-started/INSTALL.md)** - Get up and running quickly
- **[Docker Setup](docs/deployment/DOCKER.md)** - Detailed Docker deployment guide  
- **[Nginx Setup](docs/deployment/NGINX_SETUP.md)** - Production Nginx configuration with SSL
- **[Virtual Domains Setup](docs/deployment/VIRTUAL_DOMAINS_SETUP.md)** - Multiple domains on one server
- **[Production Deployment](docs/deployment/PRODUCTION_QUICK_START.md)** - Deploy to production servers
- **[User Manual](docs/user-guides/USER_MANUAL.md)** - Complete feature documentation
- **[Admin Guide](docs/admin-guides/ADMIN_GUIDE_AI_SETTINGS.md)** - AI processing and admin features
- **[API Documentation](docs/technical/API.md)** - REST API reference

## 🤝 Contributingn.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

- 🤖 **AI-Powered Search** - Natural language photo search using CLIP and BLIP models
- 📸 **Smart Organization** - Albums, categories, tags, and custom collections
- 🚀 **Auto-Processing** - Automatic AI analysis on upload with background task queue
- 🔍 **Hybrid Search** - Combines semantic AI search with traditional text search
- 🎨 **Modern UI** - Responsive design with Material Design components
- 🔒 **Privacy-First** - Private albums, secure sharing, GDPR-compliant
- 📱 **Mobile-Optimized** - Works seamlessly on all devices
- ⚡ **High Performance** - Vector search, Redis caching, GPU acceleration

## 🚀 Quick Start

### Option 1: Using Pre-built Docker Image (Fastest) 🚀

Pull and run the pre-built image from Docker Hub:

```bash
# Clone the repository
git clone https://github.com/yourusername/photo-album.git
cd photo-album

# Configure environment
cp .env.example .env
nano .env  # Edit with your settings

# Add your Docker Hub username to .env
echo "DOCKER_USERNAME=yourusername" >> .env

# Pull and start (no build needed!)
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Run setup
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### Option 2: Build From Source (Development) 🐳

Build the Docker image locally from source:

```bash
# Clone the repository
git clone https://github.com/yourusername/photo-album.git
cd photo-album

# Configure environment
cp .env.example .env
nano .env  # Edit with your settings (SECRET_KEY, DB_PASSWORD, etc.)

# Start all services (web, database, Redis, and Celery workers)
docker-compose up -d

# Run database migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

Visit `http://localhost:8000` and start uploading photos!

**✨ AI features work automatically** - Celery worker handles background processing for face detection, smart search, and more.

---

## ⚠️ CRITICAL: Production Deployment

**Before deploying to production, you MUST configure these security settings:**

```bash
# In your .env file:
DEBUG=False                    # ✅ REQUIRED
SECURE_SSL_REDIRECT=True       # ✅ REQUIRED
SESSION_COOKIE_SECURE=True     # ✅ REQUIRED
CSRF_COOKIE_SECURE=True        # ✅ REQUIRED
```

**Without these settings, your deployment is NOT secure.**

📋 **See:** [Production Security Checklist](docs/deployment/PRODUCTION_SECURITY_CHECKLIST.md) for complete deployment guide.

---

### 🐳 Docker Compose Files

Different compose files for different use cases:

- **`docker-compose.yml`** - Development (default)
  - Code mounted as volumes for live editing
  - No rebuild needed when you change Python files
  - Use: `docker-compose up -d`

- **`docker-compose.prod.yml`** - Production
  - Code baked into image (more secure)
  - Requires rebuild for code changes
  - Use: `docker-compose -f docker-compose.prod.yml up -d`

- **`docker-compose.light.yml`** - Lightweight/CPU-only
  - No GPU dependencies
  - Smaller image size
  - Use: `docker-compose -f docker-compose.light.yml up -d`

- **`docker-compose.nginx.yml`** - Production with Nginx
  - Includes Nginx reverse proxy
  - SSL/TLS support with Let's Encrypt
  - See [NGINX_SETUP.md](docs/deployment/NGINX_SETUP.md)

### Local Development (Without Docker)

⚠️ **Note:** Docker method is strongly recommended as it matches production environment exactly.

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server (requires PostgreSQL, Redis, Celery - set up separately)
python manage.py runserver
```

## 📚 Documentation

**Complete documentation is available in the [`docs/`](docs/) directory:**

- **[Getting Started](docs/getting-started/)** - Installation, overview, and setup
- **[User Guides](docs/user-guides/)** - How to use the application
- **[Admin Guides](docs/admin-guides/)** - AI settings, Celery configuration
- **[Deployment](docs/deployment/)** - Production deployment guides
- **[Technical Docs](docs/technical/)** - Implementation details

**Quick Links:**
- 📖 [Documentation Hub](docs/README.md) - Complete documentation index
- 🎯 [Feature Overview](docs/getting-started/OVERVIEW.md) - All features explained
- 💻 [Installation Guide](docs/getting-started/INSTALL.md) - Complete setup instructions
- 👤 [User Manual](docs/user-guides/USER_MANUAL.md) - End-user guide
- 📝 [Changelog](CHANGELOG.md) - Version history

## 🛠️ Technology Stack

- **Backend:** Django 5.2, Python 3.11+
- **Database:** PostgreSQL 15+ with pgvector extension
- **Cache/Queue:** Redis, Celery
- **AI Models:** CLIP (OpenAI), BLIP (Salesforce), Sentence Transformers
- **Frontend:** Vanilla JavaScript, Modern CSS, Material Icons
- **Deployment:** Docker, systemd, Gunicorn, Nginx

## 🤖 AI Features

- **Local Processing:** All AI runs on your server (no external API calls)
- **GPU Support:** CUDA acceleration for fast processing
- **Automatic Analysis:** Photos analyzed on upload (configurable)
- **Smart Search:** Natural language queries like "sunset at the beach"
- **Vector Database:** pgvector for efficient similarity search
- **Background Tasks:** Celery for async processing

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+ (with pgvector extension)
- Redis 6+
- 4GB+ RAM (8GB+ recommended for AI processing)
- Optional: NVIDIA GPU with CUDA for faster AI processing

## 🚀 Production Deployment

For production deployment:

1. Follow the [Deployment Checklist](docs/deployment/DEPLOYMENT_CHECKLIST.md)
2. Use [Systemd Deployment Guide](docs/deployment/DEPLOYMENT_SYSTEMD.md) or [Docker Guide](docs/deployment/DOCKER_GUIDE.md)
3. Configure [Celery Workers](docs/admin-guides/CELERY_SETUP.md) for background processing
4. Set up proper [AI Settings](docs/admin-guides/ADMIN_GUIDE_AI_SETTINGS.md)

## 🔒 Security

**⚠️ Important Security Notes:**

- **No Default Admin Account** - You must create your own admin user:
  ```bash
  docker-compose exec web python manage.py createsuperuser
  ```
- **Change SECRET_KEY** - Generate a unique secret key for production (never use the example)
- **Update .env** - Configure all environment variables in `.env` from `.env.example`
- **CORS Settings** - Configure `CORS_ALLOWED_ORIGINS` with your actual domains
- **Database Password** - Use a strong, unique password for `DB_PASSWORD`
- **HTTPS Required** - Always use SSL/TLS in production (see [Nginx Setup](docs/deployment/NGINX_SETUP.md))

**After deployment, immediately:**
1. Create your admin account with a strong password
2. Verify `DEBUG=False` in production
3. Check that `ALLOWED_HOSTS` includes your domain
4. Test that HTTPS redirects work correctly

See [Security Hardening Guide](docs/admin-guides/SECURITY_HARDENING.md) for more details.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[OpenAI CLIP](https://github.com/openai/CLIP)** - Image-text understanding
- **[Salesforce BLIP](https://github.com/salesforce/BLIP)** - Image captioning
- **[pgvector](https://github.com/pgvector/pgvector)** - PostgreSQL vector extension
- **Django Community** - Excellent web framework and ecosystem

## 📞 Support

- 📖 [Documentation](docs/README.md)
- 🐛 [Issue Tracker](https://github.com/badspelr/Overly-Complicated-Photo-Album/issues)
- 💬 [Discussions](https://github.com/badspelr/Overly-Complicated-Photo-Album/discussions)

---

**Version:** 1.3.0 - Public Release Ready 🎉  
**Release Date:** October 24, 2025  
**Status:** Production/Stable  
**License:** MIT  
**Grade:** A- (89/100)

*Ready for public download and deployment. See [CHANGELOG.md](CHANGELOG.md) for version history.*
