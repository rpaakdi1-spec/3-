#!/bin/bash
echo "=== Checking Frontend Logs ==="
ssh root@139.150.11.99 "docker compose -f /root/uvis/docker-compose.yml logs --tail=50 frontend"

echo -e "\n=== Checking Backend Logs ==="
ssh root@139.150.11.99 "docker compose -f /root/uvis/docker-compose.yml logs --tail=50 backend"

echo -e "\n=== Checking Container Status ==="
ssh root@139.150.11.99 "docker compose -f /root/uvis/docker-compose.yml ps"
