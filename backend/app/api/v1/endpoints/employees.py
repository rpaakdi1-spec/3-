"""
Employee API Endpoints
인사관리 시스템 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from datetime import date
import logging

from app.core.database import get_db
from app.models.employee import Employee, EmployeeRole, EmploymentType
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeListResponse,
    DriverPoolItem,
    ForkliftCapableDriversResponse,
    EmployeeStatistics,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== Helper Functions ====================

def employee_to_response(employee: Employee) -> EmployeeResponse:
    """Convert Employee model to response schema"""
    return EmployeeResponse(
        **{
            **{k: v for k, v in employee.__dict__.items() if not k.startswith('_')},
            'forklift_status': employee.forklift_status,
            'can_be_assigned_to_vehicle': employee.can_be_assigned_to_vehicle,
            'days_until_forklift_expiry': employee.days_until_forklift_expiry,
            'needs_forklift_training': employee.needs_forklift_training,
        }
    )


# ==================== CRUD Endpoints ====================

@router.post("/", response_model=EmployeeResponse, status_code=201)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db)
):
    """
    직원 등록
    
    - **employee_code**: 사원번호 (유니크)
    - **name**: 이름
    - **role**: 직급 (MASTER, ADMIN, MANAGER, DRIVER)
    - **can_drive_forklift**: 지게차 운전 가능 여부
    - **has_forklift_certificate**: 지게차 자격증 보유 여부
    """
    # Check duplicate employee_code
    existing = db.query(Employee).filter(
        Employee.employee_code == employee_data.employee_code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"사원번호 '{employee_data.employee_code}'는 이미 사용 중입니다.")
    
    # Create employee
    employee = Employee(**employee_data.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    
    logger.info(f"Created employee: {employee.employee_code} - {employee.name}")
    return employee_to_response(employee)


@router.get("/", response_model=EmployeeListResponse)
def list_employees(
    role: Optional[str] = Query(None, description="직급 필터"),
    employment_type: Optional[str] = Query(None, description="고용 형태 필터"),
    is_active: Optional[bool] = Query(None, description="재직 상태 필터"),
    license_type: Optional[str] = Query(None, description="면허 종류 필터"),
    has_cargo_license: Optional[bool] = Query(None, description="화물자격증 보유 필터"),
    can_drive_forklift: Optional[bool] = Query(None, description="지게차 운전 가능 필터"),
    has_forklift_certificate: Optional[bool] = Query(None, description="지게차 자격증 필터"),
    search: Optional[str] = Query(None, description="이름, 사원번호, 전화번호 검색"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    db: Session = Depends(get_db)
):
    """
    직원 목록 조회 (필터링, 검색, 페이지네이션 지원)
    """
    query = db.query(Employee)
    
    # Filters
    if role:
        query = query.filter(Employee.role == role)
    if employment_type:
        query = query.filter(Employee.employment_type == employment_type)
    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)
    if license_type:
        query = query.filter(Employee.license_type == license_type)
    if has_cargo_license is not None:
        query = query.filter(Employee.has_cargo_license == has_cargo_license)
    if can_drive_forklift is not None:
        query = query.filter(Employee.can_drive_forklift == can_drive_forklift)
    if has_forklift_certificate is not None:
        query = query.filter(Employee.has_forklift_certificate == has_forklift_certificate)
    
    # Search
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Employee.name.like(search_pattern),
                Employee.employee_code.like(search_pattern),
                Employee.phone.like(search_pattern)
            )
        )
    
    # Count total
    total = query.count()
    
    # Pagination
    offset = (page - 1) * page_size
    employees = query.order_by(Employee.created_at.desc()).offset(offset).limit(page_size).all()
    
    return EmployeeListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[employee_to_response(emp) for emp in employees]
    )


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """직원 상세 조회"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="직원을 찾을 수 없습니다.")
    return employee_to_response(employee)


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db)
):
    """직원 정보 수정"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="직원을 찾을 수 없습니다.")
    
    # Update fields
    update_data = employee_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(employee, key, value)
    
    db.commit()
    db.refresh(employee)
    
    logger.info(f"Updated employee: {employee.employee_code} - {employee.name}")
    return employee_to_response(employee)


@router.delete("/{employee_id}", status_code=204)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    직원 삭제 (소프트 삭제 - 휴지통으로 이동)
    
    실제로는 is_active를 False로 설정하고 resignation_date를 기록
    복구는 restore endpoint를 사용
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="직원을 찾을 수 없습니다.")
    
    employee.is_active = False
    employee.resignation_date = date.today()
    db.commit()
    
    logger.info(f"Moved to trash: {employee.employee_code} - {employee.name}")
    return None


@router.post("/{employee_id}/restore", response_model=EmployeeResponse)
def restore_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    퇴사자 복구 (휴지통에서 복원)
    
    - 퇴사 처리된 직원을 재직 상태로 되돌림
    - resignation_date를 null로 설정
    - is_active를 True로 설정
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="직원을 찾을 수 없습니다.")
    
    if employee.is_active:
        raise HTTPException(status_code=400, detail="이미 재직 중인 직원입니다.")
    
    # Restore employee
    employee.is_active = True
    employee.resignation_date = None
    db.commit()
    db.refresh(employee)
    
    logger.info(f"Restored employee from trash: {employee.employee_code} - {employee.name}")
    return employee_to_response(employee)


# ==================== 운전자 특화 Endpoints ====================

@router.get("/drivers/pool", response_model=List[DriverPoolItem])
def get_driver_pool(
    only_available: bool = Query(False, description="배차 가능한 운전자만 조회"),
    can_drive_forklift: Optional[bool] = Query(None, description="지게차 가능 필터"),
    db: Session = Depends(get_db)
):
    """
    운전자 풀 조회 (차량 배정용)
    
    - 운전직(DRIVER) 사원만 조회
    - 차량-운전자 배정 시스템에서 사용
    """
    query = db.query(Employee).filter(Employee.role == EmployeeRole.DRIVER)
    
    if only_available:
        query = query.filter(
            and_(
                Employee.is_active == True,
                Employee.license_type.isnot(None)
            )
        )
    
    if can_drive_forklift is not None:
        query = query.filter(Employee.can_drive_forklift == can_drive_forklift)
    
    drivers = query.order_by(Employee.name).all()
    
    return [
        DriverPoolItem(
            id=d.id,
            employee_code=d.employee_code,
            name=d.name,
            phone=d.phone,
            license_type=d.license_type,
            has_cargo_license=d.has_cargo_license,
            can_drive_forklift=d.can_drive_forklift,
            has_forklift_certificate=d.has_forklift_certificate,
            forklift_status=d.forklift_status,
            work_hours=f"{d.work_start_time}-{d.work_end_time}",
            is_active=d.is_active
        )
        for d in drivers
    ]


@router.get("/drivers/forklift-capable", response_model=ForkliftCapableDriversResponse)
def get_forklift_capable_drivers(db: Session = Depends(get_db)):
    """
    지게차 가능 운전자 목록
    
    - 운전 가능 + 자격증 보유
    - 운전 가능 + 자격증 미보유 (교육 대상)
    """
    drivers = db.query(Employee).filter(
        and_(
            Employee.role == EmployeeRole.DRIVER,
            Employee.is_active == True,
            Employee.can_drive_forklift == True
        )
    ).all()
    
    with_cert = [d for d in drivers if d.has_forklift_certificate]
    without_cert = [d for d in drivers if not d.has_forklift_certificate]
    
    driver_items = [
        DriverPoolItem(
            id=d.id,
            employee_code=d.employee_code,
            name=d.name,
            phone=d.phone,
            license_type=d.license_type,
            has_cargo_license=d.has_cargo_license,
            can_drive_forklift=d.can_drive_forklift,
            has_forklift_certificate=d.has_forklift_certificate,
            forklift_status=d.forklift_status,
            work_hours=f"{d.work_start_time}-{d.work_end_time}",
            is_active=d.is_active
        )
        for d in drivers
    ]
    
    return ForkliftCapableDriversResponse(
        total=len(drivers),
        with_certificate=len(with_cert),
        without_certificate=len(without_cert),
        drivers=driver_items
    )


# ==================== 통계 Endpoint ====================

@router.get("/statistics/overview", response_model=EmployeeStatistics)
def get_employee_statistics(db: Session = Depends(get_db)):
    """직원 통계"""
    total = db.query(Employee).count()
    active = db.query(Employee).filter(Employee.is_active == True).count()
    
    # By role
    role_counts = db.query(
        Employee.role,
        func.count(Employee.id)
    ).group_by(Employee.role).all()
    by_role = {role: count for role, count in role_counts}
    
    # By employment type
    type_counts = db.query(
        Employee.employment_type,
        func.count(Employee.id)
    ).group_by(Employee.employment_type).all()
    by_employment_type = {emp_type: count for emp_type, count in type_counts}
    
    # Driver statistics
    drivers_with_cargo = db.query(Employee).filter(
        and_(
            Employee.role == EmployeeRole.DRIVER,
            Employee.has_cargo_license == True
        )
    ).count()
    
    drivers_with_forklift_ability = db.query(Employee).filter(
        and_(
            Employee.role == EmployeeRole.DRIVER,
            Employee.can_drive_forklift == True
        )
    ).count()
    
    drivers_with_forklift_cert = db.query(Employee).filter(
        and_(
            Employee.role == EmployeeRole.DRIVER,
            Employee.has_forklift_certificate == True
        )
    ).count()
    
    drivers_needing_training = db.query(Employee).filter(
        and_(
            Employee.role == EmployeeRole.DRIVER,
            Employee.can_drive_forklift == True,
            Employee.has_forklift_certificate == False
        )
    ).count()
    
    return EmployeeStatistics(
        total_employees=total,
        active_employees=active,
        by_role=by_role,
        by_employment_type=by_employment_type,
        drivers_with_cargo_license=drivers_with_cargo,
        drivers_with_forklift_ability=drivers_with_forklift_ability,
        drivers_with_forklift_certificate=drivers_with_forklift_cert,
        drivers_needing_training=drivers_needing_training
    )
