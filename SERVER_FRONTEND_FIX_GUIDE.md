# 🚀 서버 Frontend 빌드 오류 해결 가이드

**날짜**: 2026-02-08  
**문제**: npm 의존성 충돌 + Phase 10 최신 코드 미반영  
**원인**: `@mui/lab@7.0.1-beta.21`과 `@mui/material@5.18.0` 버전 불일치  

---

## 📋 현재 상황

- ❌ **npm 빌드 실패**: MUI 버전 충돌
- ❌ **최신 코드 미반영**: frontend/dist 빌드 날짜가 2월 8일 07:23로 오래됨
- ⚠️ **Phase 10 Rule Builder**: 최신 코드가 반영되지 않아 브라우저에서 보이지 않음

---

## 🔧 해결 방법 1: package.json 수정 + 재빌드 (권장)

서버 `/root/uvis`에서 **순서대로** 실행:

### Step 1: 충돌 파일 제거 및 최신 코드 가져오기

```bash
cd /root/uvis

# 충돌 파일 제거
rm -f fix_services.sh server_recovery_check.sh
cd frontend
rm -f fix_services.sh server_recovery_check.sh

# 최신 코드 가져오기
git pull origin main
```

### Step 2: package.json 수정 (MUI Lab 버전 다운그레이드)

```bash
cd /root/uvis/frontend

# @mui/lab 버전을 5.x로 다운그레이드
sed -i 's/"@mui\/lab": "^7.0.1-beta.21"/"@mui\/lab": "^5.0.0-alpha.170"/' package.json

# 확인
cat package.json | grep "@mui/lab"
```

**예상 출력:**
```
"@mui/lab": "^5.0.0-alpha.170",
```

### Step 3: Dockerfile 수정 (--legacy-peer-deps 추가)

```bash
cd /root/uvis/frontend

# Dockerfile 백업
cp Dockerfile Dockerfile.backup_$(date +%Y%m%d_%H%M%S)

# Dockerfile 수정
cat > Dockerfile << 'EOF'
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# 의존성 설치 (--legacy-peer-deps 추가)
COPY package*.json ./
RUN npm install --legacy-peer-deps

# 소스 복사 및 빌드
COPY . .
# Build for production using .env.production
ENV NODE_ENV=production
RUN npm run build

# Production stage
FROM nginx:alpine

LABEL maintainer="UVIS Team"
LABEL description="UVIS Logistics Frontend"

# 빌드 결과물 복사
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx 설정 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 포트 노출
EXPOSE 80

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]
EOF

# 확인
cat Dockerfile | grep "npm install"
```

**예상 출력:**
```
RUN npm install --legacy-peer-deps
```

### Step 4: Frontend 완전 재빌드

```bash
cd /root/uvis

# 기존 컨테이너 중지 및 제거
docker-compose stop frontend nginx
docker-compose rm -f frontend nginx

# 캐시 없이 완전 재빌드
docker-compose build --no-cache frontend

# 컨테이너 시작
docker-compose up -d frontend nginx

# 30초 대기
sleep 30
```

### Step 5: 상태 확인

```bash
# 컨테이너 상태
docker-compose ps

# 빌드 날짜 확인 (현재 시간이어야 함)
ls -lh frontend/dist/index.html

# Frontend 로그 확인
docker-compose logs frontend --tail=50

# 접속 테스트
curl -I http://localhost/
curl http://localhost:8000/api/v1/dispatch-rules/ | jq .
```

**예상 결과:**
```
uvis-frontend  Up XX seconds (healthy)  0.0.0.0:80->80/tcp
```

### Step 6: 브라우저 테스트

1. **브라우저에서 강력 새로고침**: `Ctrl + Shift + R` (Chrome/Firefox)
2. **접속**: http://139.150.11.99/
3. **로그인** 후 좌측 사이드바에서 **"스마트 배차 규칙"** 메뉴 확인
4. **Rule Builder 페이지**: http://139.150.11.99/dispatch-rules

---

## ⚡ 해결 방법 2: 로컬 빌드 + 파일 복사 (빠른 임시 방법)

빌드가 계속 실패하면 로컬에서 빌드 후 파일만 복사:

```bash
cd /root/uvis/frontend

# package.json 수정
sed -i 's/"@mui\/lab": "^7.0.1-beta.21"/"@mui\/lab": "^5.0.0-alpha.170"/' package.json

# 로컬에서 빌드
npm install --legacy-peer-deps
npm run build

# 빌드 확인
ls -lh dist/index.html

# 컨테이너에 복사
cd /root/uvis
docker-compose stop frontend
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/
docker-compose start frontend

# 확인
sleep 10
docker-compose ps frontend
curl -I http://localhost/
```

---

## 🔍 문제 해결 체크리스트

### ✅ 성공 확인

- [ ] `docker-compose ps` → `uvis-frontend` 상태가 `Up (healthy)`
- [ ] `ls -lh frontend/dist/index.html` → 빌드 날짜가 현재 시간
- [ ] `curl -I http://localhost/` → `HTTP/1.1 200 OK`
- [ ] `curl http://localhost:8000/api/v1/dispatch-rules/` → 2개 규칙 반환
- [ ] 브라우저 http://139.150.11.99/ → 로그인 화면 정상
- [ ] 좌측 사이드바 → "스마트 배차 규칙" 메뉴 보임
- [ ] http://139.150.11.99/dispatch-rules → Rule Builder 페이지 정상

### ❌ 실패 시 확인사항

#### 1. Docker 빌드 실패

```bash
# 빌드 로그 확인
docker-compose build frontend 2>&1 | tee build.log
cat build.log | grep -i error
```

**일반적인 오류:**
- `ERESOLVE could not resolve` → package.json에 `--legacy-peer-deps` 추가 필요
- `npm ERR! code ENOENT` → package-lock.json 삭제 후 재시도

#### 2. 컨테이너 재시작 반복

```bash
# Frontend 로그 확인
docker-compose logs frontend --tail=100 | grep -i error

# Nginx 설정 문제 확인
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
```

**일반적인 문제:**
- `nginx: [emerg] "user" directive is not allowed here` → nginx.conf 파일 문제
- `host not found in upstream "frontend"` → Docker 네트워크 문제

#### 3. 페이지가 로드되지 않음

```bash
# Frontend 컨테이너 내부 확인
docker-compose exec frontend ls -la /usr/share/nginx/html/

# 파일이 있어야 함
# index.html, assets/, locales/, manifest.json 등
```

---

## 📸 성공 스크린샷 예상

### 1. 메인 페이지
- 좌측 사이드바에 **"스마트 배차 규칙"** 메뉴 (⚙️ 아이콘)
- isNew: true 뱃지 표시

### 2. Rule Builder 페이지 (http://139.150.11.99/dispatch-rules)
- **2개 규칙 카드 표시**:
  - Priority Drivers (priority: 100, assignment)
  - Nearby Drivers Priority (priority: 90, assignment)
- **+ 새 규칙 만들기** 버튼
- **각 규칙 카드**에 Test, Logs, Performance 버튼

### 3. Visual Rule Builder
- ReactFlow 기반 노드 그래프
- Condition, Action, Logical 노드 타입
- Add Node, Delete Node, Save Rule, Test Rule 버튼

---

## 🎯 최종 테스트 명령어

```bash
# 1. 컨테이너 상태
docker-compose ps

# 2. Frontend 접속
curl -I http://localhost/

# 3. API 접속
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/dispatch-rules/ | jq .

# 4. Rule 테스트
curl -X POST http://localhost:8000/api/v1/dispatch-rules/1/test \
  -H "Content-Type: application/json" \
  -d '{
    "test_data": {
      "driver_rating": 4.8,
      "distance_km": 3.5
    }
  }' | jq .

# 5. 브라우저 접속
echo "http://139.150.11.99/"
echo "http://139.150.11.99/dispatch-rules"
```

---

## 🆘 긴급 복구 (모든 방법 실패 시)

```bash
cd /root/uvis

# 1. 모든 컨테이너 중지
docker-compose down

# 2. Frontend 이미지 완전 제거
docker rmi uvis-frontend

# 3. 빌드 캐시 정리
docker builder prune -af

# 4. 처음부터 다시 시작
docker-compose build --no-cache frontend
docker-compose up -d

# 5. 30초 대기
sleep 30

# 6. 전체 상태 확인
docker-compose ps
docker-compose logs frontend --tail=50
```

---

## 📝 변경사항 요약

| 파일 | 변경 내용 | 이유 |
|------|----------|------|
| `frontend/package.json` | `@mui/lab`: `7.0.1-beta.21` → `5.0.0-alpha.170` | MUI Material v5와 호환 |
| `frontend/Dockerfile` | `RUN npm install` → `RUN npm install --legacy-peer-deps` | peer dependency 충돌 무시 |
| `frontend/Dockerfile` | `COPY nginx.conf /etc/nginx/nginx.conf` → `/etc/nginx/conf.d/default.conf` | 올바른 Nginx 설정 경로 |

---

## 🔗 관련 문서

- [PHASE10_FRONTEND_INTEGRATION_COMPLETE.md](./PHASE10_FRONTEND_INTEGRATION_COMPLETE.md)
- [PHASE10_FRONTEND_INTEGRATION_SUMMARY.md](./PHASE10_FRONTEND_INTEGRATION_SUMMARY.md)
- [SERVER_OVERLOAD_RECOVERY_GUIDE.md](./SERVER_OVERLOAD_RECOVERY_GUIDE.md)
- [GABIA_SERVER_RECOVERY_GUIDE.md](./GABIA_SERVER_RECOVERY_GUIDE.md)

---

## 📞 지원

- **GitHub**: https://github.com/rpaakdi1-spec/3-
- **서버 IP**: 139.150.11.99
- **API Docs**: http://139.150.11.99:8000/docs
- **Grafana**: http://139.150.11.99:3001

---

**작성**: AI Assistant (Claude Code Agent)  
**최종 업데이트**: 2026-02-08 15:30 KST  
**버전**: 1.0
