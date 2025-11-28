# Requirements.txt Review - October 20, 2025

## Summary
Total packages: 137
Recommended to keep: ~100
Can potentially remove: ~37

---

## ✅ CORE - Keep (Must Have)

### Django & Web Framework
- `Django==5.2.6` - Core framework
- `djangorestframework==3.15.2` - REST API
- `gunicorn==23.0.0` - Production web server
- `whitenoise` - Static file serving
- `asgiref==3.9.1` - ASGI support

### Django Extensions (All Used)
- `django-cors-headers==4.6.0` - CORS handling
- `django-filter==24.3` - Filtering in views/API
- `django-health-check==3.20.0` - Health check endpoints
- `django-imagekit==5.0.0` - Image processing/thumbnails
- `django-ratelimit==4.1.0` - Rate limiting
- `django-redis==5.4.0` - Redis caching
- `django-webpack-loader==3.0.0` - Frontend integration
- `django-widget-tweaks==1.5.0` - Form rendering
- `django-appconf==1.1.0` - App configuration

### Database
- `psycopg2-binary==2.9.10` - PostgreSQL adapter
- `pgvector==0.2.1` - Vector similarity search
- `psycopg-binary==3.2.10` - ⚠️ **DUPLICATE** - Can remove if using psycopg2

### Celery (Background Tasks)
- `celery==5.4.0` - Task queue
- `redis==5.1.1` - Message broker
- `amqp==5.3.1` - Celery transport
- `billiard==4.2.2` - Celery worker pool
- `kombu==5.5.4` - Celery messaging
- `vine==5.1.0` - Celery promises

### AI & ML (Core Features)
- `torch==2.8.0` - PyTorch (1.5GB+)
- `transformers==4.56.2` - Hugging Face models (BLIP)
- `sentence-transformers==3.0.1` - Semantic search (CLIP)
- `pillow==11.0.0` - Image processing
- `numpy==2.3.2` - Array operations
- `safetensors==0.6.2` - Model loading
- `huggingface-hub==0.35.0` - Model downloads
- `tokenizers==0.22.1` - Text tokenization

### AI Dependencies
- `scikit-learn==1.7.2` - ML utilities
- `scipy==1.16.2` - Scientific computing
- `nltk==3.9.1` - NLP (for tagging)
- `joblib==1.5.2` - Model caching
- `regex==2025.9.18` - Pattern matching

### Video Processing
- `moviepy==1.0.3` - Video manipulation
- `imageio==2.37.0` - Video I/O
- `imageio-ffmpeg==0.6.0` - FFmpeg wrapper
- `proglog==0.1.12` - Progress logging

### Image Processing
- `pilkit==3.0` - Image utilities
- `networkx==3.5` - Image graph operations

### Utilities
- `python-decouple==3.8` - Environment config
- `python-dotenv==1.1.1` - .env file loading
- `python-magic==0.4.27` - File type detection
- `requests==2.32.5` - HTTP requests
- `beautifulsoup4==4.13.5` - HTML parsing
- `certifi==2025.8.3` - SSL certificates
- `python-dateutil==2.9.0.post0` - Date utilities
- `tzdata==2025.2` - Timezone data

---

## ⚠️ NVIDIA GPU PACKAGES - Keep ONLY if using GPU

**Current Status:** You're using **CPU-only** processing

### NVIDIA CUDA Packages (13 packages, ~2GB installed)
```
nvidia-cublas-cu12==12.8.4.1
nvidia-cuda-cupti-cu12==12.8.90
nvidia-cuda-nvrtc-cu12==12.8.93
nvidia-cuda-runtime-cu12==12.8.90
nvidia-cudnn-cu12==9.10.2.21
nvidia-cufft-cu12==11.3.3.83
nvidia-cufile-cu12==1.13.1.3
nvidia-curand-cu12==10.3.9.90
nvidia-cusolver-cu12==11.7.3.90
nvidia-cusparse-cu12==12.5.8.93
nvidia-cusparselt-cu12==0.7.1
nvidia-nccl-cu12==2.27.3
nvidia-nvjitlink-cu12==12.8.93
nvidia-nvtx-cu12==12.8.90
triton==3.4.0
```

**Recommendation:** 
- ❌ **Remove if CPU-only** (saves ~2GB disk, ~500MB memory)
- ✅ **Keep if planning GPU setup** (per GPU_SETUP.md)

---

## ❌ DEVELOPMENT/TESTING - Can Remove for Production

### Code Quality Tools
- `black==25.9.0` - Code formatter
- `autoflake==2.3.1` - Remove unused imports
- `pyflakes==3.4.0` - Linter
- `mypy_extensions==1.1.0` - Type checking

### Testing
- `pytest==8.4.2` - Test framework
- `pytest-cov==7.0.0` - Coverage
- `pytest-django==4.11.1` - Django testing
- `coverage==7.10.7` - Code coverage
- `factory_boy==3.3.3` - Test fixtures
- `Faker==37.6.0` - Fake data generation

### Security Scanning
- `safety==3.6.2` - Dependency vulnerability scanner
- `safety-schemas==0.0.16` - Safety schemas
- `dparse==0.6.4` - Dependency parsing

**Recommendation:** Remove for production, keep for development

---

## ❓ QUESTIONABLE - Review Usage

### Potentially Unused
- `bs4==0.0.2` - ⚠️ **DUPLICATE** of beautifulsoup4
- `pip_search==0.0.14` - Pip package search (unused?)
- `decorator==4.4.2` - Older decorator library (check if needed)
- `hf-xet==1.1.10` - Hugging Face XET protocol (rarely used)
- `pytokens==0.1.10` - Token utilities (check usage)

### CLI Tools (Rarely Needed in Container)
- `click==8.3.0` - CLI framework
- `click-didyoumean==0.3.1` - CLI suggestions
- `click-plugins==1.1.1.2` - CLI plugins
- `click-repl==0.3.0` - CLI REPL
- `prompt_toolkit==3.0.52` - CLI prompts
- `rich==14.1.0` - Rich terminal output
- `shellingham==1.5.4` - Shell detection
- `typer==0.19.2` - CLI framework

**Recommendation:** These are for CLI tools, not web app. Check if any management commands use them.

### Data Validation (Check Usage)
- `marshmallow==4.0.1` - Serialization (if DRF is used, might be redundant)
- `pydantic==2.11.9` - Data validation
- `pydantic_core==2.33.2` - Pydantic core

### Authentication (Check if Used)
- `Authlib==1.6.4` - OAuth/OIDC library
- `cryptography==46.0.1` - Cryptography (might be dependency)
- `cffi==1.2.0` - Foreign function interface

---

## 📊 Disk Space Impact

| Category | Packages | Estimated Size |
|----------|----------|----------------|
| PyTorch + CUDA | 16 | ~3.5 GB |
| Transformers/AI | 10 | ~1.5 GB |
| Django Core | 30 | ~200 MB |
| Testing/Dev Tools | 10 | ~100 MB |
| Other Dependencies | 71 | ~500 MB |
| **Total** | **137** | **~5.8 GB** |

---

## 🎯 Recommended Actions

### Option 1: Minimal Cleanup (Conservative)
Remove obvious duplicates and dev tools from production:
```bash
# Remove these from requirements.txt:
- bs4==0.0.2  # Duplicate of beautifulsoup4
- psycopg-binary==3.2.10  # Duplicate of psycopg2-binary
- pip_search==0.0.14  # Unused
```
**Savings:** ~5 MB

### Option 2: Remove GPU Packages (If CPU-Only)
```bash
# Remove all nvidia-* and triton packages
# List in "NVIDIA GPU PACKAGES" section above
```
**Savings:** ~2 GB disk, ~500 MB memory

### Option 3: Split requirements.txt
Create separate files:
- `requirements.txt` - Production only
- `requirements-dev.txt` - Development/testing
- `requirements-gpu.txt` - GPU acceleration (already exists as requirements-docker.txt)

### Option 4: Aggressive Cleanup
Remove all dev/test tools + GPU packages + unused CLI tools
**Savings:** ~2.5 GB disk, ~500 MB memory

---

## 🔍 Commands to Check Usage

### Find unused imports across codebase:
```bash
docker-compose exec web bash -c "
cd /app
python -m pip list --format=freeze | cut -d'=' -f1 | while read pkg; do
    echo -n \"Checking \$pkg... \"
    grep -r \"import \$pkg\" --include='*.py' . > /dev/null && echo 'USED' || echo 'NOT FOUND'
done
"
```

### Check if marshmallow is used:
```bash
grep -r "marshmallow" --include='*.py' photo_album/
```

### Check if Authlib is used:
```bash
grep -r "authlib\|Authlib" --include='*.py' photo_album/
```

### Check if pydantic is used:
```bash
grep -r "pydantic\|Pydantic" --include='*.py' photo_album/
```

---

## 💡 My Recommendation

**For your use case (CPU-only, development environment):**

1. ✅ **Remove GPU packages** - You're not using them, saves 2GB
2. ✅ **Keep dev tools** - Useful for development
3. ✅ **Remove duplicates** (bs4, psycopg-binary)
4. ❓ **Check usage** of: Authlib, marshmallow, pydantic, CLI tools
5. ⏳ **Later:** Split into requirements-prod.txt and requirements-dev.txt

**Quick win:** Remove GPU packages now, saves 2GB and reduces Docker image size.

Would you like me to:
1. Remove GPU packages?
2. Check which questionable packages are actually used?
3. Create separate requirements files?
