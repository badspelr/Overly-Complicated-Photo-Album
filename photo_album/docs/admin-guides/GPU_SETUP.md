# GPU Acceleration Setup Guide

Your system has an **NVIDIA GeForce RTX 3060 Ti** GPU that can dramatically speed up AI processing (from minutes per photo to seconds per photo).

## Current Status
- ✅ NVIDIA GPU detected (RTX 3060 Ti)
- ✅ NVIDIA drivers installed (580.95.05)
- ✅ CUDA 13.0 available
- ✅ **Auto-detection enabled** (will use GPU if available, otherwise CPU)
- ❌ NVIDIA Container Toolkit not installed (GPU not accessible to Docker yet)

## How It Works
The application **automatically detects** GPU availability using PyTorch's `torch.cuda.is_available()`. No manual configuration needed:
- If GPU is accessible → Uses GPU acceleration (fast)
- If GPU is not accessible → Falls back to CPU (slower but works)

## Why It's Not Using GPU Yet
Docker needs the NVIDIA Container Toolkit to allow containers to access your GPU. Without it, `torch.cuda.is_available()` returns False and the app falls back to CPU.

## Installation Steps

### 1. Install NVIDIA Container Toolkit

**For Arch Linux:**
```bash
yay -S nvidia-container-toolkit
# or
sudo pacman -S nvidia-container-toolkit
```

**For Ubuntu/Debian:**
```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
```

### 2. Configure Docker to Use NVIDIA Runtime

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### 3. Verify GPU Access in Docker

```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

You should see your GPU information displayed.

### 4. Enable GPU in Photo Album

**The application already auto-detects GPU!** You just need to give Docker access to the GPU by adding the `runtime: nvidia` option:

Edit `docker-compose.light.yml` and add runtime configuration:

```yaml
  web:
    # ... other settings ...
    runtime: nvidia  # Add this line
    environment:
      # ... existing vars (no changes needed) ...

  celery-worker:
    # ... other settings ...
    runtime: nvidia  # Add this line
    environment:
      # ... existing vars (no changes needed) ...
```

**Note:** The environment variables are already set for auto-detection. You only need to add `runtime: nvidia` to both services.

### 5. Restart Containers

```bash
./dev.sh restart
```

## Performance Comparison

- **CPU Mode**: ~2-5 minutes per photo (current)
- **GPU Mode**: ~5-15 seconds per photo (expected with RTX 3060 Ti)

That's a **~20x speedup**! Processing your 350+ photos would go from ~17 hours to under 1 hour.

## Verification

After setup, check if GPU is being used:

```bash
# Watch GPU usage while processing
watch -n 1 nvidia-smi

# Check logs for GPU confirmation
docker-compose -f docker-compose.light.yml -f docker-compose.dev.yml logs celery-worker | grep -i "gpu\|cuda"
```

You should see messages like:
- "Loading local BLIP model on **cuda**..." (instead of "cpu")
- GPU utilization in nvidia-smi should spike to 80-100% during processing

## Troubleshooting

If containers fail to start with GPU enabled:
1. Verify toolkit is installed: `nvidia-ctk --version`
2. Check Docker daemon config: `cat /etc/docker/daemon.json`
3. Ensure NVIDIA runtime is listed: `docker info | grep -i runtime`
4. Check container logs: `docker logs photo_album-celery-worker-1`

## Current Workaround

Until GPU is set up, the AI processing is working on CPU. It's slower but functional. Your photos are being processed in the background.
