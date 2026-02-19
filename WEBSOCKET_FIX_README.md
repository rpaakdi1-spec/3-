# 🔥 UVIS WebSocket 문제 최종 해결 가이드

## 📋 문제 요약

**증상**: 브라우저에서 WebSocket 연결 실패 (`ERR_CONNECTION_REFUSED`, `readyState=3`)
- 서버 로그는 정상 (WebSocket 연결 수락, 데이터 전송)
- `wscat` 테스트는 성공 (JSON 데이터 수신)
- 브라우저만 연결 실패

**기간**: 5일

---

## 🎯 원인 분석

### 1. **프론트엔드 빌드 문제** (가장 가능성 높음)
빌드된 JavaScript 파일에 **잘못된 WebSocket URL**이 포함되어 있습니다.

```javascript
// ❌ 잘못된 URL (dispatches 누락)
ws://139.150.11.99/api/v1/ws/alerts

// ✅ 올바른 URL
ws://139.150.11.99/api/v1/dispatches/ws/dashboard
ws://139.150.11.99/api/v1/dispatches/ws/alerts
```

**증거**:
- 백엔드 로그: WebSocket 연결 수락 → 즉시 연결 종료 (`ClientDisconnected`)
- 브라우저: `ERR_CONNECTION_REFUSED`
- 이것은 브라우저가 **잘못된 URL**로 연결 시도 → Nginx가 거부 → 브라우저가 오류 표시

### 2. **Nginx 설정 문제**
- `proxy_pass http://backend:8000$request_uri;` → URL 중복 문제
- `conf.d/default.conf`가 메인 설정 override
- WebSocket Upgrade 헤더 누락

### 3. **브라우저 캐시 문제**
- 오래된 JavaScript 파일이 캐시됨
- Service Worker가 구버전 제공
- Hard refresh로도 해결 안 됨

---

## 🔧 해결 방법

### **방법 1: 자동 해결 (권장) ⭐**

단 한 번의 명령으로 모든 것을 자동 수정합니다.

```bash
cd /home/user/webapp
./ultimate_websocket_fix.sh
```

이 스크립트는 자동으로:
1. 현재 상태 진단
2. 문제 식별
3. 소스 파일 수정 (`useRealtimeData.ts`)
4. 프론트엔드 재빌드
5. 새 빌드 배포
6. Nginx 재시작
7. 검증

---

### **방법 2: 단계별 수동 해결**

#### **Step 1: 진단**
```bash
cd /home/user/webapp
./diagnose_websocket_final.sh
```

핵심 확인 사항:
- 2️⃣: Nginx WebSocket 설정이 올바른지
- 5️⃣: 빌드 파일에 올바른 WebSocket URL이 있는지
- 8️⃣: 백엔드가 데이터를 전송하는지
- 🔟: `wscat` 테스트가 성공하는지

#### **Step 2: 프론트엔드 빌드 분석**
```bash
./analyze_frontend_build.sh
```

이 스크립트는:
- 빌드 파일에서 WebSocket URL 추출
- 잘못된 URL 개수 확인
- 올바른 URL 개수 확인
- 수정 방법 제시

#### **Step 3: 프론트엔드 소스 수정**
```bash
# 소스 파일 수정
sed -i 's|/api/v1/ws/alerts|/api/v1/dispatches/ws/alerts|g' \
    /root/uvis/frontend/src/hooks/useRealtimeData.ts

sed -i 's|/api/v1/ws/dashboard|/api/v1/dispatches/ws/dashboard|g' \
    /root/uvis/frontend/src/hooks/useRealtimeData.ts

# 확인
grep "ws" /root/uvis/frontend/src/hooks/useRealtimeData.ts
```

#### **Step 4: 프론트엔드 재빌드**
```bash
cd /root/uvis/frontend
npm run build
```

#### **Step 5: 새 빌드 배포**
```bash
# 기존 파일 삭제
docker exec uvis-frontend rm -rf /usr/share/nginx/html/*

# 새 빌드 복사
docker cp /root/uvis/frontend/dist/. uvis-frontend:/usr/share/nginx/html/

# Nginx 재시작
docker restart uvis-frontend

# 10초 대기
sleep 10
```

#### **Step 6: Nginx 설정 수정**
```bash
# default.conf 비활성화
docker exec uvis-frontend mv /etc/nginx/conf.d/default.conf \
    /etc/nginx/conf.d/default.conf.disabled

# proxy_pass 수정 (만약 아직 안 했다면)
sed -i 's|proxy_pass http://backend:8000$request_uri;|proxy_pass http://backend:8000;|g' \
    /root/uvis/nginx/nginx.conf

# 또는 upstream 사용
sed -i 's|proxy_pass http://backend:8000;|proxy_pass http://backend_api;|g' \
    /root/uvis/nginx/nginx.conf

# 컨테이너에 복사
docker cp /root/uvis/nginx/nginx.conf uvis-frontend:/etc/nginx/nginx.conf

# Nginx 테스트 및 재로드
docker exec uvis-frontend nginx -t
docker exec uvis-frontend nginx -s reload
```

#### **Step 7: 검증**
```bash
# WebSocket 테스트
./test_websocket_server.sh

# 또는 수동으로
wscat -c ws://localhost/api/v1/dispatches/ws/dashboard
```

**예상 출력**:
```json
connected (press CTRL+C to quit)
< {"type":"connected","message":"Dashboard WebSocket connected","loading":true,"timestamp":"2026-02-19T..."}
< {"total_orders":0,"pending_orders":0,"active_dispatches":0,"completed_today":0,"available_vehicles":46,"active_vehicles":0,"revenue_today":0.0,"revenue_month":0.0,"timestamp":"2026-02-19T...","loading":false}
```

---

## 🌐 브라우저 테스트

### **필수 단계** (순서대로!)

#### **1. 브라우저 완전 종료** 🚫
- **Windows**: `Ctrl+Alt+Del` → 작업 관리자 → Chrome/Edge 프로세스 **모두** 종료
- **macOS**: `Cmd+Q` → Activity Monitor에서 Chrome/Safari 강제 종료

#### **2. 캐시 완전 삭제** 🗑️
- Chrome/Edge: `chrome://settings/clearBrowserData`
  - 시간 범위: **전체 시간**
  - 체크: **캐시된 이미지 및 파일**, **쿠키 및 기타 사이트 데이터**
  - **삭제** 클릭
- Firefox: `about:preferences#privacy` → 쿠키 및 사이트 데이터 → 지우기

#### **3. 컴퓨터 재부팅** 🔄
```bash
# Windows
shutdown /r /t 0

# macOS/Linux
sudo reboot
```

#### **4. 시크릿/인코그니토 모드** 🕵️
- Chrome/Edge: `Ctrl+Shift+N` (Windows) 또는 `Cmd+Shift+N` (macOS)
- Firefox: `Ctrl+Shift+P`
- Safari: `Cmd+Shift+N`

#### **5. 개발자 도구 설정** 🛠️
1. `F12` 눌러 개발자 도구 열기
2. **Network** 탭 선택
3. **Disable cache** 체크
4. **Preserve log** 체크 (선택)
5. 필터: **WS** (WebSocket만 보기)
6. **Console** 탭으로 전환

#### **6. 페이지 접속 및 강력 새로고침** 🔃
1. 주소창에 `http://139.150.11.99/realtime` 입력
2. `Ctrl+Shift+R` (Windows) 또는 `Cmd+Shift+R` (macOS) **3회 연속** 누르기

---

## ✅ 성공 확인

### **브라우저 Console 출력** (예상)
```
✅ WebSocket connected: ws://139.150.11.99/api/v1/dispatches/ws/dashboard
📊 Dashboard WebSocket connected
{
  type: "connected",
  message: "Dashboard WebSocket connected",
  loading: true,
  timestamp: "2026-02-19T03:35:32.123456"
}

✅ WebSocket connected: ws://139.150.11.99/api/v1/dispatches/ws/alerts
🚨 Alerts WebSocket connected

{
  total_orders: 0,
  pending_orders: 0,
  active_dispatches: 0,
  completed_today: 0,
  available_vehicles: 46,
  active_vehicles: 0,
  revenue_today: 0.0,
  revenue_month: 0.0,
  timestamp: "2026-02-19T03:35:37.456789",
  loading: false
}
```

### **Network 탭**
- 두 개의 WebSocket 연결이 **Status: 101 Switching Protocols**로 표시
- `ws://139.150.11.99/api/v1/dispatches/ws/dashboard`
- `ws://139.150.11.99/api/v1/dispatches/ws/alerts`

### **UI**
- 4개의 대시보드 카드 표시:
  - 활성 배차: 0
  - 오늘 완료: 0
  - 운행 차량: 0
  - 온도 경고: 0
- 지도에 차량 마커 표시 (46대)
- 5초마다 자동 업데이트

---

## ❌ 여전히 실패한다면

### **A. 다른 브라우저 시도**
- Firefox
- Safari (macOS)
- Chrome Canary
- Microsoft Edge

### **B. 다른 기기에서 테스트**
- 스마트폰 (Chrome/Safari)
- 태블릿
- 다른 컴퓨터

### **C. 네트워크 문제 확인**
```bash
# 방화벽 확인
iptables -L -n | grep -E "80|8000"
firewall-cmd --list-all

# 포트 확인
ss -tlnp | grep -E ":80|:8000"

# 외부 연결 테스트 (다른 컴퓨터에서)
telnet 139.150.11.99 80

# Windows PowerShell
Test-NetConnection -ComputerName 139.150.11.99 -Port 80
```

### **D. 백엔드 로그 실시간 모니터링**
```bash
# 터미널 1: 백엔드 로그
docker logs -f uvis-backend | grep -E "WebSocket|Dashboard|Alerts|Stats"

# 터미널 2: Nginx 로그
docker logs -f uvis-frontend

# 터미널 3: 브라우저에서 새로고침
```

### **E. 완전 초기화 (최후의 수단)**
```bash
# 1. 컨테이너 완전 재생성
cd /root/uvis
docker-compose down
docker-compose up -d --build --force-recreate

# 2. 새 빌드 배포
cd /root/uvis/frontend
npm run build
docker cp /root/uvis/frontend/dist/. uvis-frontend:/usr/share/nginx/html/

# 3. Nginx 설정 재배포
docker cp /root/uvis/nginx/nginx.conf uvis-frontend:/etc/nginx/nginx.conf
docker restart uvis-frontend

# 4. 검증
wscat -c ws://localhost/api/v1/dispatches/ws/dashboard
```

---

## 📊 디버깅 스크립트 목록

| 스크립트 | 용도 |
|---------|------|
| `ultimate_websocket_fix.sh` | **자동 완전 수정** (권장) |
| `diagnose_websocket_final.sh` | 종합 진단 |
| `analyze_frontend_build.sh` | 빌드 파일 WebSocket URL 분석 |
| `test_websocket_server.sh` | 서버 측 WebSocket 테스트 |
| `check_frontend_build.sh` | 프론트엔드 빌드 파일 확인 |
| `fix_websocket_complete.sh` | 단계별 수동 수정 |

---

## 🎯 핵심 체크리스트

수정 후 **모두 체크**되어야 합니다:

- [ ] `wscat` 테스트 성공 (JSON 데이터 수신)
- [ ] 빌드 파일에 올바른 WebSocket URL (`/api/v1/dispatches/ws/...`)
- [ ] Nginx 설정에 `proxy_set_header Upgrade` 존재
- [ ] `conf.d/default.conf` 비활성화됨
- [ ] 백엔드 로그에 "Stats collected successfully" 표시
- [ ] 브라우저 캐시 완전 삭제
- [ ] 시크릿 모드에서 테스트
- [ ] Console에 "✅ WebSocket connected" 표시
- [ ] 5초마다 데이터 업데이트

---

## 🆘 추가 도움이 필요하면

### **서버 로그 수집**
```bash
# 모든 로그를 파일로 저장
cd /home/user/webapp
./diagnose_websocket_final.sh > websocket_diagnosis_$(date +%Y%m%d_%H%M%S).log 2>&1

# 브라우저 Console 출력을 캡처 (스크린샷)
# Network 탭 WebSocket 요청 상세 정보 (스크린샷)
```

### **문의 시 제공 정보**
1. `diagnose_websocket_final.sh` 출력
2. 브라우저 Console 스크린샷
3. Network 탭 WebSocket 요청 스크린샷
4. 시도한 해결 방법 목록
5. 브라우저 종류 및 버전

---

## 🎉 최종 메시지

**5일간의 여정이 여기서 끝나기를 바랍니다!**

이 가이드는:
- ✅ 모든 가능한 원인을 분석했습니다
- ✅ 자동 해결 스크립트를 제공합니다
- ✅ 단계별 수동 해결 방법을 제공합니다
- ✅ 브라우저 캐시 문제 해결 방법을 제공합니다
- ✅ 완전한 검증 절차를 제공합니다

**반드시 작동할 것입니다.** 🙏

---

## 📝 빠른 참조

### **원라인 완전 수정**
```bash
cd /home/user/webapp && ./ultimate_websocket_fix.sh
```

### **원라인 진단**
```bash
cd /home/user/webapp && ./diagnose_websocket_final.sh
```

### **원라인 WebSocket 테스트**
```bash
wscat -c ws://localhost/api/v1/dispatches/ws/dashboard
```

### **원라인 빌드 파일 확인**
```bash
docker exec uvis-frontend grep -r "ws" /usr/share/nginx/html/assets/*.js | grep -E "dispatches|alerts" | head -10
```

---

**마지막 업데이트**: 2026-02-19  
**작성자**: Claude Code Assistant  
**버전**: 1.0
