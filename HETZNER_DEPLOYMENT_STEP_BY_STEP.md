# 🚀 Hetzner Cloud 배포 가이드 (단계별)

**작성일**: 2026-01-28  
**프로젝트**: UVIS GPS Fleet Management System  
**예상 시간**: 15-20분  
**월 비용**: €4.49 (~₩6,500)

---

## 📋 목차

1. [Hetzner 계정 생성](#1-hetzner-계정-생성)
2. [서버 생성](#2-서버-생성)
3. [SSH 접속](#3-ssh-접속)
4. [자동 배포 실행](#4-자동-배포-실행)
5. [배포 완료 확인](#5-배포-완료-확인)
6. [모니터링 설정](#6-모니터링-설정)

---

## 1. Hetzner 계정 생성

### 1.1 회원가입

1. **Hetzner Cloud Console 접속**
   ```
   https://console.hetzner.cloud/
   ```

2. **"Sign Up" 클릭**
   - Email 주소 입력
   - 비밀번호 설정 (8자 이상, 대소문자+숫자+특수문자)
   - 약관 동의

3. **이메일 인증**
   - 받은 메일에서 "Verify Email" 클릭
   - 인증 완료

4. **결제 정보 등록**
   - 신용카드 또는 PayPal
   - 처음 등록 시 작은 금액(€1-5) 검증 가능
   - 환불 정책: 14일 무조건 환불

### 1.2 프로젝트 생성

1. **Console 로그인 후 "New Project" 클릭**
2. **프로젝트 이름 입력**: `UVIS-Fleet-Management`
3. **생성 완료**

---

## 2. 서버 생성

### 2.1 서버 생성 시작

1. **"Add Server" 또는 "Create Server" 클릭**

### 2.2 서버 설정

#### Location (위치)
```yaml
선택: Falkenstein, Germany (fsn1)
이유:
  - 가장 저렴한 가격
  - 안정적인 네트워크
  - 글로벌 CDN 지원
```

#### Image (운영체제)
```yaml
선택: Ubuntu 22.04 LTS
버전: Ubuntu 22.04 (최신 버전)
```

#### Type (서버 사양)
```yaml
선택: CX22

사양:
  - CPU: 2 vCPU (AMD EPYC)
  - RAM: 4GB
  - Disk: 40GB NVMe SSD
  - Traffic: 20TB/월
  - Network: 1 Gbps

가격: €4.49/month (~₩6,500/월)
```

#### SSH Keys (SSH 키)

**옵션 A: 기존 SSH 키 사용 (권장)**
1. 로컬 터미널에서 공개키 확인:
   ```bash
   cat ~/.ssh/id_rsa.pub
   ```
2. 출력된 내용 복사
3. Hetzner Console에서 "Add SSH Key" 클릭
4. 이름 입력: `my-laptop`
5. 공개키 붙여넣기
6. 저장

**옵션 B: 새 SSH 키 생성**
1. 로컬 터미널에서:
   ```bash
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   # Enter 3번 (기본 경로, 비밀번호 없음)
   
   cat ~/.ssh/id_rsa.pub
   ```
2. 공개키 복사하여 Hetzner에 등록

#### Volume (추가 스토리지)
```yaml
선택: None (40GB면 충분)
```

#### Network (네트워크)
```yaml
선택: Default (기본 네트워크)
```

#### Firewalls (방화벽)
```yaml
선택: None (나중에 UFW로 설정)
```

#### Backups (백업)
```yaml
선택: None (비용 절감)
또는
선택: Enable (€0.90/month 추가)
```

#### Labels (라벨)
```yaml
선택: 선택사항
예시:
  - project: uvis
  - environment: production
  - managed-by: auto-deploy
```

### 2.3 서버 이름 설정

```yaml
Server name: uvis-fleet-production
```

### 2.4 서버 생성

1. **"Create & Buy now" 클릭**
2. **서버 생성 시작 (약 30-60초)**
3. **서버 IP 주소 확인 및 복사**

예시:
```
Server: uvis-fleet-production
IPv4: 167.235.123.45
IPv6: 2a01:4f8:c0c:1234::1
Status: Running
```

---

## 3. SSH 접속

### 3.1 서버 IP 확인

Hetzner Console에서 서버 클릭 → IP 주소 복사

예시: `167.235.123.45`

### 3.2 SSH 접속 (로컬 터미널)

```bash
# SSH 접속
ssh root@167.235.123.45

# 처음 접속 시 fingerprint 확인
# "yes" 입력하여 계속
```

### 3.3 접속 확인

```bash
# 서버 정보 확인
uname -a
# Linux uvis-fleet-production 5.15.0-xxx-generic #xxx-Ubuntu SMP ...

# 서버 사양 확인
free -h
# total        used        free      shared  buff/cache   available
# Mem:          3.8Gi       xxx        xxx       xxx        xxx

df -h
# Filesystem      Size  Used Avail Use% Mounted on
# /dev/sda1        39G  xxx   xxx   x% /
```

---

## 4. 자동 배포 실행

### 4.1 배포 스크립트 다운로드

**옵션 A: GitHub에서 직접 다운로드 (권장)**

```bash
# 1. 프로젝트 클론
cd /root
git clone https://github.com/rpaakdi1-spec/3-.git uvis
cd uvis

# 2. genspark_ai_developer 브랜치로 전환
git checkout genspark_ai_developer

# 3. 배포 스크립트 실행 권한 부여
chmod +x deploy-hetzner.sh

# 4. 배포 시작
./deploy-hetzner.sh
```

**옵션 B: 스크립트 직접 생성 (GitHub 접근 불가 시)**

```bash
# 1. 스크립트 다운로드
wget https://raw.githubusercontent.com/rpaakdi1-spec/3-/genspark_ai_developer/deploy-hetzner.sh

# 2. 실행 권한 부여
chmod +x deploy-hetzner.sh

# 3. 배포 시작
sudo ./deploy-hetzner.sh
```

### 4.2 배포 프로세스

스크립트가 자동으로 다음을 실행합니다:

```yaml
Step 1: 시스템 환경 확인
  - OS 확인 (Ubuntu 22.04)
  - Root 권한 확인
  - 디스크/메모리 확인
  - 서버 IP 자동 감지

Step 2: 시스템 업데이트
  - apt update && apt upgrade

Step 3: 필수 패키지 설치
  - curl, wget, git
  - ufw, fail2ban
  - nginx
  - postgresql-client, redis-tools

Step 4: Docker 설치
  - Docker Engine
  - Docker Compose

Step 5: 방화벽 설정 (UFW)
  - SSH (22)
  - HTTP (80)
  - HTTPS (443)
  - Custom Ports (8000, 8080, 3000, etc.)

Step 6: Fail2Ban 설정
  - SSH 보호
  - Nginx 보호

Step 7: 프로젝트 클론 (이미 클론했다면 스킵)
  - GitHub에서 소스 코드 다운로드

Step 8: 환경 변수 설정
  - .env 파일 생성
  - 데이터베이스 비밀번호 자동 생성
  - JWT Secret 자동 생성

Step 9: Docker Compose 빌드 및 실행
  - PostgreSQL 컨테이너
  - Redis 컨테이너
  - Backend API 컨테이너
  - Frontend 컨테이너
  - Nginx 리버스 프록시

Step 10: 데이터베이스 초기화
  - Alembic 마이그레이션 실행
  - 샘플 데이터 생성

Step 11: Nginx 설정
  - 리버스 프록시 설정
  - SSL/TLS (Let's Encrypt) 준비

Step 12: 모니터링 설치 (선택사항)
  - Netdata 설치
  - 시스템 메트릭 수집

Step 13: 배포 완료 확인
  - Health Check
  - API 테스트
  - Frontend 접속 확인
```

### 4.3 배포 시간

```yaml
예상 시간: 15-20분

단계별 시간:
  - 시스템 업데이트: 2-3분
  - 패키지 설치: 3-5분
  - Docker 설치: 2-3분
  - 프로젝트 설정: 1-2분
  - Docker 빌드: 5-8분
  - DB 초기화: 1-2분
  - 최종 확인: 1-2분
```

### 4.4 배포 중 확인 사항

스크립트 실행 중 다음을 확인하세요:

```bash
# 다른 터미널에서 실시간 모니터링 (선택사항)
ssh root@YOUR_SERVER_IP

# Docker 컨테이너 상태 확인
watch -n 2 'docker ps'

# 로그 확인
docker compose logs -f
```

---

## 5. 배포 완료 확인

### 5.1 자동 확인 (스크립트 완료 시)

스크립트가 완료되면 자동으로 다음을 출력합니다:

```
╔═══════════════════════════════════════════════════════════╗
║  🎉 Deployment Complete!                                  ║
╚═══════════════════════════════════════════════════════════╝

🌐 Access URLs:
   Frontend:  http://167.235.123.45
   Backend:   http://167.235.123.45/api/v1
   API Docs:  http://167.235.123.45/docs
   Health:    http://167.235.123.45/api/v1/health

📊 Monitoring:
   Netdata:   http://167.235.123.45:19999

🔑 Credentials:
   Database: postgres
   Password: [AUTO_GENERATED]
   Redis:    No password

📝 Next Steps:
   1. 도메인 연결 (선택사항)
   2. SSL 인증서 설치 (Let's Encrypt)
   3. ML 재학습 스케줄 설정
   4. 모바일 앱 백엔드 URL 변경

💰 Monthly Cost: €4.49 (~₩6,500)
```

### 5.2 수동 확인

#### Health Check
```bash
# 로컬 터미널에서
curl http://YOUR_SERVER_IP/api/v1/health

# 예상 출력:
{
  "status": "healthy",
  "timestamp": "2026-01-28T10:00:00Z",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected"
}
```

#### Frontend 접속
```bash
# 브라우저에서
http://YOUR_SERVER_IP
```

#### API 문서 확인
```bash
# 브라우저에서
http://YOUR_SERVER_IP/docs
```

#### Docker 컨테이너 확인
```bash
# SSH 접속 후
docker ps

# 예상 출력: 5개 컨테이너 실행 중
# - uvis-backend
# - uvis-frontend
# - uvis-postgres
# - uvis-redis
# - uvis-nginx
```

#### 로그 확인
```bash
# 전체 로그
docker compose logs

# Backend 로그만
docker compose logs backend

# 실시간 로그
docker compose logs -f
```

---

## 6. 모니터링 설정

### 6.1 Netdata 접속

```bash
# 브라우저에서
http://YOUR_SERVER_IP:19999
```

**Netdata 대시보드**:
- CPU 사용률
- 메모리 사용률
- 디스크 I/O
- 네트워크 트래픽
- Docker 컨테이너 메트릭

### 6.2 알림 설정 (선택사항)

```bash
# SSH 접속 후
cd /etc/netdata

# 알림 설정 파일 편집
sudo nano health_alarm_notify.conf

# Slack/Email/Discord 등 설정 가능
```

---

## 7. 추가 설정 (선택사항)

### 7.1 도메인 연결

**도메인이 있는 경우**:

1. **DNS 레코드 추가**
   ```
   Type: A
   Name: @ (또는 subdomain)
   Value: YOUR_SERVER_IP
   TTL: 3600
   ```

2. **Nginx 설정 업데이트**
   ```bash
   ssh root@YOUR_SERVER_IP
   cd /root/uvis
   nano nginx/nginx.conf
   
   # server_name 변경
   server_name yourdomain.com;
   
   # Nginx 재시작
   docker compose restart nginx
   ```

### 7.2 SSL 인증서 설치 (Let's Encrypt)

```bash
# SSH 접속 후
ssh root@YOUR_SERVER_IP

# Certbot 설치
apt install -y certbot python3-certbot-nginx

# SSL 인증서 자동 발급 및 설정
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 자동 갱신 설정 확인
certbot renew --dry-run
```

### 7.3 ML 재학습 스케줄 설정

```bash
# SSH 접속 후
ssh root@YOUR_SERVER_IP
cd /root/uvis

# Backend 컨테이너 진입
docker compose exec backend bash

# Prophet 설치
pip install prophet

# 수동 재학습 테스트
python3 scripts/retraining_job.py --use-sample-data

# Cron 작업 추가
crontab -e

# 매일 새벽 3시에 재학습 실행
0 3 * * * cd /root/uvis && docker compose exec -T backend python3 scripts/retraining_job.py >> /var/log/ml-retraining.log 2>&1
```

### 7.4 백업 설정

```bash
# SSH 접속 후
ssh root@YOUR_SERVER_IP

# 백업 스크립트 생성
cat > /root/backup.sh << 'EOF'
#!/bin/bash
# UVIS 데이터베이스 백업 스크립트

BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="uvis_backup_$DATE.sql"

mkdir -p $BACKUP_DIR

# PostgreSQL 백업
docker compose exec -T postgres pg_dump -U postgres uvis > "$BACKUP_DIR/$BACKUP_FILE"

# 압축
gzip "$BACKUP_DIR/$BACKUP_FILE"

# 7일 이상 된 백업 삭제
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
EOF

chmod +x /root/backup.sh

# 매일 새벽 2시에 백업 실행
crontab -e
0 2 * * * /root/backup.sh >> /var/log/backup.log 2>&1
```

---

## 8. 모바일 앱 연결

### 8.1 Backend URL 변경

모바일 앱에서 서버 URL을 변경해야 합니다:

```bash
# 로컬 개발 환경에서
cd /home/user/webapp/mobile

# .env 파일 편집
nano .env
```

**변경 내용**:
```env
# Before
API_URL=http://localhost:8000/api/v1
WS_URL=ws://localhost:8000/ws

# After (도메인이 없는 경우)
API_URL=http://YOUR_SERVER_IP/api/v1
WS_URL=ws://YOUR_SERVER_IP/ws

# After (도메인이 있는 경우)
API_URL=https://yourdomain.com/api/v1
WS_URL=wss://yourdomain.com/ws
```

### 8.2 앱 재빌드

```bash
# Expo 개발 서버 재시작
cd /home/user/webapp/mobile
npx expo start --clear
```

### 8.3 실제 기기에서 테스트

1. Expo Go 앱에서 QR 코드 스캔
2. 로그인 테스트 (driver1 / password123)
3. GPS 추적 기능 테스트
4. 사진 업로드 테스트

---

## 9. 트러블슈팅

### 9.1 Docker 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker compose logs

# 특정 컨테이너 로그
docker compose logs backend

# 컨테이너 재시작
docker compose restart

# 전체 재빌드
docker compose down
docker compose up -d --build
```

### 9.2 데이터베이스 연결 실패

```bash
# PostgreSQL 컨테이너 상태 확인
docker compose ps postgres

# PostgreSQL 로그 확인
docker compose logs postgres

# 데이터베이스 재시작
docker compose restart postgres

# 수동 연결 테스트
docker compose exec postgres psql -U postgres -d uvis -c "SELECT 1;"
```

### 9.3 Nginx 502 Bad Gateway

```bash
# Nginx 로그 확인
docker compose logs nginx

# Backend 상태 확인
docker compose ps backend

# Backend 재시작
docker compose restart backend

# Nginx 설정 테스트
docker compose exec nginx nginx -t
```

### 9.4 방화벽 문제

```bash
# UFW 상태 확인
sudo ufw status

# 포트 열기
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp

# UFW 재시작
sudo ufw reload
```

### 9.5 메모리 부족

```bash
# 메모리 사용량 확인
free -h

# Docker 메모리 사용량
docker stats

# 스왑 추가 (2GB)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 10. 비용 관리

### 10.1 월별 비용 예상

```yaml
Hetzner CX22: €4.49/month (~₩6,500)

추가 비용 (선택사항):
  - Backup: €0.90/month (~₩1,300)
  - Volume (추가 스토리지): €0.08/GB/month
  - Floating IP: €1.19/month
  - Load Balancer: €5.90/month

일반적인 사용: €4.49 ~ €6.00/month
```

### 10.2 비용 절감 팁

1. **백업 대신 스냅샷 사용**
   - 수동 스냅샷: 무료
   - 자동 백업: 월 €0.90

2. **트래픽 모니터링**
   - 20TB/월 무료
   - 초과 시: €1.00/TB

3. **불필요한 리소스 정리**
   - 미사용 볼륨 삭제
   - 오래된 스냅샷 삭제

### 10.3 비용 알림 설정

Hetzner Console에서:
1. Settings → Notifications
2. Budget Alerts 설정
3. 임계값: €10/month

---

## 11. 체크리스트

배포 완료 후 다음을 확인하세요:

### 필수 체크리스트

- [ ] 서버 생성 완료
- [ ] SSH 접속 성공
- [ ] 자동 배포 스크립트 실행 완료
- [ ] Health Check 통과 (`/api/v1/health`)
- [ ] Frontend 접속 확인
- [ ] API 문서 접속 확인 (`/docs`)
- [ ] Docker 컨테이너 5개 실행 중
- [ ] 방화벽 설정 완료 (UFW)
- [ ] Fail2Ban 실행 중
- [ ] Netdata 모니터링 실행 중

### 선택사항 체크리스트

- [ ] 도메인 연결
- [ ] SSL 인증서 설치 (Let's Encrypt)
- [ ] ML 재학습 스케줄 설정
- [ ] 백업 스크립트 설정
- [ ] 모바일 앱 Backend URL 변경
- [ ] 실제 기기에서 앱 테스트
- [ ] 비용 알림 설정
- [ ] Hetzner 백업 활성화 (선택)

### 보안 체크리스트

- [ ] SSH 키 인증만 허용 (비밀번호 인증 비활성화)
- [ ] Fail2Ban 정상 작동
- [ ] 방화벽 규칙 확인
- [ ] 데이터베이스 강력한 비밀번호 설정
- [ ] JWT Secret 랜덤 생성
- [ ] SSL/TLS 인증서 설치 (프로덕션)
- [ ] 정기 백업 설정

---

## 12. 연락처 및 지원

### Hetzner 지원

- **헬프센터**: https://docs.hetzner.com/
- **커뮤니티**: https://community.hetzner.com/
- **이메일**: support@hetzner.com
- **응답 시간**: 24-48시간

### 프로젝트 지원

- **GitHub Issues**: https://github.com/rpaakdi1-spec/3-/issues
- **문서**: `/home/user/webapp/*.md`

---

## 🎉 축하합니다!

UVIS GPS Fleet Management System이 Hetzner Cloud에 성공적으로 배포되었습니다!

**다음 단계**:
1. ✅ 도메인 연결 (선택사항)
2. ✅ SSL 인증서 설치
3. ✅ ML 재학습 스케줄 설정
4. ✅ 모바일 앱 연결
5. ✅ 사용자 교육 및 피드백 수집

---

**작성자**: GenSpark AI Developer  
**버전**: 1.0.0  
**최종 수정일**: 2026-01-28  
**상태**: 배포 준비 완료 ✅
