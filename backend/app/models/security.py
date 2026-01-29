"""
Two-Factor Authentication Models
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class TwoFactorAuth(Base):
    """2FA 설정 모델"""
    __tablename__ = "two_factor_auth"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    secret_key = Column(String(32), nullable=False)  # Base32 encoded secret
    is_enabled = Column(Boolean, default=False)
    backup_codes = Column(String(500), nullable=True)  # JSON array of backup codes
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="two_factor_auth")


class TwoFactorLog(Base):
    """2FA 사용 로그"""
    __tablename__ = "two_factor_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # 'enabled', 'disabled', 'verified', 'failed'
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    success = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")


class AuditLog(Base):
    """감사 로그 (모든 중요한 액션 기록)"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # 'login', 'logout', 'create_order', 'delete_dispatch', etc.
    resource_type = Column(String(50), nullable=True)  # 'order', 'dispatch', 'user', etc.
    resource_id = Column(Integer, nullable=True)
    details = Column(String(1000), nullable=True)  # JSON details
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    status = Column(String(20), default="success")  # 'success', 'failed', 'blocked'
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User")


class SecurityAlert(Base):
    """보안 알림 (의심스러운 활동 감지)"""
    __tablename__ = "security_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    alert_type = Column(String(50), nullable=False)  # 'brute_force', 'suspicious_login', 'permission_escalation', etc.
    severity = Column(String(20), default="medium")  # 'low', 'medium', 'high', 'critical'
    description = Column(String(500), nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    resolver = relationship("User", foreign_keys=[resolved_by])
