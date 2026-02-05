"""
Driver Schedule API
드라이버 근무표 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, timedelta, datetime
from loguru import logger

from app.core.database import get_db
from app.models.driver_schedule import DriverSchedule, ScheduleType
from app.models.driver import Driver
from app.schemas.driver_schedule import (
    DriverScheduleCreate,
    DriverScheduleUpdate,
    DriverScheduleResponse,
    DriverScheduleListResponse,
    DriverScheduleApprovalRequest,
    DriverAvailabilityResponse,
    BulkScheduleCreateRequest,
)

router = APIRouter()


@router.get("/", response_model=DriverScheduleListResponse)
def get_driver_schedules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    driver_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    schedule_type: Optional[ScheduleType] = None,
    is_available: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """드라이버 근무표 목록 조회"""
    query = db.query(DriverSchedule)
    
    if driver_id:
        query = query.filter(DriverSchedule.driver_id == driver_id)
    if start_date:
        query = query.filter(DriverSchedule.schedule_date >= start_date)
    if end_date:
        query = query.filter(DriverSchedule.schedule_date <= end_date)
    if schedule_type:
        query = query.filter(DriverSchedule.schedule_type == schedule_type)
    if is_available is not None:
        query = query.filter(DriverSchedule.is_available == is_available)
    
    total = query.count()
    items = query.order_by(DriverSchedule.schedule_date.desc()).offset(skip).limit(limit).all()
    
    return {"total": total, "items": items}


@router.get("/{schedule_id}", response_model=DriverScheduleResponse)
def get_driver_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """드라이버 근무표 단일 조회"""
    schedule = db.query(DriverSchedule).filter(DriverSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="근무표를 찾을 수 없습니다")
    
    return schedule


@router.post("/", response_model=DriverScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_driver_schedule(
    schedule_data: DriverScheduleCreate,
    db: Session = Depends(get_db)
):
    """드라이버 근무표 생성"""
    try:
        # 기사 존재 확인
        driver = db.query(Driver).filter(Driver.id == schedule_data.driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="기사를 찾을 수 없습니다")
        
        # 중복 체크
        existing = db.query(DriverSchedule).filter(
            DriverSchedule.driver_id == schedule_data.driver_id,
            DriverSchedule.schedule_date == schedule_data.schedule_date
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"{schedule_data.schedule_date} 날짜에 이미 일정이 등록되어 있습니다"
            )
        
        schedule = DriverSchedule(**schedule_data.model_dump())
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        
        logger.info(f"Created driver schedule: Driver {schedule.driver_id}, Date {schedule.schedule_date}")
        
        return schedule
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating driver schedule: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="근무표 생성 중 오류가 발생했습니다")


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def create_bulk_schedules(
    request: BulkScheduleCreateRequest,
    db: Session = Depends(get_db)
):
    """일괄 근무표 생성
    
    지정된 기간 동안 특정 요일에만 근무표를 생성합니다.
    """
    try:
        # 기사 존재 확인
        driver = db.query(Driver).filter(Driver.id == request.driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="기사를 찾을 수 없습니다")
        
        created_count = 0
        skipped_count = 0
        current_date = request.start_date
        
        while current_date <= request.end_date:
            # 요일 확인 (0=월요일, 6=일요일)
            weekday = current_date.weekday()
            
            if weekday in request.weekdays:
                # 중복 체크
                existing = db.query(DriverSchedule).filter(
                    DriverSchedule.driver_id == request.driver_id,
                    DriverSchedule.schedule_date == current_date
                ).first()
                
                if not existing:
                    schedule = DriverSchedule(
                        driver_id=request.driver_id,
                        schedule_date=current_date,
                        schedule_type=request.schedule_type,
                        start_time=request.start_time,
                        end_time=request.end_time,
                        is_available=(request.schedule_type == ScheduleType.WORK),
                        notes=request.notes
                    )
                    db.add(schedule)
                    created_count += 1
                else:
                    skipped_count += 1
            
            current_date += timedelta(days=1)
        
        db.commit()
        
        logger.info(
            f"Bulk created driver schedules: Driver {request.driver_id}, "
            f"Created {created_count}, Skipped {skipped_count}"
        )
        
        return {
            "created": created_count,
            "skipped": skipped_count,
            "message": f"{created_count}개의 근무표가 생성되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating bulk schedules: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="일괄 근무표 생성 중 오류가 발생했습니다")


@router.put("/{schedule_id}", response_model=DriverScheduleResponse)
def update_driver_schedule(
    schedule_id: int,
    schedule_data: DriverScheduleUpdate,
    db: Session = Depends(get_db)
):
    """드라이버 근무표 수정"""
    schedule = db.query(DriverSchedule).filter(DriverSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="근무표를 찾을 수 없습니다")
    
    try:
        update_data = schedule_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(schedule, field, value)
        
        db.commit()
        db.refresh(schedule)
        
        logger.info(f"Updated driver schedule: ID {schedule.id}")
        
        return schedule
        
    except Exception as e:
        logger.error(f"Error updating driver schedule: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="근무표 수정 중 오류가 발생했습니다")


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_driver_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """드라이버 근무표 삭제"""
    schedule = db.query(DriverSchedule).filter(DriverSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="근무표를 찾을 수 없습니다")
    
    try:
        db.delete(schedule)
        db.commit()
        
        logger.info(f"Deleted driver schedule: ID {schedule.id}")
        
    except Exception as e:
        logger.error(f"Error deleting driver schedule: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="근무표 삭제 중 오류가 발생했습니다")


@router.post("/{schedule_id}/approve", response_model=DriverScheduleResponse)
def approve_driver_schedule(
    schedule_id: int,
    approval: DriverScheduleApprovalRequest,
    user_id: int = Query(..., description="승인자 사용자 ID"),
    db: Session = Depends(get_db)
):
    """근무표 승인/거부"""
    schedule = db.query(DriverSchedule).filter(DriverSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="근무표를 찾을 수 없습니다")
    
    if not schedule.requires_approval:
        raise HTTPException(status_code=400, detail="승인이 필요하지 않은 일정입니다")
    
    try:
        schedule.is_approved = approval.is_approved
        schedule.approved_by = user_id
        schedule.approval_notes = approval.approval_notes
        
        db.commit()
        db.refresh(schedule)
        
        status_text = "승인" if approval.is_approved else "거부"
        logger.info(f"{status_text} driver schedule: ID {schedule.id}, User {user_id}")
        
        return schedule
        
    except Exception as e:
        logger.error(f"Error approving driver schedule: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="승인 처리 중 오류가 발생했습니다")


@router.get("/availability/{target_date}", response_model=list[DriverAvailabilityResponse])
def get_available_drivers(
    target_date: date,
    db: Session = Depends(get_db)
):
    """특정 날짜의 가용 기사 목록 조회
    
    해당 날짜에 근무하고 배차 가능한 기사들을 반환합니다.
    """
    # 모든 활성 기사 조회
    drivers = db.query(Driver).filter(Driver.is_active == True).all()
    
    result = []
    for driver in drivers:
        # 해당 날짜의 근무표 조회
        schedule = db.query(DriverSchedule).filter(
            DriverSchedule.driver_id == driver.id,
            DriverSchedule.schedule_date == target_date
        ).first()
        
        if schedule:
            # 근무표가 있는 경우
            is_available = schedule.is_available and schedule.schedule_type == ScheduleType.WORK
            work_hours = (schedule.start_time, schedule.end_time) if is_available else None
            
            result.append(DriverAvailabilityResponse(
                driver_id=driver.id,
                driver_name=driver.name,
                schedule_date=target_date,
                is_available=is_available,
                schedule_type=schedule.schedule_type,
                work_hours=work_hours
            ))
        else:
            # 근무표가 없는 경우 - 기본 근무시간 사용
            result.append(DriverAvailabilityResponse(
                driver_id=driver.id,
                driver_name=driver.name,
                schedule_date=target_date,
                is_available=True,
                schedule_type=ScheduleType.WORK,
                work_hours=(driver.work_start_time, driver.work_end_time)
            ))
    
    return result
