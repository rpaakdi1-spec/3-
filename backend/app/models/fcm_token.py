"""
FCM 토큰 관리 모델
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class FCMToken(Base):
    """FCM 토큰 모델"""
    __tablename__ = "fcm_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), nullable=False, unique=True, index=True)
    device_type = Column(String(20), nullable=True)  # 'ios', 'android'
    device_id = Column(String(255), nullable=True)
    app_version = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="fcm_tokens")


class PushNotificationLog(Base):
    """푸시 알림 로그 모델"""
    __tablename__ = "push_notification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    token = Column(String(255), nullable=True)
    title = Column(String(255), nullable=False)
    body = Column(String(1000), nullable=False)
    data_json = Column(String(2000), nullable=True)
    notification_type = Column(String(50), nullable=True)  # 'dispatch_assigned', 'temperature_alert', etc.
    status = Column(String(20), default="sent")  # 'sent', 'failed', 'pending'
    error_message = Column(String(500), nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
