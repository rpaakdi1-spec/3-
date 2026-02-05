# Phase 4 Week 11-12: 통합 & 배포 로드맵

## 📋 프로젝트 개요

**기간**: 2026-02-05 ~ 2026-03-19 (2주)  
**목표**: 전체 시스템 통합, 테스트, 최적화 및 프로덕션 배포  
**예상 가치**: ₩36,000,000/년  
**상태**: 🟡 진행 중

---

## 🎯 비즈니스 목표

### 핵심 KPI
- 🚀 **시스템 가용성**: 99.9% (연간 다운타임 < 8.76시간)
- ⚡ **평균 응답 시간**: < 200ms
- 📊 **동시 접속자**: 1,000명 이상 처리
- 🔒 **보안 취약점**: 0개
- 📈 **배포 성공률**: 100%
- 🔄 **자동화율**: 95%

### ROI 계산
```
시스템 안정성 향상: ₩18M
  - 다운타임 감소: ₩10M
  - 장애 대응 시간 단축: ₩8M

성능 최적화: ₩12M
  - 서버 비용 절감: ₩7M
  - 응답 시간 개선: ₩5M

운영 자동화: ₩6M
  - 배포 시간 단축: ₩4M
  - 수동 작업 감소: ₩2M

총 연간 절감: ₩36,000,000
투자 비용: ₩3,000,000
ROI: 1,100%
투자 회수 기간: 1개월
```

---

## 🏗️ 주요 작업

### 1. Docker 컨테이너화 ⭐

#### 백엔드 Docker 설정
**파일**: `backend/Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

# 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### 프론트엔드 Docker 설정
**파일**: `frontend/Dockerfile`
```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose
**파일**: `docker-compose.yml`
```yaml
version: '3.8'

services:
  # PostgreSQL
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: uvis_db
      POSTGRES_USER: uvis_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U uvis_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://uvis_user:${DB_PASSWORD}@db:5432/uvis_db
      REDIS_URL: redis://redis:6379
      JWT_SECRET: ${JWT_SECRET}
      APP_ENV: production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  # Nginx (리버스 프록시)
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

---

### 2. CI/CD 파이프라인 ⭐

#### GitHub Actions
**파일**: `.github/workflows/deploy.yml`
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: uvis/backend:latest
      
      - name: Build and push frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: uvis/frontend:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    
    steps:
      - name: Deploy to production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /opt/uvis
            docker-compose pull
            docker-compose up -d
            docker-compose exec -T backend alembic upgrade head
```

---

### 3. 모니터링 & 로깅 ⭐

#### Prometheus 설정
**파일**: `monitoring/prometheus.yml`
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'fastapi'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

#### Grafana 대시보드
**파일**: `monitoring/grafana/dashboards/system.json`
```json
{
  "dashboard": {
    "title": "UVIS System Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
          }
        ]
      }
    ]
  }
}
```

#### ELK Stack (로그 수집)
**파일**: `monitoring/logstash/logstash.conf`
```conf
input {
  file {
    path => "/var/log/uvis/*.log"
    start_position => "beginning"
    codec => json
  }
}

filter {
  if [level] == "ERROR" {
    mutate {
      add_tag => ["error"]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "uvis-logs-%{+YYYY.MM.dd}"
  }
}
```

---

### 4. 보안 강화 ⭐

#### 보안 헤더 설정
**파일**: `backend/app/middleware/security.py`
```python
from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
```

#### Rate Limiting
**파일**: `backend/app/middleware/rate_limit.py`
```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from redis import Redis
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_url: str, requests_per_minute: int = 60):
        super().__init__(app)
        self.redis = Redis.from_url(redis_url)
        self.requests_per_minute = requests_per_minute
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        current = self.redis.get(key)
        
        if current and int(current) >= self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Too many requests")
        
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)
        pipe.execute()
        
        response = await call_next(request)
        return response
```

#### SQL Injection 방지
- ✅ SQLAlchemy ORM 사용 (Parameterized queries)
- ✅ 입력 검증 (Pydantic)
- ✅ Prepared statements

#### XSS 방지
- ✅ Content Security Policy
- ✅ HTML 이스케이핑
- ✅ 입력 sanitization

---

### 5. 성능 최적화 ⭐

#### 데이터베이스 최적화
**파일**: `backend/alembic/versions/add_indexes.py`
```python
"""Add performance indexes

Revision ID: xxx
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # 자주 조회되는 컬럼에 인덱스 추가
    op.create_index('idx_orders_status', 'orders', ['status'])
    op.create_index('idx_orders_created_at', 'orders', ['created_at'])
    op.create_index('idx_dispatches_status', 'dispatches', ['status'])
    op.create_index('idx_dispatches_driver_id', 'dispatches', ['driver_id'])
    op.create_index('idx_vehicles_license_plate', 'vehicles', ['license_plate'])
    
    # 복합 인덱스
    op.create_index(
        'idx_orders_status_created',
        'orders',
        ['status', 'created_at']
    )
    
    # Full-text search 인덱스
    op.execute("""
        CREATE INDEX idx_orders_address_fts 
        ON orders 
        USING gin(to_tsvector('korean', pickup_address || ' ' || delivery_address))
    """)

def downgrade():
    op.drop_index('idx_orders_status')
    op.drop_index('idx_orders_created_at')
    op.drop_index('idx_dispatches_status')
    op.drop_index('idx_dispatches_driver_id')
    op.drop_index('idx_vehicles_license_plate')
    op.drop_index('idx_orders_status_created')
    op.drop_index('idx_orders_address_fts')
```

#### Redis 캐싱 전략
**파일**: `backend/app/core/cache.py`
```python
from redis import Redis
from functools import wraps
import json
import hashlib

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url)
    
    def cache(self, ttl: int = 300):
        """캐싱 데코레이터"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 캐시 키 생성
                cache_key = self._generate_key(func.__name__, args, kwargs)
                
                # 캐시 확인
                cached = self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)
                
                # 함수 실행
                result = await func(*args, **kwargs)
                
                # 캐시 저장
                self.redis.setex(
                    cache_key,
                    ttl,
                    json.dumps(result, default=str)
                )
                
                return result
            return wrapper
        return decorator
    
    def _generate_key(self, func_name: str, args, kwargs) -> str:
        key_data = f"{func_name}:{args}:{kwargs}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def invalidate(self, pattern: str):
        """캐시 무효화"""
        for key in self.redis.scan_iter(pattern):
            self.redis.delete(key)
```

#### 데이터베이스 커넥션 풀
**파일**: `backend/app/core/database.py`
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # 기본 커넥션 수
    max_overflow=40,       # 추가 커넥션 수
    pool_timeout=30,       # 타임아웃
    pool_recycle=3600,     # 커넥션 재사용 주기
    pool_pre_ping=True,    # 커넥션 유효성 체크
)
```

---

### 6. 백업 & 복구 ⭐

#### 자동 백업 스크립트
**파일**: `scripts/backup.sh`
```bash
#!/bin/bash

# 설정
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="uvis_db"
DB_USER="uvis_user"
RETENTION_DAYS=30

# 데이터베이스 백업
echo "Starting database backup..."
pg_dump -U $DB_USER $DB_NAME | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# 파일 백업 (uploads)
echo "Starting file backup..."
tar -czf "$BACKUP_DIR/files_backup_$DATE.tar.gz" /app/uploads

# 설정 파일 백업
echo "Starting config backup..."
tar -czf "$BACKUP_DIR/config_backup_$DATE.tar.gz" /app/.env /app/docker-compose.yml

# S3에 업로드
aws s3 cp "$BACKUP_DIR/db_backup_$DATE.sql.gz" s3://uvis-backups/
aws s3 cp "$BACKUP_DIR/files_backup_$DATE.tar.gz" s3://uvis-backups/
aws s3 cp "$BACKUP_DIR/config_backup_$DATE.tar.gz" s3://uvis-backups/

# 오래된 백업 삭제
find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $DATE"
```

#### 복구 스크립트
**파일**: `scripts/restore.sh`
```bash
#!/bin/bash

# 사용법: ./restore.sh backup_date
BACKUP_DATE=$1
BACKUP_DIR="/backups"

# 데이터베이스 복구
echo "Restoring database..."
gunzip < "$BACKUP_DIR/db_backup_$BACKUP_DATE.sql.gz" | psql -U uvis_user uvis_db

# 파일 복구
echo "Restoring files..."
tar -xzf "$BACKUP_DIR/files_backup_$BACKUP_DATE.tar.gz" -C /

echo "Restore completed"
```

#### Cron 설정
```cron
# 매일 새벽 3시 백업
0 3 * * * /opt/uvis/scripts/backup.sh >> /var/log/backup.log 2>&1

# 매주 일요일 새벽 4시 전체 백업
0 4 * * 0 /opt/uvis/scripts/full_backup.sh >> /var/log/backup.log 2>&1
```

---

### 7. 통합 테스트 ⭐

#### E2E 테스트 (Pytest)
**파일**: `backend/tests/test_e2e.py`
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_order_to_dispatch_flow():
    """주문 생성 → 배차 → 완료 전체 플로우 테스트"""
    
    # 1. 로그인
    login_response = client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "testpass"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 주문 생성
    order_data = {
        "client_id": 1,
        "pickup_address": "서울시 강남구",
        "delivery_address": "부산시 해운대구",
        "cargo_type": "냉장",
        "weight": 100.0
    }
    order_response = client.post(
        "/api/v1/orders",
        json=order_data,
        headers=headers
    )
    assert order_response.status_code == 201
    order_id = order_response.json()["id"]
    
    # 3. 배차 생성
    dispatch_data = {
        "order_id": order_id,
        "vehicle_id": 1,
        "driver_id": 1
    }
    dispatch_response = client.post(
        "/api/v1/dispatches",
        json=dispatch_data,
        headers=headers
    )
    assert dispatch_response.status_code == 201
    dispatch_id = dispatch_response.json()["id"]
    
    # 4. 배차 상태 업데이트
    status_response = client.put(
        f"/api/v1/mobile/dispatches/{dispatch_id}/status",
        json={"status": "COMPLETED"},
        headers=headers
    )
    assert status_response.status_code == 200
    
    # 5. 주문 상태 확인
    order_check = client.get(
        f"/api/v1/orders/{order_id}",
        headers=headers
    )
    assert order_check.json()["status"] == "COMPLETED"
```

#### 부하 테스트 (Locust)
**파일**: `tests/load/locustfile.py`
```python
from locust import HttpUser, task, between

class UVISUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """로그인"""
        response = self.client.post("/api/v1/auth/login", data={
            "username": "test@example.com",
            "password": "testpass"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def view_dispatches(self):
        """배차 목록 조회"""
        self.client.get(
            "/api/v1/mobile/dispatches",
            headers=self.headers
        )
    
    @task(2)
    def view_dashboard(self):
        """대시보드 조회"""
        self.client.get(
            "/api/v1/mobile/summary",
            headers=self.headers
        )
    
    @task(1)
    def update_location(self):
        """위치 업데이트"""
        self.client.post(
            "/api/v1/mobile/location",
            json={"latitude": 37.5665, "longitude": 126.9780},
            headers=self.headers
        )
```

---

## 📊 개발 일정

### Week 11 (2026-02-05 ~ 2026-02-11)

#### Day 1-2: Docker & CI/CD
- [x] Dockerfile 작성 (백엔드/프론트엔드)
- [x] docker-compose.yml 작성
- [ ] GitHub Actions 워크플로우 설정
- [ ] Docker Hub 이미지 빌드

#### Day 3-4: 모니터링 & 로깅
- [ ] Prometheus 설정
- [ ] Grafana 대시보드
- [ ] ELK Stack 구성
- [ ] 알림 규칙 설정

#### Day 5-7: 보안 & 최적화
- [ ] 보안 헤더 미들웨어
- [ ] Rate limiting
- [ ] 데이터베이스 인덱싱
- [ ] Redis 캐싱
- [ ] 커넥션 풀 최적화

### Week 12 (2026-02-12 ~ 2026-02-19)

#### Day 8-9: 백업 & 복구
- [ ] 자동 백업 스크립트
- [ ] S3 통합
- [ ] 복구 스크립트
- [ ] Cron 설정

#### Day 10-11: 통합 테스트
- [ ] E2E 테스트 작성
- [ ] 부하 테스트 (Locust)
- [ ] 성능 테스트
- [ ] 보안 스캔

#### Day 12-13: 문서화
- [ ] API 문서 완성
- [ ] 배포 가이드
- [ ] 운영 매뉴얼
- [ ] 트러블슈팅 가이드

#### Day 14: 최종 배포
- [ ] 프로덕션 배포
- [ ] 모니터링 확인
- [ ] 성능 검증
- [ ] 완료 보고서

---

## 🎯 성공 기준

### 시스템 성능
- ✅ 평균 응답 시간 < 200ms
- ✅ 동시 접속자 1,000명 처리
- ✅ 99.9% 가용성
- ✅ 에러율 < 0.1%

### 보안
- ✅ OWASP Top 10 취약점 0개
- ✅ SSL/TLS 인증서 적용
- ✅ API Rate limiting 구현
- ✅ 보안 헤더 모두 적용

### 배포
- ✅ CI/CD 파이프라인 자동화
- ✅ 무중단 배포 (Blue-Green)
- ✅ 롤백 가능
- ✅ 배포 시간 < 5분

### 모니터링
- ✅ 실시간 대시보드
- ✅ 자동 알림 (Slack/Email)
- ✅ 로그 집계 및 분석
- ✅ 성능 메트릭 수집

---

## 📚 문서 작성 항목

### 1. API 문서
- Swagger/OpenAPI 완성
- 인증 방법
- 엔드포인트 설명
- 예제 코드

### 2. 배포 가이드
- 환경 설정
- Docker 실행
- 데이터베이스 마이그레이션
- SSL 인증서

### 3. 운영 매뉴얼
- 일일 점검 사항
- 백업 확인
- 모니터링 대시보드
- 알림 대응

### 4. 트러블슈팅
- 자주 발생하는 문제
- 해결 방법
- 로그 분석
- 복구 절차

---

## ✅ 체크리스트

### 인프라
- [ ] Docker 컨테이너화
- [ ] docker-compose.yml
- [ ] Nginx 리버스 프록시
- [ ] SSL/TLS 인증서
- [ ] 도메인 설정

### CI/CD
- [ ] GitHub Actions
- [ ] 자동 테스트
- [ ] Docker Hub 이미지
- [ ] 자동 배포

### 모니터링
- [ ] Prometheus
- [ ] Grafana 대시보드
- [ ] ELK Stack
- [ ] 알림 시스템

### 보안
- [ ] 보안 헤더
- [ ] Rate limiting
- [ ] SQL Injection 방지
- [ ] XSS 방지
- [ ] CSRF 방지

### 성능
- [ ] 데이터베이스 인덱스
- [ ] Redis 캐싱
- [ ] 커넥션 풀
- [ ] CDN 설정

### 백업
- [ ] 자동 백업 스크립트
- [ ] S3 통합
- [ ] 복구 스크립트
- [ ] Cron 설정

### 테스트
- [ ] 단위 테스트
- [ ] 통합 테스트
- [ ] E2E 테스트
- [ ] 부하 테스트
- [ ] 보안 스캔

### 문서
- [ ] API 문서
- [ ] 배포 가이드
- [ ] 운영 매뉴얼
- [ ] 트러블슈팅 가이드

---

## 🎯 다음 단계

Week 12 완료 후:
1. **프로덕션 배포** ✅
2. **모니터링 시작** 📊
3. **Phase 4 완료 보고** 📝
4. **Phase 5 계획** (선택사항)

---

**로드맵 작성 완료**  
**다음**: Docker 컨테이너화 시작
