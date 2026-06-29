#!/bin/bash
# ============================================================
# 위치공유 방(Room) 시스템 배포 스크립트
# 사용법: cd /root/uvis && bash deploy_location_rooms.sh
# ============================================================

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "=========================================="
echo "  📍 위치공유 방(Room) 시스템 배포"
echo "=========================================="
echo -e "${NC}"

# 현재 디렉토리 확인
if [ ! -f "docker-compose.yml" ] && [ ! -f "docker-compose.yaml" ]; then
    echo -e "${RED}❌ 오류: /root/uvis 디렉토리에서 실행해주세요${NC}"
    echo -e "${YELLOW}실행 방법: cd /root/uvis && bash deploy_location_rooms.sh${NC}"
    exit 1
fi

echo -e "${BLUE}📁 현재 디렉토리: $(pwd)${NC}"

# ===== 1단계: 코드 업데이트 =====
echo ""
echo -e "${YELLOW}━━━ 1단계: 코드 업데이트 ━━━${NC}"
git pull origin genspark_ai_developer
echo -e "${GREEN}✅ 코드 업데이트 완료${NC}"

# ===== 2단계: DB 마이그레이션 =====
echo ""
echo -e "${YELLOW}━━━ 2단계: DB 마이그레이션 ━━━${NC}"
echo "위치공유 방 테이블 생성 중..."

cat backend/migrations/create_location_rooms.sql | \
    docker compose exec -T db psql -U uvis_user -d uvis_db

echo -e "${GREEN}✅ DB 마이그레이션 완료${NC}"

# 테이블 확인
echo ""
echo "📊 생성된 테이블 확인:"
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT tablename, 
       pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('location_rooms', 'room_locations', 'room_documents')
ORDER BY tablename;
"

# ===== 3단계: 백엔드 재빌드 & 재시작 =====
echo ""
echo -e "${YELLOW}━━━ 3단계: 백엔드 재빌드 ━━━${NC}"
docker compose build backend
echo -e "${GREEN}✅ 백엔드 빌드 완료${NC}"

echo ""
echo -e "${YELLOW}━━━ 4단계: 백엔드 재시작 ━━━${NC}"
docker compose up -d backend
echo "서비스 시작 대기 중... (20초)"
sleep 20

# 백엔드 상태 확인
echo "백엔드 상태:"
docker compose ps backend

# API 테스트
echo ""
echo "API 엔드포인트 테스트:"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
if [ "$STATUS" = "200" ]; then
    echo -e "${GREEN}✅ 백엔드 API 정상 (HTTP $STATUS)${NC}"
else
    echo -e "${YELLOW}⚠️  백엔드 상태 확인 필요 (HTTP $STATUS)${NC}"
    echo "로그 확인:"
    docker compose logs backend --tail=20
fi

# ===== 4단계: 프론트엔드 재빌드 =====
echo ""
echo -e "${YELLOW}━━━ 5단계: 프론트엔드 재빌드 ━━━${NC}"
docker compose build frontend
echo -e "${GREEN}✅ 프론트엔드 빌드 완료${NC}"

echo ""
docker compose stop frontend
docker compose rm -f frontend
docker compose up -d frontend
echo "프론트엔드 시작 대기 중... (10초)"
sleep 10

# ===== 완료 =====
echo ""
echo -e "${CYAN}"
echo "=========================================="
echo "  ✅ 배포 완료!"
echo "=========================================="
echo -e "${NC}"
echo ""
echo -e "${GREEN}📍 새로운 기능:${NC}"
echo ""
echo -e "  ${BLUE}관리자 페이지${NC}"
echo "  → 사이드바 '위치공유 방' 메뉴 클릭"
echo "  → 방 생성 → 기사/고객사 링크 복사"
echo ""
echo -e "  ${BLUE}기사 모바일 페이지${NC}"
echo "  → /room/driver/{기사토큰}"
echo "  → GPS 시작 → 서류 사진 업로드 → 완료"
echo ""
echo -e "  ${BLUE}고객사 위치 조회${NC}"
echo "  → /room/client/{고객토큰}"
echo "  → 실시간 지도 + 서류 확인"
echo ""
echo "서비스 상태:"
docker compose ps
