#!/bin/bash

echo "=== Checking uvis-frontend container health ==="

# Check container inspect for health check config
echo -e "\n1. Health check configuration:"
docker inspect uvis-frontend --format='{{json .State.Health}}' | python3 -m json.tool 2>/dev/null || echo "No health check configured or container not found"

# Check docker-compose for health check
echo -e "\n2. Docker-compose health check config:"
if [ -f /root/uvis/docker-compose.yml ]; then
    grep -A 10 "frontend:" /root/uvis/docker-compose.yml | grep -A 5 "healthcheck:"
else
    echo "docker-compose.yml not found"
fi

# Check container status
echo -e "\n3. Container detailed status:"
docker ps -a --filter name=uvis-frontend --format "table {{.ID}}\t{{.Status}}\t{{.Ports}}"

# Check if port 80 is accessible from host
echo -e "\n4. Testing port 80 from host:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://139.150.11.99:80/ 2>&1 || echo "Failed to connect"

# Check container logs for health check failures
echo -e "\n5. Recent health check related logs:"
docker logs uvis-frontend 2>&1 | tail -100 | grep -i "health\|check" || echo "No health-related logs found"

