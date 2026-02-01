from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from pathlib import Path

from app.core.database import get_db
from app.models.order import Order, OrderStatus
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse, OrderWithClientsResponse
)
from app.services.excel_upload_service import ExcelUploadService
from app.services.excel_template_service import ExcelTemplateService
from loguru import logger

router = APIRouter()


@router.get("/", response_model=OrderListResponse)
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[OrderStatus] = None,
    temperature_zone: Optional[str] = None,
    order_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """주문 목록 조회"""
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    
    if temperature_zone:
        query = query.filter(Order.temperature_zone == temperature_zone)
    
    if order_date:
        query = query.filter(Order.order_date == order_date)
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    # Add client names (Pydantic's field_serializer will handle time conversion)
    for item in items:
        if item.pickup_client:
            item.pickup_client_name = item.pickup_client.name
        if item.delivery_client:
            item.delivery_client_name = item.delivery_client.name
    
    return OrderListResponse(total=total, items=items)


@router.get("/{order_id}", response_model=OrderWithClientsResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """주문 상세 조회"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    
    # Add client info (Pydantic's field_serializer will handle time conversion)
    order.pickup_client_name = order.pickup_client.name if order.pickup_client else None
    order.delivery_client_name = order.delivery_client.name if order.delivery_client else None
    
    return order


@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """주문 생성 (거래처 ID 또는 주소로 입력 가능)"""
    from datetime import time as time_type
    
    # Check if order number already exists
    existing = db.query(Order).filter(Order.order_number == order_data.order_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 주문번호입니다")
    
    from app.models.client import Client
    from app.services.naver_map_service import NaverMapService
    
    order_dict = order_data.model_dump()
    
    # Convert time strings to time objects
    for time_field in ['pickup_start_time', 'pickup_end_time', 'delivery_start_time', 'delivery_end_time']:
        if order_dict.get(time_field):
            time_str = order_dict[time_field]
            if isinstance(time_str, str):
                hour, minute = map(int, time_str.split(':'))
                order_dict[time_field] = time_type(hour, minute)
    
    # 거래처 ID로 입력한 경우 - 거래처 존재 확인
    if order_data.pickup_client_id:
        pickup_client = db.query(Client).filter(Client.id == order_data.pickup_client_id).first()
        if not pickup_client:
            raise HTTPException(status_code=404, detail="상차 거래처를 찾을 수 없습니다")
    elif order_data.pickup_address:
        # 주소로 입력한 경우 - Naver 지오코딩
        naver_service = NaverMapService()
        full_address = f"{order_data.pickup_address} {order_data.pickup_address_detail or ''}".strip()
        latitude, longitude, error = await naver_service.geocode_address(full_address)
        
        if latitude and longitude:
            # 위경도 저장
            order_dict['pickup_latitude'] = latitude
            order_dict['pickup_longitude'] = longitude
            logger.info(f"Geocoded pickup address: {full_address} -> ({latitude}, {longitude})")
        else:
            logger.warning(f"Failed to geocode pickup address: {full_address}, error: {error}")
    else:
        raise HTTPException(status_code=400, detail="상차 거래처 ID 또는 주소를 입력해주세요")
    
    if order_data.delivery_client_id:
        delivery_client = db.query(Client).filter(Client.id == order_data.delivery_client_id).first()
        if not delivery_client:
            raise HTTPException(status_code=404, detail="하차 거래처를 찾을 수 없습니다")
    elif order_data.delivery_address:
        # 주소로 입력한 경우 - Naver 지오코딩
        naver_service = NaverMapService()
        full_address = f"{order_data.delivery_address} {order_data.delivery_address_detail or ''}".strip()
        latitude, longitude, error = await naver_service.geocode_address(full_address)
        
        if latitude and longitude:
            # 위경도 저장
            order_dict['delivery_latitude'] = latitude
            order_dict['delivery_longitude'] = longitude
            logger.info(f"Geocoded delivery address: {full_address} -> ({latitude}, {longitude})")
        else:
            logger.warning(f"Failed to geocode delivery address: {full_address}, error: {error}")
    else:
        raise HTTPException(status_code=400, detail="하차 거래처 ID 또는 주소를 입력해주세요")
    
    order_dict['status'] = OrderStatus.PENDING
    order = Order(**order_dict)
    db.add(order)
    db.commit()
    db.refresh(order)
    
    logger.info(f"Created order: {order.order_number}")
    return order


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db)
):
    """주문 수정"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    
    # Update fields
    update_data = order_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    
    # Add client info (Pydantic's field_serializer will handle time conversion)
    order.pickup_client_name = order.pickup_client.name if order.pickup_client else None
    order.delivery_client_name = order.delivery_client.name if order.delivery_client else None
    
    logger.info(f"Updated order: {order.order_number}")
    return order


@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """주문 삭제"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    
    # Check if order is part of a dispatch
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="배차대기 상태의 주문만 삭제할 수 있습니다"
        )
    
    db.delete(order)
    db.commit()
    
    logger.info(f"Deleted order: {order.order_number}")
    return {"message": "주문이 삭제되었습니다"}


@router.post("/upload")
async def upload_orders_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """엑셀 파일로 주문 일괄 업로드"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="엑셀 파일만 업로드 가능합니다")
    
    try:
        content = await file.read()
        result = ExcelUploadService.upload_orders(db, content)
        
        logger.info(f"Uploaded orders: {result['created']} created, {result['failed']} failed")
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading orders: {e}")
        raise HTTPException(status_code=500, detail="업로드 중 오류가 발생했습니다")


@router.get("/pending/count")
def get_pending_orders_count(db: Session = Depends(get_db)):
    """배차 대기 중인 주문 수 조회"""
    count = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
    return {"pending_count": count}



@router.get("/template/download")
def download_order_template():
    """주문 Excel 템플릿 다운로드"""
    template_path = ExcelTemplateService.create_orders_template()
    
    if not Path(template_path).exists():
        raise HTTPException(status_code=404, detail="템플릿 파일을 찾을 수 없습니다")
    
    return FileResponse(
        path=template_path,
        filename="orders_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
