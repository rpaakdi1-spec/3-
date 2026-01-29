#!/bin/bash

################################################################################
# UVIS 원격 배포 실행 스크립트
# 로컬에서 실행하여 원격 서버에 배포
################################################################################

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 서버 정보
PROD_SERVER="139.150.11.99"
PROD_USER="root"
PROD_DIR="/root/uvis"

clear
echo -e "${CYAN}"
echo "=========================================="
echo "  🚀 UVIS 원격 배포 실행"
echo "=========================================="
echo -e "${NC}"
echo ""
echo "대상 서버: ${PROD_SERVER}"
echo "사용자: ${PROD_USER}"
echo "프로젝트 경로: ${PROD_DIR}"
echo ""
echo -e "${YELLOW}주의: 이 스크립트는 프로덕션 환경에 배포합니다.${NC}"
echo ""

# 사용자 확인
read -p "배포를 진행하시겠습니까? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
    echo -e "${RED}배포가 취소되었습니다.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}[1/4] 서버 연결 테스트 중...${NC}"

# SSH 연결 테스트
if ssh -o BatchMode=yes -o ConnectTimeout=5 ${PROD_USER}@${PROD_SERVER} exit 2>/dev/null; then
    echo -e "${GREEN}✓ SSH 연결 성공 (키 기반 인증)${NC}"
else
    echo -e "${YELLOW}⚠ SSH 키 인증 실패, 비밀번호 인증을 시도합니다...${NC}"
fi

echo ""
echo -e "${BLUE}[2/4] 원격 서버 상태 확인 중...${NC}"

ssh ${PROD_USER}@${PROD_SERVER} << 'ENDSSH'
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}✓ 서버 접속 성공${NC}"

# 프로젝트 디렉토리 확인
if [ -d "/root/uvis" ]; then
    echo -e "${GREEN}✓ 프로젝트 디렉토리 존재${NC}"
else
    echo -e "${RED}✗ 프로젝트 디렉토리가 없습니다: /root/uvis${NC}"
    exit 1
fi

# Docker 확인
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker 설치됨: $(docker --version | head -1)${NC}"
else
    echo -e "${RED}✗ Docker가 설치되어 있지 않습니다${NC}"
    exit 1
fi

# Docker Compose 확인
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓ Docker Compose 설치됨: $(docker-compose --version | head -1)${NC}"
else
    echo -e "${RED}✗ Docker Compose가 설치되어 있지 않습니다${NC}"
    exit 1
fi

# Git 확인
if command -v git &> /dev/null; then
    echo -e "${GREEN}✓ Git 설치됨: $(git --version | head -1)${NC}"
else
    echo -e "${RED}✗ Git이 설치되어 있지 않습니다${NC}"
    exit 1
fi

# 현재 실행 중인 컨테이너 확인
cd /root/uvis
RUNNING_CONTAINERS=$(docker-compose -f docker-compose.prod.yml ps --services --filter "status=running" | wc -l)
echo -e "${GREEN}✓ 실행 중인 컨테이너: ${RUNNING_CONTAINERS}개${NC}"

ENDSSH

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 서버 상태 확인 실패${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}[3/4] 배포 스크립트 실행 중...${NC}"
echo -e "${YELLOW}(이 작업은 15-20분 정도 소요됩니다)${NC}"
echo ""

# 원격 서버에서 배포 스크립트 실행
ssh ${PROD_USER}@${PROD_SERVER} << 'ENDSSH'
set -e

cd /root/uvis

echo "=========================================="
echo "  배포 스크립트 시작"
echo "=========================================="
echo ""

# Git pull
echo "[1/10] 최신 코드 가져오는 중..."
git fetch origin main
git checkout main
git pull origin main

CURRENT_COMMIT=$(git rev-parse --short HEAD)
echo "현재 커밋: $CURRENT_COMMIT"
git log --oneline -1

echo ""

# 배포 스크립트 실행
if [ -f "deploy_production.sh" ]; then
    echo "[2/10] 배포 스크립트 실행 중..."
    bash deploy_production.sh
else
    echo "⚠ deploy_production.sh를 찾을 수 없습니다. 수동 배포를 진행합니다..."
    
    # 수동 배포
    echo "[2/10] 서비스 중지 중..."
    docker-compose -f docker-compose.prod.yml down
    
    echo "[3/10] 프론트엔드 빌드 중 (캐시 없이)..."
    docker-compose -f docker-compose.prod.yml build --no-cache frontend
    
    echo "[4/10] 백엔드 빌드 중..."
    docker-compose -f docker-compose.prod.yml build backend
    
    echo "[5/10] 서비스 시작 중..."
    docker-compose -f docker-compose.prod.yml up -d
    
    echo "[6/10] 서비스 안정화 대기 중..."
    sleep 15
    
    echo "[7/10] 서비스 상태 확인 중..."
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    echo "=========================================="
    echo "  배포 완료"
    echo "=========================================="
fi

ENDSSH

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}✗ 배포 실패!${NC}"
    echo ""
    echo "문제 해결 방법:"
    echo "1. 서버에 직접 접속하여 로그 확인:"
    echo "   ssh ${PROD_USER}@${PROD_SERVER}"
    echo "   cd ${PROD_DIR}"
    echo "   docker-compose -f docker-compose.prod.yml logs"
    echo ""
    echo "2. 수동으로 서비스 재시작:"
    echo "   docker-compose -f docker-compose.prod.yml restart"
    echo ""
    exit 1
fi

echo ""
echo -e "${BLUE}[4/4] 배포 후 검증 중...${NC}"

# 서비스 상태 확인
ssh ${PROD_USER}@${PROD_SERVER} << 'ENDSSH'
cd /root/uvis

echo ""
echo "서비스 상태:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "Health Check:"

# Backend health check
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Backend: OK"
else
    echo "✗ Backend: Failed"
fi

# Frontend check
if curl -sf http://localhost:3000 > /dev/null 2>&1; then
    echo "✓ Frontend: OK"
else
    echo "✗ Frontend: Failed"
fi

ENDSSH

echo ""
echo -e "${GREEN}"
echo "=========================================="
echo "  ✅ 배포 완료!"
echo "=========================================="
echo -e "${NC}"
echo ""
echo "접속 URL:"
echo "  Frontend:  http://${PROD_SERVER}"
echo "  Backend:   http://${PROD_SERVER}:8000"
echo "  API Docs:  http://${PROD_SERVER}:8000/docs"
echo ""
echo -e "${CYAN}=========================================="
echo "  🧪 다음 단계: 기능 테스트"
echo "==========================================${NC}"
echo ""
echo "1. 브라우저에서 접속:"
echo "   http://${PROD_SERVER}/orders"
echo ""
echo "2. 로그인 (admin 계정)"
echo ""
echo "3. 온도 자동입력 기능 테스트:"
echo "   - '+ 신규 등록' 버튼 클릭"
echo "   - 온도대 선택:"
echo "     • 냉동: -30°C ~ -18°C 자동 입력"
echo "     • 냉장: 0°C ~ 6°C 자동 입력"
echo "     • 상온: -30°C ~ 60°C 자동 입력"
echo ""
echo "4. 주문 등록 완료 테스트"
echo ""
echo -e "${GREEN}배포 성공! 🎉${NC}"
echo ""

# 모니터링 명령어 안내
echo -e "${CYAN}=========================================="
echo "  📊 모니터링 명령어"
echo "==========================================${NC}"
echo ""
echo "서버 로그 확인:"
echo "  ssh ${PROD_USER}@${PROD_SERVER} 'cd ${PROD_DIR} && docker-compose -f docker-compose.prod.yml logs -f'"
echo ""
echo "특정 서비스 로그:"
echo "  ssh ${PROD_USER}@${PROD_SERVER} 'cd ${PROD_DIR} && docker-compose -f docker-compose.prod.yml logs -f frontend'"
echo ""
echo "서비스 재시작:"
echo "  ssh ${PROD_USER}@${PROD_SERVER} 'cd ${PROD_DIR} && docker-compose -f docker-compose.prod.yml restart'"
echo ""
