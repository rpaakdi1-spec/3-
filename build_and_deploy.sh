#!/bin/bash
# 🚀 Frontend 빌드 및 배포 자동화 스크립트
# 날짜: 2026-02-08
# 용도: 서버에서 실행하여 최신 코드로 빌드 및 배포

set -e  # 오류 시 중단

echo "========================================="
echo "🚀 Frontend 빌드 및 배포 시작"
echo "========================================="
echo ""

# 현재 위치 확인
echo "📍 Step 1: 현재 위치 확인"
cd /root/uvis
pwd
echo ""

# 최신 코드 가져오기
echo "📥 Step 2: 최신 코드 가져오기"
git fetch origin main
git pull origin main
echo "✅ 최신 코드 가져오기 완료"
echo ""

# Frontend 디렉토리로 이동
echo "📂 Step 3: Frontend 디렉토리로 이동"
cd frontend
pwd
echo ""

# 의존성 설치
echo "📦 Step 4: 의존성 설치 (2-5분 소요)"
npm install --legacy-peer-deps
echo "✅ 의존성 설치 완료"
echo ""

# 빌드 실행
echo "🔨 Step 5: Frontend 빌드 (30-60초 소요)"
npm run build
echo "✅ Frontend 빌드 완료"
echo ""

# 빌드 결과 확인
echo "📊 Step 6: 빌드 결과 확인"
echo "빌드 날짜:"
ls -lh dist/index.html
echo ""
echo "파일 목록:"
ls -la dist/
echo ""

# 메인 디렉토리로 이동
cd /root/uvis

# 컨테이너 재시작
echo "🔄 Step 7: Frontend 컨테이너 재시작"
docker-compose stop frontend
docker-compose up -d frontend
echo "✅ Frontend 컨테이너 재시작 완료"
echo ""

# 대기
echo "⏳ Step 8: 10초 대기 중..."
sleep 10
echo ""

# 상태 확인
echo "========================================="
echo "📊 최종 상태 확인"
echo "========================================="
echo ""

echo "1️⃣ 컨테이너 상태:"
docker-compose ps frontend
echo ""

echo "2️⃣ Frontend 로그 (최근 20줄):"
docker-compose logs frontend --tail=20
echo ""

echo "3️⃣ 접속 테스트:"
curl -I http://localhost/
echo ""

echo "========================================="
echo "🎯 브라우저 접속 안내"
echo "========================================="
echo ""
echo "1. 브라우저에서 강력 새로고침:"
echo "   - Chrome/Firefox: Ctrl + Shift + R"
echo "   - Mac: Cmd + Shift + R"
echo ""
echo "2. 접속 URL:"
echo "   - 메인: http://139.150.11.99/"
echo "   - Rule Builder: http://139.150.11.99/dispatch-rules"
echo ""
echo "3. 확인사항:"
echo "   - 좌측 사이드바 → '스마트 배차 규칙' (한글)"
echo "   - Rule Builder 페이지 → 2개 규칙 카드"
echo "   - Visual Builder 정상 작동"
echo ""

echo "========================================="
echo "✅ 빌드 및 배포 완료!"
echo "========================================="
echo ""
echo "⚠️  브라우저에서 Ctrl + Shift + R로 강력 새로고침 하세요!"
