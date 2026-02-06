#!/bin/bash

# ============================================================================
# IoT 센서 HTTP 수집기 배포 스크립트
# 작성일: 2026-02-05
# 설명: /root/uvis/iot_sensors에 완전한 IoT 센서 시스템 배포
# ============================================================================

set -e  # 오류 시 중단

echo "========================================================================"
echo "🚀 IoT 센서 시스템 배포 시작"
echo "========================================================================"
echo ""

# 1. 작업 디렉토리 생성 및 이동
TARGET_DIR="/root/uvis/iot_sensors"
echo "📁 작업 디렉토리: $TARGET_DIR"

if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ 오류: $TARGET_DIR 디렉토리가 없습니다"
    echo "   먼저 기본 구조를 생성해주세요"
    exit 1
fi

cd "$TARGET_DIR"
echo "✅ 디렉토리 이동 완료"
echo ""

# 2. 업데이트된 파일 복사
echo "📦 핵심 파일 업데이트..."

# 2.1 HTTP 수집기 업데이트
cat > http_collector/collector.py << 'ENDOFFILE'
"""
IoT 센서 통합 - HTTP 데이터 수집기 (검증 기능 포함)
2026-02-05

FastAPI 기반 센서 데이터 수집 서버
- 온도, GPS, 도어 센서 데이터 수신
- 실시간 데이터 검증
- 알림 생성 및 전송
"""
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger
import sys
import os

# 현재 디렉토리를 sys.path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    TemperatureSensorData, GPSSensorData, DoorSensorData, 
    HumiditySensorData, AlertLevel
)
from processors.validator import validate_sensor_data
from config import settings

# ============================================================================
# FastAPI 앱 초기화
# ============================================================================

app = FastAPI(
    title="IoT 센서 데이터 수집기",
    description="Cold Chain 차량의 센서 데이터를 수집하고 검증합니다",
    version="2.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 로깅 설정
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)

# 로그 디렉토리 생성
log_dir = os.path.dirname(settings.LOG_FILE)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

logger.add(
    settings.LOG_FILE,
    rotation="500 MB",
    retention="30 days",
    level="INFO"
)

# ============================================================================
# 알림 아이콘 매핑
# ============================================================================

ALERT_ICONS = {
    AlertLevel.INFO: "ℹ️",
    AlertLevel.WARNING: "⚠️",
    AlertLevel.CRITICAL: "🚨"
}

# ============================================================================
# API 엔드포인트
# ============================================================================

@app.get("/")
async def root():
    """서비스 정보"""
    return {
        "service": "IoT 센서 데이터 수집기",
        "version": "2.0.0",
        "status": "active",
        "features": [
            "데이터 검증",
            "온도 임계값 체크",
            "배터리 모니터링",
            "GPS 위치 추적",
            "도어 상태 모니터링"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/sensors/temperature")
async def receive_temperature_data(
    data: List[TemperatureSensorData],
    x_api_key: Optional[str] = Header(None),
    vehicle_type: str = "frozen"
):
    """온도 센서 데이터 수신 및 검증"""
    try:
        logger.info(f"📥 온도 센서 데이터 수신: {len(data)}개")
        
        # API 키 검증 (선택적)
        if settings.HTTP_API_KEY and x_api_key != settings.HTTP_API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        validation_results = []
        alerts = []
        
        for sensor_data in data:
            # 데이터 검증
            validation_result = validate_sensor_data(sensor_data, vehicle_type)
            
            # 로그 출력
            temp_str = f"{sensor_data.temperature}°C"
            vehicle_str = f"[{sensor_data.vehicle_id}]" if sensor_data.vehicle_id else ""
            
            if validation_result["alert_level"]:
                icon = ALERT_ICONS.get(validation_result["alert_level"], "")
                logger.warning(
                    f"{icon} {vehicle_str} {sensor_data.sensor_id}: {temp_str} - "
                    f"{', '.join(validation_result['messages'])}"
                )
                
                # 알림 생성
                alert = {
                    "sensor_id": sensor_data.sensor_id,
                    "vehicle_id": sensor_data.vehicle_id,
                    "alert_level": validation_result["alert_level"],
                    "temperature": sensor_data.temperature,
                    "messages": validation_result["messages"],
                    "timestamp": sensor_data.timestamp.isoformat()
                }
                alerts.append(alert)
            else:
                logger.info(f"✅ {vehicle_str} {sensor_data.sensor_id}: {temp_str}")
            
            validation_results.append({
                "sensor_id": sensor_data.sensor_id,
                "valid": validation_result["valid"],
                "alert_level": validation_result["alert_level"],
                "messages": validation_result["messages"]
            })
        
        return {
            "success": True,
            "message": f"온도 데이터 {len(data)}개 수신 완료",
            "data_count": len(data),
            "validation_results": validation_results,
            "alerts": alerts,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 온도 데이터 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/sensors/data")
async def receive_mixed_sensor_data(
    data: List[Dict[str, Any]],
    x_api_key: Optional[str] = Header(None)
):
    """여러 타입의 센서 데이터 일괄 수신 (레거시 엔드포인트)"""
    try:
        logger.info(f"📥 센서 데이터 수신: {len(data)}개")
        
        # API 키 검증
        if settings.HTTP_API_KEY and x_api_key != settings.HTTP_API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # 각 데이터 출력
        for item in data:
            sensor_id = item.get("sensor_id", "unknown")
            vehicle_id = item.get("vehicle_id", "")
            vehicle_str = f"[{vehicle_id}]" if vehicle_id else ""
            
            if "temperature" in item:
                logger.info(f"🌡️ {vehicle_str} {sensor_id}: {item['temperature']}°C")
            elif "latitude" in item and "longitude" in item:
                logger.info(f"📍 {vehicle_str} {sensor_id}: ({item['latitude']}, {item['longitude']})")
            elif "is_open" in item:
                status = "열림" if item["is_open"] else "닫힘"
                logger.info(f"🚪 {vehicle_str} {sensor_id}: {status}")
        
        return {
            "success": True,
            "message": "데이터 저장 완료",
            "data_count": len(data),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 데이터 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 서버 실행
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 80)
    logger.info("🚀 IoT 센서 HTTP 수집기 시작")
    logger.info(f"📍 서버: {settings.HTTP_COLLECTOR_HOST}:{settings.HTTP_COLLECTOR_PORT}")
    logger.info(f"📖 API 문서: http://{settings.HTTP_COLLECTOR_HOST}:{settings.HTTP_COLLECTOR_PORT}/docs")
    logger.info(f"📁 로그 파일: {settings.LOG_FILE}")
    logger.info("=" * 80)
    
    uvicorn.run(
        app,
        host=settings.HTTP_COLLECTOR_HOST,
        port=settings.HTTP_COLLECTOR_PORT,
        log_level="info"
    )
ENDOFFILE

echo "✅ HTTP 수집기 업데이트 완료"

# 3. 시작 스크립트 생성
cat > start_collector.sh << 'STARTSCRIPT'
#!/bin/bash
# IoT HTTP 수집기 시작 스크립트

cd /root/uvis/iot_sensors

# 가상환경 활성화
source ../venv_iot/bin/activate

# 기존 프로세스 종료
pkill -f "python http_collector/collector.py" 2>/dev/null || true
sleep 2

# 백그라운드 실행
nohup python http_collector/collector.py > collector.log 2>&1 &

echo "✅ HTTP 수집기 시작됨 (PID: $!)"
echo "📁 로그: tail -f /root/uvis/iot_sensors/collector.log"
echo "📖 API 문서: http://localhost:8001/docs"
STARTSCRIPT

chmod +x start_collector.sh
echo "✅ 시작 스크립트 생성 완료"

# 4. 정지 스크립트 생성
cat > stop_collector.sh << 'STOPSCRIPT'
#!/bin/bash
# IoT HTTP 수집기 정지 스크립트

echo "🛑 HTTP 수집기 정지 중..."
pkill -f "python http_collector/collector.py"

if [ $? -eq 0 ]; then
    echo "✅ HTTP 수집기 정지 완료"
else
    echo "ℹ️  실행 중인 수집기가 없습니다"
fi
STOPSCRIPT

chmod +x stop_collector.sh
echo "✅ 정지 스크립트 생성 완료"

# 5. 상태 확인 스크립트 생성
cat > status.sh << 'STATUSSCRIPT'
#!/bin/bash
# IoT 센서 시스템 상태 확인

echo "========================================================================"
echo "📊 IoT 센서 시스템 상태"
echo "========================================================================"
echo ""

echo "1️⃣ HTTP 수집기 프로세스:"
ps aux | grep "[p]ython http_collector/collector.py" || echo "   ⚠️  실행 중이 아님"
echo ""

echo "2️⃣ 포트 8001 상태:"
ss -tlnp | grep ":8001" || echo "   ⚠️  포트가 열려있지 않음"
echo ""

echo "3️⃣ 최근 로그 (마지막 10줄):"
if [ -f "collector.log" ]; then
    tail -10 collector.log
else
    echo "   ℹ️  로그 파일이 없습니다"
fi
echo ""

echo "========================================================================"
STATUSSCRIPT

chmod +x status.sh
echo "✅ 상태 확인 스크립트 생성 완료"

echo ""
echo "========================================================================"
echo "✅ 배포 완료!"
echo "========================================================================"
echo ""
echo "📋 다음 단계:"
echo ""
echo "1️⃣ HTTP 수집기 시작:"
echo "   ./start_collector.sh"
echo ""
echo "2️⃣ 상태 확인:"
echo "   ./status.sh"
echo ""
echo "3️⃣ 센서 시뮬레이터 실행 (다른 터미널):"
echo "   cd /root/uvis/iot_sensors"
echo "   source ../venv_iot/bin/activate"
echo "   python tests/sensor_simulator.py --vehicles 3 --interval 10"
echo ""
echo "4️⃣ 로그 실시간 확인:"
echo "   tail -f collector.log"
echo ""
echo "5️⃣ API 문서:"
echo "   http://YOUR_SERVER_IP:8001/docs"
echo ""
echo "🛑 수집기 정지:"
echo "   ./stop_collector.sh"
echo ""
echo "========================================================================"
