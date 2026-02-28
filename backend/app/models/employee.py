"""
Employee model for HR management system
화물운수업 통합 인사관리 모델
"""
from enum import Enum as PyEnum
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Enum, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class EmployeeRole(str, PyEnum):
    """직급"""
    MASTER = "MASTER"  # 총괄 (최상위 관리자)
    ADMIN = "ADMIN"  # 관리자 (운영사원)
    MANAGER = "MANAGER"  # 현장관리자
    DRIVER = "DRIVER"  # 운전직


class EmploymentType(str, PyEnum):
    """고용 형태"""
    FULL_TIME = "FULL_TIME"  # 정규직
    CONTRACT = "CONTRACT"  # 계약직
    PART_TIME = "PART_TIME"  # 파트타임
    DAILY = "DAILY"  # 일용직


class Employee(Base):
    """
    통합 인사 관리 모델
    
    화물운수업에 최적화된 인사 정보를 관리합니다.
    운전직 사원은 자동으로 운전자 풀에 연동됩니다.
    """
    __tablename__ = "employees"

    # ==================== 기본 식별 정보 ====================
    id = Column(Integer, primary_key=True, index=True, comment="ID")
    employee_code = Column(
        String(50), 
        unique=True, 
        nullable=False, 
        index=True, 
        comment="사원번호 (예: D001, A001)"
    )
    
    # ==================== 개인 정보 ====================
    name = Column(String(100), nullable=False, index=True, comment="이름")
    name_en = Column(String(100), nullable=True, comment="영문명")
    phone = Column(String(20), nullable=False, index=True, comment="전화번호")
    email = Column(String(100), nullable=True, comment="이메일")
    address = Column(Text, nullable=True, comment="주소")
    emergency_contact = Column(String(20), nullable=True, comment="비상연락처")
    photo_url = Column(String(255), nullable=True, comment="사진 URL")
    
    # ==================== 조직 정보 ====================
    role = Column(
        Enum(EmployeeRole), 
        default=EmployeeRole.DRIVER, 
        nullable=False,
        index=True,
        comment="직급"
    )
    employment_type = Column(
        Enum(EmploymentType),
        default=EmploymentType.FULL_TIME,
        nullable=False,
        comment="고용 형태"
    )
    department = Column(String(100), nullable=True, comment="부서")
    position = Column(String(100), nullable=True, comment="직책")
    
    # ==================== 근무 정보 ====================
    hire_date = Column(Date, nullable=False, comment="입사일")
    resignation_date = Column(Date, nullable=True, comment="퇴사일")
    work_start_time = Column(String(5), default="08:00", nullable=False, comment="근무 시작 시간 (HH:MM)")
    work_end_time = Column(String(5), default="18:00", nullable=False, comment="근무 종료 시간 (HH:MM)")
    max_work_hours = Column(Integer, default=10, nullable=False, comment="최대 근무 시간")
    
    # ==================== 운전면허 정보 ====================
    license_type = Column(
        String(20), 
        nullable=True, 
        index=True,
        comment="운전면허 종류 (1종 대형, 1종 보통, 2종)"
    )
    license_number = Column(String(50), nullable=True, comment="운전면허 번호")
    license_issue_date = Column(Date, nullable=True, comment="운전면허 발급일")
    
    # ==================== 화물운송자격증 ====================
    has_cargo_license = Column(
        Boolean, 
        default=False, 
        nullable=False,
        index=True,
        comment="화물운송자격증 보유 여부"
    )
    cargo_license_number = Column(String(50), nullable=True, comment="화물운송자격증 번호")
    cargo_license_expiry_date = Column(Date, nullable=True, comment="화물운송자격증 만료일")
    
    # ==================== 🆕 지게차 운전능력 (핵심 신규 필드) ====================
    # 자격증과 별개로 실제 운전 가능 여부를 관리
    can_drive_forklift = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="지게차 실제 운전 가능 여부 (자격증 무관, 배차용)"
    )
    has_forklift_certificate = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="지게차운전기능사 자격증 보유 여부 (법적 요건)"
    )
    forklift_certificate_number = Column(
        String(50), 
        nullable=True, 
        comment="지게차 자격증 번호"
    )
    forklift_certificate_issue_date = Column(
        Date, 
        nullable=True, 
        comment="지게차 자격증 발급일"
    )
    forklift_certificate_expiry_date = Column(
        Date, 
        nullable=True,
        comment="지게차 자격증 만료일"
    )
    
    # ==================== 급여 정보 ====================
    base_salary = Column(Integer, nullable=True, comment="기본급")
    meal_allowance = Column(Integer, default=0, comment="식대")
    transportation_allowance = Column(Integer, default=0, comment="교통비")
    hazard_allowance = Column(Integer, default=0, comment="위험수당")
    bank_name = Column(String(50), nullable=True, comment="은행명")
    account_number = Column(String(50), nullable=True, comment="계좌번호")
    account_holder = Column(String(100), nullable=True, comment="예금주")
    
    # ==================== 메모 및 비고 ====================
    notes = Column(Text, nullable=True, comment="메모")
    
    # ==================== 시스템 필드 ====================
    is_active = Column(
        Boolean, 
        default=True, 
        nullable=False,
        index=True,
        comment="재직 상태 (true: 재직, false: 퇴사)"
    )
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        comment="등록일시"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="수정일시"
    )
    created_by = Column(
        Integer,
        ForeignKey('users.id'),
        nullable=True,
        comment="등록자 ID"
    )
    updated_by = Column(
        Integer,
        ForeignKey('users.id'),
        nullable=True,
        comment="수정자 ID"
    )
    
    # ==================== Relationships ====================
    creator = relationship(
        "User",
        foreign_keys=[created_by],
        lazy="joined"
    )
    updater = relationship(
        "User",
        foreign_keys=[updated_by],
        lazy="joined"
    )
    
    # ==================== Indexes ====================
    __table_args__ = (
        Index('idx_employee_name_phone', 'name', 'phone'),  # 이름+전화번호 복합 검색
        Index('idx_employee_role_active', 'role', 'is_active'),  # 직급별 재직자 조회
        Index('idx_employee_forklift', 'can_drive_forklift', 'has_forklift_certificate'),  # 지게차 능력 필터
        Index('idx_employee_hire_date', 'hire_date'),  # 입사일 정렬
    )
    
    def __repr__(self):
        return f"<Employee(code='{self.employee_code}', name='{self.name}', role={self.role})>"
    
    @property
    def full_name_with_code(self) -> str:
        """사원번호와 이름 조합"""
        return f"{self.employee_code} | {self.name}"
    
    @property
    def is_driver(self) -> bool:
        """운전직 여부"""
        return self.role == EmployeeRole.DRIVER
    
    @property
    def can_be_assigned_to_vehicle(self) -> bool:
        """차량 배정 가능 여부 (운전직 + 재직 중 + 운전면허 보유)"""
        return (
            self.is_driver and
            self.is_active and
            self.license_type is not None
        )
    
    @property
    def forklift_status(self) -> str:
        """
        지게차 상태 문자열
        
        Returns:
            - "가능 (자격증 보유)": 운전 가능 + 자격증 보유
            - "가능 (자격증 미보유)": 운전 가능 + 자격증 미보유
            - "자격증만 보유": 운전 불가 + 자격증 보유
            - "불가": 운전 불가 + 자격증 미보유
        """
        if self.can_drive_forklift and self.has_forklift_certificate:
            return "가능 (자격증 보유)"
        elif self.can_drive_forklift and not self.has_forklift_certificate:
            return "가능 (자격증 미보유)"
        elif not self.can_drive_forklift and self.has_forklift_certificate:
            return "자격증만 보유"
        else:
            return "불가"
    
    @property
    def days_until_forklift_expiry(self) -> int | None:
        """지게차 자격증 만료까지 남은 일수"""
        if not self.forklift_certificate_expiry_date:
            return None
        delta = self.forklift_certificate_expiry_date - date.today()
        return delta.days
    
    @property
    def needs_forklift_training(self) -> bool:
        """지게차 교육 필요 여부 (운전 가능하지만 자격증 미보유)"""
        return self.can_drive_forklift and not self.has_forklift_certificate
