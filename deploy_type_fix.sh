#!/bin/bash

# Order 타입 불일치 수정 배포 스크립트
# 실행 위치: /root/uvis

set -e

echo "=========================================="
echo "  Order 타입 불일치 수정 배포"
echo "=========================================="
echo ""

# 1. 최신 코드 가져오기
echo "📥 Step 1: 최신 코드 가져오기 (Commit: 70a3592)..."
git fetch origin genspark_ai_developer
git checkout genspark_ai_developer
git pull origin genspark_ai_developer
echo "✅ 최신 코드 완료"
echo ""

# 2. 프론트엔드 완전 재빌드
echo "🔨 Step 2: 프론트엔드 완전 재빌드..."
docker-compose -f docker-compose.prod.yml stop frontend
docker-compose -f docker-compose.prod.yml rm -f frontend
docker-compose -f docker-compose.prod.yml build --no-cache frontend
docker-compose -f docker-compose.prod.yml up -d frontend
sleep 10
echo "✅ 프론트엔드 재시작 완료"
echo ""

# 3. 상태 확인
echo "📊 Step 3: 컨테이너 상태 확인..."
docker-compose -f docker-compose.prod.yml ps
echo ""

# 4. 로그 확인
echo "📝 Step 4: 프론트엔드 로그 확인..."
docker-compose -f docker-compose.prod.yml logs frontend --tail=30
echo ""

echo "=========================================="
echo "  ✅ 배포 완료!"
echo "=========================================="
echo ""
echo "🎯 해결된 문제:"
echo "  ❌ React error #31 (렌더링 오류)"
echo "  ❌ 주문 등록 후 오류 페이지 발생"
echo "  ❌ Order 타입과 백엔드 API 불일치"
echo ""
echo "✅ 수정 내용:"
echo "  - Order 타입을 백엔드 스키마에 맞춰 재정의"
echo "  - cargo_type → temperature_zone"
echo "  - client_id → pickup_client_id, delivery_client_id"
echo "  - 주소 직접 입력 필드 추가"
echo "  - 시간/예약/반복 필드 추가"
echo "  - 레거시 필드 유지 (하위 호환성)"
echo ""
echo "🧪 테스트 순서:"
echo "  1. 브라우저 강력 새로고침 (Ctrl+Shift+R)"
echo "     또는 캐시 완전 삭제 (Ctrl+Shift+Delete)"
echo ""
echo "  2. http://139.150.11.99/orders 접속"
echo ""
echo "  3. '신규 등록' 버튼 클릭"
echo ""
echo "  4. 폼 입력:"
echo "     ✅ 주문번호: 자동 생성 확인 (ORD-...)"
echo "     ✅ 주문일자: 오늘 날짜 확인 (2026-01-30)"
echo "     ✅ 온도대: FROZEN 선택"
echo "     ✅ 팔레트: 10 입력"
echo "     ✅ 거래처 선택: 상차/하차 거래처 선택"
echo "     ✅ (또는 주소 직접 입력 탭 클릭)"
echo ""
echo "  5. '등록' 버튼 클릭"
echo ""
echo "  6. ✅ 성공 확인:"
echo "     - '주문이 등록되었습니다' 녹색 토스트"
echo "     - 모달 자동 닫힘"
echo "     - 주문 목록에 새 주문 추가"
echo "     - 온도대 표시 (냉동/냉장/상온)"
echo "     - 거래처명 또는 주소 표시"
echo ""
echo "  7. ❌ 오류 페이지 NO MORE!"
echo ""
echo "문제 계속 발생 시:"
echo "  - 브라우저 캐시 완전 삭제 재시도"
echo "  - 시크릿 모드에서 테스트 (Ctrl+Shift+N)"
echo "  - F12 → Console 탭에서 오류 확인"
echo "  - ./debug_422_error.sh 실행"
echo ""
