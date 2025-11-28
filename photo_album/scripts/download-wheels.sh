#!/bin/bash
# Download PyTorch manually to avoid Docker build issues
# This downloads the CPU-only version which is much smaller

echo "🔽 Downloading PyTorch CPU-only wheel..."
mkdir -p ./wheels

# Download CPU-only PyTorch (much smaller - ~200MB vs 900MB)
wget -O ./wheels/torch-2.4.1-cp313-cp313-linux_x86_64.whl \
  "https://download.pytorch.org/whl/cpu/torch-2.4.1%2Bcpu-cp313-cp313-linux_x86_64.whl"

# Download other AI packages
wget -O ./wheels/sentence_transformers-3.0.1-py3-none-any.whl \
  "https://files.pythonhosted.org/packages/sentence_transformers-3.0.1-py3-none-any.whl"

echo "✅ Downloaded wheels to ./wheels/ directory"
echo "📁 Total size:"
du -sh ./wheels/

echo ""
echo "🐳 To use these in Docker, add to Dockerfile:"
echo "COPY wheels/ /tmp/wheels/"
echo "RUN pip install /tmp/wheels/*.whl"