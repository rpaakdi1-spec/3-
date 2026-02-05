# 🌡️ IoT 센서 통합 시스템

**프로젝트**: Cold Chain IoT Integration  
**시작일**: 2026-02-05  
**목표**: 실시간 온도/위치 센서 모니터링 및 자동 알림

---

## 📋 개요

냉동/냉장 차량의 온도 센서 및 GPS를 실시간으로 모니터링하고, 이상 온도 발생 시 자동으로 알림을 전송하는 IoT 통합 시스템입니다.

---

## 🎯 주요 기능

### 1. 센서 데이터 수집
- **MQTT 브로커**: 실시간 센서 데이터 수신
- **HTTP API**: REST 기반 데이터 수집
- **다중 프로토콜**: MQTT, HTTP, WebSocket 지원

### 2. 실시간 데이터 처리
- **스트림 처리**: Redis Streams 활용
- **데이터 검증**: 센서 값 유효성 검사
- **배치 저장**: 효율적인 DB 저장

### 3. 온도 이상 탐지
- **임계값 알림**: 설정 온도 범위 초과 시
- **트렌드 분석**: ML 기반 이상 패턴 감지
- **자동 알림**: SMS, 이메일, 앱 푸시

### 4. 실시간 대시보드
- **센서 현황**: 전체 차량 센서 상태
- **온도 그래프**: 실시간 온도 변화
- **알림 히스토리**: 이상 발생 기록

### 5. 데이터 분석
- **통계 리포트**: 온도 평균, 최고/최저
- **규정 준수**: Cold Chain 온도 규정 체크
- **예측 정비**: 센서 고장 예측

---

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    IoT Sensors                          │
│  (Temperature, GPS, Battery, Door, Humidity)            │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
    ┌───▼────┐          ┌────▼─────┐
    │  MQTT  │          │   HTTP   │
    │ Broker │          │   API    │
    └───┬────┘          └────┬─────┘
        │                    │
        └──────────┬─────────┘
                   │
          ┌────────▼─────────┐
          │  Data Processor  │
          │  (Validation)    │
          └────────┬─────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
    ┌───▼───┐  ┌──▼───┐  ┌──▼────┐
    │ Redis │  │ DB   │  │ Alert │
    │Stream │  │Store │  │Engine │
    └───┬───┘  └──┬───┘  └──┬────┘
        │         │         │
        └─────────┼─────────┘
                  │
          ┌───────▼────────┐
          │   Dashboard    │
          │  (WebSocket)   │
          └────────────────┘
```

---

## 📦 프로젝트 구조

```
iot_sensors/
├── mqtt/                       # MQTT 클라이언트
│   ├── __init__.py
│   ├── broker.py              # MQTT 브로커 연결
│   ├── subscriber.py          # 토픽 구독
│   └── publisher.py           # 데이터 발행
├── http_collector/            # HTTP 수집기
│   ├── __init__.py
│   ├── collector.py           # REST API 수집
│   └── webhook.py             # Webhook 수신
├── processors/                # 데이터 처리
│   ├── __init__.py
│   ├── validator.py           # 데이터 검증
│   ├── transformer.py         # 데이터 변환
│   └── streamer.py            # 스트림 처리
├── alerts/                    # 알림 시스템
│   ├── __init__.py
│   ├── rules_engine.py        # 알림 규칙
│   ├── notifier.py            # 알림 전송
│   └── templates.py           # 알림 템플릿
├── dashboard/                 # 대시보드 API
│   ├── __init__.py
│   ├── api.py                 # FastAPI 엔드포인트
│   └── websocket.py           # WebSocket 서버
├── tests/                     # 테스트
│   └── test_sensors.py
├── docs/                      # 문서
│   └── API.md
├── requirements_iot.txt       # 의존성
└── README.md                  # 이 파일
```

---

## 🚀 빠른 시작

### 1. 환경 설정
```bash
cd /home/user/webapp/iot_sensors
pip install -r requirements_iot.txt
```

### 2. MQTT 브로커 실행 (옵션)
```bash
# Mosquitto MQTT 브로커
docker run -d -p 1883:1883 -p 9001:9001 eclipse-mosquitto
```

### 3. 센서 데이터 수집 시작
```bash
python -m mqtt.subscriber
```

### 4. 대시보드 서버 실행
```bash
uvicorn dashboard.api:app --host 0.0.0.0 --port 8001
```

---

## 📊 지원 센서 타입

### 1. 온도 센서
- **측정**: 섭씨 온도 (-30°C ~ +30°C)
- **정확도**: ±0.5°C
- **샘플링**: 1분 간격

### 2. GPS 센서
- **위치**: 위도/경도
- **정확도**: ±10m
- **샘플링**: 30초 간격

### 3. 도어 센서
- **상태**: OPEN/CLOSED
- **감지**: 자기 센서
- **이벤트 기반**: 상태 변경 시만 전송

### 4. 배터리 센서
- **전압**: 12V 시스템
- **범위**: 10V ~ 15V
- **알림**: 11V 이하 경고

### 5. 습도 센서 (선택)
- **측정**: 상대습도 (0-100%)
- **정확도**: ±3%
- **샘플링**: 5분 간격

---

## 📡 센서 데이터 포맷

### MQTT 토픽 구조
```
coldchain/vehicles/{vehicle_id}/temperature
coldchain/vehicles/{vehicle_id}/gps
coldchain/vehicles/{vehicle_id}/door
coldchain/vehicles/{vehicle_id}/battery
coldchain/vehicles/{vehicle_id}/humidity
```

### 메시지 페이로드 (JSON)
```json
{
  "vehicle_id": "V001",
  "sensor_type": "temperature",
  "timestamp": "2026-02-05T10:30:00Z",
  "value": -18.5,
  "unit": "celsius",
  "location": {
    "latitude": 37.5665,
    "longitude": 126.9780
  },
  "metadata": {
    "sensor_id": "TEMP_001",
    "battery": 12.6,
    "signal_strength": -65
  }
}
```

### HTTP API 엔드포인트
```bash
POST /api/v1/sensors/data
Content-Type: application/json

{
  "vehicle_id": "V001",
  "sensors": [
    {
      "type": "temperature",
      "value": -18.5,
      "unit": "celsius"
    },
    {
      "type": "gps",
      "latitude": 37.5665,
      "longitude": 126.9780
    }
  ],
  "timestamp": "2026-02-05T10:30:00Z"
}
```

---

## 🚨 알림 규칙

### 온도 알림
| 차량 타입 | 정상 범위 | 경고 | 위험 |
|-----------|-----------|------|------|
| 냉동 | -25°C ~ -15°C | ±2°C | ±5°C |
| 냉장 | 0°C ~ 10°C | ±2°C | ±5°C |
| 겸용 | -25°C ~ 10°C | ±2°C | ±5°C |

### 알림 우선순위
1. **긴급 (P1)**: 온도 위험 범위, 도어 열림 30분 이상
2. **높음 (P2)**: 온도 경고 범위, 배터리 저전압
3. **보통 (P3)**: 센서 연결 끊김, 데이터 지연
4. **낮음 (P4)**: 정보성 알림

### 알림 채널
- 📱 **모바일 푸시**: 실시간 알림
- 📧 **이메일**: 일일/주간 리포트
- 💬 **SMS**: 긴급 알림 (P1, P2)
- 🔔 **WebSocket**: 대시보드 실시간 업데이트

---

## 💰 비즈니스 가치

### 예상 효과
| 항목 | 개선 | 연간 가치 |
|------|------|-----------|
| 상품 손실 방지 | 90% 감소 | ₩80M |
| 규정 위반 벌금 | 95% 감소 | ₩30M |
| 클레임 처리 | 70% 감소 | ₩20M |
| 예방 정비 | 50% 향상 | ₩20M |
| **합계** | | **₩150M/년** |

### ROI
- **구현 비용**: ₩5M (센서 + 개발)
- **연간 절감**: ₩150M
- **ROI**: 3,000%
- **회수 기간**: 12일

---

## 🔧 기술 스택

### Backend
- **Python 3.11+**: 메인 언어
- **FastAPI**: REST API
- **MQTT**: paho-mqtt
- **Redis**: 스트림 처리
- **PostgreSQL**: 데이터 저장
- **WebSocket**: 실시간 통신

### 센서 통신
- **MQTT**: Eclipse Mosquitto
- **HTTP/REST**: FastAPI
- **Protocol Buffers**: 데이터 직렬화 (선택)

### 모니터링
- **Prometheus**: 메트릭 수집
- **Grafana**: 대시보드
- **AlertManager**: 알림 관리

---

## 📈 구현 단계

### Week 1: 기본 인프라 (5일)
- [x] 프로젝트 구조 생성
- [ ] MQTT 브로커 설정
- [ ] 데이터 수집 모듈
- [ ] Redis 스트림 처리
- [ ] 데이터베이스 스키마

### Week 2: 데이터 처리 (5일)
- [ ] 데이터 검증 파이프라인
- [ ] 실시간 스트림 처리
- [ ] 배치 저장 최적화
- [ ] 에러 핸들링

### Week 3: 알림 시스템 (3일)
- [ ] 알림 규칙 엔진
- [ ] SMS/이메일 전송
- [ ] 푸시 알림 통합
- [ ] 알림 히스토리

### Week 4: 대시보드 (4일)
- [ ] 백엔드 API
- [ ] WebSocket 서버
- [ ] 프론트엔드 UI
- [ ] 실시간 차트

### Week 5: 테스트 & 배포 (3일)
- [ ] 단위 테스트
- [ ] 통합 테스트
- [ ] 부하 테스트
- [ ] 문서화

---

## 🧪 테스트

### 센서 시뮬레이터
```python
# 테스트용 센서 데이터 생성
python tests/sensor_simulator.py --vehicles 10 --interval 60
```

### MQTT 테스트
```bash
# 메시지 발행
mosquitto_pub -t "coldchain/vehicles/V001/temperature" -m '{"value": -18.5}'

# 메시지 구독
mosquitto_sub -t "coldchain/vehicles/#"
```

---

## 📚 참고 자료

### MQTT
- [Eclipse Mosquitto](https://mosquitto.org/)
- [Paho MQTT Python](https://www.eclipse.org/paho/index.php?page=clients/python/index.php)

### Redis Streams
- [Redis Streams Documentation](https://redis.io/docs/data-types/streams/)

### Cold Chain 표준
- [WHO Cold Chain Guidelines](https://www.who.int/)
- [FDA Temperature Monitoring](https://www.fda.gov/)

---

## 🔐 보안

### 인증
- **MQTT TLS**: 암호화 통신
- **API Key**: HTTP API 인증
- **JWT**: 대시보드 접근

### 데이터 보호
- **암호화**: 저장 데이터 암호화
- **접근 제어**: RBAC
- **감사 로그**: 모든 접근 기록

---

## 📞 지원

- **GitHub**: https://github.com/rpaakdi1-spec/3-.git
- **문서**: `/iot_sensors/docs/`
- **API Docs**: http://localhost:8001/docs

---

**시작일**: 2026-02-05  
**예상 완료**: 2026-02-26 (3주)  
**상태**: 🚧 진행 중

**Made with ❤️ for Cold Chain Logistics**
