# 🔧 백엔드 수정사항 배포 가이드

## 📋 수정 내역 요약

### ✅ 완료된 수정사항 (커밋: ef322ee)

1. **Twilio SMS Service** - Optional Dependency로 변경
   - `twilio` 패키지가 없어도 백엔드 시작 가능
   - 환경 변수 없어도 graceful degradation
   - 파일: `backend/app/services/sms_service.py`

2. **Firebase FCM Service** - Optional Dependency로 변경
   - `firebase-admin` 패키지가 없어도 백엔드 시작 가능
   - 환경 변수 없어도 graceful degradation
   - 파일: `backend/app/services/fcm_service.py`

---

## 🚀 배포 절차 (서버: /root/uvis)

### Step 1: 코드 가져오기
```bash
cd /root/uvis
git fetch origin main
git stash  # 로컬 변경사항 임시 저장
git pull origin main
```

### Step 2: 백엔드 재빌드 (권장)
```bash
cd /root/uvis

# 기존 컨테이너 중지 및 제거
docker stop coldchain-backend
docker rm coldchain-backend

# 이미지 재빌드 (캐시 초기화)
docker build --no-cache -t uvis-backend -f backend/Dockerfile backend/

# 새 컨테이너 시작
docker run -d \
  --name coldchain-backend \
  --network uvis_coldchain-network \
  -p 8000:8000 \
  -v /root/uvis/backend:/app \
  -v /root/uvis/.env:/app/.env \
  uvis-backend

# 30초 대기
sleep 30
```

### Step 3: 상태 확인
```bash
# 컨테이너 상태
docker ps | grep coldchain-backend

# 로그 확인 (Uvicorn 시작 메시지 확인)
docker logs --tail=50 coldchain-backend

# 헬스체크
curl -s http://localhost:8000/health

# API 문서 확인
curl -s http://localhost:8000/docs | grep -o "<title>.*</title>"
```

### Step 4: 기대 결과
```
✅ 로그에 이런 메시지가 보여야 합니다:
- "⚠️ Twilio package not installed. SMS service will be disabled."
- "⚠️ Firebase Admin SDK not installed. Push notifications will be disabled."
- "INFO:     Uvicorn running on http://0.0.0.0:8000"
- "INFO:     Application startup complete."

✅ Health check 성공:
- http://localhost:8000/health → {"status": "healthy"}

✅ API 문서 접근 가능:
- http://localhost:8000/docs (Swagger UI)
```

---

## 🔍 트러블슈팅

### 문제 1: 여전히 import 에러 발생
```bash
# 해결: 완전 재빌드
cd /root/uvis
docker stop coldchain-backend
docker rm coldchain-backend
docker rmi uvis-backend  # 이미지 삭제
docker build --no-cache -t uvis-backend -f backend/Dockerfile backend/
# 위 Step 2의 docker run 명령어 다시 실행
```

### 문제 2: 컨테이너가 계속 재시작됨
```bash
# 로그 상세 확인
docker logs -f coldchain-backend

# 만약 DB 연결 에러라면 .env 확인
grep "DATABASE_URL" /root/uvis/.env
```

### 문제 3: Nginx가 502 Bad Gateway 에러
```bash
# 백엔드가 완전히 시작될 때까지 대기 (최대 60초)
sleep 60

# Nginx 재시작
docker restart coldchain-nginx

# Nginx 로그 확인
docker logs --tail=20 coldchain-nginx
```

---

## 📊 현재 프로젝트 상태

### ✅ 완료된 작업
1. **HTTP 수집기 v2.0** (포트 8001)
   - FastAPI 기반
   - 검증 통합 완료
   - 레거시 엔드포인트 지원
   - API 문서: http://localhost:8001/docs

2. **센서 시뮬레이터**
   - 3대 차량 시뮬레이션
   - 10초 간격 데이터 전송
   - HTTP Collector로 데이터 전송

3. **프론트엔드 IoT 통합** (커밋: 5bee784)
   - IoT 센서 대시보드 페이지
   - 센서 상세보기 페이지
   - 알림 센터 페이지
   - API 서비스 레이어
   - 라우팅 및 사이드바 메뉴

4. **백엔드 Optional Dependencies** (커밋: ef322ee)
   - Twilio SMS Service (optional)
   - Firebase FCM Service (optional)

### 🚧 진행 중
- 프론트엔드-백엔드 통합 테스트
- 센서 데이터 실시간 표시 검증

### ⏳ 대기 중
- Nginx 설정 최적화
- 전체 시스템 통합 테스트

---

## 🎯 다음 단계 (배포 후 확인사항)

### 1. 백엔드 정상화 확인
```bash
# Health check
curl http://localhost:8000/health

# API 문서 접근
curl http://localhost:8000/docs

# 로그인 테스트 (프론트엔드에서)
# 브라우저: http://YOUR_SERVER_IP
```

### 2. IoT 센서 시뮬레이터 실행
```bash
cd /root/uvis/iot_sensors
source ../venv_iot/bin/activate
python tests/sensor_simulator.py --vehicles 3 --interval 10
```

### 3. 프론트엔드에서 확인
```
1. 로그인 후 사이드바에서 "IoT 센서 모니터링" 클릭
2. 센서 대시보드 확인
3. 차량 선택 → 센서 상세보기
4. 알림 센터 확인
```

### 4. 통합 테스트
- [ ] 백엔드 /health 응답 확인
- [ ] 백엔드 /docs 접근 확인
- [ ] HTTP 수집기 (8001) 정상 작동 확인
- [ ] 센서 시뮬레이터 → HTTP 수집기 데이터 전송 확인
- [ ] 프론트엔드 IoT 페이지 로딩 확인
- [ ] 센서 데이터 실시간 표시 확인

---

## 📞 문제 발생 시

배포 중 문제가 발생하면 다음 정보를 공유해주세요:

1. **Git pull 결과**
```bash
cd /root/uvis && git pull origin main
```

2. **Docker 컨테이너 상태**
```bash
docker ps
```

3. **백엔드 로그 (최근 50줄)**
```bash
docker logs --tail=50 coldchain-backend
```

4. **Health check 결과**
```bash
curl -v http://localhost:8000/health
```

---

## 💡 참고사항

### Optional Dependencies 동작 방식
- **Twilio**: 패키지가 없으면 SMS 기능만 비활성화, 나머지 시스템은 정상 작동
- **Firebase**: 패키지가 없으면 푸시 알림만 비활성화, 나머지 시스템은 정상 작동

### 로그 메시지 의미
- `⚠️ Twilio package not installed` → 정상 (optional)
- `⚠️ Firebase Admin SDK not installed` → 정상 (optional)
- `INFO: Uvicorn running on http://0.0.0.0:8000` → 성공!

### 필수 확인사항
1. Uvicorn이 정상 시작되었는지
2. /health 엔드포인트가 응답하는지
3. /docs가 접근 가능한지
4. 프론트엔드에서 로그인이 되는지

---

**작성일**: 2026-02-05  
**작성자**: Claude AI Assistant  
**커밋 해시**: ef322ee  
**관련 이슈**: Backend startup failures due to missing optional dependencies
