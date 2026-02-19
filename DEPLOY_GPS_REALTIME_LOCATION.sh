#!/bin/bash

################################################################################
# 🚗 GPS 실시간 위치 기반 배차 최적화 배포 스크립트
#
# 작성일: 2026-02-19
# 커밋: 1223371
# 목적: 운행 대기 차량의 실시간 GPS 위치를 사용하여 배차 최적화
################################################################################

set -e  # 에러 발생 시 스크립트 중단

echo "========================================="
echo "🚗 GPS 실시간 위치 배차 최적화 배포"
echo "========================================="
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 현재 디렉토리 확인
echo "📂 1. 현재 디렉토리 확인..."
CURRENT_DIR=$(pwd)
echo "   현재 위치: $CURRENT_DIR"

if [[ "$CURRENT_DIR" != *"/uvis"* ]]; then
    echo -e "${YELLOW}⚠️  /root/uvis 디렉토리로 이동하는 것을 권장합니다${NC}"
    echo "   실행 명령: cd /root/uvis"
    read -p "   계속 진행하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ 배포를 취소했습니다${NC}"
        exit 1
    fi
fi
echo ""

# 2. Git 최신 코드 가져오기
echo "🔄 2. Git 최신 코드 가져오기..."
git fetch origin main
echo -e "${GREEN}✅ Git fetch 완료${NC}"
echo ""

# 3. 현재 브랜치 확인
echo "🌿 3. 현재 브랜치 확인..."
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "   현재 브랜치: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${YELLOW}⚠️  현재 브랜치가 main이 아닙니다${NC}"
    read -p "   main 브랜치로 전환하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout main
        echo -e "${GREEN}✅ main 브랜치로 전환 완료${NC}"
    else
        echo -e "${YELLOW}⚠️  현재 브랜치에서 계속 진행합니다${NC}"
    fi
fi
echo ""

# 4. 로컬 변경사항 확인
echo "🔍 4. 로컬 변경사항 확인..."
if [[ -n $(git status -s) ]]; then
    echo -e "${YELLOW}⚠️  로컬에 커밋되지 않은 변경사항이 있습니다:${NC}"
    git status -s
    echo ""
    read -p "   모든 변경사항을 버리고 원격 코드로 덮어쓰시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git reset --hard origin/main
        echo -e "${GREEN}✅ 로컬 변경사항 제거 완료${NC}"
    else
        echo -e "${RED}❌ 로컬 변경사항이 있어 배포를 중단합니다${NC}"
        echo "   변경사항을 커밋하거나 stash 후 다시 시도하세요"
        exit 1
    fi
else
    git reset --hard origin/main
    echo -e "${GREEN}✅ 최신 코드로 업데이트 완료${NC}"
fi
echo ""

# 5. 커밋 해시 확인
echo "🔖 5. 커밋 해시 확인..."
CURRENT_COMMIT=$(git log --oneline -1 | awk '{print $1}')
echo "   현재 커밋: $CURRENT_COMMIT"

EXPECTED_COMMIT="1223371"
if [ "$CURRENT_COMMIT" == "$EXPECTED_COMMIT" ]; then
    echo -e "${GREEN}✅ 올바른 커밋입니다 ($EXPECTED_COMMIT)${NC}"
else
    echo -e "${YELLOW}⚠️  예상 커밋($EXPECTED_COMMIT)과 다릅니다${NC}"
    echo "   현재 커밋: $CURRENT_COMMIT"
    read -p "   계속 진행하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ 배포를 취소했습니다${NC}"
        exit 1
    fi
fi
echo ""

# 6. 변경 파일 확인
echo "📄 6. 변경 파일 확인..."
echo "   주요 변경 파일:"
git show --name-only --oneline HEAD | tail -n +2
echo ""

# 7. 변경 내용 미리보기
echo "🔍 7. 변경 내용 미리보기..."
read -p "   변경 내용을 확인하시겠습니까? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git show HEAD
    echo ""
    read -p "   배포를 계속 진행하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ 배포를 취소했습니다${NC}"
        exit 1
    fi
fi
echo ""

# 8. Docker 컨테이너 상태 확인
echo "🐳 8. Docker 컨테이너 상태 확인..."
if docker ps | grep -q "uvis-backend"; then
    echo -e "${GREEN}✅ uvis-backend 컨테이너가 실행 중입니다${NC}"
else
    echo -e "${RED}❌ uvis-backend 컨테이너가 실행 중이 아닙니다${NC}"
    echo "   컨테이너를 시작하세요: docker start uvis-backend"
    exit 1
fi
echo ""

# 9. 백엔드 재시작
echo "🔄 9. 백엔드 컨테이너 재시작..."
docker restart uvis-backend
echo -e "${GREEN}✅ uvis-backend 재시작 완료${NC}"
echo ""

# 10. 컨테이너 시작 대기
echo "⏳ 10. 컨테이너 시작 대기 (10초)..."
for i in {10..1}; do
    echo -n "$i... "
    sleep 1
done
echo ""
echo -e "${GREEN}✅ 대기 완료${NC}"
echo ""

# 11. 컨테이너 상태 확인
echo "🔍 11. 컨테이너 상태 확인..."
if docker ps | grep -q "uvis-backend"; then
    echo -e "${GREEN}✅ uvis-backend 컨테이너가 정상 실행 중입니다${NC}"
    docker ps | grep "uvis-backend"
else
    echo -e "${RED}❌ uvis-backend 컨테이너가 실행되지 않았습니다${NC}"
    echo "   로그를 확인하세요: docker logs uvis-backend --tail 100"
    exit 1
fi
echo ""

# 12. 백엔드 로그 확인
echo "📋 12. 백엔드 로그 확인 (최근 50줄)..."
docker logs uvis-backend --tail 50
echo ""

# 13. 헬스체크
echo "🏥 13. 헬스체크..."
sleep 5  # 추가 대기
HEALTH_CHECK=$(curl -s http://localhost:8001/health || echo "FAILED")

if [[ "$HEALTH_CHECK" == *"ok"* ]] || [[ "$HEALTH_CHECK" == *"healthy"* ]]; then
    echo -e "${GREEN}✅ 백엔드 헬스체크 성공${NC}"
    echo "   응답: $HEALTH_CHECK"
else
    echo -e "${RED}❌ 백엔드 헬스체크 실패${NC}"
    echo "   응답: $HEALTH_CHECK"
    echo "   로그를 확인하세요: docker logs uvis-backend --tail 100"
    exit 1
fi
echo ""

# 14. GPS 로직 확인
echo "🔍 14. 실시간 GPS 로직 확인..."
if grep -q "latest_location = db.query(VehicleLocation)" backend/app/services/cvrptw_service.py; then
    echo -e "${GREEN}✅ 실시간 GPS 로직이 포함되어 있습니다${NC}"
else
    echo -e "${RED}❌ 실시간 GPS 로직을 찾을 수 없습니다${NC}"
    echo "   파일을 확인하세요: backend/app/services/cvrptw_service.py"
fi
echo ""

# 15. 배포 완료
echo "========================================="
echo -e "${GREEN}✅ 배포가 성공적으로 완료되었습니다!${NC}"
echo "========================================="
echo ""

# 16. 테스트 가이드
echo "📝 테스트 가이드:"
echo ""
echo "1️⃣ 백엔드 로그에서 GPS 사용 확인:"
echo "   docker logs uvis-backend --tail 200 | grep \"GPS\""
echo ""
echo "2️⃣ 데이터베이스에서 GPS 데이터 확인:"
echo "   docker exec -it uvis-db psql -U uvis_user -d uvis_db -c \\"
echo "   \"SELECT v.vehicle_code, vl.latitude, vl.longitude, vl.recorded_at \\"
echo "   \"FROM vehicles v \\"
echo "   \"LEFT JOIN vehicle_locations vl ON v.id = vl.vehicle_id \\"
echo "   \"AND vl.recorded_at >= NOW() - INTERVAL '30 minutes' \\"
echo "   \"ORDER BY vl.recorded_at DESC LIMIT 10;\""
echo ""
echo "3️⃣ AI 배차 최적화 API 테스트:"
echo "   curl -X POST 'http://139.150.11.99:8001/api/v1/dispatches/optimize-cvrptw?use_real_routing=true' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -H 'Authorization: Bearer YOUR_TOKEN' \\"
echo "     -d '{"
echo "       \"order_ids\": [1, 2, 3],"
echo "       \"vehicle_ids\": [1, 2],"
echo "       \"dispatch_date\": \"2026-02-19\","
echo "       \"time_limit\": 30,"
echo "       \"use_time_windows\": true"
echo "     }'"
echo ""
echo "4️⃣ 프론트엔드에서 배차 최적화 실행:"
echo "   http://139.150.11.99/dispatches"
echo "   → 'AI 배차 최적화' 버튼 클릭"
echo "   → 주문 선택 후 '최적화 실행'"
echo ""
echo "========================================="
echo -e "${GREEN}🎉 배포 완료! 테스트를 진행해주세요${NC}"
echo "========================================="
