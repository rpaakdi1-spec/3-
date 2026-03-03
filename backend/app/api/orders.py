from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime, timedelta
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
            'delivery_date': order.delivery_date,
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
        'delivery_date': order.delivery_date,
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
    
    # 디버깅: 요청 데이터 로깅
    logger.info(f"📥 주문 생성 요청: {order_data.model_dump()}")
    
    # Check if order number already exists
    existing = db.query(Order).filter(Order.order_number == order_data.order_number).first()
    if existing:
        logger.warning(f"❌ 중복된 주문번호: {order_data.order_number}")
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
    # 고정 좌표 매핑 (목우촌 등 자주 사용되는 주소)
    # 템플릿에서 자동으로 가져오기
    from app.models.dispatch_template import DispatchTemplate
    
    FIXED_COORDINATES = {}
    templates = db.query(DispatchTemplate).filter(
        DispatchTemplate.is_active == True,
        DispatchTemplate.pickup_latitude.isnot(None),
        DispatchTemplate.pickup_longitude.isnot(None)
    ).all()
    
    for tmpl in templates:
        if tmpl.default_pickup_address:
            FIXED_COORDINATES[tmpl.default_pickup_address] = (
                tmpl.pickup_latitude, 
                tmpl.pickup_longitude
            )
        if tmpl.default_delivery_address and tmpl.delivery_latitude and tmpl.delivery_longitude:
            FIXED_COORDINATES[tmpl.default_delivery_address] = (
                tmpl.delivery_latitude,
                tmpl.delivery_longitude
            )
    
    if order_data.pickup_client_id:
        pickup_client = db.query(Client).filter(Client.id == order_data.pickup_client_id).first()
        if not pickup_client:
            raise HTTPException(status_code=404, detail="상차 거래처를 찾을 수 없습니다")
    elif order_data.pickup_address:
        full_address = f"{order_data.pickup_address} {order_data.pickup_address_detail or ''}".strip()
        
        # 고정 좌표가 있는 경우
        if order_data.pickup_address in FIXED_COORDINATES:
            latitude, longitude = FIXED_COORDINATES[order_data.pickup_address]
            order_dict['pickup_latitude'] = latitude
            order_dict['pickup_longitude'] = longitude
            logger.info(f"✅ Using fixed coordinates for pickup: {order_data.pickup_address} -> ({latitude}, {longitude})")
        else:
            # Naver 지오코딩 사용
            try:
                naver_service = NaverMapService()
                result = await naver_service.geocode_address(full_address)
                
                if result and len(result) == 3:
                    latitude, longitude, error = result
                    if latitude and longitude:
                        order_dict['pickup_latitude'] = latitude
                        order_dict['pickup_longitude'] = longitude
                        logger.info(f"Geocoded pickup address: {full_address} -> ({latitude}, {longitude})")
                    else:
                        logger.warning(f"Failed to geocode pickup address: {full_address}, error: {error}")
                else:
                    logger.warning(f"Geocoding returned None for pickup address: {full_address}")
            except Exception as e:
                logger.error(f"Error during pickup geocoding: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="상차 거래처 ID 또는 주소를 입력해주세요")
    
    if order_data.delivery_client_id:
        delivery_client = db.query(Client).filter(Client.id == order_data.delivery_client_id).first()
        if not delivery_client:
            raise HTTPException(status_code=404, detail="하차 거래처를 찾을 수 없습니다")
    elif order_data.delivery_address:
        full_address = f"{order_data.delivery_address} {order_data.delivery_address_detail or ''}".strip()
        
        # 고정 좌표가 있는 경우
        if order_data.delivery_address in FIXED_COORDINATES:
            latitude, longitude = FIXED_COORDINATES[order_data.delivery_address]
            order_dict['delivery_latitude'] = latitude
            order_dict['delivery_longitude'] = longitude
            logger.info(f"✅ Using fixed coordinates for delivery: {order_data.delivery_address} -> ({latitude}, {longitude})")
        else:
            # Naver 지오코딩 사용
            try:
                naver_service = NaverMapService()
                result = await naver_service.geocode_address(full_address)
                
                if result and len(result) == 3:
                    latitude, longitude, error = result
                    if latitude and longitude:
                        order_dict['delivery_latitude'] = latitude
                        order_dict['delivery_longitude'] = longitude
                        logger.info(f"Geocoded delivery address: {full_address} -> ({latitude}, {longitude})")
                    else:
                        logger.warning(f"Failed to geocode delivery address: {full_address}, error: {error}")
                else:
                    logger.warning(f"Geocoding returned None for delivery address: {full_address}")
            except Exception as e:
                logger.error(f"Error during delivery geocoding: {str(e)}")
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
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db)
):
    """주문 수정 (주소 변경 시 좌표 자동 재변환)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    
    from app.services.naver_map_service import NaverMapService
    
    # Update fields
    update_data = order_data.model_dump(exclude_unset=True)
    
    # Debug logging for time fields
    time_fields = ['pickup_start_time', 'pickup_end_time', 'delivery_start_time', 'delivery_end_time']
    for field in time_fields:
        if field in update_data:
            logger.info(f"🕐 Updating {field}: {update_data[field]} (type: {type(update_data[field])})")
    
    # 주소가 변경되었는지 확인
    pickup_address_changed = (
        'pickup_address' in update_data and update_data['pickup_address'] != order.pickup_address
    ) or (
        'pickup_address_detail' in update_data and update_data['pickup_address_detail'] != order.pickup_address_detail
    )
    
    delivery_address_changed = (
        'delivery_address' in update_data and update_data['delivery_address'] != order.delivery_address
    ) or (
        'delivery_address_detail' in update_data and update_data['delivery_address_detail'] != order.delivery_address_detail
    )
    
    # 필드 업데이트
    for field, value in update_data.items():
        setattr(order, field, value)
    
    # 픽업 주소가 변경된 경우 좌표 재변환
    if pickup_address_changed and order.pickup_address:
        try:
            naver_service = NaverMapService()
            full_address = f"{order.pickup_address} {order.pickup_address_detail or ''}".strip()
            result = await naver_service.geocode_address(full_address)
            
            if result and len(result) >= 2:
                latitude, longitude = result[0], result[1]
                if latitude and longitude:
                    order.pickup_latitude = latitude
                    order.pickup_longitude = longitude
                    logger.info(f"✅ 픽업 주소 변경 → 좌표 재변환: {full_address} -> ({latitude}, {longitude})")
                else:
                    logger.warning(f"⚠️ 픽업 좌표 변환 실패: {full_address}")
            else:
                logger.warning(f"⚠️ 픽업 좌표 없음: {full_address}")
        except Exception as e:
            logger.error(f"❌ 픽업 좌표 변환 오류: {e}")
    
    # 배송 주소가 변경된 경우 좌표 재변환
    if delivery_address_changed and order.delivery_address:
        try:
            naver_service = NaverMapService()
            full_address = f"{order.delivery_address} {order.delivery_address_detail or ''}".strip()
            result = await naver_service.geocode_address(full_address)
            
            if result and len(result) >= 2:
                latitude, longitude = result[0], result[1]
                if latitude and longitude:
                    order.delivery_latitude = latitude
                    order.delivery_longitude = longitude
                    logger.info(f"✅ 배송 주소 변경 → 좌표 재변환: {full_address} -> ({latitude}, {longitude})")
                else:
                    logger.warning(f"⚠️ 배송 좌표 변환 실패: {full_address}")
            else:
                logger.warning(f"⚠️ 배송 좌표 없음: {full_address}")
        except Exception as e:
            logger.error(f"❌ 배송 좌표 변환 오류: {e}")
    
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
        'delivery_date': order.delivery_date,
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
    배치 배차 텍스트 파싱 (템플릿 기반)
    
    거래처별 템플릿을 자동으로 감지하여 파싱 규칙 적용
    
    입력 형식:
    **2/23(월)목우촌 오후배차**
    13:00 / 식육11톤(냉동)
    13:30 / 식육5톤
    
    Returns:
        {
            "success": true,
            "orders": [...],
            "count": 5,
            "template_used": "목우촌"
        }
    """
    import re
    from datetime import datetime, time as datetime_time
    from app.models.order import TemperatureZone
    from app.models.dispatch_template import DispatchTemplate
    
    text = request.get('text', '')
    pickup_address = request.get('pickup_address', '')
    delivery_address = request.get('delivery_address', '')
    
    if not text:
        raise HTTPException(status_code=400, detail="배차 텍스트가 필요합니다")
    
    logger.info(f"📝 배치 배차 파싱 시작...")
    
    # 1. 템플릿 자동 감지
    template = None
    templates = db.query(DispatchTemplate).filter(
        DispatchTemplate.is_active == True
    ).all()
    
    for tmpl in templates:
        keywords = tmpl.detection_keywords if isinstance(tmpl.detection_keywords, list) else []
        for keyword in keywords:
            if keyword.lower() in text.lower():
                template = tmpl
                logger.info(f"🎯 템플릿 감지: {template.name} (키워드: {keyword})")
                break
        if template:
            break
    
    if not template:
        logger.warning(f"⚠️ 매칭되는 템플릿 없음, 기본 파싱 사용")
        # 기본 파싱 규칙 사용 (하드코딩)
        parsing_rules = {
            "time_pattern": r"(\d{1,2}):(\d{2})",
            "product_pattern": r"식육|육가공",
            "tonnage_pattern": r"(\d+(?:\.\d+)?)톤",
            "temperature_keywords": {"냉동": "FROZEN", "냉장": "REFRIGERATED"},
            "default_temperature": "REFRIGERATED",
            "pallet_calculation": {"18": 18, "11": 16, "5": 10, "default_multiplier": 2},
            "delivery_time_offset_hours": 4,
            "notes_template": "자동 파싱: {client_name} 배차"
        }
        template_name = "기본"
    else:
        parsing_rules = template.parsing_rules
        template_name = template.name
        # 템플릿 사용 횟수 증가
        template.usage_count += 1
        db.commit()
        
        # 템플릿의 고정 주소/좌표 사용
        if not pickup_address and template.default_pickup_address:
            pickup_address = template.default_pickup_address
            logger.info(f"📍 템플릿 상차지 사용: {pickup_address}")
        
        if not delivery_address and template.default_delivery_address:
            delivery_address = template.default_delivery_address
            logger.info(f"📍 템플릿 하차지 사용: {delivery_address}")
    
    orders = []
    today = date.today()
    current_year = today.year
    order_number_prefix = f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # 2. 날짜 추출
    date_match = re.search(r'(\d{1,2})[/\-.](\d{1,2})', text)
    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        
        if 1 <= month <= 12 and 1 <= day <= 31:
            try:
                order_date = date(current_year, month, day)
                if order_date < today:
                    order_date = date(current_year + 1, month, day)
                    logger.info(f"📅 날짜가 과거이므로 다음 해로 설정: {order_date.isoformat()}")
                else:
                    logger.info(f"📅 날짜 파싱 성공: {order_date.isoformat()}")
            except ValueError as e:
                logger.warning(f"⚠️ 날짜 생성 실패: {e}")
                order_date = today
        else:
            logger.warning(f"⚠️ 유효하지 않은 날짜: {month}/{day}")
            order_date = today
    else:
        logger.warning(f"⚠️ 날짜를 찾을 수 없음")
        order_date = today
    
    logger.info(f"📅 최종 주문 날짜: {order_date.isoformat()}")
    
    # 3. 고객사명 추출
    client_match = re.search(r'[)\]]([가-힣]+)\s*(?:오전|오후)?배차', text)
    client_name = client_match.group(1) if client_match else template_name
    
    # 4. 각 배차 라인 파싱 (템플릿 규칙 사용)
    lines = text.split('\n')
    order_count = 0
    
    # 파싱 규칙 추출
    time_pattern = parsing_rules.get('time_pattern', r'(\d{1,2}):(\d{2})')
    product_pattern = parsing_rules.get('product_pattern', r'[가-힣]+')
    tonnage_pattern = parsing_rules.get('tonnage_pattern', r'(\d+(?:\.\d+)?)톤')
    temperature_keywords = parsing_rules.get('temperature_keywords', {})
    default_temperature = parsing_rules.get('default_temperature', 'REFRIGERATED')
    pallet_calc = parsing_rules.get('pallet_calculation', {})
    delivery_offset = parsing_rules.get('delivery_time_offset_hours', 4)
    notes_template = parsing_rules.get('notes_template', '자동 파싱: {client_name} 배차')
    
    for line in lines:
        # 시간 / 품목톤수(온도) 형식 파싱
        # time_pattern이 이미 캡처 그룹을 포함하고 있으므로 그대로 사용
        full_pattern = rf'({time_pattern})\s*/\s*({product_pattern}){tonnage_pattern}(?:\(([^)]+)\))?'
        match = re.search(full_pattern, line)
        
        if match:
            # match.group(1)은 전체 시간 문자열 (예: "13:00")
            time_str = match.group(1)
            time_match = re.match(r'(\d{1,2}):(\d{2})', time_str)
            if not time_match:
                logger.warning(f"⚠️ 시간 파싱 실패: {time_str}")
                continue
            
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            product_name = match.group(2)
            tonnage = float(match.group(3))
            temp_indicator = match.group(4) if len(match.groups()) >= 4 else None
            
            # 시간
            pickup_time = datetime_time(hour, minute)
            
            # 하차 시간 = 상차 시간 + offset (템플릿 설정)
            pickup_datetime = datetime.combine(order_date, pickup_time)
            delivery_datetime = pickup_datetime + timedelta(hours=delivery_offset)
            
            # 하차 날짜와 시간 분리
            delivery_date = delivery_datetime.date()
            delivery_time_start = delivery_datetime.time()
            delivery_time_end = (delivery_datetime + timedelta(hours=2)).time()
            
            # 온도대 결정 (템플릿 규칙 사용)
            temperature_zone_str = default_temperature
            if temp_indicator:
                for keyword, temp_enum in temperature_keywords.items():
                    if keyword in temp_indicator:
                        temperature_zone_str = temp_enum
                        break
            
            # TemperatureZone enum 변환
            try:
                temperature_zone = TemperatureZone[temperature_zone_str]
            except (KeyError, AttributeError):
                temperature_zone = TemperatureZone.REFRIGERATED
            
            # 팔레트 수 계산 (템플릿 규칙 사용)
            pallet_count = None
            # 정확한 톤수 매칭 먼저 시도
            for ton_str, pallets in pallet_calc.items():
                if ton_str == "default_multiplier":
                    continue
                try:
                    ton_threshold = float(ton_str)
                    if tonnage >= ton_threshold:
                        pallet_count = pallets
                        break
                except (ValueError, TypeError):
                    continue
            
            # 매칭 안 되면 default_multiplier 사용
            if pallet_count is None:
                multiplier = pallet_calc.get('default_multiplier', 2)
                pallet_count = max(1, int(tonnage * multiplier))
            
            # 중량 (톤 → kg)
            weight_kg = tonnage * 1000
            
            order_count += 1
            order_number = f"{order_number_prefix}-{order_count:03d}"
            
            # 노트 생성 (템플릿 사용)
            notes = notes_template.format(
                client_name=client_name,
                product_name=product_name,
                temperature=temperature_zone.value
            )
            
            order = {
                'order_number': order_number,
                'order_date': order_date.isoformat(),
                'delivery_date': delivery_date.isoformat(),
                'temperature_zone': temperature_zone.value,
                'pickup_address': pickup_address or f"{client_name} 본사",
                'delivery_address': delivery_address,
                'pallet_count': pallet_count,
                'weight_kg': weight_kg,
                'product_name': f"{product_name} {int(tonnage)}톤",
                'pickup_start_time': pickup_time.isoformat(),
                'pickup_end_time': datetime_time(min(hour + 1, 23), minute).isoformat(),
                'delivery_start_time': delivery_time_start.isoformat(),
                'delivery_end_time': delivery_time_end.isoformat(),
                'requested_delivery_date': delivery_date.isoformat(),
                'priority': 5,
                'requires_forklift': True,
                'is_stackable': True,
                'notes': notes
            }
            
            orders.append(order)
            logger.info(f"✅ 배차 {order_count}: {pickup_time.strftime('%H:%M')} - {product_name} {tonnage}톤 ({temperature_zone.value})")
    
    logger.info(f"✅ 총 {len(orders)}건의 배차 파싱 완료 (템플릿: {template_name})")
    
    return {
        'success': True,
        'orders': orders,
        'count': len(orders),
        'client_name': client_name,
        'order_date': order_date.isoformat(),
        'template_used': template_name
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


@router.post("/geocode-missing")
async def geocode_missing_coordinates(db: Session = Depends(get_db)):
    """
    좌표가 없는 주문들의 주소를 좌표로 일괄 변환
    
    Returns:
        {
            "success": true,
            "total_orders": 100,
            "geocoded_pickup": 50,
            "geocoded_delivery": 45,
            "failed_pickup": 5,
            "failed_delivery": 10
        }
    """
    from app.services.naver_map_service import NaverMapService
    
    naver_service = NaverMapService()
    
    # 픽업 좌표가 없는 주문들
    orders_without_pickup = db.query(Order).filter(
        (Order.pickup_latitude.is_(None)) | (Order.pickup_longitude.is_(None)),
        Order.pickup_address.isnot(None)
    ).all()
    
    # 배송 좌표가 없는 주문들
    orders_without_delivery = db.query(Order).filter(
        (Order.delivery_latitude.is_(None)) | (Order.delivery_longitude.is_(None)),
        Order.delivery_address.isnot(None)
    ).all()
    
    geocoded_pickup = 0
    failed_pickup = 0
    geocoded_delivery = 0
    failed_delivery = 0
    
    # 픽업 좌표 변환
    logger.info(f"📍 픽업 좌표 변환 시작: {len(orders_without_pickup)}건")
    for order in orders_without_pickup:
        try:
            full_address = f"{order.pickup_address} {order.pickup_address_detail or ''}".strip()
            result = await naver_service.geocode_address(full_address)
            
            if result and len(result) >= 2:
                latitude, longitude = result[0], result[1]
                if latitude and longitude:
                    order.pickup_latitude = latitude
                    order.pickup_longitude = longitude
                    geocoded_pickup += 1
                    logger.info(f"✅ 주문 {order.order_number} 픽업 좌표: {full_address} -> ({latitude}, {longitude})")
                else:
                    failed_pickup += 1
                    logger.warning(f"❌ 주문 {order.order_number} 픽업 좌표 변환 실패: {full_address}")
            else:
                failed_pickup += 1
                logger.warning(f"❌ 주문 {order.order_number} 픽업 좌표 없음: {full_address}")
        except Exception as e:
            failed_pickup += 1
            logger.error(f"❌ 주문 {order.order_number} 픽업 좌표 변환 오류: {e}")
    
    # 배송 좌표 변환
    logger.info(f"📍 배송 좌표 변환 시작: {len(orders_without_delivery)}건")
    for order in orders_without_delivery:
        try:
            full_address = f"{order.delivery_address} {order.delivery_address_detail or ''}".strip()
            result = await naver_service.geocode_address(full_address)
            
            if result and len(result) >= 2:
                latitude, longitude = result[0], result[1]
                if latitude and longitude:
                    order.delivery_latitude = latitude
                    order.delivery_longitude = longitude
                    geocoded_delivery += 1
                    logger.info(f"✅ 주문 {order.order_number} 배송 좌표: {full_address} -> ({latitude}, {longitude})")
                else:
                    failed_delivery += 1
                    logger.warning(f"❌ 주문 {order.order_number} 배송 좌표 변환 실패: {full_address}")
            else:
                failed_delivery += 1
                logger.warning(f"❌ 주문 {order.order_number} 배송 좌표 없음: {full_address}")
        except Exception as e:
            failed_delivery += 1
            logger.error(f"❌ 주문 {order.order_number} 배송 좌표 변환 오류: {e}")
    
    # 변경사항 저장
    db.commit()
    
    total_orders = len(set([o.id for o in orders_without_pickup] + [o.id for o in orders_without_delivery]))
    
    logger.info(f"✅ 좌표 일괄 변환 완료: 총 {total_orders}건, 픽업 {geocoded_pickup}건, 배송 {geocoded_delivery}건")
    
    return {
        "success": True,
        "total_orders": total_orders,
        "geocoded_pickup": geocoded_pickup,
        "geocoded_delivery": geocoded_delivery,
        "failed_pickup": failed_pickup,
        "failed_delivery": failed_delivery
    }
