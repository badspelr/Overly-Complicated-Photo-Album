# Publishing Docker Images to Docker Hub

This guide explains how to publish pre-built Docker images for your Photo Album application.

## Why Publish Docker Images?

**Benefits:**
- ✅ **Faster deployments** - Users don't need to build (saves 5-10 minutes)
- ✅ **Consistent** - Everyone uses the same tested image
- ✅ **Easier for users** - Just pull and run, no build tools needed
- ✅ **Version control** - Tag releases (v1.0.0, v1.1.0, etc.)

## Prerequisites

1. Docker Hub account: https://hub.docker.com/ (free)
2. Docker installed locally
3. Your application code ready

## Step-by-Step Guide

### 1. Create Docker Hub Repository

1. Login to https://hub.docker.com/
2. Click "Create Repository"
3. Name: `photo-album`
4. Visibility: Public (or Private for paid accounts)
5. Click "Create"

Your repository will be: `yourusername/photo-album`

### 2. Build Images Locally

```bash
# Login to Docker Hub
docker login

# Build main image (with GPU support)
docker build -t yourusername/photo-album:latest .
docker build -t yourusername/photo-album:v1.0.0 .

# Build lightweight image (CPU-only)
docker build -f Dockerfile.light -t yourusername/photo-album:lite .
docker build -f Dockerfile.light -t yourusername/photo-album:v1.0.0-lite .
```

**Tag Naming Convention:**
- `latest` - Most recent stable version
- `v1.0.0` - Specific version number
- `lite` - Lightweight CPU-only version
- `v1.0.0-lite` - Version-specific lightweight

### 3. Push to Docker Hub

```bash
# Push latest
docker push yourusername/photo-album:latest
docker push yourusername/photo-album:v1.0.0

# Push lite
docker push yourusername/photo-album:lite
docker push yourusername/photo-album:v1.0.0-lite
```

### 4. Update Documentation

Update your README.md to include Docker Hub instructions:

```markdown
## 🚀 Quick Start (Using Pre-built Image)

```bash
# Clone repository
git clone https://github.com/yourusername/photo-album.git
cd photo-album

# Configure environment
cp .env.example .env
nano .env

# Pull and start (no build required!)
DOCKER_USERNAME=yourusername docker-compose -f docker-compose.prod.yml up -d

# Run setup
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```
\```
```

## For Users

### Using Pre-built Image (Recommended)

```bash
# Set your Docker Hub username
export DOCKER_USERNAME=yourusername

# Or add to .env file:
echo "DOCKER_USERNAME=yourusername" >> .env

# Pull and run
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### Building Locally (Alternative)

If users want to build from source:

```bash
# Don't set DOCKER_USERNAME
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

## Automated Publishing with GitHub Actions

Create `.github/workflows/docker-publish.yml`:

```yaml
name: Publish Docker Images

on:
  release:
    types: [published]
  push:
    branches: [main]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Extract version
        id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT
      
      - name: Build and push main image
        run: |
          docker build -t ${{ secrets.DOCKER_USERNAME }}/photo-album:latest .
          docker build -t ${{ secrets.DOCKER_USERNAME }}/photo-album:${{ steps.version.outputs.VERSION }} .
          docker push ${{ secrets.DOCKER_USERNAME }}/photo-album:latest
          docker push ${{ secrets.DOCKER_USERNAME }}/photo-album:${{ steps.version.outputs.VERSION }}
      
      - name: Build and push lite image
        run: |
          docker build -f Dockerfile.light -t ${{ secrets.DOCKER_USERNAME }}/photo-album:lite .
          docker build -f Dockerfile.light -t ${{ secrets.DOCKER_USERNAME }}/photo-album:${{ steps.version.outputs.VERSION }}-lite .
          docker push ${{ secrets.DOCKER_USERNAME }}/photo-album:lite
          docker push ${{ secrets.DOCKER_USERNAME }}/photo-album:${{ steps.version.outputs.VERSION }}-lite
```

## Image Size Optimization

### Current Sizes (Estimated)
- **Full image**: ~5-6 GB (includes GPU support, AI models)
- **Lite image**: ~2-3 GB (CPU-only, smaller dependencies)

### Tips to Reduce Size
1. Use multi-stage builds (already implemented)
2. Clean up cache: `RUN pip install --no-cache-dir`
3. Remove dev dependencies in production
4. Use `.dockerignore` to exclude unnecessary files

## Version Management

### Semantic Versioning
- `v1.0.0` - Major.Minor.Patch
- `v1.1.0` - New features (backward compatible)
- `v1.0.1` - Bug fixes
- `v2.0.0` - Breaking changes

### Tagging Strategy
```bash
# When releasing v1.2.0:
docker build -t yourusername/photo-album:v1.2.0 .
docker build -t yourusername/photo-album:v1.2 .
docker build -t yourusername/photo-album:v1 .
docker build -t yourusername/photo-album:latest .

docker push yourusername/photo-album:v1.2.0
docker push yourusername/photo-album:v1.2
docker push yourusername/photo-album:v1
docker push yourusername/photo-album:latest
```

## Security Considerations

### ✅ What's Safe in Public Images
- ✅ Application code
- ✅ Dependencies (requirements.txt)
- ✅ Static files
- ✅ Templates
- ✅ System packages

### ❌ What Should NEVER Be in Images
- ❌ SECRET_KEY (comes from .env)
- ❌ Database passwords
- ❌ API tokens
- ❌ Email credentials
- ❌ SSL certificates
- ❌ User data

**All secrets come from `.env` file - NEVER baked into image!**

## Troubleshooting

### Image Pull Failed
```bash
# Check if image exists
docker pull yourusername/photo-album:latest

# Check Docker Hub login
docker login
```

### Wrong Architecture
```bash
# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 \
  -t yourusername/photo-album:latest .
```

### Image Too Large
```bash
# Check image size
docker images yourusername/photo-album

# Analyze layers
docker history yourusername/photo-album:latest
```

## Publishing Checklist

Before publishing a new version:

- [ ] Update version in `CHANGELOG.md`
- [ ] Test image locally
- [ ] Run security scan: `docker scan yourusername/photo-album:latest`
- [ ] Update README with new version
- [ ] Tag release in GitHub
- [ ] Push images to Docker Hub
- [ ] Update documentation
- [ ] Announce release

---

**Quick Reference:**

```bash
# Build
docker build -t yourusername/photo-album:v1.0.0 .

# Push
docker push yourusername/photo-album:v1.0.0

# Pull (for users)
docker pull yourusername/photo-album:latest
```
