---
**프로덕션 배포 가이드: WebSocket 오류 수정**
---

## 🚀 즉시 실행 가능한 명령 (프로덕션 서버)

### 전체 과정 (자동화)

```bash
# SSH로 프로덕션 서버 접속
ssh user@139.150.11.99

# 프로젝트 디렉터리로 이동
cd /root/uvis

# 최신 코드 Pull
git fetch origin phase8-verification
git checkout phase8-verification
git pull origin phase8-verification

# 배포 스크립트 실행 (모든 과정 자동화)
bash fix_websocket_production.sh
```

**예상 소요 시간**: 5-10분

---

## 📋 단계별 실행 (수동)

원하시면 단계별로 실행할 수도 있습니다:

### Step 1: 코드 가져오기
```bash
cd /root/uvis
git fetch origin phase8-verification
git checkout phase8-verification
git pull origin phase8-verification
```

### Step 2: 백엔드 중지 및 제거
```bash
docker-compose stop backend
docker-compose rm -f backend
```

### Step 3: 변경사항 확인
```bash
# 수정된 파일 확인
git log -1 --stat

# realtime_metrics_service.py 변경사항 확인
git diff HEAD~1 backend/app/services/realtime_metrics_service.py
```

### Step 4: Docker 이미지 재빌드
```bash
# 기존 이미지 제거
docker rmi uvis-backend 2>/dev/null || true

# 캐시 없이 재빌드
docker-compose build --no-cache backend
```

### Step 5: 백엔드 시작
```bash
docker-compose up -d backend
```

### Step 6: 시작 대기 (30초)
```bash
sleep 30
```

### Step 7: 검증
```bash
# 헬스 체크 실행
bash check_websocket_health.sh

# 또는 수동 확인
docker logs uvis-backend --since 5m 2>&1 | grep -i "error broadcasting"
# 기대 결과: 출력 없음 (0건)
```

---

## ✅ 검증 체크리스트

### 1. 컨테이너 상태 확인
```bash
docker ps | grep uvis-backend
```
✅ **기대**: `uvis-backend`가 `Up` 상태

### 2. WebSocket 오류 확인
```bash
docker logs uvis-backend 2>&1 | grep -i "error broadcasting" | tail -20
```
✅ **기대**: 출력 없음 (오류 0건)

### 3. 헬스 체크
```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```
✅ **기대**:
```json
{
  "status": "healthy",
  "app_name": "Cold Chain Dispatch System",
  "environment": "production"
}
```

### 4. 실시간 로그 모니터링 (30초간)
```bash
docker logs -f uvis-backend &
PID=$!
sleep 30
kill $PID
```
✅ **기대**: "Error broadcasting" 메시지 없음

### 5. 프론트엔드 테스트
```
1. 브라우저에서 http://139.150.11.99/ 접속
2. 로그인: admin / admin123
3. 대시보드로 이동
4. F12 → Network 탭 → WS 필터
5. WebSocket 연결 확인
6. 메시지 수신 확인 (5초마다)
```
✅ **기대**: WebSocket 정상 연결 및 메시지 수신

---

## 🔍 문제 해결

### 문제 1: "Error broadcasting" 메시지가 여전히 나타남

**원인**: Docker 캐시 문제

**해결**:
```bash
cd /root/uvis
docker-compose stop backend
docker-compose rm -f backend
docker rmi uvis-backend
docker system prune -f
docker-compose build --no-cache backend
docker-compose up -d backend
sleep 30
docker logs uvis-backend --since 30s
```

---

### 문제 2: 백엔드 컨테이너가 시작되지 않음

**원인**: 설정 또는 의존성 문제

**확인**:
```bash
# 컨테이너 상태 확인
docker ps -a | grep backend

# 전체 로그 확인
docker logs uvis-backend 2>&1 | tail -100

# 의존성 컨테이너 확인
docker ps | grep -E "uvis-db|uvis-redis"
```

**해결**:
```bash
# 전체 스택 재시작
docker-compose down
docker-compose up -d
sleep 30
docker-compose ps
```

---

### 문제 3: WebSocket 연결은 되는데 메시지가 수신되지 않음

**원인**: Redis 연결 문제

**확인**:
```bash
# Redis 상태 확인
docker ps | grep redis
docker logs uvis-redis --tail 20

# Redis 연결 테스트
docker exec uvis-redis redis-cli ping
# 기대 출력: PONG
```

**해결**:
```bash
# Redis 재시작
docker-compose restart redis
sleep 10
docker-compose restart backend
```

---

## 📊 배포 후 모니터링

### 24시간 모니터링 스크립트

파일: `/root/uvis/monitor_websocket.sh`
```bash
#!/bin/bash

echo "Starting 24-hour WebSocket monitoring..."
echo "Log file: /tmp/websocket_monitor.log"
echo ""

# 로그 파일 초기화
> /tmp/websocket_monitor.log

# 24시간 동안 5분마다 체크
for i in {1..288}; do
    echo "=== Check #$i at $(date) ===" >> /tmp/websocket_monitor.log
    
    # WebSocket 오류 확인
    ERROR_COUNT=$(docker logs uvis-backend --since 5m 2>&1 | grep -c "Error broadcasting")
    echo "WebSocket errors in last 5 minutes: $ERROR_COUNT" >> /tmp/websocket_monitor.log
    
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo "❌ ALERT: WebSocket errors detected!" >> /tmp/websocket_monitor.log
        docker logs uvis-backend --since 5m 2>&1 | grep "Error broadcasting" >> /tmp/websocket_monitor.log
    else
        echo "✅ No errors" >> /tmp/websocket_monitor.log
    fi
    
    echo "" >> /tmp/websocket_monitor.log
    
    # 5분 대기
    sleep 300
done

echo "Monitoring complete. Check /tmp/websocket_monitor.log for results."
```

실행:
```bash
chmod +x /root/uvis/monitor_websocket.sh
nohup /root/uvis/monitor_websocket.sh &
```

로그 확인:
```bash
tail -f /tmp/websocket_monitor.log
```

---

## 📞 지원 연락처

문제가 지속되면 다음 정보를 수집해주세요:

### 1. 로그 수집
```bash
# 백엔드 로그
docker logs uvis-backend > /tmp/backend_logs_$(date +%Y%m%d_%H%M%S).txt 2>&1

# Redis 로그
docker logs uvis-redis > /tmp/redis_logs_$(date +%Y%m%d_%H%M%S).txt 2>&1

# 데이터베이스 로그
docker logs uvis-db > /tmp/db_logs_$(date +%Y%m%d_%H%M%S).txt 2>&1
```

### 2. 시스템 정보
```bash
# Docker 버전
docker --version > /tmp/system_info.txt

# 컨테이너 상태
docker ps -a >> /tmp/system_info.txt

# 이미지 정보
docker images | grep uvis >> /tmp/system_info.txt

# 네트워크 정보
docker network inspect uvis_default >> /tmp/system_info.txt

# 시스템 리소스
free -h >> /tmp/system_info.txt
df -h >> /tmp/system_info.txt
```

### 3. 설정 파일
```bash
# Docker Compose 설정
cat docker-compose.yml > /tmp/docker-compose.txt

# 환경 변수 (민감 정보 제외)
env | grep -i uvis | grep -v PASSWORD | grep -v SECRET > /tmp/env.txt
```

---

## ✅ 최종 체크리스트

배포 완료 후 다음을 확인하세요:

- [ ] Git 최신 코드 Pull 완료
- [ ] Docker 이미지 재빌드 완료
- [ ] 백엔드 컨테이너 실행 중
- [ ] WebSocket 오류 0건 확인
- [ ] 헬스 체크 통과
- [ ] 프론트엔드 접속 가능
- [ ] WebSocket 연결 정상
- [ ] 실시간 메트릭 업데이트 확인
- [ ] 24시간 모니터링 설정
- [ ] PR #5 업데이트 (선택)

---

## 🎉 성공 확인

모든 체크리스트가 완료되면:

```bash
echo "🎉 WebSocket 오류 수정 완료!"
echo "✅ 백엔드: 정상 작동"
echo "✅ WebSocket: 오류 0건"
echo "✅ 실시간 업데이트: 정상"
echo ""
echo "다음 24시간 동안 모니터링을 계속하세요."
echo "로그: tail -f /tmp/websocket_monitor.log"
```

---

**작성일**: 2026-02-07  
**커밋**: 8cbe2a9  
**브랜치**: phase8-verification  
**PR**: #5 (https://github.com/rpaakdi1-spec/3-/pull/5)
