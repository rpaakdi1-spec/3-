from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.vehicle import VehicleType, VehicleStatus


class VehicleBase(BaseModel):
    """Base schema for Vehicle"""
    code: str = Field(..., max_length=50, description="차량코드")
    plate_number: str = Field(..., max_length=20, description="차량번호")
    vehicle_type: VehicleType = Field(..., description="온도대 구분")
    
    max_pallets: int = Field(..., gt=0, description="최대 팔레트 수")
    max_weight_kg: float = Field(..., gt=0, description="최대 적재중량(kg)")
    max_volume_cbm: Optional[float] = Field(None, gt=0, description="최대 용적(CBM)")
    
    tonnage: float = Field(..., gt=0, description="톤수")
    length_m: Optional[float] = Field(None, gt=0, description="적재함 길이(m)")
    width_m: Optional[float] = Field(None, gt=0, description="적재함 너비(m)")
    height_m: Optional[float] = Field(None, gt=0, description="적재함 높이(m)")
    
    min_temp_celsius: Optional[float] = Field(None, description="최저 온도(°C)")
    max_temp_celsius: Optional[float] = Field(None, description="최고 온도(°C)")
    
    fuel_efficiency_km_per_liter: Optional[float] = Field(None, gt=0, description="연비(km/L)")
    fuel_cost_per_liter: Optional[float] = Field(None, gt=0, description="리터당 연료비")
    
    garage_address: Optional[str] = Field(None, max_length=500, description="차고지 주소")
    garage_latitude: Optional[float] = Field(None, description="차고지 위도")
    garage_longitude: Optional[float] = Field(None, description="차고지 경도")
    
    notes: Optional[str] = Field(None, description="특이사항")


class VehicleCreate(VehicleBase):
    """Schema for creating a vehicle"""
    uvis_device_id: Optional[str] = Field(None, max_length=100, description="UVIS 단말기 ID")
    uvis_enabled: bool = Field(False, description="UVIS 연동 여부")


class VehicleUpdate(BaseModel):
    """Schema for updating a vehicle"""
    plate_number: Optional[str] = Field(None, max_length=20)
    vehicle_type: Optional[VehicleType] = None
    uvis_device_id: Optional[str] = Field(None, max_length=100)
    uvis_enabled: Optional[bool] = None
    max_pallets: Optional[int] = Field(None, gt=0)
    max_weight_kg: Optional[float] = Field(None, gt=0)
    max_volume_cbm: Optional[float] = Field(None, gt=0)
    tonnage: Optional[float] = Field(None, gt=0)
    status: Optional[VehicleStatus] = None
    garage_address: Optional[str] = Field(None, max_length=500)
    garage_latitude: Optional[float] = None
    garage_longitude: Optional[float] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class VehicleResponse(VehicleBase):
    """Schema for vehicle response"""
    id: int
    uvis_device_id: Optional[str] = None
    uvis_enabled: bool
    status: VehicleStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class VehicleListResponse(BaseModel):
    """Schema for vehicle list response"""
    total: int
    items: list[VehicleResponse]
