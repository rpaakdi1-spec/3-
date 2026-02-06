"""
Real-time Telemetry API
Phase 4 Week 3-4: 실시간 차량 텔레메트리 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import json
import asyncio

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.vehicle_telemetry_service import (
    get_telemetry_service,
    TelemetryData,
    VehicleTelemetryService
)

router = APIRouter()


# ============================================================================
# WebSocket Connection Manager
# ============================================================================

class ConnectionManager:
    """WebSocket 연결 관리자"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """모든 연결된 클라이언트에게 브로드캐스트"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


# ============================================================================
# Pydantic Schemas
# ============================================================================

class TelemetryDataInput(BaseModel):
    vehicle_id: int
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    speed: float = Field(default=0.0, ge=0, le=200)
    temperature: Optional[float] = None
    fuel_level: Optional[float] = Field(default=None, ge=0, le=100)
    engine_status: str = Field(default="ON", pattern="^(ON|OFF|IDLE)$")
    timestamp: Optional[datetime] = None


class VehicleStatusSummary(BaseModel):
    total_vehicles: int
    moving: int
    idle: int
    offline: int


# ============================================================================
# WebSocket Endpoint
# ============================================================================

@router.websocket("/ws/telemetry")
async def telemetry_websocket(websocket: WebSocket):
    """
    실시간 텔레메트리 WebSocket
    
    클라이언트가 연결하면 실시간으로 차량 위치, 이상 감지 등의
    데이터를 전송받습니다.
    """
    await manager.connect(websocket)
    try:
        while True:
            # 클라이언트로부터 메시지 수신 (keep-alive)
            data = await websocket.receive_text()
            
            # Ping-pong
            if data == "ping":
                await websocket.send_text("pong")
            
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================================================
# REST API Endpoints
# ============================================================================

@router.post("/telemetry/data", tags=["Telemetry"])
def submit_telemetry_data(
    data: TelemetryDataInput,
    db: Session = Depends(get_db)
):
    """
    텔레메트리 데이터 제출
    
    차량(또는 UVIS 장치)에서 실시간 데이터를 전송합니다.
    - GPS 위치 (latitude, longitude)
    - 속도 (speed)
    - 온도 (temperature, 선택)
    - 연료 (fuel_level, 선택)
    - 엔진 상태 (engine_status)
    """
    try:
        # TelemetryData 객체 생성
        telemetry = TelemetryData(
            vehicle_id=data.vehicle_id,
            latitude=data.latitude,
            longitude=data.longitude,
            speed=data.speed,
            temperature=data.temperature,
            fuel_level=data.fuel_level,
            engine_status=data.engine_status,
            timestamp=data.timestamp or datetime.now()
        )
        
        # 텔레메트리 서비스 처리
        service = get_telemetry_service(db)
        result = service.process_telemetry(telemetry)
        
        # WebSocket 브로드캐스트 (비동기)
        asyncio.create_task(manager.broadcast({
            "type": "telemetry_update",
            "data": telemetry.to_dict(),
            "anomalies": result.get("anomalies", [])
        }))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"텔레메트리 처리 실패: {str(e)}")


@router.get("/telemetry/vehicle/{vehicle_id}", tags=["Telemetry"])
def get_vehicle_telemetry(
    vehicle_id: int,
    minutes: int = Query(60, ge=1, le=1440),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    차량 텔레메트리 히스토리 조회
    
    특정 차량의 최근 N분간 텔레메트리 데이터를 조회합니다.
    - 위치 추적
    - 속도 변화
    - 온도 알림
    """
    service = get_telemetry_service(db)
    return service.get_vehicle_telemetry(vehicle_id, minutes)


@router.get("/telemetry/vehicles/status", tags=["Telemetry"])
def get_all_vehicles_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    전체 차량 실시간 상태 조회
    
    모든 활성 차량의 현재 상태를 조회합니다:
    - moving: 운행 중
    - idle: 정차 중
    - offline: 오프라인
    """
    service = get_telemetry_service(db)
    vehicles = service.get_all_vehicles_status()
    
    # 요약 통계
    summary = VehicleStatusSummary(
        total_vehicles=len(vehicles),
        moving=len([v for v in vehicles if v["status"] == "moving"]),
        idle=len([v for v in vehicles if v["status"] == "idle"]),
        offline=len([v for v in vehicles if v["status"] == "offline"])
    )
    
    return {
        "summary": summary,
        "vehicles": vehicles,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/telemetry/simulate/{vehicle_id}", tags=["Telemetry"])
def simulate_telemetry(
    vehicle_id: int,
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    speed: float = Query(default=60.0, ge=0, le=200),
    temperature: Optional[float] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    텔레메트리 시뮬레이션 (테스트용)
    
    실제 UVIS 장치 없이 텔레메트리 데이터를 시뮬레이션합니다.
    """
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="관리자 권한 필요")
    
    data = TelemetryDataInput(
        vehicle_id=vehicle_id,
        latitude=latitude,
        longitude=longitude,
        speed=speed,
        temperature=temperature
    )
    
    return submit_telemetry_data(data, db)


@router.get("/telemetry/statistics", tags=["Telemetry"])
def get_telemetry_statistics(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    텔레메트리 통계
    
    최근 N시간의 텔레메트리 통계를 조회합니다:
    - 총 데이터 포인트 수
    - 이상 감지 건수
    - 평균 속도
    - 온도 알림 수
    """
    from app.models.vehicle_location import VehicleLocation
    from app.models.vehicle_location import TemperatureAlert
    from datetime import timedelta
    from sqlalchemy import func
    
    since = datetime.now() - timedelta(hours=hours)
    
    # 총 데이터 포인트
    total_points = db.query(func.count(VehicleLocation.id)).filter(
        VehicleLocation.timestamp >= since
    ).scalar()
    
    # 평균 속도
    avg_speed = db.query(func.avg(VehicleLocation.speed)).filter(
        VehicleLocation.timestamp >= since
    ).scalar()
    
    # 온도 알림 수
    temp_alerts = db.query(func.count(TemperatureAlert.id)).filter(
        TemperatureAlert.created_at >= since
    ).scalar()
    
    # 과속 건수 (100 km/h 이상)
    speeding_count = db.query(func.count(VehicleLocation.id)).filter(
        and_(
            VehicleLocation.timestamp >= since,
            VehicleLocation.speed > 100
        )
    ).scalar()
    
    return {
        "period_hours": hours,
        "total_data_points": total_points or 0,
        "average_speed": round(avg_speed, 2) if avg_speed else 0,
        "temperature_alerts": temp_alerts or 0,
        "speeding_incidents": speeding_count or 0,
        "data_quality": "good" if total_points and total_points > hours * 10 else "poor"
    }
