"""
User model for authentication and authorization
"""
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class UserRole(str, PyEnum):
    """사용자 역할"""
    ADMIN = "admin"  # 관리자 (모든 권한)
    DISPATCHER = "dispatcher"  # 배차 담당자 (배차 관리)
    DRIVER = "driver"  # 기사 (배차 조회, 상태 업데이트)
    VIEWER = "viewer"  # 조회자 (읽기 전용)


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="사용자명")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="이메일")
    hashed_password = Column(String(255), nullable=False, comment="해시된 비밀번호")
    full_name = Column(String(100), nullable=True, comment="전체 이름")
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False, comment="사용자 역할")

    is_active = Column(Boolean, default=True, nullable=False, comment="활성 상태")
    is_superuser = Column(Boolean, default=False, nullable=False, comment="슈퍼유저 여부")
    
    # 새로운 필드 추가
    phone = Column(String(20), nullable=True, comment="전화번호")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    last_login = Column(DateTime(timezone=True), nullable=True, comment="마지막 로그인")

    # Relationships
    fcm_tokens = relationship("FCMToken", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    two_factor_auth = relationship("TwoFactorAuth", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role={self.role})>"
