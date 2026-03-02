#!/bin/bash
# Quick check script to run on server

echo "Waiting for backend to fully start..."
sleep 20

echo "=== Current Status ==="
docker compose ps

echo -e "\n=== Backend Logs (last 50 lines) ==="
docker compose logs backend --tail=50

echo -e "\n=== Health Check Attempts ==="
echo "Internal health check (from host):"
curl -s http://localhost:8000/health

echo -e "\n\nExternal health check (through nginx):"
curl -s http://139.150.11.99/api/v1/health

echo -e "\n\n=== If still 502, try: ==="
echo "docker compose restart backend"
echo "sleep 15"
echo "curl http://139.150.11.99/api/v1/health"
