"""
Authentication schemas
"""
from __future__ import annotations
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.user import UserRole
from app.models.employee import EmployeeRole, EmploymentType


class UserBase(BaseModel):
    """사용자 기본 스키마"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    role: UserRole = UserRole.VIEWER


class UserCreate(UserBase):
    """사용자 생성 스키마"""
    password: str = Field(..., min_length=6)
    is_superuser: bool = False


class UserUpdate(BaseModel):
    """사용자 수정 스키마"""
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    
    # Pending Employee 정보 수정 (승인 전 사용자)
    name_en: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    employment_type: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    hire_date: Optional[date] = None
    
    # 운전면허
    license_type: Optional[str] = None
    license_number: Optional[str] = None
    license_issue_date: Optional[date] = None
    
    # 화물운송자격증
    has_cargo_license: Optional[bool] = None
    cargo_license_number: Optional[str] = None
    cargo_license_issue_date: Optional[date] = None
    cargo_license_expiry_date: Optional[date] = None
    
    # 지게차
    can_drive_forklift: Optional[bool] = None
    has_forklift_certificate: Optional[bool] = None
    forklift_certificate_number: Optional[str] = None
    forklift_certificate_issue_date: Optional[date] = None
    forklift_certificate_expiry_date: Optional[date] = None


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


class UserStatusUpdate(BaseModel):
    """사용자 상태 변경 스키마"""
    is_active: bool


class PendingEmployeeData(BaseModel):
    """승인 대기 중인 인사카드 정보"""
    employee_code: str
    name: str
    name_en: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    role: str
    employment_type: str
    department: Optional[str] = None
    position: Optional[str] = None
    hire_date: date
    license_type: Optional[str] = None
    has_cargo_license: bool
    can_drive_forklift: bool
    has_forklift_certificate: bool
    
    model_config = ConfigDict(from_attributes=True)


class UserResponseWithPending(UserResponse):
    """사용자 응답 스키마 (PendingEmployee 정보 포함)"""
    pending_employee: Optional[PendingEmployeeData] = None


class SignupRequest(BaseModel):
    """회원가입 요청 스키마 (인사카드 양식 전체 정보)"""
    # 계정 정보
    username: str = Field(..., min_length=3, max_length=50, description="로그인 사용자명")
    password: str = Field(..., min_length=6, description="로그인 비밀번호")
    role: UserRole = Field(default=UserRole.DRIVER, description="시스템 권한")
    
    # 기본 인적사항
    name: str = Field(..., min_length=2, max_length=100, description="이름")
    name_en: Optional[str] = Field(None, max_length=100, description="영문명")
    phone: str = Field(..., min_length=12, max_length=13, description="전화번호 (000-0000-0000)")
    email: Optional[str] = Field(None, description="이메일 주소 (선택사항)")
    address: Optional[str] = Field(None, description="주소")
    emergency_contact: Optional[str] = Field(None, max_length=13, description="비상연락처")
    
    # 조직 정보
    employment_type: EmploymentType = Field(default=EmploymentType.FULL_TIME, description="고용 형태")
    department: Optional[str] = Field(None, max_length=100, description="부서")
    position: Optional[str] = Field(None, max_length=100, description="직책")
    
    # 근무 정보
    hire_date: date = Field(..., description="입사일")
    
    # 운전면허 정보
    license_type: Optional[str] = Field(None, max_length=20, description="운전면허 종류")
    license_number: Optional[str] = Field(None, max_length=50, description="운전면허 번호")
    license_issue_date: Optional[date] = Field(None, description="운전면허 발급일")
    
    # 화물운송자격증
    has_cargo_license: bool = Field(default=False, description="화물운송자격증 보유 여부")
    cargo_license_number: Optional[str] = Field(None, max_length=50, description="화물운송자격증 번호")
    cargo_license_issue_date: Optional[date] = Field(None, description="화물운송자격증 발급일")
    cargo_license_expiry_date: Optional[date] = Field(None, description="화물운송자격증 만료일")
    
    # 지게차 자격
    can_drive_forklift: bool = Field(default=False, description="지게차 운전 가능 여부")
    has_forklift_certificate: bool = Field(default=False, description="지게차 운전 자격증 보유")
    forklift_certificate_number: Optional[str] = Field(None, max_length=50, description="지게차 자격증 번호")
    forklift_certificate_issue_date: Optional[date] = Field(None, description="지게차 자격증 발급일")
    forklift_certificate_expiry_date: Optional[date] = Field(None, description="지게차 자격증 만료일")
    

class ApprovalRequest(BaseModel):
    """승인 요청 스키마"""
    user_id: int
    approved: bool
    rejection_reason: Optional[str] = None
