# Django Photo Album

> Modern, AI-powered photo management system built with Django 5.2

[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
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

```bash
# Clone the repository
git clone https://github.com/yourusername/photo_album.git
cd photo_album

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Visit `http://localhost:8000` and start uploading photos!

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
- **Flexible Deployment:** CPU-only by default, optional GPU acceleration
- **Automatic Analysis:** Photos analyzed on upload (configurable)
- **Smart Search:** Natural language queries like "sunset at the beach"
- **Vector Database:** pgvector for efficient similarity search
- **Background Tasks:** Celery for async processing

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+ (with pgvector extension)
- Redis 6+
- 4GB+ RAM (8GB+ recommended for AI processing)
- Optional: NVIDIA GPU with CUDA for faster AI processing (see [GPU Support](docs/deployment/GPU_SUPPORT.md))

## 🚀 Production Deployment

### Quick Start (CPU-only)

```bash
# Clone and configure
git clone https://github.com/yourusername/photo_album.git
cd photo_album
cp .env.example .env
# Edit .env with your settings

# Deploy with Docker
docker compose -f docker-compose.prod.yml up -d
```

### With GPU Support (Optional)

```bash
# If you have NVIDIA GPU + drivers + Container Toolkit
docker compose -f docker-compose.prod.yml -f docker-compose.gpu.yml up -d
```

### Comprehensive Guides

1. Follow the [Deployment Checklist](docs/deployment/DEPLOYMENT_CHECKLIST.md)
2. Use [Docker Setup Guide](docs/deployment/DOCKER_SETUP.md) for containerized deployment
3. Or use [Systemd Deployment Guide](docs/deployment/DEPLOYMENT_SYSTEMD.md) for traditional setup
4. Configure [Celery Workers](docs/admin-guides/CELERY_SETUP.md) for background processing
5. Set up proper [AI Settings](docs/admin-guides/ADMIN_GUIDE_AI_SETTINGS.md)
6. For GPU acceleration, see [GPU Support Guide](docs/deployment/GPU_SUPPORT.md)

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
- 🐛 [Issue Tracker](https://github.com/yourusername/photo_album/issues)
- 💬 [Discussions](https://github.com/yourusername/photo_album/discussions)

---

**Version:** 1.2.0  
**Last Updated:** October 18, 2025
