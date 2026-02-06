"""
Phase 7: Mobile App API Schemas
모바일 앱 전용 스키마 정의
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== Enums ====================

class DeviceType(str, Enum):
    """디바이스 타입"""
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"


class NotificationType(str, Enum):
    """알림 타입"""
    NEW_DISPATCH = "new_dispatch"
    DISPATCH_UPDATED = "dispatch_updated"
    DISPATCH_CANCELLED = "dispatch_cancelled"
    TEMPERATURE_ALERT = "temperature_alert"
    EMERGENCY_ALERT = "emergency_alert"
    MESSAGE = "message"
    SYSTEM = "system"


class NotificationPriority(str, Enum):
    """알림 우선순위"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class PhotoType(str, Enum):
    """사진 타입"""
    DELIVERY_PROOF = "delivery_proof"
    SIGNATURE = "signature"
    VEHICLE_INSPECTION = "vehicle_inspection"
    INCIDENT = "incident"
    DAMAGE = "damage"
    OTHER = "other"


# ==================== Authentication ====================

class MobileLoginRequest(BaseModel):
    """모바일 로그인 요청"""
    username: str = Field(..., description="사용자명")
    password: str = Field(..., description="비밀번호")
    device_type: DeviceType = Field(..., description="디바이스 타입")
    device_id: str = Field(..., description="디바이스 고유 ID")
    fcm_token: Optional[str] = Field(None, description="FCM 푸시 토큰")
    app_version: Optional[str] = Field(None, description="앱 버전")


class MobileLoginResponse(BaseModel):
    """모바일 로그인 응답"""
    access_token: str = Field(..., description="액세스 토큰")
    refresh_token: str = Field(..., description="리프레시 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    expires_in: int = Field(..., description="토큰 만료 시간 (초)")
    user_id: int
    username: str
    role: str
    full_name: Optional[str]


class RefreshTokenRequest(BaseModel):
    """토큰 갱신 요청"""
    refresh_token: str = Field(..., description="리프레시 토큰")


# ==================== Device Management ====================

class DeviceRegistration(BaseModel):
    """디바이스 등록 요청"""
    device_type: DeviceType
    device_id: str = Field(..., description="디바이스 고유 ID")
    fcm_token: str = Field(..., description="FCM 푸시 토큰")
    app_version: Optional[str] = None
    os_version: Optional[str] = None
    device_model: Optional[str] = None


class DeviceInfo(BaseModel):
    """디바이스 정보"""
    id: int
    device_type: str
    device_id: str
    device_model: Optional[str]
    app_version: Optional[str]
    is_active: bool
    last_used_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Push Notifications ====================

class SendPushNotificationRequest(BaseModel):
    """푸시 알림 발송 요청"""
    user_ids: Optional[List[int]] = Field(None, description="수신자 사용자 ID 목록")
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    title: str = Field(..., max_length=100)
    body: str = Field(..., max_length=500)
    data: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    action_url: Optional[str] = None
    silent: bool = Field(False, description="조용한 알림 (데이터만)")
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()


class NotificationResponse(BaseModel):
    """알림 응답"""
    id: int
    notification_type: str
    priority: str
    title: str
    body: str
    data: Optional[Dict[str, Any]]
    image_url: Optional[str]
    action_url: Optional[str]
    is_read: bool
    is_deleted: bool
    created_at: datetime
    read_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ==================== GPS Location Tracking ====================

class LocationUpdate(BaseModel):
    """단일 위치 업데이트"""
    latitude: float = Field(..., ge=-90, le=90, description="위도")
    longitude: float = Field(..., ge=-180, le=180, description="경도")
    accuracy: Optional[float] = Field(None, ge=0, description="정확도 (미터)")
    altitude: Optional[float] = Field(None, description="고도 (미터)")
    speed: Optional[float] = Field(None, ge=0, description="속도 (km/h)")
    heading: Optional[float] = Field(None, ge=0, le=360, description="방향 (0-360도)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BatchLocationUpdate(BaseModel):
    """배치 위치 업데이트 (여러 위치)"""
    vehicle_id: Optional[int] = Field(None, description="차량 ID")
    dispatch_id: Optional[int] = Field(None, description="배차 ID")
    locations: List[LocationUpdate] = Field(..., min_items=1, max_items=100)
    
    @validator('locations')
    def check_locations_chronological(cls, v):
        """위치가 시간 순서대로 정렬되어 있는지 확인"""
        timestamps = [loc.timestamp for loc in v]
        if timestamps != sorted(timestamps):
            raise ValueError('Locations must be in chronological order')
        return v


class LocationResponse(BaseModel):
    """위치 응답"""
    id: int
    vehicle_id: int
    dispatch_id: Optional[int]
    latitude: float
    longitude: float
    accuracy: Optional[float]
    speed: Optional[float]
    heading: Optional[float]
    temperature_celsius: Optional[float]
    recorded_at: datetime
    address: Optional[str]
    
    class Config:
        from_attributes = True


# ==================== Photo Upload ====================

class PhotoUploadRequest(BaseModel):
    """사진 업로드 메타데이터"""
    photo_type: PhotoType
    dispatch_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=500)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class PhotoResponse(BaseModel):
    """사진 업로드 응답"""
    id: int
    photo_type: str
    url: str
    thumbnail_url: Optional[str]
    file_size: int
    mime_type: str
    width: Optional[int]
    height: Optional[int]
    latitude: Optional[float]
    longitude: Optional[float]
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Dispatch Summary ====================

class DispatchSummary(BaseModel):
    """배차 요약 (모바일용)"""
    total: int = Field(..., description="총 배차 수")
    pending: int = Field(..., description="대기 중")
    in_progress: int = Field(..., description="진행 중")
    completed: int = Field(..., description="완료")
    cancelled: int = Field(..., description="취소")
    today_earnings: Optional[float] = Field(None, description="오늘 수익")


class MobileDispatchDetail(BaseModel):
    """모바일용 배차 상세"""
    id: int
    order_id: int
    vehicle_id: Optional[int]
    status: str
    
    # 픽업 정보
    pickup_address: str
    pickup_contact: Optional[str]
    pickup_latitude: Optional[float]
    pickup_longitude: Optional[float]
    
    # 배송 정보
    delivery_address: str
    delivery_contact: Optional[str]
    delivery_latitude: Optional[float]
    delivery_longitude: Optional[float]
    
    # 시간 정보
    scheduled_time: datetime
    actual_start_time: Optional[datetime]
    actual_end_time: Optional[datetime]
    estimated_duration: Optional[int]  # 예상 소요 시간 (분)
    
    # 상품 정보
    product_name: Optional[str]
    product_category: Optional[str]
    temperature_min: Optional[float]
    temperature_max: Optional[float]
    
    # 추가 정보
    notes: Optional[str]
    distance_km: Optional[float]
    earnings: Optional[float]
    
    class Config:
        from_attributes = True


# ==================== Real-time Updates ====================

class RealtimeLocationBroadcast(BaseModel):
    """실시간 위치 방송 메시지"""
    vehicle_id: int
    dispatch_id: Optional[int]
    latitude: float
    longitude: float
    speed: Optional[float]
    heading: Optional[float]
    temperature_celsius: Optional[float]
    timestamp: datetime


class RealtimeDispatchUpdate(BaseModel):
    """실시간 배차 업데이트 메시지"""
    dispatch_id: int
    status: str
    message: str
    timestamp: datetime
    data: Optional[Dict[str, Any]]


# ==================== Statistics ====================

class MobileStatistics(BaseModel):
    """모바일 통계"""
    today_dispatches: int
    today_completed: int
    today_distance_km: float
    today_earnings: float
    week_dispatches: int
    week_completed: int
    week_distance_km: float
    week_earnings: float
    total_dispatches: int
    total_distance_km: float
    rating: Optional[float] = Field(None, ge=0, le=5)
    rating_count: int = 0


# ==================== Offline Sync ====================

class SyncRequest(BaseModel):
    """오프라인 동기화 요청"""
    last_sync: Optional[datetime] = Field(None, description="마지막 동기화 시간")
    sync_types: List[str] = Field(
        default=["dispatches", "locations", "notifications"],
        description="동기화할 데이터 타입"
    )


class SyncResponse(BaseModel):
    """동기화 응답"""
    sync_time: datetime
    dispatches: List[MobileDispatchDetail] = []
    notifications: List[NotificationResponse] = []
    has_more: bool = False
    next_cursor: Optional[str] = None
