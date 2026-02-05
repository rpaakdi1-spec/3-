# 🚀 서버 배포 수정 - 실행 가이드

## 📋 현재 상황

### ❌ 문제점
1. **Backend**: `unhealthy` 상태 (port 8000은 열려있지만 health check 실패)
2. **Nginx**: `unhealthy` 상태, 502 Bad Gateway
3. **Frontend**: port 5173 접근 불가
4. **Database**: ✅ healthy
5. **Redis**: ✅ healthy

### 🎯 목표
- Backend를 `healthy` 상태로 만들기
- Nginx 502 오류 해결
- 프론트엔드 정상 접근 가능하도록 수정
- IoT 센서 모니터링 UI 정상 작동 확인

---

## ⚡ 빠른 해결 방법 (권장)

### 서버에서 실행할 명령어

```bash
cd /root/uvis

# 1. 최신 코드 가져오기
git fetch origin genspark_ai_developer
git checkout genspark_ai_developer
git pull origin genspark_ai_developer

# 2. 자동 수정 스크립트 실행
chmod +x SERVER_FIX_DEPLOYMENT.sh
./SERVER_FIX_DEPLOYMENT.sh
```

### 스크립트가 수행하는 작업

1. **컨테이너 정리**: 기존 충돌하는 컨테이너 모두 제거
2. **.env 검증**: 
   - `SECRET_KEY` 자동 생성 (없는 경우)
   - `DB_PASSWORD` 설정 확인
   - `DATABASE_URL` 구성
   - NAVER_MAP API 키 플레이스홀더 추가
3. **Docker 재빌드**: `--no-cache` 옵션으로 완전 재빌드
4. **서비스 시작**: 올바른 순서로 서비스 시작
   - DB/Redis → Backend → Frontend/Nginx
5. **Health Check**: 모든 서비스 건강 상태 확인

### 예상 실행 시간
- 전체: 약 **5-8분**
  - 이미지 빌드: 3-5분
  - 서비스 안정화: 1-2분
  - Health check: 30초

---

## 📊 성공 확인 방법

### 1. 컨테이너 상태 확인

```bash
docker-compose ps
```

**예상 출력**:
```
NAME              STATUS                    PORTS
uvis-backend      Up (healthy)              0.0.0.0:8000->8000/tcp
uvis-db           Up (healthy)              0.0.0.0:5432->5432/tcp
uvis-redis        Up (healthy)              0.0.0.0:6379->6379/tcp
uvis-frontend     Up                        3000/tcp
uvis-nginx        Up                        0.0.0.0:80->80/tcp
```

### 2. Backend Health Check

```bash
curl -s http://localhost:8000/health
```

**예상 출력**:
```json
{
  "status": "healthy",
  "app_name": "Cold Chain Dispatch System",
  "environment": "production"
}
```

### 3. API 문서 확인

```bash
curl -s http://localhost:8000/docs | grep -o "<title>.*</title>"
```

**예상 출력**:
```html
<title>Cold Chain Dispatch System - Swagger UI</title>
```

### 4. 프론트엔드 접근

브라우저에서:
1. `http://YOUR_SERVER_IP` 접속
2. 로그인 페이지 확인
3. 로그인 후 사이드바에서 **"IoT 센서 모니터링"** 메뉴 확인
4. IoT 센서 대시보드 접근: `/iot/sensors`

---

## 🔧 문제가 지속되는 경우

### 수동 해결 방법

상세한 트러블슈팅 가이드는 `DEPLOYMENT_TROUBLESHOOTING.md` 파일을 참조하세요.

#### 간단 체크리스트

1. **환경변수 확인**:
```bash
grep -E "^SECRET_KEY=|^DB_PASSWORD=|^DATABASE_URL=" .env
# 모두 설정되어 있어야 함
```

2. **컨테이너 로그 확인**:
```bash
# Backend 로그
docker-compose logs backend | tail -100

# Nginx 로그
docker-compose logs nginx | tail -50

# 오류 메시지 찾기
docker-compose logs backend | grep -i "error\|failed\|exception"
```

3. **네트워크 연결 테스트**:
```bash
# Backend에서 DB 연결
docker exec uvis-backend nc -zv db 5432

# Nginx에서 Backend 연결
docker exec uvis-nginx nc -zv backend 8000
```

4. **포트 충돌 확인**:
```bash
# 사용 중인 포트 확인
netstat -tuln | grep -E ":(80|8000|5432|6379) "
```

---

## 📦 새로 추가된 파일

### 1. `SERVER_FIX_DEPLOYMENT.sh`
- 자동 배포 수정 스크립트
- .env 검증 및 수정
- Docker 컨테이너 재시작
- Health check 자동 수행

### 2. `DEPLOYMENT_TROUBLESHOOTING.md`
- 상세한 트러블슈팅 가이드
- 문제별 해결 방법
- 수동 수정 단계
- 고급 디버깅 기법

### 3. `fix_env.sh` (이전에 추가됨)
- .env 파일 간단 수정용
- 기본 환경변수만 설정

---

## 🎯 권장 실행 순서

### Option 1: 자동 스크립트 (권장)
```bash
cd /root/uvis
git fetch origin genspark_ai_developer
git checkout genspark_ai_developer
git pull origin genspark_ai_developer
chmod +x SERVER_FIX_DEPLOYMENT.sh
./SERVER_FIX_DEPLOYMENT.sh
```

### Option 2: 단계별 수동 실행
자세한 내용은 `DEPLOYMENT_TROUBLESHOOTING.md` 참조

---

## 📝 Pull Request 업데이트

**PR 링크**: https://github.com/rpaakdi1-spec/3-/pull/4

### 추가된 내용
1. ✅ IoT 센서 모니터링 UI (이전)
2. ✅ Backend Twilio/Firebase 설정 (이전)
3. ✅ 자동 배포 수정 스크립트 (**NEW**)
4. ✅ 상세 트러블슈팅 가이드 (**NEW**)

---

## 🚨 중요 참고사항

### NAVER_MAP API 키
스크립트가 플레이스홀더를 추가합니다:
```bash
NAVER_MAP_CLIENT_ID=your_naver_client_id_here
NAVER_MAP_CLIENT_SECRET=your_naver_client_secret_here
```

**실제 키로 교체 필요**:
1. [네이버 클라우드 플랫폼](https://console.ncloud.com/) 접속
2. Application 등록
3. Client ID와 Secret 발급
4. `.env` 파일에서 플레이스홀더 교체

백엔드는 플레이스홀더로도 시작되지만, 지도 기능은 실제 키가 필요합니다.

### Twilio/Firebase (선택사항)
SMS/Push 알림을 사용하지 않는다면 기본값(빈 문자열)으로 유지하면 됩니다.
백엔드는 이러한 서비스가 없어도 정상 작동합니다.

---

## ✅ 완료 후 확인 사항

- [ ] `docker-compose ps`에서 모든 컨테이너 `Up` 또는 `healthy`
- [ ] `curl http://localhost:8000/health` → `{"status":"healthy"}`
- [ ] `curl http://localhost:8000/docs` → Swagger UI 표시
- [ ] 브라우저에서 `http://YOUR_SERVER_IP` → 로그인 페이지
- [ ] 로그인 후 "IoT 센서 모니터링" 메뉴 접근 가능
- [ ] IoT 센서 대시보드에서 센서 목록 표시

---

## 🆘 추가 지원이 필요한 경우

위의 스크립트를 실행한 후:

```bash
# 시스템 상태 보고서 생성
cd /root/uvis
docker-compose ps > deployment_status.txt
docker-compose logs backend >> deployment_status.txt
docker-compose logs nginx >> deployment_status.txt
grep -E "^SECRET_KEY=|^DB_PASSWORD=|^DATABASE_URL=" .env | sed 's/=.*/=****** (설정됨)/' >> deployment_status.txt

# 결과 확인
cat deployment_status.txt
```

이 파일의 내용을 공유해주시면 추가 디버깅이 가능합니다.

---

## 🎉 예상 결과

모든 것이 성공적으로 완료되면:

```
🎉 배포 수정 스크립트 완료!

✅ 다음 단계:
   1. 위의 헬스체크 결과를 확인하세요
   2. 브라우저에서 http://YOUR_SERVER_IP 접속
   3. 로그인 후 'IoT 센서 모니터링' 메뉴 확인

⚠️  문제가 지속되면:
   - docker-compose logs backend
   - docker-compose logs nginx
   - docker-compose logs frontend
   위 명령어로 상세 로그를 확인하세요
```

**Good luck! 🚀**
