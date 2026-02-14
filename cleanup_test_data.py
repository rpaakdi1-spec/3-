"""
테스트 데이터 정리 스크립트
TEST-ORD로 시작하는 주문과 관련 배차를 삭제
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.order import Order
from app.models.dispatch import Dispatch, DispatchRoute


def cleanup_test_data():
    """테스트 데이터 정리"""
    db = SessionLocal()
    
    try:
        print("\n🧹 테스트 데이터 정리 시작...\n")
        
        # 1. TEST-ORD로 시작하는 주문 조회
        test_orders = db.query(Order).filter(
            Order.order_number.like('TEST-ORD-%')
        ).all()
        
        print(f"📦 삭제할 테스트 주문: {len(test_orders)}건")
        for order in test_orders:
            print(f"    - {order.order_number}: {order.status.value}")
        
        # 2. TEST로 시작하는 배차 조회
        test_dispatches = db.query(Dispatch).filter(
            Dispatch.dispatch_number.like('TEST-%')
        ).all()
        
        print(f"\n🚚 삭제할 테스트 배차: {len(test_dispatches)}건")
        for dispatch in test_dispatches:
            print(f"    - {dispatch.dispatch_number}: {dispatch.status.value}")
        
        # 3. 배차 경로 삭제
        route_count = 0
        for dispatch in test_dispatches:
            routes = db.query(DispatchRoute).filter(
                DispatchRoute.dispatch_id == dispatch.id
            ).all()
            route_count += len(routes)
            for route in routes:
                db.delete(route)
        
        print(f"\n📍 삭제할 배차 경로: {route_count}건")
        
        # 4. 배차 삭제
        for dispatch in test_dispatches:
            db.delete(dispatch)
        
        # 5. 주문 삭제
        for order in test_orders:
            db.delete(order)
        
        # 6. 커밋
        db.commit()
        
        print(f"\n✅ 정리 완료!")
        print(f"    - 주문 {len(test_orders)}건 삭제")
        print(f"    - 배차 {len(test_dispatches)}건 삭제")
        print(f"    - 경로 {route_count}건 삭제")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    cleanup_test_data()
