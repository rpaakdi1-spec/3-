from __future__ import annotations
"""
UVIS GPS 관제 시스템 스키마
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# ==================== 인증키 관련 ====================

class UvisAccessKeyResponse(BaseModel):
    """실시간 인증키 응답"""
    id: int
    serial_key: str
    access_key: str
    issued_at: datetime
    expires_at: datetime
    is_active: bool
    
    model_config = {"from_attributes": True}


# ==================== GPS 관련 ====================

class VehicleGPSLogBase(BaseModel):
    """GPS 로그 기본"""
    tid_id: str = Field(..., description="단말기 ID")
    bi_date: str = Field(..., description="날짜 (YYYYMMDD)")
    bi_time: str = Field(..., description="시간 (HHMMSS)")
    cm_number: Optional[str] = Field(None, description="차량번호")
    bi_turn_onoff: Optional[str] = Field(None, description="시동 상태")
    bi_x_position: str = Field(..., description="위도 (문자열)")
    bi_y_position: str = Field(..., description="경도 (문자열)")
    bi_gps_speed: Optional[int] = Field(None, description="속도 (km/h)")


class VehicleGPSLogResponse(VehicleGPSLogBase):
    """GPS 로그 응답"""
    id: int
    vehicle_id: Optional[int]
    latitude: Optional[float] = Field(None, description="위도 (Float)")
    longitude: Optional[float] = Field(None, description="경도 (Float)")
    is_engine_on: bool = Field(False, description="시동 상태")
    speed_kmh: int = Field(0, description="속도 (km/h)")
    created_at: datetime
    
    model_config = {"from_attributes": True}


class VehicleGPSListResponse(BaseModel):
    """GPS 로그 목록 응답"""
    total: int
    items: List[VehicleGPSLogResponse]


# ==================== 온도 관련 ====================

class VehicleTemperatureLogBase(BaseModel):
    """온도 로그 기본"""
    tid_id: str = Field(..., description="단말기 ID")
    tpl_date: str = Field(..., description="날짜 (YYYYMMDD)")
    tpl_time: str = Field(..., description="시간 (HHMMSS)")
    cm_number: Optional[str] = Field(None, description="차량번호")
    tpl_x_position: Optional[str] = Field(None, description="위도 (문자열)")
    tpl_y_position: Optional[str] = Field(None, description="경도 (문자열)")
    tpl_signal_a: Optional[int] = Field(None, description="A 온도 부호 (0='+', 1='-')")
    tpl_degree_a: Optional[str] = Field(None, description="A 온도값")
    tpl_signal_b: Optional[int] = Field(None, description="B 온도 부호 (0='+', 1='-')")
    tpl_degree_b: Optional[str] = Field(None, description="B 온도값")


class VehicleTemperatureLogResponse(VehicleTemperatureLogBase):
    """온도 로그 응답"""
    id: int
    vehicle_id: Optional[int]
    off_key: Optional[str] = Field(None, description="고객 코드")
    temperature_a: Optional[float] = Field(None, description="A 온도 (℃)")
    temperature_b: Optional[float] = Field(None, description="B 온도 (℃)")
    latitude: Optional[float] = Field(None, description="위도 (Float)")
    longitude: Optional[float] = Field(None, description="경도 (Float)")
    created_at: datetime
    
    model_config = {"from_attributes": True}


class VehicleTemperatureListResponse(BaseModel):
    """온도 로그 목록 응답"""
    total: int
    items: List[VehicleTemperatureLogResponse]


# ==================== 실시간 모니터링 ====================

class VehicleRealtimeStatus(BaseModel):
    """차량 실시간 상태 (GPS + 온도 통합)"""
    vehicle_id: Optional[int] = Field(None, description="차량 ID")
    vehicle_plate_number: Optional[str] = Field(None, description="차량번호")
    tid_id: str = Field(..., description="단말기 ID")
    
    # GPS 정보
    gps_datetime: Optional[str] = Field(None, description="GPS 일시 (YYYY-MM-DD HH:MM:SS)")
    latitude: Optional[float] = Field(None, description="위도")
    longitude: Optional[float] = Field(None, description="경도")
    is_engine_on: Optional[bool] = Field(None, description="시동 상태")
    speed_kmh: Optional[int] = Field(None, description="속도 (km/h)")
    
    # 온도 정보
    temperature_datetime: Optional[str] = Field(None, description="온도 일시 (YYYY-MM-DD HH:MM:SS)")
    temperature_a: Optional[float] = Field(None, description="A 온도 (℃)")
    temperature_b: Optional[float] = Field(None, description="B 온도 (℃)")
    
    # 최종 업데이트
    last_updated: Optional[datetime] = Field(None, description="최종 업데이트")


class VehicleRealtimeListResponse(BaseModel):
    """차량 실시간 상태 목록"""
    total: int
    items: List[VehicleRealtimeStatus]


# ==================== API 로그 ====================

class UvisApiLogResponse(BaseModel):
    """UVIS API 로그 응답"""
    id: int
    api_type: str = Field(..., description="API 유형 (auth/gps/temperature)")
    method: str = Field(..., description="HTTP 메서드")
    url: str = Field(..., description="요청 URL")
    request_params: Optional[str] = Field(None, description="요청 파라미터")
    response_status: Optional[int] = Field(None, description="응답 상태 코드")
    response_data: Optional[str] = Field(None, description="응답 데이터")
    error_message: Optional[str] = Field(None, description="에러 메시지")
    execution_time_ms: Optional[int] = Field(None, description="실행 시간 (ms)")
    created_at: datetime
    
    model_config = {"from_attributes": True}


class UvisApiLogListResponse(BaseModel):
    """API 로그 목록"""
    total: int
    items: List[UvisApiLogResponse]


# ==================== 동기화 요청 ====================

class SyncGPSRequest(BaseModel):
    """GPS 데이터 동기화 요청"""
    force_new_key: bool = Field(False, description="새 인증키 강제 발급 여부")


class SyncTemperatureRequest(BaseModel):
    """온도 데이터 동기화 요청"""
    force_new_key: bool = Field(False, description="새 인증키 강제 발급 여부")


class SyncResponse(BaseModel):
    """동기화 응답"""
    success: bool
    message: str
    data_count: int = Field(0, description="동기화된 데이터 건수")
    access_key_issued: bool = Field(False, description="새 인증키 발급 여부")
