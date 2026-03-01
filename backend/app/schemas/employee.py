"""
Employee Pydantic schemas for request/response validation
인사관리 시스템 스키마
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator
from enum import Enum


class EmployeeRoleEnum(str, Enum):
    """직급"""
    MASTER = "MASTER"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    DRIVER = "DRIVER"


class EmploymentTypeEnum(str, Enum):
    """고용 형태"""
    FULL_TIME = "FULL_TIME"
    CONTRACT = "CONTRACT"
    PART_TIME = "PART_TIME"
    DAILY = "DAILY"


# ==================== Base Schemas ====================

class EmployeeBase(BaseModel):
    """Employee 기본 스키마"""
    employee_code: str = Field(..., max_length=50, description="사원번호")
    name: str = Field(..., max_length=100, description="이름")
    name_en: Optional[str] = Field(None, max_length=100, description="영문명")
    phone: str = Field(..., max_length=20, description="전화번호")
    email: Optional[str] = Field(None, description="이메일")  # EmailStr → str로 변경 (pending.local 같은 도메인 허용)
    address: Optional[str] = Field(None, description="주소")
    emergency_contact: Optional[str] = Field(None, max_length=20, description="비상연락처")
    photo_url: Optional[str] = Field(None, max_length=255, description="사진 URL")
    
    role: EmployeeRoleEnum = Field(EmployeeRoleEnum.DRIVER, description="직급")
    employment_type: EmploymentTypeEnum = Field(EmploymentTypeEnum.FULL_TIME, description="고용 형태")
    department: Optional[str] = Field(None, max_length=100, description="부서")
    position: Optional[str] = Field(None, max_length=100, description="직책")
    
    hire_date: date = Field(..., description="입사일")
    resignation_date: Optional[date] = Field(None, description="퇴사일")
    work_start_time: str = Field("08:00", max_length=5, description="근무 시작 시간")
    work_end_time: str = Field("18:00", max_length=5, description="근무 종료 시간")
    max_work_hours: int = Field(10, ge=1, le=24, description="최대 근무 시간")
    
    license_type: Optional[str] = Field(None, max_length=20, description="운전면허 종류")
    license_number: Optional[str] = Field(None, max_length=50, description="운전면허 번호")
    license_issue_date: Optional[date] = Field(None, description="운전면허 발급일")
    
    has_cargo_license: bool = Field(False, description="화물운송자격증 보유 여부")
    cargo_license_number: Optional[str] = Field(None, max_length=50, description="화물운송자격증 번호")
    cargo_license_expiry_date: Optional[date] = Field(None, description="화물운송자격증 만료일")
    
    # 🆕 지게차 운전능력 필드
    can_drive_forklift: bool = Field(False, description="지게차 실제 운전 가능 여부")
    has_forklift_certificate: bool = Field(False, description="지게차 자격증 보유 여부")
    forklift_certificate_number: Optional[str] = Field(None, max_length=50, description="지게차 자격증 번호")
    forklift_certificate_issue_date: Optional[date] = Field(None, description="지게차 자격증 발급일")
    forklift_certificate_expiry_date: Optional[date] = Field(None, description="지게차 자격증 만료일")
    
    base_salary: Optional[int] = Field(None, ge=0, description="기본급")
    meal_allowance: int = Field(0, ge=0, description="식대")
    transportation_allowance: int = Field(0, ge=0, description="교통비")
    hazard_allowance: int = Field(0, ge=0, description="위험수당")
    bank_name: Optional[str] = Field(None, max_length=50, description="은행명")
    account_number: Optional[str] = Field(None, max_length=50, description="계좌번호")
    account_holder: Optional[str] = Field(None, max_length=100, description="예금주")
    
    notes: Optional[str] = Field(None, description="메모")
    is_active: bool = Field(True, description="재직 상태")
    
    @field_validator('work_start_time', 'work_end_time')
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """시간 형식 검증 (HH:MM)"""
        if v and ':' in v:
            parts = v.split(':')
            if len(parts) == 2:
                try:
                    h, m = int(parts[0]), int(parts[1])
                    if 0 <= h < 24 and 0 <= m < 60:
                        return v
                except ValueError:
                    pass
        raise ValueError(f"시간은 HH:MM 형식이어야 합니다 (예: 08:00). 입력값: {v}")


class EmployeeCreate(EmployeeBase):
    """Employee 생성 스키마"""
    pass


class EmployeeUpdate(BaseModel):
    """Employee 수정 스키마 (모든 필드 optional)"""
    employee_code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    name_en: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = Field(None, max_length=20)
    photo_url: Optional[str] = Field(None, max_length=255)
    
    role: Optional[EmployeeRoleEnum] = None
    employment_type: Optional[EmploymentTypeEnum] = None
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    
    hire_date: Optional[date] = None
    resignation_date: Optional[date] = None
    work_start_time: Optional[str] = Field(None, max_length=5)
    work_end_time: Optional[str] = Field(None, max_length=5)
    max_work_hours: Optional[int] = Field(None, ge=1, le=24)
    
    license_type: Optional[str] = Field(None, max_length=20)
    license_number: Optional[str] = Field(None, max_length=50)
    license_issue_date: Optional[date] = None
    
    has_cargo_license: Optional[bool] = None
    cargo_license_number: Optional[str] = Field(None, max_length=50)
    cargo_license_expiry_date: Optional[date] = None
    
    can_drive_forklift: Optional[bool] = None
    has_forklift_certificate: Optional[bool] = None
    forklift_certificate_number: Optional[str] = Field(None, max_length=50)
    forklift_certificate_issue_date: Optional[date] = None
    forklift_certificate_expiry_date: Optional[date] = None
    
    base_salary: Optional[int] = Field(None, ge=0)
    meal_allowance: Optional[int] = Field(None, ge=0)
    transportation_allowance: Optional[int] = Field(None, ge=0)
    hazard_allowance: Optional[int] = Field(None, ge=0)
    bank_name: Optional[str] = Field(None, max_length=50)
    account_number: Optional[str] = Field(None, max_length=50)
    account_holder: Optional[str] = Field(None, max_length=100)
    
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class EmployeeResponse(EmployeeBase):
    """Employee 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    # Computed fields
    forklift_status: str = Field(..., description="지게차 상태 (가능, 불가 등)")
    can_be_assigned_to_vehicle: bool = Field(..., description="차량 배정 가능 여부")
    days_until_forklift_expiry: Optional[int] = Field(None, description="지게차 자격증 만료까지 남은 일수")
    needs_forklift_training: bool = Field(..., description="지게차 교육 필요 여부")
    
    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    """Employee 목록 응답 스키마"""
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    page_size: int = Field(..., description="페이지 크기")
    items: list[EmployeeResponse] = Field(..., description="직원 목록")


# ==================== 운전자 특화 스키마 ====================

class DriverPoolItem(BaseModel):
    """운전자 풀 항목 (차량 배정용)"""
    id: int
    employee_code: str
    name: str
    phone: str
    license_type: Optional[str]
    has_cargo_license: bool
    can_drive_forklift: bool
    has_forklift_certificate: bool
    forklift_status: str
    work_hours: str  # "08:00-18:00"
    is_active: bool
    
    class Config:
        from_attributes = True


class ForkliftCapableDriversResponse(BaseModel):
    """지게차 가능 운전자 목록"""
    total: int
    with_certificate: int = Field(..., description="자격증 보유자 수")
    without_certificate: int = Field(..., description="자격증 미보유자 수")
    drivers: list[DriverPoolItem]


# ==================== 통계 스키마 ====================

class EmployeeStatistics(BaseModel):
    """직원 통계"""
    total_employees: int
    active_employees: int
    by_role: dict[str, int]  # {"DRIVER": 50, "ADMIN": 5, ...}
    by_employment_type: dict[str, int]
    drivers_with_cargo_license: int
    drivers_with_forklift_ability: int
    drivers_with_forklift_certificate: int
    drivers_needing_training: int  # 운전 가능 + 자격증 미보유


# ==================== 필터 스키마 ====================

class EmployeeFilterParams(BaseModel):
    """직원 필터 파라미터"""
    role: Optional[EmployeeRoleEnum] = None
    employment_type: Optional[EmploymentTypeEnum] = None
    is_active: Optional[bool] = None
    license_type: Optional[str] = None
    has_cargo_license: Optional[bool] = None
    can_drive_forklift: Optional[bool] = None
    has_forklift_certificate: Optional[bool] = None
    search: Optional[str] = Field(None, description="이름, 사번, 전화번호 검색")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
