"""
Vehicle Location Schemas
실시간 차량 위치 및 온도 스키마
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ===== VehicleLocation Schemas =====

class VehicleLocationBase(BaseModel):
    """VehicleLocation 기본 스키마"""
    latitude: float = Field(..., description="위도")
    longitude: float = Field(..., description="경도")
    accuracy: Optional[float] = Field(None, description="GPS 정확도 (미터)")
    altitude: Optional[float] = Field(None, description="고도 (미터)")
    speed: Optional[float] = Field(None, description="속도 (km/h)")
    heading: Optional[float] = Field(None, description="방향 (0-360도)")
    
    temperature_celsius: Optional[float] = Field(None, description="화물칸 온도 (°C)")
    humidity_percent: Optional[float] = Field(None, description="습도 (%)")
    
    uvis_device_id: Optional[str] = Field(None, description="UVIS 단말기 ID")
    uvis_timestamp: Optional[datetime] = Field(None, description="UVIS API 타임스탬프")
    
    is_ignition_on: bool = Field(True, description="시동 상태")
    battery_voltage: Optional[float] = Field(None, description="배터리 전압 (V)")
    fuel_level_percent: Optional[float] = Field(None, description="연료 잔량 (%)")
    odometer_km: Optional[float] = Field(None, description="주행거리 (km)")
    
    address: Optional[str] = Field(None, description="역지오코딩 주소")
    notes: Optional[str] = Field(None, description="특이사항")


class VehicleLocationCreate(VehicleLocationBase):
    """VehicleLocation 생성 스키마"""
    vehicle_id: int = Field(..., description="차량 ID")
    dispatch_id: Optional[int] = Field(None, description="배차 ID")


class VehicleLocationUpdate(BaseModel):
    """VehicleLocation 업데이트 스키마"""
    address: Optional[str] = None
    notes: Optional[str] = None


class VehicleLocationResponse(VehicleLocationBase):
    """VehicleLocation 응답 스키마"""
    id: int
    vehicle_id: int
    dispatch_id: Optional[int]
    recorded_at: datetime
    
    # 차량 정보 추가
    vehicle_code: Optional[str] = None
    vehicle_plate_number: Optional[str] = None
    
    model_config = {"from_attributes": True}


# ===== TemperatureAlert Schemas =====

class TemperatureAlertBase(BaseModel):
    """TemperatureAlert 기본 스키마"""
    alert_type: str = Field(..., description="알림 유형 (TOO_HOT, TOO_COLD, SENSOR_ERROR)")
    severity: str = Field(..., description="심각도 (WARNING, CRITICAL)")
    temperature_celsius: float = Field(..., description="감지 온도 (°C)")
    threshold_min: Optional[float] = Field(None, description="최저 임계값 (°C)")
    threshold_max: Optional[float] = Field(None, description="최고 임계값 (°C)")
    message: Optional[str] = Field(None, description="알림 메시지")
    notes: Optional[str] = Field(None, description="특이사항")


class TemperatureAlertCreate(TemperatureAlertBase):
    """TemperatureAlert 생성 스키마"""
    vehicle_id: int = Field(..., description="차량 ID")
    dispatch_id: Optional[int] = Field(None, description="배차 ID")
    location_id: Optional[int] = Field(None, description="위치 ID")


class TemperatureAlertUpdate(BaseModel):
    """TemperatureAlert 업데이트 스키마"""
    resolved_at: Optional[datetime] = None
    is_resolved: Optional[bool] = None
    notification_sent: Optional[bool] = None
    notification_channels: Optional[str] = None
    notes: Optional[str] = None


class TemperatureAlertResponse(TemperatureAlertBase):
    """TemperatureAlert 응답 스키마"""
    id: int
    vehicle_id: int
    dispatch_id: Optional[int]
    location_id: Optional[int]
    detected_at: datetime
    resolved_at: Optional[datetime]
    is_resolved: bool
    notification_sent: bool
    notification_channels: Optional[str]
    
    # 차량 정보 추가
    vehicle_code: Optional[str] = None
    vehicle_plate_number: Optional[str] = None
    
    model_config = {"from_attributes": True}


# ===== Real-time Tracking Schemas =====

class VehicleTrackingInfo(BaseModel):
    """실시간 차량 추적 정보"""
    vehicle_id: int
    vehicle_code: str
    plate_number: str
    vehicle_type: str
    
    # 현재 위치
    current_location: Optional[VehicleLocationResponse] = None
    
    # 배차 정보
    dispatch_id: Optional[int] = None
    dispatch_number: Optional[str] = None
    dispatch_status: Optional[str] = None
    
    # 통계
    total_distance_today_km: float = Field(0.0, description="오늘 주행 거리 (km)")
    average_speed_kmh: float = Field(0.0, description="평균 속도 (km/h)")
    last_update: Optional[datetime] = None
    
    # 온도 알림
    active_alerts_count: int = Field(0, description="활성 알림 수")
    recent_alerts: list[TemperatureAlertResponse] = Field(default_factory=list, description="최근 알림")


class TrackingDashboardResponse(BaseModel):
    """실시간 추적 대시보드 응답"""
    total_vehicles: int = Field(..., description="전체 차량 수")
    active_vehicles: int = Field(..., description="운행 중 차량 수")
    idle_vehicles: int = Field(..., description="대기 중 차량 수")
    
    vehicles: list[VehicleTrackingInfo] = Field(default_factory=list, description="차량 목록")
    
    total_alerts: int = Field(0, description="전체 알림 수")
    critical_alerts: int = Field(0, description="위험 알림 수")
    warning_alerts: int = Field(0, description="경고 알림 수")
