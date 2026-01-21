#!/bin/bash
cd /home/user/webapp/backend
pkill -f "uvicorn main:app"
sleep 2
export PYTHONPATH=/home/user/webapp/backend:$PYTHONPATH
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend_restart.log 2>&1 &
sleep 3
echo "Backend restarted on port 8000"
curl -s http://localhost:8000/health
