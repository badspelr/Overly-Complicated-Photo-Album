# GPU Support Configuration

## Overview

The Photo Album application supports both **CPU-only** and **GPU-accelerated** deployments. By default, the production configuration runs on CPU to ensure maximum compatibility. GPU support is available as an optional overlay.

## Default: CPU-Only Deployment

The default `docker-compose.prod.yml` is optimized for CPU-only servers:
- Uses lightweight CPU-only PyTorch from `requirements-docker.txt`
- No NVIDIA driver requirements
- Works on any server (VPS, cloud instances, etc.)
- Slightly slower AI processing but fully functional

```bash
# Standard deployment (CPU-only)
docker compose -f docker-compose.prod.yml up -d
```

## Optional: GPU-Accelerated Deployment

If you have a server with NVIDIA GPU(s) and want faster AI processing:

### Prerequisites

1. **NVIDIA GPU** installed in your server
2. **NVIDIA drivers** installed on host
3. **NVIDIA Container Toolkit** installed:

```bash
# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Enable GPU Support

Use the GPU overlay file when starting containers:

```bash
# Deploy with GPU support
docker compose -f docker-compose.prod.yml -f docker-compose.gpu.yml up -d
```

### Verify GPU Access

Check that containers can see the GPU:

```bash
# Check GPU in web container
docker compose -f docker-compose.prod.yml exec web nvidia-smi

# Check GPU in celery worker
docker compose -f docker-compose.prod.yml exec celery-worker nvidia-smi
```

## Performance Comparison

| Deployment Type | AI Processing Speed | Memory Usage | Server Requirements |
|----------------|---------------------|--------------|---------------------|
| CPU-only | ~5-10s per image | ~2-4GB RAM | Any Linux server |
| GPU-accelerated | ~1-2s per image | ~4-6GB RAM + GPU | NVIDIA GPU + drivers |

## Configuration Files

- **`docker-compose.prod.yml`** - Base production configuration (CPU-only)
- **`docker-compose.gpu.yml`** - GPU overlay (adds NVIDIA runtime support)
- **`requirements.txt`** - Full requirements with GPU-enabled PyTorch
- **`requirements-docker.txt`** - Lightweight CPU-only requirements

## Switching Between CPU and GPU

### From CPU to GPU

```bash
# Stop current containers
docker compose -f docker-compose.prod.yml down

# Start with GPU support
docker compose -f docker-compose.prod.yml -f docker-compose.gpu.yml up -d
```

### From GPU to CPU

```bash
# Stop current containers
docker compose -f docker-compose.prod.yml -f docker-compose.gpu.yml down

# Start without GPU support
docker compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

### Error: "could not select device driver 'nvidia'"

This means GPU support is enabled but NVIDIA runtime isn't available:
- Make sure NVIDIA drivers are installed on the host
- Install NVIDIA Container Toolkit (see prerequisites above)
- Or run without the GPU overlay: `docker compose -f docker-compose.prod.yml up -d`

### GPU Not Detected in Container

```bash
# Check if host can see GPU
nvidia-smi

# Check Docker GPU support
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Restart Docker daemon
sudo systemctl restart docker
```

### Out of GPU Memory

Reduce batch sizes or concurrent workers:
```bash
# In .env file
CELERY_WORKER_CONCURRENCY=2  # Reduce from default 4
```

## Best Practices

1. **Start with CPU** - Test deployment without GPU first
2. **Monitor GPU usage** - Use `nvidia-smi` to track utilization
3. **Use GPU for bulk processing** - Especially helpful for batch photo uploads
4. **Scale workers appropriately** - Don't spawn more workers than your GPU can handle

## Need Help?

- See [DOCKER_SETUP.md](DOCKER_SETUP.md) for general Docker deployment
- See [PRODUCTION_QUICK_START.md](PRODUCTION_QUICK_START.md) for production deployment guide
- Check [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) before going live
