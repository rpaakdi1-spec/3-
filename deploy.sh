#!/bin/bash
# =============================================================================
# UVIS 배차 시스템 빠른 배포 스크립트
# 작성일: 2026-02-22
# 용도: 서버에서 최신 코드 배포 및 검증
# =============================================================================

set -e  # 에러 발생 시 즉시 중단

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 UVIS 배차 시스템 배포 시작"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. 코드 업데이트
echo "📥 1/6: Git 코드 업데이트..."
cd /root/uvis
git pull origin main
echo "✅ 코드 업데이트 완료"
echo ""

# 2. 백업 스크립트 확인
echo "💾 2/6: 백업 스크립트 확인..."
if [ ! -f "/root/uvis/backup_database.sh" ]; then
    echo "⚠️  백업 스크립트가 없습니다. 생성 중..."
    cat > /root/uvis/backup_database.sh << 'BACKUP_EOF'
#!/bin/bash
BACKUP_DIR="/root/uvis/backups"
LOG_FILE="/var/log/db_backup.log"
DB_CONTAINER=$(docker ps --format '{{.Names}}' | grep -iE '(uvis.*db|.*postgres|.*db)' | head -1)

if [ -z "$DB_CONTAINER" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ DB 컨테이너를 찾을 수 없습니다" | tee -a "$LOG_FILE"
  exit 1
fi

DB_NAME="uvis_db"
DB_USER="uvis_user"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/uvis_backup_$TIMESTAMP.sql"

mkdir -p "$BACKUP_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📦 백업 시작 (컨테이너: $DB_CONTAINER)" | tee -a "$LOG_FILE"

docker exec $DB_CONTAINER pg_dump -U $DB_USER $DB_NAME > "$BACKUP_FILE" 2>&1

if [ $? -eq 0 ] && [ -s "$BACKUP_FILE" ]; then
  gzip "$BACKUP_FILE"
  FILE_SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 백업 성공! 파일 크기: $FILE_SIZE" | tee -a "$LOG_FILE"
  
  find "$BACKUP_DIR" -name "uvis_backup_*.sql.gz" -mtime +30 -delete 2>/dev/null
  
  TOTAL=$(ls -1 "$BACKUP_DIR"/uvis_backup_*.sql.gz 2>/dev/null | wc -l)
  TOTAL_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📊 총 $TOTAL 개 백업 파일, 용량 $TOTAL_SIZE" | tee -a "$LOG_FILE"
  exit 0
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 백업 실패" | tee -a "$LOG_FILE"
  rm -f "$BACKUP_FILE"
  exit 1
fi
BACKUP_EOF
    chmod +x /root/uvis/backup_database.sh
    echo "✅ 백업 스크립트 생성 완료"
else
    echo "✅ 백업 스크립트 확인 완료"
fi

# Cron 등록 확인
if ! crontab -l 2>/dev/null | grep -q "backup_database.sh"; then
    echo "⚠️  Cron 작업이 등록되지 않았습니다. 등록 중..."
    (crontab -l 2>/dev/null; echo "0 2 * * * /root/uvis/backup_database.sh >> /var/log/db_backup.log 2>&1") | crontab -
    echo "✅ Cron 작업 등록 완료 (매일 02:00)"
else
    echo "✅ Cron 작업 확인 완료"
fi
echo ""

# 3. 환경 변수 확인
echo "🔧 3/6: 환경 변수 확인..."
if grep -q "^#.*GEMINI_API_KEY" /root/uvis/.env 2>/dev/null; then
    echo "⚠️  GEMINI_API_KEY가 주석 처리되어 있습니다. 활성화 중..."
    sed -i 's/^# *GEMINI_API_KEY=/GEMINI_API_KEY=/' /root/uvis/.env
    echo "✅ GEMINI_API_KEY 활성화 완료"
elif grep -q "^GEMINI_API_KEY" /root/uvis/.env 2>/dev/null; then
    echo "✅ GEMINI_API_KEY 활성화 확인 완료"
else
    echo "⚠️  GEMINI_API_KEY가 .env 파일에 없습니다. 수동 추가가 필요합니다."
fi
echo ""

# 4. 백엔드 업데이트
echo "🔄 4/6: 백엔드 코드 업데이트..."
docker cp /root/uvis/backend/app/api/v1/endpoints/dispatch_rules.py \
    uvis-backend:/app/app/api/v1/endpoints/
echo "✅ 백엔드 파일 복사 완료"
echo ""

# 5. 백엔드 재시작
echo "♻️  5/6: 백엔드 재시작..."
cd /root/uvis
docker-compose restart backend
echo "⏳ 백엔드 시작 대기 (30초)..."
sleep 30
echo "✅ 백엔드 재시작 완료"
echo ""

# 6. 시스템 진단
echo "🔍 6/6: 시스템 진단 실행..."
if [ -f "/root/uvis/system_diagnosis.sh" ]; then
    /root/uvis/system_diagnosis.sh
else
    echo "⚠️  system_diagnosis.sh 파일이 없습니다."
    echo "ℹ️  수동으로 API 테스트를 진행하세요:"
    echo "   curl -s -X POST http://localhost:8000/api/v1/auth/login \\"
    echo "     -H 'Content-Type: application/x-www-form-urlencoded' \\"
    echo "     -d 'username=admin&password=admin123'"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 배포 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 다음 단계:"
echo "   1. 웹 UI 접속: http://139.150.11.99/dispatch-rules"
echo "   2. 대시보드 접속: http://139.150.11.99/dashboard"
echo "   3. 백엔드 로그 확인: docker logs uvis-backend --tail 50"
echo "   4. 백업 테스트: /root/uvis/backup_database.sh"
echo "   5. 충돌 감지 테스트: (위 스크립트 참조)"
echo ""
echo "📝 상세 가이드:"
echo "   - DEPLOYMENT_SUMMARY.md (영문)"
echo "   - FINAL_STATUS_REPORT_KO.md (한글)"
echo ""
