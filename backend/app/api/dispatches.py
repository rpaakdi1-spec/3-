from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.models.dispatch import Dispatch, DispatchStatus
from app.models.order import OrderStatus
from app.schemas.dispatch import (
    DispatchResponse, DispatchDetailResponse, DispatchListResponse,
    OptimizationRequest, OptimizationResponse, DispatchUpdate,
    DispatchConfirmRequest, DispatchStatsResponse
)
from app.services.dispatch_optimization_service import DispatchOptimizationService
from loguru import logger

router = APIRouter()


@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_dispatch(
    request: OptimizationRequest,
    db: Session = Depends(get_db)
):
    """
    AI 기반 배차 최적화
    
    주어진 주문들에 대해 최적의 배차 계획을 생성합니다.
    - 온도대별 차량 매칭
    - 적재 용량 제약 (팔레트, 중량)
    - 거리 최적화
    """
    optimizer = DispatchOptimizationService(db)
    
    result = await optimizer.optimize_dispatch(
        order_ids=request.order_ids,
        vehicle_ids=request.vehicle_ids,
        dispatch_date=request.dispatch_date
    )
    
    return OptimizationResponse(**result)


@router.get("/", response_model=DispatchListResponse)
def get_dispatches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[DispatchStatus] = None,
    dispatch_date: Optional[date] = None,
    vehicle_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """배차 목록 조회"""
    query = db.query(Dispatch)
    
    if status:
        query = query.filter(Dispatch.status == status)
    
    if dispatch_date:
        query = query.filter(Dispatch.dispatch_date == dispatch_date)
    
    if vehicle_id:
        query = query.filter(Dispatch.vehicle_id == vehicle_id)
    
    query = query.order_by(Dispatch.dispatch_date.desc(), Dispatch.created_at.desc())
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    # Add vehicle and driver info
    for item in items:
        if item.vehicle:
            item.vehicle_code = item.vehicle.code
            item.vehicle_plate = item.vehicle.plate_number
        if item.driver:
            item.driver_name = item.driver.name
    
    return DispatchListResponse(total=total, items=items)


@router.get("/{dispatch_id}", response_model=DispatchDetailResponse)
def get_dispatch(dispatch_id: int, db: Session = Depends(get_db)):
    """배차 상세 조회 (경로 포함)"""
    dispatch = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
    if not dispatch:
        raise HTTPException(status_code=404, detail="배차를 찾을 수 없습니다")
    
    # Add vehicle and driver info
    if dispatch.vehicle:
        dispatch.vehicle_code = dispatch.vehicle.code
        dispatch.vehicle_plate = dispatch.vehicle.plate_number
    if dispatch.driver:
        dispatch.driver_name = dispatch.driver.name
    
    return dispatch


@router.put("/{dispatch_id}", response_model=DispatchResponse)
def update_dispatch(
    dispatch_id: int,
    dispatch_data: DispatchUpdate,
    db: Session = Depends(get_db)
):
    """배차 수정"""
    dispatch = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
    if not dispatch:
        raise HTTPException(status_code=404, detail="배차를 찾을 수 없습니다")
    
    # Cannot modify confirmed dispatches
    if dispatch.status == DispatchStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="확정된 배차는 수정할 수 없습니다")
    
    # Update fields
    update_data = dispatch_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dispatch, field, value)
    
    db.commit()
    db.refresh(dispatch)
    
    logger.info(f"Updated dispatch: {dispatch.dispatch_number}")
    return dispatch


@router.delete("/{dispatch_id}")
def delete_dispatch(dispatch_id: int, db: Session = Depends(get_db)):
    """배차 삭제"""
    dispatch = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
    if not dispatch:
        raise HTTPException(status_code=404, detail="배차를 찾을 수 없습니다")
    
    # Cannot delete confirmed or in-progress dispatches
    if dispatch.status in [DispatchStatus.CONFIRMED, DispatchStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=400,
            detail="확정되었거나 진행 중인 배차는 삭제할 수 없습니다"
        )
    
    # Reset order statuses
    for route in dispatch.routes:
        if route.order:
            route.order.status = OrderStatus.PENDING
    
    db.delete(dispatch)
    db.commit()
    
    logger.info(f"Deleted dispatch: {dispatch.dispatch_number}")
    return {"message": "배차가 삭제되었습니다"}


@router.post("/confirm")
def confirm_dispatches(
    request: DispatchConfirmRequest,
    db: Session = Depends(get_db)
):
    """배차 확정"""
    confirmed = []
    errors = []
    
    for dispatch_id in request.dispatch_ids:
        dispatch = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
        if not dispatch:
            errors.append({"dispatch_id": dispatch_id, "error": "배차를 찾을 수 없음"})
            continue
        
        if dispatch.status != DispatchStatus.DRAFT:
            errors.append({"dispatch_id": dispatch_id, "error": "임시저장 상태가 아님"})
            continue
        
        dispatch.status = DispatchStatus.CONFIRMED
        
        # Update order statuses
        for route in dispatch.routes:
            if route.order:
                route.order.status = OrderStatus.ASSIGNED
        
        confirmed.append(dispatch.dispatch_number)
    
    db.commit()
    
    logger.info(f"Confirmed {len(confirmed)} dispatches")
    
    return {
        "confirmed": len(confirmed),
        "failed": len(errors),
        "confirmed_dispatch_numbers": confirmed,
        "errors": errors
    }


@router.get("/stats/summary", response_model=DispatchStatsResponse)
def get_dispatch_stats(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """배차 통계 조회"""
    query = db.query(Dispatch)
    
    if start_date:
        query = query.filter(Dispatch.dispatch_date >= start_date)
    if end_date:
        query = query.filter(Dispatch.dispatch_date <= end_date)
    
    dispatches = query.all()
    
    # Calculate statistics
    total_dispatches = len(dispatches)
    
    by_status = {}
    for status in DispatchStatus:
        by_status[status.value] = sum(1 for d in dispatches if d.status == status)
    
    by_date = {}
    for dispatch in dispatches:
        date_str = dispatch.dispatch_date.isoformat()
        by_date[date_str] = by_date.get(date_str, 0) + 1
    
    total_orders = sum(d.total_orders for d in dispatches)
    unique_vehicles = len(set(d.vehicle_id for d in dispatches))
    
    avg_orders = total_orders / total_dispatches if total_dispatches > 0 else 0
    avg_pallets = sum(d.total_pallets for d in dispatches) / total_dispatches if total_dispatches > 0 else 0
    
    return DispatchStatsResponse(
        total_dispatches=total_dispatches,
        by_status=by_status,
        by_date=by_date,
        total_orders=total_orders,
        total_vehicles_used=unique_vehicles,
        avg_orders_per_dispatch=round(avg_orders, 2),
        avg_pallets_per_dispatch=round(avg_pallets, 2)
    )
