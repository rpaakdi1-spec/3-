"""
IoT 센서 통합 - HTTP 데이터 수집기
2026-02-05

REST API로 센서 데이터를 수집합니다.
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
from loguru import logger

from config import settings
from models import (
    SensorDataUpload, SensorDataResponse,
    TemperatureSensorData, GPSSensorData, 
    DoorSensorData, HumiditySensorData
)


app = FastAPI(
    title="IoT Sensor Data Collector",
    description="센서 데이터 수집 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# 인증
# ============================================================================

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """API 키 검증"""
    if settings.HTTP_API_KEY and x_api_key != settings.HTTP_API_KEY:
        raise HTTPException(status_code=403, detail="유효하지 않은 API 키")
    return x_api_key


# ============================================================================
# API 엔드포인트
# ============================================================================

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": "IoT Sensor Data Collector",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/sensors/temperature", response_model=SensorDataResponse)
async def upload_temperature_data(
    data: list[TemperatureSensorData],
    api_key: str = Depends(verify_api_key)
):
    """
    온도 센서 데이터 업로드
    
    - **data**: 온도 센서 데이터 리스트
    """
    try:
        logger.info(f"온도 데이터 수신: {len(data)}개")
        
        # 데이터 처리 (DB 저장 등)
        for sensor_data in data:
            logger.debug(f"온도: {sensor_data.sensor_id} | {sensor_data.temperature}°C")
            # TODO: DB 저장 로직
            
        return SensorDataResponse(
            success=True,
            message="온도 데이터 저장 완료",
            data_count=len(data)
        )
    except Exception as e:
        logger.error(f"온도 데이터 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/sensors/gps", response_model=SensorDataResponse)
async def upload_gps_data(
    data: list[GPSSensorData],
    api_key: str = Depends(verify_api_key)
):
    """
    GPS 센서 데이터 업로드
    
    - **data**: GPS 센서 데이터 리스트
    """
    try:
        logger.info(f"GPS 데이터 수신: {len(data)}개")
        
        for sensor_data in data:
            logger.debug(
                f"GPS: {sensor_data.sensor_id} | "
                f"위치: ({sensor_data.latitude}, {sensor_data.longitude})"
            )
            # TODO: DB 저장 로직
            
        return SensorDataResponse(
            success=True,
            message="GPS 데이터 저장 완료",
            data_count=len(data)
        )
    except Exception as e:
        logger.error(f"GPS 데이터 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/sensors/door", response_model=SensorDataResponse)
async def upload_door_data(
    data: list[DoorSensorData],
    api_key: str = Depends(verify_api_key)
):
    """
    도어 센서 데이터 업로드
    
    - **data**: 도어 센서 데이터 리스트
    """
    try:
        logger.info(f"도어 데이터 수신: {len(data)}개")
        
        for sensor_data in data:
            status = "열림" if sensor_data.is_open else "닫힘"
            logger.debug(f"도어: {sensor_data.sensor_id} | {status}")
            # TODO: DB 저장 로직
            
        return SensorDataResponse(
            success=True,
            message="도어 데이터 저장 완료",
            data_count=len(data)
        )
    except Exception as e:
        logger.error(f"도어 데이터 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/sensors/batch", response_model=SensorDataResponse)
async def upload_batch_data(
    upload: SensorDataUpload,
    api_key: str = Depends(verify_api_key)
):
    """
    다중 센서 데이터 일괄 업로드
    
    - **upload**: 센서 데이터 업로드 요청 (API 키 포함)
    """
    try:
        logger.info(f"배치 데이터 수신: {len(upload.data)}개")
        
        # 데이터 타입별 분류
        temp_data = []
        gps_data = []
        door_data = []
        
        for sensor_data in upload.data:
            if isinstance(sensor_data, TemperatureSensorData):
                temp_data.append(sensor_data)
            elif isinstance(sensor_data, GPSSensorData):
                gps_data.append(sensor_data)
            elif isinstance(sensor_data, DoorSensorData):
                door_data.append(sensor_data)
                
        logger.info(
            f"분류 완료: 온도 {len(temp_data)}개, "
            f"GPS {len(gps_data)}개, 도어 {len(door_data)}개"
        )
        
        # TODO: 타입별 DB 저장 로직
        
        return SensorDataResponse(
            success=True,
            message="배치 데이터 저장 완료",
            data_count=len(upload.data)
        )
    except Exception as e:
        logger.error(f"배치 데이터 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 메인 실행
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("HTTP 데이터 수집기 시작...")
    logger.info(f"주소: http://{settings.HTTP_COLLECTOR_HOST}:{settings.HTTP_COLLECTOR_PORT}")
    logger.info(f"API 문서: http://{settings.HTTP_COLLECTOR_HOST}:{settings.HTTP_COLLECTOR_PORT}/docs")
    
    uvicorn.run(
        app,
        host=settings.HTTP_COLLECTOR_HOST,
        port=settings.HTTP_COLLECTOR_PORT,
        log_level="info"
    )
