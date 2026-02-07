"""
Phase 8: 결제/정산 시스템 강화 - Service
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, case, extract
from typing import Optional, List, Dict, Any, Tuple
from datetime import date, datetime, timedelta
from decimal import Decimal
import uuid
import logging

from app.models.billing import (
    BillingPolicy, Invoice, InvoiceLineItem, Payment,
    DriverSettlement, DriverSettlementItem,
    BillingStatus, PaymentMethod, BillingCycleType
)
from app.models.billing_enhanced import (
    TaxInvoice, TaxInvoiceStatus,
    AutoInvoiceSchedule,
    SettlementApproval, SettlementApprovalStatus, SettlementApprovalHistory,
    PaymentReminder, PaymentReminderType, PaymentReminderStatus,
    ExportTask, ExportTaskStatus
)
from app.models.dispatch import Dispatch, DispatchStatus
from app.models.client import Client
from app.models.driver import Driver
from app.services.billing_service import BillingService

logger = logging.getLogger(__name__)


class BillingEnhancedService:
    """강화된 청구 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.billing_service = BillingService(db)
    
    # ============= 요금 미리보기 =============
    
    def preview_charge(
        self,
        client_id: int,
        dispatch_date: date,
        total_distance_km: float,
        pallets: int = 0,
        weight_kg: Optional[float] = None,
        vehicle_type: Optional[str] = None,
        is_urgent: bool = False
    ) -> Dict[str, Any]:
        """
        요금 미리보기 계산
        
        프론트엔드에서 실시간으로 요금을 확인할 수 있도록 합니다.
        """
        # 청구 정책 조회
        policy = self.billing_service.get_or_create_billing_policy(client_id)
        
        # 기본 요금 계산
        base_distance_charge = total_distance_km * policy.base_rate_per_km
        base_pallet_charge = pallets * policy.base_rate_per_pallet
        base_weight_charge = (weight_kg * policy.base_rate_per_kg) if weight_kg else 0.0
        subtotal = base_distance_charge + base_pallet_charge + base_weight_charge
        
        # 할증 계산
        weekend_surcharge = 0.0
        if dispatch_date.weekday() >= 5:  # 주말
            weekend_surcharge = subtotal * (policy.weekend_surcharge_rate / 100)
        
        express_surcharge = 0.0
        if is_urgent:
            express_surcharge = subtotal * (policy.express_surcharge_rate / 100)
        
        temperature_control_charge = 0.0
        if vehicle_type and vehicle_type in ['냉동', '냉장']:
            temperature_control_charge = policy.temperature_control_rate
        
        total_surcharge = weekend_surcharge + express_surcharge + temperature_control_charge
        
        # 할인 계산 (월간 배차 건수 기반)
        volume_discount = 0.0
        if policy.volume_discount_threshold > 0:
            month_start = date(dispatch_date.year, dispatch_date.month, 1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            dispatch_count = self.db.query(func.count(Dispatch.id)).filter(
                and_(
                    Dispatch.dispatch_date >= month_start,
                    Dispatch.dispatch_date <= month_end,
                    Dispatch.status.in_([DispatchStatus.COMPLETED, DispatchStatus.IN_PROGRESS])
                )
            ).scalar() or 0
            
            if dispatch_count >= policy.volume_discount_threshold:
                volume_discount = (subtotal + total_surcharge) * (policy.volume_discount_rate / 100)
        
        total_discount = volume_discount
        subtotal_after_discount = subtotal + total_surcharge - total_discount
        
        # 부가세 (10%)
        tax_amount = subtotal_after_discount * 0.1
        total_amount = subtotal_after_discount + tax_amount
        
        # 응답 구성
        breakdown = {
            'base_distance_charge': round(base_distance_charge, 2),
            'base_pallet_charge': round(base_pallet_charge, 2),
            'base_weight_charge': round(base_weight_charge, 2),
            'subtotal': round(subtotal, 2),
            'weekend_surcharge': round(weekend_surcharge, 2),
            'night_surcharge': 0.0,  # 추후 구현
            'express_surcharge': round(express_surcharge, 2),
            'temperature_control_charge': round(temperature_control_charge, 2),
            'total_surcharge': round(total_surcharge, 2),
            'volume_discount': round(volume_discount, 2),
            'special_discount': 0.0,
            'total_discount': round(total_discount, 2),
            'subtotal_after_discount': round(subtotal_after_discount, 2),
            'tax_amount': round(tax_amount, 2),
            'total_amount': round(total_amount, 2)
        }
        
        policy_info = {
            'billing_cycle': policy.billing_cycle.value,
            'base_rate_per_km': policy.base_rate_per_km,
            'base_rate_per_pallet': policy.base_rate_per_pallet,
            'base_rate_per_kg': policy.base_rate_per_kg,
            'weekend_surcharge_rate': policy.weekend_surcharge_rate,
            'express_surcharge_rate': policy.express_surcharge_rate,
            'volume_discount_rate': policy.volume_discount_rate
        }
        
        notes = []
        if dispatch_date.weekday() >= 5:
            notes.append(f"주말 배차로 {policy.weekend_surcharge_rate}% 할증이 적용됩니다.")
        if is_urgent:
            notes.append(f"긴급 배차로 {policy.express_surcharge_rate}% 할증이 적용됩니다.")
        if volume_discount > 0:
            notes.append(f"월간 물량 할인 {policy.volume_discount_rate}%가 적용되었습니다.")
        
        return {
            'client_id': client_id,
            'dispatch_date': dispatch_date,
            'breakdown': breakdown,
            'policy_info': policy_info,
            'notes': notes
        }
    
    # ============= 자동 청구서 생성 스케줄 =============
    
    def create_auto_invoice_schedule(
        self,
        client_id: int,
        enabled: bool = True,
        billing_day: int = 1,
        auto_send_email: bool = False,
        send_reminder: bool = True,
        reminder_days: List[int] = [7, 3, 0]
    ) -> AutoInvoiceSchedule:
        """자동 청구서 생성 스케줄 생성"""
        # 기존 스케줄 확인
        existing = self.db.query(AutoInvoiceSchedule).filter(
            AutoInvoiceSchedule.client_id == client_id
        ).first()
        
        if existing:
            # 업데이트
            existing.enabled = enabled
            existing.billing_day = billing_day
            existing.auto_send_email = auto_send_email
            existing.send_reminder = send_reminder
            existing.reminder_days = reminder_days
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        # 신규 생성
        schedule = AutoInvoiceSchedule(
            client_id=client_id,
            enabled=enabled,
            billing_day=billing_day,
            auto_send_email=auto_send_email,
            send_reminder=send_reminder,
            reminder_days=reminder_days
        )
        
        # 다음 생성일 계산
        today = date.today()
        next_date = date(today.year, today.month, billing_day)
        if next_date <= today:
            # 다음 달로
            if today.month == 12:
                next_date = date(today.year + 1, 1, billing_day)
            else:
                next_date = date(today.year, today.month + 1, billing_day)
        
        schedule.next_generation_date = next_date
        
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        
        logger.info(f"자동 청구서 스케줄 생성: client_id={client_id}, next_date={next_date}")
        return schedule
    
    def get_auto_invoice_schedules_due(self, target_date: Optional[date] = None) -> List[AutoInvoiceSchedule]:
        """오늘 실행해야 할 자동 청구서 스케줄 조회"""
        if target_date is None:
            target_date = date.today()
        
        schedules = self.db.query(AutoInvoiceSchedule).filter(
            and_(
                AutoInvoiceSchedule.enabled == True,
                AutoInvoiceSchedule.next_generation_date <= target_date
            )
        ).all()
        
        return schedules
    
    def execute_auto_invoice_schedule(self, schedule: AutoInvoiceSchedule) -> Optional[Invoice]:
        """자동 청구서 스케줄 실행"""
        try:
            # 이전 달 청구서 생성
            today = date.today()
            start_date = date(today.year, today.month, 1) - timedelta(days=1)  # 이전 달 마지막 날
            start_date = date(start_date.year, start_date.month, 1)  # 이전 달 첫날
            end_date = date(today.year, today.month, 1) - timedelta(days=1)  # 이전 달 마지막 날
            
            # 청구서 생성
            invoice = self.billing_service.generate_invoice_for_client(
                client_id=schedule.client_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # 스케줄 업데이트
            schedule.last_generated_at = datetime.now()
            schedule.last_generated_invoice_id = invoice.id
            schedule.error_count = 0
            schedule.last_error = None
            
            # 다음 생성일 계산
            if today.month == 12:
                next_date = date(today.year + 1, 1, schedule.billing_day)
            else:
                next_date = date(today.year, today.month + 1, schedule.billing_day)
            schedule.next_generation_date = next_date
            
            self.db.commit()
            
            logger.info(f"자동 청구서 생성 완료: invoice_id={invoice.id}, client_id={schedule.client_id}")
            
            # 이메일 자동 발송
            if schedule.auto_send_email:
                # TODO: 이메일 발송 로직
                pass
            
            return invoice
            
        except Exception as e:
            schedule.error_count += 1
            schedule.last_error = str(e)
            self.db.commit()
            logger.error(f"자동 청구서 생성 실패: client_id={schedule.client_id}, error={str(e)}")
            return None
    
    # ============= 정산 승인 워크플로우 =============
    
    def create_settlement_approval(
        self,
        settlement_id: int,
        submitted_by: Optional[int] = None
    ) -> SettlementApproval:
        """정산 승인 레코드 생성"""
        approval = SettlementApproval(
            settlement_id=settlement_id,
            status=SettlementApprovalStatus.PENDING,
            submitted_by=submitted_by,
            submitted_at=datetime.now() if submitted_by else None
        )
        
        self.db.add(approval)
        
        # 이력 추가
        history = SettlementApprovalHistory(
            settlement_id=settlement_id,
            action="created",
            actor_id=submitted_by,
            notes="정산서 생성"
        )
        self.db.add(history)
        
        self.db.commit()
        self.db.refresh(approval)
        
        return approval
    
    def approve_settlement(
        self,
        settlement_id: int,
        approved_by: int,
        notes: Optional[str] = None
    ) -> SettlementApproval:
        """정산 승인"""
        approval = self.db.query(SettlementApproval).filter(
            SettlementApproval.settlement_id == settlement_id
        ).first()
        
        if not approval:
            raise ValueError("승인 레코드를 찾을 수 없습니다")
        
        if approval.status != SettlementApprovalStatus.PENDING:
            raise ValueError("승인 대기 상태가 아닙니다")
        
        # 승인 처리
        approval.status = SettlementApprovalStatus.APPROVED
        approval.approved_by = approved_by
        approval.approved_at = datetime.now()
        approval.approval_notes = notes
        
        # 이력 추가
        history = SettlementApprovalHistory(
            settlement_id=settlement_id,
            action="approved",
            actor_id=approved_by,
            notes=notes
        )
        self.db.add(history)
        
        self.db.commit()
        self.db.refresh(approval)
        
        logger.info(f"정산 승인 완료: settlement_id={settlement_id}, approved_by={approved_by}")
        
        return approval
    
    def reject_settlement(
        self,
        settlement_id: int,
        rejected_by: int,
        reason: str
    ) -> SettlementApproval:
        """정산 반려"""
        approval = self.db.query(SettlementApproval).filter(
            SettlementApproval.settlement_id == settlement_id
        ).first()
        
        if not approval:
            raise ValueError("승인 레코드를 찾을 수 없습니다")
        
        if approval.status != SettlementApprovalStatus.PENDING:
            raise ValueError("승인 대기 상태가 아닙니다")
        
        # 반려 처리
        approval.status = SettlementApprovalStatus.REJECTED
        approval.rejected_by = rejected_by
        approval.rejected_at = datetime.now()
        approval.rejection_reason = reason
        
        # 이력 추가
        history = SettlementApprovalHistory(
            settlement_id=settlement_id,
            action="rejected",
            actor_id=rejected_by,
            notes=reason
        )
        self.db.add(history)
        
        self.db.commit()
        self.db.refresh(approval)
        
        logger.info(f"정산 반려 완료: settlement_id={settlement_id}, rejected_by={rejected_by}")
        
        return approval
    
    def get_settlement_approval_history(self, settlement_id: int) -> List[SettlementApprovalHistory]:
        """정산 승인 이력 조회"""
        return self.db.query(SettlementApprovalHistory).filter(
            SettlementApprovalHistory.settlement_id == settlement_id
        ).order_by(SettlementApprovalHistory.created_at.desc()).all()
    
    # ============= 결제 알림 =============
    
    def create_payment_reminder(
        self,
        invoice_id: int,
        reminder_type: PaymentReminderType,
        days_until_due: Optional[int] = None,
        channels: List[str] = ["email"]
    ) -> PaymentReminder:
        """결제 알림 생성"""
        reminder = PaymentReminder(
            invoice_id=invoice_id,
            reminder_type=reminder_type,
            days_until_due=days_until_due,
            channels=channels,
            status=PaymentReminderStatus.PENDING
        )
        
        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)
        
        return reminder
    
    def get_reminders_to_send(self, target_date: Optional[date] = None) -> List[PaymentReminder]:
        """발송할 알림 조회"""
        if target_date is None:
            target_date = date.today()
        
        # 아직 발송하지 않은 알림들 중 발송 조건에 맞는 것들
        reminders = self.db.query(PaymentReminder).join(Invoice).filter(
            and_(
                PaymentReminder.status == PaymentReminderStatus.PENDING,
                Invoice.status.in_([BillingStatus.SENT, BillingStatus.OVERDUE]),
                or_(
                    # 결제일 전 알림
                    and_(
                        PaymentReminder.reminder_type == PaymentReminderType.BEFORE_DUE,
                        Invoice.due_date == target_date + timedelta(days=PaymentReminder.days_until_due)
                    ),
                    # 결제일 당일 알림
                    and_(
                        PaymentReminder.reminder_type == PaymentReminderType.DUE_DATE,
                        Invoice.due_date == target_date
                    ),
                    # 연체 알림
                    and_(
                        PaymentReminder.reminder_type == PaymentReminderType.OVERDUE,
                        Invoice.due_date < target_date
                    )
                )
            )
        ).all()
        
        return reminders
    
    def mark_reminder_sent(self, reminder_id: int, channels_sent: Dict[str, bool]) -> PaymentReminder:
        """알림 발송 완료 처리"""
        reminder = self.db.query(PaymentReminder).get(reminder_id)
        if not reminder:
            raise ValueError("알림을 찾을 수 없습니다")
        
        reminder.status = PaymentReminderStatus.SENT
        reminder.sent_at = datetime.now()
        reminder.email_sent = channels_sent.get('email', False)
        reminder.sms_sent = channels_sent.get('sms', False)
        reminder.push_sent = channels_sent.get('push', False)
        
        self.db.commit()
        self.db.refresh(reminder)
        
        return reminder
    
    # ============= 재무 대시보드 =============
    
    def get_financial_summary(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """재무 요약 조회"""
        # 매출 집계
        invoices = self.db.query(Invoice).filter(
            and_(
                Invoice.issue_date >= start_date,
                Invoice.issue_date <= end_date
            )
        ).all()
        
        total_revenue = sum(inv.total_amount for inv in invoices)
        invoiced_amount = total_revenue
        collected_amount = sum(inv.paid_amount for inv in invoices)
        collection_rate = (collected_amount / total_revenue * 100) if total_revenue > 0 else 0
        
        # 미수금
        total_receivables = sum(inv.total_amount - inv.paid_amount for inv in invoices)
        overdue_invoices = [inv for inv in invoices if inv.due_date < date.today() and inv.status != BillingStatus.PAID]
        overdue_receivables = sum(inv.total_amount - inv.paid_amount for inv in overdue_invoices)
        current_receivables = total_receivables - overdue_receivables
        
        # 정산
        settlements = self.db.query(DriverSettlement).filter(
            and_(
                DriverSettlement.settlement_period_end >= start_date,
                DriverSettlement.settlement_period_end <= end_date
            )
        ).all()
        
        total_settlements = sum(s.net_amount for s in settlements)
        paid_settlements = sum(s.net_amount for s in settlements if s.is_paid)
        pending_settlements = total_settlements - paid_settlements
        
        # 현금 흐름
        cash_in = collected_amount
        cash_out = paid_settlements
        net_cash_flow = cash_in - cash_out
        
        return {
            'period_start': start_date,
            'period_end': end_date,
            'total_revenue': round(total_revenue, 2),
            'invoiced_amount': round(invoiced_amount, 2),
            'collected_amount': round(collected_amount, 2),
            'collection_rate': round(collection_rate, 2),
            'total_receivables': round(total_receivables, 2),
            'current_receivables': round(current_receivables, 2),
            'overdue_receivables': round(overdue_receivables, 2),
            'overdue_count': len(overdue_invoices),
            'total_settlements': round(total_settlements, 2),
            'pending_settlements': round(pending_settlements, 2),
            'paid_settlements': round(paid_settlements, 2),
            'cash_in': round(cash_in, 2),
            'cash_out': round(cash_out, 2),
            'net_cash_flow': round(net_cash_flow, 2)
        }
    
    def get_monthly_trends(
        self,
        start_date: date,
        end_date: date,
        months: int = 12
    ) -> List[Dict[str, Any]]:
        """월별 추이 조회"""
        trends = []
        
        current_date = start_date
        while current_date <= end_date and len(trends) < months:
            month_start = date(current_date.year, current_date.month, 1)
            if current_date.month == 12:
                month_end = date(current_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = date(current_date.year, current_date.month + 1, 1) - timedelta(days=1)
            
            summary = self.get_financial_summary(month_start, month_end)
            
            trends.append({
                'month': month_start.strftime('%Y-%m'),
                'revenue': summary['total_revenue'],
                'collected': summary['collected_amount'],
                'settlements': summary['paid_settlements'],
                'net_profit': summary['collected_amount'] - summary['paid_settlements']
            })
            
            # 다음 달로
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)
        
        return trends
    
    # ============= Excel/PDF 내보내기 =============
    
    def create_export_task(
        self,
        export_type: str,
        format: str,
        user_id: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> ExportTask:
        """내보내기 작업 생성"""
        task_id = str(uuid.uuid4())
        
        task = ExportTask(
            task_id=task_id,
            export_type=export_type,
            format=format,
            user_id=user_id,
            filters=filters or {},
            status=ExportTaskStatus.PENDING
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        logger.info(f"내보내기 작업 생성: task_id={task_id}, type={export_type}, format={format}")
        
        return task
    
    def get_export_task(self, task_id: str) -> Optional[ExportTask]:
        """내보내기 작업 조회"""
        return self.db.query(ExportTask).filter(ExportTask.task_id == task_id).first()
