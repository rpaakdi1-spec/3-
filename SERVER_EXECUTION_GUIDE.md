# 🎯 서버 Frontend 수정 완료 - 실행 가이드

**날짜**: 2026-02-08 15:40 KST  
**상태**: ✅ 코드 수정 완료, GitHub 푸시 완료  
**다음 단계**: 서버에서 실행 필요  

---

## 📦 GitHub에 푸시된 변경사항

### 커밋 로그
```
26efceb feat: Add automated frontend rebuild script for server
4a4610b fix(phase10): Fix frontend build errors - downgrade MUI lab to v5, add legacy-peer-deps flag
ef9adbf feat: Add service fix script for post-recovery
```

### 수정된 파일
1. **frontend/package.json**
   - `@mui/lab`: `7.0.1-beta.21` → `5.0.0-alpha.170`

2. **frontend/Dockerfile**
   - `RUN npm install` → `RUN npm install --legacy-peer-deps`
   - `COPY nginx.conf /etc/nginx/nginx.conf` → `/etc/nginx/conf.d/default.conf`

3. **SERVER_FRONTEND_FIX_GUIDE.md** (새 파일)
   - 상세한 문제 해결 가이드

4. **SERVER_COMMANDS.sh** (새 파일)
   - 자동화된 재빌드 스크립트

---

## 🚀 서버에서 실행할 명령어

서버 `/root/uvis`에 SSH 접속 후 **다음 중 하나** 실행:

### 방법 1: 자동화 스크립트 사용 (권장) ⭐

```bash
cd /root/uvis

# 최신 스크립트 다운로드
curl -O https://raw.githubusercontent.com/rpaakdi1-spec/3-/main/SERVER_COMMANDS.sh
chmod +x SERVER_COMMANDS.sh

# 실행
./SERVER_COMMANDS.sh
```

**예상 소요 시간**: 3-5분

### 방법 2: 수동 명령어 실행

```bash
cd /root/uvis

# 1. 충돌 파일 제거
rm -f fix_services.sh server_recovery_check.sh
cd frontend
rm -f fix_services.sh server_recovery_check.sh

# 2. 최신 코드 가져오기
git pull origin main

# 3. 컨테이너 중지 및 제거
cd /root/uvis
docker-compose stop frontend nginx
docker-compose rm -f frontend nginx

# 4. 재빌드
docker-compose build --no-cache frontend

# 5. 시작
docker-compose up -d frontend nginx

# 6. 30초 대기
sleep 30

# 7. 상태 확인
docker-compose ps
ls -lh frontend/dist/index.html
docker-compose logs frontend --tail=20
```

---

## ✅ 성공 확인 체크리스트

### 1. 컨테이너 상태 확인
```bash
docker-compose ps
```

**예상 출력:**
```
uvis-frontend  Up XX seconds (healthy)  0.0.0.0:80->80/tcp
uvis-nginx     Up XX seconds            0.0.0.0:443->443/tcp
```

### 2. 빌드 날짜 확인
```bash
ls -lh frontend/dist/index.html
```

**예상 출력:**
```
-rw-r--r-- 1 root root 478 Feb  8 15:XX frontend/dist/index.html
```
→ **현재 시간**이어야 함!

### 3. Frontend 접속 테스트
```bash
curl -I http://localhost/
```

**예상 출력:**
```
HTTP/1.1 200 OK
```

### 4. API 테스트
```bash
curl http://localhost:8000/api/v1/dispatch-rules/ | jq .
```

**예상 출력:**
```json
[
  {
    "id": 1,
    "name": "Priority Drivers",
    ...
  },
  {
    "id": 2,
    "name": "Nearby Drivers Priority",
    ...
  }
]
```

### 5. 브라우저 테스트
1. **강력 새로고침**: `Ctrl + Shift + R` (Chrome/Firefox)
2. **메인 페이지**: http://139.150.11.99/
3. **로그인** 후 좌측 사이드바에서 **"스마트 배차 규칙"** 메뉴 확인
4. **Rule Builder**: http://139.150.11.99/dispatch-rules

---

## 🎨 예상 화면

### 좌측 사이드바
```
📊 대시보드
🚚 배차 관리
📦 주문 관리
👤 드라이버 관리
...
⚙️ 스마트 배차 규칙  ← 이 메뉴가 보여야 함!
```

### Rule Builder 페이지
```
┌─────────────────────────────────────────┐
│ 스마트 배차 규칙                        │
│ [+ 새 규칙 만들기]                      │
├─────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ │
│ │ Priority Drivers            [ACTIVE]│ │
│ │ Assign to high-rated drivers        │ │
│ │ Priority: 100 | Assignment          │ │
│ │ [Test] [Logs] [Performance]         │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Nearby Drivers Priority     [ACTIVE]│ │
│ │ Prioritize drivers within 5km       │ │
│ │ Priority: 90 | Assignment           │ │
│ │ [Test] [Logs] [Performance]         │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

## ❌ 문제 해결

### 빌드가 여전히 실패하는 경우

```bash
cd /root/uvis

# Docker 빌드 캐시 완전 삭제
docker builder prune -af

# Frontend 이미지 삭제
docker rmi uvis-frontend

# 다시 시도
docker-compose build --no-cache frontend
docker-compose up -d frontend nginx
```

### "user directive is not allowed" 에러

```bash
# Nginx 설정 확인
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf | head -10

# user 지시문이 보이면 제거
docker-compose exec frontend sed -i '1d' /etc/nginx/conf.d/default.conf
docker-compose restart frontend
```

### 페이지가 로드되지 않는 경우

```bash
# Frontend 컨테이너 내부 파일 확인
docker-compose exec frontend ls -la /usr/share/nginx/html/

# index.html이 있어야 함
# 없으면 빌드가 제대로 되지 않은 것
```

---

## 📞 긴급 지원

### 문제가 계속되면

1. **빌드 로그 저장**:
   ```bash
   docker-compose build frontend 2>&1 | tee build.log
   ```

2. **로그 확인**:
   ```bash
   cat build.log | grep -i error
   ```

3. **전체 로그 공유**

---

## 🔗 관련 문서

- **SERVER_FRONTEND_FIX_GUIDE.md**: 상세한 문제 해결 가이드
- **SERVER_COMMANDS.sh**: 자동화 스크립트
- **PHASE10_FRONTEND_INTEGRATION_COMPLETE.md**: Phase 10 통합 문서
- **GABIA_SERVER_RECOVERY_GUIDE.md**: 서버 복구 가이드

---

## 📊 현재 상황 요약

| 항목 | 상태 | 설명 |
|------|------|------|
| GitHub 코드 | ✅ 완료 | 최신 코드 푸시됨 (커밋 26efceb) |
| package.json | ✅ 수정 | MUI Lab v5로 다운그레이드 |
| Dockerfile | ✅ 수정 | --legacy-peer-deps 추가 |
| 문서 | ✅ 작성 | 가이드 3개 생성 |
| 자동화 스크립트 | ✅ 작성 | SERVER_COMMANDS.sh 생성 |
| 서버 실행 | ⏳ 대기 | 위 명령어 실행 필요 |

---

## 🎯 다음 단계

1. **서버 SSH 접속**: `ssh root@139.150.11.99`
2. **자동화 스크립트 실행**:
   ```bash
   cd /root/uvis
   curl -O https://raw.githubusercontent.com/rpaakdi1-spec/3-/main/SERVER_COMMANDS.sh
   chmod +x SERVER_COMMANDS.sh
   ./SERVER_COMMANDS.sh
   ```
3. **브라우저 테스트**: http://139.150.11.99/dispatch-rules
4. **결과 공유**: 스크린샷 또는 에러 메시지

---

**작성**: AI Assistant (Claude Code Agent)  
**GitHub**: https://github.com/rpaakdi1-spec/3-  
**최신 커밋**: 26efceb  
**날짜**: 2026-02-08 15:40 KST
