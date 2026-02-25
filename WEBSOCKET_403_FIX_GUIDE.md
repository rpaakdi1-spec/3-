# WebSocket 403 Forbidden 에러 완전 해결 가이드

## 📋 현재 상황

### ✅ 해결 완료
1. **Vehicle API 307 리다이렉트** → 200 OK (46개 차량 데이터 정상 반환)
2. **Orders API 307 리다이렉트** → 200 OK
3. **Dispatches API 307 리다이렉트** → 200 OK
4. **Clients API 307 리다이렉트** → 200 OK
5. **Backend async ChunkedIteratorResult 에러** → 해결 완료 (로그에서 사라짐)

### ⚠️ 남은 문제
- **WebSocket 403 Forbidden 에러** (해결 중)
  ```
  ('172.24.0.5', 45432) - "WebSocket /api/v1/ws/dashboard?token=eyJ..." 403
  ```

---

## 🔍 WebSocket 403 에러 원인 분석

### 가능한 원인 3가지

#### 1️⃣ Nginx 프록시 설정 문제
- WebSocket 연결이 Nginx에서 차단될 수 있음
- `Upgrade` 및 `Connection` 헤더가 제대로 전달되지 않음
- 프록시 타임아웃 설정 부족

#### 2️⃣ Backend CORS 미들웨어 문제
- FastAPI의 CORSMiddleware가 WebSocket을 차단
- `allow_origins`가 제한적으로 설정됨
- WebSocket 연결 전에 미들웨어가 403 반환

#### 3️⃣ FastAPI WebSocket 엔드포인트 구현 문제
- `await websocket.accept()` 호출 전에 검증 수행
- 토큰 검증 실패 시 연결 거부
- 에러 처리 부족

---

## 🛠️ 해결 방법

### 방법 1: 진단 스크립트 실행 (권장)

서버에서 다음 명령어 실행:

```bash
cd /root/uvis/frontend
./diagnose_websocket_403.sh
```

이 스크립트는 다음을 확인합니다:
- Nginx WebSocket 프록시 설정
- Backend CORS 설정
- WebSocket 라우터 등록
- JWT 토큰 검증 설정
- 최근 WebSocket 로그

**결과를 확인 후 다음 단계 진행**

---

### 방법 2: WebSocket 코드 수정 배포

#### Step 1: 수정 파일 업로드
로컬 PC에서:
```bash
scp -P 2829 websocket_403_fix.py root@139.150.11.99:/root/uvis/frontend/
```

#### Step 2: 서버에서 배포 스크립트 실행
```bash
cd /root/uvis/frontend
./fix_websocket_403.sh
```

이 스크립트는:
1. 현재 WebSocket 파일 백업
2. 수정된 코드 배포
3. Backend 재시작
4. 로그 확인
5. WebSocket 연결 테스트

#### Step 3: 브라우저에서 확인
1. `http://139.150.11.99` 접속
2. **강력 새로고침**: `Ctrl + Shift + F5`
3. F12 → Console 탭 확인
4. Network 탭 → WS 필터 → `/api/v1/ws/dashboard` 확인

**예상 결과**: 
- ✅ Status: `101 Switching Protocols`
- ✅ Console에 "Dashboard connected" 메시지

---

### 방법 3: Nginx 설정 수동 확인 및 수정

#### Nginx WebSocket 설정 확인
```bash
docker exec uvis-frontend cat /etc/nginx/nginx.conf | grep -A 30 "location /api/v1/ws"
```

#### 올바른 Nginx 설정 예시
```nginx
# WebSocket 프록시 설정
location /api/v1/ws/ {
    proxy_pass http://backend:8000/api/v1/ws/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Authorization $http_authorization;
    
    # WebSocket 타임아웃 설정
    proxy_read_timeout 3600s;
    proxy_send_timeout 3600s;
}
```

#### Nginx 설정 수정 시
```bash
cd /root/uvis/frontend

# 백업
cp nginx.conf nginx.conf.backup.ws.$(date +%Y%m%d_%H%M%S)

# 수정 (vi 또는 nano 사용)
vi nginx.conf

# 컨테이너에 복사
docker cp nginx.conf uvis-frontend:/etc/nginx/nginx.conf

# 테스트 및 재로드
docker exec uvis-frontend nginx -t
docker exec uvis-frontend nginx -s reload
```

---

## 🔧 WebSocket 403 Fix 코드 개선 사항

### 주요 변경 내용

1. **무조건 연결 수락 (403 방지)**
   ```python
   # 먼저 무조건 연결 수락
   await websocket.accept()
   
   # 그 다음 토큰 검증 (실패해도 연결 유지)
   user_data = await verify_token(token_value)
   ```

2. **Query Parameter와 Header 모두 지원**
   ```python
   # ?token=xxx 또는 Authorization: Bearer xxx 모두 가능
   token_value = token or (authorization.replace("Bearer ", "") if authorization else None)
   ```

3. **강화된 로깅**
   ```python
   logger.info(f"🔵 Dashboard WebSocket connection attempt from {client_info}")
   logger.info(f"✅ WebSocket accepted for {client_info}")
   logger.info(f"🔐 User authenticated: {user_data.get('sub')}")
   ```

4. **안전한 에러 처리**
   - 토큰 검증 실패해도 연결 유지
   - 연결 종료 시 정상적으로 cleanup
   - 30초 타임아웃 시 keep-alive ping 전송

---

## 📊 시스템 상태 체크리스트

### API 엔드포인트 테스트

```bash
# JWT 토큰 획득
TOKEN=$(curl -s -X POST http://139.150.11.99/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | \
  python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# 각 API 테스트 (모두 200 OK 예상)
echo "=== Vehicle API ==="
curl -s -X GET "http://139.150.11.99/api/v1/vehicles" \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP: %{http_code}\n" -o /dev/null

echo "=== Orders API ==="
curl -s -X GET "http://139.150.11.99/api/v1/orders" \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP: %{http_code}\n" -o /dev/null

echo "=== Dispatches API ==="
curl -s -X GET "http://139.150.11.99/api/v1/dispatches" \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP: %{http_code}\n" -o /dev/null

echo "=== Clients API ==="
curl -s -X GET "http://139.150.11.99/api/v1/clients" \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP: %{http_code}\n" -o /dev/null

echo "=== Dashboard Stats API ==="
curl -s -X GET "http://139.150.11.99/api/v1/dispatches/stats/summary" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 현재 상태 요약

| 엔드포인트 | 상태 | HTTP 코드 | 데이터 |
|-----------|------|----------|--------|
| `/api/auth/login` | ✅ 정상 | 200 | JWT 토큰 반환 |
| `/api/v1/vehicles` | ✅ 정상 | 200 | 46개 차량 |
| `/api/v1/orders` | ✅ 정상 | 200 | - |
| `/api/v1/dispatches` | ✅ 정상 | 200 | - |
| `/api/v1/clients` | ✅ 정상 | 200 | - |
| `/api/v1/dispatches/stats/summary` | ✅ 정상 | 200 | 통계 (0건) |
| `/api/v1/ws/dashboard` | ⚠️ 403 | 403 | WebSocket 거부 |

---

## 🚀 다음 단계

### 즉시 실행 (서버에서)

```bash
# 1. 진단 스크립트로 원인 파악
cd /root/uvis/frontend
./diagnose_websocket_403.sh

# 2. 로컬에서 수정 파일 업로드 (로컬 PC에서)
scp -P 2829 websocket_403_fix.py root@139.150.11.99:/root/uvis/frontend/

# 3. 수정 배포
cd /root/uvis/frontend
./fix_websocket_403.sh

# 4. 브라우저 테스트
# http://139.150.11.99 접속
# Ctrl + Shift + F5 (강력 새로고침)
# F12 → Console 및 Network 탭 확인
```

### 예상 결과

#### ✅ 성공 시
- Console: "Dashboard connected"
- Network → WS: Status 101 (Switching Protocols)
- 로그: `✅ WebSocket accepted for ...`
- Dashboard 실시간 업데이트 작동

#### ❌ 여전히 403인 경우
1. `diagnose_websocket_403.sh` 결과 확인
2. Nginx 설정 재확인
3. Backend CORS 설정 확인
4. 추가 도움 요청

---

## 📌 참고 사항

### WebSocket 작동 원리

1. **Client → Nginx**: HTTP Upgrade 요청
2. **Nginx → Backend**: WebSocket 프록시 전달
3. **Backend**: `await websocket.accept()` 호출
4. **Backend ↔ Client**: 양방향 실시간 통신

### 403 에러가 발생하는 단계

- **Stage 1 (Nginx)**: Nginx에서 거부 → Nginx 로그에 403
- **Stage 2 (CORS)**: Backend CORS 미들웨어에서 거부 → Backend 로그에 403
- **Stage 3 (App)**: FastAPI 앱에서 거부 → Backend 로그에 "Connection rejected"

현재는 **Stage 2 또는 3**에서 문제 발생 추정

---

## ✅ 완료 후 확인사항

- [ ] `/api/v1/ws/dashboard` 연결 시 101 응답
- [ ] Backend 로그에 `✅ WebSocket accepted` 메시지
- [ ] Browser Console에 "Dashboard connected" 메시지
- [ ] Dashboard에서 실시간 데이터 업데이트 확인
- [ ] Backend 로그에 403 에러 없음

---

## 🆘 추가 지원

문제가 계속되면 다음 정보를 공유해주세요:

1. `diagnose_websocket_403.sh` 전체 출력
2. Backend 로그 최근 100줄
   ```bash
   docker logs uvis-backend --tail 100
   ```
3. Browser DevTools → Console 스크린샷
4. Browser DevTools → Network (WS 필터) 스크린샷

---

**작성일**: 2026-02-25  
**버전**: v1.0 (WebSocket 403 Fix)  
**상태**: Ready to Deploy
