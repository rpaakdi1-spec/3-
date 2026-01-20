from enum import Enum
from datetime import date, time
from sqlalchemy import String, Integer, Float, Date, Time, ForeignKey, Enum as SQLEnum, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from .base import Base, IDMixin, TimestampMixin


class TemperatureZone(str, Enum):
    """온도대 구분"""
    FROZEN = "냉동"  # -18°C ~ -25°C
    REFRIGERATED = "냉장"  # 0°C ~ 6°C
    AMBIENT = "상온"  # 온도 제어 없음


class OrderStatus(str, Enum):
    """주문 상태"""
    PENDING = "배차대기"
    ASSIGNED = "배차완료"
    IN_TRANSIT = "운송중"
    DELIVERED = "배송완료"
    CANCELLED = "취소"


class Order(Base, IDMixin, TimestampMixin):
    """주문 테이블"""
    
    __tablename__ = "orders"
    
    # 기본 정보
    order_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False, comment="주문번호")
    order_date: Mapped[date] = mapped_column(Date, nullable=False, comment="주문일자")
    
    # 온도대
    temperature_zone: Mapped[TemperatureZone] = mapped_column(
        SQLEnum(TemperatureZone), 
        nullable=False, 
        comment="온도대 구분"
    )
    
    # 거래처 정보 (ID 또는 주소로 지정 가능)
    pickup_client_id: Mapped[Optional[int]] = mapped_column(ForeignKey("clients.id"), nullable=True, comment="상차 거래처 ID")
    delivery_client_id: Mapped[Optional[int]] = mapped_column(ForeignKey("clients.id"), nullable=True, comment="하차 거래처 ID")
    
    # 주소로 직접 입력한 경우
    pickup_address: Mapped[Optional[str]] = mapped_column(String(500), comment="상차 주소")
    pickup_address_detail: Mapped[Optional[str]] = mapped_column(String(200), comment="상차 상세주소")
    pickup_latitude: Mapped[Optional[float]] = mapped_column(Float, comment="상차 위도")
    pickup_longitude: Mapped[Optional[float]] = mapped_column(Float, comment="상차 경도")
    
    delivery_address: Mapped[Optional[str]] = mapped_column(String(500), comment="하차 주소")
    delivery_address_detail: Mapped[Optional[str]] = mapped_column(String(200), comment="하차 상세주소")
    delivery_latitude: Mapped[Optional[float]] = mapped_column(Float, comment="하차 위도")
    delivery_longitude: Mapped[Optional[float]] = mapped_column(Float, comment="하차 경도")
    
    # 화물 정보
    pallet_count: Mapped[int] = mapped_column(Integer, nullable=False, comment="팔레트 수")
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False, comment="중량(kg)")
    volume_cbm: Mapped[Optional[float]] = mapped_column(Float, comment="용적(CBM)")
    
    # 품목 정보
    product_name: Mapped[Optional[str]] = mapped_column(String(200), comment="품목명")
    product_code: Mapped[Optional[str]] = mapped_column(String(100), comment="품목코드")
    
    # 타임 윈도우
    pickup_start_time: Mapped[Optional[time]] = mapped_column(Time, comment="상차 시작시간")
    pickup_end_time: Mapped[Optional[time]] = mapped_column(Time, comment="상차 종료시간")
    delivery_start_time: Mapped[Optional[time]] = mapped_column(Time, comment="하차 시작시간")
    delivery_end_time: Mapped[Optional[time]] = mapped_column(Time, comment="하차 종료시간")
    
    # 희망 배송일
    requested_delivery_date: Mapped[Optional[date]] = mapped_column(Date, comment="희망 배송일")
    
    # 우선순위
    priority: Mapped[int] = mapped_column(Integer, default=5, comment="우선순위(1:높음 ~ 10:낮음)")
    
    # 특수 요구사항
    requires_forklift: Mapped[bool] = mapped_column(Boolean, default=False, comment="지게차 필요 여부")
    is_stackable: Mapped[bool] = mapped_column(Boolean, default=True, comment="적재 가능 여부")
    
    # 상태
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus), 
        default=OrderStatus.PENDING, 
        comment="주문 상태"
    )
    
    # 메모
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="특이사항")
    
    # Relationships
    pickup_client = relationship("Client", foreign_keys=[pickup_client_id], back_populates="pickup_orders")
    delivery_client = relationship("Client", foreign_keys=[delivery_client_id], back_populates="delivery_orders")
    dispatch_routes = relationship("DispatchRoute", back_populates="order")
    
    def __repr__(self):
        return f"<Order(number={self.order_number}, temp={self.temperature_zone}, pallets={self.pallet_count})>"
