#!/usr/bin/env python3
"""
500 오류 긴급 핫픽스 스크립트
데이터베이스의 문제있는 시간 필드를 정리합니다.
"""

import sys
from pathlib import Path

# 백엔드 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from app.core.database import SessionLocal
from app.models.order import Order
from datetime import time as time_type

def fix_time_fields():
    """시간 필드의 잘못된 데이터를 수정"""
    db = SessionLocal()
    try:
        orders = db.query(Order).all()
        fixed_count = 0
        
        for order in orders:
            changed = False
            
            # pickup_start_time 처리
            if order.pickup_start_time is not None:
                if isinstance(order.pickup_start_time, str):
                    try:
                        # 문자열을 time 객체로 변환
                        hour, minute = map(int, order.pickup_start_time.split(':'))
                        order.pickup_start_time = time_type(hour, minute)
                        changed = True
                    except:
                        # 변환 실패 시 None으로 설정
                        order.pickup_start_time = None
                        changed = True
            
            # pickup_end_time 처리
            if order.pickup_end_time is not None:
                if isinstance(order.pickup_end_time, str):
                    try:
                        hour, minute = map(int, order.pickup_end_time.split(':'))
                        order.pickup_end_time = time_type(hour, minute)
                        changed = True
                    except:
                        order.pickup_end_time = None
                        changed = True
            
            # delivery_start_time 처리
            if order.delivery_start_time is not None:
                if isinstance(order.delivery_start_time, str):
                    try:
                        hour, minute = map(int, order.delivery_start_time.split(':'))
                        order.delivery_start_time = time_type(hour, minute)
                        changed = True
                    except:
                        order.delivery_start_time = None
                        changed = True
            
            # delivery_end_time 처리
            if order.delivery_end_time is not None:
                if isinstance(order.delivery_end_time, str):
                    try:
                        hour, minute = map(int, order.delivery_end_time.split(':'))
                        order.delivery_end_time = time_type(hour, minute)
                        changed = True
                    except:
                        order.delivery_end_time = None
                        changed = True
            
            if changed:
                fixed_count += 1
                print(f"✓ Fixed order {order.id} ({order.order_number})")
        
        if fixed_count > 0:
            db.commit()
            print(f"\n✅ Successfully fixed {fixed_count} orders")
        else:
            print("✓ No orders needed fixing")
        
        return fixed_count
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 0
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Order Time Fields Hotfix")
    print("=" * 50)
    print()
    
    count = fix_time_fields()
    
    print()
    print("=" * 50)
    print(f"Fixed {count} order(s)")
    print("=" * 50)
