# Development vs Production Docker Setup Guide

**Date:** October 18, 2025  
**Status:** ✅ **CONFIGURED**

---

## Overview

We now have **TWO deployment modes**:

1. **Development Mode** - Code mounted as volumes (edit files, see changes instantly)
2. **Production Mode** - Code baked into image (immutable, secure, fast)

---

## Development Mode (Current Setup) 🔧

### What It Does
- **Mounts your code as Docker volumes**
- Changes to files are reflected immediately
- No rebuilds needed during development
- Perfect for active development

### Files Involved
- `docker-compose.light.yml` - Base configuration
- `docker-compose.dev.yml` - Development overrides

### How to Use

```bash
# Start in development mode (code mounted)
docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml up -d

# Edit any file on your host machine
nano album/admin.py

# Changes are immediately available (gunicorn --reload watches for changes)
# Just refresh your browser!

# View logs
docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml logs -f web

# Stop
docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml down
```

### What's Mounted
```
Host Machine          →  Docker Container
═══════════════════════════════════════════
./album/              →  /app/album/
./photo_album/        →  /app/photo_album/
./manage.py           →  /app/manage.py
./media/              →  /app/media/
./staticfiles/        →  /app/staticfiles/
./logs/               →  /app/logs/
```

### Benefits ✅
- ✅ **Instant changes** - Edit code, refresh browser
- ✅ **No rebuilds** - Save 10+ minutes per change
- ✅ **Easy debugging** - Edit files directly
- ✅ **Fast iteration** - Perfect for development

### Drawbacks ⚠️
- ⚠️ File system overhead (slower than baked-in code)
- ⚠️ Host and container must have compatible permissions
- ⚠️ Not suitable for production

---

## Production Mode (Future) 🚀

### What It Does
- **Code is baked into Docker image**
- Immutable deployments
- No file mounting
- Faster, more secure

### How to Use

```bash
# Build production image
docker-compose -f docker-compose.light.yml build

# Or build with tag
docker build -f Dockerfile.light -t photo_album:v1.0 .

# Push to registry
docker tag photo_album:v1.0 your-registry.com/photo_album:v1.0
docker push your-registry.com/photo_album:v1.0

# On production server
docker pull your-registry.com/photo_album:v1.0
docker-compose -f docker-compose.light.yml up -d
```

### Benefits ✅
- ✅ **Immutable** - Code can't be changed
- ✅ **Fast** - No file system overhead
- ✅ **Secure** - No host file access
- ✅ **Easy rollback** - Just use previous image tag
- ✅ **Production best practice**

### Drawbacks ⚠️
- ⚠️ Must rebuild image for code changes
- ⚠️ Slower development cycle

---

## When to Use Each Mode

### Use Development Mode When:
- 🔧 Active development
- 🔧 Testing new features
- 🔧 Debugging issues
- 🔧 Frequent code changes
- 🔧 Local development

### Use Production Mode When:
- 🚀 Deploying to production
- 🚀 Deploying to staging
- 🚀 Creating release builds
- 🚀 Need immutable deployments
- 🚀 Performance is critical

---

## Transition from Dev to Production

### Current State: Development
```bash
# You're here now ✓
docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml up -d
```

### When Ready for Production

**Step 1: Build Production Image**
```bash
# Build with tag
docker build -f Dockerfile.light -t photo_album:v1.0 .

# Test locally (no dev override)
docker-compose -f docker-compose.light.yml up -d
```

**Step 2: Push to Registry**
```bash
# Tag for registry
docker tag photo_album:v1.0 your-registry.com/photo_album:v1.0

# Push
docker push your-registry.com/photo_album:v1.0
```

**Step 3: Deploy to Production**
```bash
# On production server
docker pull your-registry.com/photo_album:v1.0
docker-compose -f docker-compose.light.yml up -d
```

---

## Current Admin Fix Status

### ✅ Development (Working Now)
- Code is mounted as volume
- `album/admin.py` changes are live
- Admin fix is active
- No rebuild needed

### ⚠️ Production (Need to Rebuild)
- When you build for production, admin fix will be included
- Image will have updated code baked in
- One-time rebuild, then fast deployments

---

## Quick Reference Commands

### Development Commands
```bash
# Start dev mode
docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml up -d

# Restart after code change (usually not needed, auto-reloads)
docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml restart web

# View logs
docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml logs -f

# Stop
docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml down
```

### Production Commands
```bash
# Build image
docker-compose -f docker-compose.light.yml build

# Start prod mode (no dev override)
docker-compose -f docker-compose.light.yml up -d

# View logs
docker-compose -f docker-compose.light.yml logs -f

# Stop
docker-compose -f docker-compose.light.yml down
```

---

## File Structure

```
photo_album/
├── docker-compose.light.yml      # Base configuration (production)
├── docker-compose.dev.yml        # Development overrides
├── Dockerfile.light              # Production image definition
├── album/
│   ├── admin.py                  # ← Your admin fix is here
│   ├── models.py
│   └── ...
├── photo_album/
│   ├── settings.py
│   └── ...
└── manage.py
```

---

## Troubleshooting

### Code Changes Not Appearing
```bash
# Make sure you're using dev mode
docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml up -d

# Check if volumes are mounted
docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml exec web ls -la /app/album/

# Restart web service
docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml restart web
```

### Permission Issues
```bash
# Fix permissions on host
sudo chown -R $USER:$USER album/ photo_album/ media/ logs/
```

### Want to Test Production Mode Locally
```bash
# Stop dev mode
docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml down

# Rebuild image with current code
docker-compose -f docker-compose.light.yml build

# Start without dev override
docker-compose -f docker-compose.light.yml up -d
```

---

## Recommendation

### For Now (Development):
```bash
# Use this command ✓
docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml up -d
```

- ✅ Fast development
- ✅ Instant code changes
- ✅ Admin fix is live
- ✅ No rebuilds needed

### For Production (Later):
```bash
# Build once
docker build -f Dockerfile.light -t photo_album:v1.0 .

# Push to registry
docker push your-registry.com/photo_album:v1.0

# Deploy
docker-compose -f docker-compose.light.yml up -d
```

- ✅ Immutable deployments
- ✅ Fast and secure
- ✅ Easy rollback
- ✅ Production best practice

---

## Summary

**You asked:** Which option - mount code or rebuild image?  
**Answer:** **Both!** Use mounts for development (now), rebuild for production (later).

**Current Status:**
- ✅ Development mode configured
- ✅ Code mounted as volumes
- ✅ Admin fix is live
- ✅ Changes reflect instantly
- ⏳ Production image rebuild when ready

**Next Steps:**
1. ✅ Develop using mounted volumes (current setup)
2. ✅ Test admin fix works (it does!)
3. ⏳ When ready for production, rebuild image
4. ⏳ Push to registry
5. ⏳ Deploy to production

**Best of both worlds!** 🎉
