#!/bin/bash

# 가비아 서버 복구 후 문제 해결 스크립트

echo "=========================================="
echo "  문제 해결 중..."
echo "=========================================="
echo ""

cd /root/uvis

# 1. Nginx 문제 해결
echo "===== 1. Nginx 재시작 ====="
docker-compose stop nginx
sleep 2
docker-compose start nginx
sleep 5
echo "Nginx 상태:"
docker-compose ps nginx
echo ""

# 2. Frontend 컨테이너 확인 및 재시작
echo "===== 2. Frontend 확인 ====="
if docker-compose ps | grep -q frontend; then
    echo "Frontend 컨테이너 존재 - 재시작 중..."
    docker-compose restart frontend
    sleep 10
else
    echo "Frontend 컨테이너 없음 - 시작 중..."
    docker-compose up -d frontend
    sleep 10
fi
echo ""

# 3. PostgreSQL 권한 문제 해결
echo "===== 3. PostgreSQL 권한 확인 ====="
docker-compose exec -T db psql -U postgres -c "\du" 2>/dev/null || {
    echo "PostgreSQL 재시작 중..."
    docker-compose restart db
    sleep 10
}
echo ""

# 4. 전체 서비스 상태 확인
echo "===== 4. 전체 서비스 상태 ====="
docker-compose ps
echo ""

# 5. 헬스체크
echo "===== 5. 헬스체크 ====="
echo ""
echo "--- 백엔드 ---"
sleep 5
curl -s http://localhost:8000/health | head -3 || echo "백엔드 아직 시작 중..."
echo ""

echo "--- 프론트엔드 ---"
curl -I http://localhost/ 2>&1 | head -3 || echo "프론트엔드 아직 시작 중..."
echo ""

echo "--- 데이터베이스 ---"
docker-compose exec -T db pg_isready -U postgres
echo ""

# 6. 로그 확인
echo "===== 6. 최근 에러 로그 ====="
docker-compose logs --tail=20 | grep -i "error\|fatal\|exception" | tail -10 || echo "중요한 에러 없음"
echo ""

echo "=========================================="
echo "  문제 해결 완료!"
echo "=========================================="
echo ""
echo "웹사이트 접속 테스트:"
echo "  http://139.150.11.99/"
echo ""
echo "API 테스트:"
echo "  http://139.150.11.99:8000/health"
echo ""
