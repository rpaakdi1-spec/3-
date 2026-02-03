#!/usr/bin/env python3
"""
주문 상태를 영어에서 한글로 변환하는 스크립트
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import SessionLocal
from sqlalchemy import text

def fix_order_statuses():
    """주문 상태를 영어에서 한글로 변환"""
    db = SessionLocal()
    
    try:
        # Status mapping
        status_mapping = {
            'PENDING': '배차대기',
            'ASSIGNED': '배차완료',
            'IN_TRANSIT': '운송중',
            'DELIVERED': '배송완료',
            'CANCELLED': '취소'
        }
        
        print("🔄 주문 상태 업데이트 시작...")
        
        for english, korean in status_mapping.items():
            result = db.execute(
                text(f"UPDATE orders SET status = :korean WHERE status = :english"),
                {"korean": korean, "english": english}
            )
            count = result.rowcount
            if count > 0:
                print(f"✅ {english} → {korean}: {count}건 업데이트")
        
        db.commit()
        print("\n✅ 주문 상태 업데이트 완료!")
        
        # 현재 상태 확인
        result = db.execute(text("SELECT status, COUNT(*) as count FROM orders GROUP BY status"))
        print("\n📊 현재 주문 상태 분포:")
        for row in result:
            print(f"  - {row.status}: {row.count}건")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_order_statuses()
