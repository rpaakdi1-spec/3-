"""
Recurring Order Schemas
정기 주문 스키마
"""
from datetime import date, time
from typing import Optional
from pydantic import BaseModel, Field
from app.models.recurring_order import RecurringFrequency
from app.models.order import TemperatureZone


class RecurringOrderBase(BaseModel):
    """정기 주문 기본 스키마"""
    name: str = Field(..., max_length=200, description="정기 주문명")
    description: Optional[str] = Field(None, description="설명")
    
    # 반복 설정
    frequency: RecurringFrequency = Field(..., description="반복 주기")
    start_date: date = Field(..., description="시작일")
    end_date: Optional[date] = Field(None, description="종료일")
    weekdays: int = Field(0, ge=0, le=127, description="실행 요일 (비트 플래그)")
    day_of_month: Optional[int] = Field(None, ge=1, le=31, description="매월 특정일")
    
    # 주문 정보
    temperature_zone: TemperatureZone = Field(..., description="온도대")
    
    # 거래처
    pickup_client_id: Optional[int] = None
    delivery_client_id: Optional[int] = None
    pickup_address: Optional[str] = Field(None, max_length=500)
    pickup_address_detail: Optional[str] = Field(None, max_length=200)
    delivery_address: Optional[str] = Field(None, max_length=500)
    delivery_address_detail: Optional[str] = Field(None, max_length=200)
    
    # 물품 정보
    pallet_count: int = Field(..., gt=0, description="팔레트 수")
    weight_kg: Optional[int] = Field(0, ge=0)
    volume_cbm: Optional[int] = Field(0, ge=0)
    product_name: Optional[str] = Field(None, max_length=200)
    product_code: Optional[str] = Field(None, max_length=100)
    
    # 시간
    pickup_start_time: Optional[time] = None
    pickup_end_time: Optional[time] = None
    delivery_start_time: Optional[time] = None
    delivery_end_time: Optional[time] = None
    
    # 기타
    priority: int = Field(5, ge=1, le=10)
    requires_forklift: bool = False
    is_stackable: bool = True
    notes: Optional[str] = None


class RecurringOrderCreate(RecurringOrderBase):
    """정기 주문 생성 스키마"""
    pass


class RecurringOrderUpdate(BaseModel):
    """정기 주문 수정 스키마"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    
    frequency: Optional[RecurringFrequency] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    weekdays: Optional[int] = Field(None, ge=0, le=127)
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    
    temperature_zone: Optional[TemperatureZone] = None
    
    pickup_client_id: Optional[int] = None
    delivery_client_id: Optional[int] = None
    pickup_address: Optional[str] = Field(None, max_length=500)
    pickup_address_detail: Optional[str] = Field(None, max_length=200)
    delivery_address: Optional[str] = Field(None, max_length=500)
    delivery_address_detail: Optional[str] = Field(None, max_length=200)
    
    pallet_count: Optional[int] = Field(None, gt=0)
    weight_kg: Optional[int] = Field(None, ge=0)
    volume_cbm: Optional[int] = Field(None, ge=0)
    product_name: Optional[str] = Field(None, max_length=200)
    product_code: Optional[str] = Field(None, max_length=100)
    
    pickup_start_time: Optional[time] = None
    pickup_end_time: Optional[time] = None
    delivery_start_time: Optional[time] = None
    delivery_end_time: Optional[time] = None
    
    priority: Optional[int] = Field(None, ge=1, le=10)
    requires_forklift: Optional[bool] = None
    is_stackable: Optional[bool] = None
    notes: Optional[str] = None
    
    is_active: Optional[bool] = None


class RecurringOrderResponse(RecurringOrderBase):
    """정기 주문 응답 스키마"""
    id: int
    is_active: bool
    last_generated_date: Optional[date] = None
    created_at: date
    updated_at: date
    
    class Config:
        from_attributes = True


class RecurringOrderListResponse(BaseModel):
    """정기 주문 목록 응답"""
    total: int
    items: list[RecurringOrderResponse]
