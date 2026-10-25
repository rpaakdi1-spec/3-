"""긴급정비 API 엔드포인트"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import List, Optional
import math

from app.core.database import get_db
from app.models.vehicle import Vehicle, VehicleStatus, EmergencyType, EmergencySeverity
from app.models.dispatch import Dispatch, DispatchStatus
from app.schemas.emergency import (
    EmergencyReportCreate,
    EmergencyResponse,
    AffectedDispatch,
    RecommendedVehicle,
    DispatchReassignRequest,
    DispatchReassignResponse,
    ReassignedDispatch,
    EmergencyListResponse,
    EmergencyListItem
)
from loguru import logger

router = APIRouter()


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """두 지점 간 거리 계산 (km)"""
    if not all([lat1, lon1, lat2, lon2]):
        return 999999.0
    
    R = 6371  # 지구 반지름 (km)
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return round(distance, 2)


@router.post("/vehicles/{vehicle_id}/emergency", response_model=EmergencyResponse)
async def report_emergency(
    vehicle_id: int,
    request: EmergencyReportCreate,
    db: Session = Depends(get_db)
):
    """긴급정비 신고"""
    
    # 1. 차량 조회
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="차량을 찾을 수 없습니다")
    
    # 2. 차량 상태 업데이트
    vehicle.is_emergency = True
    vehicle.emergency_type = request.emergency_type
    vehicle.emergency_severity = request.severity
    vehicle.emergency_reported_at = datetime.now()
    vehicle.emergency_location = request.location
    vehicle.emergency_description = request.description
    vehicle.estimated_repair_time = request.estimated_repair_time
    
    # 긴급도에 따라 차량 상태 변경
    if request.severity == EmergencySeverity.CRITICAL.value:
        vehicle.status = VehicleStatus.BREAKDOWN
    elif request.severity == EmergencySeverity.WARNING.value:
        vehicle.status = VehicleStatus.EMERGENCY_MAINTENANCE
    # MINOR는 상태 변경 안 함
    
    # 3. 영향받는 배차 조회
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    affected_dispatches_query = db.query(Dispatch).filter(
        and_(
            Dispatch.vehicle_id == vehicle_id,
            Dispatch.status.in_([DispatchStatus.PENDING, DispatchStatus.IN_PROGRESS]),
            Dispatch.dispatch_date >= today,
            Dispatch.dispatch_date < tomorrow
        )
    )
    
    affected_dispatches = []
    for dispatch in affected_dispatches_query.all():
        # 지연 시간 추정 (대체 차량 배정 시간 포함)
        delay_estimate = 30  # 기본 30분
        if request.severity == EmergencySeverity.CRITICAL.value:
            delay_estimate = 60  # 긴급일 경우 60분
        
        affected_dispatches.append(AffectedDispatch(
            dispatch_id=dispatch.dispatch_number,
            order_number=dispatch.routes[0].order.order_number if dispatch.routes and dispatch.routes[0].order else "",
            pickup_time=dispatch.scheduled_start_time.strftime("%H:%M") if dispatch.scheduled_start_time else "",
            delay_estimate=delay_estimate,
            customer_name=dispatch.routes[0].order.pickup_client.name if dispatch.routes and dispatch.routes[0].order and dispatch.routes[0].order.pickup_client else ""
        ))
    
    # 4. 대체 차량 추천
    recommended_vehicles = []
    
    # 추천 조건: 같은 온도대, 운행가능, 용량 충족
    candidates = db.query(Vehicle).filter(
        and_(
            Vehicle.vehicle_type == vehicle.vehicle_type,
            Vehicle.status == VehicleStatus.AVAILABLE,
            Vehicle.is_active == True,
            Vehicle.id != vehicle_id
        )
    ).all()
    
    # 차고지 기준으로 거리 계산 및 정렬
    for candidate in candidates:
        distance = calculate_distance(
            vehicle.garage_latitude or 0,
            vehicle.garage_longitude or 0,
            candidate.garage_latitude or 0,
            candidate.garage_longitude or 0
        )
        
        recommended_vehicles.append(RecommendedVehicle(
            vehicle_id=candidate.id,
            code=candidate.code,
            plate_number=candidate.plate_number,
            vehicle_type=candidate.vehicle_type.value,
            distance_km=distance,
            availability=True,
            driver_name=candidate.driver_name,
            driver_phone=candidate.driver_phone
        ))
    
    # 거리순 정렬
    recommended_vehicles.sort(key=lambda x: x.distance_km)
    recommended_vehicles = recommended_vehicles[:5]  # 상위 5개
    
    # 5. 데이터베이스 커밋
    db.commit()
    
    # 6. 긴급 ID 생성
    emergency_id = f"EMG-{datetime.now().strftime('%Y%m%d')}-{vehicle_id:03d}"
    
    logger.warning(
        f"🚨 긴급정비 신고: {vehicle.plate_number} ({request.severity})"
        f" - 영향 배차: {len(affected_dispatches)}건"
    )
    
    return EmergencyResponse(
        success=True,
        vehicle_id=vehicle_id,
        emergency_id=emergency_id,
        affected_dispatches=affected_dispatches,
        recommended_vehicles=recommended_vehicles,
        message=f"긴급정비가 신고되었습니다. 영향받는 배차: {len(affected_dispatches)}건"
    )


@router.post("/dispatches/reassign", response_model=DispatchReassignResponse)
async def reassign_dispatches(
    request: DispatchReassignRequest,
    db: Session = Depends(get_db)
):
    """배차 재조정"""
    
    # 1. 차량 확인
    broken_vehicle = db.query(Vehicle).filter(Vehicle.id == request.broken_vehicle_id).first()
    if not broken_vehicle:
        raise HTTPException(status_code=404, detail="고장 차량을 찾을 수 없습니다")
    
    replacement_vehicle = db.query(Vehicle).filter(Vehicle.id == request.replacement_vehicle_id).first()
    if not replacement_vehicle:
        raise HTTPException(status_code=404, detail="대체 차량을 찾을 수 없습니다")
    
    # 2. 대체 차량 가용성 확인
    if replacement_vehicle.status != VehicleStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="대체 차량이 운행 가능 상태가 아닙니다")
    
    # 3. 배차 재조정
    reassigned = []
    
    for dispatch_id in request.dispatch_ids:
        dispatch = db.query(Dispatch).filter(Dispatch.dispatch_number == dispatch_id).first()
        
        if not dispatch:
            logger.warning(f"배차를 찾을 수 없습니다: {dispatch_id}")
            continue
        
        # 배차 차량 변경
        original_vehicle = dispatch.vehicle.plate_number if dispatch.vehicle else ""
        dispatch.vehicle_id = request.replacement_vehicle_id
        
        reassigned.append(ReassignedDispatch(
            dispatch_id=dispatch.dispatch_number,
            order_number=dispatch.routes[0].order.order_number if dispatch.routes and dispatch.routes[0].order else "",
            original_vehicle=original_vehicle,
            new_vehicle=replacement_vehicle.plate_number,
            customer_notified=request.notify_customers
        ))
        
        logger.info(f"배차 재조정: {dispatch_id} - {original_vehicle} → {replacement_vehicle.plate_number}")
    
    # 4. 고장 차량 대체 정보 업데이트
    broken_vehicle.replacement_vehicle_id = request.replacement_vehicle_id
    
    # 5. 대체 차량 상태 변경
    replacement_vehicle.status = VehicleStatus.IN_USE
    
    # 6. 데이터베이스 커밋
    db.commit()
    
    # TODO: 고객사 통보 (SMS/알림톡)
    if request.notify_customers:
        logger.info(f"고객사 통보 필요: {len(reassigned)}건")
    
    return DispatchReassignResponse(
        success=True,
        reassigned_count=len(reassigned),
        dispatches=reassigned,
        message=f"{len(reassigned)}건의 배차가 재조정되었습니다"
    )


@router.get("/emergencies", response_model=EmergencyListResponse)
async def list_emergencies(
    status: Optional[str] = "active",
    db: Session = Depends(get_db)
):
    """긴급 상황 목록 조회"""
    
    query = db.query(Vehicle).filter(Vehicle.is_emergency == True)
    
    if status == "active":
        # 활성 긴급 상황: 고장 또는 긴급정비 상태
        query = query.filter(
            Vehicle.status.in_([VehicleStatus.BREAKDOWN, VehicleStatus.EMERGENCY_MAINTENANCE])
        )
    
    emergencies = query.order_by(Vehicle.emergency_reported_at.desc()).all()
    
    items = []
    for vehicle in emergencies:
        # 영향받는 배차 수 계산
        today = datetime.now().date()
        affected_count = db.query(Dispatch).filter(
            and_(
                Dispatch.vehicle_id == vehicle.id,
                Dispatch.status.in_([DispatchStatus.PENDING, DispatchStatus.IN_PROGRESS]),
                Dispatch.dispatch_date >= today
            )
        ).count()
        
        # 상태 판정
        emergency_status = "active"
        if vehicle.status == VehicleStatus.AVAILABLE:
            emergency_status = "resolved"
        elif vehicle.status == VehicleStatus.OUT_OF_SERVICE:
            emergency_status = "cancelled"
        
        items.append(EmergencyListItem(
            vehicle_id=vehicle.id,
            plate_number=vehicle.plate_number,
            emergency_type=vehicle.emergency_type or "unknown",
            severity=vehicle.emergency_severity or "unknown",
            reported_at=vehicle.emergency_reported_at or datetime.now(),
            affected_dispatches_count=affected_count,
            status=emergency_status,
            description=vehicle.emergency_description or ""
        ))
    
    return EmergencyListResponse(
        total=len(items),
        items=items
    )


@router.post("/vehicles/{vehicle_id}/emergency/resolve")
async def resolve_emergency(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    """긴급 상황 해제 (정비 완료)"""
    
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="차량을 찾을 수 없습니다")
    
    # 긴급 상황 플래그 해제
    vehicle.is_emergency = False
    vehicle.status = VehicleStatus.AVAILABLE
    vehicle.replacement_vehicle_id = None
    
    db.commit()
    
    logger.info(f"✅ 긴급 상황 해제: {vehicle.plate_number} - 정비 완료")
    
    return {
        "success": True,
        "message": "긴급 상황이 해제되었습니다"
    }
