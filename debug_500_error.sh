#!/bin/bash

# 500 오류 디버깅 스크립트
# 작성일: 2026-01-30

echo "=================================="
echo "백엔드 500 오류 디버깅"
echo "=================================="
echo ""

echo "📋 Step 1: 백엔드 컨테이너 상태 확인"
docker-compose -f docker-compose.prod.yml ps backend
echo ""

echo "📋 Step 2: 백엔드 최근 로그 (100줄)"
docker-compose -f docker-compose.prod.yml logs backend --tail=100
echo ""

echo "📋 Step 3: 주문 API 관련 오류 필터링"
docker-compose -f docker-compose.prod.yml logs backend --tail=200 | grep -A 20 -B 5 "orders\|500\|error\|Error\|Exception"
echo ""

echo "📋 Step 4: Python 에러 스택 트레이스"
docker-compose -f docker-compose.prod.yml logs backend --tail=300 | grep -A 30 "Traceback"
echo ""

echo "=================================="
echo "디버깅 완료"
echo "=================================="
