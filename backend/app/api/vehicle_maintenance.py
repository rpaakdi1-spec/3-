"""
Vehicle Maintenance API
차량 유지보수 관리 API
Phase 3-B Week 3: 차량 유지보수 관리
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.vehicle_maintenance import (
    MaintenanceType, MaintenanceStatus, MaintenancePriority, PartCategory
)
from app.services.vehicle_maintenance_service import MaintenanceService, PartInventoryService
from app.services.maintenance_alert_service import MaintenanceAlertService

router = APIRouter()


# ============================================================================
# Pydantic Schemas
# ============================================================================

class MaintenanceRecordCreate(BaseModel):
    vehicle_id: int
    maintenance_type: MaintenanceType
    scheduled_date: date
    priority: MaintenancePriority = MaintenancePriority.MEDIUM
    description: Optional[str] = None
    service_center: Optional[str] = None
    odometer_reading: Optional[float] = None


class MaintenanceRecordUpdate(BaseModel):
    status: Optional[MaintenanceStatus] = None
    mechanic_name: Optional[str] = None
    labor_cost: Optional[float] = None
    parts_cost: Optional[float] = None
    findings: Optional[str] = None
    recommendations: Optional[str] = None
    next_maintenance_date: Optional[date] = None
    next_maintenance_odometer: Optional[float] = None


class PartUsageCreate(BaseModel):
    maintenance_id: int
    part_id: int
    quantity: int
    unit_price: float


class MaintenanceScheduleCreate(BaseModel):
    vehicle_id: int
    maintenance_type: MaintenanceType
    interval_km: Optional[float] = None
    interval_months: Optional[int] = None
    alert_before_km: float = 1000.0
    alert_before_days: int = 7


class VehiclePartCreate(BaseModel):
    part_number: str
    part_name: str
    category: PartCategory
    unit_price: float
    quantity_in_stock: int = 0
    minimum_stock: int = 0
    manufacturer: Optional[str] = None
    supplier: Optional[str] = None
    supplier_contact: Optional[str] = None


class VehiclePartUpdate(BaseModel):
    part_name: Optional[str] = None
    category: Optional[PartCategory] = None
    unit_price: Optional[float] = None
    quantity_in_stock: Optional[int] = None
    minimum_stock: Optional[int] = None
    manufacturer: Optional[str] = None
    supplier: Optional[str] = None
    supplier_contact: Optional[str] = None
    is_active: Optional[bool] = None


class StockUpdate(BaseModel):
    quantity_change: int = Field(..., description="양수: 입고, 음수: 출고")


class InspectionRecordCreate(BaseModel):
    vehicle_id: int
    inspection_type: str
    inspection_date: date
    expiry_date: date
    pass_status: bool = True
    inspection_cost: Optional[float] = None
    inspection_center: Optional[str] = None
    certificate_number: Optional[str] = None
    findings: Optional[str] = None


# ============================================================================
# Maintenance Records API
# ============================================================================

@router.post("/maintenance/records", tags=["Maintenance"])
def create_maintenance_record(
    data: MaintenanceRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """정비 기록 생성"""
    service = MaintenanceService(db)
    record = service.create_maintenance_record(
        vehicle_id=data.vehicle_id,
        maintenance_type=data.maintenance_type,
        scheduled_date=data.scheduled_date,
        priority=data.priority,
        description=data.description,
        service_center=data.service_center,
        odometer_reading=data.odometer_reading
    )
    return record


@router.get("/maintenance/records", tags=["Maintenance"])
def get_maintenance_records(
    vehicle_id: Optional[int] = None,
    status: Optional[MaintenanceStatus] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """정비 기록 목록 조회"""
    from app.models.vehicle_maintenance import VehicleMaintenanceRecord
    from sqlalchemy import and_, desc
    
    query = db.query(VehicleMaintenanceRecord)
    
    if vehicle_id:
        query = query.filter(VehicleMaintenanceRecord.vehicle_id == vehicle_id)
    if status:
        query = query.filter(VehicleMaintenanceRecord.status == status)
    if start_date:
        query = query.filter(VehicleMaintenanceRecord.scheduled_date >= start_date)
    if end_date:
        query = query.filter(VehicleMaintenanceRecord.scheduled_date <= end_date)
    
    records = query.order_by(desc(VehicleMaintenanceRecord.scheduled_date)).limit(limit).all()
    return records


@router.get("/maintenance/records/{record_id}", tags=["Maintenance"])
def get_maintenance_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """정비 기록 상세 조회"""
    from app.models.vehicle_maintenance import VehicleMaintenanceRecord
    
    record = db.query(VehicleMaintenanceRecord).filter(
        VehicleMaintenanceRecord.id == record_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="정비 기록을 찾을 수 없습니다")
    
    return record


@router.post("/maintenance/records/{record_id}/start", tags=["Maintenance"])
def start_maintenance(
    record_id: int,
    mechanic_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """정비 시작"""
    service = MaintenanceService(db)
    record = service.start_maintenance(record_id, mechanic_name)
    return record


@router.post("/maintenance/records/{record_id}/complete", tags=["Maintenance"])
def complete_maintenance(
    record_id: int,
    data: MaintenanceRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """정비 완료"""
    service = MaintenanceService(db)
    record = service.complete_maintenance(
        maintenance_id=record_id,
        labor_cost=data.labor_cost or 0,
        parts_cost=data.parts_cost or 0,
        findings=data.findings,
        recommendations=data.recommendations,
        next_maintenance_date=data.next_maintenance_date,
        next_maintenance_odometer=data.next_maintenance_odometer
    )
    return record


@router.delete("/maintenance/records/{record_id}", tags=["Maintenance"])
def cancel_maintenance(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """정비 취소"""
    from app.models.vehicle_maintenance import VehicleMaintenanceRecord
    
    record = db.query(VehicleMaintenanceRecord).filter(
        VehicleMaintenanceRecord.id == record_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="정비 기록을 찾을 수 없습니다")
    
    record.status = MaintenanceStatus.CANCELLED
    db.commit()
    
    return {"message": "정비가 취소되었습니다"}


# ============================================================================
# Part Usage API
# ============================================================================

@router.post("/maintenance/parts/usage", tags=["Maintenance"])
def add_part_usage(
    data: PartUsageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """부품 사용 내역 추가"""
    service = MaintenanceService(db)
    usage = service.add_part_usage(
        maintenance_id=data.maintenance_id,
        part_id=data.part_id,
        quantity=data.quantity,
        unit_price=data.unit_price
    )
    return usage


@router.get("/maintenance/records/{record_id}/parts", tags=["Maintenance"])
def get_maintenance_parts(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """정비 부품 사용 내역 조회"""
    from app.models.vehicle_maintenance import MaintenancePartUsage
    
    parts = db.query(MaintenancePartUsage).filter(
        MaintenancePartUsage.maintenance_record_id == record_id
    ).all()
    
    return parts


# ============================================================================
# Maintenance Schedule API
# ============================================================================

@router.post("/maintenance/schedules", tags=["Maintenance"])
def create_maintenance_schedule(
    data: MaintenanceScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """정비 스케줄 생성"""
    service = MaintenanceService(db)
    schedule = service.create_maintenance_schedule(
        vehicle_id=data.vehicle_id,
        maintenance_type=data.maintenance_type,
        interval_km=data.interval_km,
        interval_months=data.interval_months,
        alert_before_km=data.alert_before_km,
        alert_before_days=data.alert_before_days
    )
    return schedule


@router.get("/maintenance/schedules", tags=["Maintenance"])
def get_maintenance_schedules(
    vehicle_id: Optional[int] = None,
    is_overdue: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """정비 스케줄 목록 조회"""
    from app.models.vehicle_maintenance import MaintenanceSchedule
    from sqlalchemy import and_
    
    query = db.query(MaintenanceSchedule).filter(MaintenanceSchedule.is_active == True)
    
    if vehicle_id:
        query = query.filter(MaintenanceSchedule.vehicle_id == vehicle_id)
    if is_overdue is not None:
        query = query.filter(MaintenanceSchedule.is_overdue == is_overdue)
    
    schedules = query.all()
    return schedules


@router.post("/maintenance/schedules/check-due/{vehicle_id}", tags=["Maintenance"])
def check_due_maintenance(
    vehicle_id: int,
    current_odometer: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """정비 필요 여부 확인"""
    service = MaintenanceService(db)
    due_schedules = service.check_due_maintenance(vehicle_id, current_odometer)
    return due_schedules


# ============================================================================
# Vehicle Parts Inventory API
# ============================================================================

@router.post("/maintenance/parts", tags=["Parts Inventory"])
def create_part(
    data: VehiclePartCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """부품 등록"""
    service = PartInventoryService(db)
    part = service.create_part(
        part_number=data.part_number,
        part_name=data.part_name,
        category=data.category,
        unit_price=data.unit_price,
        quantity_in_stock=data.quantity_in_stock,
        minimum_stock=data.minimum_stock,
        manufacturer=data.manufacturer,
        supplier=data.supplier
    )
    return part


@router.get("/maintenance/parts", tags=["Parts Inventory"])
def get_parts(
    category: Optional[PartCategory] = None,
    low_stock: bool = False,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """부품 목록 조회"""
    from app.models.vehicle_maintenance import VehiclePart
    from sqlalchemy import and_, or_
    
    query = db.query(VehiclePart).filter(VehiclePart.is_active == True)
    
    if category:
        query = query.filter(VehiclePart.category == category)
    
    if low_stock:
        query = query.filter(VehiclePart.quantity_in_stock <= VehiclePart.minimum_stock)
    
    if search:
        query = query.filter(
            or_(
                VehiclePart.part_number.ilike(f"%{search}%"),
                VehiclePart.part_name.ilike(f"%{search}%")
            )
        )
    
    parts = query.all()
    return parts


@router.get("/maintenance/parts/{part_id}", tags=["Parts Inventory"])
def get_part(
    part_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """부품 상세 조회"""
    from app.models.vehicle_maintenance import VehiclePart
    
    part = db.query(VehiclePart).filter(VehiclePart.id == part_id).first()
    
    if not part:
        raise HTTPException(status_code=404, detail="부품을 찾을 수 없습니다")
    
    return part


@router.put("/maintenance/parts/{part_id}", tags=["Parts Inventory"])
def update_part(
    part_id: int,
    data: VehiclePartUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """부품 정보 수정"""
    from app.models.vehicle_maintenance import VehiclePart
    
    part = db.query(VehiclePart).filter(VehiclePart.id == part_id).first()
    
    if not part:
        raise HTTPException(status_code=404, detail="부품을 찾을 수 없습니다")
    
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(part, field, value)
    
    db.commit()
    db.refresh(part)
    
    return part


@router.post("/maintenance/parts/{part_id}/stock", tags=["Parts Inventory"])
def update_part_stock(
    part_id: int,
    data: StockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """부품 재고 수량 업데이트"""
    service = PartInventoryService(db)
    part = service.update_stock(part_id, data.quantity_change)
    return part


@router.get("/maintenance/parts/{part_id}/usage-history", tags=["Parts Inventory"])
def get_part_usage_history(
    part_id: int,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """부품 사용 이력 조회"""
    service = PartInventoryService(db)
    usage = service.get_part_usage_history(part_id, limit)
    return usage


# ============================================================================
# Vehicle Inspections API
# ============================================================================

@router.post("/maintenance/inspections", tags=["Inspections"])
def create_inspection(
    data: InspectionRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """차량 검사 기록 생성"""
    service = MaintenanceService(db)
    inspection = service.create_inspection_record(
        vehicle_id=data.vehicle_id,
        inspection_type=data.inspection_type,
        inspection_date=data.inspection_date,
        expiry_date=data.expiry_date,
        pass_status=data.pass_status,
        inspection_cost=data.inspection_cost,
        inspection_center=data.inspection_center,
        certificate_number=data.certificate_number
    )
    return inspection


@router.get("/maintenance/inspections", tags=["Inspections"])
def get_inspections(
    vehicle_id: Optional[int] = None,
    expiring_soon: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """차량 검사 기록 조회"""
    from app.models.vehicle_maintenance import VehicleInspection
    from sqlalchemy import desc
    
    if expiring_soon:
        service = MaintenanceService(db)
        return service.get_expiring_inspections(days=expiring_soon)
    
    query = db.query(VehicleInspection)
    
    if vehicle_id:
        query = query.filter(VehicleInspection.vehicle_id == vehicle_id)
    
    inspections = query.order_by(desc(VehicleInspection.inspection_date)).all()
    return inspections


# ============================================================================
# Analytics & Reports
# ============================================================================

@router.get("/maintenance/cost-summary", tags=["Analytics"])
def get_maintenance_cost_summary(
    vehicle_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """정비 비용 요약"""
    service = MaintenanceService(db)
    summary = service.get_maintenance_cost_summary(vehicle_id, start_date, end_date)
    return summary


@router.get("/maintenance/vehicles/{vehicle_id}/history", tags=["Analytics"])
def get_vehicle_maintenance_history(
    vehicle_id: int,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """차량별 정비 이력"""
    service = MaintenanceService(db)
    history = service.get_maintenance_history(vehicle_id, limit)
    return history


# ============================================================================
# Maintenance Alerts API
# ============================================================================

@router.get("/maintenance/alerts/overdue", tags=["Alerts"])
def get_overdue_maintenance_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """연체된 정비 알림 조회"""
    alert_service = MaintenanceAlertService(db)
    alerts = alert_service.check_overdue_maintenance()
    return alerts


@router.get("/maintenance/alerts/upcoming", tags=["Alerts"])
def get_upcoming_maintenance_alerts(
    days_ahead: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """다가오는 정비 알림 조회"""
    alert_service = MaintenanceAlertService(db)
    alerts = alert_service.check_upcoming_maintenance(days_ahead)
    return alerts


@router.get("/maintenance/alerts/inspections", tags=["Alerts"])
def get_inspection_alerts(
    days_ahead: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """만료 예정 검사 알림 조회"""
    alert_service = MaintenanceAlertService(db)
    alerts = alert_service.check_expiring_inspections(days_ahead)
    return alerts


@router.get("/maintenance/alerts/parts", tags=["Alerts"])
def get_low_stock_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """부품 재고 부족 알림 조회"""
    alert_service = MaintenanceAlertService(db)
    alerts = alert_service.check_low_stock_parts()
    return alerts


@router.post("/maintenance/alerts/send-all", tags=["Alerts"])
def send_all_maintenance_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """모든 정비 알림 전송"""
    alert_service = MaintenanceAlertService(db)
    results = alert_service.send_all_alerts()
    return results


@router.get("/maintenance/alerts/dashboard", tags=["Alerts"])
def get_maintenance_alerts_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """정비 알림 대시보드 요약"""
    alert_service = MaintenanceAlertService(db)
    
    overdue = alert_service.check_overdue_maintenance()
    upcoming = alert_service.check_upcoming_maintenance(days_ahead=7)
    expiring = alert_service.check_expiring_inspections(days_ahead=30)
    low_stock = alert_service.check_low_stock_parts()
    
    return {
        "overdue_count": len(overdue),
        "upcoming_count": len(upcoming),
        "expiring_inspections_count": len(expiring),
        "low_stock_count": len(low_stock),
        "overdue_alerts": overdue[:5],  # Top 5
        "upcoming_alerts": upcoming[:5],
        "expiring_alerts": expiring[:5],
        "low_stock_alerts": low_stock[:5],
        "total_alerts": len(overdue) + len(upcoming) + len(expiring) + len(low_stock)
    }
