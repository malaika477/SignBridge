#!/bin/bash
# SignBridge start script for Replit
# Installs deps if missing, builds the frontend if needed, then starts FastAPI.

set -e

# Install Python dependencies if not present
if ! python3 -c "import fastapi" 2>/dev/null; then
  echo "[start] Installing Python dependencies..."
  python3 -m pip install --quiet -r requirements.txt
fi

# Build the frontend if the dist folder doesn't exist
if [ ! -f frontend/dist/index.html ]; then
  echo "[start] Building frontend..."
  if [ ! -d frontend/node_modules ]; then
    cd frontend && npm install --silent && cd ..
  fi
  cd frontend && npm run build && cd ..
fi

echo "[start] Starting SignBridge on port \..."
python3 -m uvicorn server.app:app --host 0.0.0.0 --port "\"