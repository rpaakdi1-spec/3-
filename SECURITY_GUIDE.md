# 🔒 보안 강화 가이드

**Cold Chain Dispatch System - Security Hardening**

작성일: 2026-01-27  
작성자: GenSpark AI Developer  
버전: 1.0.0

---

## 📚 목차

1. [개요](#개요)
2. [구현된 보안 기능](#구현된-보안-기능)
3. [Rate Limiting](#rate-limiting)
4. [보안 헤더](#보안-헤더)
5. [입력 검증](#입력-검증)
6. [인증 및 권한](#인증-및-권한)
7. [보안 유틸리티](#보안-유틸리티)
8. [베스트 프랙티스](#베스트-프랙티스)

---

## 개요

### 보안 위협

- ❌ **SQL Injection**: 악의적인 SQL 쿼리 주입
- ❌ **XSS (Cross-Site Scripting)**: 악성 스크립트 주입
- ❌ **CSRF (Cross-Site Request Forgery)**: 위조된 요청
- ❌ **DDoS**: 서비스 거부 공격
- ❌ **Brute Force**: 무차별 대입 공격
- ❌ **Open Redirect**: 악의적인 URL 리다이렉트
- ❌ **Path Traversal**: 디렉토리 탐색 공격

### 구현된 방어 기능

- ✅ **Rate Limiting** - DDoS, Brute Force 방지
- ✅ **보안 헤더** - XSS, Clickjacking 방지
- ✅ **입력 검증** - SQL Injection, XSS 방지
- ✅ **JWT 인증** - 안전한 인증
- ✅ **CORS 설정** - 허용된 도메인만 접근
- ✅ **HTTPS 강제** - 암호화된 통신
- ✅ **요청 로깅** - 보안 감사

---

## 구현된 보안 기능

### 1. Rate Limiting

**목적**: DDoS 및 Brute Force 공격 방지

**설정**:
- 기본: 분당 60 요청
- IP 주소 기반 제한
- 제외 경로: `/health`, `/docs`, `/redoc`

**응답 헤더**:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1706356800
```

**초과 시 응답**:
```json
{
  "detail": "Too many requests. Please try again later.",
  "retry_after": 60
}
```
**HTTP Status**: 429 Too Many Requests

### 2. 보안 헤더

**구현된 헤더**:

| 헤더 | 값 | 설명 |
|------|-----|------|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | HTTPS 강제 |
| `X-Content-Type-Options` | `nosniff` | MIME 타입 스니핑 방지 |
| `X-Frame-Options` | `DENY` | Clickjacking 방지 |
| `X-XSS-Protection` | `1; mode=block` | XSS 필터 활성화 |
| `Content-Security-Policy` | `default-src 'self'; ...` | 리소스 로딩 제한 |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Referer 헤더 제어 |
| `Permissions-Policy` | `geolocation=(), ...` | 브라우저 기능 제한 |

### 3. 입력 검증

**SQL Injection 패턴 감지**:
```python
# 감지 패턴
- SELECT, INSERT, UPDATE, DELETE, DROP
- --, ;, /*, */
- OR ... =, AND ... =
- UNION SELECT
```

**XSS 패턴 감지**:
```python
# 감지 패턴
- <script>...</script>
- <iframe>
- javascript:
- on...= (이벤트 핸들러)
- <embed>, <object>
```

**자동 정제**:
```python
# HTML 이스케이프
< → &lt;
> → &gt;
& → &amp;
" → &quot;
' → &#x27;
```

### 4. 요청 로깅

**로그 내용**:
- 요청 메서드 및 경로
- 클라이언트 IP 주소
- 처리 시간
- 응답 상태 코드
- 에러 정보

**로그 예시**:
```
2026-01-27 23:00:00 | INFO | Request: GET /api/v1/orders from 192.168.1.100
2026-01-27 23:00:00 | INFO | Response: 200 in 0.045s
```

---

## Rate Limiting

### 사용법

**기본 설정** (분당 60 요청):
```python
from app.middleware.security import RateLimitMiddleware

app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
```

**커스텀 설정**:
```python
# 분당 100 요청
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# 분당 30 요청 (엄격)
app.add_middleware(RateLimitMiddleware, requests_per_minute=30)
```

### 제외 경로

자동으로 제외되는 경로:
- `/health`
- `/docs`
- `/redoc`
- `/openapi.json`

### 응답 헤더 확인

```bash
curl -I http://localhost:8000/api/v1/orders

HTTP/1.1 200 OK
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1706356800
```

---

## 보안 헤더

### HTTPS 강제 (프로덕션)

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

- 1년 동안 HTTPS만 허용
- 모든 서브도메인 포함

### XSS 방지

```
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
```

- MIME 타입 스니핑 차단
- XSS 필터 활성화

### Clickjacking 방지

```
X-Frame-Options: DENY
```

- iframe 내 로드 차단

### Content Security Policy

```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; ...
```

- 자체 리소스만 허용
- 인라인 스크립트 허용 (제한적)

---

## 입력 검증

### 보안 유틸리티 사용

```python
from app.core.security import security_utils

# XSS 정제
safe_text = security_utils.sanitize_input(user_input)

# SQL Injection 검증
is_safe = security_utils.validate_sql_input(query_string)
if not is_safe:
    raise HTTPException(status_code=400, detail="Invalid input")

# 이메일 검증
if not security_utils.validate_email(email):
    raise HTTPException(status_code=400, detail="Invalid email")

# 전화번호 검증 (한국)
if not security_utils.validate_phone(phone):
    raise HTTPException(status_code=400, detail="Invalid phone number")

# 사업자 번호 검증
if not security_utils.validate_business_number(business_number):
    raise HTTPException(status_code=400, detail="Invalid business number")
```

### 비밀번호 강도 검증

```python
is_valid, errors = security_utils.validate_password_strength(password)

if not is_valid:
    return {"errors": errors}

# 요구사항:
# - 최소 8자
# - 대문자 1개 이상
# - 소문자 1개 이상
# - 숫자 1개 이상
# - 특수문자 1개 이상
```

### 민감 데이터 마스킹

```python
# 카드 번호 마스킹
masked_card = security_utils.mask_sensitive_data("1234567890123456", visible_chars=4)
# 결과: "************3456"

# 전화번호 마스킹
masked_phone = security_utils.mask_sensitive_data("01012345678", visible_chars=4)
# 결과: "*******5678"
```

### 파일명 정제

```python
# Path Traversal 방지
safe_filename = security_utils.sanitize_filename("../../etc/passwd")
# 결과: "etcpasswd"

safe_filename = security_utils.sanitize_filename("<script>alert('xss')</script>.pdf")
# 결과: "scriptalertxssscript.pdf"
```

---

## 인증 및 권한

### JWT 토큰 인증

**토큰 생성**:
```python
from app.core.auth import create_access_token

access_token = create_access_token(data={"sub": user.username})
```

**토큰 검증**:
```python
from app.core.auth import get_current_active_user
from fastapi import Depends

@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"user": current_user.username}
```

### 권한 확인

```python
from app.core.auth import require_admin

@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin)
):
    # 관리자만 접근 가능
    pass
```

---

## 보안 유틸리티

### CSRF 토큰

```python
# CSRF 토큰 생성
csrf_token = security_utils.generate_csrf_token()

# 세션에 저장
session["csrf_token"] = csrf_token

# 검증
if request_csrf_token != session["csrf_token"]:
    raise HTTPException(status_code=403, detail="CSRF token validation failed")
```

### 안전한 리다이렉트

```python
# Open Redirect 방지
redirect_url = request.query_params.get("next")
allowed_hosts = ["example.com", "www.example.com"]

if security_utils.is_safe_redirect_url(redirect_url, allowed_hosts):
    return RedirectResponse(url=redirect_url)
else:
    return RedirectResponse(url="/")
```

### 보안 이벤트 로깅

```python
# 보안 이벤트 기록
security_utils.log_security_event(
    event_type="failed_login",
    user_id=user.id,
    ip_address=request.client.host,
    details={"attempts": 3}
)
```

---

## 베스트 프랙티스

### ✅ DO

1. **항상 HTTPS 사용**
   ```python
   # 프로덕션 환경
   if settings.APP_ENV == "production":
       assert request.url.scheme == "https"
   ```

2. **입력 검증**
   ```python
   # 모든 사용자 입력 검증
   safe_input = security_utils.sanitize_input(user_input)
   ```

3. **비밀번호 해싱**
   ```python
   # bcrypt 사용 (이미 구현됨)
   from passlib.context import CryptContext
   pwd_context = CryptContext(schemes=["bcrypt"])
   hashed = pwd_context.hash(password)
   ```

4. **Rate Limiting 설정**
   ```python
   # 민감한 엔드포인트는 더 엄격하게
   @app.post("/login")
   @limiter.limit("5/minute")  # 분당 5회만 허용
   async def login():
       pass
   ```

5. **보안 헤더 확인**
   ```bash
   # 헤더 확인
   curl -I https://api.example.com
   ```

6. **정기적인 보안 감사**
   ```bash
   # 로그 확인
   grep "Security Event" logs/app.log
   ```

### ❌ DON'T

1. **평문 비밀번호 저장 금지**
   ```python
   # ❌ 절대 금지
   user.password = "plaintext_password"
   
   # ✅ 항상 해싱
   user.hashed_password = pwd_context.hash(password)
   ```

2. **민감 정보 로깅 금지**
   ```python
   # ❌ 금지
   logger.info(f"Password: {password}")
   
   # ✅ 마스킹
   logger.info(f"Password: {'*' * len(password)}")
   ```

3. **클라이언트 입력 신뢰 금지**
   ```python
   # ❌ 위험
   db.execute(f"SELECT * FROM users WHERE id = {user_input}")
   
   # ✅ 안전 (ORM 사용)
   db.query(User).filter(User.id == user_input).first()
   ```

4. **에러 메시지에 민감 정보 포함 금지**
   ```python
   # ❌ 금지
   raise HTTPException(detail=f"Query failed: {sql_query}")
   
   # ✅ 일반적인 메시지
   raise HTTPException(detail="Operation failed")
   ```

---

## 보안 체크리스트

### 배포 전 확인사항

- [ ] HTTPS 강제 활성화
- [ ] Rate Limiting 설정
- [ ] 보안 헤더 확인
- [ ] 입력 검증 활성화
- [ ] JWT 토큰 만료 시간 설정
- [ ] CORS 허용 도메인 제한
- [ ] 민감 정보 마스킹
- [ ] 로그 레벨 확인 (프로덕션: INFO)
- [ ] 디버그 모드 비활성화
- [ ] 환경 변수 보안 (`.env` 파일)

### 정기 점검

- [ ] 취약점 스캔
- [ ] 의존성 업데이트
- [ ] 로그 검토
- [ ] Rate Limit 조정
- [ ] 인증서 갱신

---

## 보안 테스트

### SQL Injection 테스트

```bash
# 테스트 (차단되어야 함)
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"product_name": "test OR 1=1"}'
```

### XSS 테스트

```bash
# 테스트 (이스케이프되어야 함)
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"product_name": "<script>alert(\"xss\")</script>"}'
```

### Rate Limiting 테스트

```bash
# 61회 요청 (마지막 요청 차단되어야 함)
for i in {1..61}; do
  curl http://localhost:8000/api/v1/orders
done
```

---

## 참고 자료

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Security Headers](https://securityheaders.com/)

---

**작성일**: 2026-01-27  
**버전**: 1.0.0  
**상태**: ✅ 완료
