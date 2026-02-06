# 🔧 Cold Chain Dispatch System - 배포 문제 해결 가이드

## 📋 목차
1. [현재 상황 요약](#현재-상황-요약)
2. [빠른 수정 방법](#빠른-수정-방법)
3. [상세 문제 분석](#상세-문제-분석)
4. [단계별 해결 방법](#단계별-해결-방법)
5. [검증 방법](#검증-방법)

---

## 🚨 현재 상황 요약

### 문제점
- ❌ Backend: `unhealthy` 상태 (port 8000 열림, health check 실패)
- ❌ Nginx: `unhealthy` 상태, 502 Bad Gateway
- ❌ Frontend: port 5173 접근 불가
- ✅ Database (PostgreSQL): `healthy`
- ✅ Redis: `healthy`

### 원인 분석
1. **Backend 문제**:
   - 환경변수 누락 가능성 (SECRET_KEY, DATABASE_URL)
   - Import 오류 (telemetry, get_current_user)
   - Twilio/Firebase 설정 오류

2. **Nginx 문제**:
   - Backend와 통신 실패 (502 error)
   - Frontend와 연결 실패

3. **Frontend 문제**:
   - 컨테이너는 시작되었으나 포트 5173이 외부 노출 안됨
   - Nginx를 통한 접근만 가능해야 함

---

## ⚡ 빠른 수정 방법

### 방법 1: 자동 수정 스크립트 사용 (권장)

```bash
cd /root/uvis
chmod +x SERVER_FIX_DEPLOYMENT.sh
./SERVER_FIX_DEPLOYMENT.sh
```

이 스크립트는 다음을 자동으로 수행합니다:
- 기존 컨테이너 정리
- .env 파일 검증 및 수정
- Docker 이미지 재빌드
- 서비스 재시작
- 헬스체크 수행

### 방법 2: 수동 수정 (단계별 제어 원하는 경우)

아래 [단계별 해결 방법](#단계별-해결-방법) 참조

---

## 🔍 상세 문제 분석

### 1. Backend 건강 상태 확인

```bash
# 백엔드 로그 확인
docker-compose logs backend | tail -100

# 예상되는 오류 패턴:
# - "SECRET_KEY Field required" → .env 파일 문제
# - "ImportError: cannot import name" → 코드 import 문제
# - "AttributeError: 'Settings' object has no attribute" → config.py 문제
```

### 2. 환경변수 로딩 확인

```bash
# 컨테이너 내부 환경변수 확인
docker exec uvis-backend env | grep -E "SECRET_KEY|DATABASE_URL|DB_PASSWORD"

# .env 파일 확인
grep -E "^SECRET_KEY=|^DATABASE_URL=|^DB_PASSWORD=" .env
```

### 3. 네트워크 연결 확인

```bash
# 백엔드 컨테이너 내부에서 DB 연결 확인
docker exec uvis-backend nc -zv db 5432

# Nginx에서 backend 연결 확인
docker exec uvis-nginx nc -zv backend 8000
```

---

## 🛠️ 단계별 해결 방법

### Step 1: 기존 컨테이너 완전 정리

```bash
cd /root/uvis

# 모든 컨테이너 중지 및 제거
docker-compose down
docker rm -f coldchain-backend coldchain-postgres coldchain-nginx uvis-backend uvis-frontend uvis-nginx 2>/dev/null || true

# 고아 컨테이너 정리
docker ps -a | grep -E "coldchain|uvis" | awk '{print $1}' | xargs docker rm -f 2>/dev/null || true

# 사용하지 않는 이미지 정리 (선택사항)
docker image prune -f
```

### Step 2: .env 파일 완전 재구성

```bash
cd /root/uvis

# 백업 생성
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# 필수 환경변수 확인 및 추가
cat > .env.check << 'EOF'
#!/bin/bash
# .env 검증 스크립트

ENV_FILE=".env"

# SECRET_KEY 확인
if ! grep -q "^SECRET_KEY=" $ENV_FILE || [ -z "$(grep "^SECRET_KEY=" $ENV_FILE | cut -d'=' -f2)" ]; then
    echo "SECRET_KEY=$(openssl rand -hex 32)" >> $ENV_FILE
    echo "✅ SECRET_KEY 추가됨"
fi

# DB_PASSWORD 확인
if ! grep -q "^DB_PASSWORD=" $ENV_FILE || [ -z "$(grep "^DB_PASSWORD=" $ENV_FILE | cut -d'=' -f2)" ]; then
    echo "DB_PASSWORD=uvis_secure_password_2024" >> $ENV_FILE
    echo "✅ DB_PASSWORD 추가됨"
fi

# DATABASE_URL 확인 및 생성
if ! grep -q "^DATABASE_URL=" $ENV_FILE || [ -z "$(grep "^DATABASE_URL=" $ENV_FILE | cut -d'=' -f2)" ]; then
    DB_NAME=$(grep "^DB_NAME=" $ENV_FILE | cut -d'=' -f2 || echo "uvis_db")
    DB_USER=$(grep "^DB_USER=" $ENV_FILE | cut -d'=' -f2 || echo "uvis_user")
    DB_PASSWORD=$(grep "^DB_PASSWORD=" $ENV_FILE | cut -d'=' -f2)
    
    echo "DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}" >> $ENV_FILE
    echo "✅ DATABASE_URL 추가됨"
fi

# NAVER_MAP API 키 확인
if ! grep -q "^NAVER_MAP_CLIENT_ID=" $ENV_FILE || [ -z "$(grep "^NAVER_MAP_CLIENT_ID=" $ENV_FILE | cut -d'=' -f2)" ]; then
    echo "NAVER_MAP_CLIENT_ID=your_naver_client_id_here" >> $ENV_FILE
    echo "⚠️  NAVER_MAP_CLIENT_ID 플레이스홀더 추가됨 (실제 키로 교체 필요)"
fi

if ! grep -q "^NAVER_MAP_CLIENT_SECRET=" $ENV_FILE || [ -z "$(grep "^NAVER_MAP_CLIENT_SECRET=" $ENV_FILE | cut -d'=' -f2)" ]; then
    echo "NAVER_MAP_CLIENT_SECRET=your_naver_client_secret_here" >> $ENV_FILE
    echo "⚠️  NAVER_MAP_CLIENT_SECRET 플레이스홀더 추가됨 (실제 키로 교체 필요)"
fi

echo ""
echo "📝 현재 .env 설정:"
grep -E "^DB_NAME=|^DB_USER=" $ENV_FILE
echo "DB_PASSWORD=****** (설정됨)"
echo "SECRET_KEY=****** (설정됨)"
echo "DATABASE_URL=****** (설정됨)"
EOF

chmod +x .env.check
./env.check
```

### Step 3: Docker Compose 파일 검증

```bash
# docker-compose.yml 에서 backend 설정 확인
grep -A20 "backend:" docker-compose.yml

# 확인 사항:
# 1. env_file: - .env 설정 여부
# 2. environment: 섹션에 중복 설정 없는지
# 3. depends_on: db, redis 설정 여부
```

### Step 4: 이미지 재빌드 (캐시 없이)

```bash
cd /root/uvis

# 캐시 없이 완전 재빌드
docker-compose build --no-cache backend frontend

# 빌드 로그에서 오류 확인
# 특히 "ERROR" 또는 "failed" 키워드 검색
```

### Step 5: 서비스 재시작 (순차적)

```bash
cd /root/uvis

# 1. 데이터베이스 먼저 시작
docker-compose up -d db redis

# 2. 안정화 대기
sleep 10

# 3. 백엔드 시작
docker-compose up -d backend

# 4. 백엔드 로그 실시간 모니터링 (다른 터미널에서)
# docker-compose logs -f backend

# 5. 백엔드 안정화 대기 (60초)
echo "백엔드 안정화 대기 중..."
sleep 60

# 6. 백엔드 health check
curl -s http://localhost:8000/health
# 예상 출력: {"status":"healthy","app_name":"Cold Chain Dispatch System","environment":"production"}

# 7. 백엔드가 healthy면 프론트엔드/nginx 시작
docker-compose up -d frontend nginx

# 8. 전체 서비스 확인
docker-compose ps
```

### Step 6: Nginx 설정 확인

```bash
# Nginx 설정 파일 확인
docker exec uvis-nginx cat /etc/nginx/conf.d/default.conf

# 확인 사항:
# - upstream backend { server backend:8000; } 설정
# - proxy_pass http://backend; 설정
# - location / { root /usr/share/nginx/html; } 프론트엔드 설정
```

만약 Nginx 설정에 문제가 있으면:

```bash
# Nginx 설정 파일 위치 확인
find /root/uvis -name "nginx.conf" -o -name "default.conf"

# 기본 Nginx 설정 (참고용)
cat > /root/uvis/nginx/default.conf << 'EOF'
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend Docs
    location /docs {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }

    location /redoc {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }

    # Health check
    location /health {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }
}
EOF

# Nginx 재시작
docker-compose restart nginx
```

---

## ✅ 검증 방법

### 1. 컨테이너 상태 확인

```bash
docker-compose ps

# 예상 출력 (모두 healthy 또는 Up 상태):
# NAME              STATUS                    PORTS
# uvis-backend      Up (healthy)              0.0.0.0:8000->8000/tcp
# uvis-db           Up (healthy)              0.0.0.0:5432->5432/tcp
# uvis-redis        Up (healthy)              0.0.0.0:6379->6379/tcp
# uvis-frontend     Up                        3000/tcp
# uvis-nginx        Up                        0.0.0.0:80->80/tcp
```

### 2. 백엔드 Health Check

```bash
# Health 엔드포인트
curl -s http://localhost:8000/health
# 예상: {"status":"healthy","app_name":"Cold Chain Dispatch System","environment":"production"}

# API 문서 접근
curl -s http://localhost:8000/docs | grep -o "<title>.*</title>"
# 예상: <title>Cold Chain Dispatch System - Swagger UI</title>

# Root 엔드포인트
curl -s http://localhost:8000/
# 예상: {"message":"Welcome to Cold Chain Dispatch System API","docs":"/docs","health":"/health"}
```

### 3. 프론트엔드 접근 확인

```bash
# Nginx를 통한 접근
curl -s -I http://localhost/ | head -5
# 예상: HTTP/1.1 200 OK

# HTML 내용 확인
curl -s http://localhost/ | grep -o "<title>.*</title>"
# 예상: <title>냉동냉장 배차 시스템</title> (또는 프론트엔드 타이틀)
```

### 4. 브라우저 테스트

1. 브라우저에서 `http://YOUR_SERVER_IP` 접속
2. 로그인 페이지 확인
3. 로그인 후 대시보드 접근
4. 사이드바에서 **"IoT 센서 모니터링"** 메뉴 확인
5. IoT 센서 페이지 접근: `/iot/sensors`

### 5. 로그 확인

```bash
# 백엔드 로그
docker-compose logs backend | tail -100

# 중요 로그 패턴:
# ✅ "Application startup complete!" → 정상 시작
# ✅ "Uvicorn running on http://0.0.0.0:8000" → 서버 실행 중
# ❌ "ValidationError" → 환경변수 문제
# ❌ "ImportError" → 코드 import 문제
# ❌ "Connection refused" → DB/Redis 연결 문제

# Nginx 로그
docker-compose logs nginx | tail -50

# 프론트엔드 로그
docker-compose logs frontend | tail -50
```

---

## 🆘 여전히 문제가 있다면

### 백엔드가 여전히 unhealthy인 경우

```bash
# 1. 백엔드 컨테이너 내부 접속
docker exec -it uvis-backend bash

# 2. 환경변수 확인
env | grep -E "SECRET_KEY|DATABASE_URL|DB_"

# 3. Python으로 직접 실행 테스트
cd /app
python -c "from app.core.config import settings; print(settings.SECRET_KEY[:10])"
# 오류가 나면 환경변수 문제

# 4. main.py 직접 실행
python -m uvicorn main:app --host 0.0.0.0 --port 8000
# 오류 메시지 확인
```

### Nginx가 502 에러를 계속 반환하는 경우

```bash
# 1. Backend 접근 테스트 (Nginx 컨테이너에서)
docker exec uvis-nginx curl -s http://backend:8000/health

# 만약 연결 실패하면:
docker exec uvis-nginx nc -zv backend 8000

# 2. 네트워크 확인
docker network ls
docker network inspect uvis_default

# 3. Backend가 같은 네트워크에 있는지 확인
docker inspect uvis-backend | grep NetworkMode
docker inspect uvis-nginx | grep NetworkMode
```

### 프론트엔드가 빈 페이지를 표시하는 경우

```bash
# 1. 프론트엔드 빌드 파일 확인
docker exec uvis-frontend ls -la /usr/share/nginx/html/

# 2. index.html 존재 확인
docker exec uvis-frontend cat /usr/share/nginx/html/index.html | head -20

# 3. 프론트엔드 빌드 로그 확인
docker-compose logs frontend | grep -E "Build|Error|Failed"
```

---

## 📞 추가 지원

위의 모든 방법을 시도했지만 여전히 문제가 있다면, 다음 정보를 수집하여 공유해주세요:

```bash
# 전체 시스템 상태 보고서 생성
cd /root/uvis

cat > system_report.sh << 'EOF'
#!/bin/bash
echo "=== System Report ==="
echo "Date: $(date)"
echo ""

echo "=== Docker Version ==="
docker --version
docker-compose --version
echo ""

echo "=== Container Status ==="
docker-compose ps
echo ""

echo "=== Backend Logs (last 100 lines) ==="
docker-compose logs --tail=100 backend
echo ""

echo "=== Nginx Logs (last 50 lines) ==="
docker-compose logs --tail=50 nginx
echo ""

echo "=== Frontend Logs (last 30 lines) ==="
docker-compose logs --tail=30 frontend
echo ""

echo "=== Environment Variables (masked) ==="
grep -E "^DB_NAME=|^DB_USER=|^REDIS_HOST=" .env
echo "DB_PASSWORD=****** (exists: $(grep -q '^DB_PASSWORD=' .env && echo 'yes' || echo 'no'))"
echo "SECRET_KEY=****** (exists: $(grep -q '^SECRET_KEY=' .env && echo 'yes' || echo 'no'))"
echo "DATABASE_URL=****** (exists: $(grep -q '^DATABASE_URL=' .env && echo 'yes' || echo 'no'))"
echo ""

echo "=== Network Info ==="
docker network ls
echo ""

echo "=== Port Listening ==="
netstat -tuln | grep -E ":(80|8000|5173|5432|6379) "
echo ""
EOF

chmod +x system_report.sh
./system_report.sh > system_report.txt 2>&1

echo "시스템 보고서가 system_report.txt에 저장되었습니다."
```

---

## 🎉 성공적인 배포 확인

모든 것이 정상적으로 작동하면:

✅ `docker-compose ps` - 모든 컨테이너가 `Up` 또는 `healthy`
✅ `curl http://localhost:8000/health` - `{"status":"healthy"}`
✅ `curl http://localhost:8000/docs` - Swagger UI HTML 반환
✅ `curl -I http://localhost/` - `HTTP/1.1 200 OK`
✅ 브라우저에서 `http://YOUR_SERVER_IP` - 로그인 페이지 표시
✅ 로그인 후 "IoT 센서 모니터링" 메뉴 접근 가능

축하합니다! 🎊
