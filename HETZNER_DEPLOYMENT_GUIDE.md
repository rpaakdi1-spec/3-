# 🚀 Hetzner Cloud 배포 가이드

**시작일**: 2026-01-28  
**예상 비용**: €4.49/월 ($4.90/월)  
**예상 소요 시간**: 30-45분

---

## 📋 목차
1. [Hetzner 계정 확인](#1-hetzner-계정-확인)
2. [서버 생성](#2-서버-생성)
3. [초기 서버 설정](#3-초기-서버-설정)
4. [애플리케이션 배포](#4-애플리케이션-배포)
5. [도메인 및 SSL 설정](#5-도메인-및-ssl-설정)
6. [모니터링 설정](#6-모니터링-설정)
7. [백업 및 유지보수](#7-백업-및-유지보수)

---

## 1. Hetzner 계정 확인

### 제공된 계정 정보
```
✅ URL: https://accounts.hetzner.com
✅ Client number: K0175799026
✅ Login: rpaakdi@naver.com
✅ Password: @Rkdalsxo8484
```

### Step 1.1: 로그인
1. **브라우저로 접속**: https://console.hetzner.cloud/
2. **로그인 정보 입력**
3. **프로젝트 확인** (없으면 새로 생성: "New Project")

---

## 2. 서버 생성

### Step 2.1: 새 서버 생성
```
1. 좌측 메뉴에서 "Servers" 클릭
2. "Add Server" 버튼 클릭
```

### Step 2.2: 서버 설정
```
📍 Location (위치):
   ✅ Falkenstein (독일) - 가장 저렴
   ⚠️ 또는 Nuremberg, Helsinki (유럽)
   ⚠️ 한국에서 핑 약 250-300ms (Oracle Seoul은 10-30ms)

💻 Image (OS):
   ✅ Ubuntu 22.04 (권장)
   
🖥️ Type (서버 사양):
   ✅ CX22 (권장)
      - 2 vCPU (AMD)
      - 4 GB RAM
      - 40 GB NVMe SSD
      - 20 TB 트래픽
      - €4.49/월 (~$4.90/월)
   
   대안:
   - CX32: 4 vCPU, 8GB RAM, 80GB SSD - €8.49/월 (더 많은 트래픽 필요시)
   - CX22로 시작 → 나중에 업그레이드 가능

🔐 SSH Keys:
   ✅ 새 SSH 키 추가 또는 기존 키 선택
   
   SSH 키 생성 방법 (로컬 PC):
   ```bash
   ssh-keygen -t ed25519 -C "uvis-hetzner-server"
   # 저장 위치: ~/.ssh/id_ed25519
   # Public key 내용을 복사하여 Hetzner에 추가
   cat ~/.ssh/id_ed25519.pub
   ```

🏷️ Server Name:
   ✅ 예: uvis-production-server
   
🌐 Networking:
   ✅ Public IPv4 (자동 할당)
   ⚠️ Private networks 불필요 (단일 서버)
   
🔥 Firewall (선택):
   나중에 설정 가능 (서버에서 UFW 사용 권장)
```

### Step 2.3: 서버 생성 완료
```
✅ "Create & Buy Now" 클릭
✅ 약 30초 후 서버 실행됨
✅ 서버 IP 주소 확인: 예 123.45.67.89
```

---

## 3. 초기 서버 설정

### Step 3.1: SSH 접속
```bash
# 로컬 PC에서 실행
ssh root@123.45.67.89
# 또는 SSH 키 파일 지정
ssh -i ~/.ssh/id_ed25519 root@123.45.67.89
```

### Step 3.2: 서버 업데이트
```bash
# 시스템 업데이트
apt update && apt upgrade -y

# 필수 패키지 설치
apt install -y curl wget git ufw fail2ban
```

### Step 3.3: 방화벽 설정 (UFW)
```bash
# UFW 설정
ufw default deny incoming
ufw default allow outgoing

# 필수 포트 허용
ufw allow 22/tcp      # SSH
ufw allow 80/tcp      # HTTP
ufw allow 443/tcp     # HTTPS
ufw allow 8000/tcp    # Backend API
ufw allow 19999/tcp   # Netdata 모니터링

# 방화벽 활성화
ufw --force enable

# 상태 확인
ufw status verbose
```

### Step 3.4: Fail2Ban 설정 (보안)
```bash
# Fail2Ban 시작
systemctl enable fail2ban
systemctl start fail2ban

# 상태 확인
fail2ban-client status
```

---

## 4. 애플리케이션 배포

### Step 4.1: 배포 스크립트 다운로드
```bash
# 프로젝트 저장소에서 배포 스크립트 다운로드
wget https://raw.githubusercontent.com/rpaakdi1-spec/3-/genspark_ai_developer/deploy-hetzner.sh

# 실행 권한 부여
chmod +x deploy-hetzner.sh
```

### Step 4.2: 배포 스크립트 실행
```bash
# 자동 배포 실행
sudo ./deploy-hetzner.sh

# 배포 과정:
# ✅ Step 1: 시스템 환경 확인
# ✅ Step 2: Docker 및 Docker Compose 설치
# ✅ Step 3: 프로젝트 클론 (GitHub)
# ✅ Step 4: 환경 변수 설정 (.env)
# ✅ Step 5: PostgreSQL 컨테이너 시작
# ✅ Step 6: Redis 컨테이너 시작
# ✅ Step 7: Backend API 시작
# ✅ Step 8: Frontend 빌드 및 Nginx 설정
# ✅ Step 9: 모니터링 (Netdata) 설치
# ✅ Step 10: 헬스체크 및 검증

# 예상 소요 시간: 15-25분
```

### Step 4.3: 수동 배포 (선택)
배포 스크립트가 실패하거나 커스텀이 필요한 경우:

```bash
# 1. Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 2. Docker Compose 설치
apt install docker-compose-plugin -y

# 3. 프로젝트 클론
git clone https://github.com/rpaakdi1-spec/3-.git /opt/uvis
cd /opt/uvis

# 4. 환경 변수 설정
cp .env.example .env
nano .env  # 아래 설정 참고

# 5. Docker Compose 실행
docker compose -f docker-compose.prod.yml up -d

# 6. 로그 확인
docker compose -f docker-compose.prod.yml logs -f
```

### Step 4.4: 환경 변수 설정 (.env)
```bash
# .env 파일 편집
nano /opt/uvis/.env
```

필수 환경 변수:
```env
# 서버 IP 주소로 변경
SERVER_IP=123.45.67.89

# Database
DATABASE_URL=postgresql://uvis_user:uvis_password_change_me@localhost:5432/uvis_db
POSTGRES_USER=uvis_user
POSTGRES_PASSWORD=uvis_password_change_me
POSTGRES_DB=uvis_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
SECRET_KEY=your-secret-key-here-change-me-minimum-32-characters-long

# Frontend
VITE_API_URL=http://123.45.67.89:8000/api/v1
VITE_WS_URL=ws://123.45.67.89:8001/ws

# 네이버 지도 API (선택)
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret

# CORS
CORS_ORIGINS=["http://123.45.67.89","http://localhost:3000"]

# 로깅
LOG_LEVEL=INFO
```

---

## 5. 도메인 및 SSL 설정

### Step 5.1: 도메인 연결 (선택)
도메인이 있는 경우:

```
1. 도메인 DNS 설정 (예: Cloudflare, Namecheap):
   A 레코드: uvis.yourdomain.com → 123.45.67.89
   
2. DNS 전파 대기 (최대 24시간, 보통 5-10분)

3. 확인:
   dig uvis.yourdomain.com
   # 또는
   nslookup uvis.yourdomain.com
```

### Step 5.2: Let's Encrypt SSL 인증서
도메인이 있는 경우 무료 SSL 인증서 설치:

```bash
# Certbot 설치
apt install -y certbot python3-certbot-nginx

# SSL 인증서 발급
certbot --nginx -d uvis.yourdomain.com

# 자동 갱신 설정 (이미 cron에 등록됨)
certbot renew --dry-run

# Nginx 재시작
systemctl reload nginx
```

### Step 5.3: IP 접속 (도메인 없는 경우)
```
✅ Frontend: http://123.45.67.89
✅ Backend API: http://123.45.67.89:8000
✅ API Docs: http://123.45.67.89:8000/docs
✅ Health Check: http://123.45.67.89:8000/health
✅ Monitoring: http://123.45.67.89:19999

⚠️ 주의: HTTP만 사용 (HTTPS는 도메인 필요)
⚠️ WebSocket은 ws:// 프로토콜 사용
```

---

## 6. 모니터링 설정

### Step 6.1: Netdata (이미 설치됨)
```bash
# 접속: http://123.45.67.89:19999

# 모니터링 항목:
✅ CPU 사용률
✅ 메모리 사용률
✅ 디스크 I/O
✅ 네트워크 트래픽
✅ Docker 컨테이너 상태
✅ PostgreSQL 성능
✅ Redis 성능
```

### Step 6.2: 로그 확인
```bash
# Docker 로그
docker compose -f /opt/uvis/docker-compose.prod.yml logs -f

# Backend 로그만
docker compose -f /opt/uvis/docker-compose.prod.yml logs -f backend

# Nginx 로그
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# 시스템 로그
journalctl -u docker -f
```

---

## 7. 백업 및 유지보수

### Step 7.1: 데이터베이스 백업
```bash
# 백업 스크립트 생성
cat > /opt/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# PostgreSQL 백업
docker exec uvis-postgres pg_dump -U uvis_user uvis_db > $BACKUP_DIR/db_backup_$DATE.sql

# 30일 이상 된 백업 삭제
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +30 -delete

echo "Backup completed: db_backup_$DATE.sql"
EOF

chmod +x /opt/backup-db.sh

# Cron 등록 (매일 새벽 3시)
crontab -e
# 추가: 0 3 * * * /opt/backup-db.sh
```

### Step 7.2: 서버 스냅샷 (Hetzner)
```
1. Hetzner Console 접속
2. 서버 선택
3. "Create Snapshot" 클릭 (€0.01/GB/월)
4. 스냅샷 이름: uvis-production-YYYYMMDD
5. 복구 시: "Rebuild from Snapshot"
```

### Step 7.3: 자동 업데이트 (보안 패치)
```bash
# unattended-upgrades 설치
apt install -y unattended-upgrades

# 자동 보안 업데이트 활성화
dpkg-reconfigure -plow unattended-upgrades

# 설정 확인
cat /etc/apt/apt.conf.d/50unattended-upgrades
```

---

## 8. 배포 검증

### Step 8.1: 헬스체크
```bash
# Backend API
curl http://123.45.67.89:8000/health

# 예상 응답:
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "version": "3.0.0"
}
```

### Step 8.2: Frontend 접속
```
브라우저에서: http://123.45.67.89

✅ 로그인 페이지 표시
✅ API 응답 정상
✅ WebSocket 연결 정상
```

### Step 8.3: API 문서
```
브라우저에서: http://123.45.67.89:8000/docs

✅ Swagger UI 표시
✅ 모든 엔드포인트 목록 확인
```

---

## 9. 비용 분석

### 월간 비용
```
💰 Hetzner CX22 서버:      €4.49/월 ($4.90)
💰 스냅샷 (선택, 40GB):    €0.40/월 ($0.44)
💰 추가 백업 (선택):       €0.20/월 ($0.22)
─────────────────────────────────────────
📊 총 월간 비용:           €5.09/월 ($5.56)

📊 AWS 대비 절감액:        $314.44/월 (98.3% 절감)
📊 연간 절감액:            $3,773.28/년
```

### 비용 최적화 팁
```
✅ 스냅샷: 주 1회만 생성 (매일 불필요)
✅ 백업: 로컬 백업 + 필요시 외부 업로드
✅ 트래픽: 20TB 충분 (월 100-500GB 예상)
✅ 업그레이드: CX22로 시작 → 필요시 CX32
```

---

## 10. 문제 해결

### 일반적인 문제

**1. 포트 80/443 접속 불가**
```bash
# Nginx 상태 확인
systemctl status nginx

# 방화벽 확인
ufw status

# 포트 리스닝 확인
netstat -tlnp | grep :80
```

**2. Docker 컨테이너 시작 실패**
```bash
# 로그 확인
docker compose -f /opt/uvis/docker-compose.prod.yml logs

# 재시작
docker compose -f /opt/uvis/docker-compose.prod.yml restart
```

**3. 데이터베이스 연결 실패**
```bash
# PostgreSQL 상태 확인
docker ps | grep postgres

# 수동 연결 테스트
docker exec -it uvis-postgres psql -U uvis_user -d uvis_db
```

**4. 메모리 부족**
```bash
# 메모리 사용량 확인
free -h

# Docker 메모리 제한 설정 (docker-compose.yml)
services:
  backend:
    mem_limit: 1g
  postgres:
    mem_limit: 512m
```

---

## 11. 다음 단계

### 즉시 진행
- ✅ **서버 생성 및 배포**
- ✅ **헬스체크 및 검증**
- ✅ **모니터링 설정**

### 1주일 내
- 🔄 **도메인 연결 및 SSL 설정**
- 🔄 **자동 백업 스크립트 설정**
- 🔄 **성능 모니터링 및 최적화**

### 1개월 내
- 📊 **트래픽 분석 및 서버 사이징**
- 📊 **비용 최적화 검토**
- 📊 **사용자 피드백 반영**

---

## 12. 참고 자료

### 공식 문서
- Hetzner Docs: https://docs.hetzner.com/
- Docker Docs: https://docs.docker.com/
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Nginx Docs: https://nginx.org/en/docs/

### 지원
- **GitHub**: https://github.com/rpaakdi1-spec/3-
- **브랜치**: genspark_ai_developer
- **이슈**: GitHub Issues

---

## 📊 요약

| 항목 | 내용 |
|------|------|
| **배포 시간** | 30-45분 |
| **월간 비용** | €4.49 ($4.90) |
| **서버 사양** | 2 vCPU, 4GB RAM, 40GB SSD |
| **트래픽** | 20 TB/월 |
| **위치** | Falkenstein, 독일 |
| **핑** | 250-300ms (한국) |
| **AWS 대비 절감** | $314.44/월 (98.3%) |

---

**작성일**: 2026-01-28  
**버전**: 1.0.0  
**상태**: 배포 준비 완료

🎉 **이제 Hetzner Cloud로 배포를 시작하세요!**
