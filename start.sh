#!/usr/bin/env bash
set -e

# Render sets $PORT automatically
PORT=${PORT:-8000}

echo "Starting Wellness MCP + FastAPI server on port ${PORT}..."

# Use gunicorn with uvicorn worker
exec gunicorn main:app \
  --workers 1 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:${PORT}
