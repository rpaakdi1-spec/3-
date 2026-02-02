#!/bin/bash

echo "=== 1️⃣ 컨테이너 상태 확인 ==="
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo -e "\n=== 2️⃣ 백엔드 헬스체크 ==="
docker exec uvis-backend curl -f http://localhost:8000/health 2>/dev/null || echo "❌ Health check failed"

echo -e "\n=== 3️⃣ 백엔드 최근 로그 (에러만) ==="
docker logs uvis-backend --tail 50 | grep -i "error\|exception\|failed\|traceback" | tail -20

echo -e "\n=== 4️⃣ Nginx 로그 (최근 10줄) ==="
docker logs uvis-nginx --tail 10

echo -e "\n=== 5️⃣ 백엔드 전체 로그 (최근 30줄) ==="
docker logs uvis-backend --tail 30

