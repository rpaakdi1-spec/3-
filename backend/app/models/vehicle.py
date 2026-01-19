from enum import Enum
from sqlalchemy import String, Integer, Float, Boolean, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
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
    OUT_OF_SERVICE = "운행불가"


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
    
    # 차량 사양
    tonnage: Mapped[float] = mapped_column(Float, comment="톤수")
    length_m: Mapped[Optional[float]] = mapped_column(Float, comment="적재함 길이(m)")
    width_m: Mapped[Optional[float]] = mapped_column(Float, comment="적재함 너비(m)")
    height_m: Mapped[Optional[float]] = mapped_column(Float, comment="적재함 높이(m)")
    
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
    
    # Relationships
    dispatches = relationship("Dispatch", back_populates="vehicle")
    locations = relationship("VehicleLocation", back_populates="vehicle", cascade="all, delete-orphan")
    temperature_alerts = relationship("TemperatureAlert", back_populates="vehicle", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Vehicle(code={self.code}, plate={self.plate_number}, type={self.vehicle_type})>"
