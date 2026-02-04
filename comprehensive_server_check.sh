#!/bin/bash

echo "=================================================="
echo "🔍 서버 전체 상태 종합 점검"
echo "=================================================="
echo ""

# 1. Git 상태
echo "📦 1. Git 상태 확인"
echo "--------------------------------------------------"
cd /root/uvis || exit 1
echo "현재 브랜치: $(git branch --show-current)"
echo "최신 커밋: $(git log -1 --oneline)"
echo "원격 대비 상태:"
git fetch origin main 2>&1 | grep -v "^$"
git status -sb
echo ""

# 2. Docker 컨테이너 상태
echo "🐳 2. Docker 컨테이너 상태"
echo "--------------------------------------------------"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "NAME|uvis-"
echo ""

# 3. 디스크 사용량
echo "💾 3. 디스크 사용량"
echo "--------------------------------------------------"
df -h /root/uvis
echo ""

# 4. 로그 파일 크기
echo "📝 4. Docker 로그 크기"
echo "--------------------------------------------------"
for container in uvis-backend uvis-frontend uvis-nginx; do
    if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
        log_size=$(docker inspect --format='{{.LogPath}}' $container 2>/dev/null | xargs du -h 2>/dev/null | cut -f1)
        echo "$container: ${log_size:-N/A}"
    fi
done
echo ""

# 5. 백엔드 최근 에러 (broadcasting 제외)
echo "❌ 5. 백엔드 최근 에러 (broadcasting 제외)"
echo "--------------------------------------------------"
docker logs uvis-backend --tail 100 2>&1 | \
    grep -iE "(error|exception|failed|traceback)" | \
    grep -v "broadcasting" | \
    tail -20
echo ""

# 6. Nginx 설정 파일 존재 확인
echo "⚙️  6. Nginx 설정 파일 확인"
echo "--------------------------------------------------"
if [ -f nginx/nginx.conf ]; then
    echo "✅ nginx/nginx.conf 존재"
    echo "파일 크기: $(du -h nginx/nginx.conf | cut -f1)"
    echo "수정 시간: $(stat -c '%y' nginx/nginx.conf | cut -d. -f1)"
else
    echo "❌ nginx/nginx.conf 없음!"
fi

if [ -f nginx/nginx.prod.conf ]; then
    echo "✅ nginx/nginx.prod.conf 존재"
    echo "파일 크기: $(du -h nginx/nginx.prod.conf | cut -f1)"
else
    echo "❌ nginx/nginx.prod.conf 없음!"
fi
echo ""

# 7. 컨테이너 내부 Nginx 설정 확인
echo "🔧 7. 컨테이너 내부 Nginx 설정"
echo "--------------------------------------------------"
docker exec uvis-nginx cat /etc/nginx/nginx.conf 2>&1 | head -30 | grep -E "(user|worker|server|location|proxy_pass)"
echo ""

# 8. 백엔드 파이썬 버전 및 패키지
echo "🐍 8. 백엔드 환경"
echo "--------------------------------------------------"
docker exec uvis-backend python --version 2>&1
docker exec uvis-backend pip list 2>&1 | grep -iE "(fastapi|pydantic|sqlalchemy)" | head -5
echo ""

# 9. 데이터베이스 연결 테스트
echo "🗄️  9. 데이터베이스 연결 테스트"
echo "--------------------------------------------------"
docker exec uvis-db psql -U postgres -d uvis -c "SELECT COUNT(*) as total_orders FROM orders;" 2>&1 | grep -E "(total_orders|[0-9]+)"
docker exec uvis-db psql -U postgres -d uvis -c "SELECT COUNT(*) as total_clients FROM clients;" 2>&1 | grep -E "(total_clients|[0-9]+)"
echo ""

# 10. API 엔드포인트 테스트
echo "🌐 10. API 엔드포인트 테스트"
echo "--------------------------------------------------"
echo "Health Check:"
curl -s http://localhost:8000/health | head -c 100
echo ""
echo ""
echo "Orders List:"
curl -s http://localhost:8000/api/v1/orders/?limit=1 | python3 -m json.tool 2>/dev/null | head -20 || echo "JSON 파싱 실패"
echo ""

# 11. 프론트엔드 빌드 파일 확인
echo "⚛️  11. 프론트엔드 빌드 상태"
echo "--------------------------------------------------"
docker exec uvis-frontend ls -lh /usr/share/nginx/html/ 2>&1 | head -10 || echo "프론트엔드 정적 파일 확인 실패"
echo ""

# 12. 파일 권한 확인
echo "🔐 12. 중요 파일 권한"
echo "--------------------------------------------------"
ls -lh docker-compose.prod.yml nginx/nginx.conf backend/app/api/orders.py 2>&1 | grep -v "total"
echo ""

# 13. 환경 변수 확인 (민감 정보 제외)
echo "🔑 13. 환경 변수 (일부)"
echo "--------------------------------------------------"
docker exec uvis-backend env 2>&1 | grep -E "(DATABASE_URL|API_|NAVER_)" | sed 's/=.*/=***REDACTED***/g'
echo ""

# 14. 최근 코드 변경 사항
echo "📝 14. 최근 코드 변경 (최근 5개 커밋)"
echo "--------------------------------------------------"
git log --oneline -5
echo ""

# 15. 포트 사용 상태
echo "🔌 15. 포트 사용 상태"
echo "--------------------------------------------------"
netstat -tlnp 2>/dev/null | grep -E "(80|8000|5432|6379)" | grep LISTEN
echo ""

echo "=================================================="
echo "✅ 종합 점검 완료"
echo "=================================================="
echo ""
echo "💡 다음 단계:"
echo "1. 위 결과를 확인하고 이상 징후를 찾습니다"
echo "2. 특히 '❌' 표시나 에러 메시지에 주목하세요"
echo "3. 결과를 공유하면 정확한 진단을 도와드립니다"
