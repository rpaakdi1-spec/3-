# UVIS 시스템 배포 가이드

## 📋 목차
1. [사전 요구사항](#사전-요구사항)
2. [초기 설치](#초기-설치)
3. [환경 설정](#환경-설정)
4. [Docker 배포](#docker-배포)
5. [데이터베이스 마이그레이션](#데이터베이스-마이그레이션)
6. [모니터링 설정](#모니터링-설정)
7. [백업 설정](#백업-설정)
8. [트러블슈팅](#트러블슈팅)

---

## 사전 요구사항

### 서버 사양
- **CPU**: 4 코어 이상
- **메모리**: 8GB 이상
- **디스크**: 100GB 이상 (SSD 권장)
- **OS**: Ubuntu 22.04 LTS 또는 CentOS 8

### 소프트웨어
- Docker 24.0+
- Docker Compose 2.20+
- Git 2.30+
- (선택) AWS CLI 2.0+ (S3 백업 사용시)

---

## 초기 설치

### 1. 서버 업데이트
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Docker 설치
```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 설치 확인
docker --version
docker-compose --version
```

### 3. 프로젝트 클론
```bash
cd /opt
sudo git clone https://github.com/rpaakdi1-spec/3-.git uvis
cd uvis
```

---

## 환경 설정

### 1. 환경 변수 파일 생성
```bash
cp .env.example .env
```

### 2. 환경 변수 편집
```bash
nano .env
```

필수 설정 항목:
```bash
# 데이터베이스 (강력한 비밀번호로 변경)
DB_PASSWORD=your_secure_db_password_here

# JWT (최소 32자 이상의 랜덤 문자열)
JWT_SECRET=your_secure_jwt_secret_at_least_32_characters_here

# Redis (강력한 비밀번호로 변경)
REDIS_PASSWORD=your_secure_redis_password_here

# 도메인 설정
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

선택 설정:
```bash
# S3 백업 (선택사항)
S3_ENABLED=true
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
S3_BUCKET=uvis-backups

# Slack 알림 (선택사항)
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 3. 강력한 비밀번호 생성
```bash
# JWT Secret 생성
openssl rand -base64 48

# DB Password 생성
openssl rand -base64 32

# Redis Password 생성
openssl rand -base64 32
```

---

## Docker 배포

### 1. 이미지 빌드
```bash
# 모든 서비스 빌드
docker-compose build

# 또는 개별 빌드
docker-compose build backend
docker-compose build frontend
```

### 2. 서비스 시작
```bash
# 전체 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
```

### 3. 서비스 상태 확인
```bash
# 컨테이너 상태
docker-compose ps

# 헬스 체크
curl http://localhost:8000/api/v1/health
```

---

## 데이터베이스 마이그레이션

### 1. 마이그레이션 실행
```bash
# 최신 마이그레이션 적용
docker-compose exec backend alembic upgrade head

# 마이그레이션 이력 확인
docker-compose exec backend alembic history

# 현재 버전 확인
docker-compose exec backend alembic current
```

### 2. 초기 데이터 생성
```bash
# 관리자 계정 생성 스크립트 실행
docker-compose exec backend python scripts/create_admin.py
```

---

## 모니터링 설정

### 1. 모니터링 스택 시작
```bash
# Prometheus + Grafana 시작
docker-compose --profile monitoring up -d

# 접속 확인
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001 (admin/admin)
```

### 2. Grafana 대시보드 설정
1. http://localhost:3001 접속
2. 초기 비밀번호 변경
3. Data Source 추가: Prometheus (http://prometheus:9090)
4. 대시보드 import: `monitoring/grafana/dashboards/system.json`

---

## 백업 설정

### 1. 백업 스크립트 권한 설정
```bash
chmod +x scripts/backup.sh
chmod +x scripts/restore.sh
```

### 2. Cron 설정
```bash
# Cron 편집
crontab -e

# 매일 새벽 3시 자동 백업
0 3 * * * /opt/uvis/scripts/backup.sh >> /var/log/uvis-backup.log 2>&1
```

### 3. 수동 백업
```bash
# 백업 실행
./scripts/backup.sh

# 백업 확인
ls -lh /backups/database/
```

### 4. 복구 테스트
```bash
# 백업 목록 확인
ls -lh /backups/database/

# 복구 실행
./scripts/restore.sh 20260205_030000
```

---

## SSL/TLS 설정 (HTTPS)

### 1. Let's Encrypt 인증서 발급
```bash
# Certbot 설치
sudo apt install certbot

# 인증서 발급
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# 인증서 위치
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### 2. Nginx SSL 설정
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL 최적화
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location / {
        proxy_pass http://frontend:80;
        # ... 나머지 설정
    }
}

# HTTP to HTTPS 리다이렉트
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### 3. 자동 갱신 설정
```bash
# Cron에 추가
0 0 1 * * certbot renew --quiet && docker-compose restart nginx
```

---

## 무중단 배포 (Blue-Green)

### 1. 블루 환경 준비
```bash
# 현재 실행 중 (Green)
docker-compose up -d

# 새 이미지 빌드 (Blue)
docker-compose build --no-cache
```

### 2. 블루 환경 테스트
```bash
# 테스트 포트로 블루 환경 시작
docker-compose -f docker-compose.blue.yml up -d

# 헬스 체크
curl http://localhost:8001/api/v1/health
```

### 3. 트래픽 전환
```bash
# Nginx 설정 변경 (8000 -> 8001)
# 기존 요청 완료 대기
sleep 30

# Green 환경 중지
docker-compose down

# Blue를 Green으로 승격
docker-compose up -d
```

---

## 성능 최적화

### 1. PostgreSQL 튜닝
```sql
-- /etc/postgresql/postgresql.conf
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10MB
max_worker_processes = 4
max_parallel_workers_per_gather = 2
max_parallel_workers = 4
```

### 2. Redis 튜닝
```conf
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 3. Nginx 튜닝
```nginx
worker_processes auto;
worker_connections 2048;
keepalive_timeout 65;
client_max_body_size 50M;

# 캐싱
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;
proxy_cache_key "$scheme$request_method$host$request_uri";
```

---

## 트러블슈팅

### 데이터베이스 연결 오류
```bash
# 데이터베이스 상태 확인
docker-compose exec db psql -U uvis_user -d uvis_db -c "SELECT 1"

# 로그 확인
docker-compose logs db

# 재시작
docker-compose restart db
```

### 메모리 부족
```bash
# 메모리 사용량 확인
docker stats

# 불필요한 컨테이너 정리
docker system prune -a
```

### 디스크 공간 부족
```bash
# 디스크 사용량 확인
df -h

# Docker 볼륨 정리
docker volume prune

# 오래된 로그 삭제
find /var/log -name "*.log" -mtime +30 -delete
```

### 포트 충돌
```bash
# 포트 사용 확인
sudo netstat -tulpn | grep :8000

# 프로세스 종료
sudo kill -9 <PID>
```

---

## 보안 체크리스트

- [ ] 강력한 비밀번호 사용
- [ ] JWT Secret 변경
- [ ] 방화벽 설정 (UFW)
- [ ] SSH 키 기반 인증
- [ ] 불필요한 포트 차단
- [ ] 정기적인 보안 업데이트
- [ ] SSL/TLS 인증서 적용
- [ ] Rate limiting 활성화
- [ ] 로그 모니터링
- [ ] 정기적인 백업 확인

---

## 유지보수

### 일일 점검
- [ ] 서비스 상태 확인
- [ ] 에러 로그 확인
- [ ] 디스크 사용량 확인
- [ ] 백업 성공 확인

### 주간 점검
- [ ] 보안 업데이트 적용
- [ ] 성능 메트릭 리뷰
- [ ] 백업 복구 테스트
- [ ] 알림 규칙 검토

### 월간 점검
- [ ] 전체 시스템 백업
- [ ] 보안 감사
- [ ] 성능 최적화
- [ ] 용량 계획 검토

---

**배포 가이드 작성 완료**  
**버전**: 1.0.0  
**최종 업데이트**: 2026-02-05
