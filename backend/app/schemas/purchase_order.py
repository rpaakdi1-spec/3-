from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional

class PurchaseOrderBase(BaseModel):
    """발주서 기본 스키마"""
    po_number: str = Field(..., max_length=50, description="발주서 번호")
    title: str = Field(..., max_length=200, description="발주서 제목")
    supplier: str = Field(..., max_length=200, description="공급업체")
    order_date: date = Field(..., description="발주일")
    delivery_date: Optional[date] = Field(None, description="희망 납기일")
    total_amount: float = Field(default=0.0, description="총 금액")
    status: str = Field(default="작성중", description="상태: 작성중, 발송완료, 승인, 취소")
    content: Optional[str] = Field(None, description="발주 내용 및 특이사항")
    image_url: Optional[str] = Field(None, max_length=500, description="첨부 이미지 URL")
    author: str = Field(..., max_length=100, description="작성자")

class PurchaseOrderCreate(PurchaseOrderBase):
    """발주서 생성 스키마"""
    pass

class PurchaseOrderUpdate(BaseModel):
    """발주서 수정 스키마"""
    po_number: Optional[str] = Field(None, max_length=50, description="발주서 번호")
    title: Optional[str] = Field(None, max_length=200, description="발주서 제목")
    supplier: Optional[str] = Field(None, max_length=200, description="공급업체")
    order_date: Optional[date] = Field(None, description="발주일")
    delivery_date: Optional[date] = Field(None, description="희망 납기일")
    total_amount: Optional[float] = Field(None, description="총 금액")
    status: Optional[str] = Field(None, description="상태")
    content: Optional[str] = Field(None, description="발주 내용 및 특이사항")
    image_url: Optional[str] = Field(None, max_length=500, description="첨부 이미지 URL")
    author: Optional[str] = Field(None, max_length=100, description="작성자")
    is_active: Optional[bool] = Field(None, description="활성화 여부")

class PurchaseOrderResponse(PurchaseOrderBase):
    """발주서 응답 스키마"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

class PurchaseOrderListResponse(BaseModel):
    """발주서 목록 응답 스키마"""
    total: int
    items: list[PurchaseOrderResponse]
