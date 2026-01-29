from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date
import pandas as pd
from pathlib import Path
import tempfile

from app.core.database import get_db
from app.models.dispatch import Dispatch, DispatchStatus
from app.models.order import OrderStatus
from app.schemas.dispatch import (
    DispatchResponse, DispatchDetailResponse, DispatchListResponse,
    OptimizationRequest, OptimizationResponse, DispatchUpdate,
    DispatchConfirmRequest, DispatchStatsResponse
)
from app.services.dispatch_optimization_service import DispatchOptimizationService
from app.services.cvrptw_service import AdvancedDispatchOptimizationService
from loguru import logger

router = APIRouter()


@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_dispatch(
    request: OptimizationRequest,
    db: Session = Depends(get_db)
):
    """
    AI 기반 배차 최적화 (기본 Greedy 알고리즘)
    
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


@router.post("/optimize-cvrptw", response_model=OptimizationResponse)
async def optimize_dispatch_cvrptw(
    request: OptimizationRequest,
    db: Session = Depends(get_db),
    time_limit: int = Query(30, ge=5, le=300, description="최대 실행 시간 (초)"),
    use_time_windows: bool = Query(True, description="시간 제약 사용 여부"),
    use_real_routing: bool = Query(False, description="Naver Directions API 사용 (실제 경로)")
):
    """
    고급 AI 배차 최적화 (OR-Tools CVRPTW)
    
    Google OR-Tools를 사용한 고급 배차 최적화:
    - CVRPTW (Capacitated VRP with Time Windows)
    - 온도대별 차량 매칭
    - 팔레트/중량 용량 제약
    - 시간 제약 (Time Windows)
    - 거리 최소화
    - 균등 배분
    
    Parameters:
    - time_limit: 최대 실행 시간 (5-300초, 기본 30초)
    - use_time_windows: 시간 제약 사용 여부 (기본 True)
    - use_real_routing: Naver API 실제 경로 사용 (기본 False, Haversine)
    
    Note:
    - use_real_routing=True 시 Naver Directions API 호출 (느림, 정확)
    - use_real_routing=False 시 Haversine 직선거리 사용 (빠름, 근사)
    """
    logger.info(f"CVRPTW 최적화 요청: {len(request.order_ids)}건")
    logger.info(f"설정: time_limit={time_limit}s, time_windows={use_time_windows}, real_routing={use_real_routing}")
    
    optimizer = AdvancedDispatchOptimizationService(db)
    
    result = await optimizer.optimize_dispatch_cvrptw(
        order_ids=request.order_ids,
        vehicle_ids=request.vehicle_ids,
        dispatch_date=request.dispatch_date,
        time_limit_seconds=time_limit,
        use_time_windows=use_time_windows,
        use_real_routing=use_real_routing
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
            # Also include driver info from vehicle if dispatch.driver is not set
            if not item.driver and item.vehicle.driver_name:
                item.driver_name = item.vehicle.driver_name
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
        # Also include driver info from vehicle if dispatch.driver is not set
        if not dispatch.driver and dispatch.vehicle.driver_name:
            dispatch.driver_name = dispatch.vehicle.driver_name
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


@router.get("/export/excel")
def export_dispatches_to_excel(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[DispatchStatus] = None,
    db: Session = Depends(get_db)
):
    """배차 내역 엑셀 다운로드"""
    logger.info("배차 내역 엑셀 다운로드 요청")
    
    # Query dispatches with filters
    query = db.query(Dispatch)
    
    if status:
        query = query.filter(Dispatch.status == status)
    
    if start_date:
        query = query.filter(Dispatch.dispatch_date >= start_date)
    
    if end_date:
        query = query.filter(Dispatch.dispatch_date <= end_date)
    
    query = query.order_by(Dispatch.dispatch_date.desc(), Dispatch.created_at.desc())
    
    dispatches = query.all()
    
    if not dispatches:
        raise HTTPException(status_code=404, detail="다운로드할 배차 내역이 없습니다")
    
    # Prepare data for Excel
    data = []
    for dispatch in dispatches:
        # Get vehicle and driver info
        vehicle_code = dispatch.vehicle.code if dispatch.vehicle else "-"
        vehicle_plate = dispatch.vehicle.plate_number if dispatch.vehicle else "-"
        driver_name = dispatch.driver.name if dispatch.driver else "-"
        
        # Get pickup and delivery addresses from routes
        pickup_addresses = []
        delivery_addresses = []
        
        for route in dispatch.routes:
            if route.order:
                # Pickup address
                if route.order.pickup_client:
                    pickup_addr = route.order.pickup_client.address or "-"
                    if route.order.pickup_client.address_detail:
                        pickup_addr += f" {route.order.pickup_client.address_detail}"
                elif route.order.pickup_address:
                    pickup_addr = route.order.pickup_address
                    if route.order.pickup_address_detail:
                        pickup_addr += f" {route.order.pickup_address_detail}"
                else:
                    pickup_addr = "-"
                
                # Delivery address
                if route.order.delivery_client:
                    delivery_addr = route.order.delivery_client.address or "-"
                    if route.order.delivery_client.address_detail:
                        delivery_addr += f" {route.order.delivery_client.address_detail}"
                elif route.order.delivery_address:
                    delivery_addr = route.order.delivery_address
                    if route.order.delivery_address_detail:
                        delivery_addr += f" {route.order.delivery_address_detail}"
                else:
                    delivery_addr = "-"
                
                pickup_addresses.append(pickup_addr)
                delivery_addresses.append(delivery_addr)
        
        # Combine addresses (if multiple stops)
        pickup_text = " → ".join(set(pickup_addresses)) if pickup_addresses else "-"
        delivery_text = " → ".join(set(delivery_addresses)) if delivery_addresses else "-"
        
        data.append({
            "배차번호": dispatch.dispatch_number,
            "배차일자": dispatch.dispatch_date.isoformat(),
            "차량번호": vehicle_plate,
            "차량코드": vehicle_code,
            "기사명": driver_name,
            "상차지주소": pickup_text,
            "하차지주소": delivery_text,
            "주문수": dispatch.total_orders,
            "팔레트수": dispatch.total_pallets,
            "총중량(kg)": dispatch.total_weight_kg,
            "거리(km)": round(dispatch.total_distance_km, 2) if dispatch.total_distance_km else 0,
            "예상시간(분)": dispatch.estimated_duration_minutes or 0,
            "상태": dispatch.status.value,
            "생성일시": dispatch.created_at.strftime("%Y-%m-%d %H:%M")
        })
    
    # Create Excel file
    df = pd.DataFrame(data)
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.xlsx', delete=False) as tmp:
        tmp_path = tmp.name
        
        # Write to Excel with formatting
        with pd.ExcelWriter(tmp_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='배차내역', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['배차내역']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
    
    logger.info(f"배차 내역 엑셀 생성 완료: {len(dispatches)}건")
    
    # Generate filename
    today = date.today().isoformat()
    filename = f"배차내역_{today}.xlsx"
    
    return FileResponse(
        path=tmp_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
