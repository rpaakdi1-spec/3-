"""
Vehicle Maintenance Models
차량 유지보수 관리 모델
Phase 3-B Week 3: 차량 유지보수 관리
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, date
from enum import Enum

from app.models.base import Base, IDMixin, TimestampMixin


class MaintenanceType(str, Enum):
    """정비 유형"""
    REGULAR = "정기점검"           # Regular inspection
    REPAIR = "수리"                # Repair
    PARTS_REPLACEMENT = "부품교체" # Parts replacement
    OIL_CHANGE = "오일교환"        # Oil change
    TIRE_CHANGE = "타이어교체"     # Tire change
    BRAKE = "브레이크"             # Brake maintenance
    BATTERY = "배터리"             # Battery
    ACCIDENT_REPAIR = "사고수리"   # Accident repair
    EMERGENCY = "긴급정비"         # Emergency maintenance
    OTHER = "기타"                 # Other


class MaintenanceStatus(str, Enum):
    """정비 상태"""
    SCHEDULED = "예정"      # Scheduled
    IN_PROGRESS = "진행중"  # In progress
    COMPLETED = "완료"      # Completed
    CANCELLED = "취소"      # Cancelled


class MaintenancePriority(str, Enum):
    """정비 우선순위"""
    LOW = "낮음"      # Low
    MEDIUM = "보통"   # Medium
    HIGH = "높음"     # High
    URGENT = "긴급"   # Urgent


class PartCategory(str, Enum):
    """부품 카테고리"""
    ENGINE = "엔진"           # Engine
    TRANSMISSION = "변속기"   # Transmission
    BRAKE = "브레이크"        # Brake
    TIRE = "타이어"           # Tire
    BATTERY = "배터리"        # Battery
    OIL = "오일"              # Oil
    FILTER = "필터"           # Filter
    COOLANT = "냉각수"        # Coolant
    BELT = "벨트"             # Belt
    SUSPENSION = "서스펜션"   # Suspension
    ELECTRICAL = "전기장치"   # Electrical
    BODY = "차체"             # Body
    INTERIOR = "내장"         # Interior
    OTHER = "기타"            # Other


class VehicleMaintenanceRecord(Base, IDMixin, TimestampMixin):
    """차량 정비 기록"""
    __tablename__ = "vehicle_maintenance_records"

    # 기본 정보
    maintenance_number = Column(String(50), unique=True, index=True, nullable=False, comment="정비 번호")
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True, comment="차량 ID")
    
    # 정비 정보
    maintenance_type = Column(SQLEnum(MaintenanceType), nullable=False, comment="정비 유형")
    status = Column(SQLEnum(MaintenanceStatus), default=MaintenanceStatus.SCHEDULED, nullable=False, comment="상태")
    priority = Column(SQLEnum(MaintenancePriority), default=MaintenancePriority.MEDIUM, nullable=False, comment="우선순위")
    
    # 일정
    scheduled_date = Column(Date, nullable=False, index=True, comment="예정일")
    started_at = Column(DateTime, comment="시작 시각")
    completed_at = Column(DateTime, comment="완료 시각")
    
    # 주행거리
    odometer_reading = Column(Float, comment="주행거리(km)")
    
    # 정비소 정보
    service_center = Column(String(200), comment="정비소명")
    service_center_contact = Column(String(50), comment="정비소 연락처")
    service_center_address = Column(String(500), comment="정비소 주소")
    
    # 담당자
    mechanic_name = Column(String(100), comment="정비사 이름")
    assigned_by = Column(String(100), comment="지시자")
    
    # 비용
    labor_cost = Column(Float, default=0.0, comment="인건비")
    parts_cost = Column(Float, default=0.0, comment="부품비")
    total_cost = Column(Float, default=0.0, comment="총 비용")
    
    # 내용
    description = Column(Text, comment="정비 내용")
    findings = Column(Text, comment="발견사항")
    recommendations = Column(Text, comment="권고사항")
    notes = Column(Text, comment="비고")
    
    # 증빙
    invoice_number = Column(String(100), comment="청구서 번호")
    invoice_file_path = Column(String(500), comment="청구서 파일")
    before_photos = Column(Text, comment="작업 전 사진 (JSON array)")
    after_photos = Column(Text, comment="작업 후 사진 (JSON array)")
    
    # 다음 정비 예정
    next_maintenance_date = Column(Date, comment="다음 정비 예정일")
    next_maintenance_odometer = Column(Float, comment="다음 정비 주행거리")
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="maintenance_records")
    parts_used = relationship("MaintenancePartUsage", back_populates="maintenance_record", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<VehicleMaintenanceRecord(number={self.maintenance_number}, vehicle_id={self.vehicle_id}, type={self.maintenance_type.value})>"


class VehiclePart(Base, IDMixin, TimestampMixin):
    """차량 부품"""
    __tablename__ = "vehicle_parts"

    # 부품 정보
    part_number = Column(String(100), unique=True, index=True, nullable=False, comment="부품 번호")
    part_name = Column(String(200), nullable=False, comment="부품명")
    category = Column(SQLEnum(PartCategory), nullable=False, comment="카테고리")
    
    # 제조사 정보
    manufacturer = Column(String(200), comment="제조사")
    model = Column(String(200), comment="모델")
    
    # 재고 정보
    quantity_in_stock = Column(Integer, default=0, comment="재고 수량")
    minimum_stock = Column(Integer, default=0, comment="최소 재고")
    unit = Column(String(20), default="개", comment="단위")
    
    # 가격
    unit_price = Column(Float, nullable=False, comment="단가")
    supplier = Column(String(200), comment="공급업체")
    supplier_contact = Column(String(50), comment="공급업체 연락처")
    
    # 사용 정보
    compatible_models = Column(Text, comment="호환 차량 모델 (JSON array)")
    average_lifespan_km = Column(Float, comment="평균 수명(km)")
    average_lifespan_months = Column(Integer, comment="평균 수명(개월)")
    
    # 기타
    description = Column(Text, comment="설명")
    notes = Column(Text, comment="비고")
    is_active = Column(Boolean, default=True, comment="활성 여부")
    
    # Relationships
    usage_records = relationship("MaintenancePartUsage", back_populates="part")
    
    def __repr__(self):
        return f"<VehiclePart(number={self.part_number}, name={self.part_name})>"


class MaintenancePartUsage(Base, IDMixin, TimestampMixin):
    """정비 부품 사용 내역"""
    __tablename__ = "maintenance_part_usage"

    # 연결
    maintenance_record_id = Column(Integer, ForeignKey("vehicle_maintenance_records.id"), nullable=False, index=True, comment="정비 기록 ID")
    part_id = Column(Integer, ForeignKey("vehicle_parts.id"), nullable=False, index=True, comment="부품 ID")
    
    # 사용량
    quantity_used = Column(Integer, nullable=False, comment="사용 수량")
    unit_price = Column(Float, nullable=False, comment="단가")
    total_price = Column(Float, nullable=False, comment="총액")
    
    # 기타
    notes = Column(Text, comment="비고")
    
    # Relationships
    maintenance_record = relationship("VehicleMaintenanceRecord", back_populates="parts_used")
    part = relationship("VehiclePart", back_populates="usage_records")
    
    def __repr__(self):
        return f"<MaintenancePartUsage(maintenance_id={self.maintenance_record_id}, part_id={self.part_id}, qty={self.quantity_used})>"


class MaintenanceSchedule(Base, IDMixin, TimestampMixin):
    """정비 스케줄 (정기 점검 계획)"""
    __tablename__ = "maintenance_schedules"

    # 차량
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True, comment="차량 ID")
    
    # 정비 유형
    maintenance_type = Column(SQLEnum(MaintenanceType), nullable=False, comment="정비 유형")
    
    # 주기 설정 (둘 중 하나 또는 둘 다)
    interval_km = Column(Float, comment="주행거리 주기(km)")
    interval_months = Column(Integer, comment="기간 주기(개월)")
    
    # 마지막 실시
    last_maintenance_date = Column(Date, comment="마지막 정비일")
    last_maintenance_odometer = Column(Float, comment="마지막 정비 시 주행거리")
    
    # 다음 예정
    next_maintenance_date = Column(Date, index=True, comment="다음 정비 예정일")
    next_maintenance_odometer = Column(Float, comment="다음 정비 예정 주행거리")
    
    # 알림 설정
    alert_before_km = Column(Float, default=1000.0, comment="km 사전 알림")
    alert_before_days = Column(Integer, default=7, comment="일 사전 알림")
    
    # 상태
    is_active = Column(Boolean, default=True, comment="활성 여부")
    is_overdue = Column(Boolean, default=False, comment="연체 여부")
    
    # 비고
    notes = Column(Text, comment="비고")
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="maintenance_schedules")
    
    def __repr__(self):
        return f"<MaintenanceSchedule(vehicle_id={self.vehicle_id}, type={self.maintenance_type.value})>"
    
    def check_if_due(self, current_odometer: float, current_date: date) -> bool:
        """정비가 필요한지 확인"""
        is_due = False
        
        # 주행거리 기준
        if self.next_maintenance_odometer and current_odometer:
            if current_odometer >= self.next_maintenance_odometer:
                is_due = True
        
        # 날짜 기준
        if self.next_maintenance_date and current_date:
            if current_date >= self.next_maintenance_date:
                is_due = True
        
        return is_due


class VehicleInspection(Base, IDMixin, TimestampMixin):
    """차량 검사 (법정 검사)"""
    __tablename__ = "vehicle_inspections"

    # 차량
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True, comment="차량 ID")
    
    # 검사 정보
    inspection_type = Column(String(100), nullable=False, comment="검사 유형 (정기검사, 종합검사 등)")
    inspection_date = Column(Date, nullable=False, comment="검사일")
    expiry_date = Column(Date, nullable=False, index=True, comment="만료일")
    
    # 검사 결과
    result = Column(String(50), comment="검사 결과 (합격/불합격)")
    pass_status = Column(Boolean, default=True, comment="합격 여부")
    
    # 검사소 정보
    inspection_center = Column(String(200), comment="검사소명")
    inspector_name = Column(String(100), comment="검사자")
    
    # 비용
    inspection_cost = Column(Float, comment="검사 비용")
    
    # 증빙
    certificate_number = Column(String(100), comment="검사증 번호")
    certificate_file_path = Column(String(500), comment="검사증 파일")
    
    # 발견사항
    findings = Column(Text, comment="발견사항")
    defects = Column(Text, comment="결함 사항")
    recommendations = Column(Text, comment="권고사항")
    
    # 비고
    notes = Column(Text, comment="비고")
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="inspections")
    
    def __repr__(self):
        return f"<VehicleInspection(vehicle_id={self.vehicle_id}, date={self.inspection_date}, expiry={self.expiry_date})>"
    
    def is_expiring_soon(self, days: int = 30) -> bool:
        """검사 만료가 임박했는지 확인"""
        from datetime import timedelta
        if self.expiry_date:
            return (self.expiry_date - date.today()).days <= days
        return False
