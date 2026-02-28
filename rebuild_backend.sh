#!/bin/bash
echo "=== 백엔드 재빌드 및 재시작 ==="

# 백엔드 중지
docker compose down backend

# 이미지 재빌드
docker compose build backend

# 백엔드 시작
docker compose up -d backend

# 10초 대기
sleep 10

# 상태 확인
docker compose ps backend

# 로그 확인
docker compose logs backend | tail -30
