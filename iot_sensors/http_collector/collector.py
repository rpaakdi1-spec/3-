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

# 상위 디렉토리의 모듈 임포트를 위한 경로 추가
sys.path.insert(0, '..')

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
    """
    온도 센서 데이터 수신 및 검증
    
    Args:
        data: 온도 센서 데이터 리스트
        x_api_key: API 키 (헤더)
        vehicle_type: 차량 타입 (frozen/chilled/ambient)
    """
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


@app.post("/api/v1/sensors/gps")
async def receive_gps_data(
    data: List[GPSSensorData],
    x_api_key: Optional[str] = Header(None)
):
    """GPS 센서 데이터 수신"""
    try:
        logger.info(f"📥 GPS 센서 데이터 수신: {len(data)}개")
        
        # API 키 검증
        if settings.HTTP_API_KEY and x_api_key != settings.HTTP_API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        validation_results = []
        
        for sensor_data in data:
            # GPS 데이터 검증
            validation_result = validate_sensor_data(sensor_data)
            
            # 로그 출력
            logger.info(
                f"📍 {sensor_data.sensor_id}: "
                f"({sensor_data.latitude:.6f}, {sensor_data.longitude:.6f})"
            )
            
            validation_results.append({
                "sensor_id": sensor_data.sensor_id,
                "valid": validation_result["valid"],
                "messages": validation_result["messages"]
            })
        
        return {
            "success": True,
            "message": f"GPS 데이터 {len(data)}개 수신 완료",
            "data_count": len(data),
            "validation_results": validation_results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ GPS 데이터 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/sensors/door")
async def receive_door_data(
    data: List[DoorSensorData],
    x_api_key: Optional[str] = Header(None)
):
    """도어 센서 데이터 수신"""
    try:
        logger.info(f"📥 도어 센서 데이터 수신: {len(data)}개")
        
        # API 키 검증
        if settings.HTTP_API_KEY and x_api_key != settings.HTTP_API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        validation_results = []
        alerts = []
        
        for sensor_data in data:
            # 도어 데이터 검증
            validation_result = validate_sensor_data(sensor_data)
            
            # 로그 출력
            status = "🚪 열림" if sensor_data.is_open else "🔒 닫힘"
            duration_str = f" ({sensor_data.duration}초)" if sensor_data.duration else ""
            
            if validation_result["alert_level"]:
                icon = ALERT_ICONS.get(validation_result["alert_level"], "")
                logger.warning(
                    f"{icon} {sensor_data.sensor_id}: {status}{duration_str} - "
                    f"{', '.join(validation_result['messages'])}"
                )
                
                # 알림 생성
                alert = {
                    "sensor_id": sensor_data.sensor_id,
                    "vehicle_id": sensor_data.vehicle_id,
                    "alert_level": validation_result["alert_level"],
                    "is_open": sensor_data.is_open,
                    "duration": sensor_data.duration,
                    "messages": validation_result["messages"],
                    "timestamp": sensor_data.timestamp.isoformat()
                }
                alerts.append(alert)
            else:
                logger.info(f"{sensor_data.sensor_id}: {status}{duration_str}")
            
            validation_results.append({
                "sensor_id": sensor_data.sensor_id,
                "valid": validation_result["valid"],
                "alert_level": validation_result["alert_level"],
                "messages": validation_result["messages"]
            })
        
        return {
            "success": True,
            "message": f"도어 데이터 {len(data)}개 수신 완료",
            "data_count": len(data),
            "validation_results": validation_results,
            "alerts": alerts,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 도어 데이터 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/sensors/humidity")
async def receive_humidity_data(
    data: List[HumiditySensorData],
    x_api_key: Optional[str] = Header(None)
):
    """습도 센서 데이터 수신"""
    try:
        logger.info(f"📥 습도 센서 데이터 수신: {len(data)}개")
        
        # API 키 검증
        if settings.HTTP_API_KEY and x_api_key != settings.HTTP_API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        for sensor_data in data:
            logger.info(
                f"💧 {sensor_data.sensor_id}: {sensor_data.humidity}%"
            )
        
        return {
            "success": True,
            "message": f"습도 데이터 {len(data)}개 수신 완료",
            "data_count": len(data),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 습도 데이터 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/sensors/data")
async def receive_mixed_sensor_data(
    data: List[Dict[str, Any]],
    x_api_key: Optional[str] = Header(None)
):
    """
    여러 타입의 센서 데이터 일괄 수신 (레거시 엔드포인트)
    센서 시뮬레이터와의 호환성을 위해 유지
    """
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
