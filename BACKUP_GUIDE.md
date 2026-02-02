# 🔒 백업 및 복구 가이드

## 📦 백업 현황

### ✅ 최근 백업 파일
- **데이터베이스 백업**: `backup_20260202_161940.sql` (131 bytes)
- **설정 파일 백업**: `config_backup_20260202.tar.gz` (5.6K)
- **백업 위치**: `/root/uvis/backups/`

### 📋 백업에 포함된 파일
```
✅ docker-compose.prod.yml     - Docker Compose 설정
✅ .env                         - 환경 변수
✅ frontend/nginx.conf          - Frontend Nginx 설정
✅ nginx.conf                   - 메인 Nginx 설정
✅ nginx/nginx.prod.conf        - Production Nginx 설정
✅ infrastructure/logging/logstash/logstash.conf - Logstash 설정
```

---

## 🔄 정기 백업 자동화

### 1. 자동 백업 스크립트 생성
```bash
cat > /root/uvis/scripts/auto_backup.sh << 'SCRIPT'
#!/bin/bash

# 백업 디렉토리
BACKUP_DIR="/root/uvis/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DATE_SHORT=$(date +%Y%m%d)

# 백업 디렉토리 생성
mkdir -p "$BACKUP_DIR"

echo "🔄 백업 시작: $DATE"

# 1. 데이터베이스 백업
echo "📦 데이터베이스 백업 중..."
docker exec -t uvis-db pg_dump -U uvisuser -d uvisdb > "$BACKUP_DIR/backup_$DATE.sql"

# 2. 설정 파일 백업
echo "📦 설정 파일 백업 중..."
cd /root/uvis
tar -czf "$BACKUP_DIR/config_backup_$DATE_SHORT.tar.gz" \
    docker-compose.prod.yml \
    .env \
    $(find . -name "*.conf" -type f 2>/dev/null | grep -E "nginx|conf" | head -5)

# 3. 30일 이상 된 백업 삭제
echo "🧹 오래된 백업 정리 중..."
find "$BACKUP_DIR" -name "backup_*.sql" -mtime +30 -delete
find "$BACKUP_DIR" -name "config_backup_*.tar.gz" -mtime +30 -delete

# 4. 백업 결과 확인
echo ""
echo "✅ 백업 완료!"
echo ""
echo "📊 백업 파일 목록:"
ls -lh "$BACKUP_DIR" | tail -10

SCRIPT

chmod +x /root/uvis/scripts/auto_backup.sh
```

### 2. Cron 작업 등록 (매일 새벽 2시 백업)
```bash
# Crontab 편집
crontab -e

# 아래 라인 추가
0 2 * * * /root/uvis/scripts/auto_backup.sh >> /root/uvis/logs/backup.log 2>&1
```

### 3. 즉시 백업 실행 테스트
```bash
cd /root/uvis
bash scripts/auto_backup.sh
```

---

## 🔧 복구 절차

### 데이터베이스 복구
```bash
# 1. 백업 파일 확인
ls -lh /root/uvis/backups/backup_*.sql

# 2. 복구 실행 (주의: 기존 데이터 덮어씌움)
cd /root/uvis
docker exec -i uvis-db psql -U uvisuser -d uvisdb < backups/backup_20260202_161940.sql

# 3. Backend 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 4. 헬스 체크
curl -s http://localhost:8000/health | jq
```

### 설정 파일 복구
```bash
# 1. 백업 파일 확인
ls -lh /root/uvis/backups/config_backup_*.tar.gz

# 2. 백업 내용 확인
tar -tzf backups/config_backup_20260202.tar.gz

# 3. 복구 실행
cd /root/uvis
tar -xzf backups/config_backup_20260202.tar.gz

# 4. 서비스 재시작
docker-compose -f docker-compose.prod.yml restart
```

### 전체 시스템 복구
```bash
# 1. 모든 컨테이너 중지
cd /root/uvis
docker-compose -f docker-compose.prod.yml down

# 2. 설정 파일 복구
tar -xzf backups/config_backup_20260202.tar.gz

# 3. 컨테이너 재시작
docker-compose -f docker-compose.prod.yml up -d

# 4. DB 복구 대기 (30초)
sleep 30

# 5. 데이터베이스 복구
docker exec -i uvis-db psql -U uvisuser -d uvisdb < backups/backup_20260202_161940.sql

# 6. Backend 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 7. 전체 상태 확인
docker ps
curl http://localhost:8000/health
curl http://localhost:80
```

---

## 📊 백업 모니터링

### 백업 상태 확인
```bash
# 최근 백업 파일 목록
ls -lht /root/uvis/backups/ | head -10

# 백업 파일 용량 확인
du -sh /root/uvis/backups/

# 백업 로그 확인
tail -50 /root/uvis/logs/backup.log
```

### 백업 무결성 테스트
```bash
# DB 백업 파일 검증
cd /root/uvis
head -20 backups/backup_20260202_161940.sql

# 설정 파일 백업 검증
tar -tzf backups/config_backup_20260202.tar.gz
```

---

## 🚨 긴급 복구 시나리오

### 시나리오 1: 데이터베이스 손상
```bash
cd /root/uvis

# 1. DB 컨테이너 재시작
docker-compose -f docker-compose.prod.yml restart db

# 2. 30초 대기
sleep 30

# 3. 최신 백업으로 복구
LATEST_BACKUP=$(ls -t backups/backup_*.sql | head -1)
docker exec -i uvis-db psql -U uvisuser -d uvisdb < "$LATEST_BACKUP"

# 4. Backend 재시작
docker-compose -f docker-compose.prod.yml restart backend
```

### 시나리오 2: 설정 파일 손실
```bash
cd /root/uvis

# 1. 최신 설정 백업 복구
LATEST_CONFIG=$(ls -t backups/config_backup_*.tar.gz | head -1)
tar -xzf "$LATEST_CONFIG"

# 2. 전체 재시작
docker-compose -f docker-compose.prod.yml restart
```

### 시나리오 3: 전체 시스템 재구축
```bash
cd /root/uvis

# 1. 전체 중지 및 정리
docker-compose -f docker-compose.prod.yml down -v

# 2. 설정 복구
tar -xzf backups/config_backup_20260202.tar.gz

# 3. 전체 재시작
docker-compose -f docker-compose.prod.yml up -d

# 4. DB 준비 대기
sleep 30

# 5. DB 복구
docker exec -i uvis-db psql -U uvisuser -d uvisdb < backups/backup_20260202_161940.sql

# 6. 검증
docker ps
curl http://localhost:8000/health
```

---

## 📝 베스트 프랙티스

### 백업 전략
- ✅ **일일 백업**: 매일 새벽 2시 자동 백업
- ✅ **보관 기간**: 30일
- ✅ **백업 위치**: `/root/uvis/backups/`
- ✅ **로그 기록**: `/root/uvis/logs/backup.log`

### 백업 전 체크리스트
1. 디스크 공간 확인 (`df -h`)
2. 컨테이너 상태 확인 (`docker ps`)
3. 백업 스크립트 실행
4. 백업 파일 생성 확인
5. 백업 무결성 테스트

### 복구 전 체크리스트
1. 현재 상태 스냅샷 생성
2. 복구할 백업 파일 확인
3. 백업 파일 무결성 검증
4. 복구 절차 리허설
5. 복구 실행 및 검증

---

## 📞 문제 해결

### 백업 실패 시
```bash
# 1. 디스크 공간 확인
df -h

# 2. DB 컨테이너 상태 확인
docker ps | grep uvis-db
docker logs uvis-db --tail 50

# 3. 수동 백업 시도
docker exec -t uvis-db pg_dump -U uvisuser -d uvisdb > /tmp/manual_backup.sql
```

### 복구 실패 시
```bash
# 1. DB 연결 테스트
docker exec -it uvis-db psql -U uvisuser -d uvisdb -c "\l"

# 2. 백업 파일 검증
head -50 backups/backup_20260202_161940.sql

# 3. 에러 로그 확인
docker logs uvis-db --tail 100
docker logs uvis-backend --tail 100
```

---

## 🎯 다음 단계

### 권장 작업
1. ✅ **자동 백업 설정**: Cron 작업 등록
2. ✅ **복구 테스트**: 실제 복구 절차 연습
3. ✅ **모니터링 설정**: 백업 성공/실패 알림
4. ✅ **오프사이트 백업**: 원격 저장소에 백업 복사

### 추가 보안
```bash
# 백업 파일 암호화 (선택)
cd /root/uvis/backups
tar -czf - backup_20260202_161940.sql | openssl enc -aes-256-cbc -salt -out backup_encrypted.tar.gz.enc

# 복호화
openssl enc -d -aes-256-cbc -in backup_encrypted.tar.gz.enc | tar -xz
```

---

**생성일**: 2026-02-02  
**최종 백업**: backup_20260202_161940.sql  
**상태**: ✅ 정상
