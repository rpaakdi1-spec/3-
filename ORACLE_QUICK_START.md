# 🚀 Oracle Cloud 배포 - 빠른 시작

**비용**: $0/월 (완전 무료, 영구)  
**소요 시간**: 30-60분  
**난이도**: ⭐⭐⭐ (중간)

---

## ⚡ 3단계로 배포하기

### 1️⃣ Oracle Cloud 가입 (10분)

```
1. 접속: https://www.oracle.com/cloud/free/
2. "Start for free" 클릭
3. 이메일 인증
4. 계정 정보 입력:
   - Home Region: South Korea Central (Seoul) 또는
   - Home Region: Japan Central (Tokyo) 권장
5. 신용카드 등록 (본인 확인용, 청구 안됨)
6. ✅ 가입 완료!
```

### 2️⃣ VM 생성 (15분)

#### VM 1: Backend (PostgreSQL + Redis + FastAPI)
```
Oracle Cloud Console → Compute → Instances → Create Instance

Settings:
  Name: coldchain-backend
  Image: Ubuntu 22.04
  Shape: VM.Standard.E2.1.Micro (Always Free!)
  Network: Create new VCN
  SSH Key: Generate (다운로드 필수!)
  
✅ Public IP 확인: 132.145.XXX.XXX
```

#### VM 2: Frontend (React + Nginx)
```
Create Instance (같은 방법)

Settings:
  Name: coldchain-frontend
  Image: Ubuntu 22.04
  Shape: VM.Standard.E2.1.Micro (Always Free!)
  Network: Select existing (coldchain-vcn)
  SSH Key: Generate (다운로드!)
  
✅ Public IP 확인: 132.145.YYY.YYY
```

#### 방화벽 설정
```
VCN → Security Lists → Add Ingress Rules:

포트 80, 443, 8000, 8001 열기
(HTTP, HTTPS, Backend API, WebSocket)
```

### 3️⃣ 자동 배포 (20분)

#### Backend VM 배포
```bash
# 1. SSH 접속
ssh -i coldchain-backend.key ubuntu@132.145.XXX.XXX

# 2. 배포 스크립트 다운로드 & 실행
wget https://raw.githubusercontent.com/rpaakdi1-spec/3-/genspark_ai_developer/deploy-oracle-cloud.sh
chmod +x deploy-oracle-cloud.sh
sudo ./deploy-oracle-cloud.sh

# 3. 완료 대기 (약 10-15분)
# ✅ 자동으로 설치:
#    - Docker, Docker Compose
#    - PostgreSQL, Redis
#    - Backend API
#    - 방화벽 설정
#    - Netdata 모니터링 (선택)
```

#### Frontend VM 배포
```bash
# 1. SSH 접속
ssh -i coldchain-frontend.key ubuntu@132.145.YYY.YYY

# 2. Nginx + Frontend 설치
sudo apt update
sudo apt install -y nginx git curl

# 3. Node.js 설치
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 4. 프로젝트 클론
sudo mkdir -p /opt/coldchain
sudo chown ubuntu:ubuntu /opt/coldchain
cd /opt/coldchain
git clone https://github.com/rpaakdi1-spec/3-.git .
git checkout genspark_ai_developer

# 5. Frontend 빌드
cd frontend
cat > .env << EOF
VITE_API_URL=http://132.145.XXX.XXX:8000/api/v1
VITE_WS_URL=ws://132.145.XXX.XXX:8001/ws
EOF

npm install
npm run build

# 6. Nginx 설정
sudo tee /etc/nginx/sites-available/coldchain > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;
    root /opt/coldchain/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://132.145.XXX.XXX:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /ws/ {
        proxy_pass http://132.145.XXX.XXX:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}
EOF

# Nginx 활성화
sudo ln -s /etc/nginx/sites-available/coldchain /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

## ✅ 완료!

### 접속 정보
```
Frontend: http://132.145.YYY.YYY
Backend API: http://132.145.XXX.XXX:8000/docs
Monitoring: http://132.145.XXX.XXX:19999
```

### 확인 사항
- [ ] Frontend 로딩 확인
- [ ] Backend API Health Check
- [ ] 로그인 테스트
- [ ] 대시보드 확인

---

## 🔧 유용한 명령어

### Backend VM
```bash
# 로그 확인
docker-compose -f docker-compose.oracle.yml logs -f

# 재시작
docker-compose -f docker-compose.oracle.yml restart

# 상태 확인
docker ps

# 컨테이너 접속
docker exec -it coldchain-backend bash
```

### Frontend VM
```bash
# Nginx 재시작
sudo systemctl restart nginx

# 로그 확인
sudo tail -f /var/log/nginx/access.log

# Frontend 재빌드
cd /opt/coldchain/frontend
npm run build
```

### 업데이트
```bash
# Backend
cd /opt/coldchain
git pull
docker-compose -f docker-compose.oracle.yml up -d --build

# Frontend
cd /opt/coldchain/frontend
git pull
npm run build
sudo systemctl restart nginx
```

---

## 🎯 트러블슈팅

### 1. Backend API 접속 안됨
```bash
# 방화벽 확인
sudo ufw status

# 컨테이너 로그
docker logs coldchain-backend

# 재시작
docker-compose -f docker-compose.oracle.yml restart
```

### 2. Frontend 로딩 안됨
```bash
# Nginx 상태
sudo systemctl status nginx

# 설정 테스트
sudo nginx -t

# 로그 확인
sudo tail -f /var/log/nginx/error.log
```

### 3. 데이터베이스 연결 오류
```bash
# PostgreSQL 컨테이너 확인
docker logs coldchain-postgres

# 재시작
docker-compose -f docker-compose.oracle.yml restart postgres
```

---

## 💰 비용

```yaml
VM 1 (Backend):      $0/월 (Always Free)
VM 2 (Frontend):     $0/월 (Always Free)
Storage (200GB):     $0/월 (Always Free)
Traffic (10TB/월):   $0/월 (Always Free)
────────────────────────────────────────
Total:               $0/월 (완전 무료!)

vs AWS 예상 비용:    $320/월
절감액:              $320/월 (100% 절감!)
```

---

## 📞 지원

### 문서
- 상세 가이드: `ORACLE_CLOUD_DEPLOYMENT_GUIDE.md`
- 비용 절감: `COST_REDUCTION_STRATEGIES.md`
- 전체 README: `README.md`

### 저장소
- GitHub: https://github.com/rpaakdi1-spec/3-
- Branch: genspark_ai_developer
- Commit: d0bbeb3

---

**작성일**: 2026-01-28  
**상태**: ✅ 배포 준비 완료  
**예상 시간**: 30-60분  
**비용**: $0/월 (영구 무료!)
