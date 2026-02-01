#!/bin/bash

# 422 오류 수정사항 긴급 배포 스크립트
# 실행 위치: /root/uvis

set -e

echo "=========================================="
echo "  OrderModal 422 오류 수정 배포"
echo "=========================================="
echo ""

# 1. 최신 코드 가져오기
echo "📥 Step 1: 최신 코드 가져오기..."
git fetch origin genspark_ai_developer
git checkout genspark_ai_developer
git pull origin genspark_ai_developer
echo "✅ 최신 코드 (Commit: cea862c)"
echo ""

# 2. 프론트엔드 리빌드
echo "🔨 Step 2: 프론트엔드 리빌드..."
docker-compose -f docker-compose.prod.yml stop frontend
docker-compose -f docker-compose.prod.yml build --no-cache frontend
docker-compose -f docker-compose.prod.yml up -d frontend
sleep 5
echo "✅ 프론트엔드 재시작 완료"
echo ""

# 3. 상태 확인
echo "📊 Step 3: 상태 확인..."
docker-compose -f docker-compose.prod.yml ps
echo ""

# 4. 프론트엔드 로그 확인
echo "📝 Step 4: 프론트엔드 로그..."
docker-compose -f docker-compose.prod.yml logs frontend --tail=20
echo ""

echo "=========================================="
echo "  ✅ 배포 완료!"
echo "=========================================="
echo ""
echo "수정 내용:"
echo "  - order_date 초기값: '' → 오늘 날짜 (YYYY-MM-DD)"
echo "  - order_number 초기값: '' → ORD-{timestamp}"
echo "  - pickup/delivery 시간: '' → 09:00~18:00"
echo "  - requested_delivery_date: '' → 오늘 날짜"
echo ""
echo "다음 단계:"
echo "  1. 브라우저 새로고침 (Ctrl+Shift+R 또는 캐시 삭제)"
echo "  2. http://139.150.11.99/orders 접속"
echo "  3. '신규 등록' 버튼 클릭"
echo "  4. 자동 입력된 값 확인:"
echo "     ✅ 주문번호: ORD-1738217123456 (자동 생성)"
echo "     ✅ 주문일자: 2026-01-30 (오늘)"
echo "     ✅ 희망 배송일: 2026-01-30 (오늘)"
echo "     ✅ 시간: 09:00 ~ 18:00"
echo "  5. 폼 입력:"
echo "     - 온도대: FROZEN 선택"
echo "     - 팔레트: 10 입력"
echo "     - 거래처 선택: 상차/하차 거래처 선택"
echo "  6. '등록' 버튼 클릭"
echo "  7. 성공 확인: '주문이 등록되었습니다' 토스트"
echo ""
echo "문제 계속 발생 시:"
echo "  - ./debug_422_error.sh 실행하여 상세 로그 확인"
echo "  - 브라우저 F12 → Network 탭에서 Request Payload 캡처"
echo ""
