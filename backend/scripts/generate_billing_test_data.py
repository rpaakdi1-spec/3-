#!/usr/bin/env python3
"""
청구/정산 테스트 데이터 생성 스크립트
Usage:
    docker exec -it uvis-backend python /app/scripts/generate_billing_test_data.py
"""
import sys
import os
from datetime import date, datetime, timedelta
import random

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.billing import (
    Invoice, InvoiceLineItem, Payment,
    BillingStatus, PaymentMethod,
    DriverSettlement, DriverSettlementItem
)
from app.models.client import Client
from app.models.driver import Driver
from app.models.dispatch import Dispatch


def generate_invoice_number():
    """청구서 번호 생성"""
    return f"INV-{datetime.now().year}-{random.randint(10000, 99999)}"


def generate_payment_number():
    """결제 번호 생성"""
    return f"PAY-{datetime.now().year}-{random.randint(10000, 99999)}"


def generate_settlement_number():
    """정산 번호 생성"""
    return f"STL-{datetime.now().year}-{random.randint(10000, 99999)}"


def generate_test_data(db):
    """테스트 데이터 생성"""
    
    print("=" * 60)
    print("청구/정산 테스트 데이터 생성 시작")
    print("=" * 60)
    
    # 1. 기존 데이터 확인
    existing_invoices = db.query(Invoice).count()
    existing_settlements = db.query(DriverSettlement).count()
    
    print(f"\n📊 기존 데이터 현황:")
    print(f"   - 청구서: {existing_invoices}개")
    print(f"   - 정산: {existing_settlements}개")
    
    if existing_invoices > 0 or existing_settlements > 0:
        confirm = input("\n⚠️  기존 데이터가 있습니다. 계속하시겠습니까? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ 취소되었습니다.")
            return
    
    # 2. 거래처 및 기사 확인
    clients = db.query(Client).all()
    drivers = db.query(Driver).all()
    dispatches = db.query(Dispatch).all()
    
    print(f"\n📋 마스터 데이터 현황:")
    print(f"   - 거래처: {len(clients)}개")
    print(f"   - 기사: {len(drivers)}개")
    print(f"   - 배차: {len(dispatches)}개")
    
    if not clients:
        print("\n⚠️  거래처 데이터가 없습니다. 테스트 거래처를 생성합니다.")
        # 테스트 거래처 생성
        for i in range(1, 11):
            client = Client(
                client_code=f"CLI{i:04d}",
                name=f"테스트 거래처 {i}",
                business_number=f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(10000,99999)}",
                contact_person=f"담당자 {i}",
                phone=f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                email=f"client{i}@test.com",
                address=f"서울시 강남구 테스트로 {i}",
                is_active=True
            )
            db.add(client)
        db.commit()
        clients = db.query(Client).all()
        print(f"   ✅ {len(clients)}개의 테스트 거래처 생성 완료")
    
    # 3. 청구서 생성
    print("\n📝 청구서 생성 중...")
    invoices_created = 0
    
    # 지난 3개월 동안의 청구서 생성
    today = date.today()
    start_date = today - timedelta(days=90)
    
    for client in clients:
        # 각 거래처별로 5-15개의 청구서 생성
        num_invoices = random.randint(5, 15)
        
        for _ in range(num_invoices):
            # 청구 기간 설정 (30일 단위)
            invoice_date = start_date + timedelta(days=random.randint(0, 90))
            period_start = invoice_date - timedelta(days=30)
            period_end = invoice_date - timedelta(days=1)
            due_date = invoice_date + timedelta(days=30)
            
            # 금액 계산
            subtotal = random.uniform(500_000, 5_000_000)
            tax_amount = subtotal * 0.1
            discount = random.uniform(0, subtotal * 0.1) if random.random() > 0.7 else 0
            total = subtotal + tax_amount - discount
            
            # 상태 결정
            status_choices = [
                BillingStatus.DRAFT,
                BillingStatus.SENT,
                BillingStatus.PAID,
                BillingStatus.PARTIAL,
                BillingStatus.OVERDUE,
            ]
            status = random.choice(status_choices)
            
            # 결제 금액 (상태에 따라)
            if status == BillingStatus.PAID:
                paid_amount = total
                paid_date = invoice_date + timedelta(days=random.randint(1, 30))
            elif status == BillingStatus.PARTIAL:
                paid_amount = total * random.uniform(0.3, 0.8)
                paid_date = invoice_date + timedelta(days=random.randint(1, 30))
            else:
                paid_amount = 0.0
                paid_date = None
            
            # 청구서 생성
            invoice = Invoice(
                invoice_number=generate_invoice_number(),
                client_id=client.id,
                billing_period_start=period_start,
                billing_period_end=period_end,
                subtotal=subtotal,
                tax_amount=tax_amount,
                discount_amount=discount,
                total_amount=total,
                paid_amount=paid_amount,
                status=status,
                issue_date=invoice_date,
                due_date=due_date,
                paid_date=paid_date,
                notes=f"테스트 청구서 - {client.name}",
                sent_at=invoice_date if status != BillingStatus.DRAFT else None
            )
            db.add(invoice)
            db.flush()
            
            # 청구서 항목 생성 (2-5개)
            num_items = random.randint(2, 5)
            for item_idx in range(num_items):
                line_item = InvoiceLineItem(
                    invoice_id=invoice.id,
                    description=f"배송 서비스 #{item_idx + 1}",
                    quantity=random.randint(1, 10),
                    unit_price=random.uniform(50_000, 500_000),
                    amount=random.uniform(50_000, 500_000),
                    distance_km=random.uniform(10, 200),
                    pallets=random.randint(1, 20),
                    weight_kg=random.uniform(100, 2000),
                    surcharge_amount=random.uniform(0, 50_000) if random.random() > 0.8 else 0,
                    discount_amount=random.uniform(0, 20_000) if random.random() > 0.9 else 0
                )
                db.add(line_item)
            
            # 결제 기록 생성 (결제 완료 또는 부분 결제 시)
            if paid_amount > 0:
                payment = Payment(
                    payment_number=generate_payment_number(),
                    invoice_id=invoice.id,
                    amount=paid_amount,
                    payment_method=random.choice(list(PaymentMethod)),
                    payment_date=paid_date,
                    reference_number=f"REF-{random.randint(100000, 999999)}",
                    bank_name=random.choice(["신한은행", "국민은행", "우리은행", "하나은행"]),
                    notes=f"테스트 결제 - {client.name}"
                )
                db.add(payment)
            
            invoices_created += 1
    
    db.commit()
    print(f"   ✅ {invoices_created}개의 청구서 생성 완료")
    
    # 4. 기사 정산 생성
    if drivers:
        print("\n💰 기사 정산 생성 중...")
        settlements_created = 0
        
        for driver in drivers[:min(10, len(drivers))]:  # 최대 10명의 기사만
            # 각 기사별로 3-8개의 정산 생성
            num_settlements = random.randint(3, 8)
            
            for _ in range(num_settlements):
                # 정산 기간 설정 (30일 단위)
                settlement_date = start_date + timedelta(days=random.randint(0, 90))
                period_start = settlement_date - timedelta(days=30)
                period_end = settlement_date - timedelta(days=1)
                
                # 금액 계산
                total_revenue = random.uniform(1_000_000, 5_000_000)
                commission_amount = total_revenue * random.uniform(0.1, 0.3)
                expense_amount = random.uniform(100_000, 500_000)
                net_amount = total_revenue - commission_amount - expense_amount
                
                # 지급 여부
                is_paid = random.choice([True, False])
                paid_date = settlement_date + timedelta(days=random.randint(1, 15)) if is_paid else None
                
                # 정산 생성
                settlement = DriverSettlement(
                    settlement_number=generate_settlement_number(),
                    driver_id=driver.id,
                    settlement_period_start=period_start,
                    settlement_period_end=period_end,
                    total_revenue=total_revenue,
                    commission_amount=commission_amount,
                    expense_amount=expense_amount,
                    net_amount=net_amount,
                    is_paid=is_paid,
                    paid_date=paid_date,
                    dispatch_count=random.randint(20, 100),
                    total_distance_km=random.uniform(500, 3000),
                    total_pallets=random.randint(50, 300),
                    notes=f"테스트 정산 - {driver.name}"
                )
                db.add(settlement)
                db.flush()
                
                # 정산 항목 생성 (5-15개의 배차)
                num_items = random.randint(5, 15)
                for _ in range(num_items):
                    item = DriverSettlementItem(
                        settlement_id=settlement.id,
                        dispatch_id=random.choice(dispatches).id if dispatches else None,
                        revenue=random.uniform(50_000, 300_000),
                        commission_rate=random.uniform(10, 30),
                        commission_amount=random.uniform(5_000, 50_000),
                        distance_km=random.uniform(10, 200),
                        pallets=random.randint(1, 20)
                    )
                    db.add(item)
                
                settlements_created += 1
        
        db.commit()
        print(f"   ✅ {settlements_created}개의 정산 생성 완료")
    else:
        print("\n⚠️  기사 데이터가 없어 정산을 생성하지 않았습니다.")
    
    # 5. 생성된 데이터 요약
    print("\n" + "=" * 60)
    print("✅ 테스트 데이터 생성 완료!")
    print("=" * 60)
    
    final_invoices = db.query(Invoice).count()
    final_payments = db.query(Payment).count()
    final_settlements = db.query(DriverSettlement).count()
    
    # 상태별 청구서 통계
    draft_count = db.query(Invoice).filter(Invoice.status == BillingStatus.DRAFT).count()
    sent_count = db.query(Invoice).filter(Invoice.status == BillingStatus.SENT).count()
    paid_count = db.query(Invoice).filter(Invoice.status == BillingStatus.PAID).count()
    partial_count = db.query(Invoice).filter(Invoice.status == BillingStatus.PARTIAL).count()
    overdue_count = db.query(Invoice).filter(Invoice.status == BillingStatus.OVERDUE).count()
    
    # 금액 통계
    from sqlalchemy import func
    total_invoiced = db.query(func.sum(Invoice.total_amount)).scalar() or 0
    total_paid = db.query(func.sum(Invoice.paid_amount)).scalar() or 0
    total_settlements = db.query(func.sum(DriverSettlement.net_amount)).scalar() or 0
    
    print(f"\n📊 생성된 데이터:")
    print(f"   - 총 청구서: {final_invoices}개")
    print(f"     ├─ 초안: {draft_count}개")
    print(f"     ├─ 발송됨: {sent_count}개")
    print(f"     ├─ 결제 완료: {paid_count}개")
    print(f"     ├─ 부분 결제: {partial_count}개")
    print(f"     └─ 연체: {overdue_count}개")
    print(f"   - 총 결제 기록: {final_payments}개")
    print(f"   - 총 정산: {final_settlements}개")
    
    print(f"\n💰 금액 통계:")
    print(f"   - 총 청구 금액: ₩{total_invoiced:,.0f}")
    print(f"   - 총 수금 금액: ₩{total_paid:,.0f}")
    print(f"   - 수금률: {(total_paid/total_invoiced*100):.1f}%" if total_invoiced > 0 else "   - 수금률: 0.0%")
    print(f"   - 총 정산 금액: ₩{total_settlements:,.0f}")
    
    print("\n🎯 다음 단계:")
    print("   1. 브라우저에서 http://139.150.11.99 접속")
    print("   2. admin/admin123 로그인")
    print("   3. 청구/정산 > 재무 대시보드 확인")
    print("   4. 네트워크 탭에서 API 응답 확인")
    print("=" * 60)


def main():
    """메인 함수"""
    try:
        db = SessionLocal()
        generate_test_data(db)
        db.close()
    except Exception as e:
        print(f"\n❌ 에러 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
