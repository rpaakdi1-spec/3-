# 🚀 시작하기

이 가이드는 Cold Chain System API를 처음 사용하는 개발자를 위한 단계별 안내서입니다.

---

## 📋 사전 요구사항

### 1. 계정 생성

Cold Chain System API를 사용하려면 먼저 계정이 필요합니다.

!!! info "계정 등록"
    계정 등록은 시스템 관리자에게 문의하거나 `/api/v1/auth/register` 엔드포인트를 사용하세요.

### 2. 개발 도구 준비

- **HTTP 클라이언트**: Postman, cURL, 또는 Insomnia
- **IDE/Editor**: VSCode, PyCharm, 또는 Sublime Text
- **터미널**: Linux/Mac 터미널 또는 Windows PowerShell

---

## 🔐 인증 흐름

### 1단계: 계정 등록

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "developer123",
  "email": "developer@example.com",
  "password": "SecurePassword123!",
  "full_name": "홍길동",
  "role": "dispatcher"
}
```

**응답 예시**:
```json
{
  "id": 1,
  "username": "developer123",
  "email": "developer@example.com",
  "full_name": "홍길동",
  "role": "dispatcher",
  "is_active": true,
  "created_at": "2026-01-28T10:00:00Z"
}
```

### 2단계: 로그인

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "developer123",
  "password": "SecurePassword123!"
}
```

**응답 예시**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzA2NDQ4MDAwfQ.signature",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzA3MDUyODAwfQ.signature",
  "token_type": "bearer",
  "expires_in": 3600
}
```

!!! warning "토큰 보관"
    - `access_token`을 안전하게 저장하세요
    - 토큰은 1시간 후 만료됩니다
    - `refresh_token`을 사용하여 새 토큰을 발급받을 수 있습니다

### 3단계: 토큰 사용

모든 보호된 API 요청에 토큰을 포함시킵니다:

```bash
GET /api/v1/analytics/dashboard
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📚 첫 번째 API 호출

### 대시보드 데이터 조회

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/dashboard" \
  -H "Authorization: Bearer {your_access_token}" \
  -H "Content-Type: application/json"
```

**응답 예시**:
```json
{
  "active_dispatches": 15,
  "completed_today": 8,
  "pending_orders": 12,
  "vehicles_in_transit": 10,
  "temperature_alerts": 2,
  "avg_delivery_time_minutes": 45.3,
  "fleet_utilization_percent": 78.5,
  "on_time_delivery_rate": 94.2
}
```

---

## 🧪 테스트 환경

### Swagger UI 사용

가장 쉬운 방법은 내장된 Swagger UI를 사용하는 것입니다:

1. 브라우저에서 [http://localhost:8000/docs](http://localhost:8000/docs) 접속
2. 우측 상단 **Authorize** 버튼 클릭
3. `access_token` 입력 후 **Authorize** 클릭
4. 원하는 API 엔드포인트 선택
5. **Try it out** 버튼 클릭
6. 파라미터 입력 후 **Execute** 버튼 클릭

![Swagger UI Screenshot](assets/swagger-ui-example.png)

### ReDoc 사용

더 깔끔한 문서 뷰를 원한다면:

- [http://localhost:8000/redoc](http://localhost:8000/redoc) 접속

---

## 🛠️ Postman Collection 사용

### 1. Postman Collection 가져오기

1. Postman 앱 실행
2. **Import** 버튼 클릭
3. `postman_collection.json` 파일 선택
4. 컬렉션 가져오기 완료

### 2. 환경 변수 설정

1. Postman에서 **Environments** 탭 선택
2. **New Environment** 클릭
3. 다음 변수 추가:

| Variable | Initial Value | Current Value |
|----------|---------------|---------------|
| `base_url` | `http://localhost:8000` | `http://localhost:8000` |
| `access_token` | (empty) | (로그인 후 토큰) |

### 3. 로그인 요청 실행

1. `Auth > Login` 요청 선택
2. Body 탭에서 사용자 정보 입력
3. **Send** 버튼 클릭
4. 응답에서 `access_token` 복사
5. Environment 변수의 `access_token`에 붙여넣기

이제 모든 요청에 자동으로 토큰이 포함됩니다!

---

## 📖 다음 단계

축하합니다! 이제 API를 사용할 준비가 되었습니다.

다음 문서를 참고하세요:

- [API 레퍼런스](api-reference/index.md) - 모든 엔드포인트 상세 설명
- [주문 생성하기](guides/creating-orders.md) - 주문 생성 가이드
- [배차 최적화](guides/optimizing-dispatch.md) - 배차 최적화 가이드
- [Python 예제](examples/python-examples.md) - Python 코드 예제

---

## ❓ 자주 묻는 질문 (FAQ)

### Q1: 토큰이 만료되면 어떻게 하나요?

`/api/v1/auth/refresh` 엔드포인트를 사용하세요:

```bash
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "{your_refresh_token}"
}
```

### Q2: Rate Limit을 초과하면?

**429 Too Many Requests** 오류가 발생합니다. 잠시 대기 후 재시도하세요.

응답 헤더에서 제한 정보를 확인할 수 있습니다:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1706448000
```

### Q3: HTTPS는 언제 사용하나요?

프로덕션 환경에서는 항상 HTTPS를 사용하세요:
```
https://api.coldchain.com/api/v1/...
```

### Q4: API 버전은 어떻게 관리되나요?

현재 버전은 `/api/v1/` 경로에서 사용 가능합니다. 향후 버전이 출시되면 `/api/v2/`로 제공됩니다.

---

## 🆘 도움이 필요하신가요?

- **문서**: [docs.coldchain.com](https://docs.coldchain.com)
- **이메일**: support@coldchain.com
- **GitHub Issues**: [github.com/your-org/cold-chain/issues](https://github.com/your-org/cold-chain/issues)
