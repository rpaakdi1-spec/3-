#!/bin/bash
# 🚀 서버 Frontend 재빌드 자동화 스크립트
# 날짜: 2026-02-08
# 용도: /root/uvis에서 실행하여 Frontend를 완전히 재빌드

set -e  # 오류 시 중단

echo "========================================="
echo "🚀 Frontend 재빌드 시작"
echo "========================================="
echo ""

# 현재 위치 확인
echo "📍 Step 1: 현재 위치 확인"
pwd
echo ""

# 충돌 파일 제거
echo "🗑️  Step 2: 충돌 파일 제거"
rm -f fix_services.sh server_recovery_check.sh
cd frontend
rm -f fix_services.sh server_recovery_check.sh
cd ..
echo "✅ 충돌 파일 제거 완료"
echo ""

# 최신 코드 가져오기
echo "📥 Step 3: 최신 코드 가져오기"
cd frontend
git pull origin main
cd ..
echo "✅ 최신 코드 가져오기 완료"
echo ""

# 컨테이너 중지 및 제거
echo "🛑 Step 4: 컨테이너 중지 및 제거"
docker-compose stop frontend nginx
docker-compose rm -f frontend nginx
echo "✅ 컨테이너 중지 및 제거 완료"
echo ""

# 재빌드
echo "🔨 Step 5: Frontend 재빌드 (시간 소요: 2-5분)"
docker-compose build --no-cache frontend
echo "✅ Frontend 재빌드 완료"
echo ""

# 컨테이너 시작
echo "🚀 Step 6: 컨테이너 시작"
docker-compose up -d frontend nginx
echo "✅ 컨테이너 시작 완료"
echo ""

# 대기
echo "⏳ Step 7: 30초 대기 중..."
sleep 30
echo ""

# 상태 확인
echo "========================================="
echo "📊 최종 상태 확인"
echo "========================================="
echo ""

echo "1️⃣ 컨테이너 상태:"
docker-compose ps
echo ""

echo "2️⃣ 빌드 날짜:"
ls -lh frontend/dist/index.html
echo ""

echo "3️⃣ Frontend 로그 (최근 20줄):"
docker-compose logs frontend --tail=20
echo ""

echo "========================================="
echo "🎯 테스트 명령어"
echo "========================================="
echo ""
echo "# Frontend 접속 테스트"
echo "curl -I http://localhost/"
echo ""
echo "# API 테스트"
echo "curl http://localhost:8000/api/v1/dispatch-rules/ | jq ."
echo ""
echo "# 브라우저 접속"
echo "http://139.150.11.99/"
echo "http://139.150.11.99/dispatch-rules"
echo ""

echo "========================================="
echo "✅ 재빌드 완료!"
echo "========================================="
echo ""
echo "⚠️  브라우저에서 Ctrl + Shift + R로 강력 새로고침 하세요!"
