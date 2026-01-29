# 🚀 Hetzner Cloud 빠른 시작 가이드 (15분)

**예상 소요 시간**: 15-30분  
**예상 비용**: €4.49/월 ($4.90/월)  
**난이도**: ⭐⭐ (초급~중급)

---

## ✅ 준비물

1. **Hetzner 계정** (이미 있음)
   - URL: https://accounts.hetzner.com
   - Client: K0175799026
   - Login: rpaakdi@naver.com
   
2. **로컬 PC에 SSH 클라이언트**
   - Windows: PowerShell, PuTTY, 또는 Windows Terminal
   - Mac/Linux: 기본 터미널

---

## 🎯 3단계 배포

### Step 1: 서버 생성 (5분)

#### 1.1 Hetzner Console 접속
```
1. 브라우저: https://console.hetzner.cloud/
2. 로그인
3. "New Project" 또는 기존 프로젝트 선택
```

#### 1.2 서버 생성
```
1. "Add Server" 클릭

2. 설정:
   📍 Location:    Falkenstein (독일) 권장
   💻 Image:       Ubuntu 22.04
   🖥️  Type:       Shared vCPU → CX22
                  (2 vCPU, 4GB RAM, 40GB SSD)
                  €4.49/월
   
3. SSH Keys:
   - "Add SSH Key" 클릭
   - 로컬 PC에서 SSH 키 생성 (처음이면):
     
     Windows PowerShell:
     ssh-keygen -t ed25519 -C "uvis-hetzner"
     
     Mac/Linux:
     ssh-keygen -t ed25519 -C "uvis-hetzner"
     
   - Public key 복사:
     cat ~/.ssh/id_ed25519.pub
     
   - Hetzner에 붙여넣기

4. Server name: uvis-production

5. "Create & Buy Now" 클릭

6. ⏳ 약 30초 대기

7. ✅ 서버 IP 확인 (예: 123.45.67.89)
```

---

### Step 2: SSH 접속 및 배포 (15분)

#### 2.1 SSH 접속
```bash
# 로컬 PC 터미널에서 실행
ssh root@123.45.67.89

# 처음 접속시 "yes" 입력
```

#### 2.2 자동 배포 실행
```bash
# 배포 스크립트 다운로드
wget https://raw.githubusercontent.com/rpaakdi1-spec/3-/genspark_ai_developer/deploy-hetzner.sh

# 실행 권한 부여
chmod +x deploy-hetzner.sh

# 배포 시작 (자동으로 진행됨)
sudo ./deploy-hetzner.sh
```

#### 2.3 배포 진행 과정 (자동)
```
✅ Step 1:  시스템 환경 확인
✅ Step 2:  시스템 업데이트
✅ Step 3:  필수 패키지 설치
✅ Step 4:  Docker 설치
✅ Step 5:  방화벽 설정
✅ Step 6:  Fail2Ban 설정
✅ Step 7:  프로젝트 클론
✅ Step 8:  환경 변수 설정
✅ Step 9:  Docker Compose 확인
✅ Step 10: PostgreSQL & Redis 시작
✅ Step 11: 데이터베이스 초기화
✅ Step 12: Backend API 시작
✅ Step 13: Frontend 빌드 및 Nginx 설정
✅ Step 14: Netdata 모니터링 설치
✅ Step 15: 배포 검증

⏱️  예상 소요: 15-20분
```

---

### Step 3: 접속 확인 (1분)

배포 완료 후 출력된 정보:

```
접속 정보:
  🌐 Frontend:        http://123.45.67.89
  🔧 Backend API:     http://123.45.67.89:8000
  📖 API Docs:        http://123.45.67.89:8000/docs
  ❤️  Health Check:   http://123.45.67.89:8000/health
  📊 Monitoring:      http://123.45.67.89:19999
```

#### 3.1 브라우저에서 확인
1. **Frontend**: http://123.45.67.89 → 로그인 페이지 표시
2. **API Docs**: http://123.45.67.89:8000/docs → Swagger UI 표시
3. **Health Check**: http://123.45.67.89:8000/health → `{"status":"healthy"}`
4. **Monitoring**: http://123.45.67.89:19999 → Netdata 대시보드

#### 3.2 기본 로그인 정보
```
초기 관리자 계정 (변경 필요):
  Username: admin
  Password: admin123
  
⚠️ 첫 로그인 후 반드시 비밀번호 변경!
```

---

## 🔧 관리 명령어

### 서비스 관리
```bash
# SSH 접속
ssh root@123.45.67.89

# 로그 확인
docker compose -f /opt/uvis/docker-compose.prod.yml logs -f

# 서비스 재시작
docker compose -f /opt/uvis/docker-compose.prod.yml restart

# 서비스 중지
docker compose -f /opt/uvis/docker-compose.prod.yml down

# 서비스 시작
docker compose -f /opt/uvis/docker-compose.prod.yml up -d

# 서버 재부팅
reboot
```

### 백업
```bash
# 데이터베이스 백업
docker exec uvis-postgres pg_dump -U uvis_user uvis_db > backup_$(date +%Y%m%d).sql

# 파일 다운로드 (로컬 PC에서)
scp root@123.45.67.89:/root/backup_*.sql ./
```

---

## 🌐 도메인 연결 (선택)

도메인이 있으면 더 편리합니다!

### DNS 설정
```
1. 도메인 관리 페이지 (예: Cloudflare, Namecheap)
2. A 레코드 추가:
   - Type: A
   - Name: @ (또는 uvis)
   - Value: 123.45.67.89
   - TTL: Auto

3. DNS 전파 대기 (5-10분)

4. 확인: http://yourdomain.com
```

### SSL 인증서 (무료)
```bash
# SSH 접속 후
ssh root@123.45.67.89

# Certbot 설치
apt install -y certbot python3-certbot-nginx

# SSL 인증서 발급
certbot --nginx -d yourdomain.com

# 자동 갱신 확인
certbot renew --dry-run

# Nginx 재시작
systemctl reload nginx

# 완료! 이제 https://yourdomain.com 접속 가능
```

---

## 💰 비용 분석

### 월간 비용
| 항목 | 비용 |
|------|------|
| Hetzner CX22 서버 | €4.49 ($4.90) |
| 스냅샷 (선택) | €0.40 ($0.44) |
| 백업 볼륨 (선택) | €0.20 ($0.22) |
| **총합** | **€5.09 ($5.56)** |

### AWS 대비 절감
```
AWS 예상 비용:        $320.00/월
Hetzner 비용:         $4.90/월
─────────────────────────────
절감액:               $315.10/월 (98.5%)
연간 절감:            $3,781.20/년
```

---

## 🆘 문제 해결

### 배포 실패 시
```bash
# 로그 확인
docker compose -f /opt/uvis/docker-compose.prod.yml logs

# 개별 컨테이너 확인
docker ps -a
docker logs uvis-backend
docker logs uvis-postgres

# 재배포
cd /opt/uvis
docker compose -f docker-compose.prod.yml down
sudo ./deploy-hetzner.sh
```

### 포트 접속 불가
```bash
# 방화벽 확인
ufw status

# 포트 열기
ufw allow 8000/tcp

# Nginx 상태
systemctl status nginx
nginx -t
```

### 메모리 부족
```bash
# 메모리 확인
free -h

# Docker 메모리 제한 (docker-compose.yml 수정)
services:
  backend:
    mem_limit: 1g
  postgres:
    mem_limit: 512m
```

---

## 📚 추가 문서

- **상세 가이드**: [HETZNER_DEPLOYMENT_GUIDE.md](./HETZNER_DEPLOYMENT_GUIDE.md)
- **비용 절감**: [COST_REDUCTION_STRATEGIES.md](./COST_REDUCTION_STRATEGIES.md)
- **클라우드 비교**: [CLOUD_ALTERNATIVES.md](./CLOUD_ALTERNATIVES.md)
- **프로젝트 개요**: [README.md](./README.md)

---

## 🎉 완료!

축하합니다! 이제 **UVIS GPS Fleet Management System**이 프로덕션 환경에서 실행 중입니다.

### 다음 단계
1. ✅ **로그인 및 테스트**
2. 🔄 **관리자 비밀번호 변경**
3. 📊 **모니터링 확인**
4. 🌐 **도메인 연결 (선택)**
5. 📝 **사용자 매뉴얼 확인**

### 지원
- **GitHub**: https://github.com/rpaakdi1-spec/3-
- **브랜치**: genspark_ai_developer
- **문서**: `/docs` 디렉토리

---

**작성일**: 2026-01-28  
**버전**: 1.0.0  
**상태**: Production Ready

💪 Happy Fleet Management!
