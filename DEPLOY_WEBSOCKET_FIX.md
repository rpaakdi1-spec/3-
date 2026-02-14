# WebSocket 타이밍 문제 최종 수정 배포 가이드

## 문제 원인
WebSocket 연결 후 **첫 데이터 전송 전에 5초 대기**하여 클라이언트가 타임아웃으로 연결을 끊음.

## 해결 방법
**즉시 첫 데이터를 전송**한 후, 루프 끝에서 5초 대기하도록 변경.

---

## 🚀 배포 절차

### 1️⃣ 서버에서 최신 코드 Pull
```bash
cd /root/uvis && git pull origin main
```
**예상 출력**: `aa956f5..` commit이 포함된 업데이트

---

### 2️⃣ 업데이트된 파일 컨테이너에 복사
```bash
docker cp backend/app/api/dispatches.py uvis-backend:/app/app/api/dispatches.py
```
**예상 출력**: `Successfully copied ...kB to uvis-backend`

---

### 3️⃣ Python 캐시 삭제 (중요!)
```bash
docker exec uvis-backend find /app -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
docker exec uvis-backend find /app -name "*.pyc" -delete
```

---

### 4️⃣ 백엔드 완전 재시작
```bash
docker stop uvis-backend
sleep 5
docker start uvis-backend
sleep 30
```

---

### 5️⃣ 시작 확인
```bash
docker logs uvis-backend --tail=20 | grep -i "application startup complete"
```
**예상 출력**: 
```
INFO:     Application startup complete.
2026-02-14 XX:XX:XX | INFO     | main:lifespan | Application startup complete!
```

---

## ✅ 검증 절차

### A. 서버 로그 검증

#### ① 에러 확인 (빈 화면이 정상)
```bash
docker logs uvis-backend --since 2m | grep -i "failed to send stats\|error collecting stats"
```
**예상 출력**: *빈 화면 (에러 없음)*

#### ② WebSocket 연결 로그 확인
```bash
timeout 60 docker logs -f uvis-backend 2>&1 | grep -i "websocket.*dashboard\|sent dashboard"
```
**예상 출력** (브라우저에서 /realtime 접속 후):
```
INFO:     ('192.168.112.5', XXXXX) - "WebSocket /api/v1/dispatches/ws/dashboard" [accepted]
2026-02-14 XX:XX:XX | INFO     | app.api.dispatches:websocket_dashboard | WebSocket connected: dashboard
2026-02-14 XX:XX:XX | DEBUG    | app.api.dispatches:websocket_dashboard | Sent dashboard stats: pending=17, active=0
2026-02-14 XX:XX:XX | DEBUG    | app.api.dispatches:websocket_dashboard | Sent dashboard stats: pending=17, active=0
(5초마다 반복...)
```

⚠️ **중요**: `connection closed` 로그가 **나오면 안 됩니다**!

---

### B. 브라우저 검증

#### ① 캐시 완전 삭제
- **Chrome/Edge**: `Ctrl + Shift + Delete`
  - 기간: **전체 기간**
  - 항목: **쿠키 및 기타 사이트 데이터**, **캐시된 이미지 및 파일** 모두 선택
  - 삭제 후 브라우저 **완전 종료** 및 재시작

#### ② 시크릿/프라이빗 모드로 테스트
```
http://139.150.11.99/realtime
```

#### ③ 개발자 도구 (F12) 확인

**Console 탭 예상 출력**:
```
✅ WebSocket connected: ws://139.150.11.99/api/v1/dispatches/ws/dashboard
✅ WebSocket connected: ws://139.150.11.99/api/v1/ws/alerts
📊 Dashboard stats updated: {total_orders: 423, pending_orders: 17, ...}
(5초마다 반복...)
```

**Network 탭 → WS (WebSocket) 하위**:
- `dashboard` 연결: **Status 101 Switching Protocols** (지속 유지)
- `alerts` 연결: **Status 101 Switching Protocols** (지속 유지)
- Messages: 5초마다 JSON 데이터 수신 확인

---

## 🎯 성공 체크리스트

### 서버 측
- [ ] git pull 성공 (`aa956f5` commit 포함)
- [ ] 파일 복사 완료
- [ ] Python 캐시 삭제
- [ ] 컨테이너 재시작 완료
- [ ] "Application startup complete" 로그 확인
- [ ] **에러 로그 없음** (Failed to send stats 없음)
- [ ] "Sent dashboard stats" 로그가 **5초마다 출력**
- [ ] "connection closed" 로그가 **즉시 나오지 않음**

### 클라이언트 측
- [ ] 브라우저 캐시 완전 삭제
- [ ] 시크릿 모드 사용
- [ ] Console에 "WebSocket connected" 메시지
- [ ] Console에 에러 메시지 **없음**
- [ ] Network → WS 탭에서 **Status 101** 유지
- [ ] 5초마다 JSON 메시지 수신
- [ ] **재연결 시도 없음** (reconnecting 메시지 없음)
- [ ] 대시보드 카드 숫자가 **5초마다 자동 갱신**

---

## 🔧 변경 사항 요약

### `backend/app/api/dispatches.py`의 `/ws/dashboard` 엔드포인트

**변경 전** (문제 코드):
```python
# 연결 직후 확인 메시지 전송
await websocket.send_json({"type": "connected", ...})

while True:
    await asyncio.sleep(5)  # ❌ 5초 대기 후 데이터 전송
    # ... 데이터 수집 및 전송
```

**변경 후** (수정 코드):
```python
while True:
    # 연결 상태 체크
    if websocket.client_state.name != "CONNECTED":
        break
    
    # 데이터 수집
    db = SessionLocal()
    try:
        # ... 통계 수집
        await websocket.send_json(stats)  # ✅ 즉시 전송
    finally:
        db.close()
    
    await asyncio.sleep(5)  # ✅ 전송 후 대기
```

---

## 📝 코드 변경 상세

### 주요 개선 사항
1. **불필요한 확인 메시지 제거**: 바로 실제 데이터 전송
2. **타이밍 수정**: 데이터 전송 **후** 5초 대기 (전: 대기 **후** 전송)
3. **연결 상태 체크 강화**: `CONNECTED` 상태 확인
4. **에러 처리 개선**: 전송 실패 시 즉시 루프 종료
5. **로깅 개선**: 에러 타입 명시적 출력

---

## 🐛 트러블슈팅

### 여전히 "Failed to send stats" 에러 발생 시

1. **컨테이너 내부 코드 확인**:
```bash
docker exec uvis-backend grep -A 5 "await asyncio.sleep(5)" /app/app/api/dispatches.py | tail -10
```
**예상 출력**: `asyncio.sleep(5)`가 `db.close()` **이후**에 있어야 함

2. **Python 프로세스 완전 재시작**:
```bash
docker exec uvis-backend pkill -9 python
docker restart uvis-backend
```

3. **Uvicorn 로그 레벨 확인**:
```bash
docker logs uvis-backend --tail=100 | grep -i "uvicorn\|startup"
```

---

### 브라우저에서 여전히 재연결 반복 시

1. **브라우저 프로세스 완전 종료**:
   - 작업 관리자에서 Chrome/Edge 프로세스 **모두** 종료
   - 브라우저 재시작

2. **프론트엔드 재빌드**:
```bash
cd /root/uvis/frontend
rm -rf dist/ node_modules/.vite
npm run build
docker exec uvis-frontend rm -rf /usr/share/nginx/html/*
docker cp dist/. uvis-frontend:/usr/share/nginx/html/
docker restart uvis-frontend
```

3. **Network 탭에서 WebSocket URL 확인**:
   - 올바른 URL: `ws://139.150.11.99/api/v1/dispatches/ws/dashboard`
   - 잘못된 URL (이중 prefix): `ws://139.150.11.99/api/v1/ws/ws/dashboard`

---

## 📊 관련 Commit

- **aa956f5**: `fix: WebSocket 타이밍 문제 해결 - 즉시 데이터 전송 후 대기`
- **9e9f67c**: `fix: WebSocket 연결 직후 즉시 확인 메시지 전송`
- **71dc72a**: `fix: WebSocket 즉시 연결 끊김 문제 해결`

---

## 🎉 배포 완료 후 기대 결과

✅ **서버 로그**: "Sent dashboard stats" 메시지가 5초마다 정상 출력  
✅ **브라우저 Console**: WebSocket 연결 안정적 유지, 재연결 없음  
✅ **대시보드 UI**: 실시간 통계가 5초마다 자동 갱신  
✅ **에러 로그**: "Failed to send", "ClientDisconnected" 에러 **완전 제거**  

---

**작성일**: 2026-02-14  
**Commit**: aa956f5  
**Repository**: https://github.com/rpaakdi1-spec/3-
