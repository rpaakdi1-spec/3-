# Cold Chain System API Documentation

![Cold Chain Logo](assets/logo.png)

## 🎯 개요

**Cold Chain System**은 AI 기반 냉동·냉장 화물 배차 시스템입니다. 이 문서는 RESTful API의 완전한 레퍼런스와 사용 가이드를 제공합니다.

### 주요 기능

- 🚚 **지능형 배차 최적화** - Google OR-Tools 기반 VRP 솔루션
- 📊 **실시간 모니터링** - GPS 추적 및 온도 센서 통합
- 🤖 **AI/ML 예측** - 배송 시간 및 수요 예측
- 📱 **모바일 앱** - React Native 기반 iOS/Android 앱
- 🔔 **FCM 푸시 알림** - 실시간 알림 시스템
- 📈 **분석 대시보드** - 18개 분석 API 엔드포인트
- 🔒 **엔터프라이즈 보안** - 2FA, 감사 로그, Rate Limiting

---

## 🚀 빠른 시작

### 1. 계정 생성 및 인증

먼저 API 키를 발급받아야 합니다:

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "your_username",
  "email": "your@email.com",
  "password": "SecurePass123!"
}
```

### 2. 로그인 및 토큰 받기

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "SecurePass123!"
}
```

응답:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 3. API 호출하기

인증 토큰을 사용하여 API를 호출합니다:

```bash
GET /api/v1/analytics/dashboard
Authorization: Bearer {access_token}
```

---

## 📚 문서 구조

### [API 레퍼런스](api-reference/index.md)
모든 API 엔드포인트의 상세한 설명, 요청/응답 예제

### [가이드](guides/creating-orders.md)
실무 시나리오별 단계별 가이드

### [예제 코드](examples/python-examples.md)
Python, JavaScript, cURL로 작성된 실제 예제

### [배포 및 운영](deployment/production.md)
프로덕션 환경 배포 및 모니터링 가이드

---

## 🔗 유용한 링크

- **API 문서 (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API 문서 (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI Schema**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
- **GitHub Repository**: [https://github.com/your-org/cold-chain](https://github.com/your-org/cold-chain)
- **Postman Collection**: [Download](https://link-to-postman-collection)

---

## 📊 API 통계

현재 버전: **v2.0.0**

| 카테고리 | 엔드포인트 수 |
|---------|-------------|
| 인증 (Auth) | 8 |
| 분석 (Analytics) | 18 |
| ML 모델 | 7 |
| FCM 알림 | 4 |
| 실시간 모니터링 | 3 |
| 성능 (Performance) | 6 |
| 보안 (Security) | 8 |
| 리포트 | 12 |
| **총합** | **66+** |

---

## 💡 기술 스택

### Backend
- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL 15 + SQLAlchemy 2.0
- **Cache**: Redis 7 + Hiredis
- **ML**: scikit-learn, Prophet, OR-Tools
- **Monitoring**: Prometheus, Sentry

### Frontend
- **Framework**: React 18 + TypeScript
- **State**: Redux Toolkit
- **Charts**: Recharts
- **Maps**: Google Maps API

### Mobile
- **Framework**: React Native 0.73 + Expo 50
- **Push**: Firebase Cloud Messaging (FCM)

---

## 🛠️ 개발 환경 설정

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+

### Backend 설정

```bash
# Clone repository
git clone https://github.com/your-org/cold-chain.git
cd cold-chain/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\\Scripts\\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend 설정

```bash
cd ../frontend
npm install
npm run dev
```

서버 접속: [http://localhost:5173](http://localhost:5173)

---

## 🔐 인증

모든 보호된 API는 **Bearer Token** 인증이 필요합니다.

### 토큰 포함 방법

```
Authorization: Bearer {your_access_token}
```

### 토큰 만료

- **Access Token**: 1시간
- **Refresh Token**: 7일

토큰이 만료되면 `/api/v1/auth/refresh` 엔드포인트를 사용하여 갱신하세요.

---

## ⚠️ Rate Limiting

API 호출 제한:

| 엔드포인트 | 제한 |
|----------|-----|
| `/api/v1/auth/login` | 5 requests/minute |
| 읽기 (GET) | 100 requests/minute |
| 쓰기 (POST/PUT/DELETE) | 30 requests/minute |

제한 초과 시 **429 Too Many Requests** 응답이 반환됩니다.

---

## 📞 지원

문제가 발생하거나 질문이 있으신가요?

- **이슈 리포트**: [GitHub Issues](https://github.com/your-org/cold-chain/issues)
- **이메일**: support@coldchain.com
- **문서**: [docs.coldchain.com](https://docs.coldchain.com)

---

## 📝 라이선스

이 프로젝트는 [MIT License](LICENSE)로 제공됩니다.

---

**마지막 업데이트**: 2026-01-28  
**문서 버전**: 2.0.0
