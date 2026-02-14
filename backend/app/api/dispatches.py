from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date, datetime
import pandas as pd
from pathlib import Path
import tempfile
import asyncio

from app.core.database import get_db
from app.models.dispatch import Dispatch, DispatchStatus
from app.models.order import Order, OrderStatus
from app.models.vehicle import VehicleStatus
from app.schemas.dispatch import (
    DispatchResponse, DispatchDetailResponse, DispatchListResponse,
    OptimizationRequest, OptimizationResponse, DispatchUpdate,
    DispatchConfirmRequest, DispatchCompleteRequest, DispatchCancelRequest,
    DispatchStatsResponse, DashboardStatsResponse
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
        
        # Add order numbers and addresses (comma-separated)
        order_numbers = []
        pickup_addresses = []
        delivery_addresses = []
        
        for route in item.routes:
            if route.order_id and route.order:
                order_numbers.append(route.order.order_number)
                if route.route_type == 'PICKUP' and route.order.pickup_address:
                    pickup_addresses.append(route.order.pickup_address)
                elif route.route_type == 'DELIVERY' and route.order.delivery_address:
                    delivery_addresses.append(route.order.delivery_address)
        
        item.order_numbers = ", ".join(order_numbers) if order_numbers else None
        # Add pickup/delivery addresses as dynamic attributes
        item.pickup_address = ", ".join(set(pickup_addresses)) if pickup_addresses else None
        item.delivery_address = ", ".join(set(delivery_addresses)) if delivery_addresses else None
    
    return DispatchListResponse(total=total, items=items)


@router.get("/dashboard", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """대시보드 통계 조회"""
    from datetime import date, datetime
    from app.models.vehicle import Vehicle
    
    today = date.today()
    
    # 전체 주문 수 (오늘)
    total_orders = db.query(func.count(Order.id)).filter(
        Order.created_at >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ).scalar() or 0
    
    # 배차 대기 중인 주문 수
    pending_orders = db.query(func.count(Order.id)).filter(
        Order.status == OrderStatus.PENDING
    ).scalar() or 0
    
    # 진행 중인 배차 수 (확정 + 진행중)
    active_dispatches = db.query(func.count(Dispatch.id)).filter(
        Dispatch.status.in_([DispatchStatus.CONFIRMED, DispatchStatus.IN_PROGRESS])
    ).scalar() or 0
    
    # 오늘 완료된 배차 수
    completed_today = db.query(func.count(Dispatch.id)).filter(
        Dispatch.dispatch_date == today,
        Dispatch.status == DispatchStatus.COMPLETED
    ).scalar() or 0
    
    # 사용 가능한 차량 수
    available_vehicles = db.query(func.count(Vehicle.id)).filter(
        Vehicle.status == VehicleStatus.AVAILABLE,
        Vehicle.is_active == True
    ).scalar() or 0
    
    # 운행 중인 차량 수
    active_vehicles = db.query(func.count(Vehicle.id)).filter(
        Vehicle.status == VehicleStatus.IN_USE
    ).scalar() or 0
    
    logger.info(f"Dashboard stats: orders={total_orders}, pending={pending_orders}, "
                f"active_dispatches={active_dispatches}, completed_today={completed_today}, "
                f"available_vehicles={available_vehicles}, active_vehicles={active_vehicles}")
    
    return DashboardStatsResponse(
        total_orders=total_orders,
        pending_orders=pending_orders,
        active_dispatches=active_dispatches,
        completed_today=completed_today,
        available_vehicles=available_vehicles,
        active_vehicles=active_vehicles,
        revenue_today=0,  # TODO: 실제 수익 계산 로직 추가
        revenue_month=0   # TODO: 실제 수익 계산 로직 추가
    )


@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """
    대시보드 실시간 업데이트 WebSocket
    
    클라이언트에게 5초마다 대시보드 통계를 전송합니다.
    """
    await websocket.accept()
    logger.info("WebSocket connected: dashboard")
    
    try:
        from app.core.database import SessionLocal
        from datetime import date, datetime
        
        while True:
            # 5초마다 통계 업데이트
            await asyncio.sleep(5)
            
            # 새 세션 생성
            db = SessionLocal()
            try:
                from app.models.vehicle import Vehicle
                
                today = date.today()
                
                # 전체 주문 수 (오늘)
                total_orders = db.query(func.count(Order.id)).filter(
                    Order.created_at >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                ).scalar() or 0
                
                # 배차 대기 중인 주문 수
                pending_orders = db.query(func.count(Order.id)).filter(
                    Order.status == OrderStatus.PENDING
                ).scalar() or 0
                
                # 진행 중인 배차 수 (확정 + 진행중)
                active_dispatches = db.query(func.count(Dispatch.id)).filter(
                    Dispatch.status.in_([DispatchStatus.CONFIRMED, DispatchStatus.IN_PROGRESS])
                ).scalar() or 0
                
                # 오늘 완료된 배차 수
                completed_today = db.query(func.count(Dispatch.id)).filter(
                    Dispatch.dispatch_date == today,
                    Dispatch.status == DispatchStatus.COMPLETED
                ).scalar() or 0
                
                # 사용 가능한 차량 수
                available_vehicles = db.query(func.count(Vehicle.id)).filter(
                    Vehicle.status == VehicleStatus.AVAILABLE,
                    Vehicle.is_active == True
                ).scalar() or 0
                
                # 운행 중인 차량 수
                active_vehicles = db.query(func.count(Vehicle.id)).filter(
                    Vehicle.status == VehicleStatus.IN_USE
                ).scalar() or 0
                
                stats = {
                    "total_orders": total_orders,
                    "pending_orders": pending_orders,
                    "active_dispatches": active_dispatches,
                    "completed_today": completed_today,
                    "available_vehicles": available_vehicles,
                    "active_vehicles": active_vehicles,
                    "revenue_today": 0.0,
                    "revenue_month": 0.0,
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send_json(stats)
                logger.debug(f"Sent dashboard stats: pending={pending_orders}, active={active_dispatches}")
                
            except Exception as inner_e:
                logger.error(f"Error collecting stats: {type(inner_e).__name__}: {str(inner_e)}", exc_info=True)
                # Continue without closing connection
                pass
            finally:
                db.close()
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: dashboard")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.close()
        except:
            pass


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
    
    try:
        # Reset order statuses - load orders explicitly
        for route in dispatch.routes:
            if route.order_id:
                order = db.query(Order).filter(Order.id == route.order_id).first()
                if order:
                    order.status = OrderStatus.PENDING
                    logger.info(f"Reset order {order.order_number} status to PENDING")
        
        # Reset vehicle status to AVAILABLE if it was IN_USE
        if dispatch.vehicle and dispatch.vehicle.status == VehicleStatus.IN_USE:
            dispatch.vehicle.status = VehicleStatus.AVAILABLE
            logger.info(f"Vehicle {dispatch.vehicle.code} status reset to AVAILABLE")
        
        # Delete all routes first (cascade)
        for route in list(dispatch.routes):
            db.delete(route)
        
        # Then delete the dispatch
        db.delete(dispatch)
        db.commit()
        
        logger.info(f"Deleted dispatch: {dispatch.dispatch_number}")
        return {"message": "배차가 삭제되었습니다"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete dispatch {dispatch_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"배차 삭제 중 오류가 발생했습니다: {str(e)}"
        )


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
        
        # Update vehicle status to IN_USE
        if dispatch.vehicle:
            dispatch.vehicle.status = VehicleStatus.IN_USE
            logger.info(f"Vehicle {dispatch.vehicle.code} status changed to IN_USE")
        
        # Update order statuses
        updated_orders = 0
        for route in dispatch.routes:
            if route.order_id:
                # Fetch order explicitly if relationship is not loaded
                order = route.order if route.order else db.query(Order).filter(Order.id == route.order_id).first()
                if order:
                    logger.info(f"🔄 Updating order {order.order_number} status: {order.status} → ASSIGNED")
                    order.status = OrderStatus.ASSIGNED
                    updated_orders += 1
                else:
                    logger.warning(f"⚠️  Route has order_id={route.order_id} but order not found!")
            else:
                logger.debug(f"Route sequence {route.sequence} has no order_id (type: {route.route_type})")
        
        logger.info(f"✅ Confirmed dispatch {dispatch.dispatch_number}: updated {updated_orders} orders")
        confirmed.append(dispatch.dispatch_number)
    
    db.commit()
    
    logger.info(f"Confirmed {len(confirmed)} dispatches")
    
    return {
        "confirmed": len(confirmed),
        "failed": len(errors),
        "confirmed_dispatch_numbers": confirmed,
        "errors": errors
    }


@router.post("/complete")
def complete_dispatches(
    request: DispatchCompleteRequest,
    db: Session = Depends(get_db)
):
    """배차 완료"""
    completed = []
    errors = []
    
    for dispatch_id in request.dispatch_ids:
        dispatch = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
        if not dispatch:
            errors.append({"dispatch_id": dispatch_id, "error": "배차를 찾을 수 없음"})
            continue
        
        if dispatch.status != DispatchStatus.CONFIRMED and dispatch.status != DispatchStatus.IN_PROGRESS:
            errors.append({"dispatch_id": dispatch_id, "error": "확정 또는 진행중 상태가 아님"})
            continue
        
        dispatch.status = DispatchStatus.COMPLETED
        
        # Update vehicle status back to AVAILABLE
        if dispatch.vehicle:
            dispatch.vehicle.status = VehicleStatus.AVAILABLE
            logger.info(f"Vehicle {dispatch.vehicle.code} status changed to AVAILABLE (dispatch completed)")
        
        # Update order statuses to DELIVERED
        for route in dispatch.routes:
            if route.order:
                route.order.status = OrderStatus.DELIVERED
        
        completed.append(dispatch.dispatch_number)
    
    db.commit()
    
    logger.info(f"Completed {len(completed)} dispatches")
    
    return {
        "completed": len(completed),
        "failed": len(errors),
        "completed_dispatch_numbers": completed,
        "errors": errors
    }


@router.post("/cancel")
def cancel_dispatches(
    request: DispatchCancelRequest,
    db: Session = Depends(get_db)
):
    """배차 취소"""
    cancelled = []
    errors = []
    
    for dispatch_id in request.dispatch_ids:
        dispatch = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
        if not dispatch:
            errors.append({"dispatch_id": dispatch_id, "error": "배차를 찾을 수 없음"})
            continue
        
        if dispatch.status == DispatchStatus.COMPLETED:
            errors.append({"dispatch_id": dispatch_id, "error": "완료된 배차는 취소할 수 없음"})
            continue
        
        old_status = dispatch.status
        dispatch.status = DispatchStatus.CANCELLED
        
        # Update vehicle status back to AVAILABLE if it was IN_USE
        if dispatch.vehicle and dispatch.vehicle.status == VehicleStatus.IN_USE:
            dispatch.vehicle.status = VehicleStatus.AVAILABLE
            logger.info(f"Vehicle {dispatch.vehicle.code} status changed to AVAILABLE (dispatch cancelled)")
        
        # Update order statuses back to PENDING
        for route in dispatch.routes:
            if route.order:
                route.order.status = OrderStatus.PENDING
        
        # Add cancel reason to notes
        if request.reason:
            if dispatch.notes:
                dispatch.notes = f"{dispatch.notes}\n[취소 사유: {request.reason}]"
            else:
                dispatch.notes = f"[취소 사유: {request.reason}]"
        
        cancelled.append(dispatch.dispatch_number)
        logger.info(f"Cancelled dispatch {dispatch.dispatch_number} (was {old_status.value})")
    
    db.commit()
    
    logger.info(f"Cancelled {len(cancelled)} dispatches")
    
    return {
        "cancelled": len(cancelled),
        "failed": len(errors),
        "cancelled_dispatch_numbers": cancelled,
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
