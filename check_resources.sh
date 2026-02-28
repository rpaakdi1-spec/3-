#!/bin/bash
echo "=== Docker Container Resource Usage ==="
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

echo -e "\n=== System Memory Info ==="
free -h

echo -e "\n=== Docker System Info ==="
docker system df

echo -e "\n=== Top Memory Consuming Processes ==="
ps aux --sort=-%mem | head -n 10

echo -e "\n=== Backend Container Details ==="
docker exec uvis-backend ps aux --sort=-%mem | head -n 10

echo -e "\n=== Checking Uvicorn Workers ==="
docker exec uvis-backend ps aux | grep uvicorn | wc -l

echo -e "\n=== Redis Memory Usage ==="
docker exec uvis-redis redis-cli info memory | grep "used_memory_human\|maxmemory_human"

echo -e "\n=== PostgreSQL Memory Usage ==="
docker exec uvis-db psql -U coldchain_user -d coldchain_dispatch -c "SELECT pg_size_pretty(pg_database_size('coldchain_dispatch'));"
