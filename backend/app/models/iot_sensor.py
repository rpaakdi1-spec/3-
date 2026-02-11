"""
IoT Sensor Models for Phase 13-14
Real-time vehicle sensor monitoring and predictive maintenance
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class SensorType(str, enum.Enum):
    """센서 타입"""
    TEMPERATURE = "temperature"  # 온도 센서
    VIBRATION = "vibration"      # 진동 센서
    FUEL = "fuel"                # 연료 센서
    TIRE_PRESSURE = "tire_pressure"  # 타이어 압력
    ENGINE_OIL = "engine_oil"    # 엔진 오일
    BATTERY = "battery"          # 배터리
    GPS = "gps"                  # GPS


class AlertSeverity(str, enum.Enum):
    """알림 심각도"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class MaintenanceStatus(str, enum.Enum):
    """정비 상태"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class VehicleSensor(Base):
    """차량 센서 정보"""
    __tablename__ = "vehicle_sensors"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    sensor_type = Column(SQLEnum(SensorType), nullable=False)
    sensor_name = Column(String(100), nullable=False)
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100), unique=True)
    
    # 센서 설정
    min_threshold = Column(Float)  # 최소 임계값
    max_threshold = Column(Float)  # 최대 임계값
    unit = Column(String(20))      # 측정 단위
    
    # 상태
    is_active = Column(Boolean, default=True)
    last_calibration = Column(DateTime)
    next_calibration = Column(DateTime)
    
    # 타임스탬프
    installed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    readings = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")
    alerts = relationship("SensorAlert", back_populates="sensor", cascade="all, delete-orphan")


class SensorReading(Base):
    """센서 측정값"""
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("vehicle_sensors.id"), nullable=False, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    
    # 측정값
    value = Column(Float, nullable=False)
    unit = Column(String(20))
    
    # 위치 정보 (선택)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # 추가 데이터
    sensor_metadata = Column(JSON)  # 센서별 추가 정보
    
    # 이상 감지
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Float)  # 이상 점수 (0-1)
    
    # 타임스탬프
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sensor = relationship("VehicleSensor", back_populates="readings")


class SensorAlert(Base):
    """센서 알림"""
    __tablename__ = "sensor_alerts"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("vehicle_sensors.id"), nullable=False, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    reading_id = Column(Integer, ForeignKey("sensor_readings.id"), index=True)
    
    # 알림 정보
    severity = Column(SQLEnum(AlertSeverity), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # 센서 값
    sensor_value = Column(Float)
    threshold_value = Column(Float)
    
    # 상태
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Integer, ForeignKey("users.id"))
    acknowledged_at = Column(DateTime)
    
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sensor = relationship("VehicleSensor", back_populates="alerts")


class MaintenanceRecord(Base):
    """정비 이력"""
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    
    # 정비 정보
    maintenance_type = Column(String(100), nullable=False)  # 정비 유형 (예방, 고장, 정기)
    description = Column(Text, nullable=False)
    parts_replaced = Column(JSON)  # 교체한 부품 목록
    
    # 비용
    labor_cost = Column(Float)
    parts_cost = Column(Float)
    total_cost = Column(Float)
    
    # 일정
    scheduled_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime, index=True)
    
    # 상태
    status = Column(SQLEnum(MaintenanceStatus), default=MaintenanceStatus.SCHEDULED, index=True)
    
    # 담당자
    technician_name = Column(String(100))
    technician_notes = Column(Text)
    
    # 마일리지
    mileage_at_maintenance = Column(Integer)
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    predictions = relationship("MaintenancePrediction", back_populates="last_maintenance")


class MaintenancePrediction(Base):
    """정비 예측"""
    __tablename__ = "maintenance_predictions"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    
    # 예측 정보
    component = Column(String(100), nullable=False, index=True)  # 부품명
    failure_probability = Column(Float, nullable=False)  # 고장 확률 (0-1)
    predicted_failure_date = Column(DateTime, index=True)  # 예상 고장 일자
    confidence_score = Column(Float)  # 예측 신뢰도 (0-1)
    
    # 근거 데이터
    sensor_data_summary = Column(JSON)  # 센서 데이터 요약
    usage_patterns = Column(JSON)       # 사용 패턴
    historical_data = Column(JSON)      # 이력 데이터
    
    # 권장 조치
    recommended_action = Column(String(200))
    recommended_date = Column(DateTime)
    estimated_cost = Column(Float)
    
    # 상태
    is_active = Column(Boolean, default=True)
    is_scheduled = Column(Boolean, default=False)
    scheduled_maintenance_id = Column(Integer, ForeignKey("maintenance_schedules.id"))
    
    # 마지막 정비 참조
    last_maintenance_id = Column(Integer, ForeignKey("maintenance_records.id"))
    
    # ML 모델 정보
    model_version = Column(String(50))
    prediction_date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    last_maintenance = relationship("MaintenanceRecord", back_populates="predictions")
    scheduled_maintenance = relationship("MaintenanceSchedule", back_populates="predictions")


class VehicleHealth(Base):
    """차량 건강 상태 (종합 점수)"""
    __tablename__ = "vehicle_health"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, unique=True, index=True)
    
    # 건강 점수 (0-100)
    overall_score = Column(Float, nullable=False)
    engine_score = Column(Float)
    transmission_score = Column(Float)
    brake_score = Column(Float)
    suspension_score = Column(Float)
    electrical_score = Column(Float)
    
    # 상태
    health_status = Column(String(50))  # excellent, good, fair, poor, critical
    
    # 위험 요인
    risk_factors = Column(JSON)  # 위험 요인 목록
    
    # 예측 정보
    next_maintenance_due = Column(DateTime)
    predicted_issues = Column(JSON)
    
    # 통계
    total_mileage = Column(Integer)
    days_in_service = Column(Integer)
    maintenance_count = Column(Integer, default=0)
    breakdown_count = Column(Integer, default=0)
    
    # 타임스탬프
    last_assessment = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PartInventory(Base):
    """부품 재고"""
    __tablename__ = "part_inventory"

    id = Column(Integer, primary_key=True, index=True)
    
    # 부품 정보
    part_name = Column(String(200), nullable=False, index=True)
    part_number = Column(String(100), unique=True, nullable=False)
    manufacturer = Column(String(100))
    category = Column(String(100), index=True)
    
    # 재고
    quantity = Column(Integer, default=0)
    min_quantity = Column(Integer)  # 최소 재고
    max_quantity = Column(Integer)  # 최대 재고
    reorder_point = Column(Integer)  # 재주문 시점
    
    # 비용
    unit_cost = Column(Float)
    
    # 호환성
    compatible_vehicles = Column(JSON)  # 호환 차량 목록
    
    # 공급업체
    supplier_name = Column(String(200))
    supplier_contact = Column(String(100))
    lead_time_days = Column(Integer)  # 납기일
    
    # 상태
    is_available = Column(Boolean, default=True)
    
    # 타임스탬프
    last_restocked = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MaintenanceSchedule(Base):
    """정비 스케줄"""
    __tablename__ = "maintenance_schedules"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    
    # 스케줄 정보
    schedule_type = Column(String(100), nullable=False)  # preventive, predictive, emergency
    priority = Column(String(20), default="normal", index=True)  # low, normal, high, critical
    
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # 작업 항목
    work_items = Column(JSON)  # 작업 항목 목록
    required_parts = Column(JSON)  # 필요 부품 목록
    
    # 일정
    scheduled_date = Column(DateTime, nullable=False, index=True)
    estimated_duration_hours = Column(Float)
    
    # 담당자
    assigned_technician = Column(String(100))
    
    # 비용 예상
    estimated_cost = Column(Float)
    
    # 상태
    status = Column(SQLEnum(MaintenanceStatus), default=MaintenanceStatus.SCHEDULED, index=True)
    
    # 알림
    reminder_sent = Column(Boolean, default=False)
    reminder_sent_at = Column(DateTime)
    
    # 완료 정보
    completed_at = Column(DateTime)
    actual_duration_hours = Column(Float)
    actual_cost = Column(Float)
    completion_notes = Column(Text)
    
    # 연결된 정비 기록
    maintenance_record_id = Column(Integer, ForeignKey("maintenance_records.id"))
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    predictions = relationship("MaintenancePrediction", back_populates="scheduled_maintenance")
