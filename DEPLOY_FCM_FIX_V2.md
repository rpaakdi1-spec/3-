# 🚀 FCM Import Error 완전 수정 - 서버 재배포

## 📌 두 번째 Import Error 발견 및 수정

### 문제
Backend 시작 시 또 다른 import error 발생:
```python
File "/app/app/api/monitoring.py", line 17, in <module>
    from app.services.notification_service import NotificationService
File "/app/app/services/notification_service.py", line 18, in <module>
    from app.services.fcm_service import fcm_service
ImportError: cannot import name 'fcm_service' from 'app.services.fcm_service'
```

### 수정 완료
- **파일:** `backend/app/services/notification_service.py`
- **수정:** `fcm_service` → `FCMService` (클래스)
- **커밋:** `78c4c99`

---

## 🎯 서버에서 실행할 명령어

```bash
# 1. 프로젝트 디렉토리
cd /root/uvis

# 2. 최신 코드 가져오기
git fetch origin
git reset --hard origin/main

# 3. 최신 커밋 확인 (78c4c99 확인)
git log --oneline -3

# 예상 출력:
# 78c4c99 (HEAD -> main, origin/main) fix(backend): Fix fcm_service import in notification_service.py
# 07f50e5 docs: Add quick deployment reference guide
# 2933c11 docs: Add Phase 16 final deployment status report

# 4. Backend 재빌드
docker-compose stop backend
docker-compose build --no-cache backend
docker-compose up -d backend

# 5. 60초 대기 후 상태 확인
sleep 60
docker-compose ps

# 6. Backend 로그 확인 (에러 없는지 확인)
docker-compose logs backend | tail -50

# 7. Health Check
curl http://localhost:8000/api/v1/health

# 예상 응답:
# {
#   "status": "healthy",
#   "app_name": "Cold Chain Dispatch System",
#   "environment": "production"
# }

# 8. 통합 테스트
./test-deployment.sh
```

---

## ✅ 예상 결과

### 컨테이너 상태
```
NAME            STATUS
uvis-backend    Up (healthy)  ✅
uvis-frontend   Up (healthy)  ✅
uvis-minio      Up (healthy)  ✅
uvis-db         Up (healthy)  ✅
uvis-redis      Up (healthy)  ✅
```

### Backend 로그 (정상)
```
Starting Cold Chain Dispatch System...
Initializing database...
Database initialized successfully
Initializing WebSocket manager...
WebSocket manager initialized
Starting scheduler service...
Scheduler service started
Application startup complete!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 🔧 트러블슈팅

### 만약 또 다른 import error가 발생하면

모든 fcm_service import를 찾아서 확인:
```bash
cd /root/uvis
grep -r "from.*fcm_service import fcm_service" backend/
```

위 명령어 결과를 공유해주시면 추가 수정하겠습니다.

---

**작성:** 2026-02-27  
**최신 커밋:** 78c4c99  
**수정 파일:**
- mobile_enhanced.py (04af91b)
- notification_service.py (78c4c99)
