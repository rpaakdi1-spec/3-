"""
Recurring Orders API
정기 주문 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from loguru import logger

from app.core.database import get_db
from app.models.recurring_order import RecurringOrder
from app.schemas.recurring_order import (
    RecurringOrderCreate,
    RecurringOrderUpdate,
    RecurringOrderResponse,
    RecurringOrderListResponse
)

router = APIRouter(prefix="/recurring-orders", tags=["Recurring Orders"])


@router.get("/", response_model=RecurringOrderListResponse)
def get_recurring_orders(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """정기 주문 목록 조회"""
    query = db.query(RecurringOrder)
    
    # 필터링
    if is_active is not None:
        query = query.filter(RecurringOrder.is_active == is_active)
    
    # 총 개수
    total = query.count()
    
    # 페이지네이션
    recurring_orders = query.order_by(RecurringOrder.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": recurring_orders
    }


@router.get("/{recurring_order_id}", response_model=RecurringOrderResponse)
def get_recurring_order(
    recurring_order_id: int,
    db: Session = Depends(get_db)
):
    """정기 주문 상세 조회"""
    recurring_order = db.query(RecurringOrder).filter(RecurringOrder.id == recurring_order_id).first()
    if not recurring_order:
        raise HTTPException(status_code=404, detail="정기 주문을 찾을 수 없습니다")
    
    return recurring_order


@router.post("/", response_model=RecurringOrderResponse, status_code=status.HTTP_201_CREATED)
def create_recurring_order(
    recurring_order_data: RecurringOrderCreate,
    db: Session = Depends(get_db)
):
    """정기 주문 생성"""
    try:
        # 거래처 ID 또는 주소 검증
        if not recurring_order_data.pickup_client_id and not recurring_order_data.pickup_address:
            raise HTTPException(status_code=400, detail="상차 거래처 ID 또는 주소를 입력해주세요")
        
        if not recurring_order_data.delivery_client_id and not recurring_order_data.delivery_address:
            raise HTTPException(status_code=400, detail="하차 거래처 ID 또는 주소를 입력해주세요")
        
        # 종료일 검증
        if recurring_order_data.end_date and recurring_order_data.end_date < recurring_order_data.start_date:
            raise HTTPException(status_code=400, detail="종료일은 시작일 이후여야 합니다")
        
        # 정기 주문 생성
        recurring_order = RecurringOrder(**recurring_order_data.model_dump())
        db.add(recurring_order)
        db.commit()
        db.refresh(recurring_order)
        
        logger.info(f"Created recurring order: {recurring_order.name} (ID: {recurring_order.id})")
        return recurring_order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating recurring order: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="정기 주문 생성 중 오류가 발생했습니다")


@router.put("/{recurring_order_id}", response_model=RecurringOrderResponse)
def update_recurring_order(
    recurring_order_id: int,
    recurring_order_data: RecurringOrderUpdate,
    db: Session = Depends(get_db)
):
    """정기 주문 수정"""
    recurring_order = db.query(RecurringOrder).filter(RecurringOrder.id == recurring_order_id).first()
    if not recurring_order:
        raise HTTPException(status_code=404, detail="정기 주문을 찾을 수 없습니다")
    
    try:
        # 업데이트 데이터
        update_data = recurring_order_data.model_dump(exclude_unset=True)
        
        # 종료일 검증
        new_end_date = update_data.get('end_date')
        new_start_date = update_data.get('start_date', recurring_order.start_date)
        if new_end_date and new_end_date < new_start_date:
            raise HTTPException(status_code=400, detail="종료일은 시작일 이후여야 합니다")
        
        # 필드 업데이트
        for field, value in update_data.items():
            setattr(recurring_order, field, value)
        
        db.commit()
        db.refresh(recurring_order)
        
        logger.info(f"Updated recurring order: {recurring_order.name} (ID: {recurring_order.id})")
        return recurring_order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating recurring order: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="정기 주문 수정 중 오류가 발생했습니다")


@router.delete("/{recurring_order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring_order(
    recurring_order_id: int,
    db: Session = Depends(get_db)
):
    """정기 주문 삭제"""
    recurring_order = db.query(RecurringOrder).filter(RecurringOrder.id == recurring_order_id).first()
    if not recurring_order:
        raise HTTPException(status_code=404, detail="정기 주문을 찾을 수 없습니다")
    
    try:
        db.delete(recurring_order)
        db.commit()
        
        logger.info(f"Deleted recurring order: {recurring_order.name} (ID: {recurring_order.id})")
        
    except Exception as e:
        logger.error(f"Error deleting recurring order: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="정기 주문 삭제 중 오류가 발생했습니다")


@router.post("/{recurring_order_id}/toggle", response_model=RecurringOrderResponse)
def toggle_recurring_order(
    recurring_order_id: int,
    db: Session = Depends(get_db)
):
    """정기 주문 활성화/비활성화 토글"""
    recurring_order = db.query(RecurringOrder).filter(RecurringOrder.id == recurring_order_id).first()
    if not recurring_order:
        raise HTTPException(status_code=404, detail="정기 주문을 찾을 수 없습니다")
    
    try:
        recurring_order.is_active = not recurring_order.is_active
        db.commit()
        db.refresh(recurring_order)
        
        status_text = "활성화" if recurring_order.is_active else "비활성화"
        logger.info(f"{status_text} recurring order: {recurring_order.name} (ID: {recurring_order.id})")
        
        return recurring_order
        
    except Exception as e:
        logger.error(f"Error toggling recurring order: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="정기 주문 상태 변경 중 오류가 발생했습니다")
