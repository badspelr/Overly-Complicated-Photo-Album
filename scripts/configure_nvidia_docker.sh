#!/bin/bash

# Configure Docker to use NVIDIA Container Runtime

echo "Updating Docker daemon configuration..."

sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
    "log-driver": "json-file",
    "log-opts": { "max-size": "10m", "max-file": "5" },
    "dns": ["172.17.0.1"],
    "bip": "172.17.0.1/16",
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    },
    "default-runtime": "nvidia"
}
EOF

echo "Restarting Docker daemon..."
sudo systemctl restart docker

echo "Waiting for Docker to restart..."
sleep 3

echo "Testing GPU access..."
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ GPU access configured successfully!"
    echo ""
    echo "Now starting your containers..."
    docker-compose up -d
else
    echo ""
    echo "❌ GPU access test failed. Please check the configuration."
fi
