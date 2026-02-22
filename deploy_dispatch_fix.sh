#!/bin/bash

echo "======================================"
echo "배차 최적화 수정 사항 배포"
echo "======================================"
echo ""
echo "수정 내용:"
echo "  - /optimize 엔드포인트가 CVRPTW 알고리즘 사용하도록 수정"
echo "  - 기본 최적화 실행 시간 15초로 설정"
echo ""
echo "======================================"
echo ""

# 프로덕션 서버 정보
SERVER="root@139.150.11.99"
PROJECT_DIR="/root/uvis"

echo "📦 1. 수정된 파일을 서버에 복사..."
scp backend/app/api/dispatches.py $SERVER:$PROJECT_DIR/backend/app/api/

echo ""
echo "🔄 2. 백엔드 컨테이너 재시작..."
ssh $SERVER "cd $PROJECT_DIR && docker restart uvis-backend"

echo ""
echo "⏳ 3. 컨테이너 시작 대기 (10초)..."
sleep 10

echo ""
echo "✅ 4. 배포 완료 확인..."
ssh $SERVER "docker ps | grep uvis-backend"

echo ""
echo "======================================"
echo "✅ 배포 완료!"
echo "======================================"
echo ""
echo "테스트 명령:"
echo "  python3 test_dispatch_flow.py"
echo ""
