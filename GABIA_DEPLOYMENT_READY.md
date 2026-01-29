# 🚀 가비아 클라우드 배포 완료 가이드

**서버 정보**: Server-s1uvis  
**공인 IP**: **139.150.11.99** ✅  
**배포일**: 2026-01-28  
**상태**: 배포 준비 완료

---

## 📋 최종 서버 정보

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
  공인 IP: 139.150.11.99 ✅
로그인:
  사용자: root
  비밀번호: 83!Hwqbm
생성일시: 2026-01-28 22:35:15
```

---

## 🚀 배포 실행 (즉시 가능)

### SSH 접속

#### Windows (PowerShell 또는 cmd)
```powershell
ssh root@139.150.11.99
# 비밀번호: 83!Hwqbm
```

#### Mac/Linux (터미널)
```bash
ssh root@139.150.11.99
# 비밀번호: 83!Hwqbm
```

### 배포 스크립트 실행

SSH 접속 후:

```bash
# 1. 홈 디렉터리로 이동
cd /root

# 2. 배포 스크립트 다운로드
curl -O https://raw.githubusercontent.com/rpaakdi1-spec/3-/genspark_ai_developer/deploy-gabia.sh

# 3. 실행 권한 부여
chmod +x deploy-gabia.sh

# 4. 배포 시작 (20-30분 소요)
./deploy-gabia.sh
```

---

## ✅ 배포 완료 후 접속 URL

### 🌐 웹 서비스

```yaml
Frontend (메인 페이지):
  http://139.150.11.99

Backend API:
  http://139.150.11.99:8000

API 문서 (Swagger):
  http://139.150.11.99:8000/docs

Health Check:
  http://139.150.11.99:8000/health

Netdata 모니터링:
  http://139.150.11.99:19999
```

### 🧪 Health Check 테스트

```bash
# 로컬 터미널이나 SSH에서
curl http://139.150.11.99:8000/health

# 예상 출력:
{
  "status": "healthy",
  "timestamp": "2026-01-28T...",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected"
}
```

---

## 🔐 테스트 계정

배포 완료 후 로그인:

```yaml
관리자 계정:
  Username: admin@example.com
  Password: admin123

드라이버 계정:
  Username: driver1
  Password: password123
  
  Username: driver2
  Password: password123
```

---

## 📱 모바일 앱 연결

배포 완료 후 모바일 앱의 Backend URL을 변경하세요:

### 설정 파일 위치
```
/home/user/webapp/mobile/.env
```

### 변경 내용

**Before (로컬)**:
```env
EXPO_PUBLIC_API_URL=http://192.168.1.100:8000
EXPO_PUBLIC_WS_URL=ws://192.168.1.100:8001
```

**After (가비아 서버)**:
```env
EXPO_PUBLIC_API_URL=http://139.150.11.99:8000
EXPO_PUBLIC_WS_URL=ws://139.150.11.99:8000/ws
```

### Expo 재시작

```bash
# 로컬 개발 환경에서
cd /home/user/webapp/mobile

# Metro Bundler 재시작
npx expo start --clear
```

### 모바일 기기에서 테스트

1. **Expo Go 앱 실행**
2. **QR 코드 스캔** 또는 URL 입력:
   ```
   exp://8081-i16kcdhvw5ng6rusdg7lj-ad490db5.sandbox.novita.ai:8081
   ```
3. **로그인 테스트**
   - driver1 / password123
4. **기능 테스트**
   - GPS 추적
   - 사진 촬영/업로드
   - 배차 수락/거절

---

## 🔧 배포 후 추가 설정 (선택사항)

### 1. 도메인 연결

도메인이 있는 경우:

```bash
# DNS A 레코드 추가
Type: A
Name: @ (또는 subdomain)
Value: 139.150.11.99
TTL: 3600

# Nginx 설정 업데이트
ssh root@139.150.11.99
nano /root/uvis/nginx/nginx.conf

# server_name 변경
server_name yourdomain.com;

# Nginx 재시작
cd /root/uvis
docker compose restart nginx
```

### 2. SSL 인증서 설치

```bash
ssh root@139.150.11.99

# Certbot 설치
dnf install -y certbot python3-certbot-nginx

# SSL 인증서 발급
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 자동 갱신 설정
certbot renew --dry-run
```

### 3. ML 재학습 스케줄 설정

```bash
ssh root@139.150.11.99
cd /root/uvis

# Backend 컨테이너 진입
docker compose exec backend bash

# Prophet 설치
pip install prophet

# 수동 재학습 테스트
python3 scripts/retraining_job.py --use-sample-data

# Cron 작업 추가
exit
crontab -e

# 매일 새벽 3시 재학습
0 3 * * * cd /root/uvis && docker compose exec -T backend python3 scripts/retraining_job.py >> /var/log/ml-retraining.log 2>&1
```

### 4. 자동 백업 설정

```bash
ssh root@139.150.11.99

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

# 매일 새벽 2시 백업
crontab -e
0 2 * * * /root/backup.sh >> /var/log/backup.log 2>&1
```

---

## 🆘 트러블슈팅

### 문제: SSH 접속 실패

**확인 사항**:
1. 공인 IP 확인: `139.150.11.99`
2. 보안 그룹에서 22번 포트 허용 확인
3. 비밀번호 재확인: `83!Hwqbm`

**해결 방법**:
```bash
# 가비아 콘솔에서
# 서버 > 보안 그룹 > 인바운드 규칙
# SSH (22번 포트) 허용 확인
```

### 문제: Health Check 실패

```bash
# Docker 컨테이너 상태 확인
docker ps

# 모든 컨테이너 실행 중인지 확인
# - uvis-postgres
# - uvis-redis  
# - uvis-backend
# - uvis-frontend
# - uvis-nginx

# 로그 확인
docker compose logs backend

# 재시작
docker compose restart
```

### 문제: 502 Bad Gateway

```bash
# Backend 상태 확인
docker compose ps backend

# Backend 로그
docker compose logs backend

# Backend 재시작
docker compose restart backend

# Nginx 설정 테스트
docker compose exec nginx nginx -t
```

### 문제: 방화벽 차단

```bash
# Firewalld 상태 확인
sudo firewall-cmd --list-all

# 포트 추가
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=19999/tcp

# 재시작
sudo firewall-cmd --reload
```

---

## 💰 비용 안내

### 월별 비용

```yaml
가비아 클라우드 Gen2:
  서버 (2vCore, 4GB, 100GB SSD): ₩75,350/월
  공인 IP: 포함
  트래픽: 4TB/월 무료
  
예상 월 총비용: ₩75,000 ~ ₩85,000
연간 비용: ₩900,000 ~ ₩1,020,000
5년 총비용: ₩4,500,000 ~ ₩5,100,000
```

### 비교 참고

```yaml
Hetzner Cloud CX22:
  월 비용: ₩6,500
  연간: ₩78,000
  5년: ₩390,000
  절감: ₩4,131,000 (91%)

Oracle Cloud Free:
  월 비용: ₩0 (무료)
  5년: ₩0
  절감: ₩4,521,000 (100%)
```

---

## 📊 배포 체크리스트

### 배포 전
- [x] 가비아 서버 생성
- [x] 공인 IP 할당 (139.150.11.99)
- [ ] 보안 그룹 설정 (22, 80, 443, 8000, 19999)
- [ ] SSH 접속 테스트

### 배포 중
- [ ] SSH 접속 성공
- [ ] 배포 스크립트 다운로드
- [ ] 배포 스크립트 실행
- [ ] 배포 완료 메시지 확인

### 배포 후
- [ ] Health Check 성공 (http://139.150.11.99:8000/health)
- [ ] Frontend 접속 (http://139.150.11.99)
- [ ] API Docs 접속 (http://139.150.11.99:8000/docs)
- [ ] Docker 컨테이너 5개 실행 확인
- [ ] Netdata 모니터링 (http://139.150.11.99:19999)
- [ ] 테스트 계정 로그인 (driver1/password123)

### 선택사항
- [ ] 도메인 연결
- [ ] SSL 인증서 설치
- [ ] ML 재학습 스케줄
- [ ] 자동 백업 설정
- [ ] 모바일 앱 URL 변경
- [ ] 실제 기기 테스트

---

## 📝 유용한 명령어

### Docker 관리

```bash
# 컨테이너 상태 확인
docker ps

# 전체 로그
docker compose logs

# 특정 서비스 로그
docker compose logs backend
docker compose logs frontend

# 실시간 로그
docker compose logs -f

# 재시작
docker compose restart

# 중지
docker compose down

# 재빌드 및 시작
docker compose up -d --build
```

### 시스템 모니터링

```bash
# 시스템 리소스
htop

# 디스크 사용량
df -h

# 메모리 사용량
free -h

# 네트워크 연결
netstat -tlnp

# 방화벽 상태
firewall-cmd --list-all
```

### 로그 확인

```bash
# 시스템 로그
journalctl -xe

# Docker 로그
docker compose logs

# Nginx 로그
docker compose logs nginx

# Backend 로그
docker compose logs backend

# PostgreSQL 로그
docker compose logs postgres
```

---

## 📞 지원 연락처

### 가비아 고객 지원
- **고객센터**: https://customer.gabia.com/
- **전화**: 1544-4923
- **이메일**: cloud@gabia.com
- **운영시간**: 평일 09:00-18:00

### 프로젝트 문서
- **GitHub**: https://github.com/rpaakdi1-spec/3-
- **Branch**: genspark_ai_developer
- **배포 가이드**: `GABIA_DEPLOYMENT_GUIDE.md`
- **분석 문서**: `GABIA_HOSTING_ANALYSIS.md`

---

## 🎊 축하합니다!

모든 준비가 완료되었습니다!

**지금 바로 실행**:

1. **SSH 접속**: `ssh root@139.150.11.99` (비밀번호: `83!Hwqbm`)
2. **배포 시작**: `./deploy-gabia.sh` (20-30분 소요)
3. **확인**: `http://139.150.11.99` 브라우저에서 접속

**예상 결과**:
- ✅ UVIS Frontend 로딩
- ✅ API 문서 접속 가능
- ✅ Health Check 성공
- ✅ 모바일 앱 연결 가능

---

**배포를 시작하세요!** 🚀

SSH 접속 후 배포 스크립트를 실행하시고, 진행 상황이나 문제가 있으면 알려주세요!

---

**작성자**: GenSpark AI Developer  
**버전**: 1.0.0  
**최종 수정일**: 2026-01-28  
**상태**: 배포 준비 완료 ✅
