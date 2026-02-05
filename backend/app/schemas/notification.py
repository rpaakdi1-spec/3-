from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """알림 유형"""
    ORDER_CONFIRMED = "ORDER_CONFIRMED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    DISPATCH_ASSIGNED = "DISPATCH_ASSIGNED"
    DISPATCH_COMPLETED = "DISPATCH_COMPLETED"
    URGENT_DISPATCH = "URGENT_DISPATCH"
    TEMPERATURE_ALERT = "TEMPERATURE_ALERT"
    VEHICLE_MAINTENANCE = "VEHICLE_MAINTENANCE"
    DRIVER_SCHEDULE = "DRIVER_SCHEDULE"


class NotificationChannel(str, Enum):
    """알림 채널"""
    SMS = "SMS"
    KAKAO = "KAKAO"
    PUSH = "PUSH"
    EMAIL = "EMAIL"


class NotificationStatus(str, Enum):
    """알림 상태"""
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    DELIVERED = "DELIVERED"
    READ = "READ"


# Request Schemas
class NotificationSendRequest(BaseModel):
    """알림 발송 요청"""
    notification_type: NotificationType
    channel: NotificationChannel
    recipient_name: str = Field(..., min_length=1, max_length=100, description="수신자명")
    recipient_phone: Optional[str] = Field(None, description="수신자 전화번호 (SMS/카카오톡용)")
    recipient_email: Optional[str] = Field(None, description="수신자 이메일 (EMAIL용)")
    recipient_device_token: Optional[str] = Field(None, description="기기 토큰 (PUSH용)")
    
    title: str = Field(..., min_length=1, max_length=200, description="알림 제목")
    message: str = Field(..., min_length=1, description="알림 메시지")
    template_code: Optional[str] = Field(None, description="템플릿 코드")
    
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="추가 데이터")
    
    order_id: Optional[int] = Field(None, description="주문ID")
    dispatch_id: Optional[int] = Field(None, description="배차ID")
    vehicle_id: Optional[int] = Field(None, description="차량ID")
    driver_id: Optional[int] = Field(None, description="기사ID")

    @field_validator('recipient_phone')
    def validate_phone(cls, v, values):
        if v and values.data.get('channel') in [NotificationChannel.SMS, NotificationChannel.KAKAO]:
            # 한국 전화번호 검증 (간단 버전)
            import re
            if not re.match(r'^01[0-9]-?\d{3,4}-?\d{4}$', v.replace('-', '')):
                raise ValueError('올바른 전화번호 형식이 아닙니다')
        return v


class TemplateNotificationRequest(BaseModel):
    """템플릿 기반 알림 발송 요청"""
    template_code: str = Field(..., description="템플릿 코드")
    channel: NotificationChannel
    recipient_name: str
    recipient_phone: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_device_token: Optional[str] = None
    
    variables: Dict[str, Any] = Field(default_factory=dict, description="템플릿 변수")
    
    order_id: Optional[int] = None
    dispatch_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None


class BulkNotificationRequest(BaseModel):
    """일괄 알림 발송 요청"""
    notifications: List[NotificationSendRequest] = Field(..., min_length=1, max_length=100)


# Response Schemas
class NotificationResponse(BaseModel):
    """알림 응답"""
    id: int
    notification_type: NotificationType
    channel: NotificationChannel
    status: NotificationStatus
    
    recipient_name: str
    recipient_phone: Optional[str] = None
    recipient_email: Optional[str] = None
    
    title: str
    message: str
    template_code: Optional[str] = None
    
    metadata: Optional[Dict[str, Any]] = None
    
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    external_id: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int
    
    order_id: Optional[int] = None
    dispatch_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """알림 목록 응답"""
    total: int
    items: List[NotificationResponse]


class NotificationStatsResponse(BaseModel):
    """알림 통계 응답"""
    total_sent: int
    total_delivered: int
    total_failed: int
    total_pending: int
    
    by_channel: Dict[str, int]
    by_type: Dict[str, int]
    by_status: Dict[str, int]


# Template Schemas
class NotificationTemplateCreate(BaseModel):
    """알림 템플릿 생성"""
    template_code: str = Field(..., min_length=1, max_length=100)
    template_name: str = Field(..., min_length=1, max_length=200)
    notification_type: NotificationType
    channel: NotificationChannel
    
    title_template: str = Field(..., min_length=1, max_length=200)
    message_template: str = Field(..., min_length=1)
    
    kakao_template_id: Optional[str] = None
    kakao_button_json: Optional[Dict[str, Any]] = None
    
    description: Optional[str] = None
    variables: Optional[List[str]] = Field(default_factory=list)
    is_active: bool = True


class NotificationTemplateUpdate(BaseModel):
    """알림 템플릿 수정"""
    template_name: Optional[str] = None
    title_template: Optional[str] = None
    message_template: Optional[str] = None
    
    kakao_template_id: Optional[str] = None
    kakao_button_json: Optional[Dict[str, Any]] = None
    
    description: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None


class NotificationTemplateResponse(BaseModel):
    """알림 템플릿 응답"""
    id: int
    template_code: str
    template_name: str
    notification_type: NotificationType
    channel: NotificationChannel
    
    title_template: str
    message_template: str
    
    kakao_template_id: Optional[str] = None
    kakao_button_json: Optional[Dict[str, Any]] = None
    
    description: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: bool
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
