"""
Phase 8: 결제/정산 시스템 강화 - API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.billing_enhanced import (
    ChargePreviewRequest, ChargePreviewResponse,
    AutoInvoiceScheduleCreate, AutoInvoiceScheduleResponse,
    SettlementApprovalRequest, SettlementApprovalResponse,
    PaymentReminderCreate, PaymentReminderResponse,
    FinancialSummaryResponse, MonthlyTrendResponse, TopClientResponse,
    InvoiceExportRequest, ExportResponse,
    InvoiceDetailResponse, SettlementDetailResponse,
    BillingStatisticsResponse, SettlementStatisticsResponse
)
from app.services.billing_enhanced_service import BillingEnhancedService
from app.services.export_service import financial_report_exporter
from app.models.billing_enhanced import PaymentReminderType

router = APIRouter(prefix="/billing/enhanced", tags=["Billing Enhanced"])


# ============= 요금 미리보기 =============

@router.post("/preview", response_model=ChargePreviewResponse)
async def preview_charge(
    request: ChargePreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    실시간 요금 미리보기
    
    프론트엔드에서 배차 등록 시 실시간으로 예상 요금을 확인할 수 있습니다.
    - 거리, 팔레트, 날짜 등을 기반으로 요금 계산
    - 할증/할인 상세 표시
    - 적용된 청구 정책 정보 제공
    """
    service = BillingEnhancedService(db)
    
    preview = service.preview_charge(
        client_id=request.client_id,
        dispatch_date=request.dispatch_date,
        total_distance_km=request.total_distance_km,
        pallets=request.pallets,
        weight_kg=request.weight_kg,
        vehicle_type=request.vehicle_type,
        is_urgent=request.is_urgent
    )
    
    return preview


# ============= 자동 청구서 생성 스케줄 =============

@router.post("/auto-schedule", response_model=AutoInvoiceScheduleResponse)
async def create_auto_invoice_schedule(
    request: AutoInvoiceScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    자동 청구서 생성 스케줄 설정
    
    특정 고객에 대해 매월 자동으로 청구서를 생성하도록 설정합니다.
    - 청구일 지정 (1-28일)
    - 이메일 자동 발송 여부
    - 결제 알림 설정
    """
    service = BillingEnhancedService(db)
    
    schedule = service.create_auto_invoice_schedule(
        client_id=request.client_id,
        enabled=request.enabled,
        billing_day=request.billing_day,
        auto_send_email=request.auto_send_email,
        send_reminder=request.send_reminder,
        reminder_days=request.reminder_days
    )
    
    return schedule


@router.get("/auto-schedule/{client_id}", response_model=AutoInvoiceScheduleResponse)
async def get_auto_invoice_schedule(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """고객의 자동 청구서 생성 스케줄 조회"""
    from app.models.billing_enhanced import AutoInvoiceSchedule
    
    schedule = db.query(AutoInvoiceSchedule).filter(
        AutoInvoiceSchedule.client_id == client_id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="스케줄을 찾을 수 없습니다")
    
    return schedule


@router.get("/auto-schedule", response_model=List[AutoInvoiceScheduleResponse])
async def list_auto_invoice_schedules(
    enabled: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """자동 청구서 생성 스케줄 목록 조회"""
    from app.models.billing_enhanced import AutoInvoiceSchedule
    
    query = db.query(AutoInvoiceSchedule)
    
    if enabled is not None:
        query = query.filter(AutoInvoiceSchedule.enabled == enabled)
    
    schedules = query.all()
    return schedules


@router.post("/auto-schedule/execute-due")
async def execute_due_auto_invoices(
    background_tasks: BackgroundTasks,
    target_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    오늘 실행해야 할 자동 청구서 생성 (스케줄러용)
    
    매일 자동으로 실행되어야 하는 엔드포인트입니다.
    """
    service = BillingEnhancedService(db)
    
    if target_date is None:
        target_date = date.today()
    
    schedules = service.get_auto_invoice_schedules_due(target_date)
    
    results = []
    for schedule in schedules:
        invoice = service.execute_auto_invoice_schedule(schedule)
        results.append({
            'client_id': schedule.client_id,
            'success': invoice is not None,
            'invoice_id': invoice.id if invoice else None,
            'error': schedule.last_error if not invoice else None
        })
    
    return {
        'target_date': target_date,
        'schedules_processed': len(schedules),
        'results': results
    }


# ============= 정산 승인 워크플로우 =============

@router.post("/settlement-approval", response_model=SettlementApprovalResponse)
async def process_settlement_approval(
    request: SettlementApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    정산 승인/반려 처리
    
    관리자가 기사 정산서를 검토하고 승인/반려합니다.
    """
    service = BillingEnhancedService(db)
    
    if request.action == "approve":
        approval = service.approve_settlement(
            settlement_id=request.settlement_id,
            approved_by=current_user.id,
            notes=request.notes
        )
    elif request.action == "reject":
        if not request.notes:
            raise HTTPException(status_code=400, detail="반려 사유를 입력해주세요")
        approval = service.reject_settlement(
            settlement_id=request.settlement_id,
            rejected_by=current_user.id,
            reason=request.notes
        )
    else:
        raise HTTPException(status_code=400, detail="유효하지 않은 액션입니다")
    
    return approval


@router.get("/settlement-approval/{settlement_id}", response_model=SettlementApprovalResponse)
async def get_settlement_approval(
    settlement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """정산 승인 상태 조회"""
    from app.models.billing_enhanced import SettlementApproval
    
    approval = db.query(SettlementApproval).filter(
        SettlementApproval.settlement_id == settlement_id
    ).first()
    
    if not approval:
        raise HTTPException(status_code=404, detail="승인 레코드를 찾을 수 없습니다")
    
    return approval


@router.get("/settlement-approval", response_model=List[SettlementApprovalResponse])
async def list_settlement_approvals(
    status: Optional[str] = Query(None, description="필터: pending, approved, rejected"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """정산 승인 목록 조회"""
    from app.models.billing_enhanced import SettlementApproval
    
    query = db.query(SettlementApproval)
    
    if status:
        query = query.filter(SettlementApproval.status == status)
    
    approvals = query.order_by(SettlementApproval.created_at.desc()).limit(limit).all()
    
    return approvals


@router.get("/settlement-approval/{settlement_id}/history")
async def get_settlement_approval_history(
    settlement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """정산 승인 이력 조회"""
    service = BillingEnhancedService(db)
    
    history = service.get_settlement_approval_history(settlement_id)
    
    return {
        'settlement_id': settlement_id,
        'history': [
            {
                'id': h.id,
                'action': h.action,
                'actor_id': h.actor_id,
                'notes': h.notes,
                'created_at': h.created_at
            }
            for h in history
        ]
    }


# ============= 결제 알림 =============

@router.get("/payment-reminder", response_model=List[PaymentReminderResponse])
async def list_payment_reminders(
    status: Optional[str] = Query(None, description="필터: pending, sent, failed"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """결제 알림 목록 조회"""
    from app.models.billing_enhanced import PaymentReminder
    
    query = db.query(PaymentReminder)
    
    if status:
        query = query.filter(PaymentReminder.status == status)
    
    reminders = query.order_by(PaymentReminder.created_at.desc()).limit(limit).all()
    
    return reminders


@router.post("/payment-reminder", response_model=PaymentReminderResponse)
async def create_payment_reminder(
    request: PaymentReminderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """결제 알림 생성"""
    service = BillingEnhancedService(db)
    
    reminder = service.create_payment_reminder(
        invoice_id=request.invoice_id,
        reminder_type=getattr(PaymentReminderType, request.reminder_type),
        days_until_due=request.days_until_due,
        channels=request.channels
    )
    
    return reminder


@router.post("/payment-reminder/send-due")
async def send_due_payment_reminders(
    background_tasks: BackgroundTasks,
    target_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    오늘 발송해야 할 결제 알림 처리 (스케줄러용)
    
    매일 자동으로 실행되어야 하는 엔드포인트입니다.
    """
    service = BillingEnhancedService(db)
    
    if target_date is None:
        target_date = date.today()
    
    reminders = service.get_reminders_to_send(target_date)
    
    results = []
    for reminder in reminders:
        # TODO: 실제 이메일/SMS/Push 발송 로직
        channels_sent = {
            'email': 'email' in reminder.channels,
            'sms': 'sms' in reminder.channels,
            'push': 'push' in reminder.channels
        }
        
        service.mark_reminder_sent(reminder.id, channels_sent)
        
        results.append({
            'reminder_id': reminder.id,
            'invoice_id': reminder.invoice_id,
            'reminder_type': reminder.reminder_type.value,
            'channels': reminder.channels
        })
    
    return {
        'target_date': target_date,
        'reminders_sent': len(results),
        'results': results
    }


# ============= 재무 대시보드 =============

@router.get("/dashboard/financial", response_model=FinancialSummaryResponse)
async def get_financial_dashboard(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    재무 대시보드 - 요약 정보
    
    매출, 미수금, 정산, 현금 흐름 등을 한눈에 확인할 수 있습니다.
    """
    if start_date is None:
        start_date = date.today().replace(day=1)  # 이번 달 1일
    if end_date is None:
        end_date = date.today()
    
    service = BillingEnhancedService(db)
    
    summary = service.get_financial_summary(start_date, end_date)
    
    return summary


@router.get("/dashboard/trends", response_model=List[MonthlyTrendResponse])
async def get_monthly_trends(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    months: int = Query(12, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    월별 추이 조회
    
    최근 N개월의 매출/수금/정산 추이를 차트로 표시할 수 있습니다.
    """
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=365)  # 1년 전
    
    service = BillingEnhancedService(db)
    
    trends = service.get_monthly_trends(start_date, end_date, months)
    
    return trends


@router.get("/dashboard/top-clients", response_model=List[TopClientResponse])
async def get_top_clients(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """주요 고객 매출 순위"""
    if start_date is None:
        start_date = date.today().replace(day=1)
    if end_date is None:
        end_date = date.today()
    
    from app.models.billing import Invoice
    from app.models.client import Client
    from sqlalchemy import func, and_
    
    # 고객별 매출 집계
    results = db.query(
        Client.id,
        Client.name,
        func.sum(Invoice.total_amount).label('total_revenue'),
        func.count(Invoice.id).label('invoice_count'),
        (func.sum(Invoice.paid_amount) / func.sum(Invoice.total_amount) * 100).label('collection_rate')
    ).join(Invoice).filter(
        and_(
            Invoice.issue_date >= start_date,
            Invoice.issue_date <= end_date
        )
    ).group_by(Client.id, Client.name).order_by(
        func.sum(Invoice.total_amount).desc()
    ).limit(limit).all()
    
    return [
        {
            'client_id': r[0],
            'client_name': r[1],
            'total_revenue': round(r[2], 2),
            'invoice_count': r[3],
            'collection_rate': round(r[4], 2) if r[4] else 0.0
        }
        for r in results
    ]


# ============= Excel/PDF 내보내기 =============

@router.get("/export", response_model=List[ExportResponse])
async def list_export_tasks(
    status: Optional[str] = Query(None, description="필터: pending, processing, completed, failed"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """내보내기 작업 목록 조회"""
    from app.models.billing_enhanced import ExportTask
    
    query = db.query(ExportTask).filter(ExportTask.user_id == current_user.id)
    
    if status:
        query = query.filter(ExportTask.status == status)
    
    tasks = query.order_by(ExportTask.created_at.desc()).limit(limit).all()
    
    return tasks


@router.post("/export", response_model=ExportResponse)
async def create_export_task(
    request: InvoiceExportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    청구서/정산서 내보내기
    
    Excel 또는 PDF 형식으로 데이터를 내보냅니다.
    작업은 백그라운드에서 처리되며, task_id로 진행 상황을 확인할 수 있습니다.
    """
    service = BillingEnhancedService(db)
    
    filters = {}
    if request.invoice_ids:
        filters['invoice_ids'] = request.invoice_ids
    if request.start_date:
        filters['start_date'] = request.start_date
    if request.end_date:
        filters['end_date'] = request.end_date
    if request.client_id:
        filters['client_id'] = request.client_id
    if request.status:
        filters['status'] = request.status
    
    task = service.create_export_task(
        export_type="invoice",
        format=request.format,
        user_id=current_user.id,
        filters=filters
    )
    
    # TODO: 백그라운드 작업으로 실제 파일 생성
    # background_tasks.add_task(generate_export_file, task.task_id, db)
    
    return {
        'task_id': task.task_id,
        'status': task.status.value,
        'file_url': task.file_url,
        'created_at': task.created_at
    }


@router.get("/export/{task_id}", response_model=ExportResponse)
async def get_export_task_status(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """내보내기 작업 상태 조회"""
    service = BillingEnhancedService(db)
    
    task = service.get_export_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    return {
        'task_id': task.task_id,
        'status': task.status.value,
        'file_url': task.file_url,
        'created_at': task.created_at
    }


# ============= 통계 =============

@router.get("/statistics/billing")
async def get_billing_statistics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """청구 통계"""
    if start_date is None:
        start_date = date.today().replace(day=1)
    if end_date is None:
        end_date = date.today()
    
    from app.models.billing import Invoice, BillingStatus
    from sqlalchemy import func, and_
    
    # 전체 청구서 집계
    total_invoices = db.query(func.count(Invoice.id)).filter(
        and_(
            Invoice.issue_date >= start_date,
            Invoice.issue_date <= end_date
        )
    ).scalar()
    
    total_amount = db.query(func.sum(Invoice.total_amount)).filter(
        and_(
            Invoice.issue_date >= start_date,
            Invoice.issue_date <= end_date
        )
    ).scalar() or 0.0
    
    average_amount = total_amount / total_invoices if total_invoices > 0 else 0.0
    
    # 상태별 집계
    by_status = {}
    for status in BillingStatus:
        count = db.query(func.count(Invoice.id)).filter(
            and_(
                Invoice.issue_date >= start_date,
                Invoice.issue_date <= end_date,
                Invoice.status == status
            )
        ).scalar()
        
        amount = db.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.issue_date >= start_date,
                Invoice.issue_date <= end_date,
                Invoice.status == status
            )
        ).scalar() or 0.0
        
        by_status[status.value] = {
            'count': count,
            'amount': round(amount, 2)
        }
    
    # 수금 효율
    collected = db.query(func.sum(Invoice.paid_amount)).filter(
        and_(
            Invoice.issue_date >= start_date,
            Invoice.issue_date <= end_date
        )
    ).scalar() or 0.0
    
    collection_efficiency = (collected / total_amount * 100) if total_amount > 0 else 0.0
    
    return {
        'period_start': start_date,
        'period_end': end_date,
        'total_invoices': total_invoices,
        'total_amount': round(total_amount, 2),
        'average_amount': round(average_amount, 2),
        'by_status': by_status,
        'collection_efficiency': round(collection_efficiency, 2)
    }


@router.get("/statistics/settlement")
async def get_settlement_statistics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """정산 통계"""
    if start_date is None:
        start_date = date.today().replace(day=1)
    if end_date is None:
        end_date = date.today()
    
    from app.models.billing import DriverSettlement
    from app.models.billing_enhanced import SettlementApproval, SettlementApprovalStatus
    from sqlalchemy import func, and_
    
    # 전체 정산 집계
    total_settlements = db.query(func.count(DriverSettlement.id)).filter(
        and_(
            DriverSettlement.settlement_period_end >= start_date,
            DriverSettlement.settlement_period_end <= end_date
        )
    ).scalar()
    
    total_amount = db.query(func.sum(DriverSettlement.net_amount)).filter(
        and_(
            DriverSettlement.settlement_period_end >= start_date,
            DriverSettlement.settlement_period_end <= end_date
        )
    ).scalar() or 0.0
    
    average_amount = total_amount / total_settlements if total_settlements > 0 else 0.0
    
    # 승인 통계
    approved_count = db.query(func.count(SettlementApproval.id)).join(DriverSettlement).filter(
        and_(
            DriverSettlement.settlement_period_end >= start_date,
            DriverSettlement.settlement_period_end <= end_date,
            SettlementApproval.status == SettlementApprovalStatus.APPROVED
        )
    ).scalar() or 0
    
    approval_rate = (approved_count / total_settlements * 100) if total_settlements > 0 else 0.0
    
    return {
        'period_start': start_date,
        'period_end': end_date,
        'total_settlements': total_settlements,
        'total_amount': round(total_amount, 2),
        'average_amount': round(average_amount, 2),
        'approved_count': approved_count,
        'approval_rate': round(approval_rate, 2)
    }


# ============= 재무 대시보드 보고서 다운로드 =============

@router.get("/export/financial-dashboard/excel")
async def export_financial_dashboard_excel(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    months: int = Query(12, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    재무 대시보드 Excel 다운로드
    
    현재 대시보드에 표시된 모든 데이터를 Excel 파일로 내보냅니다.
    - 재무 요약 (4개 카드)
    - 월별 추이 (차트 데이터)
    - TOP 10 거래처
    """
    # 날짜 기본값 설정
    if start_date is None:
        start_date = date.today().replace(day=1)  # 이번 달 1일
    if end_date is None:
        end_date = date.today()
    
    service = BillingEnhancedService(db)
    
    # 1. 재무 요약 데이터
    summary = service.get_financial_summary(start_date, end_date)
    
    # 2. 월별 추이 데이터
    trends = service.get_monthly_trends(start_date, end_date, months)
    
    # 3. TOP 10 거래처 데이터
    from app.models.billing import Invoice
    from app.models.client import Client
    from sqlalchemy import func, and_
    
    top_clients_query = db.query(
        Client.id,
        Client.name,
        func.sum(Invoice.total_amount).label('total_revenue'),
        func.count(Invoice.id).label('invoice_count'),
        (func.sum(Invoice.paid_amount) / func.sum(Invoice.total_amount) * 100).label('collection_rate')
    ).join(Invoice).filter(
        and_(
            Invoice.issue_date >= start_date,
            Invoice.issue_date <= end_date
        )
    ).group_by(Client.id, Client.name).order_by(
        func.sum(Invoice.total_amount).desc()
    ).limit(10).all()
    
    top_clients = [
        {
            'client_id': r[0],
            'client_name': r[1],
            'total_revenue': round(r[2], 2),
            'invoice_count': r[3],
            'collection_rate': round(r[4], 2) if r[4] else 0.0
        }
        for r in top_clients_query
    ]
    
    # Excel 파일 생성
    excel_file = financial_report_exporter.generate_excel(
        summary_data={
            'total_revenue': summary.total_revenue,
            'collected_amount': summary.collected_amount,
            'collection_rate': summary.collection_rate,
            'overdue_amount': summary.overdue_amount,
            'overdue_count': summary.overdue_count,
            'pending_settlement': summary.pending_settlement
        },
        monthly_trends=[
            {
                'month': t.month,
                'revenue': t.revenue,
                'collected': t.collected,
                'profit': t.profit
            }
            for t in trends
        ],
        top_clients=top_clients,
        start_date=start_date,
        end_date=end_date
    )
    
    # 파일명 생성
    filename = f"재무대시보드_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.xlsx"
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
        }
    )


@router.get("/export/financial-dashboard/pdf")
async def export_financial_dashboard_pdf(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    months: int = Query(12, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    재무 대시보드 PDF 다운로드
    
    현재 대시보드에 표시된 모든 데이터를 PDF 파일로 내보냅니다.
    - 재무 요약 (4개 카드)
    - 월별 추이 (테이블)
    - TOP 10 거래처
    """
    # 날짜 기본값 설정
    if start_date is None:
        start_date = date.today().replace(day=1)
    if end_date is None:
        end_date = date.today()
    
    service = BillingEnhancedService(db)
    
    # 1. 재무 요약 데이터
    summary = service.get_financial_summary(start_date, end_date)
    
    # 2. 월별 추이 데이터
    trends = service.get_monthly_trends(start_date, end_date, months)
    
    # 3. TOP 10 거래처 데이터
    from app.models.billing import Invoice
    from app.models.client import Client
    from sqlalchemy import func, and_
    
    top_clients_query = db.query(
        Client.id,
        Client.name,
        func.sum(Invoice.total_amount).label('total_revenue'),
        func.count(Invoice.id).label('invoice_count'),
        (func.sum(Invoice.paid_amount) / func.sum(Invoice.total_amount) * 100).label('collection_rate')
    ).join(Invoice).filter(
        and_(
            Invoice.issue_date >= start_date,
            Invoice.issue_date <= end_date
        )
    ).group_by(Client.id, Client.name).order_by(
        func.sum(Invoice.total_amount).desc()
    ).limit(10).all()
    
    top_clients = [
        {
            'client_id': r[0],
            'client_name': r[1],
            'total_revenue': round(r[2], 2),
            'invoice_count': r[3],
            'collection_rate': round(r[4], 2) if r[4] else 0.0
        }
        for r in top_clients_query
    ]
    
    # PDF 파일 생성
    pdf_file = financial_report_exporter.generate_pdf(
        summary_data={
            'total_revenue': summary.total_revenue,
            'collected_amount': summary.collected_amount,
            'collection_rate': summary.collection_rate,
            'overdue_amount': summary.overdue_amount,
            'overdue_count': summary.overdue_count,
            'pending_settlement': summary.pending_settlement
        },
        monthly_trends=[
            {
                'month': t.month,
                'revenue': t.revenue,
                'collected': t.collected,
                'profit': t.profit
            }
            for t in trends
        ],
        top_clients=top_clients,
        start_date=start_date,
        end_date=end_date
    )
    
    # 파일명 생성
    filename = f"재무대시보드_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
    
    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
        }
    )
