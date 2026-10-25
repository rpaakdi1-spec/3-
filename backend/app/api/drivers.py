from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.database import get_db
from app.models.driver import Driver

router = APIRouter()


# Pydantic schemas
class DriverBase(BaseModel):
    code: str = Field(..., description="기사코드")
    name: str = Field(..., description="기사명")
    phone: str = Field(..., description="전화번호")
    emergency_contact: Optional[str] = Field(None, description="비상연락처")
    work_start_time: str = Field(default="08:00", description="근무시작시간")
    work_end_time: str = Field(default="18:00", description="근무종료시간")
    max_work_hours: int = Field(default=10, description="최대 근무시간")
    license_number: Optional[str] = Field(None, description="운전면허번호")
    license_type: Optional[str] = Field(None, description="면허 종류")
    notes: Optional[str] = Field(None, description="특이사항")
    is_active: bool = Field(default=True, description="사용 여부")


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    work_start_time: Optional[str] = None
    work_end_time: Optional[str] = None
    max_work_hours: Optional[int] = None
    license_number: Optional[str] = None
    license_type: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class DriverResponse(DriverBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=List[DriverResponse])
def list_drivers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    운전자 목록 조회
    
    - **skip**: 건너뛸 레코드 수
    - **limit**: 최대 반환 레코드 수
    - **search**: 검색어 (이름, 전화번호, 코드)
    - **is_active**: 활성화 상태 필터
    """
    query = db.query(Driver)
    
    # Apply filters
    if search:
        search_filter = or_(
            Driver.name.ilike(f"%{search}%"),
            Driver.phone.ilike(f"%{search}%"),
            Driver.code.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    if is_active is not None:
        query = query.filter(Driver.is_active == is_active)
    
    # Order by code
    query = query.order_by(Driver.code)
    
    # Apply pagination
    drivers = query.offset(skip).limit(limit).all()
    
    return drivers


@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(driver_id: int, db: Session = Depends(get_db)):
    """운전자 상세 조회"""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@router.post("", response_model=DriverResponse, status_code=201)
def create_driver(driver_data: DriverCreate, db: Session = Depends(get_db)):
    """운전자 생성"""
    # Check if code already exists
    existing = db.query(Driver).filter(Driver.code == driver_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Driver with code {driver_data.code} already exists")
    
    # Check if phone already exists
    existing_phone = db.query(Driver).filter(Driver.phone == driver_data.phone).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail=f"Driver with phone {driver_data.phone} already exists")
    
    driver = Driver(**driver_data.model_dump())
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@router.put("/{driver_id}", response_model=DriverResponse)
def update_driver(driver_id: int, driver_data: DriverUpdate, db: Session = Depends(get_db)):
    """운전자 수정"""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Update fields
    update_data = driver_data.model_dump(exclude_unset=True)
    
    # Check phone uniqueness if being updated
    if "phone" in update_data:
        existing_phone = db.query(Driver).filter(
            and_(Driver.phone == update_data["phone"], Driver.id != driver_id)
        ).first()
        if existing_phone:
            raise HTTPException(status_code=400, detail=f"Driver with phone {update_data['phone']} already exists")
    
    for key, value in update_data.items():
        setattr(driver, key, value)
    
    db.commit()
    db.refresh(driver)
    return driver


@router.delete("/{driver_id}", status_code=204)
def delete_driver(driver_id: int, db: Session = Depends(get_db)):
    """운전자 삭제 (soft delete - is_active = False)"""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Soft delete
    driver.is_active = False
    db.commit()
    return None


@router.get("/code/{code}", response_model=DriverResponse)
def get_driver_by_code(code: str, db: Session = Depends(get_db)):
    """코드로 운전자 조회"""
    driver = db.query(Driver).filter(Driver.code == code).first()
    if not driver:
        raise HTTPException(status_code=404, detail=f"Driver with code {code} not found")
    return driver


@router.get("/stats/summary")
def get_driver_stats(db: Session = Depends(get_db)):
    """운전자 통계"""
    total = db.query(Driver).count()
    active = db.query(Driver).filter(Driver.is_active == True).count()
    inactive = total - active
    
    return {
        "total": total,
        "active": active,
        "inactive": inactive
    }
