# 모니터링 및 알림 시스템

## 📋 개요

시스템 상태를 실시간으로 모니터링하고 이상 상황을 자동으로 감지하여 관리자에게 알림을 전송하는 종합 모니터링 시스템입니다.

### 주요 기능

1. **시스템 헬스 체크** - DB, 리소스, 애플리케이션 상태
2. **메트릭 수집** - 주문, 배차, 차량, 시스템 통계
3. **이상 감지** - 자동 알림 생성
4. **다중 채널 알림** - 이메일, SMS, Slack
5. **대시보드 API** - 실시간 모니터링 대시보드
6. **알림 레벨** - Info, Warning, Critical

---

## 🎯 시스템 구성

### Backend

**모니터링 서비스:** `/backend/app/services/monitoring_service.py` (17,050자)  
**알림 서비스:** `/backend/app/services/notification_service.py` (13,489자)  
**API:** `/backend/app/api/monitoring.py` (7,692자)

---

## 🚀 API 엔드포인트

### 1. 시스템 헬스 체크

**GET** `/api/v1/monitoring/health`

**응답:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-27T22:00:00",
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 45.23,
      "message": "Database connection OK"
    },
    "system_resources": {
      "status": "healthy",
      "cpu_percent": 25.3,
      "memory_percent": 45.7,
      "disk_percent": 62.1,
      "memory_available_gb": 8.52,
      "disk_free_gb": 150.45
    },
    "application": {
      "status": "healthy",
      "recent_orders_24h": 145,
      "active_dispatches": 23,
      "active_vehicles": 45
    }
  }
}
```

**상태 코드:**
- `healthy`: 모든 시스템 정상
- `degraded`: 성능 저하
- `unhealthy`: 심각한 문제

### 2. 시스템 메트릭 조회

**GET** `/api/v1/monitoring/metrics?period_hours=24`

**파라미터:**
- `period_hours`: 수집 기간 (1-168시간)

**응답:**
```json
{
  "period_hours": 24,
  "timestamp": "2026-01-27T22:00:00",
  "orders": {
    "total": 145,
    "by_status": {
      "배차대기": 12,
      "배차완료": 45,
      "운송중": 38,
      "배송완료": 48,
      "취소": 2
    },
    "avg_processing_hours": 6.5,
    "completion_rate": 33.1
  },
  "dispatches": {
    "total": 67,
    "by_status": {
      "임시저장": 5,
      "확정": 20,
      "진행중": 30,
      "완료": 12,
      "취소": 0
    },
    "avg_distance_km": 42.5
  },
  "vehicles": {
    "total": 50,
    "available": 27,
    "in_use": 20,
    "maintenance": 3,
    "utilization_rate": 40.0
  },
  "system": {
    "cpu": {
      "percent": 25.3,
      "count": 8
    },
    "memory": {
      "total_gb": 16.0,
      "used_gb": 7.3,
      "available_gb": 8.7,
      "percent": 45.6
    },
    "disk": {
      "total_gb": 500.0,
      "used_gb": 310.2,
      "free_gb": 189.8,
      "percent": 62.0
    },
    "network": {
      "bytes_sent_mb": 1250.45,
      "bytes_recv_mb": 2340.67
    }
  }
}
```

### 3. 시스템 알림 조회

**GET** `/api/v1/monitoring/alerts`

**응답:**
```json
{
  "total": 3,
  "alerts": [
    {
      "level": "warning",
      "category": "system",
      "title": "CPU 사용률 주의",
      "message": "CPU 사용률이 75.3%입니다",
      "timestamp": "2026-01-27T22:00:00"
    },
    {
      "level": "warning",
      "category": "business",
      "title": "배차 대기 주문 많음",
      "message": "2시간 이상 배차 대기 중인 주문이 12건 있습니다",
      "timestamp": "2026-01-27T22:00:00"
    },
    {
      "level": "info",
      "category": "business",
      "title": "차량 활용률 낮음",
      "message": "차량 활용률이 28.5%로 낮습니다",
      "timestamp": "2026-01-27T22:00:00"
    }
  ]
}
```

**알림 레벨:**
- `critical`: 즉시 조치 필요 (>90% 리소스, DB 실패)
- `warning`: 주의 필요 (>70% 리소스, 응답 지연)
- `info`: 정보성 알림

### 4. 알림 전송

**POST** `/api/v1/monitoring/notify`

**요청:**
```json
{
  "title": "시스템 알림",
  "message": "CPU 사용률이 높습니다",
  "level": "warning",
  "channels": ["email", "slack"],
  "email_recipients": ["admin@example.com"],
  "sms_recipients": ["01012345678"]
}
```

**응답:**
```json
{
  "success": true,
  "results": {
    "email": true,
    "slack": true
  },
  "message": "알림이 전송되었습니다"
}
```

### 5. 대시보드 요약

**GET** `/api/v1/monitoring/dashboard`

**응답:**
```json
{
  "timestamp": "2026-01-27T22:00:00",
  "health": {
    "status": "healthy",
    "database": "healthy",
    "resources": "healthy",
    "application": "healthy"
  },
  "metrics": {
    "orders_24h": 145,
    "active_dispatches": 23,
    "vehicle_utilization": 40.0,
    "cpu_percent": 25.3,
    "memory_percent": 45.7,
    "disk_percent": 62.1
  },
  "alerts": {
    "total": 3,
    "by_level": {
      "critical": 0,
      "warning": 2,
      "info": 1
    },
    "recent": [...]
  }
}
```

### 6. 테스트 엔드포인트

**GET** `/api/v1/monitoring/test/email?to_email=admin@example.com`  
**GET** `/api/v1/monitoring/test/slack`  
**POST** `/api/v1/monitoring/test/alert?level=warning&channel=slack`

---

## 🔧 설정

### 환경 변수

`.env` 파일에 다음 설정 추가:

```bash
# 이메일 알림 (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # Gmail 앱 비밀번호
SMTP_FROM=noreply@yourdomain.com

# Slack 알림
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# SMS 알림 (알리고)
ALIGO_API_KEY=your_aligo_api_key
ALIGO_USER_ID=your_aligo_user_id
ALIGO_SENDER=01012345678
```

### Gmail 앱 비밀번호 생성

1. Google 계정 설정 접속
2. **보안** > **2단계 인증** 활성화
3. **앱 비밀번호** 생성
4. 생성된 16자리 비밀번호를 `SMTP_PASSWORD`에 설정

### Slack Webhook URL 생성

1. [Slack API](https://api.slack.com/apps) 접속
2. **Create New App** > **From scratch**
3. **Incoming Webhooks** 활성화
4. **Add New Webhook to Workspace**
5. 채널 선택 후 Webhook URL 복사

### 알리고 SMS API 설정

1. [알리고](https://smartsms.aligo.in/) 가입
2. **API 키 발급** (회원정보 > API 연동정보)
3. `ALIGO_API_KEY`, `ALIGO_USER_ID`, `ALIGO_SENDER` 설정

---

## 💻 사용 방법

### Python에서 사용

```python
from app.services.monitoring_service import MonitoringService
from app.services.notification_service import NotificationService

# 1. 시스템 헬스 체크
health = MonitoringService.get_system_health(db)
print(f"시스템 상태: {health['status']}")

# 2. 메트릭 수집
metrics = MonitoringService.get_metrics(db, period_hours=24)
print(f"24시간 주문 수: {metrics['orders']['total']}")

# 3. 알림 조회
alerts = MonitoringService.get_alerts(db)
print(f"활성 알림: {len(alerts)}개")

# 4. 알림 전송
notification_service = NotificationService()
notification_service.send_alert(
    title="시스템 알림",
    message="CPU 사용률이 높습니다",
    level="warning",
    channels=["email", "slack"],
    recipients={
        "email": ["admin@example.com"],
        "slack": []  # Slack은 Webhook URL만 필요
    }
)
```

### API로 사용

```bash
# 헬스 체크
curl "http://localhost:8000/api/v1/monitoring/health"

# 메트릭 조회
curl "http://localhost:8000/api/v1/monitoring/metrics?period_hours=24"

# 알림 조회
curl "http://localhost:8000/api/v1/monitoring/alerts"

# 대시보드 요약
curl "http://localhost:8000/api/v1/monitoring/dashboard"

# 이메일 테스트
curl "http://localhost:8000/api/v1/monitoring/test/email?to_email=admin@example.com"

# Slack 테스트
curl "http://localhost:8000/api/v1/monitoring/test/slack"
```

---

## 📊 모니터링 항목

### 시스템 리소스

| 항목 | 경고 임계값 | 위험 임계값 |
|------|------------|------------|
| CPU 사용률 | 70% | 90% |
| 메모리 사용률 | 70% | 90% |
| 디스크 사용률 | 80% | 90% |

### 데이터베이스

| 항목 | 경고 임계값 | 위험 임계값 |
|------|------------|------------|
| 응답 시간 | 500ms | 1000ms |
| 연결 실패 | - | 즉시 |

### 비즈니스 로직

| 항목 | 조건 | 레벨 |
|------|------|------|
| 배차 대기 주문 | 2시간 이상 대기 10건 초과 | warning |
| 차량 활용률 | 30% 미만 | info |
| 지연된 배차 | 예정일 초과 5건 초과 | warning |

---

## 🔔 알림 채널별 동작

### 알림 레벨에 따른 자동 채널 선택

| 레벨 | 이메일 | SMS | Slack |
|------|--------|-----|-------|
| info | ❌ | ❌ | ✅ |
| warning | ✅ | ❌ | ✅ |
| critical | ✅ | ✅ | ✅ |

### 이메일 템플릿

**시스템 헬스 보고:**
```html
<h2>시스템 상태 보고</h2>
<p>시스템 상태: <strong>healthy</strong></p>

<h3>데이터베이스</h3>
<ul>
    <li>상태: healthy</li>
    <li>응답 시간: 45ms</li>
</ul>

<h3>시스템 리소스</h3>
<ul>
    <li>CPU: 25.3%</li>
    <li>메모리: 45.7%</li>
    <li>디스크: 62.1%</li>
</ul>
```

### Slack 메시지

**레벨별 색상 및 이모지:**
- Info: 🔵 녹색
- Warning: 🟠 주황
- Critical: 🔴 빨강

**메시지 형식:**
```
:rotating_light: [CRITICAL] 시스템 알림

CPU 사용률이 95.3%로 매우 높습니다

Category: system
Timestamp: 2026-01-27T22:00:00

---
Cold Chain Dispatch System
```

---

## 🧪 테스트

### 1. 로컬 테스트

```bash
# 시스템 헬스 체크
curl "http://localhost:8000/api/v1/monitoring/health"

# 메트릭 조회
curl "http://localhost:8000/api/v1/monitoring/metrics?period_hours=1"

# 알림 조회
curl "http://localhost:8000/api/v1/monitoring/alerts"
```

### 2. 알림 테스트

```bash
# 이메일 테스트
curl "http://localhost:8000/api/v1/monitoring/test/email?to_email=your_email@gmail.com"

# Slack 테스트
curl "http://localhost:8000/api/v1/monitoring/test/slack"

# 알림 레벨 테스트
curl -X POST "http://localhost:8000/api/v1/monitoring/test/alert?level=warning&channel=slack"
```

### 3. Python 테스트

```python
import pytest
from app.services.monitoring_service import MonitoringService

def test_system_health(db):
    health = MonitoringService.get_system_health(db)
    assert health["status"] in ["healthy", "degraded", "unhealthy"]
    assert "checks" in health
    assert "database" in health["checks"]
    assert "system_resources" in health["checks"]

def test_metrics(db):
    metrics = MonitoringService.get_metrics(db, 24)
    assert "orders" in metrics
    assert "dispatches" in metrics
    assert "vehicles" in metrics
    assert "system" in metrics

def test_alerts(db):
    alerts = MonitoringService.get_alerts(db)
    assert isinstance(alerts, list)
    for alert in alerts:
        assert "level" in alert
        assert alert["level"] in ["info", "warning", "critical"]
```

---

## 📈 대시보드 통합

### Frontend 대시보드에서 사용

```typescript
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1/monitoring';

// 대시보드 데이터 로드
async function loadDashboard() {
  const response = await axios.get(`${API_URL}/dashboard`);
  const data = response.data;
  
  // 상태 표시
  updateHealthStatus(data.health.status);
  
  // 메트릭 표시
  updateMetrics(data.metrics);
  
  // 알림 표시
  updateAlerts(data.alerts);
}

// 5초마다 자동 갱신
setInterval(loadDashboard, 5000);
```

---

## 🚨 자동 알림 시나리오

### 1. CPU 사용률 높음

**트리거:** CPU > 90%  
**레벨:** Critical  
**채널:** 이메일 + SMS + Slack  
**액션:** 관리자에게 즉시 알림

### 2. 배차 대기 주문 누적

**트리거:** 2시간 이상 대기 주문 10건 초과  
**레벨:** Warning  
**채널:** 이메일 + Slack  
**액션:** 배차 담당자에게 알림

### 3. 데이터베이스 응답 지연

**트리거:** 응답 시간 > 1초  
**레벨:** Critical  
**채널:** 이메일 + SMS + Slack  
**액션:** 시스템 관리자에게 즉시 알림

---

## 🔜 향후 개선 사항

### 단기 (1-2주)

1. **로그 집계 시스템**
   - 로그 파일 분석
   - 에러 로그 자동 수집
   - 로그 검색 기능

2. **메트릭 히스토리**
   - 시계열 데이터 저장
   - 트렌드 분석
   - 예측 알고리즘

3. **사용자 정의 알림 규칙**
   - 임계값 설정
   - 알림 스케줄
   - 수신자 그룹 관리

### 중기 (1-2개월)

1. **Grafana 연동**
   - 시각화 대시보드
   - 커스텀 차트
   - 실시간 모니터링

2. **Prometheus 메트릭**
   - 표준 메트릭 포맷
   - 장기 데이터 저장
   - 고급 쿼리

3. **ELK 스택 연동**
   - Elasticsearch 로그 저장
   - Logstash 로그 수집
   - Kibana 시각화

---

## ✅ 완료 체크리스트

- [x] 시스템 헬스 체크
- [x] 메트릭 수집 (주문, 배차, 차량, 시스템)
- [x] 이상 감지 (리소스, DB, 비즈니스)
- [x] 다중 채널 알림 (이메일, SMS, Slack)
- [x] API 엔드포인트 (7개)
- [x] 알림 레벨 시스템
- [x] 대시보드 API
- [x] 테스트 엔드포인트
- [x] 문서화

---

## 🎉 결론

모니터링 및 알림 시스템이 성공적으로 완료되었습니다!

**주요 성과:**
- ✅ 전체 시스템 헬스 체크
- ✅ 실시간 메트릭 수집
- ✅ 자동 이상 감지
- ✅ 다중 채널 알림 (이메일/SMS/Slack)
- ✅ 대시보드 API
- ✅ 완전한 문서화

**통계:**
- Backend: 38,231자 (3개 파일)
- API: 7개 엔드포인트
- 알림 채널: 3개
- 모니터링 항목: 20개 이상

**Phase 3 완료!**

---

**작성일:** 2026-01-27  
**작성자:** GenSpark AI Developer  
**프로젝트:** Cold Chain Dispatch System  
**GitHub:** https://github.com/rpaakdi1-spec/3-  
**Pull Request:** https://github.com/rpaakdi1-spec/3-/pull/1
