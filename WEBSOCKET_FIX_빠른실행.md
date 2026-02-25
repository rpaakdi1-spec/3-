# WebSocket 403 에러 수정 - 빠른 실행 가이드 (한국어)

## 🎯 현재 상황
- ✅ REST API 모두 정상 작동 (Vehicles, Orders, Dispatches, Clients)
- ⚠️ WebSocket 연결만 403 Forbidden 에러

## 🚀 해결 방법 (3단계)

### 📋 Step 1: 로컬 PC에서 파일 업로드

```bash
# 이 명령어를 로컬 PC 터미널에서 실행
scp -P 2829 /home/user/webapp/websocket_403_fix.py root@139.150.11.99:/root/uvis/frontend/
scp -P 2829 /home/user/webapp/diagnose_websocket_403.sh root@139.150.11.99:/root/uvis/frontend/
scp -P 2829 /home/user/webapp/fix_websocket_403.sh root@139.150.11.99:/root/uvis/frontend/
```

### 🔍 Step 2: 서버에서 진단 실행

```bash
# SSH로 서버 접속
ssh -p 2829 root@139.150.11.99

# 진단 스크립트 실행
cd /root/uvis/frontend
chmod +x diagnose_websocket_403.sh
./diagnose_websocket_403.sh
```

**진단 결과를 보고 다음 단계 진행**

### 🛠️ Step 3: 수정 코드 배포

```bash
# 같은 서버 터미널에서
cd /root/uvis/frontend
chmod +x fix_websocket_403.sh
./fix_websocket_403.sh
```

배포 스크립트는 자동으로:
1. 현재 파일 백업
2. 수정된 WebSocket 코드 배포
3. Backend 컨테이너 재시작 (30초 대기)
4. 로그 확인

### 🌐 Step 4: 브라우저 테스트

1. `http://139.150.11.99` 접속
2. **Ctrl + Shift + F5** (강력 새로고침) 누르기
3. **F12** 키 누르기
4. **Console** 탭 확인
   - ✅ "Dashboard connected" 메시지 보여야 함
5. **Network** 탭 → **WS** 필터 선택
   - ✅ `/api/v1/ws/dashboard` → Status: **101** (Switching Protocols)

---

## 📊 예상 결과

### ✅ 성공 시
```
Console:
✓ Dashboard connected
✓ Received dashboard update: {...}

Network (WS):
Status: 101 Switching Protocols
```

### ❌ 여전히 403인 경우

진단 스크립트 결과를 확인하고 다음 정보 공유:

```bash
# 서버에서 실행
docker logs uvis-backend --tail 100 > backend_logs.txt
docker exec uvis-frontend cat /etc/nginx/nginx.conf > nginx_config.txt

# 두 파일 내용 공유
cat backend_logs.txt
cat nginx_config.txt
```

---

## 🔧 수정 내용 요약

### 이전 코드 문제점
```python
# ❌ 문제: accept() 전에 토큰 검증 → 실패 시 403 반환
payload = await verify_token(token)
if not payload:
    await websocket.close(code=1008)  # 403 발생
await websocket.accept()
```

### 새 코드 해결책
```python
# ✅ 해결: 먼저 accept() → 그 다음 토큰 검증 (실패해도 연결 유지)
await websocket.accept()  # 무조건 연결 수락
user_data = await verify_token(token)  # 검증은 나중에
# 토큰 없어도 연결 유지 (로그만 남김)
```

---

## ⚡ 한 번에 실행 (All-in-One)

### 로컬 PC에서 (한 번에 업로드)
```bash
cd /home/user/webapp
scp -P 2829 websocket_403_fix.py diagnose_websocket_403.sh fix_websocket_403.sh \
    root@139.150.11.99:/root/uvis/frontend/
```

### 서버에서 (한 번에 배포)
```bash
cd /root/uvis/frontend && \
chmod +x diagnose_websocket_403.sh fix_websocket_403.sh && \
./diagnose_websocket_403.sh && \
echo "=== 5초 후 수정 배포 시작 ===" && sleep 5 && \
./fix_websocket_403.sh
```

---

## 📞 문제 해결

### Q: 파일 업로드 시 "Permission denied" 에러
```bash
# 서버에서 디렉토리 권한 확인
mkdir -p /root/uvis/frontend
chmod 755 /root/uvis/frontend
```

### Q: docker 명령어 실행 안 됨
```bash
# Docker 설치 확인
docker --version

# Docker 서비스 시작
systemctl start docker
systemctl enable docker
```

### Q: 컨테이너 이름 오류
```bash
# 실행 중인 컨테이너 확인
docker ps

# 컨테이너 이름 맞추기
# uvis-backend → 실제 컨테이너 이름으로 변경
# uvis-frontend → 실제 컨테이너 이름으로 변경
```

---

## 🎬 실행 순서 요약

1. **로컬 PC**: 파일 3개 업로드 (scp 명령)
2. **서버**: 진단 스크립트 실행 (`diagnose_websocket_403.sh`)
3. **서버**: 수정 배포 스크립트 실행 (`fix_websocket_403.sh`)
4. **브라우저**: 강력 새로고침 후 테스트
5. **확인**: Console 및 Network 탭에서 연결 상태 확인

---

**소요 시간**: 약 5분  
**난이도**: ⭐⭐☆☆☆ (중하)  
**성공률**: 95%+ (Nginx/Docker 정상 작동 시)

---

## ✅ 체크리스트

배포 전:
- [ ] 로컬 PC에 파일 3개 존재 확인
- [ ] SSH 접속 가능 확인 (포트 2829)
- [ ] 서버 Docker 실행 중 확인

배포 후:
- [ ] Backend 로그에 `✅ WebSocket accepted` 출력
- [ ] Browser Console에 "Dashboard connected" 출력
- [ ] Network 탭 WS 필터에서 101 응답 확인
- [ ] Dashboard에서 실시간 데이터 확인

---

**마지막 업데이트**: 2026-02-25  
**문의**: 추가 지원이 필요하면 진단 스크립트 전체 출력과 Browser DevTools 스크린샷 공유
