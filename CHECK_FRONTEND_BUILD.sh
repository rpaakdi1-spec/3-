#!/bin/bash
# 프론트엔드 빌드 확인 스크립트

echo "====================================================================="
echo "프론트엔드 빌드 파일 확인"
echo "====================================================================="
echo ""

cd /root/uvis

echo "=== 1. 빌드된 파일 목록 ==="
docker-compose exec frontend ls -lh /usr/share/nginx/html/assets/ | head -10
echo ""

echo "=== 2. 사이드바 관련 코드 확인 (운영 관리, 실시간 배차 모니터링) ==="
docker-compose exec frontend sh -c "grep -o '운영 관리\|실시간 배차 모니터링\|AI & 최적화\|커뮤니케이션' /usr/share/nginx/html/assets/index-*.js 2>/dev/null | head -10" || echo "키워드 검색 중..."
echo ""

echo "=== 3. LayoutWrapper 확인 (App.tsx) ==="
grep -A 5 "dispatch-monitoring" frontend/src/App.tsx | head -10
echo ""

echo "=== 4. 프론트엔드 최근 액세스 로그 ==="
docker-compose exec frontend tail -20 /var/log/nginx/access.log 2>/dev/null || echo "로그 파일 없음 (정상)"
echo ""

echo "====================================================================="
echo "✅ 확인 완료!"
echo "====================================================================="
echo ""
echo "🎯 다음 단계:"
echo "1. 브라우저에서 접속: http://139.150.11.99/dispatch-monitoring"
echo "2. Ctrl+Shift+R (하드 리프레시) 실행"
echo "3. 왼쪽 사이드바 확인"
echo ""
