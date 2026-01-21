#!/bin/bash
cd /home/user/webapp/backend

# Kill any existing process on port 8000
fuser -k 8000/tcp 2>/dev/null || true
sleep 2

# Find Python with dependencies
PYTHON_BIN=""
if [ -f "/root/.server/.venv/bin/python" ]; then
    PYTHON_BIN="/root/.server/.venv/bin/python"
elif [ -f "/home/user/.venv/bin/python" ]; then
    PYTHON_BIN="/home/user/.venv/bin/python"
fi

if [ -z "$PYTHON_BIN" ]; then
    echo "❌ Virtual environment not found"
    exit 1
fi

echo "✅ Using Python: $PYTHON_BIN"

# Start backend
nohup $PYTHON_BIN -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend_8000.log 2>&1 &
BACKEND_PID=$!

sleep 5

if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✅ Backend started successfully (PID: $BACKEND_PID)"
    curl -s http://localhost:8000/health || echo "⚠️ Health check failed"
else
    echo "❌ Backend failed to start"
    cat /tmp/backend_8000.log
fi
