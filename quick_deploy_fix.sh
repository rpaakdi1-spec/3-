#!/bin/bash

# 배차 최적화 엔드포인트 수정 - 빠른 배포 스크립트
# 사용법: ./quick_deploy_fix.sh

set -e

echo "=================================================="
echo "배차 최적화 엔드포인트 수정 배포"
echo "=================================================="
echo ""

SERVER="root@139.150.11.99"
REMOTE_PATH="/root/uvis/backend/app/api"
LOCAL_FILE="backend/app/api/dispatches.py"

# 1. 파일 존재 확인
if [ ! -f "$LOCAL_FILE" ]; then
    echo "❌ 에러: $LOCAL_FILE 파일을 찾을 수 없습니다."
    exit 1
fi

echo "✓ 로컬 파일 확인: $LOCAL_FILE"
echo ""

# 2. 파일 백업 및 복사
echo "📤 서버로 파일 복사 중..."
echo "   실행할 명령어:"
echo "   scp $LOCAL_FILE $SERVER:$REMOTE_PATH/"
echo ""
echo "   수동으로 실행하세요:"
echo ""
echo "   scp $LOCAL_FILE $SERVER:$REMOTE_PATH/"
echo ""
read -p "파일을 복사했습니까? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 배포 취소"
    exit 1
fi

# 3. Docker 재시작
echo ""
echo "🔄 Docker 컨테이너 재시작..."
echo "   실행할 명령어:"
echo "   ssh $SERVER 'cd /root/uvis && docker restart uvis-backend'"
echo ""
echo "   수동으로 실행하세요:"
echo ""
echo "   ssh $SERVER 'cd /root/uvis && docker restart uvis-backend'"
echo ""
read -p "컨테이너를 재시작했습니까? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 배포 취소"
    exit 1
fi

# 4. 테스트
echo ""
echo "🧪 배포 확인 테스트..."
echo ""
echo "다음 명령어로 테스트하세요:"
echo ""
echo "1. 컨테이너 상태 확인:"
echo "   ssh $SERVER 'docker ps | grep uvis-backend'"
echo ""
echo "2. 로그 확인 (에러가 없어야 함):"
echo "   ssh $SERVER 'docker logs uvis-backend --tail 30'"
echo ""
echo "3. API 테스트:"
echo "   ssh $SERVER 'curl -X POST \"http://localhost:8000/api/v1/dispatches/optimize\" -H \"Content-Type: application/json\" -d '\''{ \"order_ids\": [1, 2], \"vehicle_ids\": [], \"dispatch_date\": \"2026-02-19\" }'\'' | jq .'"
echo ""
echo "4. 통합 테스트 (로컬에서):"
echo "   python3 test_dispatch_flow.py"
echo ""

echo "=================================================="
echo "✅ 배포 가이드 출력 완료"
echo "=================================================="
echo ""
echo "📋 자세한 내용은 DEPLOY_OPTIMIZATION_FIX.md 참조"
