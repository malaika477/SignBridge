#!/bin/bash
set -e

# Install Python dependencies (slim set for Glitch's limited environment)
python3 -m pip install --quiet --upgrade pip
python3 -m pip install --quiet \
    fastapi uvicorn[standard] \
    scikit-learn numpy joblib \
    python-dotenv \
    groq openai

# Build the frontend
cd frontend
npm install
npm run build
cd ..

# Run the backend on the port Glitch assigns
export PORT=${PORT:-3000}
python3 -m uvicorn server.app:app --host 0.0.0.0 --port $PORT