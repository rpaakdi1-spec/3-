"""
Phase 16: Driver App Models
드라이버 앱 고도화를 위한 데이터 모델
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, 
    Boolean, ForeignKey, Text, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class NotificationType(str, enum.Enum):
    """알림 타입"""
    DISPATCH_ASSIGNED = "DISPATCH_ASSIGNED"  # 배차 배정
    DISPATCH_UPDATED = "DISPATCH_UPDATED"    # 배차 변경
    DISPATCH_CANCELLED = "DISPATCH_CANCELLED"  # 배차 취소
    ROUTE_OPTIMIZED = "ROUTE_OPTIMIZED"      # 경로 최적화
    CHAT_MESSAGE = "CHAT_MESSAGE"            # 채팅 메시지
    SYSTEM_ALERT = "SYSTEM_ALERT"            # 시스템 알림
    PERFORMANCE_UPDATE = "PERFORMANCE_UPDATE"  # 성과 업데이트


class DeliveryProofType(str, enum.Enum):
    """배송 증빙 타입"""
    PHOTO = "PHOTO"              # 사진
    SIGNATURE = "SIGNATURE"      # 서명
    NOTE = "NOTE"                # 메모
    GPS_LOCATION = "GPS_LOCATION"  # GPS 위치


class ChatMessageType(str, enum.Enum):
    """채팅 메시지 타입"""
    TEXT = "TEXT"      # 텍스트
    IMAGE = "IMAGE"    # 이미지
    FILE = "FILE"      # 파일
    LOCATION = "LOCATION"  # 위치


class DriverNotification(Base):
    """드라이버 알림"""
    __tablename__ = "driver_notifications"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False, index=True)
    dispatch_id = Column(Integer, ForeignKey("dispatches.id"), nullable=True, index=True)
    
    notification_type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    title = Column(String(200), nullable=False, comment="알림 제목")
    message = Column(Text, nullable=False, comment="알림 내용")
    
    # Push 알림 정보
    push_token = Column(String(500), nullable=True, comment="FCM 토큰")
    push_sent = Column(Boolean, default=False, comment="Push 발송 여부")
    push_sent_at = Column(DateTime, nullable=True, comment="Push 발송 시각")
    
    # 알림 상태
    is_read = Column(Boolean, default=False, comment="읽음 여부")
    read_at = Column(DateTime, nullable=True, comment="읽은 시각")
    
    # 액션 정보
    action_required = Column(Boolean, default=False, comment="액션 필요 여부")
    action_url = Column(String(500), nullable=True, comment="액션 URL")
    action_taken = Column(Boolean, default=False, comment="액션 수행 여부")
    action_taken_at = Column(DateTime, nullable=True, comment="액션 수행 시각")
    
    # 메타 정보
    metadata = Column(JSON, nullable=True, comment="추가 메타데이터")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    driver = relationship("Driver", back_populates="notifications")
    dispatch = relationship("Dispatch", back_populates="driver_notifications")


class PushToken(Base):
    """드라이버 Push 토큰"""
    __tablename__ = "push_tokens"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False, index=True)
    
    token = Column(String(500), nullable=False, unique=True, comment="FCM 토큰")
    device_type = Column(String(50), nullable=True, comment="디바이스 타입 (iOS/Android)")
    device_id = Column(String(200), nullable=True, comment="디바이스 ID")
    
    is_active = Column(Boolean, default=True, comment="활성 여부")
    last_used_at = Column(DateTime, default=datetime.utcnow, comment="마지막 사용 시각")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    driver = relationship("Driver", back_populates="push_tokens")


class DeliveryProof(Base):
    """배송 증빙"""
    __tablename__ = "delivery_proofs"

    id = Column(Integer, primary_key=True, index=True)
    dispatch_id = Column(Integer, ForeignKey("dispatches.id"), nullable=False, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    
    proof_type = Column(SQLEnum(DeliveryProofType), nullable=False, comment="증빙 타입")
    
    # 파일 정보
    file_url = Column(String(500), nullable=True, comment="파일 URL")
    file_name = Column(String(200), nullable=True, comment="파일명")
    file_size = Column(Integer, nullable=True, comment="파일 크기 (bytes)")
    
    # 위치 정보
    latitude = Column(Float, nullable=True, comment="위도")
    longitude = Column(Float, nullable=True, comment="경도")
    address = Column(String(500), nullable=True, comment="주소")
    
    # 메모
    note = Column(Text, nullable=True, comment="메모")
    
    # 수령인 정보
    recipient_name = Column(String(100), nullable=True, comment="수령인 이름")
    recipient_phone = Column(String(20), nullable=True, comment="수령인 연락처")
    
    # 메타 정보
    metadata = Column(JSON, nullable=True, comment="추가 메타데이터")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dispatch = relationship("Dispatch", back_populates="delivery_proofs")
    driver = relationship("Driver", back_populates="delivery_proofs")
    order = relationship("Order", back_populates="delivery_proofs")


class ChatRoom(Base):
    """채팅방"""
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_name = Column(String(200), nullable=False, comment="채팅방 이름")
    room_type = Column(String(50), nullable=False, comment="채팅방 타입 (1:1/GROUP)")
    
    # 참여자 정보 (JSON으로 저장)
    participants = Column(JSON, nullable=False, comment="참여자 목록")
    
    # 최근 메시지
    last_message = Column(Text, nullable=True, comment="마지막 메시지")
    last_message_at = Column(DateTime, nullable=True, comment="마지막 메시지 시각")
    
    # 상태
    is_active = Column(Boolean, default=True, comment="활성 여부")
    
    # 메타 정보
    metadata = Column(JSON, nullable=True, comment="추가 메타데이터")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan")


class ChatMessage(Base):
    """채팅 메시지"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False, index=True)
    sender_id = Column(Integer, nullable=False, index=True, comment="발신자 ID")
    sender_type = Column(String(50), nullable=False, comment="발신자 타입 (DRIVER/DISPATCHER/ADMIN)")
    
    message_type = Column(SQLEnum(ChatMessageType), nullable=False, default=ChatMessageType.TEXT)
    content = Column(Text, nullable=True, comment="메시지 내용")
    
    # 파일 정보 (이미지/파일인 경우)
    file_url = Column(String(500), nullable=True, comment="파일 URL")
    file_name = Column(String(200), nullable=True, comment="파일명")
    
    # 위치 정보 (위치 공유인 경우)
    latitude = Column(Float, nullable=True, comment="위도")
    longitude = Column(Float, nullable=True, comment="경도")
    
    # 읽음 상태
    is_read = Column(Boolean, default=False, comment="읽음 여부")
    read_at = Column(DateTime, nullable=True, comment="읽은 시각")
    
    # 메타 정보
    metadata = Column(JSON, nullable=True, comment="추가 메타데이터")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    room = relationship("ChatRoom", back_populates="messages")


class DriverPerformance(Base):
    """드라이버 성과"""
    __tablename__ = "driver_performances"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False, index=True)
    
    # 기간
    period_start = Column(DateTime, nullable=False, index=True, comment="기간 시작")
    period_end = Column(DateTime, nullable=False, index=True, comment="기간 종료")
    period_type = Column(String(20), nullable=False, comment="기간 타입 (DAILY/WEEKLY/MONTHLY)")
    
    # 배송 통계
    total_dispatches = Column(Integer, default=0, comment="총 배차 건수")
    completed_dispatches = Column(Integer, default=0, comment="완료 배차 건수")
    cancelled_dispatches = Column(Integer, default=0, comment="취소 배차 건수")
    completion_rate = Column(Float, default=0.0, comment="완료율 (%)")
    
    # 거리/시간
    total_distance = Column(Float, default=0.0, comment="총 이동 거리 (km)")
    total_duration = Column(Integer, default=0, comment="총 이동 시간 (분)")
    avg_delivery_time = Column(Integer, default=0, comment="평균 배송 시간 (분)")
    
    # 수익
    total_revenue = Column(Float, default=0.0, comment="총 수익")
    avg_revenue_per_dispatch = Column(Float, default=0.0, comment="배차당 평균 수익")
    
    # 평가
    avg_rating = Column(Float, default=0.0, comment="평균 평점")
    total_reviews = Column(Integer, default=0, comment="총 리뷰 수")
    
    # 랭킹
    rank = Column(Integer, nullable=True, comment="순위")
    
    # 메타 정보
    metadata = Column(JSON, nullable=True, comment="추가 통계 데이터")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    driver = relationship("Driver", back_populates="performances")


class NavigationSession(Base):
    """네비게이션 세션"""
    __tablename__ = "navigation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    dispatch_id = Column(Integer, ForeignKey("dispatches.id"), nullable=False, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False, index=True)
    
    # 경로 정보
    origin_lat = Column(Float, nullable=False, comment="출발지 위도")
    origin_lng = Column(Float, nullable=False, comment="출발지 경도")
    origin_address = Column(String(500), nullable=True, comment="출발지 주소")
    
    destination_lat = Column(Float, nullable=False, comment="목적지 위도")
    destination_lng = Column(Float, nullable=False, comment="목적지 경도")
    destination_address = Column(String(500), nullable=True, comment="목적지 주소")
    
    # 경로 데이터
    route_data = Column(JSON, nullable=True, comment="경로 데이터")
    distance = Column(Float, nullable=True, comment="거리 (km)")
    duration = Column(Integer, nullable=True, comment="예상 소요시간 (분)")
    
    # 세션 상태
    started_at = Column(DateTime, nullable=True, comment="시작 시각")
    completed_at = Column(DateTime, nullable=True, comment="완료 시각")
    is_active = Column(Boolean, default=True, comment="활성 여부")
    
    # 실시간 위치 추적
    current_lat = Column(Float, nullable=True, comment="현재 위도")
    current_lng = Column(Float, nullable=True, comment="현재 경도")
    last_location_update = Column(DateTime, nullable=True, comment="마지막 위치 업데이트")
    
    # 메타 정보
    metadata = Column(JSON, nullable=True, comment="추가 메타데이터")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dispatch = relationship("Dispatch", back_populates="navigation_sessions")
    driver = relationship("Driver", back_populates="navigation_sessions")


class DriverLocation(Base):
    """드라이버 실시간 위치"""
    __tablename__ = "driver_locations"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False, index=True)
    
    # 위치 정보
    latitude = Column(Float, nullable=False, comment="위도")
    longitude = Column(Float, nullable=False, comment="경도")
    accuracy = Column(Float, nullable=True, comment="정확도 (m)")
    altitude = Column(Float, nullable=True, comment="고도 (m)")
    
    # 이동 정보
    speed = Column(Float, nullable=True, comment="속도 (km/h)")
    heading = Column(Float, nullable=True, comment="방향 (도)")
    
    # 배터리 정보
    battery_level = Column(Integer, nullable=True, comment="배터리 잔량 (%)")
    
    # 메타 정보
    metadata = Column(JSON, nullable=True, comment="추가 메타데이터")
    
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    driver = relationship("Driver", back_populates="locations")
