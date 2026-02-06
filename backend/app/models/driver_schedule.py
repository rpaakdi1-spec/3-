"""
Driver Schedule Model
드라이버 근무표 모델 - 근무 일정 및 가용성 관리
"""
from sqlalchemy import Column, Integer, ForeignKey, Date, String, Boolean, Text, Time, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import date, time
from enum import Enum
from app.models.base import Base


class ScheduleType(str, Enum):
    """근무 일정 유형"""
    WORK = "근무"
    DAY_OFF = "휴무"
    VACATION = "휴가"
    SICK_LEAVE = "병가"
    TRAINING = "교육"


class DriverSchedule(Base):
    """드라이버 근무표 모델"""
    __tablename__ = "driver_schedules"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Driver
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False, index=True, comment="기사 ID")
    
    # Schedule Date
    schedule_date = Column(Date, nullable=False, index=True, comment="일정 날짜")
    
    # Schedule Type
    schedule_type = Column(
        SQLEnum(ScheduleType),
        nullable=False,
        default=ScheduleType.WORK,
        comment="일정 유형"
    )
    
    # Work Hours (for WORK type)
    start_time = Column(Time, comment="근무 시작 시간")
    end_time = Column(Time, comment="근무 종료 시간")
    
    # Availability
    is_available = Column(Boolean, default=True, index=True, comment="배차 가능 여부")
    
    # Notes
    notes = Column(Text, comment="비고")
    
    # Approval (for leave requests)
    requires_approval = Column(Boolean, default=False, comment="승인 필요 여부")
    is_approved = Column(Boolean, default=None, comment="승인 여부 (None: 대기, True: 승인, False: 거부)")
    approved_by = Column(Integer, ForeignKey("users.id"), comment="승인자 ID")
    approval_notes = Column(Text, comment="승인 메모")
    
    # Timestamps
    created_at = Column(Date, server_default=func.now(), comment="생성 시간")
    updated_at = Column(Date, onupdate=func.now(), comment="수정 시간")
    
    # Relationships
    driver = relationship("Driver", back_populates="schedules")
    
    def __repr__(self):
        return f"<DriverSchedule(driver_id={self.driver_id}, date={self.schedule_date}, type={self.schedule_type})>"
    
    def is_working_day(self) -> bool:
        """근무일 여부 확인"""
        return self.schedule_type == ScheduleType.WORK and self.is_available
    
    def get_work_hours(self) -> tuple:
        """근무 시간 반환 (start_time, end_time)"""
        if self.schedule_type == ScheduleType.WORK:
            return (self.start_time, self.end_time)
        return (None, None)
