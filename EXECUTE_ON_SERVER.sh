#!/bin/bash
################################################################################
# 🚀 프로덕션 서버 배포 실행 스크립트
# 
# 이 스크립트를 프로덕션 서버에서 실행하세요:
# ssh root@139.150.11.99 'bash -s' < EXECUTE_ON_SERVER.sh
#
# 또는 서버에 직접 접속 후:
# cd /root/uvis
# bash EXECUTE_ON_SERVER.sh
################################################################################

set -e  # Exit on error

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 배너
echo "════════════════════════════════════════════════════════════════"
echo "  🚀 Phase 1-3 ML 배차 시스템 프로덕션 배포"
echo "════════════════════════════════════════════════════════════════"
echo ""

# 현재 위치 확인
log_info "현재 디렉토리: $(pwd)"
log_info "사용자: $(whoami)"
echo ""

# Step 1: 저장소 업데이트
log_info "Step 1/6: Git 저장소 업데이트..."
cd /root/uvis
git fetch origin main
CURRENT_COMMIT=$(git rev-parse HEAD)
LATEST_COMMIT=$(git rev-parse origin/main)

if [ "$CURRENT_COMMIT" = "$LATEST_COMMIT" ]; then
    log_success "이미 최신 버전입니다 (${CURRENT_COMMIT:0:7})"
else
    log_info "업데이트 중: ${CURRENT_COMMIT:0:7} → ${LATEST_COMMIT:0:7}"
    git pull origin main
    log_success "저장소 업데이트 완료"
fi
echo ""

# Step 2: 환경 변수 확인
log_info "Step 2/6: 환경 변수 확인..."
if [ ! -f backend/.env ]; then
    log_error ".env 파일이 없습니다!"
    log_warning "backend/.env.example을 참고하여 .env 파일을 생성하세요"
    exit 1
fi

# OpenAI API 키 확인
if grep -q "OPENAI_API_KEY=your-key-here" backend/.env || ! grep -q "OPENAI_API_KEY=sk-" backend/.env; then
    log_error "OpenAI API 키가 설정되지 않았습니다!"
    log_warning "backend/.env 파일에 OPENAI_API_KEY를 설정하세요"
    exit 1
fi

log_success "환경 변수 확인 완료"
echo ""

# Step 3: Redis 확인 및 시작
log_info "Step 3/6: Redis 확인 및 시작..."
if docker ps | grep -q redis; then
    log_success "Redis가 실행 중입니다"
else
    log_warning "Redis가 실행되지 않았습니다. 시작합니다..."
    docker-compose -f docker-compose.prod.yml up -d redis
    sleep 3
    
    if docker ps | grep -q redis; then
        log_success "Redis 시작 완료"
    else
        log_error "Redis 시작 실패"
        exit 1
    fi
fi
echo ""

# Step 4: Backend 재빌드 및 재시작
log_info "Step 4/6: Backend 재빌드 중... (약 3분 소요)"
docker-compose -f docker-compose.prod.yml up -d --build --no-deps backend

# Backend 시작 대기
log_info "Backend 시작 대기 중..."
for i in {1..30}; do
    if docker ps | grep -q uvis-backend && \
       curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Backend 시작 완료"
        break
    fi
    
    if [ $i -eq 30 ]; then
        log_error "Backend 시작 시간 초과"
        docker logs uvis-backend --tail 50
        exit 1
    fi
    
    echo -n "."
    sleep 2
done
echo ""
echo ""

# Step 5: Frontend 재빌드 및 재시작
log_info "Step 5/6: Frontend 재빌드 중... (약 2분 소요)"
docker-compose -f docker-compose.prod.yml up -d --build --no-deps frontend

# Frontend 시작 대기
log_info "Frontend 시작 대기 중..."
for i in {1..20}; do
    if docker ps | grep -q uvis-frontend; then
        log_success "Frontend 시작 완료"
        break
    fi
    
    if [ $i -eq 20 ]; then
        log_error "Frontend 시작 시간 초과"
        docker logs uvis-frontend --tail 50
        exit 1
    fi
    
    echo -n "."
    sleep 2
done
echo ""
echo ""

# Step 6: 헬스 체크
log_info "Step 6/6: 헬스 체크..."

# 컨테이너 상태 확인
log_info "컨테이너 상태:"
docker ps | grep uvis

# API 헬스 체크
log_info "API 헬스 체크..."
if curl -sf http://localhost:8000/health > /dev/null; then
    log_success "✓ Backend API 정상"
else
    log_error "✗ Backend API 응답 없음"
fi

# Redis 연결 체크
log_info "Redis 연결 체크..."
if docker exec -it uvis-redis redis-cli ping | grep -q PONG; then
    log_success "✓ Redis 연결 정상"
else
    log_error "✗ Redis 연결 실패"
fi

# ML Dispatch API 체크
log_info "ML Dispatch API 체크..."
RESPONSE=$(curl -sf http://localhost:8000/api/ml-dispatch/ab-test/stats 2>&1)
if [ $? -eq 0 ]; then
    log_success "✓ ML Dispatch API 정상"
else
    log_warning "✗ ML Dispatch API 응답 없음 (처음 실행 시 정상)"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
log_success "🎉 배포 완료!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📊 배포 정보:"
echo "  - Backend:  http://139.150.11.99:8000"
echo "  - Frontend: http://139.150.11.99"
echo "  - API Docs: http://139.150.11.99:8000/docs"
echo ""
echo "🔍 다음 단계:"
echo "  1. 브라우저에서 http://139.150.11.99 접속 확인"
echo "  2. 파일럿 롤아웃 시작:"
echo "     ./scripts/gradual_rollout.sh pilot"
echo ""
echo "  3. 자동 모니터링 시작 (1시간):"
echo "     nohup ./scripts/monitor_pilot.sh > logs/monitor_output.log 2>&1 &"
echo ""
echo "  4. 실시간 로그 확인:"
echo "     tail -f logs/monitor_output.log"
echo ""
log_info "자세한 내용은 FINAL_DEPLOYMENT_STEPS.md를 참고하세요"
echo ""
