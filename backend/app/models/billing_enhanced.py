"""
Phase 8: 결제/정산 시스템 강화 - 추가 모델
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Date, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.models.base import Base


# ============= 전자세금계산서 =============

class TaxInvoiceStatus(str, enum.Enum):
    """전자세금계산서 상태"""
    PENDING = "PENDING"      # 대기
    ISSUED = "ISSUED"        # 발행됨
    CANCELLED = "CANCELLED"  # 취소됨
    FAILED = "FAILED"        # 실패


class TaxInvoice(Base):
    """전자세금계산서"""
    __tablename__ = "tax_invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, unique=True, index=True)
    tax_invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # 공급자 정보
    supplier_registration_number = Column(String(20), nullable=False)  # 사업자등록번호
    supplier_company_name = Column(String(200), nullable=False)
    supplier_ceo_name = Column(String(100), nullable=False)
    supplier_address = Column(String(500), nullable=False)
    supplier_business_type = Column(String(100), nullable=True)
    supplier_business_item = Column(String(100), nullable=True)
    
    # 공급받는자 정보
    buyer_registration_number = Column(String(20), nullable=False)
    buyer_company_name = Column(String(200), nullable=False)
    buyer_ceo_name = Column(String(100), nullable=False)
    buyer_address = Column(String(500), nullable=False)
    buyer_email = Column(String(200), nullable=True)
    buyer_business_type = Column(String(100), nullable=True)
    buyer_business_item = Column(String(100), nullable=True)
    
    # 금액 정보
    supply_amount = Column(Float, nullable=False)  # 공급가액
    tax_amount = Column(Float, nullable=False)  # 세액
    total_amount = Column(Float, nullable=False)  # 합계
    
    # 발행 정보
    issue_date = Column(Date, nullable=False)
    issue_type = Column(String(20), default="정발행")  # 정발행/역발행
    
    # 상태
    status = Column(SQLEnum(TaxInvoiceStatus), default=TaxInvoiceStatus.PENDING)
    
    # 국세청 연동 정보
    nts_confirm_number = Column(String(50), nullable=True)  # 국세청 승인번호
    nts_response = Column(JSON, nullable=True)  # 국세청 응답
    
    # 외부 API 정보
    api_provider = Column(String(50), nullable=True)  # barobill, popbill 등
    api_request_id = Column(String(100), nullable=True)
    api_response = Column(JSON, nullable=True)
    
    # 메타데이터
    remarks = Column(Text, nullable=True)
    issued_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    invoice = relationship("Invoice", back_populates="tax_invoice")
    
    def __repr__(self):
        return f"<TaxInvoice(number={self.tax_invoice_number}, status={self.status})>"


# ============= 자동 청구서 생성 스케줄 =============

class AutoInvoiceSchedule(Base):
    """자동 청구서 생성 스케줄"""
    __tablename__ = "auto_invoice_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, unique=True, index=True)
    
    # 스케줄 설정
    enabled = Column(Boolean, default=True)
    billing_day = Column(Integer, nullable=False)  # 청구일 (1-28)
    auto_send_email = Column(Boolean, default=False)
    send_reminder = Column(Boolean, default=True)
    reminder_days = Column(JSON, default=[7, 3, 0])  # 알림 발송일 목록
    
    # 실행 이력
    last_generated_at = Column(DateTime(timezone=True), nullable=True)
    last_generated_invoice_id = Column(Integer, nullable=True)
    next_generation_date = Column(Date, nullable=True)
    
    # 에러 추적
    last_error = Column(Text, nullable=True)
    error_count = Column(Integer, default=0)
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client")
    
    def __repr__(self):
        return f"<AutoInvoiceSchedule(client_id={self.client_id}, enabled={self.enabled})>"


# ============= 정산 승인 워크플로우 =============

class SettlementApprovalStatus(str, enum.Enum):
    """정산 승인 상태"""
    PENDING = "PENDING"      # 승인 대기
    APPROVED = "APPROVED"    # 승인됨
    REJECTED = "REJECTED"    # 반려됨


class SettlementApproval(Base):
    """정산 승인"""
    __tablename__ = "settlement_approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    settlement_id = Column(Integer, ForeignKey("driver_settlements.id"), nullable=False, unique=True, index=True)
    
    # 승인 상태
    status = Column(SQLEnum(SettlementApprovalStatus), default=SettlementApprovalStatus.PENDING)
    
    # 승인자 정보
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # 반려 정보
    rejected_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    settlement = relationship("DriverSettlement", back_populates="approval")
    submitter = relationship("User", foreign_keys=[submitted_by])
    approver = relationship("User", foreign_keys=[approved_by])
    rejecter = relationship("User", foreign_keys=[rejected_by])
    
    def __repr__(self):
        return f"<SettlementApproval(settlement_id={self.settlement_id}, status={self.status})>"


class SettlementApprovalHistory(Base):
    """정산 승인 이력"""
    __tablename__ = "settlement_approval_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    settlement_id = Column(Integer, ForeignKey("driver_settlements.id"), nullable=False, index=True)
    
    # 액션 정보
    action = Column(String(50), nullable=False)  # created, submitted, approved, rejected, paid
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    settlement = relationship("DriverSettlement")
    actor = relationship("User")
    
    def __repr__(self):
        return f"<SettlementApprovalHistory(settlement_id={self.settlement_id}, action={self.action})>"


# ============= 결제 알림 =============

class PaymentReminderType(str, enum.Enum):
    """결제 알림 유형"""
    BEFORE_DUE = "BEFORE_DUE"  # 결제일 전
    DUE_DATE = "DUE_DATE"      # 결제일 당일
    OVERDUE = "OVERDUE"        # 연체


class PaymentReminderStatus(str, enum.Enum):
    """결제 알림 상태"""
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


class PaymentReminder(Base):
    """결제 알림"""
    __tablename__ = "payment_reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    
    # 알림 정보
    reminder_type = Column(SQLEnum(PaymentReminderType), nullable=False)
    days_until_due = Column(Integer, nullable=True)  # 결제일까지 남은 일수 (음수면 연체일수)
    
    # 발송 채널
    channels = Column(JSON, default=["email"])  # email, sms, push
    
    # 상태
    status = Column(SQLEnum(PaymentReminderStatus), default=PaymentReminderStatus.PENDING)
    
    # 발송 정보
    sent_at = Column(DateTime(timezone=True), nullable=True)
    email_sent = Column(Boolean, default=False)
    sms_sent = Column(Boolean, default=False)
    push_sent = Column(Boolean, default=False)
    
    # 에러 추적
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    invoice = relationship("Invoice")
    
    def __repr__(self):
        return f"<PaymentReminder(invoice_id={self.invoice_id}, type={self.reminder_type})>"


# ============= Excel/PDF 내보내기 작업 =============

class ExportTaskStatus(str, enum.Enum):
    """내보내기 작업 상태"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ExportTask(Base):
    """내보내기 작업"""
    __tablename__ = "export_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # 작업 정보
    export_type = Column(String(50), nullable=False)  # invoice, settlement, transaction
    format = Column(String(20), nullable=False)  # excel, pdf
    
    # 필터 조건
    filters = Column(JSON, nullable=True)
    
    # 사용자
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 상태
    status = Column(SQLEnum(ExportTaskStatus), default=ExportTaskStatus.PENDING)
    
    # 결과
    file_path = Column(String(500), nullable=True)
    file_url = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # 에러 추적
    error_message = Column(Text, nullable=True)
    
    # 메타데이터
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<ExportTask(task_id={self.task_id}, status={self.status})>"
