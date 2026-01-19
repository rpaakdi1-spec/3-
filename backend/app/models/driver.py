from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from .base import Base, IDMixin, TimestampMixin


class Driver(Base, IDMixin, TimestampMixin):
    """기사 마스터 테이블"""
    
    __tablename__ = "drivers"
    
    # 기본 정보
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False, comment="기사코드")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="기사명")
    
    # 연락처
    phone: Mapped[str] = mapped_column(String(20), nullable=False, comment="전화번호")
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(20), comment="비상연락처")
    
    # 근무 정보
    work_start_time: Mapped[str] = mapped_column(String(5), default="08:00", comment="근무시작시간(HH:MM)")
    work_end_time: Mapped[str] = mapped_column(String(5), default="18:00", comment="근무종료시간(HH:MM)")
    max_work_hours: Mapped[int] = mapped_column(default=10, comment="최대 근무시간")
    
    # 자격증
    license_number: Mapped[Optional[str]] = mapped_column(String(50), comment="운전면허번호")
    license_type: Mapped[Optional[str]] = mapped_column(String(20), comment="면허 종류")
    
    # 메모
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="특이사항")
    
    # 활성화 상태
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="사용 여부")
    
    # Relationships
    dispatches = relationship("Dispatch", back_populates="driver")
    
    def __repr__(self):
        return f"<Driver(code={self.code}, name={self.name})>"
