from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.order import TemperatureZone, OrderStatus


class OrderBase(BaseModel):
    """Base schema for Order"""
    order_number: str = Field(..., max_length=50, description="주문번호")
    order_date: date = Field(..., description="주문일자")
    temperature_zone: TemperatureZone = Field(..., description="온도대 구분")
    
    pickup_client_id: int = Field(..., description="상차 거래처 ID")
    delivery_client_id: int = Field(..., description="하차 거래처 ID")
    
    pallet_count: int = Field(..., gt=0, description="팔레트 수")
    weight_kg: float = Field(..., gt=0, description="중량(kg)")
    volume_cbm: Optional[float] = Field(None, gt=0, description="용적(CBM)")
    
    product_name: Optional[str] = Field(None, max_length=200, description="품목명")
    product_code: Optional[str] = Field(None, max_length=100, description="품목코드")
    
    pickup_start_time: Optional[str] = Field(None, max_length=5, description="상차 시작시간(HH:MM)")
    pickup_end_time: Optional[str] = Field(None, max_length=5, description="상차 종료시간(HH:MM)")
    delivery_start_time: Optional[str] = Field(None, max_length=5, description="하차 시작시간(HH:MM)")
    delivery_end_time: Optional[str] = Field(None, max_length=5, description="하차 종료시간(HH:MM)")
    
    requested_delivery_date: Optional[date] = Field(None, description="희망 배송일")
    priority: int = Field(5, ge=1, le=10, description="우선순위(1:높음 ~ 10:낮음)")
    
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
    weight_kg: Optional[float] = Field(None, gt=0)
    volume_cbm: Optional[float] = Field(None, gt=0)
    product_name: Optional[str] = Field(None, max_length=200)
    product_code: Optional[str] = Field(None, max_length=100)
    status: Optional[OrderStatus] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
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
    
    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    """Schema for order list response"""
    total: int
    items: list[OrderResponse]


class OrderWithClientsResponse(OrderResponse):
    """Schema for order with full client details"""
    pickup_client: Optional[dict] = None
    delivery_client: Optional[dict] = None
