from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import Base


class NotificationType(str, enum.Enum):
    """알림 유형"""
    ORDER_CONFIRMED = "ORDER_CONFIRMED"  # 주문 확정
    ORDER_CANCELLED = "ORDER_CANCELLED"  # 주문 취소
    DISPATCH_ASSIGNED = "DISPATCH_ASSIGNED"  # 배차 배정
    DISPATCH_COMPLETED = "DISPATCH_COMPLETED"  # 배차 완료
    URGENT_DISPATCH = "URGENT_DISPATCH"  # 긴급 배차
    TEMPERATURE_ALERT = "TEMPERATURE_ALERT"  # 온도 이상
    VEHICLE_MAINTENANCE = "VEHICLE_MAINTENANCE"  # 차량 정비
    DRIVER_SCHEDULE = "DRIVER_SCHEDULE"  # 기사 스케줄


class NotificationChannel(str, enum.Enum):
    """알림 채널"""
    SMS = "SMS"  # SMS
    KAKAO = "KAKAO"  # 카카오톡
    PUSH = "PUSH"  # 웹 푸시
    EMAIL = "EMAIL"  # 이메일


class NotificationStatus(str, enum.Enum):
    """알림 상태"""
    PENDING = "PENDING"  # 대기
    SENT = "SENT"  # 발송 완료
    FAILED = "FAILED"  # 발송 실패
    DELIVERED = "DELIVERED"  # 전달 완료
    READ = "READ"  # 읽음


class Notification(Base):
    """알림 테이블"""
    __tablename__ = "notifications"
    __table_args__ = {'comment': '알림 이력'}

    id = Column(Integer, primary_key=True, index=True, comment='알림ID')
    
    # 알림 정보
    notification_type = Column(
        SQLEnum(NotificationType),
        nullable=False,
        index=True,
        comment='알림 유형'
    )
    channel = Column(
        SQLEnum(NotificationChannel),
        nullable=False,
        index=True,
        comment='알림 채널'
    )
    status = Column(
        SQLEnum(NotificationStatus),
        nullable=False,
        default=NotificationStatus.PENDING,
        index=True,
        comment='알림 상태'
    )
    
    # 수신자 정보
    recipient_name = Column(String(100), nullable=False, comment='수신자명')
    recipient_phone = Column(String(20), index=True, comment='수신자 전화번호')
    recipient_email = Column(String(200), index=True, comment='수신자 이메일')
    recipient_device_token = Column(String(500), comment='기기 토큰 (FCM)')
    
    # 내용
    title = Column(String(200), nullable=False, comment='알림 제목')
    message = Column(Text, nullable=False, comment='알림 메시지')
    template_code = Column(String(100), comment='템플릿 코드 (카카오톡)')
    
    # 추가 데이터
    meta_data = Column(JSON, comment='추가 메타데이터 (JSON)')
    
    # 발송 정보
    sent_at = Column(DateTime, comment='발송 시각')
    delivered_at = Column(DateTime, comment='전달 완료 시각')
    read_at = Column(DateTime, comment='읽음 시각')
    
    # 외부 서비스 정보
    external_id = Column(String(200), comment='외부 서비스 메시지 ID')
    external_response = Column(JSON, comment='외부 서비스 응답')
    error_message = Column(Text, comment='에러 메시지')
    retry_count = Column(Integer, default=0, comment='재시도 횟수')
    
    # 관련 엔티티
    order_id = Column(Integer, index=True, comment='주문ID')
    dispatch_id = Column(Integer, index=True, comment='배차ID')
    vehicle_id = Column(Integer, index=True, comment='차량ID')
    driver_id = Column(Integer, index=True, comment='기사ID')
    
    # 시스템 필드
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment='생성일시')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='수정일시')
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.notification_type}, channel={self.channel}, status={self.status})>"


class NotificationTemplate(Base):
    """알림 템플릿 테이블"""
    __tablename__ = "notification_templates"
    __table_args__ = {'comment': '알림 템플릿'}

    id = Column(Integer, primary_key=True, index=True, comment='템플릿ID')
    
    # 템플릿 정보
    template_code = Column(String(100), unique=True, nullable=False, index=True, comment='템플릿 코드')
    template_name = Column(String(200), nullable=False, comment='템플릿명')
    notification_type = Column(
        SQLEnum(NotificationType),
        nullable=False,
        index=True,
        comment='알림 유형'
    )
    channel = Column(
        SQLEnum(NotificationChannel),
        nullable=False,
        index=True,
        comment='알림 채널'
    )
    
    # 내용 템플릿
    title_template = Column(String(200), nullable=False, comment='제목 템플릿')
    message_template = Column(Text, nullable=False, comment='메시지 템플릿')
    
    # 카카오톡 전용
    kakao_template_id = Column(String(100), comment='카카오톡 템플릿 ID')
    kakao_button_json = Column(JSON, comment='카카오톡 버튼 (JSON)')
    
    # 메타데이터
    description = Column(Text, comment='템플릿 설명')
    variables = Column(JSON, comment='변수 목록 (JSON)')
    is_active = Column(Boolean, default=True, comment='사용 여부')
    
    # 시스템 필드
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment='생성일시')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='수정일시')
    
    def __repr__(self):
        return f"<NotificationTemplate(code={self.template_code}, type={self.notification_type})>"
