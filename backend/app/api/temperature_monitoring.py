"""
Temperature Monitoring API
온도 모니터링 API 엔드포인트
Phase 3-A Part 4: 온도 기록 자동 수집
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.temperature_monitoring import TemperatureMonitoringService
from pydantic import BaseModel, Field


router = APIRouter(prefix="/temperature-monitoring", tags=["Temperature Monitoring"])


# ============= Schemas =============

class TemperatureCollectionResponse(BaseModel):
    """온도 수집 결과 응답"""
    success: bool
    collected_count: int
    alerts_created: int
    critical_alerts: int
    critical_alert_details: List[dict] = []
    timestamp: str
    error: Optional[str] = None


class TemperatureHistoryItem(BaseModel):
    """온도 이력 항목"""
    timestamp: str
    sensor: str
    temperature: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class TemperatureStatistics(BaseModel):
    """온도 통계"""
    vehicle_id: int
    period_hours: int
    sensor_a: dict
    sensor_b: dict
    alerts: dict


class TemperatureAlertItem(BaseModel):
    """온도 알림 항목"""
    id: int
    vehicle_id: int
    vehicle_number: Optional[str]
    dispatch_id: Optional[int]
    alert_type: str
    severity: str
    temperature: float
    threshold_min: Optional[float]
    threshold_max: Optional[float]
    detected_at: str
    message: str
    notification_sent: bool


class AlertResolveRequest(BaseModel):
    """알림 해결 요청"""
    notes: Optional[str] = Field(None, description="해결 메모")


# ============= Endpoints =============

@router.post("/collect", response_model=TemperatureCollectionResponse)
async def collect_temperatures(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    모든 차량의 온도 데이터 자동 수집
    
    - UVIS API에서 실시간 온도 데이터 가져오기
    - 임계값 체크 및 알림 생성
    - Critical 알림 즉시 전송
    
    **사용 시나리오:**
    - 스케줄러를 통한 주기적 자동 수집 (예: 5분마다)
    - 수동 온도 데이터 갱신
    """
    service = TemperatureMonitoringService(db)
    result = await service.collect_all_temperatures()
    return result


@router.get("/vehicles/{vehicle_id}/history", response_model=List[TemperatureHistoryItem])
async def get_vehicle_temperature_history(
    vehicle_id: int,
    hours: int = Query(24, ge=1, le=168, description="조회 기간 (시간, 최대 7일)"),
    sensor: Optional[str] = Query(None, regex="^(A|B)$", description="센서 선택 (A, B, 또는 both)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    차량 온도 이력 조회
    
    - 지정된 기간의 온도 이력 조회
    - 센서별 필터링 가능
    - 위치 정보 포함
    
    **Parameters:**
    - **vehicle_id**: 차량 ID
    - **hours**: 조회 기간 (1~168시간, 기본: 24시간)
    - **sensor**: 센서 선택 (A, B, 또는 생략 시 both)
    """
    service = TemperatureMonitoringService(db)
    history = service.get_vehicle_temperature_history(vehicle_id, hours, sensor)
    return history


@router.get("/vehicles/{vehicle_id}/statistics", response_model=TemperatureStatistics)
async def get_vehicle_temperature_statistics(
    vehicle_id: int,
    hours: int = Query(24, ge=1, le=168, description="통계 기간 (시간, 최대 7일)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    차량 온도 통계
    
    - 센서별 최소/최대/평균 온도
    - 샘플 개수
    - 알림 발생 건수
    
    **Parameters:**
    - **vehicle_id**: 차량 ID
    - **hours**: 통계 기간 (1~168시간, 기본: 24시간)
    """
    service = TemperatureMonitoringService(db)
    stats = service.get_temperature_statistics(vehicle_id, hours)
    return stats


@router.get("/alerts/active", response_model=List[TemperatureAlertItem])
async def get_active_temperature_alerts(
    vehicle_id: Optional[int] = Query(None, description="차량 ID (생략 시 전체 조회)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    활성 온도 알림 조회
    
    - 미해결된 온도 알림 목록
    - 차량별 필터링 가능
    - 심각도 및 온도 정보 포함
    
    **Parameters:**
    - **vehicle_id**: 차량 ID (optional, 생략 시 전체 조회)
    """
    service = TemperatureMonitoringService(db)
    alerts = service.get_active_temperature_alerts(vehicle_id)
    return alerts


@router.post("/alerts/{alert_id}/resolve")
async def resolve_temperature_alert(
    alert_id: int,
    request: AlertResolveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    온도 알림 해결 처리
    
    - 알림을 해결됨으로 표시
    - 해결 시각 기록
    - 해결 메모 추가 가능
    
    **Parameters:**
    - **alert_id**: 알림 ID
    - **notes**: 해결 메모 (optional)
    """
    service = TemperatureMonitoringService(db)
    success = await service.resolve_temperature_alert(alert_id, request.notes)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {
        "success": True,
        "message": "Temperature alert resolved successfully",
        "alert_id": alert_id,
        "resolved_at": datetime.utcnow().isoformat()
    }


@router.get("/alerts/statistics")
async def get_alert_statistics(
    hours: int = Query(24, ge=1, le=168, description="통계 기간 (시간)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    온도 알림 통계
    
    - 기간별 알림 발생 건수
    - 심각도별 분류
    - 해결/미해결 상태
    """
    from app.models.vehicle_location import TemperatureAlert
    from sqlalchemy import func
    from datetime import timedelta
    
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # 전체 알림 수
    total_alerts = db.query(func.count(TemperatureAlert.id)).filter(
        TemperatureAlert.detected_at >= start_time
    ).scalar()
    
    # 심각도별
    critical_count = db.query(func.count(TemperatureAlert.id)).filter(
        TemperatureAlert.detected_at >= start_time,
        TemperatureAlert.severity == "CRITICAL"
    ).scalar()
    
    warning_count = db.query(func.count(TemperatureAlert.id)).filter(
        TemperatureAlert.detected_at >= start_time,
        TemperatureAlert.severity == "WARNING"
    ).scalar()
    
    # 해결 상태별
    resolved_count = db.query(func.count(TemperatureAlert.id)).filter(
        TemperatureAlert.detected_at >= start_time,
        TemperatureAlert.is_resolved == True
    ).scalar()
    
    unresolved_count = db.query(func.count(TemperatureAlert.id)).filter(
        TemperatureAlert.detected_at >= start_time,
        TemperatureAlert.is_resolved == False
    ).scalar()
    
    # 알림 유형별
    alert_types = db.query(
        TemperatureAlert.alert_type,
        func.count(TemperatureAlert.id).label("count")
    ).filter(
        TemperatureAlert.detected_at >= start_time
    ).group_by(TemperatureAlert.alert_type).all()
    
    return {
        "period_hours": hours,
        "total_alerts": total_alerts,
        "by_severity": {
            "critical": critical_count,
            "warning": warning_count
        },
        "by_status": {
            "resolved": resolved_count,
            "unresolved": unresolved_count
        },
        "by_type": {alert_type: count for alert_type, count in alert_types},
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/thresholds")
async def get_temperature_thresholds(
    current_user: User = Depends(get_current_user)
):
    """
    온도 임계값 설정 조회
    
    - 차량 유형별 온도 임계값
    - Warning 및 Critical 기준
    """
    from app.services.temperature_monitoring import TemperatureThreshold
    
    return {
        "frozen": {
            "name": "냉동",
            "min": TemperatureThreshold.FROZEN_MIN,
            "max": TemperatureThreshold.FROZEN_MAX,
            "warning_min": TemperatureThreshold.FROZEN_WARNING_MIN,
            "warning_max": TemperatureThreshold.FROZEN_WARNING_MAX
        },
        "chilled": {
            "name": "냉장",
            "min": TemperatureThreshold.CHILLED_MIN,
            "max": TemperatureThreshold.CHILLED_MAX,
            "warning_min": TemperatureThreshold.CHILLED_WARNING_MIN,
            "warning_max": TemperatureThreshold.CHILLED_WARNING_MAX
        },
        "ambient": {
            "name": "상온",
            "min": TemperatureThreshold.AMBIENT_MIN,
            "max": TemperatureThreshold.AMBIENT_MAX
        }
    }
