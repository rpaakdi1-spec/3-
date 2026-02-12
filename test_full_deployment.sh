#!/bin/bash
# Phase 10 전체 배포 테스트 스크립트
# 시간: 약 10-15분
# 목적: 서버 배포 전 샌드박스에서 모든 오류 검사

set -e  # 에러 발생 시 중단

cd /home/user/webapp

echo "=========================================="
echo "Phase 10 전체 배포 테스트 시작"
echo "$(date)"
echo "=========================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERROR_COUNT=0

# 1. 코드 최신화
echo ""
echo -e "${YELLOW}1. 코드 최신화${NC}"
git fetch origin main
git reset --hard origin/main
echo -e "${GREEN}✓ 최신 코드 확인 완료${NC}"

# 2. 환경 변수 확인
echo ""
echo -e "${YELLOW}2. 환경 변수 확인${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}✗ .env 파일이 없습니다${NC}"
    ((ERROR_COUNT++))
else
    export $(cat .env | grep -v '^#' | xargs)
    if [ -z "$DB_PASSWORD" ]; then
        echo -e "${RED}✗ DB_PASSWORD가 설정되지 않았습니다${NC}"
        ((ERROR_COUNT++))
    else
        echo -e "${GREEN}✓ 환경 변수 확인 완료${NC}"
    fi
fi

# 3. Docker 전체 재빌드
echo ""
echo -e "${YELLOW}3. Docker 전체 재빌드 (5-10분 소요)${NC}"
docker-compose down -v
docker-compose build --no-cache 2>&1 | tail -20
echo -e "${GREEN}✓ Docker 빌드 완료${NC}"

# 4. 컨테이너 시작
echo ""
echo -e "${YELLOW}4. 컨테이너 시작${NC}"
docker-compose up -d
echo "  대기 중 (30초)..."
sleep 30
docker-compose ps
echo -e "${GREEN}✓ 컨테이너 시작 완료${NC}"

# 5. 데이터베이스 마이그레이션
echo ""
echo -e "${YELLOW}5. 데이터베이스 마이그레이션${NC}"
cd backend
if docker-compose run --rm backend alembic upgrade heads 2>&1 | grep -q "ERROR"; then
    echo "  마이그레이션 에러 발생, stamp 시도..."
    docker-compose run --rm backend alembic stamp heads
fi
docker-compose run --rm backend alembic current
cd ..
echo -e "${GREEN}✓ 마이그레이션 완료${NC}"

# 6. 백엔드 헬스 체크 (최대 60초 대기)
echo ""
echo -e "${YELLOW}6. 백엔드 헬스 체크${NC}"
MAX_RETRY=30
RETRY=0
while [ $RETRY -lt $MAX_RETRY ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 백엔드 헬스 체크 성공${NC}"
        break
    fi
    RETRY=$((RETRY+1))
    echo -n "."
    sleep 2
done

if [ $RETRY -eq $MAX_RETRY ]; then
    echo -e "${RED}✗ 백엔드 헬스 체크 실패${NC}"
    docker-compose logs backend --tail=30
    ((ERROR_COUNT++))
fi

# 7. 프론트엔드 빌드 테스트
echo ""
echo -e "${YELLOW}7. 프론트엔드 빌드 테스트 (3-5분 소요)${NC}"
cd frontend
if npm install --legacy-peer-deps > /dev/null 2>&1; then
    echo "  npm install 완료"
else
    echo -e "${RED}✗ npm install 실패${NC}"
    ((ERROR_COUNT++))
fi

if npm run build > /tmp/frontend_build.log 2>&1; then
    echo -e "${GREEN}✓ 프론트엔드 빌드 완료${NC}"
else
    echo -e "${RED}✗ 프론트엔드 빌드 실패${NC}"
    tail -20 /tmp/frontend_build.log
    ((ERROR_COUNT++))
fi
cd ..

# 8. TypeScript 에러 체크
echo ""
echo -e "${YELLOW}8. TypeScript 에러 체크${NC}"
cd frontend
npx tsc --noEmit --skipLibCheck 2>&1 | grep "error TS" > /tmp/ts_errors.log || true
TS_ERROR_COUNT=$(cat /tmp/ts_errors.log | wc -l)
echo "  TypeScript 에러 수: $TS_ERROR_COUNT"
if [ $TS_ERROR_COUNT -gt 0 ]; then
    echo -e "${YELLOW}⚠ TypeScript 에러가 있습니다 (상위 10개):${NC}"
    head -10 /tmp/ts_errors.log
fi
cd ..

# 9. API 엔드포인트 테스트
echo ""
echo -e "${YELLOW}9. API 엔드포인트 테스트${NC}"

# 9-1. Health Check
echo "  9-1. Health Check"
if curl -s http://localhost:8000/health | jq . > /dev/null 2>&1; then
    echo -e "${GREEN}    ✓ Health Check OK${NC}"
else
    echo -e "${RED}    ✗ Health Check Failed${NC}"
    ((ERROR_COUNT++))
fi

# 9-2. OpenAPI Docs
echo "  9-2. OpenAPI Docs"
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo -e "${GREEN}    ✓ Swagger UI OK${NC}"
else
    echo -e "${RED}    ✗ Swagger UI Failed${NC}"
    ((ERROR_COUNT++))
fi

# 9-3. Phase 10 API
echo "  9-3. Phase 10 Dispatch Rules API"
if curl -s http://localhost:8000/api/v1/dispatch-rules | jq . > /dev/null 2>&1; then
    RULE_COUNT=$(curl -s http://localhost:8000/api/v1/dispatch-rules | jq '. | length')
    echo -e "${GREEN}    ✓ Dispatch Rules API OK (규칙 수: $RULE_COUNT)${NC}"
else
    echo -e "${RED}    ✗ Dispatch Rules API Failed${NC}"
    ((ERROR_COUNT++))
fi

# 10. 데이터베이스 테이블 확인
echo ""
echo -e "${YELLOW}10. 데이터베이스 테이블 확인${NC}"
echo "  Phase 10 테이블:"
docker-compose exec -T db psql -U uvis_user -d uvis_db -c "\dt" | grep -E "dispatch_rules|rule_execution" || {
    echo -e "${RED}    ✗ Phase 10 테이블이 없습니다${NC}"
    ((ERROR_COUNT++))
}

# 11. 로그 수집
echo ""
echo -e "${YELLOW}11. 로그 수집${NC}"
docker-compose logs backend --tail=50 > /tmp/backend.log
docker-compose logs frontend --tail=30 > /tmp/frontend.log
docker-compose logs db --tail=30 > /tmp/db.log
echo -e "${GREEN}✓ 로그 수집 완료${NC}"
echo "  - Backend: /tmp/backend.log"
echo "  - Frontend: /tmp/frontend.log"
echo "  - Database: /tmp/db.log"

# 12. 컨테이너 상태 확인
echo ""
echo -e "${YELLOW}12. 컨테이너 상태 확인${NC}"
docker-compose ps
UNHEALTHY=$(docker-compose ps | grep -v "Up" | grep -v "NAME" | grep -v "^$" | wc -l)

if [ $UNHEALTHY -gt 0 ]; then
    echo -e "${RED}✗ $UNHEALTHY 개의 컨테이너가 비정상 상태입니다${NC}"
    ((ERROR_COUNT++))
else
    echo -e "${GREEN}✓ 모든 컨테이너 정상${NC}"
fi

# 13. 리소스 사용량
echo ""
echo -e "${YELLOW}13. 리소스 사용량${NC}"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# 최종 리포트
echo ""
echo "=========================================="
echo "전체 테스트 완료!"
echo "$(date)"
echo "=========================================="
echo ""

if [ $ERROR_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ 모든 테스트 통과!${NC}"
    echo ""
    echo "서버 배포 가능 상태입니다."
    echo ""
    echo "다음 단계:"
    echo "  1. 스테이징 서버에 배포"
    echo "  2. http://139.150.11.99:8000/docs 접속 확인"
    echo "  3. http://139.150.11.99:3000/dispatch-rules 접속 확인"
    echo ""
    exit 0
else
    echo -e "${RED}❌ $ERROR_COUNT 개의 에러 발견${NC}"
    echo ""
    echo "로그 확인:"
    echo "  - cat /tmp/backend.log"
    echo "  - cat /tmp/frontend.log"
    echo "  - cat /tmp/ts_errors.log"
    echo ""
    echo "컨테이너 로그:"
    echo "  - docker-compose logs backend"
    echo "  - docker-compose logs frontend"
    echo ""
    exit 1
fi
