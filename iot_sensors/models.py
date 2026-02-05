"""
IoT 센서 통합 - 데이터 모델
2026-02-05
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class SensorType(str, Enum):
    """센서 타입"""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    GPS = "gps"
    DOOR = "door"
    PRESSURE = "pressure"
    VIBRATION = "vibration"


class AlertLevel(str, Enum):
    """알림 레벨"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class SensorStatus(str, Enum):
    """센서 상태"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


# ============================================================================
# 센서 데이터 모델
# ============================================================================

class SensorBase(BaseModel):
    """센서 기본 정보"""
    sensor_id: str = Field(..., description="센서 고유 ID")
    vehicle_id: Optional[str] = Field(None, description="차량 ID")
    sensor_type: SensorType = Field(..., description="센서 타입")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="타임스탬프")


class TemperatureSensorData(SensorBase):
    """온도 센서 데이터"""
    sensor_type: SensorType = Field(default=SensorType.TEMPERATURE, const=True)
    temperature: float = Field(..., description="온도 (°C)")
    humidity: Optional[float] = Field(None, description="습도 (%)")
    battery_level: Optional[float] = Field(None, ge=0, le=100, description="배터리 잔량 (%)")
    
    @validator("temperature")
    def validate_temperature(cls, v):
        if v < -50 or v > 60:
            raise ValueError("온도 값이 허용 범위를 벗어났습니다 (-50°C ~ 60°C)")
        return round(v, 1)


class GPSSensorData(SensorBase):
    """GPS 센서 데이터"""
    sensor_type: SensorType = Field(default=SensorType.GPS, const=True)
    latitude: float = Field(..., ge=-90, le=90, description="위도")
    longitude: float = Field(..., ge=-180, le=180, description="경도")
    altitude: Optional[float] = Field(None, description="고도 (m)")
    speed: Optional[float] = Field(None, ge=0, description="속도 (km/h)")
    heading: Optional[float] = Field(None, ge=0, le=360, description="방향 (°)")
    accuracy: Optional[float] = Field(None, ge=0, description="정확도 (m)")


class DoorSensorData(SensorBase):
    """도어 센서 데이터"""
    sensor_type: SensorType = Field(default=SensorType.DOOR, const=True)
    is_open: bool = Field(..., description="도어 열림 여부")
    duration: Optional[int] = Field(None, ge=0, description="열림 지속 시간 (초)")


class HumiditySensorData(SensorBase):
    """습도 센서 데이터"""
    sensor_type: SensorType = Field(default=SensorType.HUMIDITY, const=True)
    humidity: float = Field(..., ge=0, le=100, description="습도 (%)")
    temperature: Optional[float] = Field(None, description="온도 (°C)")


# ============================================================================
# 센서 등록 및 관리
# ============================================================================

class SensorRegistration(BaseModel):
    """센서 등록 정보"""
    sensor_id: str = Field(..., description="센서 고유 ID")
    sensor_type: SensorType = Field(..., description="센서 타입")
    vehicle_id: Optional[str] = Field(None, description="연결된 차량 ID")
    location: Optional[str] = Field(None, description="센서 설치 위치")
    manufacturer: Optional[str] = Field(None, description="제조사")
    model: Optional[str] = Field(None, description="모델명")
    firmware_version: Optional[str] = Field(None, description="펌웨어 버전")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="추가 메타데이터")


class SensorInfo(SensorRegistration):
    """센서 상세 정보"""
    id: int = Field(..., description="DB ID")
    status: SensorStatus = Field(default=SensorStatus.ACTIVE, description="센서 상태")
    last_seen: Optional[datetime] = Field(None, description="마지막 데이터 수신 시간")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="등록 시간")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="수정 시간")
    
    class Config:
        from_attributes = True


# ============================================================================
# 알림 및 이벤트
# ============================================================================

class AlertBase(BaseModel):
    """알림 기본 정보"""
    alert_type: str = Field(..., description="알림 타입")
    level: AlertLevel = Field(..., description="알림 레벨")
    message: str = Field(..., description="알림 메시지")
    sensor_id: str = Field(..., description="센서 ID")
    vehicle_id: Optional[str] = Field(None, description="차량 ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="발생 시간")


class TemperatureAlert(AlertBase):
    """온도 알림"""
    alert_type: str = Field(default="temperature_anomaly", const=True)
    current_temperature: float = Field(..., description="현재 온도")
    threshold_min: float = Field(..., description="최소 임계값")
    threshold_max: float = Field(..., description="최대 임계값")
    temperature_category: str = Field(..., description="온도대 (냉동/냉장/상온)")


class DoorAlert(AlertBase):
    """도어 알림"""
    alert_type: str = Field(default="door_open", const=True)
    duration: int = Field(..., description="열림 지속 시간 (초)")


class SensorOfflineAlert(AlertBase):
    """센서 오프라인 알림"""
    alert_type: str = Field(default="sensor_offline", const=True)
    last_seen: datetime = Field(..., description="마지막 데이터 수신 시간")


# ============================================================================
# 분석 및 통계
# ============================================================================

class SensorStatistics(BaseModel):
    """센서 통계"""
    sensor_id: str
    sensor_type: SensorType
    period_start: datetime
    period_end: datetime
    data_count: int
    
    # 온도 센서 통계
    avg_temperature: Optional[float] = None
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    
    # GPS 센서 통계
    total_distance: Optional[float] = None  # km
    avg_speed: Optional[float] = None  # km/h
    max_speed: Optional[float] = None  # km/h
    
    # 도어 센서 통계
    door_open_count: Optional[int] = None
    total_open_duration: Optional[int] = None  # seconds


class VehicleSensorSummary(BaseModel):
    """차량별 센서 요약"""
    vehicle_id: str
    timestamp: datetime
    
    # 센서 상태
    active_sensors: int
    inactive_sensors: int
    
    # 최신 센서 데이터
    current_temperature: Optional[float] = None
    current_humidity: Optional[float] = None
    current_location: Optional[Dict[str, float]] = None  # {"lat": ..., "lng": ...}
    door_status: Optional[str] = None
    
    # 알림
    active_alerts: int
    critical_alerts: int


# ============================================================================
# HTTP API 모델
# ============================================================================

class SensorDataUpload(BaseModel):
    """센서 데이터 업로드 (HTTP POST)"""
    api_key: str = Field(..., description="API 키")
    data: list[TemperatureSensorData | GPSSensorData | DoorSensorData | HumiditySensorData]


class SensorDataResponse(BaseModel):
    """센서 데이터 응답"""
    success: bool
    message: str
    data_count: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# WebSocket 메시지
# ============================================================================

class WebSocketMessage(BaseModel):
    """WebSocket 메시지"""
    type: str = Field(..., description="메시지 타입 (sensor_data, alert, heartbeat)")
    payload: Dict[str, Any] = Field(..., description="메시지 페이로드")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
