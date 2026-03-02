"""
반자동 배차 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.semi_auto_dispatch_service import SemiAutoDispatchService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/orders/{order_id}/suggest-vehicles")
async def suggest_vehicles_for_order(
    order_id: int,
    max_distance_km: int = 150,
    time_window_hours: int = 2,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    주문에 대한 배차 가능 차량 제안
    
    Args:
        order_id: 주문 ID
        max_distance_km: 최대 거리 (기본 150km)
        time_window_hours: 시간 여유 (기본 2시간)
    
    Returns:
        {
            "success": true,
            "order": {...},
            "suggestions": [
                {
                    "vehicle_id": 1,
                    "vehicle_number": "12가3456",
                    "driver": {...},
                    "status": "waiting",
                    "distance_km": 10.5,
                    "estimated_arrival_min": 20,
                    "score": 85.0,
                    "reasons": ["대기 중", "적재 가능", ...],
                    "warnings": []
                }
            ],
            "total_count": 5
        }
    """
    try:
        service = SemiAutoDispatchService(db)
        result = await service.suggest_vehicles(
            order_id=order_id,
            max_distance_km=max_distance_km,
            time_window_hours=time_window_hours
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "배차 제안 실패")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"배차 제안 API 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"배차 제안 중 오류 발생: {str(e)}"
        )


@router.post("/orders/{order_id}/manual-dispatch")
async def manual_dispatch_with_selected_vehicle(
    order_id: int,
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    사용자가 선택한 차량으로 수동 배차
    
    Args:
        order_id: 주문 ID
        vehicle_id: 선택한 차량 ID
    
    Returns:
        {
            "success": true,
            "dispatch_id": 123,
            "message": "배차가 완료되었습니다"
        }
    """
    from app.models.order import Order
    from app.models.vehicle import Vehicle
    from app.models.dispatch import Dispatch
    from datetime import datetime
    
    try:
        # 주문 확인
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="주문을 찾을 수 없습니다"
            )
        
        # 차량 확인
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="차량을 찾을 수 없습니다"
            )
        
        if not vehicle.assigned_driver_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="차량에 배정된 운전자가 없습니다"
            )
        
        # 배차 생성
        dispatch = Dispatch(
            order_id=order_id,
            vehicle_id=vehicle_id,
            driver_id=vehicle.assigned_driver_id,
            status='pending',
            assigned_at=datetime.utcnow(),
            assigned_by=current_user.id,
            pickup_address=order.pickup_address,
            delivery_address=order.delivery_address,
            pickup_latitude=order.pickup_latitude,
            pickup_longitude=order.pickup_longitude,
            delivery_latitude=order.delivery_latitude,
            delivery_longitude=order.delivery_longitude,
            scheduled_pickup_time=order.pickup_start_time,
            # 기타 필요한 필드
        )
        
        db.add(dispatch)
        
        # 주문 상태 업데이트
        order.status = 'dispatched'
        
        db.commit()
        db.refresh(dispatch)
        
        logger.info(f"✅ 수동 배차 완료: 주문 #{order_id} → 차량 #{vehicle_id}")
        
        return {
            "success": True,
            "dispatch_id": dispatch.id,
            "message": f"{vehicle.vehicle_number} 차량으로 배차가 완료되었습니다",
            "vehicle_number": vehicle.vehicle_number,
            "driver_name": vehicle.assigned_driver.name if vehicle.assigned_driver else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"수동 배차 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"배차 중 오류 발생: {str(e)}"
        )
