#!/bin/bash

# 프로덕션 배포 스크립트
# 사용법: ./deploy.sh [start|stop|restart|status|logs]

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경 변수 확인
check_env() {
    log_info "환경 변수 확인 중..."
    
    if [ ! -f .env ]; then
        log_error ".env 파일이 없습니다."
        log_info ".env.example을 복사하여 .env 파일을 생성하세요."
        exit 1
    fi
    
    # 필수 환경 변수 확인
    source .env
    
    required_vars=(
        "SECRET_KEY"
        "DB_PASSWORD"
        "REDIS_PASSWORD"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_error "필수 환경 변수가 설정되지 않았습니다: $var"
            exit 1
        fi
    done
    
    log_info "환경 변수 확인 완료 ✓"
}

# 사전 배포 점검
pre_deploy_check() {
    log_info "사전 배포 점검 시작..."
    
    # Docker 확인
    if ! command -v docker &> /dev/null; then
        log_error "Docker가 설치되어 있지 않습니다."
        exit 1
    fi
    
    # Docker Compose 확인
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose가 설치되어 있지 않습니다."
        exit 1
    fi
    
    # 디스크 공간 확인
    available_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$available_space" -lt 10 ]; then
        log_warn "디스크 공간이 부족합니다: ${available_space}GB"
    fi
    
    log_info "사전 배포 점검 완료 ✓"
}

# 서비스 시작
start_services() {
    log_info "서비스 시작 중..."
    
    check_env
    pre_deploy_check
    
    # Docker 이미지 빌드
    log_info "Docker 이미지 빌드 중..."
    docker-compose -f docker-compose.prod.yml build
    
    # 서비스 시작
    log_info "컨테이너 시작 중..."
    docker-compose -f docker-compose.prod.yml up -d
    
    # 헬스체크 대기
    log_info "서비스 헬스체크 대기 중..."
    sleep 10
    
    # 헬스체크
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "서비스가 정상적으로 시작되었습니다 ✓"
        log_info "API 문서: http://localhost:8000/docs"
    else
        log_error "서비스 헬스체크 실패"
        log_info "로그를 확인하세요: docker-compose -f docker-compose.prod.yml logs"
        exit 1
    fi
}

# 서비스 중지
stop_services() {
    log_info "서비스 중지 중..."
    docker-compose -f docker-compose.prod.yml down
    log_info "서비스가 중지되었습니다 ✓"
}

# 서비스 재시작
restart_services() {
    log_info "서비스 재시작 중..."
    stop_services
    start_services
}

# 서비스 상태 확인
check_status() {
    log_info "서비스 상태 확인 중..."
    docker-compose -f docker-compose.prod.yml ps
}

# 로그 확인
view_logs() {
    service=${2:-all}
    if [ "$service" = "all" ]; then
        docker-compose -f docker-compose.prod.yml logs -f
    else
        docker-compose -f docker-compose.prod.yml logs -f "$service"
    fi
}

# 백업
backup_data() {
    log_info "데이터 백업 시작..."
    
    backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # PostgreSQL 백업
    log_info "데이터베이스 백업 중..."
    docker-compose -f docker-compose.prod.yml exec -T postgres \
        pg_dump -U coldchain coldchain_dispatch > "$backup_dir/database.sql"
    
    # Redis 백업
    log_info "Redis 백업 중..."
    docker-compose -f docker-compose.prod.yml exec -T redis \
        redis-cli --rdb "$backup_dir/redis.rdb" || true
    
    # 압축
    tar -czf "$backup_dir.tar.gz" "$backup_dir"
    rm -rf "$backup_dir"
    
    log_info "백업 완료: $backup_dir.tar.gz ✓"
}

# 무중단 배포
zero_downtime_deploy() {
    log_info "무중단 배포 시작..."
    
    # 백업
    backup_data
    
    # 새 버전 빌드
    log_info "새 버전 빌드 중..."
    docker-compose -f docker-compose.prod.yml build backend
    
    # 롤링 업데이트
    log_info "롤링 업데이트 시작..."
    docker-compose -f docker-compose.prod.yml up -d --no-deps backend
    
    # 헬스체크
    sleep 10
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "무중단 배포 완료 ✓"
    else
        log_error "헬스체크 실패. 이전 버전으로 롤백하세요."
        exit 1
    fi
}

# 메인 스크립트
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        check_status
        ;;
    logs)
        view_logs "$@"
        ;;
    backup)
        backup_data
        ;;
    deploy)
        zero_downtime_deploy
        ;;
    *)
        echo "사용법: $0 {start|stop|restart|status|logs [service]|backup|deploy}"
        echo ""
        echo "명령어:"
        echo "  start   - 서비스 시작"
        echo "  stop    - 서비스 중지"
        echo "  restart - 서비스 재시작"
        echo "  status  - 서비스 상태 확인"
        echo "  logs    - 로그 확인 (옵션: 서비스명)"
        echo "  backup  - 데이터 백업"
        echo "  deploy  - 무중단 배포"
        exit 1
        ;;
esac
