from __future__ import annotations
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
    
    forklift_operator_available: bool = Field(False, description="지게차 운전능력 가능 여부")
    
    tonnage: float = Field(..., gt=0, description="톤수")
    length_m: Optional[float] = Field(None, gt=0, description="적재함 길이(m)")
    width_m: Optional[float] = Field(None, gt=0, description="적재함 너비(m)")
    height_m: Optional[float] = Field(None, gt=0, description="적재함 높이(m)")
    
    driver_name: Optional[str] = Field(None, max_length=100, description="운전자명")
    driver_phone: Optional[str] = Field(None, max_length=20, description="운전자 연락처")
    
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
    forklift_operator_available: Optional[bool] = None
    tonnage: Optional[float] = Field(None, gt=0)
    driver_name: Optional[str] = Field(None, max_length=100)
    driver_phone: Optional[str] = Field(None, max_length=20)
    status: Optional[VehicleStatus] = None
    garage_address: Optional[str] = Field(None, max_length=500)
    garage_latitude: Optional[float] = None
    garage_longitude: Optional[float] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class VehicleGPSData(BaseModel):
    """Real-time GPS data from UVIS"""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    current_address: Optional[str] = Field(None, description="현재 위치 주소 (역지오코딩)")
    is_engine_on: Optional[bool] = None
    speed_kmh: Optional[int] = None
    temperature_a: Optional[float] = None
    temperature_b: Optional[float] = None
    battery_voltage: Optional[float] = None
    last_updated: Optional[datetime] = None
    gps_datetime: Optional[str] = None


class VehicleResponse(VehicleBase):
    """Schema for vehicle response"""
    id: int
    uvis_device_id: Optional[str] = None
    uvis_enabled: bool
    status: VehicleStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime
    gps_data: Optional[VehicleGPSData] = Field(None, description="Real-time GPS data (when include_gps=true)")
    
    model_config = ConfigDict(from_attributes=True)


class VehicleListResponse(BaseModel):
    """Schema for vehicle list response"""
    total: int
    items: list[VehicleResponse]


class VehicleGPSData(BaseModel):
    """Real-time GPS data from UVIS"""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    current_address: Optional[str] = Field(None, description="현재 위치 주소 (역지오코딩)")
    is_engine_on: Optional[bool] = None
    speed_kmh: Optional[int] = None
    temperature_a: Optional[float] = None
    temperature_b: Optional[float] = None
    battery_voltage: Optional[float] = None
    last_updated: Optional[datetime] = None
    gps_datetime: Optional[str] = None


class VehicleWithGPSResponse(VehicleResponse):
    """Vehicle response with real-time GPS data"""
    gps_data: Optional[VehicleGPSData] = None
