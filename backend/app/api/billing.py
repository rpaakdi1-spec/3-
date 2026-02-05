"""
Billing API
청구 및 정산 API 엔드포인트
Phase 3-B Week 1: 청구/정산 자동화
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.billing import BillingCycleType, BillingStatus, PaymentMethod
from app.services.billing_service import BillingService, DriverSettlementService


router = APIRouter(prefix="/billing", tags=["Billing"])


# ============= Schemas =============

class BillingPolicyCreate(BaseModel):
    """청구 정책 생성"""
    billing_cycle: BillingCycleType = BillingCycleType.MONTHLY
    billing_day: Optional[int] = 1
    payment_terms_days: int = 30
    base_rate_per_km: float = 2000.0
    base_rate_per_pallet: float = 5000.0
    base_rate_per_kg: float = 100.0
    weekend_surcharge_rate: float = 0.0
    night_surcharge_rate: float = 0.0
    express_surcharge_rate: float = 0.0
    temperature_control_rate: float = 0.0
    volume_discount_threshold: int = 0
    volume_discount_rate: float = 0.0


class BillingPolicyResponse(BaseModel):
    """청구 정책 응답"""
    id: int
    client_id: int
    billing_cycle: str
    billing_day: Optional[int]
    payment_terms_days: int
    base_rate_per_km: float
    base_rate_per_pallet: float
    base_rate_per_kg: float
    weekend_surcharge_rate: float
    night_surcharge_rate: float
    express_surcharge_rate: float
    temperature_control_rate: float
    volume_discount_threshold: int
    volume_discount_rate: float
    is_active: bool


class InvoiceGenerateRequest(BaseModel):
    """청구서 생성 요청"""
    client_id: int
    start_date: date
    end_date: date
    auto_send: bool = False


class InvoiceResponse(BaseModel):
    """청구서 응답"""
    id: int
    invoice_number: str
    client_id: int
    billing_period_start: date
    billing_period_end: date
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    paid_amount: float
    status: str
    issue_date: date
    due_date: date
    paid_date: Optional[date]


class PaymentRecordRequest(BaseModel):
    """결제 기록 요청"""
    amount: float = Field(..., gt=0)
    payment_method: PaymentMethod
    payment_date: date
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class DriverSettlementResponse(BaseModel):
    """기사 정산 응답"""
    id: int
    settlement_number: str
    driver_id: int
    settlement_period_start: date
    settlement_period_end: date
    total_revenue: float
    commission_amount: float
    net_amount: float
    dispatch_count: int
    total_distance_km: float
    is_paid: bool
    paid_date: Optional[date]


# ============= Endpoints =============

@router.get("/policies/{client_id}", response_model=BillingPolicyResponse)
async def get_billing_policy(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    거래처 청구 정책 조회
    
    - 거래처별 청구 설정
    - 요금 체계 및 할증/할인 정책
    """
    service = BillingService(db)
    policy = service.get_or_create_billing_policy(client_id)
    
    return {
        "id": policy.id,
        "client_id": policy.client_id,
        "billing_cycle": policy.billing_cycle.value,
        "billing_day": policy.billing_day,
        "payment_terms_days": policy.payment_terms_days,
        "base_rate_per_km": policy.base_rate_per_km,
        "base_rate_per_pallet": policy.base_rate_per_pallet,
        "base_rate_per_kg": policy.base_rate_per_kg,
        "weekend_surcharge_rate": policy.weekend_surcharge_rate,
        "night_surcharge_rate": policy.night_surcharge_rate,
        "express_surcharge_rate": policy.express_surcharge_rate,
        "temperature_control_rate": policy.temperature_control_rate,
        "volume_discount_threshold": policy.volume_discount_threshold,
        "volume_discount_rate": policy.volume_discount_rate,
        "is_active": policy.is_active
    }


@router.post("/policies/{client_id}")
async def update_billing_policy(
    client_id: int,
    policy_data: BillingPolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    청구 정책 업데이트
    
    - 요금 설정 변경
    - 할증/할인 정책 수정
    """
    from app.models.billing import BillingPolicy
    
    policy = db.query(BillingPolicy).filter(
        BillingPolicy.client_id == client_id,
        BillingPolicy.is_active == True
    ).first()
    
    if not policy:
        # 새로 생성
        policy = BillingPolicy(client_id=client_id)
        db.add(policy)
    
    # 업데이트
    for field, value in policy_data.dict().items():
        setattr(policy, field, value)
    
    db.commit()
    db.refresh(policy)
    
    return {"success": True, "message": "청구 정책이 업데이트되었습니다"}


@router.post("/invoices/generate", response_model=InvoiceResponse)
async def generate_invoice(
    request: InvoiceGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    청구서 생성
    
    - 지정 기간의 완료 배차 기반 자동 생성
    - 요금 자동 계산 및 할증/할인 적용
    - 부가세 자동 계산
    """
    service = BillingService(db)
    
    invoice = service.generate_invoice_for_client(
        client_id=request.client_id,
        start_date=request.start_date,
        end_date=request.end_date,
        auto_send=request.auto_send
    )
    
    if not invoice:
        raise HTTPException(status_code=404, detail="청구할 배차가 없습니다")
    
    return {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "client_id": invoice.client_id,
        "billing_period_start": invoice.billing_period_start,
        "billing_period_end": invoice.billing_period_end,
        "subtotal": invoice.subtotal,
        "tax_amount": invoice.tax_amount,
        "discount_amount": invoice.discount_amount,
        "total_amount": invoice.total_amount,
        "paid_amount": invoice.paid_amount,
        "status": invoice.status.value,
        "issue_date": invoice.issue_date,
        "due_date": invoice.due_date,
        "paid_date": invoice.paid_date
    }


@router.post("/invoices/generate-monthly")
async def generate_monthly_invoices(
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    월간 청구서 일괄 생성
    
    - 모든 거래처 대상
    - 해당 월의 완료 배차 기반
    """
    service = BillingService(db)
    invoices = service.generate_monthly_invoices(year, month)
    
    return {
        "success": True,
        "message": f"{year}년 {month}월 청구서 {len(invoices)}건 생성 완료",
        "invoice_count": len(invoices),
        "invoices": [
            {
                "invoice_number": inv.invoice_number,
                "client_id": inv.client_id,
                "total_amount": inv.total_amount
            }
            for inv in invoices
        ]
    }


@router.get("/invoices")
async def list_invoices(
    client_id: Optional[int] = Query(None),
    status: Optional[BillingStatus] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    청구서 목록 조회
    
    - 거래처별 필터
    - 상태별 필터
    - 기간별 필터
    """
    from app.models.billing import Invoice
    from sqlalchemy import and_
    
    query = db.query(Invoice)
    
    conditions = []
    if client_id:
        conditions.append(Invoice.client_id == client_id)
    if status:
        conditions.append(Invoice.status == status)
    if start_date:
        conditions.append(Invoice.issue_date >= start_date)
    if end_date:
        conditions.append(Invoice.issue_date <= end_date)
    
    if conditions:
        query = query.filter(and_(*conditions))
    
    total = query.count()
    invoices = query.order_by(Invoice.issue_date.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "invoices": [
            {
                "id": inv.id,
                "invoice_number": inv.invoice_number,
                "client_id": inv.client_id,
                "client_name": inv.client.name if inv.client else None,
                "total_amount": inv.total_amount,
                "paid_amount": inv.paid_amount,
                "status": inv.status.value,
                "issue_date": inv.issue_date,
                "due_date": inv.due_date
            }
            for inv in invoices
        ]
    }


@router.get("/invoices/{invoice_id}")
async def get_invoice_detail(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    청구서 상세 조회
    
    - 청구 항목 포함
    - 결제 이력 포함
    """
    from app.models.billing import Invoice
    
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="청구서를 찾을 수 없습니다")
    
    return {
        "invoice": {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "client_id": invoice.client_id,
            "client_name": invoice.client.name if invoice.client else None,
            "billing_period_start": invoice.billing_period_start,
            "billing_period_end": invoice.billing_period_end,
            "subtotal": invoice.subtotal,
            "tax_amount": invoice.tax_amount,
            "discount_amount": invoice.discount_amount,
            "total_amount": invoice.total_amount,
            "paid_amount": invoice.paid_amount,
            "status": invoice.status.value,
            "issue_date": invoice.issue_date,
            "due_date": invoice.due_date,
            "paid_date": invoice.paid_date
        },
        "line_items": [
            {
                "id": item.id,
                "description": item.description,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "amount": item.amount,
                "distance_km": item.distance_km,
                "pallets": item.pallets,
                "surcharge_amount": item.surcharge_amount,
                "discount_amount": item.discount_amount
            }
            for item in invoice.line_items
        ],
        "payments": [
            {
                "id": payment.id,
                "payment_number": payment.payment_number,
                "amount": payment.amount,
                "payment_method": payment.payment_method.value,
                "payment_date": payment.payment_date,
                "reference_number": payment.reference_number
            }
            for payment in invoice.payments
        ]
    }


@router.post("/invoices/{invoice_id}/payments")
async def record_payment(
    invoice_id: int,
    payment_data: PaymentRecordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    결제 기록
    
    - 결제 금액 및 방법 기록
    - 청구서 상태 자동 업데이트
    """
    service = BillingService(db)
    
    try:
        payment = service.record_payment(
            invoice_id=invoice_id,
            amount=payment_data.amount,
            payment_method=payment_data.payment_method,
            payment_date=payment_data.payment_date,
            reference_number=payment_data.reference_number,
            notes=payment_data.notes
        )
        
        return {
            "success": True,
            "message": "결제가 기록되었습니다",
            "payment": {
                "payment_number": payment.payment_number,
                "amount": payment.amount,
                "payment_method": payment.payment_method.value,
                "payment_date": payment.payment_date
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/invoices/overdue/list")
async def get_overdue_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    연체 청구서 조회
    
    - 결제 기한 초과 청구서
    - 미수금 관리용
    """
    service = BillingService(db)
    invoices = service.get_overdue_invoices()
    
    return {
        "total": len(invoices),
        "overdue_invoices": [
            {
                "id": inv.id,
                "invoice_number": inv.invoice_number,
                "client_id": inv.client_id,
                "client_name": inv.client.name if inv.client else None,
                "total_amount": inv.total_amount,
                "paid_amount": inv.paid_amount,
                "outstanding_amount": inv.total_amount - inv.paid_amount,
                "due_date": inv.due_date,
                "days_overdue": (date.today() - inv.due_date).days
            }
            for inv in invoices
        ]
    }


@router.get("/invoices/summary")
async def get_invoice_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    청구서 요약 통계
    
    - 총 청구 금액
    - 결제 금액
    - 미수금
    - 상태별 분류
    """
    service = BillingService(db)
    summary = service.get_invoice_summary(start_date, end_date)
    
    return summary


# ============= Driver Settlement Endpoints =============

@router.post("/settlements/generate")
async def generate_driver_settlement(
    driver_id: int,
    start_date: date,
    end_date: date,
    commission_rate: float = Query(15.0, ge=0, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    기사 정산 생성
    
    - 지정 기간의 완료 배차 기반
    - 수수료 자동 계산
    """
    service = DriverSettlementService(db)
    
    settlement = service.generate_driver_settlement(
        driver_id=driver_id,
        start_date=start_date,
        end_date=end_date,
        commission_rate=commission_rate
    )
    
    if not settlement:
        raise HTTPException(status_code=404, detail="정산할 배차가 없습니다")
    
    return {
        "success": True,
        "settlement": {
            "settlement_number": settlement.settlement_number,
            "driver_id": settlement.driver_id,
            "total_revenue": settlement.total_revenue,
            "commission_amount": settlement.commission_amount,
            "net_amount": settlement.net_amount,
            "dispatch_count": settlement.dispatch_count
        }
    }


@router.post("/settlements/generate-monthly")
async def generate_monthly_settlements(
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    commission_rate: float = Query(15.0, ge=0, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    월간 기사 정산 일괄 생성
    
    - 모든 기사 대상
    - 수수료 일괄 적용
    """
    service = DriverSettlementService(db)
    settlements = service.generate_monthly_settlements(year, month, commission_rate)
    
    return {
        "success": True,
        "message": f"{year}년 {month}월 정산 {len(settlements)}건 생성 완료",
        "settlement_count": len(settlements),
        "settlements": [
            {
                "settlement_number": stl.settlement_number,
                "driver_id": stl.driver_id,
                "net_amount": stl.net_amount
            }
            for stl in settlements
        ]
    }


@router.get("/settlements")
async def list_settlements(
    driver_id: Optional[int] = Query(None),
    is_paid: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    기사 정산 목록 조회
    """
    from app.models.billing import DriverSettlement
    
    query = db.query(DriverSettlement)
    
    if driver_id:
        query = query.filter(DriverSettlement.driver_id == driver_id)
    if is_paid is not None:
        query = query.filter(DriverSettlement.is_paid == is_paid)
    
    total = query.count()
    settlements = query.order_by(DriverSettlement.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "settlements": [
            {
                "id": stl.id,
                "settlement_number": stl.settlement_number,
                "driver_id": stl.driver_id,
                "driver_name": stl.driver.name if stl.driver else None,
                "total_revenue": stl.total_revenue,
                "commission_amount": stl.commission_amount,
                "net_amount": stl.net_amount,
                "dispatch_count": stl.dispatch_count,
                "is_paid": stl.is_paid,
                "paid_date": stl.paid_date
            }
            for stl in settlements
        ]
    }


@router.post("/settlements/{settlement_id}/mark-paid")
async def mark_settlement_paid(
    settlement_id: int,
    paid_date: date,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    정산 지급 완료 처리
    """
    service = DriverSettlementService(db)
    
    try:
        settlement = service.mark_settlement_paid(settlement_id, paid_date, notes)
        
        return {
            "success": True,
            "message": "정산 지급이 완료되었습니다",
            "settlement_number": settlement.settlement_number
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
