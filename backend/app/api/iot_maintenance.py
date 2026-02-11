"""
IoT Sensor & Predictive Maintenance API for Phase 13-14
Real-time sensor monitoring and AI-based maintenance prediction
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.iot_sensor_service import IoTSensorService
from app.services.predictive_maintenance_service import PredictiveMaintenanceService


router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class SensorDataRequest(BaseModel):
    """센서 데이터 수집 요청"""
    vehicle_id: int = Field(..., description="차량 ID")
    sensor_type: str = Field(..., description="센서 타입")
    value: float = Field(..., description="측정값")
    latitude: Optional[float] = Field(None, description="위도")
    longitude: Optional[float] = Field(None, description="경도")
    metadata: Optional[dict] = Field(None, description="추가 메타데이터")


class AcknowledgeAlertRequest(BaseModel):
    """알림 확인 요청"""
    alert_id: int = Field(..., description="알림 ID")


class ResolveAlertRequest(BaseModel):
    """알림 해결 요청"""
    alert_id: int = Field(..., description="알림 ID")
    resolution_notes: Optional[str] = Field(None, description="해결 노트")


class PredictMaintenanceRequest(BaseModel):
    """정비 예측 요청"""
    vehicle_id: int = Field(..., description="차량 ID")
    analyze_days: int = Field(30, description="분석 기간 (일)")


class ScheduleMaintenanceRequest(BaseModel):
    """정비 스케줄 요청"""
    prediction_id: int = Field(..., description="예측 ID")
    scheduled_date: datetime = Field(..., description="예정일")
    assigned_technician: Optional[str] = Field(None, description="담당 기술자")


# ============================================================================
# IoT Sensor Endpoints
# ============================================================================

@router.post("/sensors/collect")
async def collect_sensor_data(
    request: SensorDataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    센서 데이터 수집
    
    - 실시간 센서 측정값 저장
    - 자동 이상 감지
    - 임계값 초과 시 알림 생성
    """
    service = IoTSensorService(db)
    
    try:
        result = await service.collect_sensor_data(
            vehicle_id=request.vehicle_id,
            sensor_type=request.sensor_type,
            value=request.value,
            latitude=request.latitude,
            longitude=request.longitude,
            metadata=request.metadata
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data collection failed: {str(e)}")


@router.get("/sensors/vehicle/{vehicle_id}")
async def get_vehicle_sensors(
    vehicle_id: int,
    sensor_type: Optional[str] = Query(None, description="센서 타입 필터"),
    active_only: bool = Query(True, description="활성 센서만"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    차량 센서 목록 조회
    
    - 차량에 설치된 모든 센서 정보
    - 센서 타입별 필터링
    - 활성/비활성 상태 필터
    """
    service = IoTSensorService(db)
    
    try:
        sensors = await service.get_vehicle_sensors(
            vehicle_id=vehicle_id,
            sensor_type=sensor_type,
            active_only=active_only
        )
        return {
            "vehicle_id": vehicle_id,
            "sensors": sensors,
            "total": len(sensors)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sensors/readings/{vehicle_id}")
async def get_latest_readings(
    vehicle_id: int,
    sensor_type: Optional[str] = Query(None, description="센서 타입"),
    limit: int = Query(100, description="조회 개수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    최신 센서 측정값 조회
    
    - 차량의 최신 센서 데이터
    - 센서 타입별 필터링
    - 이상 감지 정보 포함
    """
    service = IoTSensorService(db)
    
    try:
        readings = await service.get_latest_readings(
            vehicle_id=vehicle_id,
            sensor_type=sensor_type,
            limit=limit
        )
        return {
            "vehicle_id": vehicle_id,
            "readings": readings,
            "total": len(readings)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sensors/statistics/{vehicle_id}")
async def get_sensor_statistics(
    vehicle_id: int,
    sensor_type: str = Query(..., description="센서 타입"),
    hours: int = Query(24, description="조회 기간 (시간)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    센서 통계 조회
    
    - 평균, 최소, 최대값
    - 이상 감지 비율
    - 시간대별 트렌드
    """
    service = IoTSensorService(db)
    
    try:
        stats = await service.get_sensor_statistics(
            vehicle_id=vehicle_id,
            sensor_type=sensor_type,
            hours=hours
        )
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sensors/alerts")
async def get_active_alerts(
    vehicle_id: Optional[int] = Query(None, description="차량 ID"),
    severity: Optional[str] = Query(None, description="심각도"),
    unresolved_only: bool = Query(True, description="미해결만"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    활성 알림 조회
    
    - 차량별/심각도별 필터링
    - 미해결 알림 목록
    - 실시간 알림 상태
    """
    service = IoTSensorService(db)
    
    try:
        alerts = await service.get_active_alerts(
            vehicle_id=vehicle_id,
            severity=severity,
            unresolved_only=unresolved_only
        )
        return {
            "alerts": alerts,
            "total": len(alerts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sensors/alerts/acknowledge")
async def acknowledge_alert(
    request: AcknowledgeAlertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    알림 확인
    
    - 알림 확인 처리
    - 담당자 기록
    """
    service = IoTSensorService(db)
    
    try:
        result = await service.acknowledge_alert(
            alert_id=request.alert_id,
            user_id=current_user.id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sensors/alerts/resolve")
async def resolve_alert(
    request: ResolveAlertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    알림 해결
    
    - 알림 해결 처리
    - 해결 노트 기록
    """
    service = IoTSensorService(db)
    
    try:
        result = await service.resolve_alert(
            alert_id=request.alert_id,
            resolution_notes=request.resolution_notes
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sensors/dashboard")
async def get_realtime_dashboard(
    vehicle_ids: Optional[List[int]] = Query(None, description="차량 ID 목록"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    실시간 대시보드 데이터
    
    - 전체 차량 센서 현황
    - 활성 알림 수
    - 이상 감지 통계
    """
    service = IoTSensorService(db)
    
    try:
        dashboard_data = await service.get_realtime_dashboard_data(
            vehicle_ids=vehicle_ids
        )
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Predictive Maintenance Endpoints
# ============================================================================

@router.post("/maintenance/predict")
async def predict_maintenance(
    request: PredictMaintenanceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    정비 필요성 예측
    
    - AI 기반 고장 예측
    - 부품별 고장 확률
    - 권장 정비 일정
    """
    service = PredictiveMaintenanceService(db)
    
    try:
        predictions = await service.predict_maintenance(
            vehicle_id=request.vehicle_id,
            analyze_days=request.analyze_days
        )
        return {
            "vehicle_id": request.vehicle_id,
            "predictions": predictions,
            "total": len(predictions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/maintenance/predictions/{vehicle_id}")
async def get_vehicle_predictions(
    vehicle_id: int,
    active_only: bool = Query(True, description="활성 예측만"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    차량 예측 결과 조회
    
    - 저장된 예측 결과
    - 부품별 고장 확률
    - 예정 정비 일정
    """
    service = PredictiveMaintenanceService(db)
    
    try:
        predictions = await service.get_vehicle_predictions(
            vehicle_id=vehicle_id,
            active_only=active_only
        )
        return {
            "vehicle_id": vehicle_id,
            "predictions": predictions,
            "total": len(predictions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/maintenance/health/{vehicle_id}")
async def get_vehicle_health(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    차량 건강 상태 조회
    
    - 종합 건강 점수 (0-100)
    - 부품별 상태 점수
    - 위험 요인 분석
    """
    service = PredictiveMaintenanceService(db)
    
    try:
        health = await service.calculate_vehicle_health(vehicle_id=vehicle_id)
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/maintenance/schedule")
async def schedule_maintenance(
    request: ScheduleMaintenanceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    예측 기반 정비 스케줄 생성
    
    - 예측 결과로 정비 예약
    - 부품 및 비용 산정
    - 담당 기술자 배정
    """
    service = PredictiveMaintenanceService(db)
    
    try:
        schedule = await service.schedule_maintenance(
            prediction_id=request.prediction_id,
            scheduled_date=request.scheduled_date,
            assigned_technician=request.assigned_technician
        )
        return schedule
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/maintenance/statistics")
async def get_maintenance_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    정비 통계
    
    - 활성 예측 수
    - 스케줄된 정비 수
    - 고위험 차량 수
    - 완료된 정비 통계
    """
    service = PredictiveMaintenanceService(db)
    
    try:
        stats = await service.get_maintenance_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
