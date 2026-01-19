from enum import Enum
from sqlalchemy import String, Float, Boolean, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from .base import Base, IDMixin, TimestampMixin


class ClientType(str, Enum):
    """거래처 구분"""
    PICKUP = "상차"  # 상차지
    DELIVERY = "하차"  # 하차지
    BOTH = "양쪽"  # 상차/하차 모두 가능


class Client(Base, IDMixin, TimestampMixin):
    """거래처 마스터 테이블"""
    
    __tablename__ = "clients"
    
    # 기본 정보
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False, comment="거래처코드")
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="거래처명")
    client_type: Mapped[ClientType] = mapped_column(SQLEnum(ClientType), nullable=False, comment="상차/하차 구분")
    
    # 주소 정보
    address: Mapped[str] = mapped_column(String(500), nullable=False, comment="기본 주소")
    address_detail: Mapped[Optional[str]] = mapped_column(String(200), comment="상세 주소")
    
    # 좌표 정보
    latitude: Mapped[Optional[float]] = mapped_column(Float, comment="위도")
    longitude: Mapped[Optional[float]] = mapped_column(Float, comment="경도")
    geocoded: Mapped[bool] = mapped_column(Boolean, default=False, comment="지오코딩 완료 여부")
    geocode_error: Mapped[Optional[str]] = mapped_column(Text, comment="지오코딩 오류 메시지")
    
    # 운영 시간
    pickup_start_time: Mapped[Optional[str]] = mapped_column(String(5), comment="상차가능시작시간(HH:MM)")
    pickup_end_time: Mapped[Optional[str]] = mapped_column(String(5), comment="상차가능종료시간(HH:MM)")
    delivery_start_time: Mapped[Optional[str]] = mapped_column(String(5), comment="하차가능시작시간(HH:MM)")
    delivery_end_time: Mapped[Optional[str]] = mapped_column(String(5), comment="하차가능종료시간(HH:MM)")
    
    # 시설 정보
    has_forklift: Mapped[bool] = mapped_column(Boolean, default=False, comment="지게차 유무")
    loading_time_minutes: Mapped[int] = mapped_column(default=30, comment="평균 상하차 소요시간(분)")
    
    # 연락처
    contact_person: Mapped[Optional[str]] = mapped_column(String(100), comment="담당자명")
    phone: Mapped[Optional[str]] = mapped_column(String(20), comment="전화번호")
    
    # 메모
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="특이사항")
    
    # 활성화 상태
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="사용 여부")
    
    # Relationships
    pickup_orders = relationship("Order", foreign_keys="Order.pickup_client_id", back_populates="pickup_client")
    delivery_orders = relationship("Order", foreign_keys="Order.delivery_client_id", back_populates="delivery_client")
    
    def __repr__(self):
        return f"<Client(code={self.code}, name={self.name}, type={self.client_type})>"
