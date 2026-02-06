"""
Order Template Model
주문 템플릿 모델 - 자주 쓰는 주문 양식 저장
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.models.base import Base
from app.models.order import TemperatureZone


class OrderTemplate(Base):
    """주문 템플릿 모델"""
    __tablename__ = "order_templates"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Template Info
    name = Column(String(100), nullable=False, index=True, comment="템플릿 이름")
    description = Column(Text, comment="템플릿 설명")
    category = Column(String(50), comment="카테고리 (예: 정기배송, 긴급, 장거리)")
    
    # Template Data (same as Order fields)
    temperature_zone = Column(String(20), nullable=False)
    
    # Pickup
    pickup_client_id = Column(Integer, comment="상차 거래처 ID")
    pickup_address = Column(String(500), comment="상차 주소")
    pickup_address_detail = Column(String(200), comment="상차 상세주소")
    
    # Delivery
    delivery_client_id = Column(Integer, comment="하차 거래처 ID")
    delivery_address = Column(String(500), comment="하차 주소")
    delivery_address_detail = Column(String(200), comment="하차 상세주소")
    
    # Order Details
    pallet_count = Column(Integer, nullable=False, comment="팔레트 수")
    weight_kg = Column(Float, default=0, comment="중량(kg)")
    volume_cbm = Column(Float, default=0, comment="용적(CBM)")
    
    # Product
    product_name = Column(String(200), comment="품목명")
    product_code = Column(String(100), comment="품목코드")
    
    # Time Windows (default values)
    pickup_start_time = Column(String(5), comment="상차 시작 시간 (HH:MM)")
    pickup_end_time = Column(String(5), comment="상차 종료 시간 (HH:MM)")
    delivery_start_time = Column(String(5), comment="하차 시작 시간 (HH:MM)")
    delivery_end_time = Column(String(5), comment="하차 종료 시간 (HH:MM)")
    
    # Handling
    requires_forklift = Column(Boolean, default=False, comment="지게차 필요 여부")
    is_stackable = Column(Boolean, default=True, comment="적재 가능 여부")
    
    # Priority
    priority = Column(Integer, default=5, comment="우선순위 (1-10)")
    
    # Notes
    notes = Column(Text, comment="비고")
    
    # Usage
    usage_count = Column(Integer, default=0, comment="사용 횟수")
    last_used_at = Column(DateTime(timezone=True), comment="마지막 사용 시간")
    
    # Sharing
    is_shared = Column(Boolean, default=False, comment="공유 여부 (모든 사용자가 사용 가능)")
    created_by = Column(Integer, comment="생성자 User ID")
    
    # Status
    is_active = Column(Boolean, default=True, index=True, comment="활성화 여부")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 시간")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정 시간")
    
    def to_order_data(self) -> dict:
        """템플릿을 Order 생성 데이터로 변환"""
        return {
            "temperature_zone": self.temperature_zone,
            "pickup_client_id": self.pickup_client_id,
            "pickup_address": self.pickup_address,
            "pickup_address_detail": self.pickup_address_detail,
            "delivery_client_id": self.delivery_client_id,
            "delivery_address": self.delivery_address,
            "delivery_address_detail": self.delivery_address_detail,
            "pallet_count": self.pallet_count,
            "weight_kg": self.weight_kg or 0,
            "volume_cbm": self.volume_cbm or 0,
            "product_name": self.product_name,
            "product_code": self.product_code,
            "pickup_start_time": self.pickup_start_time,
            "pickup_end_time": self.pickup_end_time,
            "delivery_start_time": self.delivery_start_time,
            "delivery_end_time": self.delivery_end_time,
            "requires_forklift": self.requires_forklift,
            "is_stackable": self.is_stackable,
            "priority": self.priority,
            "notes": self.notes,
        }
    
    def __repr__(self):
        return f"<OrderTemplate(id={self.id}, name='{self.name}', category='{self.category}')>"
