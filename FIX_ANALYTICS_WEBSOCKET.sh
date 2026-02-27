#!/bin/bash
# ===================================================================
# Analytics 페이지 WebSocket 에러 수정 배포 스크립트
# 중복 라우트 제거
# ===================================================================

set -e  # 에러 발생 시 중단

echo "====================================================================="
echo "Analytics 페이지 WebSocket 에러 수정 배포 시작"
echo "====================================================================="
echo ""

# 현재 디렉토리로 이동
cd /root/uvis

# 1. 최신 코드 가져오기
echo "=== 1. 최신 코드 Pull ==="
git pull origin main
echo "✅ 코드 업데이트 완료"
echo ""

# 2. 프론트엔드 재빌드
echo "=== 2. 프론트엔드 컨테이너 재빌드 ==="
docker-compose stop frontend
docker-compose rm -f frontend
docker-compose build --no-cache frontend
echo "✅ 프론트엔드 이미지 재빌드 완료"
echo ""

# 3. 프론트엔드 시작
echo "=== 3. 프론트엔드 컨테이너 시작 ==="
docker-compose up -d frontend
echo "⏳ 프론트엔드 시작 대기 중 (30초)..."
sleep 30
echo ""

# 4. 프론트엔드 상태 확인
echo "=== 4. 프론트엔드 상태 확인 ==="
docker-compose ps frontend
echo ""

# 5. 프론트엔드 로그 확인
echo "=== 5. 최근 프론트엔드 로그 ==="
docker-compose logs frontend --tail 20
echo ""

echo "====================================================================="
echo "✅ Analytics 페이지 WebSocket 에러 수정 배포 완료!"
echo "====================================================================="
echo ""
echo "🎯 주요 변경사항:"
echo "1. ✅ 중복된 /analytics 라우트 제거"
echo "2. ✅ /analytics → AnalyticsPage (통계 및 분석)"
echo "3. ✅ /analytics-dashboard → AnalyticsDashboardPage (고급 분석 & BI)"
echo ""
echo "🧪 테스트 방법:"
echo "1. 브라우저에서 http://139.150.11.99 접속"
echo "2. 캐시 클리어: F12 → Console → localStorage.clear(); location.reload();"
echo "3. 로그인 후 다음 페이지 테스트:"
echo "   - /analytics: 통계 및 분석 페이지 (WebSocket 에러 없음)"
echo "   - /analytics-dashboard: 고급 분석 & BI 대시보드"
echo "4. F12 → Console에서 WebSocket 에러 확인 (없어야 함)"
echo ""
echo "📋 라우트 구조:"
echo "- /analytics              → AnalyticsPage (통계 및 분석)"
echo "- /analytics-dashboard    → AnalyticsDashboardPage (고급 분석 & BI)"
echo ""
