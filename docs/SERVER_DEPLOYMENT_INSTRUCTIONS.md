# 🚀 프로덕션 서버 배포 실행 가이드

## 📋 서버 정보
- **IP**: 139.150.11.99
- **OS**: Ubuntu/CentOS (Docker 지원)
- **현재 실행 중**: UVIS 시스템

---

## ✅ 사전 준비사항

### 1. 서버 접속
```bash
# SSH로 서버 접속
ssh root@139.150.11.99
# 또는
ssh user@139.150.11.99

# 프로젝트 디렉토리로 이동
cd /root/uvis
# 또는
cd ~/uvis
```

### 2. 저장소 최신화
```bash
# 최신 코드 가져오기
git fetch origin
git pull origin main

# 최신 커밋 확인
git log --oneline -5

# 예상 출력:
# 5f5b6fc feat(deploy): Add production deployment scripts and guides
# 8ccae2f docs: Add Phase 16 completion report
# f7e7869 feat(chat): Add complete real-time chat frontend implementation
# a8817df docs: Add comprehensive project status report for February 26
# 92aabe4 fix(frontend): Fix import path for useFCM hook
```

---

## 🔧 Phase 16 배포 단계

### Step 1: 환경 변수 설정 (최우선!)

#### 백엔드 환경 변수 (.env)
```bash
# .env 파일 백업
cp .env .env.backup-$(date +%Y%m%d-%H%M%S)

# .env 파일 편집
nano .env
```

**필수 추가/수정 항목:**
```bash
# ===== MinIO / S3 설정 (Phase 16.2 - 파일 업로드) =====
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=<강력한_비밀번호_입력>  # 반드시 변경!
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001
S3_ENDPOINT=http://minio:9000
S3_BUCKET_NAME=uvis-files
S3_REGION=us-east-1
S3_USE_SSL=false

# ===== Firebase FCM 설정 (Phase 16.1 - 푸시 알림) =====
# 주의: Firebase Console에서 먼저 프로젝트 생성 필요
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@your-project-id.iam.gserviceaccount.com

# ===== 기존 설정 확인 =====
DB_PASSWORD=<현재_설정된_값_확인>
REDIS_PASSWORD=<현재_설정된_값_확인>
JWT_SECRET=<현재_설정된_값_확인>
```

**비밀번호 생성 방법:**
```bash
# 강력한 랜덤 비밀번호 (32자)
openssl rand -base64 32

# JWT Secret (64자 hex)
openssl rand -hex 64
```

#### 프론트엔드 환경 변수 (frontend/.env)
```bash
# frontend/.env 파일 생성
nano frontend/.env
```

**내용:**
```bash
# API URLs
VITE_API_URL=http://139.150.11.99:8000/api/v1
VITE_WS_URL=ws://139.150.11.99:8000/ws

# Firebase FCM (Phase 16.1)
# 주의: Firebase Console에서 웹 앱 추가 후 설정 복사
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef123456
VITE_FIREBASE_VAPID_KEY=your-vapid-key-from-cloud-messaging
```

---

### Step 2: Firebase 프로젝트 설정 (FCM)

Firebase를 사용하지 않으려면 이 단계를 건너뛸 수 있습니다. 하지만 푸시 알림 기능은 작동하지 않습니다.

#### 1. Firebase Console 접속
```
URL: https://console.firebase.google.com
```

#### 2. 새 프로젝트 생성
1. "프로젝트 추가" 클릭
2. 프로젝트 이름: `uvis-dispatch` (또는 원하는 이름)
3. Google Analytics: 선택 사항
4. 프로젝트 생성 완료 대기

#### 3. 웹 앱 추가
1. 프로젝트 개요 > 웹 앱 추가 (</> 아이콘)
2. 앱 닉네임: `UVIS Web`
3. Firebase SDK 설정 정보 **복사** → `frontend/.env`에 입력

#### 4. Cloud Messaging 설정
1. 프로젝트 설정 > Cloud Messaging 탭
2. "웹 푸시 인증서" 섹션
3. "키 쌍 생성" 클릭
4. VAPID 키 **복사** → `frontend/.env`의 `VITE_FIREBASE_VAPID_KEY`

#### 5. Service Account 키 다운로드
1. 프로젝트 설정 > 서비스 계정 탭
2. "새 비공개 키 생성" 클릭
3. JSON 파일 다운로드
4. JSON 내용에서 다음 추출:
   - `project_id` → `FIREBASE_PROJECT_ID`
   - `private_key` → `FIREBASE_PRIVATE_KEY`
   - `client_email` → `FIREBASE_CLIENT_EMAIL`

**주의사항:**
- `FIREBASE_PRIVATE_KEY`는 줄바꿈을 `\n`으로 변환해야 합니다
- 또는 Base64로 인코딩하여 저장

---

### Step 3: 배포 실행

#### 방법 1: 자동 배포 스크립트 (권장)
```bash
# 배포 스크립트 실행
./deploy.sh

# 스크립트가 다음을 자동으로 수행:
# 1. 환경 파일 검증
# 2. Git 저장소 업데이트 (선택)
# 3. 프론트엔드 빌드
# 4. Docker 이미지 빌드
# 5. 컨테이너 시작
# 6. 헬스 체크
# 7. MinIO 버킷 생성 (선택)
```

#### 방법 2: 수동 배포
```bash
# 1. 프론트엔드 빌드
cd frontend
npm install
npm run build
cd ..

# 2. Docker 컨테이너 중지
docker-compose down

# 3. Docker 이미지 빌드 (캐시 없이)
docker-compose build --no-cache

# 4. 컨테이너 시작
docker-compose up -d

# 5. 로그 확인
docker-compose logs -f
```

---

### Step 4: 서비스 확인

```bash
# 컨테이너 상태 확인
docker-compose ps

# 예상 출력 (모두 "Up" 상태여야 함):
# NAME              STATUS
# uvis-backend      Up (healthy)
# uvis-frontend     Up (healthy)
# uvis-db           Up (healthy)
# uvis-redis        Up (healthy)
# uvis-minio        Up (healthy)
# uvis-grafana      Up
# uvis-prometheus   Up

# 헬스 체크
curl http://localhost:8000/api/v1/health
# 예상 출력: {"status":"healthy","app_name":"..."}

curl http://localhost/
# 예상 출력: HTML 페이지
```

---

### Step 5: MinIO 설정

#### 1. MinIO Console 접속
```
URL: http://139.150.11.99:9001
Username: admin (또는 MINIO_ROOT_USER 값)
Password: <MINIO_ROOT_PASSWORD>
```

#### 2. 버킷 생성
1. 왼쪽 메뉴 > "Buckets" 클릭
2. "Create Bucket" 버튼
3. Bucket Name: `uvis-files`
4. Region: `us-east-1`
5. "Create Bucket" 클릭

#### 3. 버킷 확인
```bash
# MinIO Client 설치 (필요시)
wget https://dl.min.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc
chmod +x /usr/local/bin/mc

# MinIO alias 설정
mc alias set local http://localhost:9000 admin <MINIO_ROOT_PASSWORD>

# 버킷 목록 확인
mc ls local/

# 예상 출력:
# [2026-02-26 00:00:00 KST]     0B uvis-files/
```

**또는 자동 생성 (배포 스크립트 사용 시):**
```bash
# deploy.sh 실행 중 "MinIO 버킷을 생성하시겠습니까?" 질문에 'y' 입력
```

---

### Step 6: 통합 테스트 실행

```bash
# 테스트 스크립트 실행
./test-deployment.sh

# 테스트 항목:
# ✓ 인증 시스템
# ✓ 서비스 헬스 체크
# ✓ FCM 푸시 알림 (토큰 등록, 전송)
# ✓ 파일 업로드/다운로드
# ✓ 실시간 채팅 (채팅방 생성, 메시지)
# ✓ UVIS 기존 기능

# 예상 출력:
# ╔════════════════════════════════════════════════════════════╗
# ║                  테스트 결과 요약                          ║
# ╚════════════════════════════════════════════════════════════╝
#   총 테스트: 15
#   통과: 15
#   실패: 0
# ✓ 모든 테스트 통과!
```

---

## 🌐 서비스 접속 URL

배포 완료 후 다음 URL로 접속 가능:

| 서비스 | URL | 설명 |
|--------|-----|------|
| **프론트엔드** | http://139.150.11.99 | 메인 웹 애플리케이션 |
| **백엔드 API** | http://139.150.11.99:8000 | REST API |
| **API 문서** | http://139.150.11.99:8000/docs | Swagger UI |
| **MinIO Console** | http://139.150.11.99:9001 | 파일 스토리지 관리 |
| **Grafana** | http://139.150.11.99:3001 | 모니터링 대시보드 |
| **Prometheus** | http://139.150.11.99:9090 | 메트릭 수집기 |

---

## 🧪 Phase 16 기능 테스트

### 1. FCM 푸시 알림 테스트

#### 브라우저에서:
1. http://139.150.11.99 접속
2. 로그인
3. 대시보드 상단 알림 아이콘 클릭
4. "푸시 알림 활성화" 버튼 클릭
5. 브라우저 권한 허용
6. 성공 메시지 확인: "푸시 알림이 활성화되었습니다! 🔔"

#### API로 테스트 알림 전송:
```bash
# 1. 로그인
TOKEN=$(curl -s -X POST http://139.150.11.99:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' \
  | jq -r '.access_token')

# 2. 테스트 알림 전송
curl -X POST http://139.150.11.99:8000/api/v1/notifications/test \
  -H "Authorization: Bearer $TOKEN"
```

### 2. 파일 업로드 테스트

#### 웹 UI에서:
1. http://139.150.11.99/files 접속
2. "파일 업로드" 탭
3. 파일을 드래그 앤 드롭 또는 "파일 선택"
4. 업로드 진행률 확인
5. "파일 관리" 탭에서 업로드된 파일 확인

#### API로:
```bash
# 이미지 업로드
curl -X POST http://139.150.11.99:8000/api/v1/files/upload-image \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test-image.jpg"

# 응답에서 file_url 확인
```

### 3. 실시간 채팅 테스트

#### 웹 UI에서:
1. http://139.150.11.99/chat 접속
2. 왼쪽 "+" 버튼으로 채팅방 생성
3. 채팅방 이름 입력 → "만들기"
4. 메시지 입력 및 전송
5. 다른 브라우저(또는 시크릿 모드)로 동일 계정 로그인
6. 같은 채팅방 접속
7. 실시간 메시지 수신 확인

---

## ⚠️ 문제 해결

### 컨테이너가 시작되지 않음
```bash
# 로그 확인
docker-compose logs backend
docker-compose logs frontend
docker-compose logs minio

# 특정 컨테이너 재시작
docker-compose restart backend

# 전체 재시작
docker-compose down
docker-compose up -d
```

### MinIO 연결 오류
```bash
# MinIO 상태 확인
docker-compose logs minio

# MinIO 재시작
docker-compose restart minio

# 버킷 재생성
mc mb local/uvis-files --ignore-existing
```

### WebSocket 연결 실패
```bash
# 백엔드 로그에서 WebSocket 관련 오류 확인
docker-compose logs backend | grep -i websocket

# 방화벽 확인
sudo ufw status
sudo ufw allow 8000/tcp
```

### FCM 푸시 알림 실패
```bash
# Firebase 설정 확인
docker-compose exec backend python -c "
import os
print('FIREBASE_PROJECT_ID:', os.getenv('FIREBASE_PROJECT_ID'))
print('FIREBASE_CLIENT_EMAIL:', os.getenv('FIREBASE_CLIENT_EMAIL'))
"

# FCM 초기화 로그 확인
docker-compose logs backend | grep -i firebase
```

---

## 📊 모니터링

### 실시간 로그 모니터링
```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스
docker-compose logs -f backend
docker-compose logs -f minio

# 에러만 필터링
docker-compose logs backend | grep ERROR
```

### 리소스 사용량
```bash
# Docker 컨테이너 리소스
docker stats

# 디스크 사용량
df -h
docker system df
```

### Grafana 대시보드
```
URL: http://139.150.11.99:3001
Username: admin
Password: <GRAFANA_PASSWORD from .env>
```

---

## ✅ 배포 완료 체크리스트

- [ ] Git 저장소 최신화 (`git pull`)
- [ ] .env 파일 설정 (DB, Redis, MinIO, Firebase)
- [ ] frontend/.env 파일 설정 (Firebase)
- [ ] 프론트엔드 빌드 성공
- [ ] Docker 이미지 빌드 성공
- [ ] 모든 컨테이너 "Up (healthy)" 상태
- [ ] MinIO 버킷 생성 완료 (`uvis-files`)
- [ ] 백엔드 헬스 체크 통과 (HTTP 200)
- [ ] 프론트엔드 접근 가능
- [ ] FCM 푸시 알림 테스트 성공
- [ ] 파일 업로드 테스트 성공
- [ ] 실시간 채팅 테스트 성공
- [ ] `./test-deployment.sh` 전체 통과

---

## 🔄 롤백 (필요 시)

```bash
# 이전 커밋으로 돌아가기
git log --oneline -10
git checkout <이전_커밋_해시>

# Docker 재빌드 및 재시작
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📞 지원

문제 발생 시:
1. `docker-compose logs -f` 로그 확인
2. `docs/PRODUCTION_DEPLOYMENT_GUIDE.md` 참조
3. `docs/PHASE_16_COMPLETION_REPORT.md` 참조
4. GitHub Issues 작성

---

**배포 실행 가이드 버전**: 1.0  
**최종 업데이트**: 2026-02-26  
**대상 서버**: 139.150.11.99
