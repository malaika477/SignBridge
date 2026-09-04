#!/bin/bash
# Build step for Replit deployments
set -e
python3 -m pip install --quiet -r requirements.txt
cd frontend && npm install --silent && npm run build && cd ..