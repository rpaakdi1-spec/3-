# 🚀 배포 다음 단계 - 실행 가이드

**작성일**: 2026-01-28  
**상태**: 실제 배포 진행 중  
**예상 소요**: 30분

---

## 📋 현재 상황

✅ **Phase 1-20 완료** (96% 전체 진행률)  
✅ **Hetzner 배포 스크립트 완성**  
✅ **문서화 완료**  
✅ **Git 커밋 완료** (최신: 3b65eeb)

---

## 💰 배포 옵션 선택

### **Option A: Hetzner Cloud (권장)** 💵
- **비용**: €4.49/월 ($4.90/월)
- **장점**: 빠른 배포 (20분), 단일 서버, 자동화 스크립트
- **스펙**: 2 vCPU, 4GB RAM, 40GB NVMe, 20TB 트래픽
- **적합**: 빠른 프로덕션 배포, 안정적인 성능 필요

### **Option B: Oracle Cloud Free Tier** 🆓
- **비용**: $0/월 (완전 무료, 영구)
- **장점**: 완전 무료, Always Free 보장
- **스펙**: VM 2개 (각 1 vCPU, 1GB RAM, 50GB 스토리지)
- **적합**: 예산 제약, 학습/테스트, 소규모 운영
- **제약**: 설정 복잡도 높음, 성능 제한적
- **자세한 가이드**: [Oracle Cloud 배포 가이드 보기](#oracle-cloud-무료-배포-option-b)

---

## 🎯 Hetzner Cloud 배포 (Option A)

### **Step 1: Hetzner 서버 생성 (5분)** ⏱️

#### 1.1 Hetzner Console 접속
```
🔗 URL: https://console.hetzner.cloud/
🔑 Login: rpaakdi@naver.com
🔑 Password: @Rkdalsxo8484
```

#### 1.2 서버 생성 클릭
1. 좌측 메뉴 **"Servers"** 클릭
2. **"Add Server"** 버튼 클릭

#### 1.3 서버 설정
```
📍 Location:    Falkenstein, 독일 (가장 저렴)
💻 Image:       Ubuntu 22.04
🖥️  Type:       Shared vCPU > CX22
                - 2 vCPU (AMD)
                - 4 GB RAM
                - 40 GB NVMe SSD
                - 20 TB 트래픽
                - €4.49/월 ($4.90)

🔐 SSH Keys:    "Add SSH Key" 클릭 후
                로컬에서 생성:
                ssh-keygen -t ed25519 -C "uvis-hetzner"
                
                Public key 복사:
                cat ~/.ssh/id_ed25519.pub
                
                Hetzner에 붙여넣기

🏷️  Name:       uvis-production-server

🌐 Networking:  Public IPv4 (자동)
🔥 Firewall:    나중에 설정 (스크립트에서 자동)
```

#### 1.4 서버 생성 완료
1. **"Create & Buy Now"** 클릭
2. 약 30초 대기
3. ✅ **서버 IP 주소 확인** (예: 123.45.67.89)

---

### **Step 2: 자동 배포 실행 (15-20분)** ⏱️

#### 2.1 로컬 PC에서 SSH 접속
```bash
# SSH 접속
ssh root@123.45.67.89

# 처음 접속시 "yes" 입력하여 호스트 추가
```

#### 2.2 배포 스크립트 다운로드
```bash
# 배포 스크립트 다운로드
wget https://raw.githubusercontent.com/rpaakdi1-spec/3-/genspark_ai_developer/deploy-hetzner.sh

# 실행 권한 부여
chmod +x deploy-hetzner.sh

# 스크립트 확인
ls -lh deploy-hetzner.sh
```

#### 2.3 자동 배포 시작
```bash
# 배포 실행 (완전 자동화)
sudo ./deploy-hetzner.sh

# 진행 과정 (자동):
# ✅ Step 1:  시스템 환경 확인
# ✅ Step 2:  시스템 업데이트 (apt update & upgrade)
# ✅ Step 3:  필수 패키지 설치
# ✅ Step 4:  Docker 및 Docker Compose 설치
# ✅ Step 5:  방화벽 설정 (UFW)
# ✅ Step 6:  Fail2Ban 보안 설정
# ✅ Step 7:  프로젝트 클론 (GitHub)
# ✅ Step 8:  환경 변수 자동 생성
# ✅ Step 9:  Docker Compose 확인
# ✅ Step 10: PostgreSQL & Redis 시작
# ✅ Step 11: 데이터베이스 마이그레이션
# ✅ Step 12: Backend API 시작
# ✅ Step 13: Frontend 빌드 및 Nginx 설정
# ✅ Step 14: Netdata 모니터링 설치
# ✅ Step 15: 헬스체크 및 검증

# 예상 소요: 15-20분
```

---

### **Step 3: 배포 완료 확인 (1분)** ⏱️

배포 완료 후 터미널에 출력되는 정보:

```
╔═══════════════════════════════════════════════════════════╗
║           배포 완료!                                      ║
╚═══════════════════════════════════════════════════════════╝

접속 정보:
  🌐 Frontend:        http://123.45.67.89
  🔧 Backend API:     http://123.45.67.89:8000
  📖 API Docs:        http://123.45.67.89:8000/docs
  ❤️  Health Check:   http://123.45.67.89:8000/health
  📊 Monitoring:      http://123.45.67.89:19999
```

#### 3.1 브라우저에서 접속 테스트
1. **Frontend**: http://123.45.67.89
   - 로그인 페이지가 표시되어야 함
   
2. **API Docs**: http://123.45.67.89:8000/docs
   - Swagger UI가 표시되어야 함
   
3. **Health Check**: http://123.45.67.89:8000/health
   - `{"status":"healthy","database":"connected","redis":"connected"}`
   
4. **Monitoring**: http://123.45.67.89:19999
   - Netdata 대시보드 표시

---

## 🔧 배포 후 관리 명령어

### 로그 확인
```bash
# SSH 접속
ssh root@123.45.67.89

# 전체 로그
docker compose -f /opt/uvis/docker-compose.prod.yml logs -f

# Backend 로그만
docker compose -f /opt/uvis/docker-compose.prod.yml logs -f backend

# Frontend 로그만
docker compose -f /opt/uvis/docker-compose.prod.yml logs -f frontend

# Nginx 로그
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 서비스 관리
```bash
# 서비스 재시작
docker compose -f /opt/uvis/docker-compose.prod.yml restart

# 서비스 중지
docker compose -f /opt/uvis/docker-compose.prod.yml down

# 서비스 시작
docker compose -f /opt/uvis/docker-compose.prod.yml up -d

# 서비스 상태 확인
docker compose -f /opt/uvis/docker-compose.prod.yml ps

# 서버 재부팅
reboot
```

### 데이터베이스 관리
```bash
# PostgreSQL 접속
docker exec -it uvis-postgres psql -U uvis_user -d uvis_db

# 데이터베이스 백업
docker exec uvis-postgres pg_dump -U uvis_user uvis_db > backup_$(date +%Y%m%d).sql

# 백업 다운로드 (로컬 PC에서)
scp root@123.45.67.89:/root/backup_*.sql ./
```

---

## 🆘 문제 해결

### 배포 스크립트 실패 시
```bash
# 로그 확인
cat /opt/uvis/deploy.log

# 수동 재시도
cd /opt/uvis
sudo ./deploy-hetzner.sh

# Docker 로그 확인
docker compose -f docker-compose.prod.yml logs
```

### 포트 접속 불가
```bash
# 방화벽 확인
ufw status verbose

# Nginx 상태
systemctl status nginx
nginx -t

# Docker 컨테이너 확인
docker ps -a
```

### Backend API 오류
```bash
# Backend 로그 확인
docker logs uvis-backend

# Backend 재시작
docker compose -f /opt/uvis/docker-compose.prod.yml restart backend

# 데이터베이스 연결 확인
docker exec -it uvis-postgres psql -U uvis_user -d uvis_db -c "\conninfo"
```

### Frontend 표시 안 됨
```bash
# Nginx 로그 확인
tail -f /var/log/nginx/error.log

# Frontend 파일 확인
ls -la /opt/uvis/frontend/dist

# Nginx 재시작
systemctl restart nginx
```

---

## 🌐 도메인 및 SSL 설정 (선택)

### 도메인 연결
도메인이 있는 경우:

```
1. DNS 관리 페이지 접속 (Cloudflare, Namecheap 등)
2. A 레코드 추가:
   Type: A
   Name: @ (또는 uvis)
   Value: 123.45.67.89
   TTL: Auto
3. DNS 전파 대기 (5-10분)
```

### Let's Encrypt SSL
```bash
# SSH 접속
ssh root@123.45.67.89

# Certbot 설치
apt install -y certbot python3-certbot-nginx

# SSL 인증서 발급
certbot --nginx -d yourdomain.com

# Nginx 재시작
systemctl reload nginx

# 이제 https://yourdomain.com 접속 가능!
```

---

## 💾 백업 설정

### 자동 백업 스크립트 (이미 생성됨)
```bash
# 백업 스크립트 확인
cat /opt/backup-db.sh

# 수동 백업 실행
/opt/backup-db.sh

# Cron 등록 확인
crontab -l
# 출력: 0 3 * * * /opt/backup-db.sh
```

### Hetzner 스냅샷
```
1. Hetzner Console 접속
2. Servers → uvis-production-server 선택
3. "Create Snapshot" 클릭
4. 이름: uvis-backup-YYYYMMDD
5. 비용: €0.01/GB/월 (40GB = €0.40/월)
```

---

## 📊 모니터링

### Netdata 대시보드
```
URL: http://123.45.67.89:19999

모니터링 항목:
✅ CPU 사용률 (실시간)
✅ 메모리 사용률
✅ 디스크 I/O
✅ 네트워크 트래픽
✅ Docker 컨테이너 상태
✅ PostgreSQL 성능
✅ Redis 성능
✅ Nginx 상태
```

---

## 📈 성능 최적화 (필요시)

### 메모리 부족 시
```bash
# Docker 메모리 제한 설정
nano /opt/uvis/docker-compose.prod.yml

# 추가:
services:
  backend:
    mem_limit: 1g
    mem_reservation: 512m
  postgres:
    mem_limit: 512m
    mem_reservation: 256m
  redis:
    mem_limit: 256m
    mem_reservation: 128m

# 재시작
docker compose -f /opt/uvis/docker-compose.prod.yml restart
```

### 트래픽 증가 시 서버 업그레이드
```
Hetzner Console:
1. Servers → uvis-production-server
2. "Resize" 또는 "Power off" → "Resize"
3. CX32 선택 (4 vCPU, 8GB RAM) - €8.49/월
4. "Resize Server" 클릭
5. 약 1-2분 후 재시작
```

---

## 🎯 배포 완료 체크리스트

### 필수 확인 사항
- [ ] Hetzner 서버 생성 완료 (IP: ____________)
- [ ] SSH 접속 성공
- [ ] 배포 스크립트 실행 완료
- [ ] Frontend 접속 성공 (http://[IP])
- [ ] Backend API 접속 성공 (http://[IP]:8000)
- [ ] API Docs 접속 성공 (http://[IP]:8000/docs)
- [ ] Health Check 정상 (http://[IP]:8000/health)
- [ ] Monitoring 접속 성공 (http://[IP]:19999)

### 선택 사항
- [ ] 도메인 연결 (DNS A 레코드)
- [ ] SSL 인증서 설치 (Let's Encrypt)
- [ ] 자동 백업 검증 (cron 확인)
- [ ] Hetzner 스냅샷 생성

---

## 📞 지원

### 문제 발생 시
- **GitHub Issues**: https://github.com/rpaakdi1-spec/3-/issues
- **배포 가이드**: [HETZNER_DEPLOYMENT_GUIDE.md](./HETZNER_DEPLOYMENT_GUIDE.md)
- **빠른 시작**: [HETZNER_QUICK_START.md](./HETZNER_QUICK_START.md)

### Hetzner 지원
- **Portal**: https://accounts.hetzner.com/support
- **Docs**: https://docs.hetzner.com/
- **Email**: support@hetzner.com

---

## 🎉 배포 완료 후

배포가 성공적으로 완료되면:

1. ✅ **서버 IP 기록**
2. ✅ **관리자 비밀번호 변경**
3. ✅ **모니터링 대시보드 북마크**
4. ✅ **백업 스케줄 확인**
5. ✅ **팀원들에게 접속 정보 공유**

---

---

## 🆓 Oracle Cloud 무료 배포 (Option B)

### **왜 Oracle Cloud Free Tier?**

```yaml
비용 비교:
  Hetzner:     €4.49/월 ($4.90/월)
  Oracle:      $0/월 (완전 무료!)
  AWS:         ~$320/월
  
절감액:
  vs Hetzner:  $4.90/월 → $58.80/년
  vs AWS:      $320/월 → $3,840/년
```

### **Oracle Cloud 무료 제공 리소스**

```
✅ VM 2개 (각각):
   - 1/8 OCPU (1 vCPU)
   - 1 GB RAM
   - 50 GB Boot Volume
   
✅ Block Storage:
   - 200 GB 총 스토리지
   
✅ Network:
   - 10 TB 아웃바운드 트래픽/월
   - Public IPv4 주소
   
✅ Database (선택):
   - Autonomous Database 20GB

⚠️  평생 무료 (Always Free Eligible)
    - 신용카드 등록 필요 (본인 확인용)
    - 무료 한도 내에서는 절대 청구 안됨
```

---

### **빠른 시작 - 3단계**

#### **1단계: Oracle Cloud 가입 (10분)**

```bash
# 1. Oracle Cloud 접속
https://www.oracle.com/cloud/free/

# 2. "Start for free" 클릭

# 3. 계정 정보 입력
이메일: your-email@example.com
지역: South Korea 또는 Japan (가까운 곳)
Home Region: 
  - South Korea Central (Seoul) 권장 ✅
  - Japan Central (Tokyo) 대안

# 4. 신용카드 등록 (본인 확인용)
⚠️ 무료 티어 내에서는 청구되지 않음
⚠️ $1 임시 승인 후 취소됨

# 5. ✅ 가입 완료!
```

---

#### **2단계: VM 인스턴스 생성 (15분)**

##### **VM 1: Backend + Database**

```bash
# Oracle Cloud Console 접속
https://cloud.oracle.com/

# 좌측 메뉴 → Compute → Instances → Create Instance

설정:
  Name: uvis-backend
  
  Image: 
    ✅ Canonical Ubuntu 22.04 (Latest)
  
  Shape:
    ✅ VM.Standard.E2.1.Micro
       - 1/8 OCPU (1 vCPU)
       - 1 GB RAM
       - 🆓 Always Free 뱃지 확인!
  
  Networking:
    ✅ Create new VCN: uvis-vcn
    ✅ Create new subnet: uvis-subnet
    ✅ Assign public IPv4: 체크
  
  SSH Keys:
    ✅ "Generate key pair" 선택
    ✅ "Save Private Key" 클릭 → uvis-backend.key 저장
    ⚠️  이 키를 안전하게 보관하세요!
  
  Boot Volume:
    ✅ 50 GB (기본값)
    ✅ Use in-transit encryption: 체크

# "Create" 클릭

# ✅ Public IP 확인: 132.145.XXX.XXX
```

##### **VM 2: Frontend (선택 - 권장)**

```bash
# 같은 방법으로 생성

설정:
  Name: uvis-frontend
  Image: Ubuntu 22.04
  Shape: VM.Standard.E2.1.Micro (Always Free)
  
  Networking:
    ✅ Select existing VCN: uvis-vcn
    ✅ Select existing subnet: uvis-subnet
    ✅ Assign public IPv4: 체크
  
  SSH Keys:
    ✅ Generate key pair → uvis-frontend.key

# ✅ Public IP 확인: 132.145.YYY.YYY
```

---

#### **3단계: 방화벽 설정 (5분)**

##### **Oracle Cloud 방화벽 (Security List)**

```bash
# 좌측 메뉴 → Networking → Virtual Cloud Networks

# "uvis-vcn" 클릭 → "Security Lists" → "Default Security List"

# "Add Ingress Rules" 클릭하여 다음 규칙 추가:

규칙 1 - HTTP:
  Source CIDR: 0.0.0.0/0
  IP Protocol: TCP
  Destination Port: 80
  Description: HTTP

규칙 2 - HTTPS:
  Source CIDR: 0.0.0.0/0
  IP Protocol: TCP
  Destination Port: 443
  Description: HTTPS

규칙 3 - Backend API:
  Source CIDR: 0.0.0.0/0
  IP Protocol: TCP
  Destination Port: 8000
  Description: Backend API

규칙 4 - WebSocket:
  Source CIDR: 0.0.0.0/0
  IP Protocol: TCP
  Destination Port: 8001
  Description: WebSocket

규칙 5 - Netdata:
  Source CIDR: 0.0.0.0/0
  IP Protocol: TCP
  Destination Port: 19999
  Description: Monitoring
```

---

#### **4단계: 자동 배포 (20분)**

##### **Backend VM 배포**

```bash
# 1. SSH 키 권한 설정 (로컬 PC에서)
chmod 400 uvis-backend.key

# 2. SSH 접속
ssh -i uvis-backend.key ubuntu@132.145.XXX.XXX
# 처음 접속 시 "yes" 입력

# 3. 자동 배포 스크립트 다운로드
wget https://raw.githubusercontent.com/rpaakdi1-spec/3-/genspark_ai_developer/deploy-oracle-cloud.sh

# 4. 실행 권한 부여
chmod +x deploy-oracle-cloud.sh

# 5. 배포 실행
sudo ./deploy-oracle-cloud.sh

# 자동 진행 과정 (15-20분):
# ✅ Step 1:  시스템 환경 확인
# ✅ Step 2:  시스템 업데이트
# ✅ Step 3:  필수 패키지 설치
# ✅ Step 4:  Docker 설치
# ✅ Step 5:  방화벽 설정 (UFW)
# ✅ Step 6:  프로젝트 클론
# ✅ Step 7:  환경 변수 생성
# ✅ Step 8:  Docker Compose 설정
# ✅ Step 9:  PostgreSQL & Redis 시작
# ✅ Step 10: 데이터베이스 마이그레이션
# ✅ Step 11: Backend API 시작
# ✅ Step 12: Netdata 모니터링 설치
# ✅ Step 13: 헬스체크 및 검증
```

##### **Frontend VM 배포 (선택 - 권장)**

```bash
# 1. 새 터미널에서 SSH 접속
chmod 400 uvis-frontend.key
ssh -i uvis-frontend.key ubuntu@132.145.YYY.YYY

# 2. 시스템 업데이트 및 패키지 설치
sudo apt update && sudo apt upgrade -y
sudo apt install -y nginx git curl

# 3. Node.js 설치 (v18.x)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 4. 방화벽 설정
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 5. 프로젝트 클론
sudo mkdir -p /opt/uvis
sudo chown ubuntu:ubuntu /opt/uvis
cd /opt/uvis
git clone https://github.com/rpaakdi1-spec/3-.git .
git checkout genspark_ai_developer

# 6. Frontend 환경 변수 설정
cd /opt/uvis/frontend
cat > .env << EOF
VITE_API_URL=http://132.145.XXX.XXX:8000/api/v1
VITE_WS_URL=ws://132.145.XXX.XXX:8001/ws
EOF

# 7. 의존성 설치 및 빌드
npm install
npm run build

# 8. Nginx 설정
sudo tee /etc/nginx/sites-available/uvis > /dev/null << 'NGINX_EOF'
server {
    listen 80;
    server_name _;
    root /opt/uvis/frontend/dist;
    index index.html;
    
    # Frontend static files
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API proxy
    location /api/ {
        proxy_pass http://132.145.XXX.XXX:8000;  # Backend IP로 변경!
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # WebSocket proxy
    location /ws/ {
        proxy_pass http://132.145.XXX.XXX:8001;  # Backend IP로 변경!
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/json application/javascript;
}
NGINX_EOF

# 9. Nginx 활성화
sudo ln -s /etc/nginx/sites-available/uvis /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# ✅ Frontend 배포 완료!
```

---

### **배포 완료 확인**

#### **접속 정보**
```
Frontend:        http://132.145.YYY.YYY
Backend API:     http://132.145.XXX.XXX:8000
API Docs:        http://132.145.XXX.XXX:8000/docs
Health Check:    http://132.145.XXX.XXX:8000/health
Monitoring:      http://132.145.XXX.XXX:19999
```

#### **확인 체크리스트**
- [ ] Frontend 로딩 성공
- [ ] Backend API Health Check: `{"status":"healthy"}`
- [ ] API Docs (Swagger UI) 표시
- [ ] 로그인 기능 테스트
- [ ] Netdata 모니터링 접속 성공

---

### **Oracle Cloud 관리 명령어**

#### **Backend VM 관리**
```bash
# SSH 접속
ssh -i uvis-backend.key ubuntu@132.145.XXX.XXX

# 로그 확인
docker-compose -f docker-compose.oracle.yml logs -f

# 서비스 재시작
docker-compose -f docker-compose.oracle.yml restart

# 서비스 중지
docker-compose -f docker-compose.oracle.yml down

# 서비스 시작
docker-compose -f docker-compose.oracle.yml up -d

# 컨테이너 상태
docker ps -a

# 데이터베이스 백업
docker exec uvis-postgres pg_dump -U uvis_user uvis_db > backup_$(date +%Y%m%d).sql
```

#### **Frontend VM 관리**
```bash
# SSH 접속
ssh -i uvis-frontend.key ubuntu@132.145.YYY.YYY

# Nginx 재시작
sudo systemctl restart nginx

# Nginx 로그
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Frontend 재빌드
cd /opt/uvis/frontend
npm run build
sudo systemctl restart nginx
```

---

### **비용 완전 무료 확인**

#### **Oracle Cloud 무료 사용량 확인**
```
1. Oracle Cloud Console 로그인
2. 좌측 메뉴 → "Governance & Administration" → "Cost Management"
3. "Usage" 클릭

확인 사항:
✅ Always Free 리소스만 사용 중
✅ 청구 금액: $0.00
✅ 예상 청구: $0.00

⚠️  주의: Always Free가 아닌 리소스 생성 시 과금됨
    (예: 더 큰 VM, Paid Database 등)
```

---

### **Oracle Cloud vs Hetzner 비교**

```yaml
비용 (1년 기준):
  Oracle Cloud:    $0
  Hetzner:         $58.80 (€4.49/월 × 12)
  절감액:          $58.80/년
  
성능:
  Oracle:
    - VM 2개 (각 1 vCPU, 1GB RAM)
    - 총 2 vCPU, 2GB RAM
    - 100GB 스토리지
    - 제한: CPU 성능 낮음 (1/8 OCPU)
  
  Hetzner:
    - VM 1개 (2 vCPU, 4GB RAM)
    - 40GB NVMe SSD (빠름)
    - 20TB 트래픽
    - 장점: 더 빠른 CPU, 더 많은 RAM
    
배포 난이도:
  Oracle:    ⭐⭐⭐ (중간 - VM 2개 관리)
  Hetzner:   ⭐⭐ (쉬움 - 단일 서버, 자동화)
  
적합한 경우:
  Oracle:
    ✅ 예산 제약이 있는 경우
    ✅ 학습/테스트 목적
    ✅ 소규모 사용자 (<100명)
    ✅ 트래픽이 적은 경우
    
  Hetzner:
    ✅ 프로덕션 환경
    ✅ 더 나은 성능 필요
    ✅ 간단한 관리 원함
    ✅ 중대규모 사용자 (100-1000명)
```

---

### **추가 리소스**

#### **상세 가이드**
- **Oracle Cloud 전체 가이드**: [ORACLE_CLOUD_DEPLOYMENT_GUIDE.md](./ORACLE_CLOUD_DEPLOYMENT_GUIDE.md)
- **Oracle Cloud 빠른 시작**: [ORACLE_QUICK_START.md](./ORACLE_QUICK_START.md)
- **비용 최적화**: [COST_REDUCTION_STRATEGIES.md](./COST_REDUCTION_STRATEGIES.md)
- **클라우드 비교**: [CLOUD_ALTERNATIVES.md](./CLOUD_ALTERNATIVES.md)

#### **자동 배포 스크립트**
- **Oracle Cloud 스크립트**: [deploy-oracle-cloud.sh](./deploy-oracle-cloud.sh)
- **Docker Compose**: [docker-compose.oracle.yml](./docker-compose.oracle.yml)

#### **지원**
- **Oracle Cloud Docs**: https://docs.oracle.com/
- **Oracle Cloud Free Tier**: https://www.oracle.com/cloud/free/
- **GitHub Issues**: https://github.com/rpaakdi1-spec/3-/issues

---

## 🎯 배포 옵션 권장 사항

### **선택 가이드**

```
예산이 있다면 → Hetzner (Option A) 추천 ✅
  - 빠른 배포 (20분)
  - 더 나은 성능 (2 vCPU, 4GB RAM)
  - 간단한 관리 (단일 서버)
  - 비용: $4.90/월 ($58.80/년)
  - AWS 대비 98.5% 절감

예산이 없다면 → Oracle Cloud (Option B) 추천 ✅
  - 완전 무료 ($0/월, 평생)
  - 충분한 성능 (소규모용)
  - 배포 시간: 30-60분
  - VM 2개 관리 필요
  - AWS 대비 100% 절감

최고 성능 필요 → Hetzner CX32 업그레이드
  - 4 vCPU, 8GB RAM
  - €8.49/월 ($9.28/월)
  - 중대규모 트래픽 처리

테스트/개발용 → Oracle Cloud (무료)
  - 비용 부담 없음
  - 실험 가능
  - 프로덕션 전환 쉬움
```

---

**작성일**: 2026-01-28  
**버전**: 2.0.0  
**상태**: 배포 옵션 추가 완료  
**배포 옵션**: Hetzner (유료) + Oracle Cloud (무료)

🚀 **Happy Deploying!**
