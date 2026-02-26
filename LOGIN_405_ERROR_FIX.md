# 🚨 로그인 405 에러 해결 가이드

## 📊 현재 상황
- ✅ UI 정상 렌더링 (Tailwind v3 적용 완료)
- ❌ 로그인 시도 시 **405 Method Not Allowed** 오류

---

## 🔍 405 에러란?

**HTTP 405 Method Not Allowed**
- 클라이언트가 사용한 HTTP 메서드(GET, POST 등)를 서버가 허용하지 않음
- 예: POST 요청을 보냈는데 서버가 GET만 허용하는 경우

---

## 🎯 로그인 시 발생 가능한 원인

### 1. Backend API 서버 문제
- Backend 서버가 실행되지 않음
- `/api/auth/login` 엔드포인트가 없음
- CORS 설정 문제

### 2. Nginx 라우팅 문제
- `/api/*` 요청이 backend로 프록시되지 않음
- Nginx 설정에서 POST 메서드 차단

### 3. Frontend 코드 문제
- 잘못된 API 엔드포인트
- 잘못된 HTTP 메서드 사용

---

## 🔧 즉시 진단 명령어

```bash
# 1. Backend 컨테이너 상태 확인
docker ps | grep backend

# 2. Backend 로그 확인
docker logs uvis-backend --tail 50

# 3. Nginx 설정 확인
docker exec uvis-frontend cat /etc/nginx/nginx.conf | grep -A 10 "location /api"

# 4. API 엔드포인트 직접 테스트
curl -X POST http://139.150.11.99/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -v

# 5. Frontend에서 사용하는 API URL 확인
grep -r "api/auth/login" /root/uvis/frontend/src/
```

---

## 💡 일반적인 해결 방법

### 해결책 1: Backend 서버 시작
```bash
cd /root/uvis
docker-compose ps
docker-compose up -d backend
docker logs uvis-backend --tail 30
```

### 해결책 2: Nginx 프록시 설정 확인
```bash
# Nginx 설정에 다음이 있어야 함
location /api/ {
    proxy_pass http://backend:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

### 해결책 3: CORS 설정 (Backend)
Backend에서 CORS 허용 필요:
```python
# Python Flask 예시
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
```

---

## 📝 다음 단계

위 진단 명령어를 실행하고 결과를 알려주세요!

특히:
1. `docker ps | grep backend` 결과
2. `docker logs uvis-backend --tail 50` 결과
3. `curl -X POST ...` 결과

이 정보를 바탕으로 정확한 해결책을 제시하겠습니다!
