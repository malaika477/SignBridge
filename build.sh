#!/bin/bash
set -e
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install --quiet -r requirements-deploy.txt
cd frontend && npm install --silent && npm run build && cd ..