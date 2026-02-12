#!/usr/bin/env python3
"""
Generate test billing data for Cold Chain system
청구/정산 테스트 데이터 생성
"""

from datetime import date, timedelta
import random

# 데이터 생성 스크립트
script = """
from app.core.database import SessionLocal
from app.models.invoice import Invoice, InvoiceStatus
from app.models.settlement import Settlement, SettlementStatus
from app.models.client import Client
from datetime import date, timedelta
import random

db = SessionLocal()

try:
    # 1. 기존 데이터 확인
    invoice_count = db.query(Invoice).count()
    settlement_count = db.query(Settlement).count()
    client_count = db.query(Client).count()
    
    print(f"📊 Current data:")
    print(f"  Clients: {client_count}")
    print(f"  Invoices: {invoice_count}")
    print(f"  Settlements: {settlement_count}")
    
    # 2. Client 확인 (없으면 생성)
    if client_count == 0:
        print("\\n🏢 Creating test clients...")
        test_clients = [
            Client(name="삼성전자", business_number="123-45-67890", phone="02-1234-5678", address="서울 강남구"),
            Client(name="LG전자", business_number="234-56-78901", phone="02-2345-6789", address="서울 서초구"),
            Client(name="현대백화점", business_number="345-67-89012", phone="02-3456-7890", address="서울 종로구"),
            Client(name="롯데마트", business_number="456-78-90123", phone="02-4567-8901", address="서울 송파구"),
            Client(name="이마트", business_number="567-89-01234", phone="02-5678-9012", address="서울 강서구"),
            Client(name="CJ제일제당", business_number="678-90-12345", phone="02-6789-0123", address="서울 중구"),
            Client(name="농심", business_number="789-01-23456", phone="02-7890-1234", address="서울 동대문구"),
            Client(name="풀무원", business_number="890-12-34567", phone="02-8901-2345", address="서울 마포구"),
            Client(name="오리온", business_number="901-23-45678", phone="02-9012-3456", address="서울 용산구"),
            Client(name="빙그레", business_number="012-34-56789", phone="02-0123-4567", address="서울 영등포구"),
        ]
        for client in test_clients:
            db.add(client)
        db.commit()
        print(f"✅ Created {len(test_clients)} test clients")
    
    # Client ID 목록 가져오기
    client_ids = [c.id for c in db.query(Client).all()]
    
    if not client_ids:
        print("❌ No clients found!")
        exit(1)
    
    # 3. Invoice 생성 (최근 3개월, 50건)
    print(f"\\n📝 Creating test invoices...")
    today = date.today()
    
    for i in range(50):
        days_ago = random.randint(1, 90)  # 최근 3개월
        invoice_date = today - timedelta(days=days_ago)
        due_date = invoice_date + timedelta(days=30)
        
        # 금액 (100만원 ~ 1000만원)
        total_amount = random.randint(1000000, 10000000)
        
        # 상태 (70% 발행, 20% 지급완료, 10% 초안)
        status_choice = random.random()
        if status_choice < 0.7:
            status = InvoiceStatus.ISSUED
        elif status_choice < 0.9:
            status = InvoiceStatus.PAID
        else:
            status = InvoiceStatus.DRAFT
        
        invoice = Invoice(
            client_id=random.choice(client_ids),
            invoice_number=f"INV-{today.year}-{1000+i:04d}",
            invoice_date=invoice_date,
            due_date=due_date,
            total_amount=total_amount,
            paid_amount=total_amount if status == InvoiceStatus.PAID else 0,
            status=status,
            notes=f"배송료 청구 (테스트 데이터 {i+1})"
        )
        db.add(invoice)
    
    db.commit()
    print(f"✅ Created 50 test invoices")
    
    # 4. Settlement 생성 (최근 3개월, 30건)
    print(f"\\n💰 Creating test settlements...")
    
    for i in range(30):
        days_ago = random.randint(1, 90)
        settlement_date = today - timedelta(days=days_ago)
        
        # 금액 (500만원 ~ 2000만원)
        total_amount = random.randint(5000000, 20000000)
        
        # 상태 (40% 대기, 40% 승인, 20% 지급완료)
        status_choice = random.random()
        if status_choice < 0.4:
            status = SettlementStatus.PENDING
        elif status_choice < 0.8:
            status = SettlementStatus.APPROVED
        else:
            status = SettlementStatus.PAID
        
        settlement = Settlement(
            client_id=random.choice(client_ids),
            settlement_date=settlement_date,
            total_amount=total_amount,
            status=status,
            notes=f"월간 정산 (테스트 데이터 {i+1})"
        )
        db.add(settlement)
    
    db.commit()
    print(f"✅ Created 30 test settlements")
    
    # 5. 최종 확인
    print(f"\\n📊 Final data count:")
    print(f"  Clients: {db.query(Client).count()}")
    print(f"  Invoices: {db.query(Invoice).count()}")
    print(f"  Settlements: {db.query(Settlement).count()}")
    
    # 6. 통계 출력
    total_invoices = db.query(Invoice).count()
    paid_invoices = db.query(Invoice).filter(Invoice.status == InvoiceStatus.PAID).count()
    total_revenue = db.query(Invoice).with_entities(db.func.sum(Invoice.total_amount)).scalar() or 0
    total_settlements = db.query(Settlement).with_entities(db.func.sum(Settlement.total_amount)).scalar() or 0
    
    print(f"\\n💵 Financial summary:")
    print(f"  Total invoices: {total_invoices}")
    print(f"  Paid invoices: {paid_invoices}")
    print(f"  Total revenue: ₩{total_revenue:,}")
    print(f"  Total settlements: ₩{total_settlements:,}")
    
    print(f"\\n✅ Test data generation complete!")
    
except Exception as e:
    print(f"\\n❌ Error: {e}")
    db.rollback()
finally:
    db.close()
"""

print(script)
