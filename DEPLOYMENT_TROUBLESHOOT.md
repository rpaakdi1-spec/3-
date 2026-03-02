# 배포 문제 해결 가이드

## 현재 상태
- ✅ Backend: 정상 빌드 및 시작
- ❌ Frontend: 계속 재시작 (Restarting)
- ❌ Health Check: 502 Bad Gateway

## 진단 명령어

### 1. 프론트엔드 로그 확인
```bash
docker compose logs frontend --tail=100
```

### 2. 프론트엔드 상세 로그 확인 (실시간)
```bash
docker compose logs -f frontend
```

### 3. 백엔드 로그 확인
```bash
docker compose logs backend --tail=100
```

### 4. 컨테이너 상태 확인
```bash
docker compose ps
```

### 5. 프론트엔드 컨테이너 내부 확인
```bash
docker compose exec frontend ls -la /usr/share/nginx/html/
```

### 6. Nginx 설정 테스트
```bash
docker compose exec frontend nginx -t
```

## 일반적인 문제 및 해결책

### Problem 1: Frontend 빌드 실패
**증상**: 컨테이너가 계속 재시작
**확인**:
```bash
docker compose logs frontend | grep -i error
```

**해결**:
```bash
# 프론트엔드 재빌드
docker compose build --no-cache frontend
docker compose up -d frontend
```

### Problem 2: Nginx 설정 오류
**증상**: 502 Bad Gateway
**확인**:
```bash
docker compose exec frontend nginx -t
docker compose exec frontend cat /var/log/nginx/error.log
```

**해결**:
```bash
# Nginx 설정 확인 후 재시작
docker compose restart frontend
```

### Problem 3: Backend 연결 실패
**증상**: 502 Bad Gateway, Frontend는 정상
**확인**:
```bash
# Backend 상태 확인
docker compose ps backend
docker compose logs backend --tail=50

# Backend 헬스체크
curl http://localhost:8000/health
```

**해결**:
```bash
# Backend 재시작
docker compose restart backend
```

### Problem 4: 포트 충돌
**증상**: 컨테이너 시작 실패
**확인**:
```bash
netstat -tuln | grep -E '80|8000'
```

**해결**:
```bash
# 충돌하는 프로세스 중지 후 재시작
docker compose down
docker compose up -d
```

## 완전 재배포 (최후의 수단)

```bash
# 1. 모든 컨테이너 중지 및 제거
docker compose down

# 2. 캐시 없이 완전 재빌드
docker compose build --no-cache

# 3. 컨테이너 시작
docker compose up -d

# 4. 로그 모니터링
docker compose logs -f

# 5. 상태 확인
docker compose ps
```

## 로그 수집 (문제 보고용)

```bash
# 모든 로그를 파일로 저장
docker compose logs > /tmp/uvis_logs.txt

# 또는 개별 서비스별로
docker compose logs frontend > /tmp/frontend_logs.txt
docker compose logs backend > /tmp/backend_logs.txt
```

## 빠른 진단 스크립트

```bash
#!/bin/bash
echo "=== Container Status ==="
docker compose ps

echo -e "\n=== Frontend Logs (Last 30 lines) ==="
docker compose logs frontend --tail=30

echo -e "\n=== Backend Logs (Last 30 lines) ==="
docker compose logs backend --tail=30

echo -e "\n=== Frontend Health ==="
docker compose exec frontend ls -la /usr/share/nginx/html/ 2>/dev/null || echo "Frontend not running"

echo -e "\n=== Backend Health ==="
curl -s http://localhost:8000/health || echo "Backend not responding"

echo -e "\n=== Nginx Test ==="
docker compose exec frontend nginx -t 2>&1 || echo "Nginx test failed"
```

위 스크립트를 `diagnose.sh`로 저장하고 실행:
```bash
chmod +x diagnose.sh
./diagnose.sh
```
