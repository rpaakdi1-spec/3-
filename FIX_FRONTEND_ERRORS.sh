#!/bin/bash
# ===================================================================
# Frontend API 에러 수정 배포 스크립트
# ===================================================================

set -e  # 에러 발생 시 중단

echo "====================================================================="
echo "Frontend API 에러 수정 배포 시작"
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
echo "✅ Frontend API 에러 수정 배포 완료!"
echo "====================================================================="
echo ""
echo "🎯 수정된 항목:"
echo "1. ✅ 자동배차최적화 - Orders API status 파라미터 수정 (CONFIRMED → 배차대기)"
echo "2. ✅ 실시간 차량 텔레메트리 - WebSocket URL 중복 경로 수정 (/api/v1/api/v1 → /api/v1)"
echo "3. ✅ 온도모니터링 - API 응답 배열 처리 개선"
echo ""
echo "🧪 테스트 방법:"
echo "1. 브라우저에서 http://139.150.11.99 접속"
echo "2. 캐시 클리어: F12 → Console → localStorage.clear(); sessionStorage.clear(); location.reload();"
echo "3. 로그인 후 다음 페이지 테스트:"
echo "   - 자동배차최적화 (AI & 최적화 > 자동 배차 최적화)"
echo "   - 실시간 차량 텔레메트리 (모니터링 & 분석 > 실시간 차량 텔레메트리)"
echo "   - 온도모니터링 (모니터링 & 분석 > 실시간 온도 모니터링)"
echo ""
echo "⚠️  참고사항:"
echo "- ML 예측 API 400 에러: ML 모델 학습 중이므로 정상 (학습 완료 후 해결)"
echo "- 고급 분석 BI 대시보드 500 에러: 백엔드 데이터 이슈로 추가 조사 필요"
echo ""
