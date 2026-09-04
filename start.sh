#!/bin/bash
# SignBridge start script for Replit
set -e
# Create a project-local virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "[start] Creating Python virtual environment..."
  python3 -m venv .venv
fi
# Install Python dependencies into the virtual environment
echo "[start] Installing/checking Python dependencies..."
.venv/bin/python -m pip install --quiet -r requirements.txt
# Build the frontend if the dist folder doesn't exist
if [ ! -f frontend/dist/index.html ]; then
  echo "[start] Building frontend..."
  if [ ! -d frontend/node_modules ]; then
    cd frontend
    npm install --silent
    cd ..
  fi
  cd frontend
  npm run build
  cd ..
fi
echo "[start] Starting SignBridge..."
.venv/bin/python -m uvicorn server.app:app --host 0.0.0.0 --port 3000
