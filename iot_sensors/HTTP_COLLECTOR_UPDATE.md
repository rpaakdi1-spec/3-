# HTTP 수집기 업데이트 완료 ✅

## 📦 업데이트 내용

### 1. HTTP 수집기 - 검증 기능 통합 (v2.0.0)

**파일**: `http_collector/collector.py`

**주요 기능**:
- ✅ 온도 센서 데이터 검증 (`/api/v1/sensors/temperature`)
- ✅ GPS 센서 데이터 검증 (`/api/v1/sensors/gps`)
- ✅ 도어 센서 데이터 검증 (`/api/v1/sensors/door`)
- ✅ 습도 센서 데이터 검증 (`/api/v1/sensors/humidity`)
- ✅ 레거시 엔드포인트 호환 (`/api/v1/sensors/data`)

**검증 로직**:
- 온도 임계값 체크 (냉동/냉장/상온)
- 배터리 잔량 모니터링 (20% 경고, 10% 위험)
- GPS 좌표 유효성 검증
- 도어 열림 시간 체크 (5분 경고, 10분 위험)
- 타임스탬프 지연 검증

**알림 시스템**:
- 3단계 알림 레벨: INFO, WARNING, CRITICAL
- 실시간 로그 출력 (이모지 포함)
- 알림 데이터 JSON 응답 포함

---

## 🚀 서버 배포 방법

### Option A: 한 번에 배포 (권장)

서버에서 다음 명령어를 복사해서 실행하세요:

```bash
cd /root/uvis/iot_sensors

# 배포 스크립트 다운로드 (GitHub에서)
curl -o deploy_to_server.sh https://raw.githubusercontent.com/rpaakdi1-spec/3-/main/iot_sensors/deploy_to_server.sh

# 실행 권한 부여
chmod +x deploy_to_server.sh

# 배포 실행
bash deploy_to_server.sh
```

### Option B: 수동 배포

#### 1. HTTP 수집기 파일 업데이트

```bash
cd /root/uvis/iot_sensors

cat > http_collector/collector.py << 'ENDOFFILE'
# [전체 코드는 deploy_to_server.sh 참조]
ENDOFFILE
```

#### 2. 시작/정지 스크립트 생성

```bash
# start_collector.sh
cat > start_collector.sh << 'SCRIPT'
#!/bin/bash
cd /root/uvis/iot_sensors
source ../venv_iot/bin/activate
pkill -f "python http_collector/collector.py" 2>/dev/null || true
sleep 2
nohup python http_collector/collector.py > collector.log 2>&1 &
echo "✅ HTTP 수집기 시작됨 (PID: $!)"
SCRIPT

chmod +x start_collector.sh

# stop_collector.sh
cat > stop_collector.sh << 'SCRIPT'
#!/bin/bash
pkill -f "python http_collector/collector.py"
echo "✅ HTTP 수집기 정지 완료"
SCRIPT

chmod +x stop_collector.sh

# status.sh
cat > status.sh << 'SCRIPT'
#!/bin/bash
echo "📊 HTTP 수집기 상태:"
ps aux | grep "[p]ython http_collector/collector.py"
ss -tlnp | grep ":8001"
tail -10 collector.log 2>/dev/null
SCRIPT

chmod +x status.sh
```

---

## 📋 실행 가이드

### 1️⃣ HTTP 수집기 시작

```bash
cd /root/uvis/iot_sensors
./start_collector.sh
```

**또는 직접 실행**:
```bash
cd /root/uvis/iot_sensors
source ../venv_iot/bin/activate
nohup python http_collector/collector.py > collector.log 2>&1 &
```

### 2️⃣ 상태 확인

```bash
./status.sh
```

**또는 개별 확인**:
```bash
# 프로세스 확인
ps aux | grep collector.py

# 포트 확인
ss -tlnp | grep 8001

# 로그 확인
tail -f collector.log
```

### 3️⃣ 센서 시뮬레이터 실행 (새 터미널)

```bash
cd /root/uvis/iot_sensors
source ../venv_iot/bin/activate
python tests/sensor_simulator.py --vehicles 3 --interval 10
```

### 4️⃣ API 테스트

**브라우저에서 접속**:
- API 문서: `http://YOUR_SERVER_IP:8001/docs`
- 헬스 체크: `http://YOUR_SERVER_IP:8001/health`

**curl로 테스트**:
```bash
# 헬스 체크
curl http://localhost:8001/health

# 온도 데이터 전송
curl -X POST "http://localhost:8001/api/v1/sensors/temperature" \
  -H "Content-Type: application/json" \
  -d '[{
    "sensor_id": "TEMP001",
    "vehicle_id": "V001",
    "temperature": -9.5,
    "battery_level": 85
  }]'
```

### 5️⃣ 수집기 정지

```bash
./stop_collector.sh
```

---

## 📊 예상 로그 출력

### 정상 온도
```
2026-02-05 10:30:15 | INFO     | collector:receive_temperature_data - 📥 온도 센서 데이터 수신: 3개
2026-02-05 10:30:15 | INFO     | collector:receive_temperature_data - ✅ [V001] TEMP001: -19.2°C
2026-02-05 10:30:15 | INFO     | collector:receive_temperature_data - ✅ [V002] TEMP002: -22.5°C
2026-02-05 10:30:15 | INFO     | collector:receive_temperature_data - ✅ [V003] TEMP003: -18.1°C
```

### 이상 온도 (경고)
```
2026-02-05 10:30:25 | WARNING  | collector:receive_temperature_data - ⚠️ [V001] TEMP001: -26.8°C - 온도 경고: -26.8°C (정상 범위: -25.0~-18.0°C)
```

### 이상 온도 (위험)
```
2026-02-05 10:30:35 | WARNING  | collector:receive_temperature_data - 🚨 [V002] TEMP002: -9.5°C - 온도 위험: -9.5°C (정상 범위: -25.0~-18.0°C)
```

---

## 🔧 트러블슈팅

### 문제 1: 수집기가 시작되지 않음

**확인**:
```bash
cd /root/uvis/iot_sensors
source ../venv_iot/bin/activate
python http_collector/collector.py
```

**일반적인 원인**:
- 가상환경 미활성화
- 의존성 미설치 (`pip install -r requirements_iot.txt`)
- 포트 8001 이미 사용 중

### 문제 2: 센서 시뮬레이터 연결 실패

**확인**:
```bash
# HTTP 수집기가 실행 중인지 확인
ss -tlnp | grep 8001

# 로컬 테스트
curl http://localhost:8001/health
```

### 문제 3: 방화벽 차단

```bash
# 포트 8001 열기
firewall-cmd --permanent --add-port=8001/tcp
firewall-cmd --reload
firewall-cmd --list-ports
```

---

## 📈 다음 단계 (Week 2)

현재 완료:
- ✅ HTTP 수집기 구현
- ✅ 데이터 검증 로직
- ✅ 알림 생성
- ✅ 센서 시뮬레이터

Week 2 계획:
- ⏳ PostgreSQL 데이터베이스 저장
- ⏳ Redis Streams 실시간 처리
- ⏳ 알림 전송 (Telegram, Email, SMS)
- ⏳ 배치 저장 최적화

---

## 📞 지원

- **GitHub**: https://github.com/rpaakdi1-spec/3-
- **문서**: `/root/uvis/iot_sensors/README.md`
- **API 문서**: `http://YOUR_SERVER_IP:8001/docs`

---

**작성일**: 2026-02-05  
**버전**: 2.0.0  
**상태**: ✅ 프로덕션 준비 완료
