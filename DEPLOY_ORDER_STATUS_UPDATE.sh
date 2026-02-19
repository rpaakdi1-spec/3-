#!/bin/bash

# 주문 상태 자동 업데이트 기능 배포
# Deploy Order Status Auto-Update Feature
# 작성일: 2026-02-19

echo "=========================================="
echo "🔄 주문 상태 자동 업데이트 기능 배포"
echo "=========================================="
echo ""

# 1. 백엔드 디렉토리로 이동
echo "📂 백엔드 디렉토리로 이동..."
cd /root/uvis/backend

# 2. 현재 상태 확인
echo ""
echo "📋 현재 Git 상태..."
git status

# 3. 변경사항 임시 저장
if ! git diff-index --quiet HEAD --; then
    echo ""
    echo "💾 로컬 변경사항 임시 저장..."
    git stash push -m "deploy_order_status_$(date +%Y%m%d_%H%M%S)"
fi

# 4. 최신 코드 가져오기
echo ""
echo "⬇️ 최신 코드 가져오기..."
git fetch origin main
git reset --hard origin/main

# 5. 최신 커밋 확인
echo ""
echo "✅ 최신 커밋:"
git log --oneline -1

# 6. 변경 내용 확인
echo ""
echo "🔍 주문 상태 업데이트 코드 확인..."
echo ""

echo "1️⃣ OrderStatus import 확인:"
grep -n "from app.models.order import.*OrderStatus" app/services/cvrptw_service.py

echo ""
echo "2️⃣ 주문 상태 업데이트 로직 확인:"
grep -A 3 "주문 상태 업데이트" app/services/cvrptw_service.py

if [ $? -eq 0 ]; then
    echo "✅ 주문 상태 업데이트 코드 확인됨"
else
    echo "❌ 주문 상태 업데이트 코드를 찾을 수 없음"
    exit 1
fi

# 7. 파일을 컨테이너에 복사
echo ""
echo "📦 업데이트된 파일을 컨테이너에 복사..."
docker cp app/services/cvrptw_service.py uvis-backend:/app/app/services/cvrptw_service.py

# 8. Python 캐시 삭제
echo ""
echo "🧹 Python 캐시 삭제..."
docker exec uvis-backend find /app -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
docker exec uvis-backend find /app -type f -name "*.pyc" -delete 2>/dev/null || true

# 9. 컨테이너 재시작
echo ""
echo "🔄 백엔드 컨테이너 재시작..."
docker restart uvis-backend

# 10. 대기
echo ""
echo "⏳ 컨테이너 시작 대기 (10초)..."
sleep 10

# 11. 로그 확인
echo ""
echo "📋 최근 로그 확인..."
docker logs uvis-backend --tail 30

# 12. 헬스체크
echo ""
echo "🏥 헬스체크..."
curl -s http://localhost:8000/api/v1/health | jq .

echo ""
echo "=========================================="
echo "✅ 주문 상태 자동 업데이트 기능 배포 완료!"
echo "=========================================="
echo ""
echo "📋 변경 내용:"
echo "  • 배차 생성 시 주문 상태 자동 업데이트"
echo "  • OrderStatus.PENDING → OrderStatus.ASSIGNED"
echo "  • 로그에 상태 변경 기록"
echo ""
echo "🧪 테스트 방법:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 배차 최적화 실행:"
echo "   curl -X POST 'http://localhost:8000/api/v1/dispatches/optimize' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"order_ids\":[27,28,30],\"vehicle_ids\":[],\"dispatch_date\":\"2026-02-19\"}' | jq ."
echo ""
echo "2. 주문 상태 확인:"
echo "   curl -s 'http://localhost:8000/api/v1/orders/27' | jq '.status'"
echo "   curl -s 'http://localhost:8000/api/v1/orders/28' | jq '.status'"
echo "   curl -s 'http://localhost:8000/api/v1/orders/30' | jq '.status'"
echo ""
echo "3. 예상 결과:"
echo "   \"배차완료\" (ASSIGNED)"
echo ""
echo "4. 백엔드 로그에서 확인:"
echo "   docker logs uvis-backend --tail 50 | grep '주문.*상태 변경'"
echo ""
echo "   예상 로그:"
echo "   → 주문 ORD-20260219-001 상태 변경: 배차대기 → 배차완료"
echo "   → 주문 ORD-20260219-002 상태 변경: 배차대기 → 배차완료"
echo ""
echo "✅ 주문 관리 페이지에서 확인:"
echo "  1. 브라우저에서 주문 관리 페이지 열기"
echo "  2. 배차된 주문의 상태 배지 확인"
echo "  3. '배차완료' 상태로 변경되어야 함"
echo ""
echo "🔄 주문 상태 흐름:"
echo "  배차대기 → 배차완료 → 배송중 → 배송완료"
echo "  (PENDING → ASSIGNED → IN_TRANSIT → DELIVERED)"
echo ""
