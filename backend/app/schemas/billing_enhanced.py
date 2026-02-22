"""
Phase 8: 결제/정산 시스템 강화 - 스키마
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal


# ============= 요금 미리보기 =============

class ChargePreviewRequest(BaseModel):
    """요금 미리보기 요청"""
    client_id: int = Field(..., description="고객 ID")
    dispatch_date: date = Field(..., description="배차 날짜")
    total_distance_km: float = Field(..., ge=0, description="총 거리 (km)")
    pallets: int = Field(0, ge=0, description="팔레트 수")
    weight_kg: Optional[float] = Field(None, ge=0, description="무게 (kg)")
    vehicle_type: Optional[str] = Field(None, description="차량 타입 (냉동/냉장)")
    is_urgent: bool = Field(False, description="긴급 배차 여부")
    
    @validator('dispatch_date')
    def validate_dispatch_date(cls, v):
        if v < date.today():
            raise ValueError('배차 날짜는 오늘 이후여야 합니다')
        return v


class ChargeBreakdown(BaseModel):
    """요금 상세 내역"""
    base_distance_charge: float = Field(..., description="거리 기본 요금")
    base_pallet_charge: float = Field(..., description="팔레트 기본 요금")
    base_weight_charge: float = Field(0.0, description="무게 기본 요금")
    subtotal: float = Field(..., description="소계")
    
    # 할증
    weekend_surcharge: float = Field(0.0, description="주말 할증")
    night_surcharge: float = Field(0.0, description="야간 할증")
    express_surcharge: float = Field(0.0, description="긴급 할증")
    temperature_control_charge: float = Field(0.0, description="온도 관리 요금")
    total_surcharge: float = Field(..., description="총 할증")
    
    # 할인
    volume_discount: float = Field(0.0, description="물량 할인")
    special_discount: float = Field(0.0, description="특별 할인")
    total_discount: float = Field(..., description="총 할인")
    
    # 최종
    subtotal_after_discount: float = Field(..., description="할인 후 소계")
    tax_amount: float = Field(..., description="부가세 (10%)")
    total_amount: float = Field(..., description="최종 금액")


class ChargePreviewResponse(BaseModel):
    """요금 미리보기 응답"""
    client_id: int
    dispatch_date: date
    breakdown: ChargeBreakdown
    policy_info: Dict[str, Any] = Field(..., description="적용된 청구 정책 정보")
    notes: List[str] = Field(default_factory=list, description="안내 사항")


# ============= 자동 청구서 생성 =============

class AutoInvoiceScheduleCreate(BaseModel):
    """자동 청구서 생성 스케줄 설정"""
    client_id: int = Field(..., description="고객 ID")
    enabled: bool = Field(True, description="스케줄 활성화 여부")
    billing_day: int = Field(..., ge=1, le=28, description="청구일 (1-28)")
    auto_send_email: bool = Field(False, description="이메일 자동 발송")
    send_reminder: bool = Field(True, description="결제 알림 발송")
    reminder_days: List[int] = Field([7, 3, 0], description="알림 발송일 (D-day)")


class AutoInvoiceScheduleResponse(BaseModel):
    """자동 청구서 생성 스케줄 응답"""
    id: int
    client_id: int
    enabled: bool
    billing_day: int
    auto_send_email: bool
    send_reminder: bool
    reminder_days: List[int]
    last_generated_at: Optional[datetime]
    next_generation_date: Optional[date]
    created_at: datetime
    updated_at: datetime


# ============= 정산 승인 워크플로우 =============

class SettlementApprovalRequest(BaseModel):
    """정산 승인/반려 요청"""
    settlement_id: int = Field(..., description="정산서 ID")
    action: str = Field(..., description="승인 액션 (approve/reject)")
    notes: Optional[str] = Field(None, description="승인/반려 사유")
    
    @validator('action')
    def validate_action(cls, v):
        if v not in ['approve', 'reject']:
            raise ValueError('action은 approve 또는 reject만 가능합니다')
        return v


class SettlementApprovalResponse(BaseModel):
    """정산 승인 응답"""
    settlement_id: int
    status: str
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    approval_notes: Optional[str]


class SettlementApprovalHistory(BaseModel):
    """정산 승인 이력"""
    id: int
    settlement_id: int
    action: str  # created, submitted, approved, rejected, paid
    actor_id: Optional[int]
    actor_name: Optional[str]
    notes: Optional[str]
    created_at: datetime


# ============= 전자세금계산서 =============

class TaxInvoiceIssueRequest(BaseModel):
    """전자세금계산서 발행 요청"""
    invoice_id: int = Field(..., description="청구서 ID")
    supplier_registration_number: str = Field(..., description="공급자 사업자등록번호")
    supplier_company_name: str = Field(..., description="공급자 상호")
    supplier_ceo_name: str = Field(..., description="공급자 대표자명")
    supplier_address: str = Field(..., description="공급자 주소")
    
    buyer_registration_number: str = Field(..., description="공급받는자 사업자등록번호")
    buyer_company_name: str = Field(..., description="공급받는자 상호")
    buyer_ceo_name: str = Field(..., description="공급받는자 대표자명")
    buyer_address: str = Field(..., description="공급받는자 주소")
    buyer_email: str = Field(..., description="공급받는자 이메일")
    
    issue_type: str = Field("정발행", description="발행 유형 (정발행/역발행)")
    remarks: Optional[str] = Field(None, description="비고")


class TaxInvoiceResponse(BaseModel):
    """전자세금계산서 응답"""
    id: int
    invoice_id: int
    tax_invoice_number: str
    issue_date: date
    supply_amount: float  # 공급가액
    tax_amount: float  # 세액
    total_amount: float  # 합계
    status: str  # pending, issued, cancelled
    nts_confirm_number: Optional[str]  # 국세청 승인번호
    issued_at: Optional[datetime]
    cancelled_at: Optional[datetime]


# ============= 결제 알림 =============

class PaymentReminderCreate(BaseModel):
    """결제 알림 생성"""
    invoice_id: int = Field(..., description="청구서 ID")
    reminder_type: str = Field(..., description="알림 유형 (before/due/overdue)")
    days_until_due: Optional[int] = Field(None, description="결제일까지 남은 일수")
    channels: List[str] = Field(["email"], description="알림 채널 (email/sms/push)")


class PaymentReminderResponse(BaseModel):
    """결제 알림 응답"""
    id: int
    invoice_id: int
    reminder_type: str
    sent_at: datetime
    channels: List[str]
    status: str  # sent, failed, pending


# ============= 재무 대시보드 =============

class FinancialSummaryResponse(BaseModel):
    """재무 요약 대시보드"""
    period_start: date
    period_end: date
    
    # 매출
    total_revenue: float = Field(..., description="총 매출")
    invoiced_amount: float = Field(..., description="청구 금액")
    collected_amount: float = Field(..., description="수금 금액")
    collection_rate: float = Field(..., description="수금률 (%)")
    
    # 미수금
    total_receivables: float = Field(..., description="총 미수금")
    current_receivables: float = Field(..., description="정상 미수금")
    overdue_receivables: float = Field(..., description="연체 미수금")
    overdue_count: int = Field(..., description="연체 건수")
    
    # 정산
    total_settlements: float = Field(..., description="총 정산 금액")
    pending_settlements: float = Field(..., description="정산 대기 금액")
    paid_settlements: float = Field(..., description="지급 완료 금액")
    
    # 현금 흐름
    cash_in: float = Field(..., description="현금 유입")
    cash_out: float = Field(..., description="현금 유출")
    net_cash_flow: float = Field(..., description="순 현금 흐름")


class MonthlyTrendResponse(BaseModel):
    """월별 추이"""
    month: str  # YYYY-MM
    revenue: float
    collected: float
    settlements: float
    net_profit: float


class TopClientResponse(BaseModel):
    """주요 고객 매출"""
    client_id: int
    client_name: str
    total_revenue: float
    total_collected: float
    invoice_count: int
    collection_rate: float


# ============= Excel/PDF 내보내기 =============

class InvoiceExportRequest(BaseModel):
    """청구서 내보내기 요청"""
    invoice_ids: Optional[List[int]] = Field(None, description="청구서 ID 목록 (없으면 전체)")
    start_date: Optional[date] = Field(None, description="시작 날짜")
    end_date: Optional[date] = Field(None, description="종료 날짜")
    client_id: Optional[int] = Field(None, description="특정 고객")
    status: Optional[str] = Field(None, description="청구서 상태")
    format: str = Field("excel", description="내보내기 형식 (excel/pdf)")
    include_details: bool = Field(True, description="상세 항목 포함 여부")


class ExportResponse(BaseModel):
    """내보내기 응답"""
    task_id: str = Field(..., description="작업 ID")
    status: str = Field(..., description="작업 상태")
    file_url: Optional[str] = Field(None, description="다운로드 URL")
    created_at: datetime


# ============= 청구서 상세 조회 향상 =============

class InvoiceDetailResponse(BaseModel):
    """청구서 상세 응답 (향상)"""
    id: int
    invoice_number: str
    client_id: int
    client_name: str
    
    # 청구 기간
    billing_period_start: date
    billing_period_end: date
    issue_date: date
    due_date: date
    
    # 금액
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    paid_amount: float
    balance: float
    
    # 상태
    status: str
    is_overdue: bool
    days_overdue: Optional[int]
    
    # 항목
    line_items: List[Dict[str, Any]]
    
    # 결제 이력
    payment_history: List[Dict[str, Any]]
    
    # 전자세금계산서
    tax_invoice: Optional[TaxInvoiceResponse]
    
    # 메타
    created_at: datetime
    updated_at: datetime
    notes: Optional[str]


class SettlementDetailResponse(BaseModel):
    """정산서 상세 응답 (향상)"""
    id: int
    settlement_number: str
    driver_id: int
    driver_name: str
    
    # 정산 기간
    period_start: date
    period_end: date
    
    # 금액
    total_amount: float
    paid_amount: float
    balance: float
    
    # 상태
    status: str
    approval_status: str  # pending, approved, rejected
    
    # 항목
    line_items: List[Dict[str, Any]]
    
    # 승인 이력
    approval_history: List[SettlementApprovalHistory]
    
    # 메타
    created_at: datetime
    approved_at: Optional[datetime]
    paid_at: Optional[datetime]
    notes: Optional[str]


# ============= 통계 =============

class BillingStatisticsResponse(BaseModel):
    """청구 통계"""
    period_start: date
    period_end: date
    
    total_invoices: int
    total_amount: float
    average_amount: float
    
    by_status: Dict[str, Dict[str, Any]]  # {status: {count, amount}}
    by_client: List[TopClientResponse]
    
    payment_methods: Dict[str, int]  # {method: count}
    collection_efficiency: float  # 수금 효율


class SettlementStatisticsResponse(BaseModel):
    """정산 통계"""
    period_start: date
    period_end: date
    
    total_settlements: int
    total_amount: float
    average_amount: float
    
    by_status: Dict[str, Dict[str, Any]]
    by_driver: List[Dict[str, Any]]
    
    approval_rate: float
    average_approval_days: float
