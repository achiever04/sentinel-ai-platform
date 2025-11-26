#!/bin/bash

echo "Starting Sentinel AI Backend..."

# Activate virtual environment
source venv/bin/activate

# Check Redis
if ! pgrep -x "redis-server" > /dev/null; then
    echo "Starting Redis..."
    redis-server --daemonize yes
fi

# Start Celery worker (background)
echo "Starting Celery worker..."
celery -A backend.tasks.celery_app worker --loglevel=info --detach

# Start FastAPI
echo "Starting FastAPI server on http://localhost:8000"
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
