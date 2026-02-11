"""
Phase 11-B: Traffic Information API
교통 정보 연동 API 엔드포인트
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.traffic import TrafficLevel, AlertType, RouteStatus
from app.services.traffic_api_service import TrafficAPIService
from app.services.route_optimization_service import RouteOptimizationService


router = APIRouter()


# ==================== Pydantic Schemas ====================

class RouteOptimizationRequest(BaseModel):
    """경로 최적화 요청"""
    origin_lat: float
    origin_lng: float
    destination_lat: float
    destination_lng: float
    dispatch_id: Optional[int] = None


class RouteComparisonRequest(BaseModel):
    """경로 비교 요청"""
    route_ids: List[int]


class TrafficAlertCreate(BaseModel):
    """교통 알림 생성"""
    alert_type: AlertType
    title: str
    description: Optional[str] = None
    road_name: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    severity: str = "MEDIUM"


class RouteHistoryComplete(BaseModel):
    """경로 이력 완료"""
    actual_distance: float
    actual_duration: int
    fuel_consumed: Optional[float] = None


# ==================== 교통 정보 API ====================

@router.get("/traffic/conditions")
async def get_traffic_conditions(
    road_name: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    실시간 교통 상황 조회
    
    - **road_name**: 도로명 (선택)
    - **limit**: 조회 개수
    """
    from app.models.traffic import TrafficCondition
    
    query = db.query(TrafficCondition)
    
    if road_name:
        query = query.filter(TrafficCondition.road_name.contains(road_name))
    
    conditions = query.order_by(
        TrafficCondition.collected_at.desc()
    ).limit(limit).all()
    
    return {
        "conditions": [
            {
                "id": c.id,
                "road_name": c.road_name,
                "section_name": c.section_name,
                "traffic_level": c.traffic_level.value,
                "speed": c.speed,
                "travel_time": c.travel_time,
                "api_provider": c.api_provider,
                "collected_at": c.collected_at.isoformat()
            }
            for c in conditions
        ],
        "total": len(conditions)
    }


@router.get("/traffic/alerts")
async def get_traffic_alerts(
    is_active: bool = True,
    alert_type: Optional[AlertType] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    교통 알림 조회
    
    - **is_active**: 활성 여부
    - **alert_type**: 알림 타입
    - **limit**: 조회 개수
    """
    from app.models.traffic import TrafficAlert
    from sqlalchemy import and_
    
    query = db.query(TrafficAlert).filter(
        TrafficAlert.is_active == is_active
    )
    
    if alert_type:
        query = query.filter(TrafficAlert.alert_type == alert_type)
    
    alerts = query.order_by(
        TrafficAlert.created_at.desc()
    ).limit(limit).all()
    
    return {
        "alerts": [
            {
                "id": a.id,
                "alert_type": a.alert_type.value,
                "title": a.title,
                "description": a.description,
                "road_name": a.road_name,
                "location_lat": a.location_lat,
                "location_lng": a.location_lng,
                "severity": a.severity,
                "start_time": a.start_time.isoformat() if a.start_time else None,
                "end_time": a.end_time.isoformat() if a.end_time else None,
                "is_active": a.is_active,
                "created_at": a.created_at.isoformat()
            }
            for a in alerts
        ],
        "total": len(alerts)
    }


@router.post("/traffic/alerts")
async def create_traffic_alert(
    alert_data: TrafficAlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    교통 알림 생성
    
    관리자가 수동으로 교통 알림을 생성합니다.
    """
    service = TrafficAPIService(db)
    
    alert = service.create_traffic_alert(
        alert_type=alert_data.alert_type,
        title=alert_data.title,
        description=alert_data.description,
        road_name=alert_data.road_name,
        location_lat=alert_data.location_lat,
        location_lng=alert_data.location_lng,
        severity=alert_data.severity
    )
    
    return {
        "message": "Traffic alert created",
        "alert_id": alert.id
    }


@router.get("/traffic/statistics")
async def get_traffic_statistics(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    교통 통계
    
    - **days**: 조회 기간 (일)
    """
    from app.models.traffic import TrafficCondition
    from sqlalchemy import func
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 혼잡도별 통계
    traffic_stats = db.query(
        TrafficCondition.traffic_level,
        func.count(TrafficCondition.id).label('count'),
        func.avg(TrafficCondition.speed).label('avg_speed')
    ).filter(
        TrafficCondition.collected_at >= start_date
    ).group_by(
        TrafficCondition.traffic_level
    ).all()
    
    return {
        "period_days": days,
        "traffic_levels": [
            {
                "level": stat.traffic_level.value if stat.traffic_level else "UNKNOWN",
                "count": stat.count,
                "avg_speed": round(stat.avg_speed, 1) if stat.avg_speed else 0
            }
            for stat in traffic_stats
        ]
    }


# ==================== 경로 최적화 API ====================

@router.post("/routes/optimize")
async def optimize_route(
    route_data: RouteOptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    경로 최적화
    
    출발지와 목적지를 기반으로 최적 경로를 계산합니다.
    """
    service = RouteOptimizationService(db)
    
    route = service.optimize_route(
        origin_lat=route_data.origin_lat,
        origin_lng=route_data.origin_lng,
        destination_lat=route_data.destination_lat,
        destination_lng=route_data.destination_lng,
        dispatch_id=route_data.dispatch_id
    )
    
    return {
        "route_id": route.id,
        "distance": route.distance,
        "duration": route.duration,
        "duration_in_traffic": route.duration_in_traffic,
        "traffic_level": route.traffic_level.value if route.traffic_level else None,
        "toll_fee": route.toll_fee,
        "fuel_cost": route.fuel_cost,
        "optimization_score": route.optimization_score,
        "is_optimal": route.is_optimal,
        "api_provider": route.api_provider
    }


@router.post("/routes/alternatives")
async def get_alternative_routes(
    route_data: RouteOptimizationRequest,
    count: int = 3,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    대안 경로 조회
    
    여러 경로 옵션을 제공합니다.
    """
    service = RouteOptimizationService(db)
    
    routes = service.get_alternative_routes(
        origin_lat=route_data.origin_lat,
        origin_lng=route_data.origin_lng,
        destination_lat=route_data.destination_lat,
        destination_lng=route_data.destination_lng,
        count=count
    )
    
    return {
        "routes": [
            {
                "id": r.id,
                "route_name": r.route_name or ("최적 경로" if r.is_optimal else "대안 경로"),
                "distance": r.distance,
                "duration": r.duration,
                "duration_in_traffic": r.duration_in_traffic,
                "traffic_level": r.traffic_level.value if r.traffic_level else None,
                "toll_fee": r.toll_fee,
                "fuel_cost": r.fuel_cost,
                "total_cost": r.toll_fee + (r.fuel_cost or 0),
                "optimization_score": r.optimization_score,
                "is_optimal": r.is_optimal
            }
            for r in routes
        ],
        "total": len(routes)
    }


@router.post("/routes/compare")
async def compare_routes(
    comparison_data: RouteComparisonRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    경로 비교
    
    여러 경로를 비교합니다.
    """
    service = RouteOptimizationService(db)
    
    comparisons = service.compare_routes(comparison_data.route_ids)
    
    return {
        "comparisons": comparisons,
        "total": len(comparisons)
    }


@router.get("/routes/history")
async def get_route_history(
    vehicle_id: Optional[int] = None,
    driver_id: Optional[int] = None,
    days: int = 30,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    경로 이력 조회
    
    - **vehicle_id**: 차량 ID
    - **driver_id**: 드라이버 ID
    - **days**: 조회 기간
    - **limit**: 조회 개수
    """
    from app.models.traffic import RouteHistory
    from sqlalchemy import and_
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(RouteHistory).filter(
        RouteHistory.created_at >= start_date
    )
    
    if vehicle_id:
        query = query.filter(RouteHistory.vehicle_id == vehicle_id)
    
    if driver_id:
        query = query.filter(RouteHistory.driver_id == driver_id)
    
    histories = query.order_by(
        RouteHistory.created_at.desc()
    ).limit(limit).all()
    
    return {
        "histories": [
            {
                "id": h.id,
                "dispatch_id": h.dispatch_id,
                "vehicle_id": h.vehicle_id,
                "driver_id": h.driver_id,
                "actual_distance": h.actual_distance,
                "actual_duration": h.actual_duration,
                "fuel_consumed": h.fuel_consumed,
                "distance_variance": h.distance_variance,
                "duration_variance": h.duration_variance,
                "started_at": h.started_at.isoformat() if h.started_at else None,
                "completed_at": h.completed_at.isoformat() if h.completed_at else None
            }
            for h in histories
        ],
        "total": len(histories)
    }


@router.put("/routes/history/{history_id}/complete")
async def complete_route_history(
    history_id: int,
    completion_data: RouteHistoryComplete,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    경로 이력 완료
    
    실제 주행 정보를 기록합니다.
    """
    service = RouteOptimizationService(db)
    
    history = service.complete_route_history(
        history_id=history_id,
        actual_distance=completion_data.actual_distance,
        actual_duration=completion_data.actual_duration,
        fuel_consumed=completion_data.fuel_consumed
    )
    
    if not history:
        raise HTTPException(status_code=404, detail="Route history not found")
    
    return {
        "message": "Route history completed",
        "history_id": history.id,
        "distance_variance": history.distance_variance,
        "duration_variance": history.duration_variance
    }


@router.get("/routes/statistics")
async def get_route_statistics(
    vehicle_id: Optional[int] = None,
    driver_id: Optional[int] = None,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    경로 통계
    
    - **vehicle_id**: 차량 ID
    - **driver_id**: 드라이버 ID
    - **days**: 조회 기간
    """
    service = RouteOptimizationService(db)
    
    statistics = service.get_route_statistics(
        vehicle_id=vehicle_id,
        driver_id=driver_id,
        days=days
    )
    
    return statistics
