# 🚀 FCM Import Error 수정 - 서버 배포 가이드

## 📋 문제 요약
Backend 컨테이너가 시작하지 못하는 문제:
```
ImportError: cannot import name 'fcm_service' from 'app.services.fcm_service'
```

## ✅ 수정 완료
- **커밋:** `04af91b` - fix(backend): Fix FCM service import error in mobile_enhanced.py
- **저장소:** https://github.com/rpaakdi1-spec/3-
- **브랜치:** main

## 🎯 서버 배포 단계

### 1단계: 최신 코드 가져오기
```bash
ssh root@139.150.11.99
cd /root/uvis

# 현재 rebase 취소
git rebase --abort

# 원격 저장소의 최신 코드로 동기화
git fetch origin
git reset --hard origin/main

# 최신 코드 확인
git log --oneline -3
```

**예상 출력:**
```
04af91b fix(backend): Fix FCM service import error in mobile_enhanced.py
41c669f docs: Add detailed server deployment instructions for Phase 16
...
```

### 2단계: Backend Docker 이미지 재빌드
```bash
cd /root/uvis

# Backend 컨테이너 중지
docker-compose stop backend

# Backend 이미지 재빌드 (캐시 없이)
docker-compose build --no-cache backend

# Backend 컨테이너 시작
docker-compose up -d backend
```

### 3단계: 서비스 상태 확인
```bash
# 컨테이너 상태 확인 (30초 대기)
sleep 30
docker-compose ps

# Backend 로그 확인
docker-compose logs backend | tail -50
```

**정상 동작 확인:**
- uvis-backend 컨테이너 상태: `Up (healthy)`
- 로그에서 "Application startup complete!" 메시지 확인

### 4단계: Health Check
```bash
# Backend API 헬스 체크
curl http://localhost:8000/api/v1/health

# Frontend 접속 확인
curl -I http://localhost/
```

**예상 출력:**
```json
{
  "status": "healthy",
  "app_name": "Cold Chain Dispatch System",
  "environment": "production"
}
```

## 🔧 트러블슈팅

### Backend가 여전히 unhealthy 상태인 경우

#### Option 1: 전체 재시작
```bash
docker-compose restart backend
sleep 30
docker-compose logs backend | tail -50
```

#### Option 2: 완전 재빌드
```bash
# 모든 컨테이너 중지
docker-compose down

# 전체 이미지 재빌드
docker-compose build --no-cache

# 전체 서비스 시작
docker-compose up -d

# 상태 확인
sleep 60
docker-compose ps
```

#### Option 3: 환경변수 확인
```bash
# Backend .env 파일 확인
cat /root/uvis/.env | grep -E "DATABASE_URL|REDIS_URL|MINIO"
```

**필수 환경변수 확인:**
- `DATABASE_URL=postgresql://uvis_user:uvis_secure_password_2024@db:5432/uvis_db`
- `REDIS_URL=redis://:uvis_redis_secure_2024@redis:6379/0`
- `MINIO_ROOT_USER=admin`
- `MINIO_ROOT_PASSWORD=uvis_minio_secure_2024`
- `S3_ENDPOINT=http://minio:9000`

### Frontend가 unhealthy 상태인 경우

#### Nginx 설정 확인
```bash
# Frontend 컨테이너 내부 Nginx 설정 테스트
docker-compose exec frontend nginx -t

# Frontend 재시작
docker-compose restart frontend
```

#### 로그 확인
```bash
docker-compose logs frontend | tail -50
```

## 🎯 배포 후 테스트

### 1. API 문서 접속
```bash
curl http://139.150.11.99:8000/docs
```
브라우저: http://139.150.11.99:8000/docs

### 2. Frontend 접속
브라우저: http://139.150.11.99

### 3. 주요 기능 테스트
- ✅ 로그인
- ✅ 대시보드
- ✅ 주문 관리
- ✅ 배차 관리
- ✅ 실시간 모니터링
- ✅ Phase 16 기능들:
  - 파일 업로드: http://139.150.11.99/files
  - 실시간 채팅: http://139.150.11.99/chat
  - FCM 푸시 알림 (Frontend에서 알림 권한 허용 필요)

## 📊 최종 확인 체크리스트

- [ ] `git log`로 최신 커밋 확인 (04af91b)
- [ ] Backend 컨테이너 상태: `Up (healthy)`
- [ ] Frontend 컨테이너 상태: `Up (healthy)`
- [ ] MinIO 컨테이너 상태: `Up (healthy)`
- [ ] Database 컨테이너 상태: `Up (healthy)`
- [ ] Redis 컨테이너 상태: `Up (healthy)`
- [ ] Health check 성공: `curl http://localhost:8000/api/v1/health`
- [ ] Frontend 접속 성공: `curl -I http://localhost/`
- [ ] API 문서 접속: http://139.150.11.99:8000/docs
- [ ] 메인 페이지 접속: http://139.150.11.99
- [ ] 로그인 기능 정상 동작

## 🔄 롤백 절차 (필요시)

문제가 발생하면 이전 버전으로 롤백:
```bash
cd /root/uvis

# 이전 커밋으로 롤백 (41c669f)
git reset --hard 41c669f

# Docker 이미지 재빌드
docker-compose build --no-cache backend

# 서비스 재시작
docker-compose up -d backend
```

## 📞 지원

문제가 지속되면 다음 정보를 수집하여 보고:

```bash
# 전체 시스템 상태
docker-compose ps

# Backend 로그 (최근 100줄)
docker-compose logs backend | tail -100

# Frontend 로그 (최근 50줄)
docker-compose logs frontend | tail -50

# 환경변수 확인 (민감 정보 제외)
cat .env | grep -v PASSWORD | grep -v SECRET | grep -v KEY
```

---

**작성일:** 2026-02-27  
**커밋:** 04af91b  
**상태:** ✅ 수정 완료, 배포 대기
