# 🚀 프로덕션 배포 가이드

## 📋 배포 전 체크리스트

### 1. 환경 변수 설정 (.env)

#### 필수 설정 항목
```bash
# ===== 데이터베이스 =====
DB_NAME=uvis_db
DB_USER=uvis_user
DB_PASSWORD=<강력한_비밀번호_생성>  # 필수 변경!
DB_PORT=5432

# ===== Redis =====
REDIS_PASSWORD=<강력한_비밀번호_생성>  # 필수 변경!
REDIS_PORT=6379

# ===== JWT 인증 =====
JWT_SECRET=<64자_이상_랜덤_문자열>  # 필수 변경!

# ===== MinIO / S3 =====
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=<강력한_비밀번호_생성>  # 필수 변경!
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001
S3_ENDPOINT=http://minio:9000
S3_BUCKET_NAME=uvis-files
S3_REGION=us-east-1
S3_USE_SSL=false

# ===== 애플리케이션 =====
APP_ENV=production
DEBUG=false
BACKEND_PORT=8000
FRONTEND_PORT=80

# ===== CORS =====
CORS_ORIGINS=http://139.150.11.99,http://localhost

# ===== Firebase FCM (Phase 16.1) =====
# Firebase Console에서 생성 필요: https://console.firebase.google.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key-base64
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@your-project-id.iam.gserviceaccount.com

# ===== Naver Map API =====
NAVER_MAP_CLIENT_ID=oimsa0yj4k
NAVER_MAP_CLIENT_SECRET=6tHvrcgeJ4HZsAwkKnEvoaMYl51EZguYDk8uAJ5d

# ===== UVIS API =====
UVIS_API_URL=https://s1.u-vis.com/uvisc/InterfaceAction.do
UVIS_SERIAL_KEY=S1910-3A84-4559--CC4
UVIS_ACCESS_KEY_METHOD=GetAccessKeyWithValues
UVIS_ACCESS_KEY_TTL=300

# ===== AI API Keys (선택) =====
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIzaSy...
```

#### 프론트엔드 환경 변수 (frontend/.env)
```bash
# API URLs
VITE_API_URL=http://139.150.11.99:8000/api/v1
VITE_WS_URL=ws://139.150.11.99:8000/ws

# Firebase FCM
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef
VITE_FIREBASE_VAPID_KEY=your-vapid-key
```

---

## 🔐 보안 강화 설정

### 비밀번호 생성 (Linux/Mac)
```bash
# 강력한 랜덤 비밀번호 생성
openssl rand -base64 32

# JWT Secret (64자 이상)
openssl rand -hex 64
```

### Firebase 프로젝트 설정

1. **Firebase Console 접속**
   - https://console.firebase.google.com

2. **새 프로젝트 생성**
   - 프로젝트 이름: UVIS Dispatch System
   - Google Analytics: 선택 사항

3. **Cloud Messaging 활성화**
   - 프로젝트 설정 > Cloud Messaging
   - Server key 확인

4. **웹 앱 추가**
   - 프로젝트 설정 > 일반 > 웹 앱 추가
   - Firebase SDK 설정 정보 복사

5. **Service Account 키 다운로드**
   - 프로젝트 설정 > 서비스 계정
   - "새 비공개 키 생성" 클릭
   - JSON 파일 다운로드
   - `FIREBASE_PRIVATE_KEY`, `FIREBASE_CLIENT_EMAIL` 추출

6. **VAPID 키 생성**
   - Cloud Messaging > 웹 구성
   - 웹 푸시 인증서 생성

---

## 📦 배포 단계

### Step 1: 저장소 업데이트
```bash
cd /home/user/webapp
git pull origin main
```

### Step 2: 환경 변수 설정
```bash
# .env 파일 편집
nano .env

# 프론트엔드 .env 파일 편집
nano frontend/.env
```

### Step 3: 프론트엔드 빌드
```bash
cd frontend
npm install
npm run build
cd ..
```

### Step 4: Docker 이미지 빌드
```bash
# 기존 컨테이너 중지
docker-compose down

# 캐시 없이 새로 빌드
docker-compose build --no-cache

# 또는 개별 빌드
docker-compose build --no-cache backend
docker-compose build --no-cache frontend
```

### Step 5: 컨테이너 시작
```bash
# 모든 서비스 시작
docker-compose up -d

# 모니터링 프로파일 포함 (선택)
docker-compose --profile monitoring up -d

# 로그 확인
docker-compose logs -f
```

### Step 6: 상태 확인
```bash
# 컨테이너 상태
docker-compose ps

# 헬스 체크
curl http://localhost:8000/api/v1/health
curl http://localhost/health

# 개별 서비스 로그
docker-compose logs backend
docker-compose logs frontend
docker-compose logs minio
```

---

## 🗄️ MinIO 초기 설정

### Step 1: MinIO Console 접속
```
URL: http://139.150.11.99:9001
Username: admin (MINIO_ROOT_USER)
Password: <MINIO_ROOT_PASSWORD>
```

### Step 2: 버킷 생성
1. Buckets 메뉴 선택
2. "Create Bucket" 클릭
3. Bucket Name: `uvis-files`
4. Region: `us-east-1`
5. Versioning: 선택 사항
6. Object Locking: 비활성화

### Step 3: 액세스 정책 설정 (선택)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": ["*"]
      },
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::uvis-files/public/*"]
    }
  ]
}
```

### Step 4: 폴더 구조 생성 (자동)
```
uvis-files/
├── uploads/      # 일반 파일
├── images/       # 이미지 파일
├── documents/    # 문서 파일
├── orders/       # 주문 관련
└── vehicles/     # 차량 관련
```

---

## 🧪 기능 테스트

### 1. FCM 푸시 알림 테스트

#### 브라우저 테스트
1. http://139.150.11.99 접속
2. 로그인
3. 대시보드에서 알림 아이콘 클릭
4. "푸시 알림 활성화" 버튼 클릭
5. 브라우저 권한 허용
6. 토큰 등록 확인

#### API 테스트
```bash
# 1. 로그인하여 토큰 받기
TOKEN=$(curl -X POST http://139.150.11.99:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' \
  | jq -r '.access_token')

# 2. FCM 토큰 등록
curl -X POST http://139.150.11.99:8000/api/v1/notifications/register-token \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "test-fcm-token-123",
    "device_type": "web",
    "device_id": "test-device",
    "app_version": "1.0.0"
  }'

# 3. 테스트 알림 전송
curl -X POST http://139.150.11.99:8000/api/v1/notifications/test \
  -H "Authorization: Bearer $TOKEN"
```

### 2. 파일 업로드 테스트

#### 이미지 업로드
```bash
# 테스트 이미지 업로드
curl -X POST http://139.150.11.99:8000/api/v1/files/upload-image \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test-image.jpg"

# 응답 예시
{
  "success": true,
  "file_url": "http://minio:9000/uvis-files/images/2026/02/26/abc123.jpg",
  "file_key": "images/2026/02/26/abc123.jpg",
  "file_size": 1048576,
  "content_type": "image/jpeg"
}
```

#### 파일 목록 조회
```bash
curl -X GET "http://139.150.11.99:8000/api/v1/files/list?folder=images" \
  -H "Authorization: Bearer $TOKEN"
```

#### 파일 다운로드
```bash
curl -X GET "http://139.150.11.99:8000/api/v1/files/download/images/2026/02/26/abc123.jpg" \
  -H "Authorization: Bearer $TOKEN" \
  -o downloaded-image.jpg
```

### 3. 실시간 채팅 테스트

#### 채팅방 생성
```bash
curl -X POST http://139.150.11.99:8000/api/v1/chat/rooms \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "테스트 채팅방",
    "description": "배포 테스트용 채팅방"
  }'

# 응답에서 room_id 확인
```

#### WebSocket 연결 테스트 (브라우저)
1. http://139.150.11.99/chat 접속
2. 채팅방 선택
3. 메시지 전송 테스트
4. 다른 브라우저/시크릿 모드로 동시 접속
5. 실시간 메시지 수신 확인

#### WebSocket 연결 테스트 (wscat)
```bash
# wscat 설치 (필요시)
npm install -g wscat

# WebSocket 연결
wscat -c "ws://139.150.11.99:8000/api/v1/chat/ws/1?token=$TOKEN"

# 메시지 전송
{"type":"message","data":{"content":"테스트 메시지","message_type":"text"}}

# 타이핑 전송
{"type":"typing","data":{"is_typing":true}}
```

---

## 📊 모니터링 및 로그

### Docker 로그 확인
```bash
# 실시간 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f minio

# 최근 100줄
docker-compose logs --tail=100 backend
```

### 애플리케이션 로그
```bash
# 백엔드 로그
tail -f backend/logs/app.log

# 에러 로그 필터링
grep "ERROR" backend/logs/app.log
```

### 시스템 리소스 모니터링
```bash
# Docker 리소스 사용량
docker stats

# 디스크 사용량
df -h

# 볼륨 크기
docker system df -v
```

### Grafana 대시보드 (선택)
```
URL: http://139.150.11.99:3001
Username: admin
Password: <GRAFANA_PASSWORD>
```

---

## ⚠️ 트러블슈팅

### 문제: 컨테이너가 시작되지 않음
```bash
# 로그 확인
docker-compose logs <service-name>

# 컨테이너 재시작
docker-compose restart <service-name>

# 강제 재생성
docker-compose up -d --force-recreate <service-name>
```

### 문제: MinIO 연결 오류
```bash
# MinIO 상태 확인
docker-compose exec minio curl http://localhost:9000/minio/health/live

# MinIO 재시작
docker-compose restart minio

# 버킷 생성 확인
docker-compose exec minio mc ls local/
```

### 문제: WebSocket 연결 실패
```bash
# 백엔드 로그 확인
docker-compose logs backend | grep -i websocket

# 방화벽 확인 (서버)
sudo ufw status
sudo ufw allow 8000/tcp

# Nginx 설정 확인 (사용 시)
nginx -t
```

### 문제: FCM 푸시 알림 실패
```bash
# Firebase 설정 확인
docker-compose exec backend python -c "
import os
print('FIREBASE_PROJECT_ID:', os.getenv('FIREBASE_PROJECT_ID'))
print('FIREBASE_CLIENT_EMAIL:', os.getenv('FIREBASE_CLIENT_EMAIL'))
"

# FCM 서비스 초기화 로그
docker-compose logs backend | grep -i fcm
```

### 문제: 데이터베이스 연결 오류
```bash
# PostgreSQL 상태 확인
docker-compose exec db pg_isready -U uvis_user

# 데이터베이스 접속 테스트
docker-compose exec db psql -U uvis_user -d uvis_db -c "SELECT version();"

# 연결 정보 확인
docker-compose exec backend env | grep DATABASE_URL
```

---

## 🔄 롤백 절차

### Docker 이미지 롤백
```bash
# 이전 버전 확인
docker images | grep uvis

# 특정 버전으로 롤백
docker tag uvis-backend:previous uvis-backend:latest
docker-compose up -d backend

# Git 커밋으로 롤백
git log --oneline
git checkout <commit-hash>
docker-compose build --no-cache
docker-compose up -d
```

---

## ✅ 배포 완료 체크리스트

- [ ] 환경 변수 모두 설정 완료
- [ ] Docker 이미지 빌드 성공
- [ ] 모든 컨테이너 정상 실행 (docker-compose ps)
- [ ] 헬스 체크 통과 (백엔드, 프론트엔드)
- [ ] MinIO 버킷 생성 완료
- [ ] FCM 푸시 알림 테스트 성공
- [ ] 파일 업로드/다운로드 테스트 성공
- [ ] 실시간 채팅 테스트 성공
- [ ] API 엔드포인트 접근 가능
- [ ] 프론트엔드 UI 정상 표시
- [ ] WebSocket 연결 정상
- [ ] 로그 정상 기록
- [ ] 모니터링 대시보드 접근 가능 (선택)

---

## 📞 지원

배포 중 문제가 발생하면:
1. 로그 확인: `docker-compose logs -f`
2. 문서 참조: `/docs` 디렉토리
3. GitHub Issues 작성

---

**배포 가이드 버전**: 1.0  
**최종 업데이트**: 2026-02-26
