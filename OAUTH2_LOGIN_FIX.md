# 🔧 OAuth2 로그인 문제 해결

**날짜**: 2026-02-25  
**문제**: 422 Unprocessable Entity - OAuth2 form data vs JSON 불일치

---

## 🔍 문제 분석

### 발견된 사실:
1. ✅ 백엔드 경로: `/api/v1/auth/login` **존재함**
2. ✅ 백엔드 응답: `HTTP 422` (경로는 맞지만 데이터 형식 오류)
3. ❌ 데이터 형식 불일치:
   - 프론트엔드 → JSON: `{"username":"admin","password":"admin123"}`
   - 백엔드 기대 → OAuth2 Form: `username=admin&password=admin123`

### 백엔드 코드:
```python
# app/api/auth.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")
```

OAuth2PasswordBearer는 `application/x-www-form-urlencoded` 형식을 요구합니다.

---

## 🎯 해결책: Nginx 경로 수정

### **현재 Nginx 설정**:
```nginx
location /api/ {
    proxy_pass http://backend:8000/api/v1;  # ❌ 잘못됨
}
```

**문제**: `/api/` → `/api/v1`로 변경하면서 슬래시가 제거됨

### **올바른 설정**:
```nginx
location /api/ {
    proxy_pass http://backend:8000/api/v1/;  # ✅ 끝에 / 추가
}
```

---

## 🛠️ 수정 명령어

```bash
cd /root/uvis/frontend

# Nginx 설정 수정 (끝에 슬래시 추가)
sed -i 's|proxy_pass http://backend:8000/api/v1;|proxy_pass http://backend:8000/api/v1/;|' nginx.conf

# 변경 확인
grep "proxy_pass" nginx.conf

# 배포
docker cp nginx.conf uvis-frontend:/etc/nginx/nginx.conf
docker exec uvis-frontend nginx -t
docker exec uvis-frontend nginx -s reload

# 테스트
curl -X POST http://139.150.11.99/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' -v
```

---

## 📋 프론트엔드 코드 확인 필요

만약 위 방법으로도 422 에러가 계속되면, 프론트엔드 로그인 코드를 확인해야 합니다:

```bash
cd /root/uvis/frontend
grep -r "auth/login" src/ | head -10
cat src/services/api.ts | grep -A 20 "login"
```

### 프론트엔드가 보내야 할 형식:

**현재 (JSON)** - ❌ 작동 안 함:
```typescript
fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
})
```

**수정 필요 (Form Data)** - ✅ 작동:
```typescript
const formData = new URLSearchParams();
formData.append('username', username);
formData.append('password', password);

fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: formData
})
```

---

## ✅ 예상 성공 응답

수정 후 다음과 같은 응답이 나와야 합니다:

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "access_token": "eyJ0eXAiOiJKV1QiLC...",
  "token_type": "bearer"
}
```

---

## 📊 진단 요약

| 항목 | 상태 | 비고 |
|------|------|------|
| 백엔드 경로 | ✅ `/api/v1/auth/login` | 존재함 |
| Nginx 프록시 | ⚠️ 슬래시 누락 | 수정 필요 |
| 데이터 형식 | ❌ JSON vs Form | 확인 필요 |
| 에러 코드 | 422 | 데이터 형식 문제 |

---

## 🚀 다음 단계

1. ✅ Nginx 설정 수정 (슬래시 추가)
2. ✅ 테스트 실행
3. ⏳ 422 에러 계속되면 프론트엔드 코드 확인
4. ⏳ 필요시 프론트엔드 수정 (JSON → Form Data)

---

**생성일**: 2026-02-25  
**관련 문서**: LOGIN_405_DEBUG.md, TAILWIND_V3_DOWNGRADE_RECORD.md
