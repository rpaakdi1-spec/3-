from __future__ import annotations
"""
Tracking schemas for customer delivery tracking system
고객용 배송 추적 시스템 스키마
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TrackingStatus(str, Enum):
    """배송 추적 상태"""
    ORDER_RECEIVED = "order_received"  # 주문 접수
    DISPATCHED = "dispatched"  # 배차 완료
    IN_TRANSIT = "in_transit"  # 배송 중
    OUT_FOR_DELIVERY = "out_for_delivery"  # 배송 출발
    DELIVERED = "delivered"  # 배송 완료
    DELAYED = "delayed"  # 지연
    EXCEPTION = "exception"  # 예외 발생


class TrackingStatusKorean:
    """한글 상태 매핑"""
    STATUS_MAP = {
        TrackingStatus.ORDER_RECEIVED: "주문 접수",
        TrackingStatus.DISPATCHED: "배차 완료",
        TrackingStatus.IN_TRANSIT: "배송 중",
        TrackingStatus.OUT_FOR_DELIVERY: "배송 출발",
        TrackingStatus.DELIVERED: "배송 완료",
        TrackingStatus.DELAYED: "배송 지연",
        TrackingStatus.EXCEPTION: "예외 발생",
    }


class TrackingEvent(BaseModel):
    """배송 추적 이벤트"""
    status: TrackingStatus = Field(..., description="배송 상태")
    status_description: str = Field(..., description="상태 설명 (한글)")
    location: Optional[str] = Field(None, description="위치")
    timestamp: datetime = Field(..., description="발생 시각")
    description: Optional[str] = Field(None, description="상세 설명")


class TrackingInfo(BaseModel):
    """배송 추적 정보"""
    tracking_number: str = Field(..., description="추적 번호")
    order_number: str = Field(..., description="주문 번호")
    current_status: TrackingStatus = Field(..., description="현재 상태")
    current_status_description: str = Field(..., description="현재 상태 설명 (한글)")
    
    # 배송 정보
    sender_name: str = Field(..., description="발송인")
    sender_address: Optional[str] = Field(None, description="발송지 주소")
    receiver_name: str = Field(..., description="수령인")
    receiver_address: str = Field(..., description="배송지 주소")
    receiver_phone: Optional[str] = Field(None, description="수령인 연락처")
    
    # 상품 정보
    product_name: Optional[str] = Field(None, description="상품명")
    pallet_count: int = Field(..., description="팔레트 수")
    weight_kg: float = Field(..., description="중량 (kg)")
    temperature_zone: Optional[str] = Field(None, description="온도대")
    
    # 차량 정보
    vehicle_code: Optional[str] = Field(None, description="차량 번호")
    driver_name: Optional[str] = Field(None, description="기사명")
    driver_phone: Optional[str] = Field(None, description="기사 연락처")
    
    # 위치 정보
    current_location: Optional[dict] = Field(None, description="현재 위치 (lat, lng)")
    
    # 시간 정보
    order_date: datetime = Field(..., description="주문 일시")
    dispatch_date: Optional[datetime] = Field(None, description="배차 일시")
    estimated_delivery_time: Optional[datetime] = Field(None, description="예상 배송 시간")
    actual_delivery_time: Optional[datetime] = Field(None, description="실제 배송 시간")
    
    # 이벤트 히스토리
    events: List[TrackingEvent] = Field(default_factory=list, description="배송 이벤트 히스토리")
    


class TrackingNumberCreate(BaseModel):
    """추적 번호 생성 요청"""
    order_id: int = Field(..., description="주문 ID")


class TrackingNumberResponse(BaseModel):
    """추적 번호 생성 응답"""
    tracking_number: str = Field(..., description="생성된 추적 번호")
    order_id: int = Field(..., description="주문 ID")
    created_at: datetime = Field(..., description="생성 시각")


class TrackingRequest(BaseModel):
    """추적 번호 조회 요청"""
    tracking_number: str = Field(..., description="추적 번호", min_length=10, max_length=50)


class TrackingNotificationRequest(BaseModel):
    """알림 전송 요청"""
    tracking_number: str = Field(..., description="추적 번호")
    notification_type: str = Field(..., description="알림 유형 (sms/email)")
    recipient: str = Field(..., description="수신자 (전화번호 또는 이메일)")
    message: Optional[str] = Field(None, description="커스텀 메시지")


class TrackingLinkResponse(BaseModel):
    """추적 링크 응답"""
    tracking_number: str = Field(..., description="추적 번호")
    tracking_url: str = Field(..., description="추적 URL")
    qr_code_url: Optional[str] = Field(None, description="QR 코드 URL")


class TrackingStatistics(BaseModel):
    """배송 추적 통계"""
    total_shipments: int = Field(..., description="총 배송 건수")
    in_transit: int = Field(..., description="배송 중")
    delivered: int = Field(..., description="배송 완료")
    delayed: int = Field(..., description="지연")
    on_time_rate: float = Field(..., description="정시 배송률 (%)")
    avg_delivery_time_hours: float = Field(..., description="평균 배송 시간 (시간)")


class DeliveryStatusResponse(BaseModel):
    """배송 상태 응답"""
    tracking_number: str = Field(..., description="추적 번호")
    current_status: TrackingStatus = Field(..., description="현재 상태")
    status_description: str = Field(..., description="상태 설명")
    updated_at: datetime = Field(..., description="업데이트 시각")


class DeliveryTimelineResponse(BaseModel):
    """배송 타임라인 응답"""
    tracking_number: str = Field(..., description="추적 번호")
    events: List[TrackingEvent] = Field(..., description="이벤트 목록")


class RouteDetailsResponse(BaseModel):
    """경로 상세 응답"""
    tracking_number: str = Field(..., description="추적 번호")
    origin: Optional[dict] = Field(None, description="출발지 정보")
    destination: Optional[dict] = Field(None, description="도착지 정보")
    current_location: Optional[dict] = Field(None, description="현재 위치")
    estimated_arrival: Optional[datetime] = Field(None, description="예상 도착 시간")
    distance_remaining_km: Optional[float] = Field(None, description="남은 거리 (km)")


class PublicTrackingResponse(BaseModel):
    """공개 추적 정보 응답 (고객용)"""
    tracking_number: str = Field(..., description="추적 번호")
    current_status: TrackingStatus = Field(..., description="현재 상태")
    status_description: str = Field(..., description="상태 설명")
    estimated_delivery: Optional[datetime] = Field(None, description="예상 배송 시간")
    events: List[TrackingEvent] = Field(default_factory=list, description="배송 이벤트")


class NotificationRequest(BaseModel):
    """알림 요청"""
    tracking_number: str = Field(..., description="추적 번호")
    recipient_email: Optional[str] = Field(None, description="수신자 이메일")
    recipient_phone: Optional[str] = Field(None, description="수신자 전화번호")
    notification_type: str = Field(..., description="알림 유형 (email/sms/both)")


class NotificationResponse(BaseModel):
    """알림 응답"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="결과 메시지")
    sent_at: datetime = Field(..., description="전송 시각")
