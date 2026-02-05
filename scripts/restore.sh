#!/bin/bash

###############################################################################
# UVIS 시스템 복구 스크립트
# 용도: 백업으로부터 데이터베이스 및 파일 복구
# 사용법: ./restore.sh <backup_date>
# 예시: ./restore.sh 20260205_030000
###############################################################################

set -e

# ===== 설정 =====
BACKUP_DIR="/backups"
BACKUP_DATE="$1"

# 데이터베이스 설정
DB_NAME="${DB_NAME:-uvis_db}"
DB_USER="${DB_USER:-uvis_user}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# ===== 로그 함수 =====
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

# ===== 사용법 확인 =====
if [ -z "$BACKUP_DATE" ]; then
    error "사용법: $0 <backup_date>"
    echo ""
    echo "사용 가능한 백업:"
    ls -lh "$BACKUP_DIR/database/" | grep "db_" | awk '{print $9}'
    exit 1
fi

# ===== 백업 파일 확인 =====
DB_BACKUP_FILE="$BACKUP_DIR/database/db_${BACKUP_DATE}.sql.gz"
FILES_BACKUP="$BACKUP_DIR/files/files_${BACKUP_DATE}.tar.gz"
CONFIG_BACKUP="$BACKUP_DIR/config/config_${BACKUP_DATE}.tar.gz"

if [ ! -f "$DB_BACKUP_FILE" ]; then
    error "데이터베이스 백업 파일을 찾을 수 없습니다: $DB_BACKUP_FILE"
    exit 1
fi

# ===== 확인 프롬프트 =====
log "===== 복구 작업 시작 ====="
log "백업 날짜: $BACKUP_DATE"
log "데이터베이스: $DB_BACKUP_FILE"
log "파일: $FILES_BACKUP"
log "설정: $CONFIG_BACKUP"
echo ""
read -p "정말로 복구하시겠습니까? 현재 데이터가 덮어씌워집니다. (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    log "복구 취소됨"
    exit 0
fi

START_TIME=$(date +%s)

# ===== 1. 서비스 중지 =====
log "서비스 중지 중..."
cd /opt/uvis
docker-compose stop backend || true
log "✓ 서비스 중지 완료"

# ===== 2. 데이터베이스 복구 =====
log "데이터베이스 복구 시작..."

# 기존 데이터베이스 백업
log "기존 데이터베이스 백업 중..."
PGPASSWORD="$DB_PASSWORD" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --format=custom \
    | gzip > "$BACKUP_DIR/database/db_before_restore_$(date +%Y%m%d_%H%M%S).sql.gz" || true

# 데이터베이스 삭제 및 재생성
log "데이터베이스 재생성 중..."
PGPASSWORD="$DB_PASSWORD" psql \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d postgres \
    -c "DROP DATABASE IF EXISTS $DB_NAME;" || true

PGPASSWORD="$DB_PASSWORD" psql \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d postgres \
    -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# 백업 복구
log "백업 데이터 복구 중..."
gunzip < "$DB_BACKUP_FILE" | \
    PGPASSWORD="$DB_PASSWORD" pg_restore \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --no-owner \
    --no-acl \
    --if-exists \
    --clean

log "✓ 데이터베이스 복구 완료"

# ===== 3. 파일 복구 (선택사항) =====
if [ -f "$FILES_BACKUP" ]; then
    log "파일 복구 시작..."
    
    # 기존 파일 백업
    if [ -d "/app/uploads" ]; then
        log "기존 파일 백업 중..."
        tar -czf "$BACKUP_DIR/files/files_before_restore_$(date +%Y%m%d_%H%M%S).tar.gz" \
            -C /app uploads || true
    fi
    
    # 백업 복구
    log "백업 파일 복구 중..."
    tar -xzf "$FILES_BACKUP" -C /app
    
    # 권한 설정
    chmod -R 755 /app/uploads
    
    log "✓ 파일 복구 완료"
else
    log "⚠ 파일 백업이 없습니다. 파일 복구 건너뜀."
fi

# ===== 4. 설정 파일 복구 (선택사항) =====
if [ -f "$CONFIG_BACKUP" ]; then
    read -p "설정 파일도 복구하시겠습니까? (yes/no): " RESTORE_CONFIG
    
    if [ "$RESTORE_CONFIG" = "yes" ]; then
        log "설정 파일 복구 시작..."
        
        # 기존 설정 백업
        tar -czf "$BACKUP_DIR/config/config_before_restore_$(date +%Y%m%d_%H%M%S).tar.gz" \
            -C /opt/uvis .env docker-compose.yml nginx/ monitoring/ || true
        
        # 백업 복구
        tar -xzf "$CONFIG_BACKUP" -C /opt/uvis
        
        log "✓ 설정 파일 복구 완료"
        log "⚠ 설정이 변경되었습니다. 서비스를 재시작하세요."
    fi
fi

# ===== 5. 서비스 재시작 =====
log "서비스 재시작 중..."
cd /opt/uvis
docker-compose up -d

# 서비스 확인
log "서비스 상태 확인 중..."
sleep 10

if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    log "✓ 서비스가 정상적으로 시작되었습니다."
else
    error "✗ 서비스 시작 실패. 로그를 확인하세요."
    docker-compose logs backend
    exit 1
fi

# ===== 완료 =====
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

log "===== 복구 완료 ====="
log "소요 시간: ${DURATION}초"
log "복구된 백업: $BACKUP_DATE"

echo ""
log "복구 후 확인 사항:"
log "1. 웹 대시보드 접속 확인"
log "2. 데이터 무결성 확인"
log "3. 주요 기능 테스트"

exit 0
