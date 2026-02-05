"""
Recurring Order Model
정기 주문 모델
"""
from sqlalchemy import Column, Integer, String, Date, Time, Boolean, DateTime, Enum as SQLEnum, Text
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.order import TemperatureZone
import enum


class RecurringFrequency(str, enum.Enum):
    """반복 주기"""
    DAILY = "DAILY"  # 매일
    WEEKLY = "WEEKLY"  # 매주
    MONTHLY = "MONTHLY"  # 매월
    CUSTOM = "CUSTOM"  # 커스텀 (특정 요일)


class RecurringOrder(Base):
    """정기 주문 모델"""
    __tablename__ = "recurring_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 기본 정보
    name = Column(String(200), nullable=False, comment="정기 주문명")
    description = Column(Text, nullable=True, comment="설명")
    
    # 반복 설정
    frequency = Column(SQLEnum(RecurringFrequency), nullable=False, comment="반복 주기")
    start_date = Column(Date, nullable=False, comment="시작일")
    end_date = Column(Date, nullable=True, comment="종료일 (null이면 무제한)")
    
    # 요일 설정 (WEEKLY, CUSTOM용)
    # 비트 플래그: 월(1), 화(2), 수(4), 목(8), 금(16), 토(32), 일(64)
    # 예: 월수금 = 1 + 4 + 16 = 21
    weekdays = Column(Integer, default=0, comment="실행 요일 (비트 플래그)")
    
    # 매월 특정일 (MONTHLY용)
    day_of_month = Column(Integer, nullable=True, comment="매월 특정일 (1-31)")
    
    # 주문 정보 (템플릿)
    temperature_zone = Column(SQLEnum(TemperatureZone), nullable=False)
    
    # 거래처 정보
    pickup_client_id = Column(Integer, nullable=True)
    delivery_client_id = Column(Integer, nullable=True)
    pickup_address = Column(String(500), nullable=True)
    pickup_address_detail = Column(String(200), nullable=True)
    delivery_address = Column(String(500), nullable=True)
    delivery_address_detail = Column(String(200), nullable=True)
    
    # 물품 정보
    pallet_count = Column(Integer, nullable=False)
    weight_kg = Column(Integer, default=0)
    volume_cbm = Column(Integer, default=0)
    product_name = Column(String(200), nullable=True)
    product_code = Column(String(100), nullable=True)
    
    # 시간 정보
    pickup_start_time = Column(Time, nullable=True)
    pickup_end_time = Column(Time, nullable=True)
    delivery_start_time = Column(Time, nullable=True)
    delivery_end_time = Column(Time, nullable=True)
    
    # 기타
    priority = Column(Integer, default=5)
    requires_forklift = Column(Boolean, default=False)
    is_stackable = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # 상태
    is_active = Column(Boolean, default=True, comment="활성화 여부")
    last_generated_date = Column(Date, nullable=True, comment="마지막 생성일")
    
    # 메타데이터
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def should_generate_today(self, target_date) -> bool:
        """오늘 주문을 생성해야 하는지 확인"""
        # 시작일 이전이면 생성하지 않음
        if target_date < self.start_date:
            return False
        
        # 종료일 이후면 생성하지 않음
        if self.end_date and target_date > self.end_date:
            return False
        
        # 활성화되지 않았으면 생성하지 않음
        if not self.is_active:
            return False
        
        # 오늘 이미 생성했으면 생성하지 않음
        if self.last_generated_date == target_date:
            return False
        
        # 빈도별 체크
        if self.frequency == RecurringFrequency.DAILY:
            return True
        
        elif self.frequency == RecurringFrequency.WEEKLY:
            # 요일 체크 (월요일=0, 일요일=6)
            weekday = target_date.weekday()
            weekday_bit = 1 << weekday  # 비트 플래그 계산
            return bool(self.weekdays & weekday_bit)
        
        elif self.frequency == RecurringFrequency.MONTHLY:
            # 매월 특정일 체크
            return target_date.day == self.day_of_month
        
        elif self.frequency == RecurringFrequency.CUSTOM:
            # 커스텀 요일 체크
            weekday = target_date.weekday()
            weekday_bit = 1 << weekday
            return bool(self.weekdays & weekday_bit)
        
        return False
    
    def __repr__(self):
        return f"<RecurringOrder(id={self.id}, name='{self.name}', frequency='{self.frequency}')>"
