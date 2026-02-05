"""
Order Template API
주문 템플릿 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from loguru import logger

from app.core.database import get_db
from app.models.order_template import OrderTemplate
from app.models.order import Order
from app.schemas.order_template import (
    OrderTemplateCreate,
    OrderTemplateUpdate,
    OrderTemplateResponse,
    OrderTemplateListResponse,
)
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter()


@router.get("/", response_model=OrderTemplateListResponse)
def get_order_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    is_shared: Optional[bool] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """주문 템플릿 목록 조회"""
    query = db.query(OrderTemplate)
    
    if category:
        query = query.filter(OrderTemplate.category == category)
    if is_shared is not None:
        query = query.filter(OrderTemplate.is_shared == is_shared)
    if is_active is not None:
        query = query.filter(OrderTemplate.is_active == is_active)
    
    total = query.count()
    items = query.order_by(OrderTemplate.usage_count.desc()).offset(skip).limit(limit).all()
    
    return {"total": total, "items": items}


@router.get("/{template_id}", response_model=OrderTemplateResponse)
def get_order_template(template_id: int, db: Session = Depends(get_db)):
    """주문 템플릿 단일 조회"""
    template = db.query(OrderTemplate).filter(OrderTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")
    
    return template


@router.post("/", response_model=OrderTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_order_template(
    template_data: OrderTemplateCreate,
    db: Session = Depends(get_db)
):
    """주문 템플릿 생성"""
    try:
        # 검증: pickup_client_id 또는 pickup_address 필수
        if not template_data.pickup_client_id and not template_data.pickup_address:
            raise HTTPException(
                status_code=400,
                detail="상차 거래처 ID 또는 주소를 입력해주세요"
            )
        
        # 검증: delivery_client_id 또는 delivery_address 필수
        if not template_data.delivery_client_id and not template_data.delivery_address:
            raise HTTPException(
                status_code=400,
                detail="하차 거래처 ID 또는 주소를 입력해주세요"
            )
        
        template = OrderTemplate(**template_data.model_dump())
        db.add(template)
        db.commit()
        db.refresh(template)
        
        logger.info(f"Created order template: {template.name} (ID: {template.id})")
        
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order template: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="템플릿 생성 중 오류가 발생했습니다")


@router.put("/{template_id}", response_model=OrderTemplateResponse)
def update_order_template(
    template_id: int,
    template_data: OrderTemplateUpdate,
    db: Session = Depends(get_db)
):
    """주문 템플릿 수정"""
    template = db.query(OrderTemplate).filter(OrderTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")
    
    try:
        update_data = template_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(template, field, value)
        
        db.commit()
        db.refresh(template)
        
        logger.info(f"Updated order template: {template.name} (ID: {template.id})")
        
        return template
        
    except Exception as e:
        logger.error(f"Error updating order template: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="템플릿 수정 중 오류가 발생했습니다")


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_template(template_id: int, db: Session = Depends(get_db)):
    """주문 템플릿 삭제"""
    template = db.query(OrderTemplate).filter(OrderTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")
    
    try:
        db.delete(template)
        db.commit()
        
        logger.info(f"Deleted order template: {template.name} (ID: {template.id})")
        
    except Exception as e:
        logger.error(f"Error deleting order template: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="템플릿 삭제 중 오류가 발생했습니다")


@router.post("/{template_id}/use", response_model=OrderResponse)
def use_order_template(
    template_id: int,
    order_number: str,
    order_date: str,
    db: Session = Depends(get_db)
):
    """템플릿으로 주문 생성
    
    템플릿을 기반으로 실제 주문을 생성합니다.
    order_number와 order_date는 필수입니다.
    """
    template = db.query(OrderTemplate).filter(OrderTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")
    
    try:
        # 템플릿 데이터를 Order 생성 데이터로 변환
        order_data = template.to_order_data()
        order_data["order_number"] = order_number
        order_data["order_date"] = order_date
        
        # 주문 생성
        order = Order(**order_data)
        db.add(order)
        
        # 템플릿 사용 횟수 증가
        template.usage_count += 1
        template.last_used_at = datetime.utcnow()
        
        db.commit()
        db.refresh(order)
        
        logger.info(
            f"Created order from template: {order.order_number} "
            f"(Template: {template.name}, ID: {template.id})"
        )
        
        return order
        
    except Exception as e:
        logger.error(f"Error creating order from template: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="템플릿으로 주문 생성 중 오류가 발생했습니다")


@router.get("/categories/list")
def get_template_categories(db: Session = Depends(get_db)):
    """템플릿 카테고리 목록 조회"""
    categories = (
        db.query(OrderTemplate.category)
        .filter(OrderTemplate.category.isnot(None))
        .filter(OrderTemplate.is_active == True)
        .distinct()
        .all()
    )
    
    return {"categories": [cat[0] for cat in categories if cat[0]]}


@router.post("/{template_id}/duplicate", response_model=OrderTemplateResponse)
def duplicate_order_template(template_id: int, db: Session = Depends(get_db)):
    """템플릿 복제"""
    original = db.query(OrderTemplate).filter(OrderTemplate.id == template_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")
    
    try:
        # 복제
        duplicate_data = {
            "name": f"{original.name} (복사본)",
            "description": original.description,
            "category": original.category,
            "temperature_zone": original.temperature_zone,
            "pickup_client_id": original.pickup_client_id,
            "pickup_address": original.pickup_address,
            "pickup_address_detail": original.pickup_address_detail,
            "delivery_client_id": original.delivery_client_id,
            "delivery_address": original.delivery_address,
            "delivery_address_detail": original.delivery_address_detail,
            "pallet_count": original.pallet_count,
            "weight_kg": original.weight_kg,
            "volume_cbm": original.volume_cbm,
            "product_name": original.product_name,
            "product_code": original.product_code,
            "pickup_start_time": original.pickup_start_time,
            "pickup_end_time": original.pickup_end_time,
            "delivery_start_time": original.delivery_start_time,
            "delivery_end_time": original.delivery_end_time,
            "requires_forklift": original.requires_forklift,
            "is_stackable": original.is_stackable,
            "priority": original.priority,
            "notes": original.notes,
            "is_shared": False,  # 복사본은 기본적으로 개인용
            "created_by": original.created_by,
        }
        
        duplicate = OrderTemplate(**duplicate_data)
        db.add(duplicate)
        db.commit()
        db.refresh(duplicate)
        
        logger.info(f"Duplicated order template: {duplicate.name} (ID: {duplicate.id})")
        
        return duplicate
        
    except Exception as e:
        logger.error(f"Error duplicating order template: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="템플릿 복제 중 오류가 발생했습니다")
