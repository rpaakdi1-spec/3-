#!/bin/bash

# 500 오류 수정 배포 스크립트
# 작성일: 2026-01-30
# 설명: 백엔드 시간 필드 변환 안정화

set -e

echo "=================================="
echo "500 오류 수정 배포 시작"
echo "=================================="
echo ""

# 1. 현재 위치 확인
echo "📍 Step 1: 현재 디렉토리 확인"
pwd
echo ""

# 2. Git 업데이트
echo "📥 Step 2: 최신 코드 가져오기"
git fetch origin genspark_ai_developer
git checkout genspark_ai_developer
git pull origin genspark_ai_developer
echo "✅ 코드 업데이트 완료"
echo ""

# 3. 백엔드 재시작
echo "🔄 Step 3: 백엔드 재시작"
docker-compose -f docker-compose.prod.yml restart backend
echo "✅ 백엔드 재시작 완료"
echo ""

# 4. 백엔드 상태 확인
echo "📊 Step 4: 백엔드 상태 확인"
sleep 5
docker-compose -f docker-compose.prod.yml ps backend
echo ""

# 5. 백엔드 로그 확인
echo "📋 Step 5: 백엔드 로그 확인 (최근 30줄)"
docker-compose -f docker-compose.prod.yml logs backend --tail=30
echo ""

echo "=================================="
echo "✅ 배포 완료!"
echo "=================================="
echo ""
echo "다음 단계:"
echo "1. 브라우저에서 http://139.150.11.99/orders 새로고침"
echo "2. F12 눌러 Network 탭 확인"
echo "3. GET /api/v1/orders/ 요청이 200 OK인지 확인"
echo "4. 주문 목록이 정상적으로 로드되는지 확인"
echo ""
echo "문제가 계속되면 다음 명령으로 상세 로그 확인:"
echo "./debug_500_error.sh"
echo ""
