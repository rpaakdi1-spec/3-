from enum import Enum
from sqlalchemy import String, Integer, Float, Boolean, Enum as SQLEnum, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime
from .base import Base, IDMixin, TimestampMixin


class VehicleType(str, Enum):
    """차량 온도대 구분"""
    FROZEN = "냉동"  # -18°C ~ -25°C
    REFRIGERATED = "냉장"  # 0°C ~ 6°C
    DUAL = "겸용"  # 냉동/냉장 모두 가능
    AMBIENT = "상온"  # 온도 제어 없음


class VehicleStatus(str, Enum):
    """차량 상태"""
    AVAILABLE = "운행가능"
    IN_USE = "운행중"
    MAINTENANCE = "정비중"
    EMERGENCY_MAINTENANCE = "긴급정비"  # 긴급 정비 중
    BREAKDOWN = "고장"  # 고장 (운행 불가)
    OUT_OF_SERVICE = "운행불가"


class EmergencyType(str, Enum):
    """긴급 상황 유형"""
    BREAKDOWN = "breakdown"  # 고장
    MALFUNCTION = "malfunction"  # 기능 이상
    ACCIDENT = "accident"  # 사고
    OTHER = "other"  # 기타


class EmergencySeverity(str, Enum):
    """긴급도"""
    CRITICAL = "critical"  # 긴급 - 즉시 운행 불가
    WARNING = "warning"  # 주의 - 조속한 정비 필요
    MINOR = "minor"  # 경미 - 운행 가능, 운행 후 정비


class Vehicle(Base, IDMixin, TimestampMixin):
    """차량 마스터 테이블"""
    
    __tablename__ = "vehicles"
    
    # 기본 정보
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False, comment="차량코드")
    plate_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, comment="차량번호")
    vehicle_type: Mapped[VehicleType] = mapped_column(SQLEnum(VehicleType), nullable=False, comment="온도대 구분")
    
    # UVIS 연동
    uvis_device_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, comment="UVIS 단말기 ID")
    uvis_enabled: Mapped[bool] = mapped_column(Boolean, default=False, comment="UVIS 연동 여부")
    
    # 적재 용량
    max_pallets: Mapped[int] = mapped_column(Integer, nullable=False, comment="최대 팔레트 수")
    max_weight_kg: Mapped[float] = mapped_column(Float, nullable=False, comment="최대 적재중량(kg)")
    max_volume_cbm: Mapped[Optional[float]] = mapped_column(Float, comment="최대 용적(CBM)")
    
    # 하역 장비
    forklift_operator_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="지게차 운전능력 가능 여부")
    
    # 차량 사양
    tonnage: Mapped[float] = mapped_column(Float, comment="톤수")
    length_m: Mapped[Optional[float]] = mapped_column(Float, comment="적재함 길이(m)")
    width_m: Mapped[Optional[float]] = mapped_column(Float, comment="적재함 너비(m)")
    height_m: Mapped[Optional[float]] = mapped_column(Float, comment="적재함 높이(m)")
    
    # 운전자 정보
    driver_name: Mapped[Optional[str]] = mapped_column(String(100), comment="운전자명")
    driver_phone: Mapped[Optional[str]] = mapped_column(String(20), comment="운전자 연락처")
    
    # 온도 범위
    min_temp_celsius: Mapped[Optional[float]] = mapped_column(Float, comment="최저 온도(°C)")
    max_temp_celsius: Mapped[Optional[float]] = mapped_column(Float, comment="최고 온도(°C)")
    
    # 운영 정보
    fuel_efficiency_km_per_liter: Mapped[Optional[float]] = mapped_column(Float, comment="연비(km/L)")
    fuel_cost_per_liter: Mapped[Optional[float]] = mapped_column(Float, comment="리터당 연료비")
    
    # 상태
    status: Mapped[VehicleStatus] = mapped_column(
        SQLEnum(VehicleStatus), 
        default=VehicleStatus.AVAILABLE, 
        comment="차량 상태"
    )
    
    # 차고지 위치
    garage_address: Mapped[Optional[str]] = mapped_column(String(500), comment="차고지 주소")
    garage_latitude: Mapped[Optional[float]] = mapped_column(Float, comment="차고지 위도")
    garage_longitude: Mapped[Optional[float]] = mapped_column(Float, comment="차고지 경도")
    
    # 메모
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="특이사항")
    
    # 활성화 상태
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="사용 여부")
    
    # 긴급정비 관련
    is_emergency: Mapped[bool] = mapped_column(Boolean, default=False, comment="긴급 상황 여부")
    emergency_type: Mapped[Optional[str]] = mapped_column(String(50), comment="긴급 유형")
    emergency_severity: Mapped[Optional[str]] = mapped_column(String(20), comment="긴급도")
    emergency_reported_at: Mapped[Optional[datetime]] = mapped_column(DateTime, comment="신고 시각")
    emergency_location: Mapped[Optional[str]] = mapped_column(String(500), comment="발생 위치")
    emergency_description: Mapped[Optional[str]] = mapped_column(Text, comment="상황 설명")
    estimated_repair_time: Mapped[Optional[int]] = mapped_column(Integer, comment="예상 수리 시간(분)")
    replacement_vehicle_id: Mapped[Optional[int]] = mapped_column(Integer, comment="대체 차량 ID")
    
    # Relationships
    dispatches = relationship("Dispatch", back_populates="vehicle")
    locations = relationship("VehicleLocation", back_populates="vehicle", cascade="all, delete-orphan")
    temperature_alerts = relationship("TemperatureAlert", back_populates="vehicle", cascade="all, delete-orphan")
    gps_logs = relationship("VehicleGPSLog", back_populates="vehicle", cascade="all, delete-orphan")
    temperature_logs = relationship("VehicleTemperatureLog", back_populates="vehicle", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Vehicle(code={self.code}, plate={self.plate_number}, type={self.vehicle_type})>"
