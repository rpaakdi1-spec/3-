"""
Authentication schemas
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.user import UserRole


class UserBase(BaseModel):
    """사용자 기본 스키마"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.VIEWER


class UserCreate(UserBase):
    """사용자 생성 스키마"""
    password: str = Field(..., min_length=6)
    is_superuser: bool = False


class UserUpdate(BaseModel):
    """사용자 수정 스키마"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    """사용자 응답 스키마"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """토큰 응답"""
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    """토큰 데이터"""
    username: Optional[str] = None
    role: Optional[str] = None


class UserListResponse(BaseModel):
    """사용자 목록 응답"""
    total: int
    items: list[UserResponse]


class ChangePassword(BaseModel):
    """비밀번호 변경 스키마"""
    old_password: str
    new_password: str = Field(..., min_length=6)
