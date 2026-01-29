# UVIS GPS 실시간 관제 시스템 완전 가이드

## 📅 작성일
**2026-01-27**

## 📖 목차
1. [개요](#개요)
2. [시스템 구성](#시스템-구성)
3. [주요 기능](#주요-기능)
4. [API 엔드포인트](#api-엔드포인트)
5. [사용 방법](#사용-방법)
6. [데이터베이스 스키마](#데이터베이스-스키마)
7. [인터페이스 사양](#인터페이스-사양)
8. [문제 해결](#문제-해결)

---

## 개요

### 🎯 목적
광신특수(주)의 UVIS GPS 관제 시스템과 연동하여 냉동·냉장 화물차량의 실시간 위치 및 온도 정보를 모니터링합니다.

### 🔑 핵심 기능
- ✅ **실시간 GPS 추적**: 차량 위치, 속도, 시동 상태 모니터링
- ✅ **온도 모니터링**: 냉동실/냉장실 온도 실시간 조회
- ✅ **자동 동기화**: 3-5분 간격 자동 데이터 동기화
- ✅ **인증키 관리**: 5분 유효 인증키 자동 갱신
- ✅ **API 로깅**: 모든 UVIS API 호출 기록 저장

### 📊 통계
- **연동 API**: 3개 (인증키, GPS, 온도)
- **데이터베이스 테이블**: 4개
- **API 엔드포인트**: 10개+
- **프론트엔드 컴포넌트**: 1개

---

## 시스템 구성

### 백엔드 아키텍처

```
backend/
├── app/
│   ├── models/
│   │   ├── uvis_gps.py            # UVIS GPS 모델
│   │   └── vehicle.py             # 차량 모델 (수정)
│   ├── services/
│   │   └── uvis_gps_service.py    # UVIS API 서비스
│   ├── schemas/
│   │   └── uvis_gps.py            # UVIS 스키마
│   └── api/
│       └── uvis_gps.py            # UVIS API 라우터
└── main.py                         # FastAPI 앱 (수정)
```

### 프론트엔드 구조

```
frontend/
└── src/
    └── components/
        └── UvisGPSMonitoring.tsx   # 실시간 모니터링 컴포넌트
```

---

## 주요 기능

### 1. 인증키 관리

#### 📋 설명
- UVIS API 접근을 위한 실시간 인증키 자동 발급 및 관리
- **유효 시간**: 5분
- **자동 갱신**: 만료 전 자동 재발급

#### 🔐 업체 인증키
```
S1910-3A84-4559--CC4
```

#### 📝 프로세스
1. 업체 인증키로 실시간 인증키 요청
2. 발급된 키를 DB에 저장 (만료 시간 포함)
3. 5분 후 자동 만료
4. 새 요청 시 유효한 키 조회 또는 재발급

### 2. 실시간 GPS 데이터 수집

#### 📡 수집 항목
- **단말기 ID** (`TID_ID`): 차량 식별
- **위치**: 위도/경도 (GPS 좌표)
- **시동 상태**: ON/OFF
- **속도**: km/h
- **일시**: YYYYMMDD + HHMMSS

#### 🔄 동기화 주기
- **수동**: 사용자가 "동기화" 버튼 클릭
- **자동**: 10초/30초/1분/5분 간격 선택 가능

### 3. 실시간 온도 데이터 수집

#### 🌡️ 수집 항목
- **냉동실 A 온도**: 부호(+/-) + 온도값
- **냉장실 B 온도**: 부호(+/-) + 온도값
- **위치**: 위도/경도
- **일시**: YYYYMMDD + HHMMSS

#### 📊 온도 색상 코드
- **파란색** (< -15°C): 냉동 상태 양호
- **하늘색** (-15°C ~ 5°C): 정상 범위
- **녹색** (5°C ~ 15°C): 냉장 상태
- **주황색** (> 15°C): 주의 필요

### 4. 실시간 모니터링 대시보드

#### 🖥️ 화면 구성
1. **컨트롤 패널**
   - UVIS 데이터 동기화 버튼
   - 새로고침 버튼
   - 자동 새로고침 설정 (10초/30초/1분/5분)
   - 마지막 동기화 시간 표시

2. **차량 카드**
   - 차량번호 및 시동 상태
   - GPS 정보 (위도, 경도, 속도)
   - 온도 정보 (냉동실 A, 냉장실 B)
   - 최종 업데이트 시간

3. **통계 패널**
   - 전체 차량 수
   - 시동 ON 차량 수
   - GPS 활성 차량 수
   - 온도 센서 활성 차량 수

---

## API 엔드포인트

### 인증키 관리

#### 1. 현재 유효한 인증키 조회
```http
GET /api/v1/uvis-gps/access-key/current
```

**응답 예시:**
```json
{
  "id": 1,
  "serial_key": "S1910-3A84-4559--CC4",
  "access_key": "abc123...",
  "issued_at": "2026-01-27T07:00:00Z",
  "expires_at": "2026-01-27T07:05:00Z",
  "is_active": true
}
```

#### 2. 새 인증키 발급
```http
POST /api/v1/uvis-gps/access-key/issue
```

**응답 예시:**
```json
{
  "id": 2,
  "serial_key": "S1910-3A84-4559--CC4",
  "access_key": "xyz789...",
  "issued_at": "2026-01-27T07:05:00Z",
  "expires_at": "2026-01-27T07:10:00Z",
  "is_active": true
}
```

### 데이터 동기화

#### 3. GPS 데이터 동기화
```http
POST /api/v1/uvis-gps/sync/gps
Content-Type: application/json

{
  "force_new_key": false
}
```

**응답 예시:**
```json
{
  "success": true,
  "message": "GPS 데이터 12건 동기화 완료",
  "data_count": 12,
  "access_key_issued": false
}
```

#### 4. 온도 데이터 동기화
```http
POST /api/v1/uvis-gps/sync/temperature
Content-Type: application/json

{
  "force_new_key": false
}
```

**응답 예시:**
```json
{
  "success": true,
  "message": "온도 데이터 12건 동기화 완료",
  "data_count": 12,
  "access_key_issued": false
}
```

#### 5. 전체 데이터 동기화 (GPS + 온도)
```http
POST /api/v1/uvis-gps/sync/all?force_new_key=false
```

**응답 예시:**
```json
{
  "success": true,
  "message": "전체 동기화 완료 (GPS: 12건, 온도: 12건)",
  "gps_count": 12,
  "temperature_count": 12,
  "access_key_issued": false
}
```

### GPS 로그 조회

#### 6. GPS 로그 목록
```http
GET /api/v1/uvis-gps/gps-logs?skip=0&limit=50&vehicle_id=1
```

**쿼리 파라미터:**
- `skip`: 건너뛸 개수 (기본: 0)
- `limit`: 조회 개수 (기본: 50, 최대: 500)
- `vehicle_id`: 차량 ID (선택)
- `tid_id`: 단말기 ID (선택)
- `date_from`: 시작 날짜 YYYYMMDD (선택)
- `date_to`: 종료 날짜 YYYYMMDD (선택)

#### 7. GPS 로그 상세
```http
GET /api/v1/uvis-gps/gps-logs/{gps_log_id}
```

### 온도 로그 조회

#### 8. 온도 로그 목록
```http
GET /api/v1/uvis-gps/temperature-logs?skip=0&limit=50
```

#### 9. 온도 로그 상세
```http
GET /api/v1/uvis-gps/temperature-logs/{temp_log_id}
```

### 실시간 모니터링

#### 10. 전체 차량 실시간 상태
```http
GET /api/v1/uvis-gps/realtime/vehicles
```

**응답 예시:**
```json
{
  "total": 3,
  "items": [
    {
      "vehicle_id": 1,
      "vehicle_plate_number": "12가3456",
      "tid_id": "UV123456789",
      "gps_datetime": "2026-01-27 15:30:45",
      "latitude": 37.5665,
      "longitude": 126.9780,
      "is_engine_on": true,
      "speed_kmh": 60,
      "temperature_datetime": "2026-01-27 15:30:50",
      "temperature_a": -18.5,
      "temperature_b": 3.2,
      "last_updated": "2026-01-27T06:30:50Z"
    }
  ]
}
```

#### 11. 특정 차량 실시간 상태
```http
GET /api/v1/uvis-gps/realtime/vehicles/{vehicle_id}
```

### API 로그 조회

#### 12. API 호출 로그 목록
```http
GET /api/v1/uvis-gps/api-logs?skip=0&limit=100&api_type=gps
```

**쿼리 파라미터:**
- `skip`: 건너뛸 개수 (기본: 0)
- `limit`: 조회 개수 (기본: 100, 최대: 1000)
- `api_type`: API 유형 (auth/gps/temperature) (선택)

---

## 사용 방법

### 백엔드 설정

#### 1. 데이터베이스 마이그레이션
```bash
cd /home/user/webapp/backend
source venv/bin/activate
python3 -c "from app.core.database import init_db; init_db()"
```

#### 2. 백엔드 서버 시작
```bash
cd /home/user/webapp/backend
source venv/bin/activate
python3 main.py
```

#### 3. API 문서 확인
```
http://localhost:8000/docs
```

### 프론트엔드 사용

#### 1. 컴포넌트 import
```typescript
import UvisGPSMonitoring from './components/UvisGPSMonitoring';
```

#### 2. 컴포넌트 사용
```tsx
<UvisGPSMonitoring />
```

#### 3. 주요 기능
1. **UVIS 데이터 동기화**: 버튼 클릭하여 최신 데이터 가져오기
2. **자동 새로고침**: 10초/30초/1분/5분 간격 선택
3. **차량 모니터링**: 각 차량의 위치, 시동, 온도 실시간 확인

---

## 데이터베이스 스키마

### 1. uvis_access_keys (인증키 관리)
```sql
CREATE TABLE uvis_access_keys (
  id INTEGER PRIMARY KEY,
  serial_key VARCHAR(50) NOT NULL,
  access_key VARCHAR(100) NOT NULL,
  issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP
);
```

### 2. vehicle_gps_logs (GPS 로그)
```sql
CREATE TABLE vehicle_gps_logs (
  id INTEGER PRIMARY KEY,
  vehicle_id INTEGER,
  tid_id VARCHAR(11) NOT NULL,
  bi_date VARCHAR(8) NOT NULL,
  bi_time VARCHAR(6) NOT NULL,
  cm_number VARCHAR(30),
  bi_turn_onoff VARCHAR(3),
  bi_x_position VARCHAR(10) NOT NULL,
  bi_y_position VARCHAR(10) NOT NULL,
  bi_gps_speed INTEGER,
  latitude FLOAT,
  longitude FLOAT,
  is_engine_on BOOLEAN DEFAULT FALSE,
  speed_kmh INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
);
```

### 3. vehicle_temperature_logs (온도 로그)
```sql
CREATE TABLE vehicle_temperature_logs (
  id INTEGER PRIMARY KEY,
  vehicle_id INTEGER,
  off_key VARCHAR(7),
  tid_id VARCHAR(11) NOT NULL,
  tpl_date VARCHAR(8) NOT NULL,
  tpl_time VARCHAR(6) NOT NULL,
  cm_number VARCHAR(30),
  tpl_x_position VARCHAR(10),
  tpl_y_position VARCHAR(10),
  tpl_signal_a INTEGER,
  tpl_degree_a VARCHAR(5),
  temperature_a FLOAT,
  tpl_signal_b INTEGER,
  tpl_degree_b VARCHAR(5),
  temperature_b FLOAT,
  latitude FLOAT,
  longitude FLOAT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
);
```

### 4. uvis_api_logs (API 호출 로그)
```sql
CREATE TABLE uvis_api_logs (
  id INTEGER PRIMARY KEY,
  api_type VARCHAR(20) NOT NULL,
  method VARCHAR(10) NOT NULL,
  url TEXT NOT NULL,
  request_params TEXT,
  response_status INTEGER,
  response_data TEXT,
  error_message TEXT,
  execution_time_ms INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 인터페이스 사양

### UVIS-001: 실시간 인증키 발급

**URL:**
```
https://s1.u-vis.com/uvisc/InterfaceAction.do?method=GetAccessKeyWithValues&SerialKey=[업체인증키]
```

**입력:**
- `SerialKey`: S1910-3A84-4559--CC4

**출력:**
- `AccessKey`: 실시간 인증키 (5분 유효)

### UVIS-002: 실시간 운행정보

**URL:**
```
https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=[실시간인증키]&GUBUN=01
```

**입력:**
- `AccessKey`: 실시간 인증키
- `GUBUN`: 01 (운행정보)

**출력:**
- `TID_ID`: 단말기 ID
- `BI_DATE`: 날짜 (YYYYMMDD)
- `BI_TIME`: 시간 (HHMMSS)
- `CM_NUMBER`: 차량번호
- `BI_TURN_ONOFF`: 시동 상태
- `BI_X_POSITION`: 위도
- `BI_Y_POSITION`: 경도
- `BI_GPS_SPEED`: 속도

### UVIS-003: 실시간 온도정보

**URL:**
```
https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=[실시간인증키]&GUBUN=02
```

**입력:**
- `AccessKey`: 실시간 인증키
- `GUBUN`: 02 (온도정보)

**출력:**
- `TID_ID`: 단말기 ID
- `TPL_DATE`: 날짜 (YYYYMMDD)
- `TPL_TIME`: 시간 (HHMMSS)
- `CM_NUMBER`: 차량번호
- `TPL_X_POSITION`: 위도
- `TPL_Y_POSITION`: 경도
- `TPL_SIGNAL_A`: A 온도 부호 (0='+', 1='-')
- `TPL_DEGREE_A`: A 온도값
- `TPL_SIGNAL_B`: B 온도 부호 (0='+', 1='-')
- `TPL_DEGREE_B`: B 온도값

---

## 문제 해결

### 1. 인증키 발급 실패

**증상:**
- "인증키 발급 실패" 에러 메시지

**원인:**
- UVIS 서버 응답 없음
- 업체 인증키 오류
- 네트워크 연결 문제

**해결:**
1. `uvis_api_logs` 테이블에서 에러 로그 확인
2. 업체 인증키 확인: `S1910-3A84-4559--CC4`
3. UVIS 서버 상태 확인: https://s1.u-vis.com

### 2. 데이터 동기화 안 됨

**증상:**
- "동기화 완료" 메시지는 나오지만 데이터가 0건

**원인:**
- UVIS에서 반환하는 데이터가 없음
- 차량 단말기 미등록

**해결:**
1. `vehicles` 테이블에서 `uvis_device_id` 확인
2. `uvis_enabled` 플래그가 `true`인지 확인
3. UVIS 관리자에게 단말기 등록 확인

### 3. 차량이 목록에 안 보임

**증상:**
- GPS/온도 데이터는 있지만 차량 목록에 표시 안 됨

**원인:**
- `vehicle_id`가 NULL (차량 매칭 실패)
- 차량의 `uvis_device_id`와 로그의 `tid_id` 불일치

**해결:**
1. `vehicle_gps_logs` 테이블에서 `vehicle_id` NULL 확인
2. `tid_id`로 검색하여 해당 단말기 ID 확인
3. `vehicles` 테이블에 `uvis_device_id` 업데이트

**SQL 예시:**
```sql
UPDATE vehicles 
SET uvis_device_id = 'UV123456789', 
    uvis_enabled = true 
WHERE id = 1;
```

### 4. 온도가 이상하게 표시됨

**증상:**
- 온도가 너무 높거나 낮게 표시

**원인:**
- 온도 부호 처리 오류
- 센서 고장

**해결:**
1. `vehicle_temperature_logs` 테이블에서 원본 데이터 확인
2. `tpl_signal_a/b` (부호)와 `tpl_degree_a/b` (값) 확인
3. `temperature_a/b` (변환된 값) 확인

### 5. 자동 새로고침이 작동 안 함

**증상:**
- 자동 새로고침 체크했지만 데이터가 갱신 안 됨

**원인:**
- 브라우저 탭이 백그라운드 상태
- 네트워크 연결 끊김

**해결:**
1. 브라우저 탭을 활성 상태로 유지
2. F12 개발자 도구에서 Network 탭 확인
3. "새로고침" 버튼 수동 클릭하여 테스트

---

## 추가 개선 사항

### 향후 구현 예정
- [ ] 지도 뷰 (Google Maps / Kakao Maps 연동)
- [ ] 온도 이상 알림 (임계값 설정)
- [ ] GPS 경로 히스토리 (시간대별 이동 경로)
- [ ] 실시간 알림 (WebSocket/SSE)
- [ ] 엑셀 내보내기 (GPS/온도 로그)
- [ ] 차량 그룹 관리 (지역별/노선별)

---

## 결론

### ✅ 완료된 작업
1. ✅ UVIS API 3종 연동 (인증키, GPS, 온도)
2. ✅ 데이터베이스 4개 테이블 생성
3. ✅ 백엔드 API 10개+ 엔드포인트 구현
4. ✅ 프론트엔드 실시간 모니터링 컴포넌트
5. ✅ 자동 새로고침 및 동기화 기능
6. ✅ API 호출 로깅 및 디버깅

### 🎯 사용자 혜택
- 📡 **실시간 모니터링**: 차량 위치 및 온도 실시간 확인
- 🚛 **효율적 관제**: 시동 ON/OFF, 속도, 온도 한눈에 파악
- 🔄 **자동 동기화**: 10초/30초/1분/5분 간격 자동 갱신
- 🌡️ **온도 관리**: 냉동/냉장 온도 이상 즉시 감지
- 📊 **통계 대시보드**: 전체 차량, 시동 ON, GPS 활성 등 통계

### 🚀 기술 성과
- **FastAPI**: 고성능 비동기 API
- **SQLAlchemy**: ORM 기반 데이터베이스 관리
- **React + TypeScript**: 타입 안전 프론트엔드
- **httpx**: 비동기 HTTP 클라이언트
- **자동 재시도**: 인증키 자동 갱신

---

**🎉 UVIS GPS 실시간 관제 시스템 구현 완료!**
