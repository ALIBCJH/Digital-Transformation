#!/usr/bin/env bash
set -euo pipefail

# Install Docker only if missing
if ! command -v docker >/dev/null 2>&1; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker
fi

# Pull pre-built React image from GitHub Container Registry
docker pull ghcr.io/ALIBCJH/digital-transformation-frontend:latest

# Run React container
docker run -d --name react-frontend \
    --restart=unless-stopped \
    -p 80:80 \
    -e VITE_API_BASE_URL="${BACKEND_URL:-http://127.0.0.1:8000}/api" \
    ghcr.io/ALIBCJH/digital-transformation-frontend:latest


   docker run -d --name react-frontend --restart=unless-stopped -p 80:80 \
   -e VITE_API_BASE_URL="${BACKEND_URL}/api" \
   "ghcr.io/ALIBCJH/digital-transformation-frontend${IMAGE_TAG}"
fi