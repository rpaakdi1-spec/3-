# 가비아 클라우드 Gen2 배포 가이드

**서버 정보**: Server-s1uvis  
**생성일**: 2026-01-28  
**OS**: Rocky Linux 8.10  
**사양**: 2vCore, 4GB RAM, 100GB SSD

---

## 📋 서버 정보

```yaml
서버 이름: Server-s1uvis
서버 ID: 4c33bb4d-70f6-4300-b50b-6d018995ecd5
OS: Rocky Linux 8.10
사양:
  CPU: 2vCore
  Memory: 4GB
  Storage: 100GB SSD
네트워크:
  사설 IP: 192.168.0.143
  공인 IP: (할당 필요)
로그인:
  사용자: root
  비밀번호: 83!Hwqbm
생성일시: 2026-01-28 22:35:15
```

---

## ⚠️ 1단계: 공인 IP 할당 (필수)

현재 공인 IP가 없어 외부 접속이 불가능합니다. 먼저 공인 IP를 할당하세요.

### 방법 1: 가비아 콘솔에서 할당

1. **가비아 클라우드 콘솔 접속**
   ```
   https://console.gabiacloud.com/
   ```

2. **서버 선택**
   - 프로젝트 > 서버 > Server-s1uvis 클릭

3. **공인 IP 할당**
   - "네트워크" 탭 클릭
   - "공인 IP 할당" 버튼 클릭
   - 새 공인 IP 생성 선택
   - "적용" 클릭

4. **할당된 공인 IP 확인**
   - 서버 상세 페이지에서 공인 IP 확인
   - 예시: `123.456.789.012`

### 방법 2: CLI로 확인 (서버 접속 후)

```bash
# 서버 접속 후
curl ifconfig.me
# 또는
curl ipinfo.io/ip
```

---

## 🔐 2단계: 보안 그룹 설정

### 필수 포트 허용

가비아 콘솔에서 보안 그룹 설정:

| 서비스 | 프로토콜 | 포트 | 출처 | 설명 |
|--------|----------|------|------|------|
| SSH | TCP | 22 | 0.0.0.0/0 | SSH 접속 |
| HTTP | TCP | 80 | 0.0.0.0/0 | 웹 서버 |
| HTTPS | TCP | 443 | 0.0.0.0/0 | HTTPS |
| Backend | TCP | 8000 | 0.0.0.0/0 | API 서버 |
| Netdata | TCP | 19999 | 0.0.0.0/0 | 모니터링 (선택) |

### 설정 방법

1. 서버 상세 페이지 > "보안 그룹" 탭
2. "인바운드 규칙 추가" 클릭
3. 위 표의 포트들 추가
4. "저장" 클릭

---

## 🚀 3단계: SSH 접속

공인 IP가 할당되면 SSH로 서버에 접속합니다.

### Windows (PowerShell 또는 cmd)

```powershell
ssh root@YOUR_PUBLIC_IP
# 비밀번호 입력: 83!Hwqbm

# 예시
ssh root@123.456.789.012
```

### Mac/Linux (터미널)

```bash
ssh root@YOUR_PUBLIC_IP
# 비밀번호 입력: 83!Hwqbm

# 예시
ssh root@123.456.789.012
```

### 첫 접속 시

```bash
# Fingerprint 확인 메시지
The authenticity of host '123.456.789.012' can't be established.
ECDSA key fingerprint is SHA256:...
Are you sure you want to continue connecting (yes/no)?

# "yes" 입력
yes

# 비밀번호 입력
Password: 83!Hwqbm
```

---

## 📦 4단계: 자동 배포 실행

### 배포 스크립트 다운로드 및 실행

SSH 접속 후:

```bash
# 1. 홈 디렉터리로 이동
cd /root

# 2. 배포 스크립트 다운로드
curl -O https://raw.githubusercontent.com/rpaakdi1-spec/3-/genspark_ai_developer/deploy-gabia.sh

# 3. 실행 권한 부여
chmod +x deploy-gabia.sh

# 4. 배포 시작
./deploy-gabia.sh
```

### 배포 진행 과정

스크립트가 자동으로 다음을 실행합니다:

```yaml
Step 1: 시스템 환경 확인
  - OS: Rocky Linux 8.10 확인
  - Root 권한 확인
  - 디스크/메모리 확인
  - 공인 IP 자동 감지

Step 2: SELinux 및 방화벽 설정
  - SELinux 비활성화
  - Firewalld 설정
  - 필수 포트 허용 (22, 80, 443, 8000, 19999)

Step 3: 시스템 업데이트
  - dnf update -y

Step 4: EPEL 저장소 및 필수 패키지 설치
  - EPEL, curl, wget, git, vim, fail2ban, jq

Step 5: Docker 설치
  - Docker Engine
  - Docker Compose Plugin

Step 6: Fail2Ban 설정
  - SSH 보호 설정

Step 7: 프로젝트 클론
  - GitHub에서 UVIS 프로젝트 클론
  - genspark_ai_developer 브랜치 체크아웃

Step 8: 환경 변수 설정
  - .env 파일 생성
  - 데이터베이스 비밀번호 자동 생성
  - JWT Secret 자동 생성
  - Redis 비밀번호 자동 생성

Step 9: Docker Compose 파일 생성
  - PostgreSQL, Redis, Backend, Frontend, Nginx

Step 10: Nginx 설정
  - 리버스 프록시 설정
  - WebSocket 지원 설정

Step 11: Docker 컨테이너 빌드 및 실행
  - docker compose build
  - docker compose up -d

Step 12: 컨테이너 시작 대기
  - 30초 대기

Step 13: 데이터베이스 마이그레이션
  - Alembic 마이그레이션 실행

Step 14: Netdata 설치 (선택사항)
  - 시스템 모니터링 도구

Step 15: 배포 완료
  - 접속 정보 출력
  - 인증 정보 출력
  - 다음 단계 안내
```

### 배포 시간

```yaml
예상 시간: 20-30분

단계별 시간:
  - 시스템 업데이트: 3-5분
  - 패키지 설치: 3-5분
  - Docker 설치: 2-3분
  - 프로젝트 클론: 1-2분
  - Docker 빌드: 8-12분
  - DB 마이그레이션: 1-2분
  - Netdata 설치: 2-3분
```

---

## ✅ 5단계: 배포 완료 확인

배포가 완료되면 다음 메시지가 표시됩니다:

```
╔═══════════════════════════════════════════════════════════╗
║  🎉 배포 완료!                                             ║
╚═══════════════════════════════════════════════════════════╝

🌐 접속 정보:
   Frontend:  http://YOUR_PUBLIC_IP
   Backend:   http://YOUR_PUBLIC_IP:8000
   API Docs:  http://YOUR_PUBLIC_IP:8000/docs
   Health:    http://YOUR_PUBLIC_IP:8000/health
   Netdata:   http://YOUR_PUBLIC_IP:19999

🔑 인증 정보:
   Database:  postgres / [AUTO_GENERATED]
   Redis:     [AUTO_GENERATED]
   JWT:       [AUTO_GENERATED]

📝 다음 단계:
   1. Health Check: curl http://YOUR_PUBLIC_IP:8000/health
   2. 브라우저에서 http://YOUR_PUBLIC_IP 접속
   3. 테스트 계정으로 로그인: driver1 / password123
   4. ML 재학습 스케줄 설정 (선택사항)
   5. 모바일 앱 Backend URL 변경

축하합니다! UVIS가 성공적으로 배포되었습니다! 🎊
```

### 수동 확인

```bash
# Health Check
curl http://YOUR_PUBLIC_IP:8000/health

# 예상 출력:
{
  "status": "healthy",
  "timestamp": "2026-01-28T...",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected"
}

# Docker 컨테이너 확인
docker ps

# 예상 출력: 5개 컨테이너 실행 중
# - uvis-postgres
# - uvis-redis
# - uvis-backend
# - uvis-frontend
# - uvis-nginx
```

### 브라우저 확인

1. **Frontend 접속**
   ```
   http://YOUR_PUBLIC_IP
   ```

2. **API 문서 확인**
   ```
   http://YOUR_PUBLIC_IP:8000/docs
   ```

3. **Netdata 모니터링**
   ```
   http://YOUR_PUBLIC_IP:19999
   ```

---

## 🔧 6단계: 추가 설정 (선택사항)

### 6.1 도메인 연결

도메인이 있는 경우:

1. **DNS A 레코드 추가**
   ```
   Type: A
   Name: @ (또는 subdomain)
   Value: YOUR_PUBLIC_IP
   TTL: 3600
   ```

2. **Nginx 설정 업데이트**
   ```bash
   ssh root@YOUR_PUBLIC_IP
   nano /root/uvis/nginx/nginx.conf
   
   # server_name 변경
   server_name yourdomain.com;
   
   # Nginx 재시작
   cd /root/uvis
   docker compose restart nginx
   ```

### 6.2 SSL 인증서 설치

```bash
ssh root@YOUR_PUBLIC_IP

# Certbot 설치
dnf install -y certbot python3-certbot-nginx

# SSL 인증서 발급
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 자동 갱신 확인
certbot renew --dry-run
```

### 6.3 ML 재학습 스케줄 설정

```bash
ssh root@YOUR_PUBLIC_IP
cd /root/uvis

# Backend 컨테이너 진입
docker compose exec backend bash

# Prophet 설치
pip install prophet

# 수동 재학습 테스트
python3 scripts/retraining_job.py --use-sample-data

# Cron 작업 추가
exit  # 컨테이너에서 나오기
crontab -e

# 매일 새벽 3시 재학습
0 3 * * * cd /root/uvis && docker compose exec -T backend python3 scripts/retraining_job.py >> /var/log/ml-retraining.log 2>&1
```

### 6.4 백업 설정

```bash
ssh root@YOUR_PUBLIC_IP

# 백업 스크립트 생성
cat > /root/backup.sh << 'EOF'
#!/bin/bash
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

# 매일 새벽 2시 백업 실행
crontab -e
0 2 * * * /root/backup.sh >> /var/log/backup.log 2>&1
```

---

## 📱 7단계: 모바일 앱 연결

### Backend URL 변경

로컬 개발 환경에서:

```bash
cd /home/user/webapp/mobile
nano .env
```

**변경**:
```env
# Before
API_URL=http://localhost:8000/api/v1
WS_URL=ws://localhost:8000/ws

# After
API_URL=http://YOUR_PUBLIC_IP:8000/api/v1
WS_URL=ws://YOUR_PUBLIC_IP:8000/ws

# 도메인이 있는 경우
API_URL=https://yourdomain.com/api/v1
WS_URL=wss://yourdomain.com/ws
```

### Expo 재시작

```bash
cd /home/user/webapp/mobile
npx expo start --clear
```

---

## 🆘 트러블슈팅

### 문제: 공인 IP로 접속이 안 됨

**해결**:
```bash
# 1. 방화벽 확인
sudo firewall-cmd --list-all

# 2. 포트 확인
sudo netstat -tlnp | grep -E ':(80|8000|443)'

# 3. Docker 컨테이너 상태
docker ps

# 4. 로그 확인
docker compose logs
```

### 문제: Docker 컨테이너가 시작되지 않음

**해결**:
```bash
# 로그 확인
docker compose logs backend

# 재시작
docker compose restart

# 전체 재빌드
docker compose down
docker compose up -d --build
```

### 문제: 502 Bad Gateway

**해결**:
```bash
# Backend 상태 확인
docker compose ps backend

# Backend 로그 확인
docker compose logs backend

# Backend 재시작
docker compose restart backend

# Nginx 설정 테스트
docker compose exec nginx nginx -t
```

### 문제: SELinux 관련 오류

**해결**:
```bash
# SELinux 상태 확인
getenforce

# 임시 비활성화
sudo setenforce 0

# 영구 비활성화
sudo sed -i 's/^SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config

# 재부팅
sudo reboot
```

---

## 💰 비용 관리

### 월별 예상 비용

```yaml
기본 비용:
  서버: ₩75,350/월 (2vCore, 4GB, 100GB SSD)
  트래픽: 4TB/월 무료
  공인 IP: 포함

추가 비용 (선택사항):
  추가 스토리지: ~₩5,000/50GB
  백업: ~₩5,000/월
  로드밸런서: 별도

예상 월 총비용: ₩75,000 ~ ₩85,000
```

### 비용 절감 팁

1. **트래픽 모니터링**
   - 4TB/월 무료 한도 확인
   - 초과 시 별도 과금

2. **불필요한 리소스 정리**
   - 미사용 스냅샷 삭제
   - 미사용 공인 IP 해제

3. **Netdata로 리소스 사용량 모니터링**
   ```
   http://YOUR_PUBLIC_IP:19999
   ```

---

## 📊 비교: 가비아 vs Hetzner

| 항목 | 가비아 Gen2 | Hetzner CX22 |
|------|-------------|--------------|
| **월 비용** | ₩75,350 | ₩6,500 |
| **5년 총비용** | ₩4,521,000 | ₩390,000 |
| **사양** | 2vCore, 4GB, 100GB SSD | 2vCore, 4GB, 40GB NVMe |
| **IOPS** | 4,000-20,000 (SSD) | 수천 (NVMe) |
| **트래픽** | 4TB/월 | 20TB/월 |
| **위치** | 가산 IDC (서울) | Falkenstein (독일) |
| **한국어 지원** | ✅ 완벽 | ❌ 없음 |
| **배포 시간** | 20-30분 | 15-20분 |

**절감 금액**: Hetzner 선택 시 **₩4,131,000 절감** (5년)

---

## 🎯 체크리스트

### 배포 전
- [ ] 공인 IP 할당 완료
- [ ] 보안 그룹 설정 완료 (22, 80, 443, 8000)
- [ ] SSH 접속 테스트 완료
- [ ] Root 비밀번호 확인 (83!Hwqbm)

### 배포 중
- [ ] 배포 스크립트 다운로드
- [ ] 배포 스크립트 실행
- [ ] 배포 완료 메시지 확인

### 배포 후
- [ ] Health Check 성공
- [ ] Frontend 접속 확인
- [ ] API Docs 접속 확인
- [ ] Docker 컨테이너 5개 실행 확인
- [ ] Netdata 모니터링 확인
- [ ] 모바일 앱 URL 변경
- [ ] SSL 인증서 설치 (선택)
- [ ] ML 재학습 스케줄 설정 (선택)
- [ ] 백업 설정 (선택)

---

## 📞 지원

### 가비아 고객 지원

- **고객센터**: https://customer.gabia.com/
- **전화**: 1544-4923
- **이메일**: cloud@gabia.com
- **운영시간**: 평일 09:00-18:00

### 프로젝트 문의

- **GitHub Issues**: https://github.com/rpaakdi1-spec/3-/issues
- **문서**: `/root/uvis/*.md`

---

## 🎊 축하합니다!

UVIS GPS Fleet Management System이 가비아 클라우드 Gen2에 성공적으로 배포되었습니다!

**다음 단계**:
1. ✅ 실제 사용자 테스트
2. ✅ ML 재학습 자동화
3. ✅ 모바일 앱 배포
4. ✅ 사용자 피드백 수집

---

**작성자**: GenSpark AI Developer  
**버전**: 1.0.0  
**최종 수정일**: 2026-01-28  
**상태**: 배포 준비 완료 ✅
