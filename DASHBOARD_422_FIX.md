# 🔧 대시보드 422 에러 해결 가이드

**날짜**: 2026-02-25  
**문제**: GET /api/v1/dispatches/dashboard → 422 Unprocessable Entity  
**원인**: FastAPI 라우트 순서 문제

---

## 🔍 문제 분석

### 에러 메시지:
```json
{
  "detail": [{
    "type": "int_parsing",
    "loc": ["path", "dispatch_id"],
    "msg": "Input should be a valid integer, unable to parse string as an integer",
    "input": "dashboard"
  }]
}
```

### 원인:
백엔드 FastAPI가 `/api/v1/dispatches/dashboard`를 `/api/v1/dispatches/{dispatch_id}` 경로로 매칭하여 `"dashboard"`를 정수로 파싱하려고 시도함.

---

## 🛠️ 해결 방법

### 방법 1: 백엔드 라우트 순서 수정 (추천)

**파일**: `/root/uvis/backend/app/api/dispatches.py`

**수정 전** (잘못된 순서):
```python
@router.get("/{dispatch_id}")
async def get_dispatch(dispatch_id: int, ...):
    ...

@router.get("/dashboard")
async def get_dashboard(...):
    ...
```

**수정 후** (올바른 순서):
```python
# 구체적인 경로를 먼저 정의
@router.get("/dashboard")
async def get_dashboard(...):
    ...

@router.get("/stats/summary")
async def get_stats_summary(...):
    ...

# 동적 경로는 마지막에
@router.get("/{dispatch_id}")
async def get_dispatch(dispatch_id: int, ...):
    ...
```

**적용 명령어**:
```bash
cd /root/uvis/backend

# 백업
cp app/api/dispatches.py app/api/dispatches.py.backup

# 파일 편집
vi app/api/dispatches.py
# 또는
nano app/api/dispatches.py

# 백엔드 재시작
docker restart uvis-backend

# 10초 대기
sleep 10

# 테스트
TOKEN=$(curl -s -X POST http://139.150.11.99/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

curl -X GET http://139.150.11.99/api/v1/dispatches/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

---

### 방법 2: 프론트엔드 API 경로 변경

대시보드 API가 다른 경로에 있다면 프론트엔드를 수정:

**파일**: `/root/uvis/frontend/src/api/client.ts` 또는 `src/config/api.ts`

**확인 필요**: 백엔드의 실제 대시보드 엔드포인트

가능한 경로:
- `/api/v1/dashboard`
- `/api/v1/monitoring/dashboard`
- `/api/v1/dispatches/stats/summary`

---

## 📋 진단 명령어

### 1. 백엔드 라우트 확인
```bash
# dispatches API의 모든 GET 라우트 확인
docker exec uvis-backend grep -E "@router\.get" /app/app/api/dispatches.py | head -20

# dashboard 관련 라우트 찾기
docker exec uvis-backend grep -r "def.*dashboard" /app/app/api --include="*.py"

# 라우트 등록 순서 확인
docker exec uvis-backend sed -n '1,200p' /app/app/api/dispatches.py | grep -E "@router|async def"
```

### 2. 백엔드 로그 모니터링
```bash
# 실시간 로그 확인
docker logs -f uvis-backend

# 별도 터미널에서 API 호출
curl -X GET http://139.150.11.99/api/v1/dispatches/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎯 WebSocket 403 에러 해결

**문제**: WebSocket `/api/v1/dispatches/ws/dashboard` → 403 Forbidden

### 원인:
1. WebSocket이 JWT 토큰을 요구하는데 전송되지 않음
2. Nginx WebSocket 프록시 미설정

### 해결 1: Nginx WebSocket 프록시 추가

```bash
cd /root/uvis/frontend

# nginx.conf 편집
vi nginx.conf
```

다음 블록을 `server { }` 안에 추가 (location /api/v1/ 블록 위에):

```nginx
# WebSocket for dispatches
location /api/v1/dispatches/ws/ {
    proxy_pass http://backend:8000/api/v1/dispatches/ws/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # WebSocket은 긴 연결 유지
    proxy_connect_timeout 7d;
    proxy_send_timeout 7d;
    proxy_read_timeout 7d;
}
```

적용:
```bash
docker cp nginx.conf uvis-frontend:/etc/nginx/nginx.conf
docker exec uvis-frontend nginx -t
docker exec uvis-frontend nginx -s reload
```

### 해결 2: WebSocket 인증 토큰 전달

프론트엔드가 WebSocket 연결 시 토큰을 쿼리 파라미터로 전달해야 할 수 있음:

```typescript
// 수정 전
const ws = new WebSocket('ws://139.150.11.99/api/v1/dispatches/ws/dashboard');

// 수정 후
const token = localStorage.getItem('access_token');
const ws = new WebSocket(`ws://139.150.11.99/api/v1/dispatches/ws/dashboard?token=${token}`);
```

---

## ✅ 검증

### 1. 대시보드 API 테스트
```bash
TOKEN=$(curl -s -X POST http://139.150.11.99/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

curl -X GET http://139.150.11.99/api/v1/dispatches/dashboard \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**예상 성공 응답**:
```json
{
  "pending_orders": 0,
  "pending_dispatches": 0,
  "in_progress": 0,
  "completed": 0,
  "weekly_stats": [...],
  "delivery_status": [...]
}
```

### 2. 브라우저 테스트
1. 브라우저 새로고침 (Ctrl + F5)
2. F12 → Console 확인
3. Network 탭에서 `/api/v1/dispatches/dashboard` 요청 확인
4. Status: **200 OK** 확인

---

## 📚 관련 문제

1. **반복 에러**: 
   ```
   ❌ Error broadcasting dashboard metrics: ASSIGNED
   ❌ Error broadcasting vehicle updates: object ChunkedIteratorResult can't be used in 'await' expression
   ```
   
   → 백엔드 비동기 코드 버그 (별도 수정 필요, 기능에는 영향 없음)

2. **Health check 404**:
   ```
   GET /api/v1/health → 404
   ```
   
   → Health 엔드포인트가 `/health`에 있지만 `/api/v1/health`로 호출됨

---

## 🎯 우선 순위

1. ✅ **즉시**: 백엔드 라우트 순서 확인 및 수정
2. ✅ **즉시**: 백엔드 재시작 후 테스트
3. ⏳ **중요**: Nginx WebSocket 프록시 추가
4. ⏳ **나중**: 백엔드 비동기 에러 수정

---

**다음 단계**: 위 진단 명령어 실행 후 결과 공유
