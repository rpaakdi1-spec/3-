from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from pathlib import Path

from app.core.database import get_db
from app.models.order import Order, OrderStatus
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse
)
from app.services.excel_upload_service import ExcelUploadService
from app.services.excel_template_service import ExcelTemplateService
from app.services.order_nlp_service import parse_order_text
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
    
    # Convert items to dict to avoid SQLAlchemy relationship serialization issues
    items_dict = []
    for order in items:
        order_dict = {
            'id': order.id,
            'order_number': order.order_number,
            'order_date': order.order_date,
            'temperature_zone': order.temperature_zone,
            'pickup_client_id': order.pickup_client_id,
            'delivery_client_id': order.delivery_client_id,
            'pickup_address': order.pickup_address,
            'pickup_address_detail': order.pickup_address_detail,
            'delivery_address': order.delivery_address,
            'delivery_address_detail': order.delivery_address_detail,
            'pallet_count': order.pallet_count,
            'weight_kg': order.weight_kg,
            'volume_cbm': order.volume_cbm,
            'product_name': order.product_name,
            'product_code': order.product_code,
            'pickup_start_time': order.pickup_start_time,
            'pickup_end_time': order.pickup_end_time,
            'delivery_start_time': order.delivery_start_time,
            'delivery_end_time': order.delivery_end_time,
            'requested_delivery_date': order.requested_delivery_date,
            'priority': order.priority,
            'is_reserved': order.is_reserved,
            'reserved_at': order.reserved_at,
            'confirmed_at': order.confirmed_at,
            'recurring_type': order.recurring_type,
            'recurring_end_date': order.recurring_end_date,
            'requires_forklift': order.requires_forklift,
            'is_stackable': order.is_stackable,
            'notes': order.notes,
            'status': order.status,
            'created_at': order.created_at,
            'updated_at': order.updated_at,
            'pickup_latitude': order.pickup_latitude,
            'pickup_longitude': order.pickup_longitude,
            'delivery_latitude': order.delivery_latitude,
            'delivery_longitude': order.delivery_longitude,
            # Add client names
            'pickup_client_name': order.pickup_client.name if order.pickup_client else None,
            'delivery_client_name': order.delivery_client.name if order.delivery_client else None,
        }
        items_dict.append(order_dict)
    
    return OrderListResponse(total=total, items=items_dict)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """주문 상세 조회"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    
    # Convert to dict to avoid SQLAlchemy relationship serialization issues
    order_dict = {
        'id': order.id,
        'order_number': order.order_number,
        'order_date': order.order_date,
        'temperature_zone': order.temperature_zone,
        'pickup_client_id': order.pickup_client_id,
        'delivery_client_id': order.delivery_client_id,
        'pickup_address': order.pickup_address,
        'pickup_address_detail': order.pickup_address_detail,
        'delivery_address': order.delivery_address,
        'delivery_address_detail': order.delivery_address_detail,
        'pallet_count': order.pallet_count,
        'weight_kg': order.weight_kg,
        'volume_cbm': order.volume_cbm,
        'product_name': order.product_name,
        'product_code': order.product_code,
        'pickup_start_time': order.pickup_start_time,
        'pickup_end_time': order.pickup_end_time,
        'delivery_start_time': order.delivery_start_time,
        'delivery_end_time': order.delivery_end_time,
        'requested_delivery_date': order.requested_delivery_date,
        'priority': order.priority,
        'is_reserved': order.is_reserved,
        'reserved_at': order.reserved_at,
        'confirmed_at': order.confirmed_at,
        'recurring_type': order.recurring_type,
        'recurring_end_date': order.recurring_end_date,
        'requires_forklift': order.requires_forklift,
        'is_stackable': order.is_stackable,
        'notes': order.notes,
        'status': order.status,
        'created_at': order.created_at,
        'updated_at': order.updated_at,
        'pickup_latitude': order.pickup_latitude,
        'pickup_longitude': order.pickup_longitude,
        'delivery_latitude': order.delivery_latitude,
        'delivery_longitude': order.delivery_longitude,
        # Add client names
        'pickup_client_name': order.pickup_client.name if order.pickup_client else None,
        'delivery_client_name': order.delivery_client.name if order.delivery_client else None,
    }
    
    return order_dict


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
        try:
            naver_service = NaverMapService()
            full_address = f"{order_data.pickup_address} {order_data.pickup_address_detail or ''}".strip()
            result = await naver_service.geocode_address(full_address)
            
            if result and len(result) == 3:
                latitude, longitude, error = result
                if latitude and longitude:
                    # 위경도 저장
                    order_dict['pickup_latitude'] = latitude
                    order_dict['pickup_longitude'] = longitude
                    logger.info(f"Geocoded pickup address: {full_address} -> ({latitude}, {longitude})")
                else:
                    logger.warning(f"Failed to geocode pickup address: {full_address}, error: {error}")
            else:
                logger.warning(f"Geocoding returned None for pickup address: {full_address}")
        except Exception as e:
            logger.error(f"Error during pickup geocoding: {str(e)}")
            # Continue without geocoding
    else:
        raise HTTPException(status_code=400, detail="상차 거래처 ID 또는 주소를 입력해주세요")
    
    if order_data.delivery_client_id:
        delivery_client = db.query(Client).filter(Client.id == order_data.delivery_client_id).first()
        if not delivery_client:
            raise HTTPException(status_code=404, detail="하차 거래처를 찾을 수 없습니다")
    elif order_data.delivery_address:
        # 주소로 입력한 경우 - Naver 지오코딩
        try:
            naver_service = NaverMapService()
            full_address = f"{order_data.delivery_address} {order_data.delivery_address_detail or ''}".strip()
            result = await naver_service.geocode_address(full_address)
            
            if result and len(result) == 3:
                latitude, longitude, error = result
                if latitude and longitude:
                    # 위경도 저장
                    order_dict['delivery_latitude'] = latitude
                    order_dict['delivery_longitude'] = longitude
                    logger.info(f"Geocoded delivery address: {full_address} -> ({latitude}, {longitude})")
                else:
                    logger.warning(f"Failed to geocode delivery address: {full_address}, error: {error}")
            else:
                logger.warning(f"Geocoding returned None for delivery address: {full_address}")
        except Exception as e:
            logger.error(f"Error during delivery geocoding: {str(e)}")
            # Continue without geocoding
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
    
    # Debug logging for time fields
    time_fields = ['pickup_start_time', 'pickup_end_time', 'delivery_start_time', 'delivery_end_time']
    for field in time_fields:
        if field in update_data:
            logger.info(f"🕐 Updating {field}: {update_data[field]} (type: {type(update_data[field])})")
    
    for field, value in update_data.items():
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    
    # Verify time fields after commit
    for field in time_fields:
        if hasattr(order, field):
            value = getattr(order, field)
            logger.info(f"✅ After commit {field}: {value} (type: {type(value)})")
    
    # Convert to dict to avoid SQLAlchemy relationship serialization issues
    order_dict = {
        'id': order.id,
        'order_number': order.order_number,
        'order_date': order.order_date,
        'temperature_zone': order.temperature_zone,
        'pickup_client_id': order.pickup_client_id,
        'delivery_client_id': order.delivery_client_id,
        'pickup_address': order.pickup_address,
        'pickup_address_detail': order.pickup_address_detail,
        'delivery_address': order.delivery_address,
        'delivery_address_detail': order.delivery_address_detail,
        'pallet_count': order.pallet_count,
        'weight_kg': order.weight_kg,
        'volume_cbm': order.volume_cbm,
        'product_name': order.product_name,
        'product_code': order.product_code,
        'pickup_start_time': order.pickup_start_time,
        'pickup_end_time': order.pickup_end_time,
        'delivery_start_time': order.delivery_start_time,
        'delivery_end_time': order.delivery_end_time,
        'requested_delivery_date': order.requested_delivery_date,
        'priority': order.priority,
        'is_reserved': order.is_reserved,
        'reserved_at': order.reserved_at,
        'confirmed_at': order.confirmed_at,
        'recurring_type': order.recurring_type,
        'recurring_end_date': order.recurring_end_date,
        'requires_forklift': order.requires_forklift,
        'is_stackable': order.is_stackable,
        'notes': order.notes,
        'status': order.status,
        'created_at': order.created_at,
        'updated_at': order.updated_at,
        'pickup_latitude': order.pickup_latitude,
        'pickup_longitude': order.pickup_longitude,
        'delivery_latitude': order.delivery_latitude,
        'delivery_longitude': order.delivery_longitude,
        # Add client names
        'pickup_client_name': order.pickup_client.name if order.pickup_client else None,
        'delivery_client_name': order.delivery_client.name if order.delivery_client else None,
    }
    
    logger.info(f"Updated order: {order.order_number}")
    return order_dict


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


@router.post("/parse-nlp")
def parse_order_nlp(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    자연어 주문 파싱 (NLP)
    
    거래처의 자연어 요청을 구조화된 주문으로 변환합니다.
    
    Example:
        {
            "text": "[02/03] 추가 배차요청\\n백암 _ 저온 → 경산 16판 1대\\n동이천센터 → 양산 16판 1대"
        }
    
    Returns:
        {
            "success": true,
            "orders": [...],
            "count": 2,
            "valid_count": 2,
            "review_count": 0
        }
    """
    text = request.get('text', '')
    
    if not text:
        raise HTTPException(status_code=400, detail="텍스트가 필요합니다")
    
    logger.info(f"📝 NLP 주문 파싱 요청: {len(text)} characters")
    
    result = parse_order_text(db, text)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result['message'])
    
    logger.info(f"✅ NLP 파싱 완료: {result['count']}건 (유효: {result['valid_count']}, 검토 필요: {result['review_count']})")
    
    return result


@router.post("/parse-batch-dispatch")
def parse_batch_dispatch(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    배치 배차 텍스트 파싱 (목우촌 형식)
    
    입력 형식:
    **2/23(월)목우촌 오후배차**
    13:00 / 식육11톤(냉동)
    13:30 / 식육5톤
    14:30 / 육가공11톤
    15:00 / 식육5톤
    16:30 / 육가공11톤
    
    상차지:전북 김제시 금산면 용산리 9-13
    하차지:경기도 안성시 양성면 양성로376-106
    
    Returns:
        {
            "success": true,
            "orders": [...],
            "count": 5
        }
    """
    import re
    from datetime import datetime, time as datetime_time
    from app.models.order import TemperatureZone
    
    text = request.get('text', '')
    pickup_address = request.get('pickup_address', '')
    delivery_address = request.get('delivery_address', '')
    
    if not text:
        raise HTTPException(status_code=400, detail="배차 텍스트가 필요합니다")
    
    logger.info(f"📝 배치 배차 파싱 시작...")
    
    orders = []
    order_number_prefix = f"ORD-{datetime.now().strftime('%Y%m%d')}"
    
    # 1. 날짜 추출 (예: 2/23(월))
    date_match = re.search(r'(\d{1,2})/(\d{1,2})', text)
    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        current_year = datetime.now().year
        order_date = date(current_year, month, day)
    else:
        order_date = date.today()
    
    # 2. 고객사명 추출 (예: 목우촌)
    client_match = re.search(r'[)\]]([가-힣]+)\s*(?:오전|오후)?배차', text)
    client_name = client_match.group(1) if client_match else "고객사"
    
    # 3. 각 배차 라인 파싱
    lines = text.split('\n')
    order_count = 0
    
    for line in lines:
        # 시간 / 품목톤수(온도) 형식 파싱
        # 예: 13:00 / 식육11톤(냉동)
        match = re.search(r'(\d{1,2}):(\d{2})\s*/\s*([가-힣]+)(\d+(?:\.\d+)?)톤(?:\(([^)]+)\))?', line)
        
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            product_name = match.group(3)  # 식육, 육가공 등
            tonnage = float(match.group(4))  # 11, 5 등
            temp_indicator = match.group(5)  # 냉동, None
            
            # 시간
            pickup_time = datetime_time(hour, minute)
            
            # 온도대 결정
            if temp_indicator and '냉동' in temp_indicator:
                temperature_zone = TemperatureZone.FROZEN
            else:
                temperature_zone = TemperatureZone.REFRIGERATED
            
            # 톤수에 따른 팔레트 수 매핑
            # 18톤 = 18팔레트, 11톤 = 16팔레트, 5톤 = 10팔레트
            if tonnage >= 18:
                pallet_count = 18
            elif tonnage >= 11:
                pallet_count = 16
            elif tonnage >= 5:
                pallet_count = 10
            else:
                # 5톤 미만은 비율로 계산 (톤당 2팔레트)
                pallet_count = max(1, int(tonnage * 2))
            
            # 중량 (톤 → kg)
            weight_kg = tonnage * 1000
            
            order_count += 1
            order_number = f"{order_number_prefix}-{order_count:03d}"
            
            order = {
                'order_number': order_number,
                'order_date': order_date.isoformat(),
                'temperature_zone': temperature_zone.value,
                'pickup_address': pickup_address or f"{client_name} 본사",
                'delivery_address': delivery_address,
                'pallet_count': pallet_count,
                'weight_kg': weight_kg,
                'product_name': f"{product_name} {int(tonnage)}톤",
                'pickup_start_time': pickup_time.isoformat(),
                'pickup_end_time': datetime_time(hour + 1, minute).isoformat(),
                'delivery_start_time': '16:00:00',
                'delivery_end_time': '18:00:00',
                'requested_delivery_date': order_date.isoformat(),
                'priority': 5,
                'requires_forklift': True,
                'is_stackable': True,
                'notes': f"{client_name} {product_name} ({temperature_zone.value})"
            }
            
            orders.append(order)
            logger.info(f"✅ 배차 {order_count}: {pickup_time.strftime('%H:%M')} - {product_name} {tonnage}톤 ({temperature_zone.value})")
    
    logger.info(f"✅ 총 {len(orders)}건의 배차 파싱 완료")
    
    return {
        'success': True,
        'orders': orders,
        'count': len(orders),
        'client_name': client_name,
        'order_date': order_date.isoformat()
    }


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
