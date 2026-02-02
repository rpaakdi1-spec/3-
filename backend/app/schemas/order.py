from __future__ import annotations
from datetime import datetime, date, time
from typing import Optional, Union
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from app.models.order import TemperatureZone, OrderStatus


class OrderBase(BaseModel):
    """Base schema for Order"""
    order_number: str = Field(..., max_length=50, description="주문번호")
    order_date: date = Field(..., description="주문일자")
    temperature_zone: TemperatureZone = Field(..., description="온도대 구분")
    
    # 거래처 선택 방식 1: 거래처 ID로 선택
    pickup_client_id: Optional[int] = Field(None, description="상차 거래처 ID")
    delivery_client_id: Optional[int] = Field(None, description="하차 거래처 ID")
    
    # 거래처 선택 방식 2: 주소로 직접 입력
    pickup_address: Optional[str] = Field(None, max_length=500, description="상차 주소")
    pickup_address_detail: Optional[str] = Field(None, max_length=200, description="상차 상세주소")
    delivery_address: Optional[str] = Field(None, max_length=500, description="하차 주소")
    delivery_address_detail: Optional[str] = Field(None, max_length=200, description="하차 상세주소")
    
    pallet_count: int = Field(..., gt=0, description="팔레트 수")
    weight_kg: Optional[float] = Field(None, ge=0, description="중량(kg)")  # Allow 0 for backward compatibility
    volume_cbm: Optional[float] = Field(None, ge=0, description="용적(CBM)")  # Allow 0 for backward compatibility
    
    product_name: Optional[str] = Field(None, max_length=200, description="품목명")
    product_code: Optional[str] = Field(None, max_length=100, description="품목코드")
    
    # Time fields accept both string (HH:MM) and time objects from database
    pickup_start_time: Optional[Union[str, time]] = Field(None, description="상차 시작시간(HH:MM)")
    pickup_end_time: Optional[Union[str, time]] = Field(None, description="상차 종료시간(HH:MM)")
    delivery_start_time: Optional[Union[str, time]] = Field(None, description="하차 시작시간(HH:MM)")
    delivery_end_time: Optional[Union[str, time]] = Field(None, description="하차 종료시간(HH:MM)")
    
    requested_delivery_date: Optional[date] = Field(None, description="희망 배송일")
    priority: int = Field(5, ge=1, le=10, description="우선순위(1:높음 ~ 10:낮음)")
    
    # 예약 관련
    is_reserved: bool = Field(False, description="예약 오더 여부")
    reserved_at: Optional[date] = Field(None, description="예약 생성일")
    confirmed_at: Optional[date] = Field(None, description="오더 확정일")
    
    # 반복 오더 설정
    recurring_type: Optional[str] = Field(None, max_length=20, description="반복 유형 (DAILY, WEEKLY, MONTHLY)")
    recurring_end_date: Optional[date] = Field(None, description="반복 종료일")
    
    requires_forklift: bool = Field(False, description="지게차 필요 여부")
    is_stackable: bool = Field(True, description="적재 가능 여부")
    
    notes: Optional[str] = Field(None, description="특이사항")


class OrderCreate(OrderBase):
    """Schema for creating an order"""
    pass


class OrderUpdate(BaseModel):
    """Schema for updating an order"""
    order_date: Optional[date] = None
    temperature_zone: Optional[TemperatureZone] = None
    pickup_client_id: Optional[int] = None
    delivery_client_id: Optional[int] = None
    pallet_count: Optional[int] = Field(None, gt=0)
    weight_kg: Optional[float] = Field(None, ge=0)
    volume_cbm: Optional[float] = Field(None, ge=0)
    product_name: Optional[str] = Field(None, max_length=200)
    product_code: Optional[str] = Field(None, max_length=100)
    requested_delivery_date: Optional[date] = None
    status: Optional[OrderStatus] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    is_reserved: Optional[bool] = None
    reserved_at: Optional[date] = None
    confirmed_at: Optional[date] = None
    recurring_type: Optional[str] = Field(None, max_length=20)
    recurring_end_date: Optional[date] = None
    notes: Optional[str] = None


class OrderResponse(OrderBase):
    """Schema for order response"""
    id: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    
    # Include client info
    pickup_client_name: Optional[str] = None
    delivery_client_name: Optional[str] = None
    
    # Include address info (for orders created with address)
    pickup_latitude: Optional[float] = None
    pickup_longitude: Optional[float] = None
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_serializer('status')
    def serialize_status(self, value: OrderStatus, _info) -> str:
        """Serialize OrderStatus enum as name (PENDING) instead of value (배차대기)"""
        return value.name if isinstance(value, OrderStatus) else value
    
    @field_serializer('pickup_start_time', 'pickup_end_time', 'delivery_start_time', 'delivery_end_time')
    def serialize_time(self, value: Optional[time], _info) -> Optional[str]:
        """Convert time objects to HH:MM string format (handles both time objects and strings)"""
        if value is None:
            return None
        if isinstance(value, time):
            return value.strftime('%H:%M')
        if isinstance(value, str):
            # Already a string, return as is
            return value
        # Fallback for any other type
        return str(value) if value is not None else None


class OrderListResponse(BaseModel):
    """Schema for order list response"""
    total: int
    items: list[OrderResponse]


class OrderWithClientsResponse(OrderResponse):
    """Schema for order with full client details"""
    pickup_client: Optional[dict] = None
    delivery_client: Optional[dict] = None
