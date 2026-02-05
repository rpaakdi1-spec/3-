"""
Driver Schedule Schemas
드라이버 근무표 Pydantic 스키마
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time
from enum import Enum


class ScheduleType(str, Enum):
    """근무 일정 유형"""
    WORK = "근무"
    DAY_OFF = "휴무"
    VACATION = "휴가"
    SICK_LEAVE = "병가"
    TRAINING = "교육"


class DriverScheduleBase(BaseModel):
    """드라이버 근무표 기본 스키마"""
    driver_id: int = Field(..., description="기사 ID")
    schedule_date: date = Field(..., description="일정 날짜")
    schedule_type: ScheduleType = Field(ScheduleType.WORK, description="일정 유형")
    start_time: Optional[str] = Field(None, description="근무 시작 시간 (HH:MM)")
    end_time: Optional[str] = Field(None, description="근무 종료 시간 (HH:MM)")
    is_available: bool = Field(True, description="배차 가능 여부")
    notes: Optional[str] = Field(None, description="비고")
    requires_approval: bool = Field(False, description="승인 필요 여부")


class DriverScheduleCreate(DriverScheduleBase):
    """드라이버 근무표 생성"""
    pass


class DriverScheduleUpdate(BaseModel):
    """드라이버 근무표 수정"""
    schedule_type: Optional[ScheduleType] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_available: Optional[bool] = None
    notes: Optional[str] = None
    requires_approval: Optional[bool] = None


class DriverScheduleResponse(DriverScheduleBase):
    """드라이버 근무표 응답"""
    id: int
    is_approved: Optional[bool]
    approved_by: Optional[int]
    approval_notes: Optional[str]
    created_at: date
    updated_at: Optional[date]
    
    class Config:
        from_attributes = True


class DriverScheduleListResponse(BaseModel):
    """드라이버 근무표 목록 응답"""
    total: int
    items: list[DriverScheduleResponse]


class DriverScheduleApprovalRequest(BaseModel):
    """근무표 승인 요청"""
    is_approved: bool = Field(..., description="승인 여부")
    approval_notes: Optional[str] = Field(None, description="승인 메모")


class DriverAvailabilityResponse(BaseModel):
    """기사 가용성 응답"""
    driver_id: int
    driver_name: str
    schedule_date: date
    is_available: bool
    schedule_type: ScheduleType
    work_hours: Optional[tuple[str, str]]  # (start_time, end_time)


class BulkScheduleCreateRequest(BaseModel):
    """일괄 근무표 생성 요청"""
    driver_id: int
    start_date: date
    end_date: date
    schedule_type: ScheduleType = ScheduleType.WORK
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    weekdays: list[int] = Field(..., description="요일 (0=월요일, 6=일요일)")
    notes: Optional[str] = None
