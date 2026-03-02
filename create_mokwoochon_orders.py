#!/usr/bin/env python3
"""
목우촌 2/23(월) 오후배차 주문 생성 스크립트
"""
import sys
import os
from datetime import date, time

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.order import Order, TemperatureZone, OrderStatus

def create_mokwoochon_orders():
    """목우촌 배차 5건 생성"""
    db = SessionLocal()
    
    try:
        # 공통 정보
        order_date = date(2026, 2, 23)  # 2026-02-23 (월요일)
        pickup_address = "전북 김제시 금산면 용산리 9-13"
        pickup_detail = "목우촌"
        delivery_address = "경기도 안성시 양성면 양성로 376-106"
        delivery_detail = "도곡리 40-4"
        
        orders_data = [
            {
                "order_number": "MOK-20260223-001",
                "product_name": "식육(냉동)",
                "pickup_start_time": time(13, 0),
                "pickup_end_time": time(14, 0),
                "temperature_zone": TemperatureZone.FROZEN,
                "pallet_count": 16,
                "weight_kg": 11000.0,
                "notes": "11톤 냉동차량 필요"
            },
            {
                "order_number": "MOK-20260223-002",
                "product_name": "식육(냉장)",
                "pickup_start_time": time(13, 30),
                "pickup_end_time": time(14, 30),
                "temperature_zone": TemperatureZone.REFRIGERATED,
                "pallet_count": 10,
                "weight_kg": 5000.0,
                "notes": "5톤 냉장차량 필요"
            },
            {
                "order_number": "MOK-20260223-003",
                "product_name": "육가공(냉장)",
                "pickup_start_time": time(14, 30),
                "pickup_end_time": time(15, 30),
                "temperature_zone": TemperatureZone.REFRIGERATED,
                "pallet_count": 16,
                "weight_kg": 11000.0,
                "notes": "11톤 냉장차량 필요"
            },
            {
                "order_number": "MOK-20260223-004",
                "product_name": "식육(냉장)",
                "pickup_start_time": time(15, 0),
                "pickup_end_time": time(16, 0),
                "temperature_zone": TemperatureZone.REFRIGERATED,
                "pallet_count": 10,
                "weight_kg": 5000.0,
                "notes": "5톤 냉장차량 필요"
            },
            {
                "order_number": "MOK-20260223-005",
                "product_name": "육가공(냉장)",
                "pickup_start_time": time(16, 30),
                "pickup_end_time": time(17, 30),
                "temperature_zone": TemperatureZone.REFRIGERATED,
                "pallet_count": 16,
                "weight_kg": 11000.0,
                "notes": "11톤 냉장차량 필요"
            }
        ]
        
        created_orders = []
        
        for order_data in orders_data:
            # Check if order already exists
            existing = db.query(Order).filter(
                Order.order_number == order_data["order_number"]
            ).first()
            
            if existing:
                print(f"⚠️  주문 {order_data['order_number']} 이미 존재함 - 건너뜀")
                continue
            
            order = Order(
                order_number=order_data["order_number"],
                order_date=order_date,
                temperature_zone=order_data["temperature_zone"],
                pickup_address=pickup_address,
                pickup_address_detail=pickup_detail,
                delivery_address=delivery_address,
                delivery_address_detail=delivery_detail,
                pallet_count=order_data["pallet_count"],
                weight_kg=order_data["weight_kg"],
                product_name=order_data["product_name"],
                pickup_start_time=order_data["pickup_start_time"],
                pickup_end_time=order_data["pickup_end_time"],
                delivery_start_time=time(16, 0),  # 예상 하차 시작
                delivery_end_time=time(18, 0),    # 예상 하차 종료
                requested_delivery_date=order_date,
                priority=5,
                status=OrderStatus.PENDING,
                requires_forklift=True,
                is_stackable=True,
                notes=order_data["notes"]
            )
            
            db.add(order)
            created_orders.append(order)
            print(f"✅ 주문 생성: {order_data['order_number']} - {order_data['product_name']} ({order_data['pallet_count']}p)")
        
        db.commit()
        
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🎉 목우촌 배차 주문 생성 완료!")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📅 날짜: 2026-02-23 (월)")
        print(f"📦 생성된 주문: {len(created_orders)}건")
        print(f"🏢 상차지: {pickup_address}")
        print(f"🏢 하차지: {delivery_address}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # 주문 요약
        print("\n📋 주문 요약:")
        for i, order in enumerate(created_orders, 1):
            print(f"{i}. {order.order_number}")
            print(f"   - 품목: {order.product_name}")
            print(f"   - 시간: {order.pickup_start_time.strftime('%H:%M')}")
            print(f"   - 팔레트: {order.pallet_count}p")
            print(f"   - 온도: {order.temperature_zone.value}")
            print(f"   - 무게: {order.weight_kg:,.0f}kg")
            print()
        
        return created_orders
        
    except Exception as e:
        db.rollback()
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        db.close()


if __name__ == "__main__":
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📦 목우촌 2/23(월) 오후배차 주문 생성")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    orders = create_mokwoochon_orders()
    
    if orders:
        print("\n✅ 모든 주문이 성공적으로 생성되었습니다!")
        print("\n다음 단계:")
        print("1. 브라우저에서 http://139.150.11.99/orders 접속")
        print("2. 생성된 주문 확인")
        print("3. AI 배차 최적화 또는 수동 배차 진행")
    else:
        print("\n⚠️  주문 생성 실패 또는 이미 존재함")
