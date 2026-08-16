#!/bin/bash
set -e

APP_PORT="${PORT:-10000}"

echo "=== Starting AtmosIQ 2.0 Production Stack (Port: $APP_PORT, Host: 0.0.0.0) ==="

mkdir -p /home/user/app/logs /home/user/app/artifacts /app/logs /app/artifacts 2>/dev/null || true

# Start FastAPI Inference Backend on internal port 8000
echo "--> Starting FastAPI Inference Engine on 0.0.0.0:8000..."
python -m uvicorn atmosiq.api.app:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

# Wait for FastAPI to become ready
echo "--> Waiting for FastAPI to initialize..."
for i in {1..30}; do
  if curl -s http://127.0.0.1:8000/health/live > /dev/null 2>&1; then
    echo "--> FastAPI is LIVE and ready!"
    break
  fi
  sleep 1
done

# Start Next.js Frontend on 0.0.0.0:$APP_PORT
echo "--> Starting Next.js Web Interface on 0.0.0.0:$APP_PORT..."
if [ -d "/home/user/app/frontend" ]; then
  cd /home/user/app/frontend
elif [ -d "/app/frontend" ]; then
  cd /app/frontend
elif [ -d "./frontend" ]; then
  cd ./frontend
fi

NODE_ENV=production npx next start --hostname 0.0.0.0 --port "$APP_PORT" &
NEXT_PID=$!

# Trap signals for graceful shutdown
trap "kill -TERM $FASTAPI_PID $NEXT_PID" SIGTERM SIGINT

wait -n $FASTAPI_PID $NEXT_PID
