# 🚀 AI 배차 모니터링 대시보드 배포 가이드

## 📋 목차
1. [자동 배포 (권장)](#자동-배포)
2. [수동 배포](#수동-배포)
3. [Docker 배포](#docker-배포)
4. [확인 및 테스트](#확인-및-테스트)
5. [문제 해결](#문제-해결)

---

## 🎯 자동 배포 (권장)

서버에서 다음 명령어를 실행하세요:

```bash
cd /root/uvis
chmod +x DEPLOY_DISPATCH_MONITORING.sh
./DEPLOY_DISPATCH_MONITORING.sh
```

이 스크립트는 자동으로:
- ✅ Git pull로 최신 코드 가져오기
- ✅ 백엔드 재시작
- ✅ 프론트엔드 빌드
- ✅ 빌드 파일 배포
- ✅ 헬스 체크

---

## 🔧 수동 배포

### Step 1: Git Pull
```bash
cd /root/uvis
git pull origin main
```

### Step 2: 백엔드 재시작

#### Docker 사용 시:
```bash
cd /root/uvis
docker-compose restart backend

# 로그 확인
docker-compose logs -f backend
```

#### PM2 사용 시:
```bash
pm2 restart uvis-backend
pm2 logs uvis-backend
```

#### systemd 사용 시:
```bash
sudo systemctl restart uvis-backend
sudo systemctl status uvis-backend
```

### Step 3: 프론트엔드 빌드
```bash
cd /root/uvis/frontend
npm run build
```

### Step 4: 프론트엔드 배포

#### Docker 사용 시:
```bash
# 기존 파일 삭제
docker exec uvis-frontend rm -rf /usr/share/nginx/html/*

# 새 빌드 복사
docker cp dist/. uvis-frontend:/usr/share/nginx/html/

# 재시작
docker-compose restart frontend
```

#### Nginx 직접 사용 시:
```bash
# 빌드 파일 복사
sudo cp -r dist/* /var/www/html/

# Nginx 재시작
sudo systemctl reload nginx
```

---

## 🐳 Docker 배포 (상세)

### 1. Docker Compose 확인
```bash
cd /root/uvis
cat docker-compose.yml | grep -A 5 backend
cat docker-compose.yml | grep -A 5 frontend
```

### 2. 컨테이너 상태 확인
```bash
docker-compose ps
```

### 3. 전체 재시작 (필요시)
```bash
# 모든 컨테이너 재시작
docker-compose restart

# 또는 개별 재시작
docker-compose restart backend
docker-compose restart frontend
```

### 4. 로그 확인
```bash
# 실시간 로그
docker-compose logs -f backend
docker-compose logs -f frontend

# 최근 100줄
docker-compose logs --tail=100 backend
```

---

## ✅ 확인 및 테스트

### 1. 백엔드 API 테스트
```bash
# 헬스 체크
curl http://139.150.11.99/api/v1/health

# 실시간 통계
curl http://139.150.11.99/api/v1/dispatch/monitoring/live-stats

# Agent 성능
curl http://139.150.11.99/api/v1/dispatch/monitoring/agent-performance?days=30

# 최고 성과 차량
curl http://139.150.11.99/api/v1/dispatch/monitoring/top-vehicles?limit=10
```

### 2. 프론트엔드 접속
```
브라우저에서 접속:
http://139.150.11.99/dispatch/monitoring

Ctrl + Shift + R (강력 새로고침)
```

### 3. 브라우저 개발자 도구 확인
```
1. F12 키를 눌러 개발자 도구 열기
2. Console 탭: JavaScript 에러 확인
3. Network 탭: API 요청 확인
4. 필터: "monitoring" 입력
```

---

## 🔍 문제 해결

### 문제 1: 백엔드 API 404 에러

**증상:**
```
GET /api/v1/dispatch/monitoring/live-stats → 404 Not Found
```

**해결:**
```bash
# 1. 백엔드 로그 확인
docker-compose logs backend | grep "dispatch/monitoring"

# 2. 라우터 등록 확인
docker exec uvis-backend cat /app/main.py | grep "dispatch_monitoring"

# 3. 백엔드 재시작
docker-compose restart backend
```

### 문제 2: 프론트엔드 페이지 404 에러

**증상:**
```
http://139.150.11.99/dispatch/monitoring → 404 Not Found
```

**해결:**
```bash
# 1. 빌드 파일 존재 확인
docker exec uvis-frontend ls -la /usr/share/nginx/html/assets/ | grep DispatchMonitoring

# 2. Nginx 설정 확인
docker exec uvis-frontend cat /etc/nginx/conf.d/default.conf

# 3. 프론트엔드 재배포
cd /root/uvis/frontend
npm run build
docker cp dist/. uvis-frontend:/usr/share/nginx/html/
docker-compose restart frontend
```

### 문제 3: 빌드 파일이 로드되지 않음

**증상:**
```
브라우저 Console:
Failed to load resource: net::ERR_FILE_NOT_FOUND
```

**해결:**
```bash
# 1. 브라우저 캐시 완전 삭제
F12 → Application → Storage → Clear site data

# 2. 시크릿 모드로 접속
Ctrl + Shift + N (Chrome)
Ctrl + Shift + P (Firefox)

# 3. 파일 존재 확인
docker exec uvis-frontend ls -lh /usr/share/nginx/html/assets/ | grep -i dispatch
```

### 문제 4: WebSocket 연결 실패

**증상:**
```
WebSocket connection to 'ws://...' failed
```

**해결:**
```bash
# 1. Nginx WebSocket 설정 확인
docker exec uvis-frontend cat /etc/nginx/conf.d/default.conf | grep -A 5 "websocket"

# 2. 백엔드 WebSocket 엔드포인트 확인
curl http://139.150.11.99/api/v1/health

# 3. 방화벽 확인
sudo firewall-cmd --list-all | grep 8000
```

### 문제 5: 모듈 import 에러

**증상:**
```
ModuleNotFoundError: No module named 'app.api.dispatch_monitoring'
```

**해결:**
```bash
# 1. 파일 존재 확인
ls -la /root/uvis/backend/app/api/dispatch_monitoring.py

# 2. Python 경로 확인
docker exec uvis-backend python3 -c "import sys; print('\n'.join(sys.path))"

# 3. 컨테이너 재빌드 (필요시)
docker-compose down
docker-compose up -d --build
```

---

## 📞 지원

문제가 지속되면 다음 정보를 제공해주세요:

```bash
# 시스템 정보
docker-compose ps
docker-compose logs --tail=50 backend
docker-compose logs --tail=50 frontend

# API 테스트
curl -v http://139.150.11.99/api/v1/health
curl -v http://139.150.11.99/api/v1/dispatch/monitoring/live-stats

# 파일 확인
ls -la /root/uvis/backend/app/api/ | grep dispatch
ls -la /root/uvis/frontend/dist/assets/ | grep Dispatch
```

---

## 🎯 빠른 체크리스트

배포 전:
- [ ] Git pull 완료
- [ ] 백엔드 코드 수정 확인
- [ ] 프론트엔드 코드 수정 확인

배포 중:
- [ ] 백엔드 재시작 완료
- [ ] 프론트엔드 빌드 성공
- [ ] 빌드 파일 배포 완료
- [ ] 컨테이너 재시작 완료

배포 후:
- [ ] API 헬스 체크 성공
- [ ] 프론트엔드 접속 성공
- [ ] 브라우저 캐시 삭제
- [ ] 실시간 통계 확인
- [ ] WebSocket 연결 확인

---

**작성일**: 2026-02-14  
**버전**: 1.0
