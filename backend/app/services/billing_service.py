"""
Billing Service
청구 및 정산 서비스
Phase 3-B Week 1: 청구/정산 자동화
"""
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import logging

from app.models.billing import (
    BillingPolicy, Invoice, InvoiceLineItem, Payment,
    DriverSettlement, DriverSettlementItem,
    BillingCycleType, BillingStatus, PaymentMethod
)
from app.models.dispatch import Dispatch
from app.models.client import Client
from app.models.driver import Driver

logger = logging.getLogger(__name__)


class BillingService:
    """청구 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_billing_policy(self, client_id: int) -> BillingPolicy:
        """
        청구 정책 조회 또는 생성
        
        Args:
            client_id: 거래처 ID
            
        Returns:
            BillingPolicy 객체
        """
        policy = self.db.query(BillingPolicy).filter(
            and_(
                BillingPolicy.client_id == client_id,
                BillingPolicy.is_active == True
            )
        ).first()
        
        if not policy:
            # 기본 정책 생성
            policy = BillingPolicy(
                client_id=client_id,
                billing_cycle=BillingCycleType.MONTHLY,
                billing_day=1,
                payment_terms_days=30,
                base_rate_per_km=2000.0,
                base_rate_per_pallet=5000.0,
                base_rate_per_kg=100.0,
                is_active=True
            )
            self.db.add(policy)
            self.db.commit()
            self.db.refresh(policy)
            logger.info(f"기본 청구 정책 생성: client_id={client_id}")
        
        return policy
    
    def generate_invoice_number(self) -> str:
        """
        청구서 번호 생성
        
        Returns:
            청구서 번호 (INV-YYYYMMDD-NNNN)
        """
        today = datetime.now()
        prefix = f"INV-{today.strftime('%Y%m%d')}"
        
        # 오늘 날짜의 마지막 청구서 번호 조회
        last_invoice = self.db.query(Invoice).filter(
            Invoice.invoice_number.like(f"{prefix}%")
        ).order_by(desc(Invoice.invoice_number)).first()
        
        if last_invoice:
            last_number = int(last_invoice.invoice_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:04d}"
    
    def calculate_dispatch_charge(
        self,
        dispatch: Dispatch,
        policy: BillingPolicy
    ) -> Dict[str, float]:
        """
        배차 요금 계산
        
        Args:
            dispatch: 배차 객체
            policy: 청구 정책
            
        Returns:
            요금 정보 딕셔너리
        """
        # 기본 요금 계산
        base_amount = 0.0
        
        # 거리 기반
        if dispatch.total_distance_km:
            base_amount += dispatch.total_distance_km * policy.base_rate_per_km
        
        # 팔레트 기반
        total_pallets = 0
        for route in dispatch.routes:
            if route.order and route.order.pallets:
                total_pallets += route.order.pallets
        if total_pallets > 0:
            base_amount += total_pallets * policy.base_rate_per_pallet
        
        # 할증 계산
        surcharge_amount = 0.0
        
        # 주말 할증
        if dispatch.dispatch_date.weekday() >= 5:  # 토요일(5), 일요일(6)
            surcharge_amount += base_amount * (policy.weekend_surcharge_rate / 100)
        
        # 긴급 배차 할증 (예: 상태가 URGENT인 경우)
        if hasattr(dispatch, 'is_urgent') and dispatch.is_urgent:
            surcharge_amount += base_amount * (policy.express_surcharge_rate / 100)
        
        # 온도 관리 추가 요금 (냉동/냉장 차량)
        if dispatch.vehicle and dispatch.vehicle.vehicle_type in ['냉동', '냉장']:
            surcharge_amount += policy.temperature_control_rate
        
        # 할인 계산
        discount_amount = 0.0
        
        # 물량 할인 (월간 배차 건수 기준)
        if policy.volume_discount_threshold > 0:
            month_start = date(dispatch.dispatch_date.year, dispatch.dispatch_date.month, 1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            # 해당 월의 배차 건수 조회
            dispatch_count = self.db.query(func.count(Dispatch.id)).join(
                Dispatch.routes
            ).join(
                Dispatch.routes[0].order.delivery_client if dispatch.routes else None
            ).filter(
                and_(
                    Dispatch.dispatch_date >= month_start,
                    Dispatch.dispatch_date <= month_end,
                    Dispatch.status.in_(['COMPLETED', 'IN_PROGRESS'])
                )
            ).scalar()
            
            if dispatch_count >= policy.volume_discount_threshold:
                discount_amount = (base_amount + surcharge_amount) * (policy.volume_discount_rate / 100)
        
        total_amount = base_amount + surcharge_amount - discount_amount
        
        return {
            'base_amount': round(base_amount, 2),
            'surcharge_amount': round(surcharge_amount, 2),
            'discount_amount': round(discount_amount, 2),
            'total_amount': round(total_amount, 2)
        }
    
    def generate_invoice_for_client(
        self,
        client_id: int,
        start_date: date,
        end_date: date,
        auto_send: bool = False
    ) -> Invoice:
        """
        거래처별 청구서 자동 생성
        
        Args:
            client_id: 거래처 ID
            start_date: 청구 시작일
            end_date: 청구 종료일
            auto_send: 자동 발송 여부
            
        Returns:
            생성된 Invoice 객체
        """
        # 청구 정책 조회
        policy = self.get_or_create_billing_policy(client_id)
        
        # 해당 기간의 완료된 배차 조회
        dispatches = self.db.query(Dispatch).join(
            Dispatch.routes
        ).filter(
            and_(
                Dispatch.dispatch_date >= start_date,
                Dispatch.dispatch_date <= end_date,
                Dispatch.status == 'COMPLETED'
            )
        ).all()
        
        # 이미 청구된 배차 제외
        dispatches = [d for d in dispatches if not self._is_dispatch_invoiced(d.id)]
        
        if not dispatches:
            logger.warning(f"청구할 배차가 없습니다: client_id={client_id}, period={start_date}~{end_date}")
            return None
        
        # 청구서 생성
        invoice_number = self.generate_invoice_number()
        
        invoice = Invoice(
            invoice_number=invoice_number,
            client_id=client_id,
            billing_period_start=start_date,
            billing_period_end=end_date,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=policy.payment_terms_days),
            status=BillingStatus.DRAFT
        )
        
        self.db.add(invoice)
        self.db.flush()  # ID 생성
        
        # 청구 항목 생성
        subtotal = 0.0
        
        for dispatch in dispatches:
            charges = self.calculate_dispatch_charge(dispatch, policy)
            
            # 설명 생성
            description = f"배차번호: {dispatch.dispatch_number}"
            if dispatch.routes:
                route_info = []
                for route in dispatch.routes:
                    if route.order:
                        route_info.append(f"{route.order.pickup_address} → {route.order.delivery_address}")
                if route_info:
                    description += f" ({', '.join(route_info)})"
            
            line_item = InvoiceLineItem(
                invoice_id=invoice.id,
                dispatch_id=dispatch.id,
                description=description,
                quantity=1.0,
                unit_price=charges['total_amount'],
                amount=charges['total_amount'],
                distance_km=dispatch.total_distance_km,
                surcharge_amount=charges['surcharge_amount'],
                discount_amount=charges['discount_amount']
            )
            
            self.db.add(line_item)
            subtotal += charges['total_amount']
        
        # 총액 계산 (부가세 10%)
        tax_amount = subtotal * 0.1
        total_amount = subtotal + tax_amount
        
        invoice.subtotal = round(subtotal, 2)
        invoice.tax_amount = round(tax_amount, 2)
        invoice.total_amount = round(total_amount, 2)
        invoice.status = BillingStatus.PENDING if not auto_send else BillingStatus.SENT
        
        if auto_send:
            invoice.sent_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(invoice)
        
        logger.info(f"청구서 생성 완료: {invoice_number}, client_id={client_id}, amount={total_amount:,.0f}원")
        
        return invoice
    
    def _is_dispatch_invoiced(self, dispatch_id: int) -> bool:
        """배차가 이미 청구되었는지 확인"""
        return self.db.query(InvoiceLineItem).filter(
            InvoiceLineItem.dispatch_id == dispatch_id
        ).first() is not None
    
    def record_payment(
        self,
        invoice_id: int,
        amount: float,
        payment_method: PaymentMethod,
        payment_date: date,
        reference_number: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Payment:
        """
        결제 기록
        
        Args:
            invoice_id: 청구서 ID
            amount: 결제 금액
            payment_method: 결제 방법
            payment_date: 결제 날짜
            reference_number: 거래 참조 번호
            notes: 메모
            
        Returns:
            생성된 Payment 객체
        """
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            raise ValueError(f"청구서를 찾을 수 없습니다: invoice_id={invoice_id}")
        
        # 결제 번호 생성
        payment_number = f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        payment = Payment(
            payment_number=payment_number,
            invoice_id=invoice_id,
            amount=amount,
            payment_method=payment_method,
            payment_date=payment_date,
            reference_number=reference_number,
            notes=notes
        )
        
        self.db.add(payment)
        
        # 청구서 결제 금액 업데이트
        invoice.paid_amount += amount
        
        # 청구서 상태 업데이트
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = BillingStatus.PAID
            invoice.paid_date = payment_date
        elif invoice.paid_amount > 0:
            invoice.status = BillingStatus.PARTIAL
        
        self.db.commit()
        self.db.refresh(payment)
        
        logger.info(f"결제 기록 완료: {payment_number}, amount={amount:,.0f}원")
        
        return payment
    
    def get_overdue_invoices(self) -> List[Invoice]:
        """
        연체된 청구서 조회
        
        Returns:
            연체 청구서 리스트
        """
        today = date.today()
        
        invoices = self.db.query(Invoice).filter(
            and_(
                Invoice.status.in_([BillingStatus.SENT, BillingStatus.PARTIAL]),
                Invoice.due_date < today
            )
        ).all()
        
        # 상태를 OVERDUE로 업데이트
        for invoice in invoices:
            if invoice.status != BillingStatus.OVERDUE:
                invoice.status = BillingStatus.OVERDUE
        
        self.db.commit()
        
        return invoices
    
    def generate_monthly_invoices(self, year: int, month: int) -> List[Invoice]:
        """
        월간 청구서 일괄 생성
        
        Args:
            year: 연도
            month: 월
            
        Returns:
            생성된 청구서 리스트
        """
        start_date = date(year, month, 1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # 활성 거래처 조회
        clients = self.db.query(Client).filter(
            Client.is_active == True
        ).all()
        
        invoices = []
        
        for client in clients:
            try:
                invoice = self.generate_invoice_for_client(
                    client_id=client.id,
                    start_date=start_date,
                    end_date=end_date,
                    auto_send=False
                )
                
                if invoice:
                    invoices.append(invoice)
                    logger.info(f"월간 청구서 생성: client={client.name}, invoice={invoice.invoice_number}")
                
            except Exception as e:
                logger.error(f"청구서 생성 실패: client_id={client.id}, error={e}")
                continue
        
        logger.info(f"{year}년 {month}월 청구서 {len(invoices)}건 생성 완료")
        
        return invoices
    
    def get_invoice_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        청구서 요약 통계
        
        Args:
            start_date: 시작일
            end_date: 종료일
            
        Returns:
            통계 딕셔너리
        """
        query = self.db.query(Invoice)
        
        if start_date:
            query = query.filter(Invoice.issue_date >= start_date)
        if end_date:
            query = query.filter(Invoice.issue_date <= end_date)
        
        invoices = query.all()
        
        total_amount = sum(inv.total_amount for inv in invoices)
        paid_amount = sum(inv.paid_amount for inv in invoices)
        outstanding_amount = total_amount - paid_amount
        
        status_counts = {}
        for status in BillingStatus:
            count = sum(1 for inv in invoices if inv.status == status)
            status_counts[status.value] = count
        
        return {
            'total_invoices': len(invoices),
            'total_amount': round(total_amount, 2),
            'paid_amount': round(paid_amount, 2),
            'outstanding_amount': round(outstanding_amount, 2),
            'payment_rate': round((paid_amount / total_amount * 100) if total_amount > 0 else 0, 2),
            'status_breakdown': status_counts
        }


class DriverSettlementService:
    """기사 정산 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_settlement_number(self) -> str:
        """정산 번호 생성"""
        today = datetime.now()
        prefix = f"STL-{today.strftime('%Y%m%d')}"
        
        last_settlement = self.db.query(DriverSettlement).filter(
            DriverSettlement.settlement_number.like(f"{prefix}%")
        ).order_by(desc(DriverSettlement.settlement_number)).first()
        
        if last_settlement:
            last_number = int(last_settlement.settlement_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:04d}"
    
    def generate_driver_settlement(
        self,
        driver_id: int,
        start_date: date,
        end_date: date,
        commission_rate: float = 15.0
    ) -> DriverSettlement:
        """
        기사 정산 생성
        
        Args:
            driver_id: 기사 ID
            start_date: 정산 시작일
            end_date: 정산 종료일
            commission_rate: 수수료율 (%)
            
        Returns:
            생성된 DriverSettlement 객체
        """
        # 해당 기간의 완료된 배차 조회
        dispatches = self.db.query(Dispatch).filter(
            and_(
                Dispatch.driver_id == driver_id,
                Dispatch.dispatch_date >= start_date,
                Dispatch.dispatch_date <= end_date,
                Dispatch.status == 'COMPLETED'
            )
        ).all()
        
        # 이미 정산된 배차 제외
        dispatches = [d for d in dispatches if not self._is_dispatch_settled(d.id)]
        
        if not dispatches:
            logger.warning(f"정산할 배차가 없습니다: driver_id={driver_id}, period={start_date}~{end_date}")
            return None
        
        # 정산 생성
        settlement_number = self.generate_settlement_number()
        
        settlement = DriverSettlement(
            settlement_number=settlement_number,
            driver_id=driver_id,
            settlement_period_start=start_date,
            settlement_period_end=end_date,
            is_paid=False
        )
        
        self.db.add(settlement)
        self.db.flush()
        
        # 정산 항목 생성
        total_revenue = 0.0
        total_distance = 0.0
        total_pallets = 0
        
        for dispatch in dispatches:
            # 배차의 청구 금액 조회
            line_item = self.db.query(InvoiceLineItem).filter(
                InvoiceLineItem.dispatch_id == dispatch.id
            ).first()
            
            revenue = line_item.amount if line_item else 0.0
            commission = revenue * (commission_rate / 100)
            
            # 팔레트 수 계산
            pallets = 0
            for route in dispatch.routes:
                if route.order and route.order.pallets:
                    pallets += route.order.pallets
            
            settlement_item = DriverSettlementItem(
                settlement_id=settlement.id,
                dispatch_id=dispatch.id,
                revenue=revenue,
                commission_rate=commission_rate,
                commission_amount=commission,
                distance_km=dispatch.total_distance_km,
                pallets=pallets
            )
            
            self.db.add(settlement_item)
            
            total_revenue += revenue
            total_distance += dispatch.total_distance_km or 0
            total_pallets += pallets
        
        # 정산 총액 계산
        total_commission = total_revenue * (commission_rate / 100)
        net_amount = total_revenue - total_commission
        
        settlement.total_revenue = round(total_revenue, 2)
        settlement.commission_amount = round(total_commission, 2)
        settlement.net_amount = round(net_amount, 2)
        settlement.dispatch_count = len(dispatches)
        settlement.total_distance_km = round(total_distance, 2)
        settlement.total_pallets = total_pallets
        
        self.db.commit()
        self.db.refresh(settlement)
        
        logger.info(f"기사 정산 생성: {settlement_number}, driver_id={driver_id}, net={net_amount:,.0f}원")
        
        return settlement
    
    def _is_dispatch_settled(self, dispatch_id: int) -> bool:
        """배차가 이미 정산되었는지 확인"""
        return self.db.query(DriverSettlementItem).filter(
            DriverSettlementItem.dispatch_id == dispatch_id
        ).first() is not None
    
    def mark_settlement_paid(
        self,
        settlement_id: int,
        paid_date: date,
        notes: Optional[str] = None
    ) -> DriverSettlement:
        """
        정산 지급 완료 처리
        
        Args:
            settlement_id: 정산 ID
            paid_date: 지급일
            notes: 메모
            
        Returns:
            업데이트된 DriverSettlement
        """
        settlement = self.db.query(DriverSettlement).filter(
            DriverSettlement.id == settlement_id
        ).first()
        
        if not settlement:
            raise ValueError(f"정산을 찾을 수 없습니다: settlement_id={settlement_id}")
        
        settlement.is_paid = True
        settlement.paid_date = paid_date
        
        if notes:
            settlement.notes = notes
        
        self.db.commit()
        self.db.refresh(settlement)
        
        logger.info(f"정산 지급 완료: {settlement.settlement_number}")
        
        return settlement
    
    def generate_monthly_settlements(
        self,
        year: int,
        month: int,
        commission_rate: float = 15.0
    ) -> List[DriverSettlement]:
        """
        월간 기사 정산 일괄 생성
        
        Args:
            year: 연도
            month: 월
            commission_rate: 수수료율 (%)
            
        Returns:
            생성된 정산 리스트
        """
        start_date = date(year, month, 1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # 활성 기사 조회
        drivers = self.db.query(Driver).filter(
            Driver.is_active == True
        ).all()
        
        settlements = []
        
        for driver in drivers:
            try:
                settlement = self.generate_driver_settlement(
                    driver_id=driver.id,
                    start_date=start_date,
                    end_date=end_date,
                    commission_rate=commission_rate
                )
                
                if settlement:
                    settlements.append(settlement)
                    logger.info(f"월간 정산 생성: driver={driver.name}, settlement={settlement.settlement_number}")
                
            except Exception as e:
                logger.error(f"정산 생성 실패: driver_id={driver.id}, error={e}")
                continue
        
        logger.info(f"{year}년 {month}월 정산 {len(settlements)}건 생성 완료")
        
        return settlements
