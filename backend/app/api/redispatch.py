"""
동적 재배차 API 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from loguru import logger

from app.core.database import get_db
from app.services.redispatch_service import get_redispatch_service, DynamicRedispatchService


router = APIRouter()


class UrgentOrderRequest(BaseModel):
    """긴급 주문 추가 요청"""
    order_id: int
    force_dispatch: bool = False


class VehicleIssueRequest(BaseModel):
    """차량 문제 요청"""
    vehicle_id: int
    issue_type: str  # 'breakdown', 'delay', 'accident'
    estimated_delay_minutes: Optional[int] = None


class CancelOrderRequest(BaseModel):
    """주문 취소 요청"""
    order_id: int


@router.post("/urgent-order")
async def add_urgent_order(
    request: UrgentOrderRequest,
    db: Session = Depends(get_db)
):
    """
    긴급 주문 추가 및 재배차
    
    Args:
        order_id: 긴급 주문 ID
        force_dispatch: 기존 배차에 강제 추가 여부
        
    Returns:
        재배차 결과
    """
    try:
        service = get_redispatch_service(db)
        result = await service.add_urgent_order(
            order_id=request.order_id,
            force_dispatch=request.force_dispatch
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding urgent order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vehicle-issue")
async def handle_vehicle_issue(
    request: VehicleIssueRequest,
    db: Session = Depends(get_db)
):
    """
    차량 문제 처리 (고장, 지연 등)
    
    Args:
        vehicle_id: 차량 ID
        issue_type: 문제 유형
        estimated_delay_minutes: 예상 지연 시간
        
    Returns:
        재배차 결과
    """
    try:
        service = get_redispatch_service(db)
        result = await service.handle_vehicle_issue(
            vehicle_id=request.vehicle_id,
            issue_type=request.issue_type,
            estimated_delay_minutes=request.estimated_delay_minutes
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error handling vehicle issue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel-order")
async def cancel_order_and_redispatch(
    request: CancelOrderRequest,
    db: Session = Depends(get_db)
):
    """
    주문 취소 및 재배차
    
    Args:
        order_id: 취소할 주문 ID
        
    Returns:
        재배차 결과
    """
    try:
        service = get_redispatch_service(db)
        result = await service.cancel_order_and_redispatch(
            order_id=request.order_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error cancelling order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-dispatch/{dispatch_id}")
async def optimize_in_progress_dispatch(
    dispatch_id: int,
    db: Session = Depends(get_db)
):
    """
    진행 중인 배차 최적화
    
    Args:
        dispatch_id: 배차 ID
        
    Returns:
        최적화 결과
    """
    try:
        service = get_redispatch_service(db)
        result = await service.optimize_in_progress_dispatch(
            dispatch_id=dispatch_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error optimizing dispatch: {e}")
        raise HTTPException(status_code=500, detail=str(e))
