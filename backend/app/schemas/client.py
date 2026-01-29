from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.client import ClientType


class ClientBase(BaseModel):
    """Base schema for Client"""
    code: str = Field(..., max_length=50, description="거래처 코드")
    name: str = Field(..., max_length=200, description="거래처명")
    client_type: ClientType = Field(..., description="상차/하차 구분")
    address: str = Field(..., max_length=500, description="기본 주소")
    address_detail: Optional[str] = Field(None, max_length=200, description="상세 주소")
    
    pickup_start_time: Optional[str] = Field(None, max_length=5, description="상차가능시작시간")
    pickup_end_time: Optional[str] = Field(None, max_length=5, description="상차가능종료시간")
    delivery_start_time: Optional[str] = Field(None, max_length=5, description="하차가능시작시간")
    delivery_end_time: Optional[str] = Field(None, max_length=5, description="하차가능종료시간")
    
    forklift_operator_available: bool = Field(False, description="지게차 운전능력 가능 여부")
    loading_time_minutes: int = Field(30, description="평균 상하차 소요시간(분)")
    
    contact_person: Optional[str] = Field(None, max_length=100, description="담당자명")
    phone: Optional[str] = Field(None, max_length=20, description="전화번호")
    notes: Optional[str] = Field(None, description="특이사항")


class ClientCreate(ClientBase):
    """Schema for creating a client"""
    latitude: Optional[float] = Field(None, description="위도")
    longitude: Optional[float] = Field(None, description="경도")


class ClientUpdate(BaseModel):
    """Schema for updating a client"""
    name: Optional[str] = Field(None, max_length=200)
    client_type: Optional[ClientType] = None
    address: Optional[str] = Field(None, max_length=500)
    address_detail: Optional[str] = Field(None, max_length=200)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    pickup_start_time: Optional[str] = Field(None, max_length=5)
    pickup_end_time: Optional[str] = Field(None, max_length=5)
    delivery_start_time: Optional[str] = Field(None, max_length=5)
    delivery_end_time: Optional[str] = Field(None, max_length=5)
    forklift_operator_available: Optional[bool] = None
    loading_time_minutes: Optional[int] = None
    contact_person: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ClientResponse(ClientBase):
    """Schema for client response"""
    id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    geocoded: bool
    geocode_error: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ClientListResponse(BaseModel):
    """Schema for client list response"""
    total: int
    items: list[ClientResponse]


class GeocodeRequest(BaseModel):
    """Schema for geocoding request"""
    client_ids: list[int] = Field(..., description="Client IDs to geocode")


class GeocodeResponse(BaseModel):
    """Schema for geocoding response"""
    success_count: int
    failed_count: int
    results: list[dict]
    message: Optional[str] = None
