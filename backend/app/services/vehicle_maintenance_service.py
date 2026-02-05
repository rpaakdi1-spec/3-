"""
Vehicle Maintenance Service
차량 유지보수 관리 서비스
Phase 3-B Week 3: 차량 유지보수 관리
"""
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import logging

from app.models.vehicle_maintenance import (
    VehicleMaintenanceRecord,
    VehiclePart,
    MaintenancePartUsage,
    MaintenanceSchedule,
    VehicleInspection,
    MaintenanceType,
    MaintenanceStatus,
    MaintenancePriority,
    PartCategory
)
from app.models.vehicle import Vehicle

logger = logging.getLogger(__name__)


class MaintenanceService:
    """차량 정비 관리 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_maintenance_number(self) -> str:
        """
        정비 번호 생성
        
        Returns:
            정비 번호 (MNT-YYYYMMDD-NNNN)
        """
        today = datetime.now()
        prefix = f"MNT-{today.strftime('%Y%m%d')}"
        
        last_record = self.db.query(VehicleMaintenanceRecord).filter(
            VehicleMaintenanceRecord.maintenance_number.like(f"{prefix}%")
        ).order_by(desc(VehicleMaintenanceRecord.maintenance_number)).first()
        
        if last_record:
            last_number = int(last_record.maintenance_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:04d}"
    
    def create_maintenance_record(
        self,
        vehicle_id: int,
        maintenance_type: MaintenanceType,
        scheduled_date: date,
        priority: MaintenancePriority = MaintenancePriority.MEDIUM,
        description: Optional[str] = None,
        service_center: Optional[str] = None,
        odometer_reading: Optional[float] = None
    ) -> VehicleMaintenanceRecord:
        """
        정비 기록 생성
        
        Args:
            vehicle_id: 차량 ID
            maintenance_type: 정비 유형
            scheduled_date: 예정일
            priority: 우선순위
            description: 설명
            service_center: 정비소
            odometer_reading: 주행거리
            
        Returns:
            생성된 VehicleMaintenanceRecord
        """
        maintenance_number = self.generate_maintenance_number()
        
        record = VehicleMaintenanceRecord(
            maintenance_number=maintenance_number,
            vehicle_id=vehicle_id,
            maintenance_type=maintenance_type,
            status=MaintenanceStatus.SCHEDULED,
            priority=priority,
            scheduled_date=scheduled_date,
            description=description,
            service_center=service_center,
            odometer_reading=odometer_reading
        )
        
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        
        logger.info(f"정비 기록 생성: {maintenance_number}, vehicle_id={vehicle_id}")
        
        return record
    
    def start_maintenance(
        self,
        maintenance_id: int,
        mechanic_name: Optional[str] = None
    ) -> VehicleMaintenanceRecord:
        """
        정비 시작
        
        Args:
            maintenance_id: 정비 ID
            mechanic_name: 정비사 이름
            
        Returns:
            업데이트된 기록
        """
        record = self.db.query(VehicleMaintenanceRecord).filter(
            VehicleMaintenanceRecord.id == maintenance_id
        ).first()
        
        if not record:
            raise ValueError(f"정비 기록을 찾을 수 없습니다: {maintenance_id}")
        
        record.status = MaintenanceStatus.IN_PROGRESS
        record.started_at = datetime.utcnow()
        if mechanic_name:
            record.mechanic_name = mechanic_name
        
        # 차량 상태 업데이트
        vehicle = record.vehicle
        if vehicle:
            vehicle.status = "MAINTENANCE"
        
        self.db.commit()
        self.db.refresh(record)
        
        logger.info(f"정비 시작: {record.maintenance_number}")
        
        return record
    
    def complete_maintenance(
        self,
        maintenance_id: int,
        labor_cost: float,
        parts_cost: float,
        findings: Optional[str] = None,
        recommendations: Optional[str] = None,
        next_maintenance_date: Optional[date] = None,
        next_maintenance_odometer: Optional[float] = None
    ) -> VehicleMaintenanceRecord:
        """
        정비 완료 처리
        
        Args:
            maintenance_id: 정비 ID
            labor_cost: 인건비
            parts_cost: 부품비
            findings: 발견사항
            recommendations: 권고사항
            next_maintenance_date: 다음 정비 예정일
            next_maintenance_odometer: 다음 정비 주행거리
            
        Returns:
            업데이트된 기록
        """
        record = self.db.query(VehicleMaintenanceRecord).filter(
            VehicleMaintenanceRecord.id == maintenance_id
        ).first()
        
        if not record:
            raise ValueError(f"정비 기록을 찾을 수 없습니다: {maintenance_id}")
        
        record.status = MaintenanceStatus.COMPLETED
        record.completed_at = datetime.utcnow()
        record.labor_cost = labor_cost
        record.parts_cost = parts_cost
        record.total_cost = labor_cost + parts_cost
        record.findings = findings
        record.recommendations = recommendations
        record.next_maintenance_date = next_maintenance_date
        record.next_maintenance_odometer = next_maintenance_odometer
        
        # 차량 상태 복구
        vehicle = record.vehicle
        if vehicle and vehicle.status == "MAINTENANCE":
            vehicle.status = "AVAILABLE"
        
        # 정비 스케줄 업데이트
        if next_maintenance_date or next_maintenance_odometer:
            self._update_maintenance_schedule(
                vehicle_id=record.vehicle_id,
                maintenance_type=record.maintenance_type,
                last_date=date.today(),
                last_odometer=record.odometer_reading,
                next_date=next_maintenance_date,
                next_odometer=next_maintenance_odometer
            )
        
        self.db.commit()
        self.db.refresh(record)
        
        logger.info(f"정비 완료: {record.maintenance_number}, cost={record.total_cost:,.0f}원")
        
        return record
    
    def add_part_usage(
        self,
        maintenance_id: int,
        part_id: int,
        quantity: int,
        unit_price: float
    ) -> MaintenancePartUsage:
        """
        부품 사용 내역 추가
        
        Args:
            maintenance_id: 정비 ID
            part_id: 부품 ID
            quantity: 수량
            unit_price: 단가
            
        Returns:
            생성된 MaintenancePartUsage
        """
        usage = MaintenancePartUsage(
            maintenance_record_id=maintenance_id,
            part_id=part_id,
            quantity_used=quantity,
            unit_price=unit_price,
            total_price=quantity * unit_price
        )
        
        self.db.add(usage)
        
        # 부품 재고 차감
        part = self.db.query(VehiclePart).filter(VehiclePart.id == part_id).first()
        if part:
            part.quantity_in_stock -= quantity
        
        self.db.commit()
        self.db.refresh(usage)
        
        logger.info(f"부품 사용 기록: part_id={part_id}, qty={quantity}")
        
        return usage
    
    def _update_maintenance_schedule(
        self,
        vehicle_id: int,
        maintenance_type: MaintenanceType,
        last_date: date,
        last_odometer: Optional[float],
        next_date: Optional[date],
        next_odometer: Optional[float]
    ):
        """정비 스케줄 업데이트"""
        schedule = self.db.query(MaintenanceSchedule).filter(
            and_(
                MaintenanceSchedule.vehicle_id == vehicle_id,
                MaintenanceSchedule.maintenance_type == maintenance_type,
                MaintenanceSchedule.is_active == True
            )
        ).first()
        
        if schedule:
            schedule.last_maintenance_date = last_date
            schedule.last_maintenance_odometer = last_odometer
            schedule.next_maintenance_date = next_date
            schedule.next_maintenance_odometer = next_odometer
            self.db.commit()
    
    def create_maintenance_schedule(
        self,
        vehicle_id: int,
        maintenance_type: MaintenanceType,
        interval_km: Optional[float] = None,
        interval_months: Optional[int] = None,
        alert_before_km: float = 1000.0,
        alert_before_days: int = 7
    ) -> MaintenanceSchedule:
        """
        정비 스케줄 생성
        
        Args:
            vehicle_id: 차량 ID
            maintenance_type: 정비 유형
            interval_km: 주행거리 주기
            interval_months: 기간 주기
            alert_before_km: km 사전 알림
            alert_before_days: 일 사전 알림
            
        Returns:
            생성된 MaintenanceSchedule
        """
        # 기존 스케줄 확인
        existing = self.db.query(MaintenanceSchedule).filter(
            and_(
                MaintenanceSchedule.vehicle_id == vehicle_id,
                MaintenanceSchedule.maintenance_type == maintenance_type,
                MaintenanceSchedule.is_active == True
            )
        ).first()
        
        if existing:
            logger.warning(f"이미 스케줄이 존재합니다: vehicle_id={vehicle_id}, type={maintenance_type}")
            return existing
        
        schedule = MaintenanceSchedule(
            vehicle_id=vehicle_id,
            maintenance_type=maintenance_type,
            interval_km=interval_km,
            interval_months=interval_months,
            alert_before_km=alert_before_km,
            alert_before_days=alert_before_days,
            is_active=True
        )
        
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        
        logger.info(f"정비 스케줄 생성: vehicle_id={vehicle_id}, type={maintenance_type}")
        
        return schedule
    
    def check_due_maintenance(self, vehicle_id: int, current_odometer: float) -> List[MaintenanceSchedule]:
        """
        정비 필요 여부 확인
        
        Args:
            vehicle_id: 차량 ID
            current_odometer: 현재 주행거리
            
        Returns:
            정비가 필요한 스케줄 리스트
        """
        schedules = self.db.query(MaintenanceSchedule).filter(
            and_(
                MaintenanceSchedule.vehicle_id == vehicle_id,
                MaintenanceSchedule.is_active == True
            )
        ).all()
        
        due_schedules = []
        today = date.today()
        
        for schedule in schedules:
            if schedule.check_if_due(current_odometer, today):
                due_schedules.append(schedule)
                schedule.is_overdue = True
        
        self.db.commit()
        
        return due_schedules
    
    def get_maintenance_history(
        self,
        vehicle_id: int,
        limit: int = 50
    ) -> List[VehicleMaintenanceRecord]:
        """
        정비 이력 조회
        
        Args:
            vehicle_id: 차량 ID
            limit: 최대 개수
            
        Returns:
            정비 기록 리스트
        """
        records = self.db.query(VehicleMaintenanceRecord).filter(
            VehicleMaintenanceRecord.vehicle_id == vehicle_id
        ).order_by(desc(VehicleMaintenanceRecord.scheduled_date)).limit(limit).all()
        
        return records
    
    def get_maintenance_cost_summary(
        self,
        vehicle_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        정비 비용 요약
        
        Args:
            vehicle_id: 차량 ID (선택)
            start_date: 시작일
            end_date: 종료일
            
        Returns:
            비용 요약 딕셔너리
        """
        query = self.db.query(VehicleMaintenanceRecord).filter(
            VehicleMaintenanceRecord.status == MaintenanceStatus.COMPLETED
        )
        
        if vehicle_id:
            query = query.filter(VehicleMaintenanceRecord.vehicle_id == vehicle_id)
        if start_date:
            query = query.filter(VehicleMaintenanceRecord.completed_at >= start_date)
        if end_date:
            query = query.filter(VehicleMaintenanceRecord.completed_at <= end_date)
        
        records = query.all()
        
        total_labor = sum(r.labor_cost or 0 for r in records)
        total_parts = sum(r.parts_cost or 0 for r in records)
        total_cost = sum(r.total_cost or 0 for r in records)
        
        # 유형별 비용
        type_costs = {}
        for record in records:
            type_name = record.maintenance_type.value
            if type_name not in type_costs:
                type_costs[type_name] = 0
            type_costs[type_name] += record.total_cost or 0
        
        return {
            'total_records': len(records),
            'total_labor_cost': round(total_labor, 2),
            'total_parts_cost': round(total_parts, 2),
            'total_cost': round(total_cost, 2),
            'average_cost': round(total_cost / len(records), 2) if records else 0,
            'cost_by_type': type_costs
        }
    
    def create_inspection_record(
        self,
        vehicle_id: int,
        inspection_type: str,
        inspection_date: date,
        expiry_date: date,
        pass_status: bool = True,
        inspection_cost: Optional[float] = None,
        inspection_center: Optional[str] = None,
        certificate_number: Optional[str] = None
    ) -> VehicleInspection:
        """
        차량 검사 기록 생성
        
        Args:
            vehicle_id: 차량 ID
            inspection_type: 검사 유형
            inspection_date: 검사일
            expiry_date: 만료일
            pass_status: 합격 여부
            inspection_cost: 검사 비용
            inspection_center: 검사소
            certificate_number: 검사증 번호
            
        Returns:
            생성된 VehicleInspection
        """
        inspection = VehicleInspection(
            vehicle_id=vehicle_id,
            inspection_type=inspection_type,
            inspection_date=inspection_date,
            expiry_date=expiry_date,
            pass_status=pass_status,
            result="합격" if pass_status else "불합격",
            inspection_cost=inspection_cost,
            inspection_center=inspection_center,
            certificate_number=certificate_number
        )
        
        self.db.add(inspection)
        self.db.commit()
        self.db.refresh(inspection)
        
        logger.info(f"검사 기록 생성: vehicle_id={vehicle_id}, type={inspection_type}")
        
        return inspection
    
    def get_expiring_inspections(self, days: int = 30) -> List[VehicleInspection]:
        """
        만료 임박 검사 조회
        
        Args:
            days: 임박 기준 일수
            
        Returns:
            만료 임박 검사 리스트
        """
        threshold_date = date.today() + timedelta(days=days)
        
        inspections = self.db.query(VehicleInspection).filter(
            and_(
                VehicleInspection.expiry_date <= threshold_date,
                VehicleInspection.expiry_date >= date.today()
            )
        ).order_by(VehicleInspection.expiry_date).all()
        
        return inspections


class PartInventoryService:
    """부품 재고 관리 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_part(
        self,
        part_number: str,
        part_name: str,
        category: PartCategory,
        unit_price: float,
        quantity_in_stock: int = 0,
        minimum_stock: int = 0,
        manufacturer: Optional[str] = None,
        supplier: Optional[str] = None
    ) -> VehiclePart:
        """
        부품 등록
        
        Args:
            part_number: 부품 번호
            part_name: 부품명
            category: 카테고리
            unit_price: 단가
            quantity_in_stock: 재고 수량
            minimum_stock: 최소 재고
            manufacturer: 제조사
            supplier: 공급업체
            
        Returns:
            생성된 VehiclePart
        """
        part = VehiclePart(
            part_number=part_number,
            part_name=part_name,
            category=category,
            unit_price=unit_price,
            quantity_in_stock=quantity_in_stock,
            minimum_stock=minimum_stock,
            manufacturer=manufacturer,
            supplier=supplier,
            is_active=True
        )
        
        self.db.add(part)
        self.db.commit()
        self.db.refresh(part)
        
        logger.info(f"부품 등록: {part_number} - {part_name}")
        
        return part
    
    def update_stock(self, part_id: int, quantity_change: int) -> VehiclePart:
        """
        재고 수량 업데이트
        
        Args:
            part_id: 부품 ID
            quantity_change: 변경량 (양수: 입고, 음수: 출고)
            
        Returns:
            업데이트된 VehiclePart
        """
        part = self.db.query(VehiclePart).filter(VehiclePart.id == part_id).first()
        
        if not part:
            raise ValueError(f"부품을 찾을 수 없습니다: {part_id}")
        
        part.quantity_in_stock += quantity_change
        
        self.db.commit()
        self.db.refresh(part)
        
        logger.info(f"재고 업데이트: {part.part_number}, change={quantity_change}, new={part.quantity_in_stock}")
        
        return part
    
    def get_low_stock_parts(self) -> List[VehiclePart]:
        """
        재고 부족 부품 조회
        
        Returns:
            재고 부족 부품 리스트
        """
        parts = self.db.query(VehiclePart).filter(
            and_(
                VehiclePart.is_active == True,
                VehiclePart.quantity_in_stock <= VehiclePart.minimum_stock
            )
        ).all()
        
        return parts
    
    def get_part_usage_history(
        self,
        part_id: int,
        limit: int = 50
    ) -> List[MaintenancePartUsage]:
        """
        부품 사용 이력 조회
        
        Args:
            part_id: 부품 ID
            limit: 최대 개수
            
        Returns:
            사용 이력 리스트
        """
        usage = self.db.query(MaintenancePartUsage).filter(
            MaintenancePartUsage.part_id == part_id
        ).order_by(desc(MaintenancePartUsage.created_at)).limit(limit).all()
        
        return usage
