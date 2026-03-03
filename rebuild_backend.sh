#!/bin/bash
cd /root/uvis
echo "🔄 최신 코드 확인..."
git pull origin main

echo "🏗️ 백엔드 이미지 재빌드..."
docker compose build backend

echo "🚀 백엔드 컨테이너 재시작..."
docker compose up -d backend

echo "⏳ 백엔드 시작 대기 (20초)..."
sleep 20

echo "✅ 컨테이너 상태 확인..."
docker compose ps backend

echo "✅ 백엔드 헬스체크..."
curl -s http://139.150.11.99/api/v1/health | jq '.' || echo "헬스체크 실패"

echo ""
echo "✅ 배포 완료!"
