"""
Phase 7: Mobile Photo Storage Model
사진 저장 및 관리 모델
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class MobilePhoto(Base):
    """모바일 사진 저장 모델"""
    __tablename__ = "mobile_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 소유자 정보
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    dispatch_id = Column(Integer, ForeignKey("dispatches.id"), nullable=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True, index=True)
    
    # 사진 타입
    photo_type = Column(String(50), nullable=False, index=True)  # delivery_proof, signature, vehicle_inspection, incident, damage, other
    
    # 파일 정보
    file_path = Column(String(500), nullable=False)  # S3/MinIO 파일 경로
    thumbnail_path = Column(String(500), nullable=True)  # 썸네일 경로
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # 바이트 단위
    mime_type = Column(String(100), nullable=False)
    
    # 이미지 메타데이터
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    
    # 위치 정보 (사진 촬영 시 GPS)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(String(500), nullable=True)
    
    # 추가 정보
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # 메타데이터
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")
    dispatch = relationship("Dispatch")
    vehicle = relationship("Vehicle")
    
    def __repr__(self):
        return f"<MobilePhoto(id={self.id}, type={self.photo_type}, user_id={self.user_id})>"


class NotificationPreferences(Base):
    """사용자 알림 설정 모델"""
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # 알림 활성화 설정
    push_enabled = Column(Boolean, default=True)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    
    # 알림 타입별 설정
    new_dispatch_enabled = Column(Boolean, default=True)
    dispatch_updated_enabled = Column(Boolean, default=True)
    dispatch_cancelled_enabled = Column(Boolean, default=True)
    temperature_alert_enabled = Column(Boolean, default=True)
    emergency_alert_enabled = Column(Boolean, default=True)
    message_enabled = Column(Boolean, default=True)
    system_enabled = Column(Boolean, default=True)
    
    # 조용한 시간 (알림 받지 않음)
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5), nullable=True)  # "22:00"
    quiet_hours_end = Column(String(5), nullable=True)  # "08:00"
    
    # 알림 우선순위 필터
    min_priority = Column(String(20), default="normal")  # low, normal, high, urgent
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notification_preferences")
    
    def __repr__(self):
        return f"<NotificationPreferences(user_id={self.user_id}, push={self.push_enabled})>"


class MobileSession(Base):
    """모바일 세션 관리 (Refresh Token 저장)"""
    __tablename__ = "mobile_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 토큰 정보
    refresh_token_hash = Column(String(64), nullable=False, unique=True, index=True)  # SHA256 해시
    access_token_jti = Column(String(36), nullable=True)  # JWT ID
    
    # 디바이스 정보
    device_id = Column(String(255), nullable=False, index=True)
    device_type = Column(String(20), nullable=False)  # ios, android, web
    device_model = Column(String(100), nullable=True)
    os_version = Column(String(50), nullable=True)
    app_version = Column(String(20), nullable=True)
    
    # IP 및 위치
    ip_address = Column(String(45), nullable=True)
    country = Column(String(2), nullable=True)
    city = Column(String(100), nullable=True)
    
    # 상태
    is_active = Column(Boolean, default=True, index=True)
    is_revoked = Column(Boolean, default=False)
    
    # 시간 정보
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    last_used_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<MobileSession(user_id={self.user_id}, device={self.device_type}, active={self.is_active})>"
