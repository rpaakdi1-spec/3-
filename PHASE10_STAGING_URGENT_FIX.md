# Phase 10 스테이징 배포 긴급 수정

## 🚨 발생한 문제

### 문제 1: DB_PASSWORD 환경 변수
```
WARN[0000] The "DB_PASSWORD" variable is not set. Defaulting to a blank string.
```

### 문제 2: MUI Lab 버전 충돌
```
Could not resolve dependency:
peer @mui/material@"^7.3.7" from @mui/lab@7.0.1-beta.21
```

---

## ✅ 즉시 해결 방법

### 스테이징 서버에서 실행하세요:

```bash
# ========================================
# 1. 환경 변수 확인 및 export
# ========================================
cd /root/uvis

# .env 파일에서 DB_PASSWORD 확인
cat .env | grep DB_PASSWORD

# 환경 변수로 export (Docker Compose가 읽을 수 있도록)
export $(cat .env | grep -v '^#' | xargs)

# 확인
echo $DB_PASSWORD

# ========================================
# 2. Frontend package.json 수정 (@mui/lab 버전 다운그레이드)
# ========================================
cd /root/uvis/frontend

# @mui/lab 버전을 5.x로 변경
sed -i 's/"@mui\/lab": ".*"/"@mui\/lab": "^5.0.0-alpha.176"/' package.json

# 확인
cat package.json | grep "@mui/lab"

# ========================================
# 3. Docker Compose 파일 수정 (npm install에 --legacy-peer-deps 추가)
# ========================================
cd /root/uvis/frontend

# Dockerfile 수정
cat > Dockerfile << 'DOCKERFILE'
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./

# Install dependencies with legacy peer deps
RUN npm install --legacy-peer-deps

COPY . .

RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
DOCKERFILE

# ========================================
# 4. 백엔드 마이그레이션 (루트에서 실행)
# ========================================
cd /root/uvis

# 환경 변수 다시 export
export $(cat .env | grep -v '^#' | xargs)

# 마이그레이션 실행
docker-compose run --rm backend alembic upgrade head

# ========================================
# 5. Docker Compose 재시작
# ========================================
cd /root/uvis

# Down
docker-compose down

# Up with build
docker-compose up -d --build

# ========================================
# 6. 상태 확인 (60초 대기)
# ========================================
echo "컨테이너 시작 대기 중..."
sleep 60

docker-compose ps

# 백엔드 로그 확인
docker-compose logs backend --tail=50

# 프론트엔드 로그 확인
docker-compose logs frontend --tail=30

# ========================================
# 7. API 테스트
# ========================================
echo ""
echo "API Health Check:"
curl http://localhost:8000/health

echo ""
echo "Phase 10 API:"
curl http://localhost:8000/api/v1/dispatch-rules

echo ""
echo "=========================================="
echo "✅ 배포 완료!"
echo "=========================================="
echo "Swagger: http://139.150.11.99:8000/docs"
echo "Frontend: http://139.150.11.99:3000"
echo "Rules: http://139.150.11.99:3000/dispatch-rules"
```

---

## 📝 단계별 상세 설명

### 1단계: .env 환경 변수 확인

```bash
cd /root/uvis
cat .env
```

다음 내용이 있는지 확인:
```env
DB_PASSWORD=your_password_here
```

없으면 추가:
```bash
vi .env
# DB_PASSWORD=SecurePassword123! 추가
```

### 2단계: package.json 수정

문제: @mui/lab@7.x는 @mui/material@7.x를 요구하지만, 프로젝트는 @mui/material@5.x 사용

해결: @mui/lab을 5.x 버전으로 다운그레이드

```bash
cd /root/uvis/frontend
vi package.json
```

변경:
```json
"@mui/lab": "^5.0.0-alpha.176"
```

### 3단계: Frontend Dockerfile 수정

`--legacy-peer-deps` 플래그 추가:

```dockerfile
RUN npm install --legacy-peer-deps
```

### 4단계: 환경 변수 Export

Docker Compose가 .env 파일을 자동으로 읽지 못하는 경우:

```bash
export $(cat .env | grep -v '^#' | xargs)
echo $DB_PASSWORD  # 확인
```

### 5단계: 배포

```bash
cd /root/uvis
docker-compose down
docker-compose up -d --build
```

---

## 🔧 대안: docker-compose.yml 수정

`.env` 파일을 읽도록 docker-compose.yml 수정:

```bash
cd /root/uvis
vi docker-compose.yml
```

`db` 서비스에 `env_file` 추가:

```yaml
services:
  db:
    image: postgres:15
    env_file:
      - .env
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    # ...
```

---

## 🆘 문제가 계속되면

### Option 1: @mui/lab 완전 제거 (Timeline 사용 안 함)

RuleVersionHistory.tsx에서 Timeline 대신 간단한 리스트 사용:

```bash
cd /root/uvis/frontend

# @mui/lab 제거
npm uninstall @mui/lab

# package.json에서도 제거
vi package.json
# "@mui/lab" 라인 삭제

# 재빌드
cd /root/uvis
docker-compose up -d --build
```

### Option 2: MUI 전체 업그레이드 (권장하지 않음)

모든 MUI 패키지를 v7로 업그레이드 (Breaking Changes 많음):

```bash
cd /root/uvis/frontend
npm install @mui/material@^7.3.7 @mui/icons-material@^7.3.7 @mui/lab@^7.0.1-beta.21 --legacy-peer-deps
```

---

## 📋 체크리스트

배포 성공 여부 확인:

```bash
# 1. 컨테이너 상태
docker-compose ps
# 모두 Up 상태여야 함

# 2. 백엔드 로그
docker-compose logs backend --tail=20
# "Application startup complete" 메시지 확인

# 3. API Health
curl http://localhost:8000/health
# {"status":"ok"} 응답

# 4. 데이터베이스 테이블
docker-compose exec db psql -U uvis_user -d uvis_db -c "\dt" | grep dispatch_rules
# dispatch_rules 및 rule_execution_logs 테이블 확인

# 5. 프론트엔드
curl -I http://localhost:3000
# HTTP/1.1 200 OK
```

---

## 🎯 최종 확인 스크립트

모든 수정이 완료되면:

```bash
#!/bin/bash

cd /root/uvis

echo "=========================================="
echo "Phase 10 배포 최종 확인"
echo "=========================================="

# 환경 변수 export
export $(cat .env | grep -v '^#' | xargs)

# Docker 재시작
docker-compose down
sleep 5
docker-compose up -d --build

# 60초 대기
echo "컨테이너 시작 대기 중 (60초)..."
sleep 60

# 상태 확인
echo ""
echo "=== Docker 컨테이너 상태 ==="
docker-compose ps

echo ""
echo "=== 백엔드 로그 (최근 30줄) ==="
docker-compose logs backend --tail=30

echo ""
echo "=== 프론트엔드 로그 (최근 20줄) ==="
docker-compose logs frontend --tail=20

echo ""
echo "=== API Health Check ==="
curl -s http://localhost:8000/health || echo "❌ API 응답 없음"

echo ""
echo "=== Phase 10 API ==="
curl -s http://localhost:8000/api/v1/dispatch-rules | head -20 || echo "❌ Phase 10 API 응답 없음"

echo ""
echo "=== 데이터베이스 테이블 ==="
docker-compose exec -T db psql -U uvis_user -d uvis_db -c "\dt" | grep -E "dispatch_rules|rule_execution"

echo ""
echo "=========================================="
echo "배포 완료!"
echo "=========================================="
echo "Swagger UI: http://139.150.11.99:8000/docs"
echo "Frontend: http://139.150.11.99:3000"
echo "Phase 10: http://139.150.11.99:3000/dispatch-rules"
```

---

**작성**: 2026-02-08  
**상태**: Urgent Fix Ready
