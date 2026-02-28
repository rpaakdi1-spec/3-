"""
Pending Employee model - 회원가입 시 임시로 저장하는 인사카드 정보
"""
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class PendingEmployee(Base):
    """
    회원가입 시 입력한 인사카드 정보를 임시 저장
    승인 시 Employee 테이블로 이동
    """
    __tablename__ = "pending_employees"

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="연결된 사용자 ID")
    
    # 기본 식별 정보
    employee_code = Column(String(50), nullable=False, index=True, comment="사원번호")
    
    # 개인 정보
    name = Column(String(100), nullable=False, comment="이름")
    name_en = Column(String(100), nullable=True, comment="영문명")
    phone = Column(String(20), nullable=False, comment="전화번호")
    email = Column(String(100), nullable=True, comment="이메일")
    address = Column(Text, nullable=True, comment="주소")
    emergency_contact = Column(String(20), nullable=True, comment="비상연락처")
    
    # 조직 정보
    role = Column(String(20), nullable=False, comment="직급")
    employment_type = Column(String(20), nullable=False, comment="고용 형태")
    department = Column(String(100), nullable=True, comment="부서")
    position = Column(String(100), nullable=True, comment="직책")
    
    # 근무 정보
    hire_date = Column(Date, nullable=False, comment="입사일")
    work_start_time = Column(String(5), default="08:00", comment="근무 시작 시간")
    work_end_time = Column(String(5), default="18:00", comment="근무 종료 시간")
    max_work_hours = Column(Integer, default=10, comment="최대 근무 시간")
    
    # 운전면허 정보
    license_type = Column(String(20), nullable=True, comment="운전면허 종류")
    license_number = Column(String(50), nullable=True, comment="운전면허 번호")
    license_issue_date = Column(Date, nullable=True, comment="운전면허 발급일")
    
    # 화물운송자격증
    has_cargo_license = Column(Boolean, default=False, comment="화물운송자격증 보유")
    cargo_license_number = Column(String(50), nullable=True, comment="화물운송자격증 번호")
    cargo_license_issue_date = Column(Date, nullable=True, comment="화물운송자격증 발급일")
    cargo_license_expiry_date = Column(Date, nullable=True, comment="화물운송자격증 만료일")
    
    # 지게차 자격
    can_drive_forklift = Column(Boolean, default=False, comment="지게차 운전 가능")
    has_forklift_certificate = Column(Boolean, default=False, comment="지게차 자격증 보유")
    forklift_certificate_number = Column(String(50), nullable=True, comment="지게차 자격증 번호")
    forklift_certificate_issue_date = Column(Date, nullable=True, comment="지게차 자격증 발급일")
    forklift_certificate_expiry_date = Column(Date, nullable=True, comment="지게차 자격증 만료일")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    
    # Relationship
    user = relationship("User", foreign_keys=[user_id], backref="pending_employee_data")
    
    def __repr__(self):
        return f"<PendingEmployee(id={self.id}, name='{self.name}', employee_code='{self.employee_code}')>"
