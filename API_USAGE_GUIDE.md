# API 사용 가이드 - Cold Chain Dispatch System

시스템 API 통합을 위한 개발자 가이드입니다.

## 📋 목차

1. [API 개요](#api-개요)
2. [인증](#인증)
3. [주요 엔드포인트](#주요-엔드포인트)
4. [에러 처리](#에러-처리)
5. [예제 코드](#예제-코드)

---

## 🌐 API 개요

### Base URL
```
Production: https://your-domain.com/api/v1
Development: http://localhost:8000/api/v1
```

### API 문서
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 데이터 형식
- **요청**: JSON (Content-Type: application/json)
- **응답**: JSON
- **문자 인코딩**: UTF-8
- **날짜 형식**: ISO 8601 (예: "2026-01-27T10:30:00Z")

---

## 🔐 인증

### JWT 토큰 기반 인증

#### 1. 로그인 및 토큰 발급
```bash
POST /auth/login

# 요청
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'

# 응답
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### 2. 인증된 요청
```bash
# Authorization 헤더에 Bearer 토큰 포함
curl -X GET "http://localhost:8000/api/v1/orders" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 3. 토큰 갱신
```bash
POST /auth/refresh

curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📡 주요 엔드포인트

### 주문 관리 (Orders)

#### 주문 목록 조회
```bash
GET /orders

# 요청
curl -X GET "http://localhost:8000/api/v1/orders?skip=0&limit=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 응답
{
  "total": 150,
  "items": [
    {
      "id": 1,
      "order_number": "ORD20260127001",
      "client_id": 10,
      "client_name": "A 거래처",
      "pickup_address": "서울특별시 강남구...",
      "delivery_address": "부산광역시 해운대구...",
      "cargo_type": "frozen",
      "temperature_range": "-18°C ~ -15°C",
      "weight_kg": 500.0,
      "status": "pending",
      "created_at": "2026-01-27T10:00:00Z"
    }
  ]
}
```

#### 주문 생성
```bash
POST /orders

# 요청
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 10,
    "pickup_address": "서울특별시 강남구 테헤란로 123",
    "pickup_latitude": 37.4979,
    "pickup_longitude": 127.0276,
    "delivery_address": "부산광역시 해운대구 센텀중앙로 79",
    "delivery_latitude": 35.1688,
    "delivery_longitude": 129.1315,
    "cargo_type": "frozen",
    "temperature_min": -18.0,
    "temperature_max": -15.0,
    "weight_kg": 500.0,
    "volume_cbm": 2.5,
    "desired_pickup_time": "2026-01-28T09:00:00Z",
    "desired_delivery_time": "2026-01-28T18:00:00Z",
    "special_instructions": "취급 주의"
  }'

# 응답
{
  "id": 151,
  "order_number": "ORD20260127151",
  "status": "pending",
  "created_at": "2026-01-27T14:30:00Z"
}
```

#### 주문 상세 조회
```bash
GET /orders/{order_id}

curl -X GET "http://localhost:8000/api/v1/orders/151" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 주문 수정
```bash
PUT /orders/{order_id}

curl -X PUT "http://localhost:8000/api/v1/orders/151" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "weight_kg": 550.0,
    "special_instructions": "취급 주의 - 깨지기 쉬움"
  }'
```

#### 주문 취소
```bash
DELETE /orders/{order_id}

curl -X DELETE "http://localhost:8000/api/v1/orders/151" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 배차 관리 (Dispatches)

#### 자동 배차
```bash
POST /dispatches/auto

# 요청
curl -X POST "http://localhost:8000/api/v1/dispatches/auto" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 151
  }'

# 응답
{
  "id": 201,
  "dispatch_number": "DIS20260127201",
  "order_id": 151,
  "vehicle_id": 5,
  "driver_id": 12,
  "estimated_departure": "2026-01-28T09:00:00Z",
  "estimated_arrival": "2026-01-28T18:30:00Z",
  "distance_km": 400.5,
  "estimated_duration_minutes": 390,
  "status": "assigned"
}
```

#### 수동 배차
```bash
POST /dispatches/manual

curl -X POST "http://localhost:8000/api/v1/dispatches/manual" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 151,
    "vehicle_id": 5,
    "driver_id": 12,
    "estimated_departure": "2026-01-28T09:00:00Z"
  }'
```

#### 배차 현황 조회
```bash
GET /dispatches/status

curl -X GET "http://localhost:8000/api/v1/dispatches/status?status=in_progress" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 배차 상태 업데이트
```bash
PATCH /dispatches/{dispatch_id}/status

curl -X PATCH "http://localhost:8000/api/v1/dispatches/201/status" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "latitude": 37.5665,
    "longitude": 126.9780,
    "notes": "출발하였습니다"
  }'
```

### 배송 추적 (Delivery Tracking)

#### 추적 링크 생성
```bash
POST /delivery-tracking

# 요청
curl -X POST "http://localhost:8000/api/v1/delivery-tracking" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dispatch_id": 201
  }'

# 응답
{
  "tracking_number": "TRK20260127001ABC",
  "tracking_url": "https://your-domain.com/tracking/TRK20260127001ABC",
  "qr_code_url": "https://your-domain.com/api/v1/delivery-tracking/TRK20260127001ABC/qr",
  "expires_at": "2026-02-27T14:30:00Z"
}
```

#### 배송 현황 조회 (공개 API - 인증 불필요)
```bash
GET /delivery-tracking/{tracking_number}

# 요청
curl -X GET "http://localhost:8000/api/v1/delivery-tracking/TRK20260127001ABC"

# 응답
{
  "tracking_number": "TRK20260127001ABC",
  "order_number": "ORD20260127151",
  "status": "in_progress",
  "current_location": {
    "latitude": 37.5665,
    "longitude": 126.9780,
    "address": "서울특별시 중구..."
  },
  "estimated_arrival": "2026-01-28T18:30:00Z",
  "driver_contact": "010-1234-5678",
  "history": [
    {
      "status": "assigned",
      "timestamp": "2026-01-27T14:30:00Z",
      "notes": "배차 완료"
    },
    {
      "status": "in_progress",
      "timestamp": "2026-01-28T09:05:00Z",
      "notes": "출발하였습니다"
    }
  ]
}
```

### 차량 관리 (Vehicles)

#### 가용 차량 조회
```bash
GET /vehicles/available

curl -X GET "http://localhost:8000/api/v1/vehicles/available?cargo_type=frozen" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 차량 위치 업데이트
```bash
POST /vehicles/{vehicle_id}/location

curl -X POST "http://localhost:8000/api/v1/vehicles/5/location" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 37.5665,
    "longitude": 126.9780
  }'
```

### 모니터링 (Monitoring)

#### 시스템 헬스체크
```bash
GET /monitoring/health

curl -X GET "http://localhost:8000/api/v1/monitoring/health"
```

#### 시스템 메트릭
```bash
GET /monitoring/metrics

curl -X GET "http://localhost:8000/api/v1/monitoring/metrics"
```

#### 대시보드 데이터
```bash
GET /monitoring/dashboard

curl -X GET "http://localhost:8000/api/v1/monitoring/dashboard" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## ❌ 에러 처리

### HTTP 상태 코드

| 코드 | 의미 | 설명 |
|------|------|------|
| 200 | OK | 요청 성공 |
| 201 | Created | 리소스 생성 성공 |
| 400 | Bad Request | 잘못된 요청 (유효성 검증 실패) |
| 401 | Unauthorized | 인증 실패 |
| 403 | Forbidden | 권한 없음 |
| 404 | Not Found | 리소스를 찾을 수 없음 |
| 422 | Unprocessable Entity | 유효성 검증 실패 |
| 429 | Too Many Requests | Rate Limit 초과 |
| 500 | Internal Server Error | 서버 오류 |

### 에러 응답 형식

```json
{
  "detail": "에러 메시지",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-01-27T14:30:00Z"
}
```

### 유효성 검증 에러 (422)

```json
{
  "detail": [
    {
      "loc": ["body", "weight_kg"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

---

## 💻 예제 코드

### Python

```python
import requests
from typing import Optional

class ColdChainAPI:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.login(username, password)
    
    def login(self, username: str, password: str):
        """로그인 및 토큰 발급"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]
    
    def _headers(self):
        """인증 헤더"""
        return {"Authorization": f"Bearer {self.token}"}
    
    def create_order(self, order_data: dict):
        """주문 생성"""
        response = requests.post(
            f"{self.base_url}/orders",
            headers=self._headers(),
            json=order_data
        )
        response.raise_for_status()
        return response.json()
    
    def auto_dispatch(self, order_id: int):
        """자동 배차"""
        response = requests.post(
            f"{self.base_url}/dispatches/auto",
            headers=self._headers(),
            json={"order_id": order_id}
        )
        response.raise_for_status()
        return response.json()
    
    def track_delivery(self, tracking_number: str):
        """배송 추적 (인증 불필요)"""
        response = requests.get(
            f"{self.base_url}/delivery-tracking/{tracking_number}"
        )
        response.raise_for_status()
        return response.json()

# 사용 예제
api = ColdChainAPI(
    base_url="http://localhost:8000/api/v1",
    username="your_username",
    password="your_password"
)

# 주문 생성
order = api.create_order({
    "client_id": 10,
    "pickup_address": "서울특별시 강남구...",
    "delivery_address": "부산광역시 해운대구...",
    "cargo_type": "frozen",
    "weight_kg": 500.0
})

# 자동 배차
dispatch = api.auto_dispatch(order["id"])

print(f"배차 완료: {dispatch['dispatch_number']}")
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

class ColdChainAPI {
  constructor(baseURL, username, password) {
    this.baseURL = baseURL;
    this.client = axios.create({ baseURL });
    this.login(username, password);
  }

  async login(username, password) {
    const response = await this.client.post('/auth/login', {
      username,
      password
    });
    this.token = response.data.access_token;
    this.client.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
  }

  async createOrder(orderData) {
    const response = await this.client.post('/orders', orderData);
    return response.data;
  }

  async autoDispatch(orderId) {
    const response = await this.client.post('/dispatches/auto', {
      order_id: orderId
    });
    return response.data;
  }

  async trackDelivery(trackingNumber) {
    // 인증 불필요
    const response = await axios.get(
      `${this.baseURL}/delivery-tracking/${trackingNumber}`
    );
    return response.data;
  }
}

// 사용 예제
(async () => {
  const api = new ColdChainAPI(
    'http://localhost:8000/api/v1',
    'your_username',
    'your_password'
  );

  // 주문 생성
  const order = await api.createOrder({
    client_id: 10,
    pickup_address: '서울특별시 강남구...',
    delivery_address: '부산광역시 해운대구...',
    cargo_type: 'frozen',
    weight_kg: 500.0
  });

  // 자동 배차
  const dispatch = await api.autoDispatch(order.id);

  console.log(`배차 완료: ${dispatch.dispatch_number}`);
})();
```

### cURL

```bash
#!/bin/bash

# 환경 변수 설정
BASE_URL="http://localhost:8000/api/v1"
USERNAME="your_username"
PASSWORD="your_password"

# 로그인 및 토큰 발급
TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# 주문 생성
ORDER_RESPONSE=$(curl -s -X POST "$BASE_URL/orders" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 10,
    "pickup_address": "서울특별시 강남구...",
    "delivery_address": "부산광역시 해운대구...",
    "cargo_type": "frozen",
    "weight_kg": 500.0
  }')

ORDER_ID=$(echo $ORDER_RESPONSE | jq -r '.id')
echo "주문 생성: $ORDER_ID"

# 자동 배차
DISPATCH_RESPONSE=$(curl -s -X POST "$BASE_URL/dispatches/auto" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"order_id\":$ORDER_ID}")

DISPATCH_NUMBER=$(echo $DISPATCH_RESPONSE | jq -r '.dispatch_number')
echo "배차 완료: $DISPATCH_NUMBER"
```

---

## 📚 추가 리소스

- **Swagger UI**: http://localhost:8000/docs (인터랙티브 API 문서)
- **ReDoc**: http://localhost:8000/redoc (상세 API 문서)
- **Postman Collection**: [다운로드 링크]
- **GitHub Repository**: https://github.com/your-org/coldchain-dispatch

---

## 📞 지원

- **기술 문의**: api-support@your-domain.com
- **버그 리포트**: GitHub Issues
- **문서 업데이트**: docs@your-domain.com

---

**버전**: 1.0.0  
**최종 업데이트**: 2026-01-27  
**작성자**: GenSpark AI Developer
