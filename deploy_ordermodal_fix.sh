#!/bin/bash

# OrderModal 수정사항 배포 스크립트
# 실행 위치: /root/uvis

set -e  # 오류 발생 시 중단

echo "=========================================="
echo "  OrderModal 수정사항 배포 시작"
echo "=========================================="
echo ""

# 1. 최신 코드 가져오기
echo "📥 Step 1: 최신 코드 가져오기..."
git fetch origin genspark_ai_developer
git checkout genspark_ai_developer
git pull origin genspark_ai_developer
echo "✅ 최신 코드 가져오기 완료"
echo ""

# 2. 프론트엔드 중지
echo "🛑 Step 2: 프론트엔드 컨테이너 중지..."
docker-compose -f docker-compose.prod.yml stop frontend
echo "✅ 프론트엔드 중지 완료"
echo ""

# 3. 프론트엔드 리빌드 (캐시 삭제)
echo "🔨 Step 3: 프론트엔드 리빌드 (캐시 삭제 포함)..."
docker-compose -f docker-compose.prod.yml build --no-cache frontend
echo "✅ 프론트엔드 빌드 완료"
echo ""

# 4. 프론트엔드 시작
echo "🚀 Step 4: 프론트엔드 시작..."
docker-compose -f docker-compose.prod.yml up -d frontend
sleep 5
echo "✅ 프론트엔드 시작 완료"
echo ""

# 5. 상태 확인
echo "📊 Step 5: 컨테이너 상태 확인..."
docker-compose -f docker-compose.prod.yml ps
echo ""

# 6. 로그 확인
echo "📝 Step 6: 프론트엔드 로그 확인..."
docker-compose -f docker-compose.prod.yml logs frontend --tail=30
echo ""

# 완료 메시지
echo ""
echo "=========================================="
echo "  ✅ 배포 완료!"
echo "=========================================="
echo ""
echo "다음 단계:"
echo "1. 브라우저 캐시 삭제 (Ctrl+Shift+Delete 또는 시크릿 모드)"
echo "2. http://139.150.11.99 접속"
echo "3. 주문 관리 → 신규 등록 테스트"
echo ""
echo "테스트 순서:"
echo "  1) 캘린더 페이지: http://139.150.11.99/calendar"
echo "  2) 다음 날짜 클릭 (빈 날짜)"
echo "  3) '주문 등록 페이지로 이동' 클릭"
echo "  4) 주문 관리 페이지에서 '신규 등록' 클릭"
echo "  5) 폼 입력:"
echo "     - 주문번호: 자동 생성 확인"
echo "     - 온도대: FROZEN 선택"
echo "     - 팔레트: 10 입력"
echo "     - 거래처 선택: 상차/하차 거래처 선택"
echo "     - 등록 버튼 클릭"
echo "  6) '주문이 등록되었습니다' 토스트 확인"
echo ""
echo "문제 발생 시:"
echo "  - F12 → Console 탭에서 오류 메시지 확인"
echo "  - Network 탭에서 POST /api/v1/orders/ 요청 확인"
echo "  - 상세 가이드: /root/uvis/ORDERMODAL_FIX_DEPLOYMENT.md"
echo ""
