#!/bin/bash

# 온도대 Enum 값 수정 배포 스크립트
# 작성일: 2026-01-30
# 설명: temperature_zone 값을 백엔드 한글 Enum과 일치하도록 수정

set -e

echo "=================================="
echo "온도대 Enum 값 수정 배포 시작"
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

# 3. 프론트엔드 재빌드 (캐시 제거)
echo "🏗️  Step 3: 프론트엔드 재빌드 (캐시 제거)"
docker-compose -f docker-compose.prod.yml stop frontend
docker-compose -f docker-compose.prod.yml build --no-cache frontend
echo "✅ 프론트엔드 빌드 완료"
echo ""

# 4. 프론트엔드 재시작
echo "🚀 Step 4: 프론트엔드 재시작"
docker-compose -f docker-compose.prod.yml up -d frontend
echo "✅ 프론트엔드 시작 완료"
echo ""

# 5. 상태 확인
echo "📊 Step 5: 컨테이너 상태 확인"
docker-compose -f docker-compose.prod.yml ps
echo ""

# 6. 로그 확인
echo "📋 Step 6: 프론트엔드 로그 확인 (최근 50줄)"
docker-compose -f docker-compose.prod.yml logs frontend --tail=50
echo ""

echo "=================================="
echo "✅ 배포 완료!"
echo "=================================="
echo ""
echo "다음 단계:"
echo "1. 브라우저 캐시 완전 삭제 (Ctrl+Shift+Delete)"
echo "2. http://139.150.11.99/orders 접속"
echo "3. 신규 등록 버튼 클릭"
echo "4. 온도대 선택: 냉동, 냉장, 상온 중 선택"
echo "5. 등록 버튼 클릭하여 성공 확인"
echo ""
