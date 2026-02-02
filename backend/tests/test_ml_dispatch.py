"""
ML Dispatch Service 테스트 스크립트

Usage:
    cd /home/user/webapp
    python backend/tests/test_ml_dispatch.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, time
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.vehicle import Vehicle, VehicleType, VehicleStatus
from app.models.order import Order, TemperatureZone, OrderStatus
from app.models.client import Client, ClientType
from app.services.ml_dispatch_service import MLDispatchService


def create_test_data(db: Session):
    """테스트용 데이터 생성"""
    
    # 테스트 거래처 생성
    pickup_client = Client(
        code="TEST_PICKUP_001",
        name="테스트 상차지",
        client_type=ClientType.PICKUP,
        address="서울 강남구",
        latitude=37.5172,
        longitude=127.0473
    )
    
    delivery_client = Client(
        code="TEST_DELIVERY_001",
        name="테스트 하차지",
        client_type=ClientType.DELIVERY,
        address="서울 강북구",
        latitude=37.6397,
        longitude=127.0255,
        unload_start_time="08:00",
        unload_end_time="18:00",
        pallet_type="11형"
    )
    
    db.add_all([pickup_client, delivery_client])
    db.commit()
    
    # 테스트 차량 생성
    vehicles = []
    
    # 차량 1: 냉동 차량, 회전수 적음
    v1 = Vehicle(
        code="TEST_V001",
        plate_number="12가3456",
        vehicle_type=VehicleType.FROZEN,
        status=VehicleStatus.AVAILABLE,
        max_pallets=20,
        length_m=9.5,
        garage_latitude=37.5665,
        garage_longitude=126.9780,
        supports_frozen=True,
        supports_chilled=False,
        supports_ambient=False,
        max_pallets_11type=20,
        max_pallets_12type=17,
        rotation_count_this_month=3
    )
    
    # 차량 2: 겸용 차량, 회전수 많음
    v2 = Vehicle(
        code="TEST_V002",
        plate_number="34나5678",
        vehicle_type=VehicleType.DUAL,
        status=VehicleStatus.AVAILABLE,
        max_pallets=24,
        length_m=11.0,
        garage_latitude=37.4979,
        garage_longitude=127.0276,
        supports_frozen=True,
        supports_chilled=True,
        supports_ambient=True,
        max_pallets_11type=24,
        max_pallets_12type=20,
        rotation_count_this_month=8
    )
    
    # 차량 3: 냉동 차량, 멀리 위치
    v3 = Vehicle(
        code="TEST_V003",
        plate_number="56다7890",
        vehicle_type=VehicleType.FROZEN,
        status=VehicleStatus.AVAILABLE,
        max_pallets=20,
        length_m=9.5,
        garage_latitude=37.3595,
        garage_longitude=127.1058,  # 성남 (멀리)
        supports_frozen=True,
        supports_chilled=False,
        supports_ambient=False,
        max_pallets_11type=20,
        max_pallets_12type=17,
        rotation_count_this_month=5
    )
    
    vehicles = [v1, v2, v3]
    db.add_all(vehicles)
    db.commit()
    
    # 테스트 주문 생성
    order = Order(
        order_number="TEST_ORDER_001",
        order_date=datetime.now().date(),
        temperature_zone=TemperatureZone.FROZEN,
        pickup_client_id=pickup_client.id,
        delivery_client_id=delivery_client.id,
        pickup_latitude=pickup_client.latitude,
        pickup_longitude=pickup_client.longitude,
        delivery_latitude=delivery_client.latitude,
        delivery_longitude=delivery_client.longitude,
        pallet_count=15,
        pallet_type="11형",
        status=OrderStatus.PENDING,
        priority=5
    )
    
    db.add(order)
    db.commit()
    
    return order, vehicles


async def test_ml_dispatch():
    """ML Dispatch 테스트"""
    
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("ML Dispatch Service 테스트")
        print("=" * 60)
        
        # 테스트 데이터 생성
        print("\n1️⃣  테스트 데이터 생성 중...")
        order, vehicles = create_test_data(db)
        print(f"   ✅ 주문: {order.order_number}")
        print(f"   ✅ 차량: {len(vehicles)}대")
        
        # ML Dispatch 서비스 초기화
        print("\n2️⃣  ML Dispatch 서비스 초기화...")
        ml_service = MLDispatchService(db)
        print("   ✅ 서비스 초기화 완료")
        
        # 배차 최적화 실행
        print("\n3️⃣  배차 최적화 실행 중...")
        rankings = await ml_service.optimize_single_order(order, vehicles)
        
        if not rankings:
            print("   ❌ 배차 가능한 차량 없음!")
            return
        
        print(f"   ✅ {len(rankings)}대 차량 순위 결정 완료")
        
        # 결과 출력
        print("\n4️⃣  배차 순위 결과:")
        print("-" * 60)
        
        for i, rank in enumerate(rankings, 1):
            vehicle = rank.vehicle
            scores = rank.agent_scores
            
            print(f"\n순위 {i}: {vehicle.code} ({vehicle.plate_number})")
            print(f"  🎯 최종 점수: {rank.total_score:.3f}")
            print(f"  📊 세부 점수:")
            print(f"     - 거리: {scores.distance:.3f} (낮을수록 좋음)")
            print(f"     - 회전수: {scores.rotation:.3f} (낮을수록 좋음)")
            print(f"     - 시간여유: {scores.time_window:.3f} (높을수록 좋음)")
            print(f"     - 선호도: {scores.preference:.3f} (높을수록 좋음)")
            print(f"     - 전압안전: {scores.voltage:.3f} (1.0=안전)")
            print(f"  💡 선택 이유: {rank.reason}")
        
        # 최종 추천
        best = rankings[0]
        print("\n" + "=" * 60)
        print(f"✨ 추천 차량: {best.vehicle.code} ({best.reason})")
        print("=" * 60)
        
    finally:
        # 테스트 데이터 삭제
        print("\n5️⃣  테스트 데이터 정리 중...")
        db.query(Order).filter(Order.order_number.like("TEST_%")).delete()
        db.query(Vehicle).filter(Vehicle.code.like("TEST_%")).delete()
        db.query(Client).filter(Client.code.like("TEST_%")).delete()
        db.commit()
        print("   ✅ 정리 완료")
        
        db.close()


if __name__ == "__main__":
    import asyncio
    
    print("\n🚀 ML Dispatch Service 테스트 시작\n")
    
    asyncio.run(test_ml_dispatch())
    
    print("\n✅ 테스트 완료!\n")
