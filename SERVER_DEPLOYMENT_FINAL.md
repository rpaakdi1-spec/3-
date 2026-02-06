# 🚀 서버 배포 최종 수정 가이드

## 📋 문제 요약

### 발견된 문제들
1. ✅ **Backend 순환 import 이슈** - `database.py`와 `models` 간 순환 참조
2. ✅ **SECRET_KEY 누락** - 컨테이너 재생성 시 환경변수 손실
3. ✅ **metadata 필드명 충돌** - SQLAlchemy 예약어 사용
4. ✅ **NotificationLevel 정의 누락** - `monitoring.py`에서 미정의 변수 참조
5. ✅ **Models export 누락** - `__init__.py`에서 일부 모델 미export
6. ⚠️ **Frontend package-lock.json 누락** - npm ci 실패 원인

### 해결된 문제들
- ✅ `backend/app/core/database.py`: 순환 import 해결 (Base를 database.py에 직접 정의)
- ✅ `backend/app/models/notification.py`: metadata → notification_metadata 변경
- ✅ `backend/app/models/__init__.py`: 모든 모델 export 추가
- ✅ `backend/app/api/monitoring.py`: NotificationLevel 참조 제거 (문자열로 변경)
- ✅ `docker-compose.yml`: backend 서비스에 env_file 추가
- ✅ `.env`: SECRET_KEY, DATABASE_URL 자동 생성

---

## 🎯 서버에서 실행할 명령어

### 방법 1: 자동 스크립트 (권장) ⭐

```bash
cd /root/uvis

# 최신 코드 가져오기
git fetch origin genspark_ai_developer
git reset --hard origin/genspark_ai_developer

# 스크립트 실행 권한 부여
chmod +x SERVER_FINAL_FIX.sh

# 스크립트 실행
./SERVER_FINAL_FIX.sh
```

**예상 실행 시간:** 약 3-4분  
**포함 작업:**
- 최신 코드 반영 (commit 707138b)
- .env 파일 검증 및 SECRET_KEY 자동 생성
- docker-compose.yml에 env_file 추가
- Backend 재빌드 및 재시작
- Health check 자동 확인

---

### 방법 2: 수동 단계별 실행

```bash
cd /root/uvis

# 1. 최신 코드 가져오기
git fetch origin genspark_ai_developer
git reset --hard origin/genspark_ai_developer

# 2. SECRET_KEY 생성
SECRET_KEY=$(openssl rand -hex 32)
echo "SECRET_KEY=$SECRET_KEY" >> .env

# 3. DATABASE_URL 설정
DB_NAME=uvis_db
DB_USER=uvis_user
DB_PASSWORD=uvis_secure_password_2024
echo "DB_NAME=$DB_NAME" >> .env
echo "DB_USER=$DB_USER" >> .env
echo "DB_PASSWORD=$DB_PASSWORD" >> .env
echo "DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}" >> .env

# 4. Backend 재빌드 및 시작
docker-compose build --no-cache backend
docker-compose up -d --force-recreate backend

# 5. 90초 대기
sleep 90

# 6. 상태 확인
docker-compose ps backend
docker-compose logs --tail=50 backend

# 7. Health Check
curl -s http://localhost:8000/health
```

---

## ✅ 성공 확인 방법

### 1. Backend Health Check
```bash
curl -s http://localhost:8000/health
```

**예상 응답:**
```json
{
  "status": "healthy",
  "app_name": "Cold Chain Dispatch System",
  "environment": "production"
}
```

### 2. API 문서 접근
브라우저에서:
- **API Docs**: http://YOUR_SERVER_IP:8000/docs
- **ReDoc**: http://YOUR_SERVER_IP:8000/redoc
- **Root**: http://YOUR_SERVER_IP:8000/

### 3. 컨테이너 상태 확인
```bash
docker-compose ps
```

**예상 출력:**
```
NAME            STATUS          PORTS
uvis-backend    Up (healthy)    0.0.0.0:8000->8000/tcp
uvis-db         Up (healthy)    0.0.0.0:5432->5432/tcp
uvis-redis      Up (healthy)    0.0.0.0:6379->6379/tcp
```

---

## 🔧 주요 변경사항 (Commit 707138b)

### 1. backend/app/core/database.py
```python
# Before: 순환 import 발생
from app.models import *  # ❌

# After: init_db()에서만 import
def init_db():
    from app import models  # ✅ 함수 내부에서만 import
    Base.metadata.create_all(bind=engine)
```

### 2. backend/app/models/notification.py
```python
# Before: SQLAlchemy 예약어 사용
metadata = Column(JSON, comment='추가 메타데이터 (JSON)')  # ❌

# After: 이름 변경
notification_metadata = Column(JSON, comment='추가 메타데이터 (JSON)')  # ✅
```

### 3. backend/app/api/monitoring.py
```python
# Before: 정의되지 않은 변수 참조
level=NotificationLevel.INFO  # ❌

# After: 문자열 사용
level="info"  # ✅
```

### 4. backend/app/models/__init__.py
```python
# 모든 모델 export 추가
from .base import Base
from .user import User
from .client import Client
from .vehicle import Vehicle, VehicleType, VehicleStatus
from .driver import Driver, DriverStatus
from .order import Order, OrderStatus
from .dispatch import Dispatch, DispatchRoute, DispatchStatus
# ... 30+ models

__all__ = [
    "Base", "User", "Client", "Vehicle", "VehicleType",
    "VehicleStatus", "Driver", "DriverStatus", "Order",
    "OrderStatus", "Dispatch", "DispatchRoute", "DispatchStatus",
    # ... 모든 모델
]
```

### 5. docker-compose.yml (자동 수정)
```yaml
services:
  backend:
    env_file:
      - .env  # ✅ 추가됨
    environment:
      - DATABASE_URL=${DATABASE_URL}
      # ...
```

---

## 🐛 문제 발생 시 디버깅

### Backend 로그 확인
```bash
# 전체 로그
docker-compose logs backend

# 최근 100줄
docker-compose logs --tail=100 backend

# 실시간 로그
docker-compose logs -f backend

# 에러만 필터링
docker-compose logs backend | grep -i error
```

### 환경 변수 확인
```bash
# .env 파일 확인
cat .env | grep -E "SECRET_KEY|DATABASE_URL|DB_"

# 컨테이너 내부 환경 변수 확인
docker exec uvis-backend env | grep -E "SECRET_KEY|DATABASE_URL"

# 컨테이너 내부 .env 파일 확인
docker exec uvis-backend cat /app/.env
```

### 데이터베이스 연결 확인
```bash
# PostgreSQL 접속 테스트
docker exec uvis-db psql -U uvis_user -d uvis_db -c "SELECT 1;"

# Redis 접속 테스트
docker exec uvis-redis redis-cli ping
```

### 포트 리스닝 확인
```bash
netstat -tuln | grep -E ":(80|8000|5173|5432|6379)"
```

---

## 📊 Frontend 배포 (다음 단계)

Backend가 정상 작동하면 Frontend 배포:

### Frontend package-lock.json 생성
```bash
cd /root/uvis/frontend

# Node.js 및 npm 설치 (없는 경우)
curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
yum install -y nodejs

# package-lock.json 생성
npm install

cd ..
```

### Frontend 빌드 및 시작
```bash
docker-compose build frontend nginx
docker-compose up -d frontend nginx

# 상태 확인
docker-compose ps
```

### Frontend 접속 확인
- **메인**: http://YOUR_SERVER_IP/
- **Login**: http://YOUR_SERVER_IP/login
- **IoT 모니터링**: http://YOUR_SERVER_IP/iot-sensors

---

## 📈 성능 최적화 (선택사항)

### 1. Redis 캐시 설정
```bash
# .env에 추가
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379
```

### 2. Gunicorn Worker 수 조정
```dockerfile
# backend/Dockerfile
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 3. Nginx 캐싱 설정
```nginx
# nginx/nginx.conf
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;
```

---

## 🔐 보안 강화 (프로덕션)

### 1. SECRET_KEY 교체
```bash
# 강력한 SECRET_KEY 생성
openssl rand -hex 64

# .env에서 교체 후 Backend 재시작
docker-compose restart backend
```

### 2. HTTPS 설정
```bash
# Let's Encrypt 인증서 발급
certbot --nginx -d your-domain.com
```

### 3. 방화벽 설정
```bash
# 필요한 포트만 오픈
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

---

## 📞 지원 및 연락

### GitHub Repository
- **Repo**: https://github.com/rpaakdi1-spec/3-
- **Branch**: genspark_ai_developer
- **Latest Commit**: 707138b

### Pull Request
- **PR #4**: https://github.com/rpaakdi1-spec/3-/pull/4

### 문제 보고
이슈 발생 시 다음 정보를 포함해 주세요:
1. 실행한 명령어
2. 에러 메시지 전문
3. `docker-compose logs backend` 출력
4. `.env` 파일 내용 (민감 정보 제외)

---

## ✨ 완료 체크리스트

배포 완료 후 확인:

- [ ] Backend health check 성공 (`curl http://localhost:8000/health`)
- [ ] API 문서 접근 가능 (http://YOUR_SERVER_IP:8000/docs)
- [ ] 데이터베이스 연결 정상
- [ ] Redis 연결 정상
- [ ] 모든 컨테이너 Healthy 상태
- [ ] Frontend 접속 가능 (http://YOUR_SERVER_IP/)
- [ ] 로그인 기능 테스트
- [ ] IoT 센서 모니터링 페이지 접근
- [ ] NAVER MAP API 키 설정 (필요 시)

---

## 🎉 배포 성공 후

축하합니다! 🎊

이제 다음 작업을 진행할 수 있습니다:
1. ✅ IoT 센서 데이터 수집 테스트
2. ✅ 실시간 모니터링 대시보드 확인
3. ✅ 온도 알람 시스템 테스트
4. ✅ 사용자 관리 및 권한 설정
5. ✅ 데이터 백업 및 복구 절차 수립

---

**마지막 업데이트:** 2026-02-05  
**작성자:** GenSpark AI Developer  
**Commit:** 707138b
