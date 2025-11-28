# Docker Requirements Confusion - Clarification

## Current Situation

You have **TWO different requirements files**:

### 1. `requirements.txt` (FULL VERSION - Currently Used)
- **137 packages** (now 124 after cleanup)
- **Includes GPU packages** (nvidia-*, triton)
- **Used by:** `Dockerfile` (main)
- **Image size:** 8.4 GB
- **Currently ACTIVE** in your running containers

### 2. `requirements-docker.txt` (LIGHTWEIGHT VERSION - Not Used)
- **~16 packages** only
- **CPU-only PyTorch** (no GPU packages)
- **Used by:** `Dockerfile.light`
- **Image size:** Much smaller (~2-3 GB estimated)
- **NOT currently used**

---

## What's Actually Running

Based on inspection:

```bash
# Current configuration uses:
- docker-compose.light.yml  # Specifies Dockerfile.light
- docker-compose.dev.yml    # Overrides to use Dockerfile (FULL)
- Dockerfile                # Uses requirements.txt (FULL VERSION)
```

**Current images:**
- `photo_album-web`: 8.4 GB (built 44 hours ago)
- Uses `requirements.txt` with all 124 packages + GPU support

---

## The Files

### `Dockerfile` (Currently Used)
```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
- ✅ Currently active
- Includes GPU packages (nvidia-*, triton)
- Larger image size (8.4 GB)

### `Dockerfile.light` (Available but Not Used)
```dockerfile
COPY requirements-docker.txt /app/
RUN pip install --no-cache-dir -r requirements-docker.txt
```
- ❌ Not currently active
- CPU-only, smaller packages
- Smaller image size (~2-3 GB)

---

## Decision Time: Which Should You Use?

### Option 1: Keep Current Setup (requirements.txt)
**Pros:**
- ✅ Already working
- ✅ GPU packages ready for GPU work
- ✅ Just cleaned up unused packages

**Cons:**
- ❌ Larger image size (8.4 GB)
- ❌ GPU packages not used yet (waste ~2 GB)

**Recommendation:** ✅ **Keep this if planning GPU work soon**

---

### Option 2: Switch to Lightweight (requirements-docker.txt)
**Pros:**
- ✅ Smaller image (~2-3 GB vs 8.4 GB)
- ✅ Faster builds
- ✅ CPU-optimized PyTorch
- ✅ No unused GPU packages

**Cons:**
- ❌ Need to rebuild images
- ❌ Need to update requirements-docker.txt
- ❌ Would need to switch back for GPU work

**Recommendation:** ⚠️ **Only if NOT doing GPU work**

---

## My Recommendation

Since you said you're **"going to work on GPU processing next"**:

### ✅ **Keep using requirements.txt (current setup)**

**Why?**
1. Already working and tested
2. GPU packages ready to use
3. Just cleaned up 37 unused packages
4. No need to rebuild images now
5. When you add GPU support, it's just configuration changes

**No action needed** - your current setup is good!

---

## Future: Consolidate After GPU Work

Once GPU work is done, you could:

1. **Create three files:**
   - `requirements-base.txt` - Core packages
   - `requirements-cpu.txt` - CPU-only AI packages
   - `requirements-gpu.txt` - GPU packages
   
2. **Use based on deployment:**
   - Development: `requirements.txt` (all packages)
   - Production CPU: `-base.txt` + `-cpu.txt`
   - Production GPU: `-base.txt` + `-gpu.txt`

---

## Summary

**Current state:**
- ✅ Using `requirements.txt` (full version)
- ✅ Docker image: 8.4 GB with GPU packages
- ✅ Recently cleaned: 137 → 124 packages

**Files:**
- `requirements.txt` - **ACTIVE** (124 packages, includes GPU)
- `requirements-docker.txt` - NOT USED (16 packages, CPU-only)
- `Dockerfile` - **ACTIVE** (uses requirements.txt)
- `Dockerfile.light` - NOT USED (uses requirements-docker.txt)

**What to do:**
- ✅ **Keep current setup** - it's ready for GPU work
- ✅ `requirements-docker.txt` is outdated anyway (missing many packages)
- ✅ Focus on GPU setup next using current requirements.txt

**No changes needed!** Your cleaned `requirements.txt` is the right file to use.

---

## Update - October 2025: Gunicorn Upgrade

### What Changed

**Gunicorn upgraded from v22.0 to v23.0** in both requirements files:

**requirements.txt:**
```python
gunicorn==23.0.0  # Production WSGI server
```

**requirements-docker.txt:**
```python
gunicorn>=23.0,<24.0  # Updated from >=22.0,<23.0
```

### Why the Upgrade

1. **Python 3.13 Compatibility**: Version 23.0 fixes critical bugs with Python 3.13
   - Resolved `InvalidHTTPVersion` errors causing worker crashes
   - Better handling of malformed HTTP requests from bots/scanners
   - Improved error message formatting

2. **Production Stability**: Eliminated worker crashes from external scanners
   - Workers were crashing and restarting due to Gunicorn bug
   - Version 23.0 handles these gracefully without worker restarts

3. **Better Performance**: General improvements and bug fixes

### Impact

✅ **More stable workers** - No more crashes from invalid HTTP requests  
✅ **Python 3.13 ready** - Fully compatible with latest Python  
✅ **Better error handling** - Improved logging and error messages  
✅ **Production tested** - Running successfully in production

### When to Upgrade

If you're still on Gunicorn v22.x:
```bash
# Update requirements files (already done)
# Rebuild Docker images
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d web
```

### See Also

- [CHANGELOG.md](../../CHANGELOG.md) - Full list of recent changes
- [GPU_SUPPORT.md](GPU_SUPPORT.md) - New GPU configuration guide
- [DOCKER_HEALTH_CHECK_FIX.md](DOCKER_HEALTH_CHECK_FIX.md) - Health check improvements

