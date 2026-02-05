"""
Billing and Settlement Models
청구 및 정산 모델
Phase 3-B Week 1-2: 청구/정산 자동화
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.models.base import Base


class BillingCycleType(str, enum.Enum):
    """청구 주기 유형"""
    IMMEDIATE = "IMMEDIATE"  # 즉시
    WEEKLY = "WEEKLY"        # 주간
    MONTHLY = "MONTHLY"      # 월간
    CUSTOM = "CUSTOM"        # 커스텀


class BillingStatus(str, enum.Enum):
    """청구 상태"""
    DRAFT = "DRAFT"          # 초안
    PENDING = "PENDING"      # 대기
    SENT = "SENT"            # 발송됨
    PARTIAL = "PARTIAL"      # 부분 결제
    PAID = "PAID"            # 결제 완료
    OVERDUE = "OVERDUE"      # 연체
    CANCELLED = "CANCELLED"  # 취소됨


class PaymentMethod(str, enum.Enum):
    """결제 방법"""
    CASH = "CASH"            # 현금
    TRANSFER = "TRANSFER"    # 계좌이체
    CARD = "CARD"            # 신용카드
    CHECK = "CHECK"          # 수표


class BillingPolicy(Base):
    """청구 정책"""
    __tablename__ = "billing_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    
    # 청구 설정
    billing_cycle = Column(SQLEnum(BillingCycleType), default=BillingCycleType.MONTHLY)
    billing_day = Column(Integer, nullable=True)  # 청구일 (1-31)
    payment_terms_days = Column(Integer, default=30)  # 결제 기한 (일)
    
    # 요금 설정
    base_rate_per_km = Column(Float, default=0.0)  # 기본 요금 (km당)
    base_rate_per_pallet = Column(Float, default=0.0)  # 팔레트당 요금
    base_rate_per_kg = Column(Float, default=0.0)  # 중량당 요금
    
    # 추가 요금
    weekend_surcharge_rate = Column(Float, default=0.0)  # 주말 할증 (%)
    night_surcharge_rate = Column(Float, default=0.0)  # 야간 할증 (%)
    express_surcharge_rate = Column(Float, default=0.0)  # 긴급 할증 (%)
    temperature_control_rate = Column(Float, default=0.0)  # 온도 관리 추가 요금
    
    # 할인
    volume_discount_threshold = Column(Integer, default=0)  # 물량 할인 기준
    volume_discount_rate = Column(Float, default=0.0)  # 물량 할인율 (%)
    
    # 메타데이터
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="billing_policies")
    
    def __repr__(self):
        return f"<BillingPolicy(client_id={self.client_id}, cycle={self.billing_cycle})>"


class Invoice(Base):
    """청구서"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    
    # 청구 기간
    billing_period_start = Column(Date, nullable=False)
    billing_period_end = Column(Date, nullable=False)
    
    # 금액
    subtotal = Column(Float, default=0.0)  # 소계
    tax_amount = Column(Float, default=0.0)  # 세금
    discount_amount = Column(Float, default=0.0)  # 할인
    total_amount = Column(Float, default=0.0)  # 총액
    paid_amount = Column(Float, default=0.0)  # 결제 금액
    
    # 상태
    status = Column(SQLEnum(BillingStatus), default=BillingStatus.DRAFT, index=True)
    
    # 날짜
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    paid_date = Column(Date, nullable=True)
    
    # 메타데이터
    notes = Column(Text, nullable=True)
    pdf_url = Column(String(500), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    client = relationship("Client", back_populates="invoices")
    line_items = relationship("InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Invoice(number={self.invoice_number}, client_id={self.client_id}, total={self.total_amount}, status={self.status})>"


class InvoiceLineItem(Base):
    """청구서 항목"""
    __tablename__ = "invoice_line_items"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    dispatch_id = Column(Integer, ForeignKey("dispatches.id"), nullable=True, index=True)
    
    # 항목 정보
    description = Column(String(500), nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    
    # 상세 정보
    distance_km = Column(Float, nullable=True)
    pallets = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)
    
    # 할증/할인
    surcharge_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    invoice = relationship("Invoice", back_populates="line_items")
    dispatch = relationship("Dispatch", back_populates="invoice_line_items")
    
    def __repr__(self):
        return f"<InvoiceLineItem(invoice_id={self.invoice_id}, amount={self.amount})>"


class Payment(Base):
    """결제 기록"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(50), unique=True, nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    
    # 결제 정보
    amount = Column(Float, nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    payment_date = Column(Date, nullable=False)
    
    # 상세 정보
    reference_number = Column(String(100), nullable=True)  # 거래 참조 번호
    bank_name = Column(String(100), nullable=True)
    account_number = Column(String(100), nullable=True)
    
    notes = Column(Text, nullable=True)
    receipt_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(number={self.payment_number}, invoice_id={self.invoice_id}, amount={self.amount})>"


class DriverSettlement(Base):
    """기사 정산"""
    __tablename__ = "driver_settlements"
    
    id = Column(Integer, primary_key=True, index=True)
    settlement_number = Column(String(50), unique=True, nullable=False, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False, index=True)
    
    # 정산 기간
    settlement_period_start = Column(Date, nullable=False)
    settlement_period_end = Column(Date, nullable=False)
    
    # 금액
    total_revenue = Column(Float, default=0.0)  # 총 매출
    commission_amount = Column(Float, default=0.0)  # 수수료
    expense_amount = Column(Float, default=0.0)  # 비용
    net_amount = Column(Float, default=0.0)  # 순액
    
    # 상태
    is_paid = Column(Boolean, default=False)
    paid_date = Column(Date, nullable=True)
    
    # 통계
    dispatch_count = Column(Integer, default=0)
    total_distance_km = Column(Float, default=0.0)
    total_pallets = Column(Integer, default=0.0)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    driver = relationship("Driver", back_populates="settlements")
    settlement_items = relationship("DriverSettlementItem", back_populates="settlement", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DriverSettlement(number={self.settlement_number}, driver_id={self.driver_id}, net={self.net_amount})>"


class DriverSettlementItem(Base):
    """기사 정산 항목"""
    __tablename__ = "driver_settlement_items"
    
    id = Column(Integer, primary_key=True, index=True)
    settlement_id = Column(Integer, ForeignKey("driver_settlements.id"), nullable=False, index=True)
    dispatch_id = Column(Integer, ForeignKey("dispatches.id"), nullable=False, index=True)
    
    # 금액
    revenue = Column(Float, nullable=False)
    commission_rate = Column(Float, default=0.0)  # 수수료율 (%)
    commission_amount = Column(Float, default=0.0)
    
    # 상세
    distance_km = Column(Float, nullable=True)
    pallets = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    settlement = relationship("DriverSettlement", back_populates="settlement_items")
    dispatch = relationship("Dispatch", back_populates="settlement_items")
    
    def __repr__(self):
        return f"<DriverSettlementItem(settlement_id={self.settlement_id}, dispatch_id={self.dispatch_id})>"
