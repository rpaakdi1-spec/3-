"""
Order Template Schemas
주문 템플릿 Pydantic 스키마
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OrderTemplateBase(BaseModel):
    """주문 템플릿 기본 스키마"""
    name: str = Field(..., max_length=100, description="템플릿 이름")
    description: Optional[str] = Field(None, description="템플릿 설명")
    category: Optional[str] = Field(None, max_length=50, description="카테고리")
    
    temperature_zone: str = Field(..., description="온도대")
    
    pickup_client_id: Optional[int] = Field(None, description="상차 거래처 ID")
    pickup_address: Optional[str] = Field(None, max_length=500, description="상차 주소")
    pickup_address_detail: Optional[str] = Field(None, max_length=200, description="상차 상세주소")
    
    delivery_client_id: Optional[int] = Field(None, description="하차 거래처 ID")
    delivery_address: Optional[str] = Field(None, max_length=500, description="하차 주소")
    delivery_address_detail: Optional[str] = Field(None, max_length=200, description="하차 상세주소")
    
    pallet_count: int = Field(..., gt=0, description="팔레트 수")
    weight_kg: Optional[float] = Field(0, ge=0, description="중량(kg)")
    volume_cbm: Optional[float] = Field(0, ge=0, description="용적(CBM)")
    
    product_name: Optional[str] = Field(None, max_length=200, description="품목명")
    product_code: Optional[str] = Field(None, max_length=100, description="품목코드")
    
    pickup_start_time: Optional[str] = Field(None, description="상차 시작 시간")
    pickup_end_time: Optional[str] = Field(None, description="상차 종료 시간")
    delivery_start_time: Optional[str] = Field(None, description="하차 시작 시간")
    delivery_end_time: Optional[str] = Field(None, description="하차 종료 시간")
    
    requires_forklift: bool = Field(False, description="지게차 필요 여부")
    is_stackable: bool = Field(True, description="적재 가능 여부")
    priority: int = Field(5, ge=1, le=10, description="우선순위")
    notes: Optional[str] = Field(None, description="비고")
    
    is_shared: bool = Field(False, description="공유 여부")


class OrderTemplateCreate(OrderTemplateBase):
    """주문 템플릿 생성"""
    pass


class OrderTemplateUpdate(BaseModel):
    """주문 템플릿 수정"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    
    temperature_zone: Optional[str] = None
    
    pickup_client_id: Optional[int] = None
    pickup_address: Optional[str] = Field(None, max_length=500)
    pickup_address_detail: Optional[str] = Field(None, max_length=200)
    
    delivery_client_id: Optional[int] = None
    delivery_address: Optional[str] = Field(None, max_length=500)
    delivery_address_detail: Optional[str] = Field(None, max_length=200)
    
    pallet_count: Optional[int] = Field(None, gt=0)
    weight_kg: Optional[float] = Field(None, ge=0)
    volume_cbm: Optional[float] = Field(None, ge=0)
    
    product_name: Optional[str] = Field(None, max_length=200)
    product_code: Optional[str] = Field(None, max_length=100)
    
    pickup_start_time: Optional[str] = None
    pickup_end_time: Optional[str] = None
    delivery_start_time: Optional[str] = None
    delivery_end_time: Optional[str] = None
    
    requires_forklift: Optional[bool] = None
    is_stackable: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    
    is_shared: Optional[bool] = None
    is_active: Optional[bool] = None


class OrderTemplateResponse(OrderTemplateBase):
    """주문 템플릿 응답"""
    id: int
    usage_count: int
    last_used_at: Optional[datetime]
    created_by: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class OrderTemplateListResponse(BaseModel):
    """주문 템플릿 목록 응답"""
    total: int
    items: list[OrderTemplateResponse]
