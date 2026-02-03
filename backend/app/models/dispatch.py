from enum import Enum
from datetime import date
from sqlalchemy import String, Integer, Float, Date, ForeignKey, Enum as SQLEnum, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from .base import Base, IDMixin, TimestampMixin


class DispatchStatus(str, Enum):
    """배차 상태"""
    DRAFT = "임시저장"
    CONFIRMED = "확정"
    IN_PROGRESS = "진행중"
    COMPLETED = "배차완료"
    CANCELLED = "취소"


class Dispatch(Base, IDMixin, TimestampMixin):
    """배차 계획 테이블"""
    
    __tablename__ = "dispatches"
    
    # 기본 정보
    dispatch_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False, comment="배차번호")
    dispatch_date: Mapped[date] = mapped_column(Date, nullable=False, index=True, comment="배차일자")
    
    # 차량 및 기사
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False, comment="차량 ID")
    driver_id: Mapped[Optional[int]] = mapped_column(ForeignKey("drivers.id"), comment="기사 ID")
    
    # 배차 통계
    total_orders: Mapped[int] = mapped_column(Integer, default=0, comment="총 주문 건수")
    total_pallets: Mapped[int] = mapped_column(Integer, default=0, comment="총 팔레트 수")
    total_weight_kg: Mapped[float] = mapped_column(Float, default=0.0, comment="총 중량(kg)")
    
    # 거리 및 시간
    total_distance_km: Mapped[Optional[float]] = mapped_column(Float, comment="총 주행거리(km)")
    empty_distance_km: Mapped[Optional[float]] = mapped_column(Float, comment="공차거리(km)")
    estimated_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, comment="예상 소요시간(분)")
    
    # 비용
    estimated_cost: Mapped[Optional[float]] = mapped_column(Float, comment="예상 비용")
    
    # 상태
    status: Mapped[DispatchStatus] = mapped_column(
        SQLEnum(DispatchStatus), 
        default=DispatchStatus.DRAFT, 
        comment="배차 상태"
    )
    
    # AI 최적화 정보
    optimization_score: Mapped[Optional[float]] = mapped_column(Float, comment="최적화 점수")
    ai_metadata: Mapped[Optional[dict]] = mapped_column(JSON, comment="AI 배차 메타데이터")
    
    # 메모
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="특이사항")
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="dispatches")
    driver = relationship("Driver", back_populates="dispatches")
    routes = relationship("DispatchRoute", back_populates="dispatch", order_by="DispatchRoute.sequence")
    vehicle_locations = relationship("VehicleLocation", back_populates="dispatch")
    temperature_alerts = relationship("TemperatureAlert", back_populates="dispatch")
    
    def __repr__(self):
        return f"<Dispatch(number={self.dispatch_number}, date={self.dispatch_date}, vehicle_id={self.vehicle_id})>"


class RouteType(str, Enum):
    """경로 유형"""
    GARAGE_START = "차고지출발"
    PICKUP = "상차"
    DELIVERY = "하차"
    GARAGE_END = "차고지복귀"


class DispatchRoute(Base, IDMixin, TimestampMixin):
    """배차 경로 상세 테이블"""
    
    __tablename__ = "dispatch_routes"
    
    # 배차 정보
    dispatch_id: Mapped[int] = mapped_column(ForeignKey("dispatches.id"), nullable=False, comment="배차 ID")
    
    # 순서
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, comment="경로 순서")
    
    # 경로 유형
    route_type: Mapped[RouteType] = mapped_column(SQLEnum(RouteType), nullable=False, comment="경로 유형")
    
    # 주문 정보 (상차/하차일 경우)
    order_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orders.id"), comment="주문 ID")
    
    # 위치 정보
    location_name: Mapped[str] = mapped_column(String(200), nullable=False, comment="위치명")
    address: Mapped[str] = mapped_column(String(500), nullable=False, comment="주소")
    latitude: Mapped[float] = mapped_column(Float, nullable=False, comment="위도")
    longitude: Mapped[float] = mapped_column(Float, nullable=False, comment="경도")
    
    # 이전 지점으로부터의 거리/시간
    distance_from_previous_km: Mapped[Optional[float]] = mapped_column(Float, comment="이전 지점 거리(km)")
    duration_from_previous_minutes: Mapped[Optional[int]] = mapped_column(Integer, comment="이전 지점 소요시간(분)")
    
    # 예상 도착/작업 시간
    estimated_arrival_time: Mapped[Optional[str]] = mapped_column(String(5), comment="예상 도착시간(HH:MM)")
    estimated_work_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, comment="예상 작업시간(분)")
    estimated_departure_time: Mapped[Optional[str]] = mapped_column(String(5), comment="예상 출발시간(HH:MM)")
    
    # 적재 상태
    current_pallets: Mapped[int] = mapped_column(Integer, default=0, comment="현재 적재 팔레트 수")
    current_weight_kg: Mapped[float] = mapped_column(Float, default=0.0, comment="현재 적재 중량(kg)")
    
    # 메모
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="특이사항")
    
    # Relationships
    dispatch = relationship("Dispatch", back_populates="routes")
    order = relationship("Order", back_populates="dispatch_routes")
    
    def __repr__(self):
        return f"<DispatchRoute(dispatch_id={self.dispatch_id}, seq={self.sequence}, type={self.route_type})>"
