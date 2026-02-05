#!/bin/bash

###############################################################################
# UVIS 시스템 자동 백업 스크립트
# 용도: 데이터베이스, 파일, 설정 백업
# 실행: ./backup.sh
###############################################################################

set -e

# ===== 설정 =====
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DATE_SHORT=$(date +%Y%m%d)
RETENTION_DAYS=30

# 데이터베이스 설정
DB_NAME="${DB_NAME:-uvis_db}"
DB_USER="${DB_USER:-uvis_user}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# S3 설정 (선택사항)
S3_ENABLED="${S3_ENABLED:-false}"
S3_BUCKET="${S3_BUCKET:-uvis-backups}"
S3_REGION="${S3_REGION:-ap-northeast-2}"

# Slack 알림 설정 (선택사항)
SLACK_ENABLED="${SLACK_ENABLED:-false}"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"

# ===== 로그 함수 =====
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

send_slack_notification() {
    if [ "$SLACK_ENABLED" = "true" ] && [ -n "$SLACK_WEBHOOK" ]; then
        local message="$1"
        local color="${2:-good}"
        
        curl -X POST "$SLACK_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d "{
                \"attachments\": [{
                    \"color\": \"$color\",
                    \"text\": \"$message\",
                    \"footer\": \"UVIS Backup System\",
                    \"ts\": $(date +%s)
                }]
            }" > /dev/null 2>&1
    fi
}

# ===== 백업 디렉토리 생성 =====
mkdir -p "$BACKUP_DIR"/{database,files,config,logs}

# ===== 시작 =====
log "===== 백업 시작 ====="
START_TIME=$(date +%s)

# ===== 1. 데이터베이스 백업 =====
log "데이터베이스 백업 시작..."
DB_BACKUP_FILE="$BACKUP_DIR/database/db_${DATE}.sql.gz"

if PGPASSWORD="$DB_PASSWORD" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --format=custom \
    --compress=9 \
    | gzip > "$DB_BACKUP_FILE"; then
    
    DB_SIZE=$(du -h "$DB_BACKUP_FILE" | cut -f1)
    log "✓ 데이터베이스 백업 완료: $DB_BACKUP_FILE ($DB_SIZE)"
else
    error "✗ 데이터베이스 백업 실패"
    send_slack_notification "❌ Database backup failed" "danger"
    exit 1
fi

# ===== 2. 파일 백업 (uploads) =====
log "파일 백업 시작..."
FILES_BACKUP="$BACKUP_DIR/files/files_${DATE}.tar.gz"

if [ -d "/app/uploads" ]; then
    if tar -czf "$FILES_BACKUP" -C /app uploads 2>/dev/null; then
        FILES_SIZE=$(du -h "$FILES_BACKUP" | cut -f1)
        log "✓ 파일 백업 완료: $FILES_BACKUP ($FILES_SIZE)"
    else
        error "✗ 파일 백업 실패"
    fi
else
    log "⚠ /app/uploads 디렉토리가 없습니다. 파일 백업 건너뜀."
fi

# ===== 3. 설정 파일 백업 =====
log "설정 파일 백업 시작..."
CONFIG_BACKUP="$BACKUP_DIR/config/config_${DATE}.tar.gz"

tar -czf "$CONFIG_BACKUP" \
    -C /opt/uvis \
    .env \
    docker-compose.yml \
    nginx/nginx.conf \
    monitoring/ \
    2>/dev/null || true

CONFIG_SIZE=$(du -h "$CONFIG_BACKUP" | cut -f1)
log "✓ 설정 파일 백업 완료: $CONFIG_BACKUP ($CONFIG_SIZE)"

# ===== 4. S3 업로드 (선택사항) =====
if [ "$S3_ENABLED" = "true" ]; then
    log "S3 업로드 시작..."
    
    # AWS CLI 확인
    if ! command -v aws &> /dev/null; then
        error "AWS CLI가 설치되어 있지 않습니다."
    else
        # 데이터베이스 백업 업로드
        if aws s3 cp "$DB_BACKUP_FILE" \
            "s3://$S3_BUCKET/database/" \
            --region "$S3_REGION" \
            --storage-class STANDARD_IA; then
            log "✓ 데이터베이스 백업 S3 업로드 완료"
        else
            error "✗ 데이터베이스 백업 S3 업로드 실패"
        fi
        
        # 파일 백업 업로드
        if [ -f "$FILES_BACKUP" ]; then
            if aws s3 cp "$FILES_BACKUP" \
                "s3://$S3_BUCKET/files/" \
                --region "$S3_REGION" \
                --storage-class STANDARD_IA; then
                log "✓ 파일 백업 S3 업로드 완료"
            else
                error "✗ 파일 백업 S3 업로드 실패"
            fi
        fi
        
        # 설정 백업 업로드
        if aws s3 cp "$CONFIG_BACKUP" \
            "s3://$S3_BUCKET/config/" \
            --region "$S3_REGION"; then
            log "✓ 설정 백업 S3 업로드 완료"
        else
            error "✗ 설정 백업 S3 업로드 실패"
        fi
    fi
fi

# ===== 5. 오래된 백업 삭제 =====
log "오래된 백업 정리 중..."

find "$BACKUP_DIR/database" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR/files" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR/config" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

DELETED_COUNT=$(find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS 2>/dev/null | wc -l)
log "✓ $DELETED_COUNT개의 오래된 백업 파일 삭제 완료"

# ===== 6. 백업 검증 =====
log "백업 검증 중..."

if [ -f "$DB_BACKUP_FILE" ] && [ -s "$DB_BACKUP_FILE" ]; then
    log "✓ 데이터베이스 백업 검증 완료"
else
    error "✗ 데이터베이스 백업 파일이 비어있거나 존재하지 않습니다!"
    send_slack_notification "❌ Database backup verification failed" "danger"
    exit 1
fi

# ===== 완료 =====
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

log "===== 백업 완료 ====="
log "소요 시간: ${DURATION}초"
log "백업 위치: $BACKUP_DIR"

# Slack 알림
BACKUP_SUMMARY="✅ Backup completed successfully
• Database: $DB_SIZE
• Files: $FILES_SIZE
• Config: $CONFIG_SIZE
• Duration: ${DURATION}s
• Retention: ${RETENTION_DAYS} days"

send_slack_notification "$BACKUP_SUMMARY" "good"

# 로그 저장
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup completed - Duration: ${DURATION}s" \
    >> "$BACKUP_DIR/logs/backup_${DATE_SHORT}.log"

exit 0
