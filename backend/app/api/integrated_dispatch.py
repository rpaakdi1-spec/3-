"""
Phase 12: 통합 배차 API
자동 배차, 차량 지도, 경로 조회, 분석
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.services.integrated_dispatch_service import IntegratedDispatchService
from app.services.dispatch_analytics_service import DispatchAnalyticsService
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()


# ============================================
# Request/Response Models
# ============================================

class AutoDispatchRequest(BaseModel):
    """자동 배차 요청"""
    order_id: int
    apply_rules: bool = True
    simulate: bool = False


class VehicleLocationResponse(BaseModel):
    """차량 위치 응답"""
    vehicle_id: int
    license_plate: str
    driver_name: Optional[str]
    latitude: float
    longitude: float
    status: str
    last_updated: Optional[str]


# ============================================
# API Endpoints
# ============================================

@router.post("/dispatch/auto")
async def auto_dispatch(
    request: AutoDispatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    자동 배차 실행
    
    **기능**:
    - 가용 차량 자동 조회
    - 거리/시간 자동 계산
    - 배차 규칙 자동 적용
    - 최적 기사 선택
    - 경로 자동 생성
    
    **Parameters**:
    - order_id: 주문 ID
    - apply_rules: 배차 규칙 적용 여부 (기본: True)
    - simulate: 시뮬레이션 모드 (기본: False, 실제 배차하지 않음)
    
    **Returns**:
    ```json
    {
        "success": true,
        "dispatch_id": 123,
        "vehicle": {...},
        "driver": {...},
        "distance_km": 5.2,
        "estimated_time_min": 15,
        "route": {...},
        "alternatives": [...],
        "reasoning": "가장 가까운 차량 (5.2km, 약 15분) | 우수 기사 (평점 4.8/5.0)"
    }
    ```
    """
    service = IntegratedDispatchService(db)
    
    result = await service.auto_dispatch(
        order_id=request.order_id,
        apply_rules=request.apply_rules,
        simulate=request.simulate
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Auto dispatch failed"))
    
    return result


@router.get("/vehicles/map")
async def get_vehicles_on_map(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    지도에 표시할 모든 차량 위치 조회
    
    **Parameters**:
    - status: 차량 상태 필터 (available, busy, idle 등)
    
    **Returns**:
    ```json
    {
        "vehicles": [
            {
                "vehicle_id": 1,
                "license_plate": "12가3456",
                "driver_name": "홍길동",
                "latitude": 37.5665,
                "longitude": 126.9780,
                "status": "available",
                "last_updated": "2026-02-11T13:00:00"
            },
            ...
        ],
        "total": 10
    }
    ```
    """
    service = IntegratedDispatchService(db)
    
    # 모든 차량 위치 조회
    from app.models.vehicle import Vehicle
    from app.models.driver import Driver
    
    query = db.query(Vehicle).filter(Vehicle.is_active == True)
    
    if status:
        query = query.filter(Vehicle.status == status)
    
    vehicles = query.all()
    
    vehicle_locations = []
    for vehicle in vehicles:
        # GPS 위치 조회
        location = await service.gps_service.get_vehicle_location(vehicle.id)
        
        if not location:
            # 마지막 알려진 위치 사용
            if vehicle.last_known_latitude and vehicle.last_known_longitude:
                location = (vehicle.last_known_latitude, vehicle.last_known_longitude)
            else:
                continue
        
        # 기사 정보
        driver = db.query(Driver).filter(Driver.id == vehicle.driver_id).first()
        
        vehicle_locations.append({
            "vehicle_id": vehicle.id,
            "license_plate": vehicle.license_plate,
            "driver_name": driver.name if driver else None,
            "driver_phone": driver.phone if driver else None,
            "driver_rating": driver.rating if driver else None,
            "latitude": location[0],
            "longitude": location[1],
            "status": vehicle.status,
            "vehicle_type": vehicle.vehicle_type,
            "temperature_type": vehicle.temperature_type,
            "last_updated": vehicle.updated_at.isoformat() if vehicle.updated_at else None
        })
    
    return {
        "vehicles": vehicle_locations,
        "total": len(vehicle_locations)
    }


@router.get("/routes/{order_id}")
async def get_order_route(
    order_id: int,
    vehicle_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    주문 경로 조회
    
    **Parameters**:
    - order_id: 주문 ID
    - vehicle_id: 차량 ID (선택, 없으면 배차된 차량 사용)
    
    **Returns**:
    ```json
    {
        "order_id": 123,
        "vehicle_id": 45,
        "current_to_pickup": {
            "distance_km": 5.2,
            "duration_min": 15,
            "route": [...]
        },
        "pickup_to_delivery": {
            "distance_km": 12.3,
            "duration_min": 30,
            "route": [...]
        },
        "total_distance_km": 17.5,
        "total_duration_min": 45
    }
    ```
    """
    from app.models.order import Order
    from app.models.dispatch import Dispatch
    
    # 주문 조회
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 차량 ID 결정
    if not vehicle_id:
        # 배차된 차량 조회
        dispatch = db.query(Dispatch).filter(
            Dispatch.order_id == order_id
        ).order_by(Dispatch.created_at.desc()).first()
        
        if dispatch:
            vehicle_id = dispatch.vehicle_id
        else:
            raise HTTPException(
                status_code=400,
                detail="No vehicle assigned. Please provide vehicle_id parameter."
            )
    
    # 경로 조회
    service = IntegratedDispatchService(db)
    route = await service.get_vehicle_route(vehicle_id, order_id)
    
    if not route:
        raise HTTPException(status_code=404, detail="Cannot calculate route")
    
    return {
        "order_id": order_id,
        "vehicle_id": vehicle_id,
        **route
    }


@router.get("/vehicles/{vehicle_id}/location")
async def get_vehicle_location(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    특정 차량의 실시간 위치 조회
    
    **Returns**:
    ```json
    {
        "vehicle_id": 1,
        "license_plate": "12가3456",
        "latitude": 37.5665,
        "longitude": 126.9780,
        "address": "서울시 중구 세종대로 110",
        "status": "available",
        "last_updated": "2026-02-11T13:00:00"
    }
    ```
    """
    from app.models.vehicle import Vehicle
    
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    service = IntegratedDispatchService(db)
    
    # GPS 위치 조회
    location = await service.gps_service.get_vehicle_location(vehicle_id)
    
    if not location:
        # 마지막 알려진 위치
        if vehicle.last_known_latitude and vehicle.last_known_longitude:
            location = (vehicle.last_known_latitude, vehicle.last_known_longitude)
        else:
            raise HTTPException(status_code=404, detail="Vehicle location not available")
    
    # 주소로 변환
    address = await service.map_service.reverse_geocode(location[0], location[1])
    
    return {
        "vehicle_id": vehicle_id,
        "license_plate": vehicle.license_plate,
        "latitude": location[0],
        "longitude": location[1],
        "address": address,
        "status": vehicle.status,
        "last_updated": vehicle.updated_at.isoformat() if vehicle.updated_at else None
    }


@router.post("/dispatch/batch")
async def batch_auto_dispatch(
    order_ids: list[int],
    apply_rules: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    여러 주문 일괄 자동 배차
    
    **Parameters**:
    - order_ids: 주문 ID 리스트
    - apply_rules: 배차 규칙 적용 여부
    
    **Returns**:
    ```json
    {
        "total": 5,
        "success": 4,
        "failed": 1,
        "results": [...]
    }
    ```
    """
    service = IntegratedDispatchService(db)
    
    results = []
    success_count = 0
    failed_count = 0
    
    for order_id in order_ids:
        result = await service.auto_dispatch(
            order_id=order_id,
            apply_rules=apply_rules,
            simulate=False
        )
        
        if result["success"]:
            success_count += 1
        else:
            failed_count += 1
        
        results.append(result)
    
    return {
        "total": len(order_ids),
        "success": success_count,
        "failed": failed_count,
        "results": results
    }


@router.get("/dispatch/analytics/statistics")
async def get_dispatch_statistics(
    start_date: Optional[datetime] = Query(None, description="시작 날짜"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    배차 통계 조회
    
    **Returns**:
    ```json
    {
        "total_dispatches": 150,
        "success_rate": 95.5,
        "avg_distance_km": 12.3,
        "avg_duration_min": 25.5,
        "by_status": {...},
        "by_vehicle_type": {...}
    }
    ```
    """
    analytics = DispatchAnalyticsService(db)
    return analytics.get_dispatch_statistics(start_date, end_date)


@router.get("/dispatch/analytics/driver-performance")
async def get_driver_performance(
    driver_id: Optional[int] = Query(None, description="기사 ID"),
    limit: int = Query(10, ge=1, le=100, description="반환할 기사 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    기사별 성과 분석
    
    **Returns**:
    ```json
    {
        "drivers": [
            {
                "driver_id": 1,
                "driver_name": "홍길동",
                "total_dispatches": 50,
                "completed": 48,
                "completion_rate": 96.0,
                "avg_rating": 4.8,
                "total_distance_km": 520.5
            },
            ...
        ]
    }
    ```
    """
    analytics = DispatchAnalyticsService(db)
    performance = analytics.get_driver_performance(driver_id, limit)
    
    return {
        "drivers": performance,
        "total": len(performance)
    }


@router.get("/dispatch/analytics/suggestions")
async def get_optimization_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    최적화 제안 조회
    
    **Returns**:
    ```json
    {
        "suggestions": [
            {
                "type": "warning",
                "title": "배차 시간이 평균보다 깁니다",
                "description": "최근 7일 평균 배차 시간: 50.2분",
                "action": "차량 추가 배치 또는 배차 규칙 최적화를 고려하세요"
            },
            ...
        ],
        "generated_at": "2026-02-11T13:00:00"
    }
    ```
    """
    analytics = DispatchAnalyticsService(db)
    suggestions = analytics.get_optimization_suggestions()
    
    return {
        "suggestions": suggestions,
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/dispatch/analytics/hourly-pattern")
async def get_hourly_dispatch_pattern(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    시간대별 배차 패턴 분석 (최근 30일)
    
    **Returns**:
    ```json
    {
        "pattern": {
            "0": 5,
            "1": 2,
            ...
            "23": 8
        },
        "peak_hours": [8, 9, 17, 18],
        "low_hours": [0, 1, 2, 3]
    }
    ```
    """
    analytics = DispatchAnalyticsService(db)
    pattern = analytics.get_hourly_dispatch_pattern()
    
    # 피크 시간대 계산 (상위 25%)
    sorted_hours = sorted(pattern.items(), key=lambda x: x[1], reverse=True)
    peak_count = max(1, len(sorted_hours) // 4)
    peak_hours = [int(h) for h, _ in sorted_hours[:peak_count] if int(h) >= 6 and int(h) <= 22]
    
    # 한산한 시간대 (하위 25%)
    low_hours = [int(h) for h, _ in sorted_hours[-peak_count:]]
    
    return {
        "pattern": pattern,
        "peak_hours": sorted(peak_hours),
        "low_hours": sorted(low_hours)
    }
