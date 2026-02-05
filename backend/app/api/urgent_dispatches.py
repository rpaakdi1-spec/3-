"""
Urgent Dispatch API
긴급 배차 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from loguru import logger

from app.core.database import get_db
from app.models.order import Order
from app.services.urgent_dispatch_service import UrgentDispatchService
from pydantic import BaseModel, Field

router = APIRouter()


class UrgentDispatchRequest(BaseModel):
    """긴급 배차 요청"""
    order_id: int = Field(..., description="주문 ID")
    urgency_level: int = Field(5, ge=1, le=5, description="긴급도 (1-5, 5가 가장 긴급)")
    urgent_reason: str = Field("긴급 주문", description="긴급 사유")


class UrgentDispatchResponse(BaseModel):
    """긴급 배차 응답"""
    success: bool
    message: str
    dispatch_id: Optional[int]
    dispatch_number: Optional[str]
    vehicle_name: Optional[str]
    driver_name: Optional[str]
    distance_km: Optional[float]


@router.post("/create", response_model=UrgentDispatchResponse)
def create_urgent_dispatch(
    request: UrgentDispatchRequest,
    db: Session = Depends(get_db)
):
    """긴급 배차 생성
    
    긴급 주문에 대해 자동으로 가장 가까운 가용 차량을 배정합니다.
    """
    try:
        # 주문 조회
        order = db.query(Order).filter(Order.id == request.order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
        
        # 이미 배차된 주문인지 확인
        if order.status != "PENDING":
            raise HTTPException(
                status_code=400,
                detail=f"이미 배차된 주문입니다 (상태: {order.status})"
            )
        
        # 긴급 배차 자동 생성
        result = UrgentDispatchService.auto_assign_urgent_order(
            db,
            order,
            request.urgency_level,
            request.urgent_reason
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['message'])
        
        dispatch = result['dispatch']
        
        return UrgentDispatchResponse(
            success=True,
            message=result['message'],
            dispatch_id=dispatch.id,
            dispatch_number=dispatch.dispatch_number,
            vehicle_name=result.get('vehicle_name'),
            driver_name=result.get('driver_name'),
            distance_km=result.get('distance_km')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating urgent dispatch: {e}")
        raise HTTPException(status_code=500, detail="긴급 배차 생성 중 오류가 발생했습니다")


@router.post("/find-vehicle/{order_id}")
def find_nearest_vehicle_for_order(
    order_id: int,
    max_distance_km: float = Query(50.0, description="최대 거리 (km)"),
    db: Session = Depends(get_db)
):
    """주문에 대해 가장 가까운 가용 차량 찾기 (미리보기)
    
    실제 배차를 생성하지 않고 어떤 차량이 배정될지 확인합니다.
    """
    try:
        # 주문 조회
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
        
        # 가장 가까운 차량 찾기
        result = UrgentDispatchService.find_nearest_available_vehicle(
            db,
            order,
            order.order_date,
            max_distance_km
        )
        
        if not result:
            return {
                "found": False,
                "message": "가용 차량을 찾을 수 없습니다"
            }
        
        vehicle = result['vehicle']
        driver = result['driver']
        
        return {
            "found": True,
            "vehicle": {
                "id": vehicle.id,
                "license_plate": vehicle.license_plate,
                "vehicle_type": vehicle.vehicle_type,
                "capacity_ton": vehicle.capacity_ton
            },
            "driver": {
                "id": driver.id,
                "name": driver.name,
                "phone": driver.phone
            } if driver else None,
            "distance_km": result['distance_km'],
            "reason": result['reason']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding nearest vehicle: {e}")
        raise HTTPException(status_code=500, detail="차량 검색 중 오류가 발생했습니다")


@router.get("/urgent-orders")
def get_urgent_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """긴급 주문 목록 조회
    
    우선순위가 높거나 긴급 주문들을 조회합니다.
    """
    from app.models.dispatch import Dispatch
    
    # 우선순위 8 이상이거나 is_urgent인 배차
    urgent_dispatches = (
        db.query(Dispatch)
        .filter(
            (Order.priority >= 8) | (Dispatch.is_urgent == True)
        )
        .order_by(Dispatch.urgency_level.desc(), Dispatch.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    total = db.query(Dispatch).filter(
        (Order.priority >= 8) | (Dispatch.is_urgent == True)
    ).count()
    
    return {
        "total": total,
        "items": [
            {
                "id": d.id,
                "dispatch_number": d.dispatch_number,
                "dispatch_date": d.dispatch_date,
                "vehicle_id": d.vehicle_id,
                "driver_id": d.driver_id,
                "is_urgent": d.is_urgent,
                "urgency_level": d.urgency_level,
                "urgent_reason": d.urgent_reason,
                "status": d.status,
                "created_at": d.created_at
            }
            for d in urgent_dispatches
        ]
    }
