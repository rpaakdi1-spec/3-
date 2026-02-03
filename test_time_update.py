"""
주문 시간 필드 업데이트 테스트 스크립트
"""
import sys
sys.path.insert(0, '/home/user/webapp/backend')

from app.schemas.order import OrderUpdate
from datetime import time

print("=" * 80)
print("시간 필드 업데이트 테스트")
print("=" * 80)

# 테스트 1: 문자열 시간
print("\n📋 테스트 1: 문자열 시간 파싱")
print("-" * 80)
try:
    data = {
        "pickup_start_time": "09:00",
        "pickup_end_time": "18:00",
        "delivery_start_time": "10:00",
        "delivery_end_time": "17:00"
    }
    order_update = OrderUpdate(**data)
    print(f"✅ 성공!")
    print(f"  pickup_start_time: {order_update.pickup_start_time} (type: {type(order_update.pickup_start_time)})")
    print(f"  pickup_end_time: {order_update.pickup_end_time} (type: {type(order_update.pickup_end_time)})")
    print(f"  delivery_start_time: {order_update.delivery_start_time} (type: {type(order_update.delivery_start_time)})")
    print(f"  delivery_end_time: {order_update.delivery_end_time} (type: {type(order_update.delivery_end_time)})")
except Exception as e:
    print(f"❌ 실패: {e}")
    import traceback
    traceback.print_exc()

# 테스트 2: time 객체
print("\n📋 테스트 2: time 객체 직접 전달")
print("-" * 80)
try:
    data = {
        "pickup_start_time": time(9, 0),
        "pickup_end_time": time(18, 0)
    }
    order_update = OrderUpdate(**data)
    print(f"✅ 성공!")
    print(f"  pickup_start_time: {order_update.pickup_start_time}")
    print(f"  pickup_end_time: {order_update.pickup_end_time}")
except Exception as e:
    print(f"❌ 실패: {e}")

# 테스트 3: model_dump 확인
print("\n📋 테스트 3: model_dump(exclude_unset=True) 결과")
print("-" * 80)
try:
    data = {
        "pallet_count": 10,
        "pickup_start_time": "09:00",
        "pickup_end_time": "18:00"
    }
    order_update = OrderUpdate(**data)
    dumped = order_update.model_dump(exclude_unset=True)
    print(f"✅ Dumped data:")
    for key, value in dumped.items():
        print(f"  {key}: {value} (type: {type(value).__name__})")
except Exception as e:
    print(f"❌ 실패: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("테스트 완료")
print("=" * 80)
