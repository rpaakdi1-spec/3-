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
    phone: Optional[str] = Field(None, max_length=20)
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
    approval_status: str = "pending"
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
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


class SignupRequest(BaseModel):
    """회원가입 요청 스키마 (인사카드 정보 연동)"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: EmailStr
    full_name: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=10, max_length=20)
    employee_code: str = Field(..., description="직원번호 (인사카드 연동용)")
    role: UserRole = UserRole.DRIVER
    

class ApprovalRequest(BaseModel):
    """승인 요청 스키마"""
    user_id: int
    approved: bool
    rejection_reason: Optional[str] = None
