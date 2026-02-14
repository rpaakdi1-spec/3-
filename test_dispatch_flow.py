"""
전체 배차 프로세스 End-to-End 테스트 스크립트

테스트 흐름:
1. 주문 등록 (PENDING)
2. 차량 매칭 - AI 배차 최적화 (DRAFT)
3. 배차 확정 (CONFIRMED)
4. 배차 진행 (IN_PROGRESS)
5. 배차 완료 (COMPLETED)

Requirements:
- uvis-backend 컨테이너가 실행 중이어야 함
- 데이터베이스에 활성 차량(vehicles)과 거래처(clients)가 존재해야 함
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import date, time, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.order import Order, OrderStatus, TemperatureZone
from app.models.dispatch import Dispatch, DispatchStatus, DispatchRoute, RouteType
from app.models.vehicle import Vehicle, VehicleStatus
from app.models.client import Client
from app.services.dispatch_optimization_service import DispatchOptimizationService
import random


def print_step(step_num, title):
    """단계 출력"""
    print(f"\n{'='*80}")
    print(f"STEP {step_num}: {title}")
    print(f"{'='*80}\n")


def print_info(label, value):
    """정보 출력"""
    print(f"  ✅ {label}: {value}")


def print_error(message):
    """에러 출력"""
    print(f"  ❌ ERROR: {message}")


def create_test_orders(db: Session, count: int = 5):
    """테스트 주문 생성"""
    print_step(1, "주문 등록 (PENDING)")
    
    # 활성 거래처 조회
    clients = db.query(Client).filter(Client.is_active == True).limit(10).all()
    
    if len(clients) < 2:
        print_error("거래처가 부족합니다. 최소 2개의 활성 거래처가 필요합니다.")
        return []
    
    print_info("활성 거래처 수", len(clients))
    
    created_orders = []
    today = date.today()
    
    # 온도대별로 주문 생성
    temperature_zones = [TemperatureZone.FROZEN, TemperatureZone.REFRIGERATED, TemperatureZone.AMBIENT]
    
    for i in range(count):
        # 랜덤 상차/하차 거래처 선택
        pickup_client = random.choice(clients)
        delivery_client = random.choice([c for c in clients if c.id != pickup_client.id])
        
        # 주문 번호 생성
        order_number = f"TEST-ORD-{today.strftime('%Y%m%d')}-{i+1:03d}"
        
        # 온도대 선택 (순환)
        temp_zone = temperature_zones[i % len(temperature_zones)]
        
        # 주문 생성
        order = Order(
            order_number=order_number,
            order_date=today,
            temperature_zone=temp_zone,
            pickup_client_id=pickup_client.id,
            delivery_client_id=delivery_client.id,
            pickup_address=pickup_client.address,
            pickup_latitude=pickup_client.latitude,
            pickup_longitude=pickup_client.longitude,
            delivery_address=delivery_client.address,
            delivery_latitude=delivery_client.latitude,
            delivery_longitude=delivery_client.longitude,
            pallet_count=random.randint(5, 15),
            weight_kg=random.uniform(300, 800),
            volume_cbm=random.uniform(5, 15),
            product_name=f"테스트상품-{i+1}",
            pickup_start_time=time(9, 0),
            pickup_end_time=time(12, 0),
            delivery_start_time=time(13, 0),
            delivery_end_time=time(17, 0),
            priority=random.randint(1, 10),
            status=OrderStatus.PENDING,
            notes=f"E2E 테스트 주문 #{i+1}"
        )
        
        db.add(order)
        created_orders.append(order)
    
    db.commit()
    
    # 결과 출력
    print_info("생성된 주문 수", len(created_orders))
    for order in created_orders:
        db.refresh(order)
        print(f"    - {order.order_number}: {order.temperature_zone.value}, "
              f"{order.pallet_count}팔레트, {order.status.value}")
    
    return created_orders


async def optimize_and_create_dispatch(db: Session, orders: list):
    """AI 배차 최적화 및 배차 생성"""
    print_step(2, "차량 매칭 - AI 배차 최적화 (DRAFT)")
    
    if not orders:
        print_error("주문이 없습니다.")
        return []
    
    # 활성 차량 조회
    vehicles = db.query(Vehicle).filter(
        Vehicle.is_active == True,
        Vehicle.status == VehicleStatus.AVAILABLE
    ).all()
    
    if not vehicles:
        print_error("사용 가능한 차량이 없습니다.")
        return []
    
    print_info("사용 가능한 차량 수", len(vehicles))
    
    # AI 최적화 서비스 초기화
    optimizer = DispatchOptimizationService(db)
    
    # 최적화 실행
    order_ids = [order.id for order in orders]
    vehicle_ids = [v.id for v in vehicles[:10]]  # 상위 10대만 사용
    dispatch_date = date.today()
    
    print(f"  🤖 AI 최적화 실행 중... (주문 {len(order_ids)}건, 차량 {len(vehicle_ids)}대)")
    
    try:
        result = await optimizer.optimize_dispatch(
            order_ids=order_ids,
            vehicle_ids=vehicle_ids,
            dispatch_date=dispatch_date
        )
        
        print_info("최적화 성공", f"{result['total_dispatches']}건의 배차 생성")
        print_info("총 배정 주문", f"{result['total_orders']}건")
        print_info("미배정 주문", f"{result['unassigned_orders']}건")
        print_info("총 예상 거리", f"{result['total_distance_km']:.2f} km")
        print_info("최적화 점수", f"{result.get('optimization_score', 0):.3f}")
        
        # 생성된 배차 조회
        created_dispatches = []
        for dispatch_data in result['dispatches']:
            dispatch = db.query(Dispatch).filter(
                Dispatch.dispatch_number == dispatch_data['dispatch_number']
            ).first()
            if dispatch:
                created_dispatches.append(dispatch)
                print(f"    - {dispatch.dispatch_number}: "
                      f"차량 {dispatch.vehicle.code}, "
                      f"{dispatch.total_orders}건, "
                      f"{dispatch.total_distance_km:.1f}km, "
                      f"상태: {dispatch.status.value}")
        
        return created_dispatches
        
    except Exception as e:
        print_error(f"AI 최적화 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def confirm_dispatches(db: Session, dispatches: list):
    """배차 확정"""
    print_step(3, "배차 확정 (CONFIRMED)")
    
    if not dispatches:
        print_error("확정할 배차가 없습니다.")
        return []
    
    confirmed = []
    
    for dispatch in dispatches:
        if dispatch.status != DispatchStatus.DRAFT:
            print(f"  ⚠️  {dispatch.dispatch_number}: 이미 확정됨 (현재 상태: {dispatch.status.value})")
            continue
        
        # 배차 상태 변경
        dispatch.status = DispatchStatus.CONFIRMED
        
        # 차량 상태 변경
        if dispatch.vehicle:
            dispatch.vehicle.status = VehicleStatus.IN_USE
        
        # 주문 상태 변경
        updated_orders = 0
        for route in dispatch.routes:
            if route.order:
                route.order.status = OrderStatus.ASSIGNED
                updated_orders += 1
        
        confirmed.append(dispatch)
        print_info(f"배차 확정", 
                  f"{dispatch.dispatch_number} → 차량 {dispatch.vehicle.code} 운행중, "
                  f"주문 {updated_orders}건 배차완료")
    
    db.commit()
    
    print_info("총 확정 배차", f"{len(confirmed)}건")
    return confirmed


def start_dispatches(db: Session, dispatches: list):
    """배차 진행"""
    print_step(4, "배차 진행 (IN_PROGRESS)")
    
    if not dispatches:
        print_error("진행할 배차가 없습니다.")
        return []
    
    in_progress = []
    
    for dispatch in dispatches:
        if dispatch.status != DispatchStatus.CONFIRMED:
            print(f"  ⚠️  {dispatch.dispatch_number}: 확정 상태가 아님 (현재 상태: {dispatch.status.value})")
            continue
        
        # 배차 상태 변경
        dispatch.status = DispatchStatus.IN_PROGRESS
        
        # 주문 상태 변경 (배송중)
        updated_orders = 0
        for route in dispatch.routes:
            if route.order:
                route.order.status = OrderStatus.IN_TRANSIT
                updated_orders += 1
        
        in_progress.append(dispatch)
        print_info(f"배차 시작", 
                  f"{dispatch.dispatch_number} → 주문 {updated_orders}건 배송중")
    
    db.commit()
    
    print_info("총 진행 배차", f"{len(in_progress)}건")
    return in_progress


def complete_dispatches(db: Session, dispatches: list):
    """배차 완료"""
    print_step(5, "배차 완료 (COMPLETED)")
    
    if not dispatches:
        print_error("완료할 배차가 없습니다.")
        return []
    
    completed = []
    
    for dispatch in dispatches:
        if dispatch.status not in [DispatchStatus.CONFIRMED, DispatchStatus.IN_PROGRESS]:
            print(f"  ⚠️  {dispatch.dispatch_number}: 진행중 상태가 아님 (현재 상태: {dispatch.status.value})")
            continue
        
        # 배차 상태 변경
        dispatch.status = DispatchStatus.COMPLETED
        
        # 차량 상태 변경 (복귀)
        if dispatch.vehicle:
            dispatch.vehicle.status = VehicleStatus.AVAILABLE
        
        # 주문 상태 변경 (배송완료)
        updated_orders = 0
        for route in dispatch.routes:
            if route.order:
                route.order.status = OrderStatus.DELIVERED
                updated_orders += 1
        
        completed.append(dispatch)
        print_info(f"배차 완료", 
                  f"{dispatch.dispatch_number} → 차량 {dispatch.vehicle.code} 복귀, "
                  f"주문 {updated_orders}건 배송완료")
    
    db.commit()
    
    print_info("총 완료 배차", f"{len(completed)}건")
    return completed


def print_summary(db: Session, orders: list, dispatches: list):
    """최종 결과 요약"""
    print_step("✅", "테스트 완료 - 최종 요약")
    
    # 주문 상태 통계
    order_status_counts = {}
    for order in orders:
        db.refresh(order)
        status = order.status.value
        order_status_counts[status] = order_status_counts.get(status, 0) + 1
    
    print("📦 주문 상태:")
    for status, count in order_status_counts.items():
        print(f"    - {status}: {count}건")
    
    # 배차 상태 통계
    dispatch_status_counts = {}
    total_distance = 0
    total_orders_assigned = 0
    
    for dispatch in dispatches:
        db.refresh(dispatch)
        status = dispatch.status.value
        dispatch_status_counts[status] = dispatch_status_counts.get(status, 0) + 1
        total_distance += dispatch.total_distance_km or 0
        total_orders_assigned += dispatch.total_orders
    
    print("\n🚚 배차 상태:")
    for status, count in dispatch_status_counts.items():
        print(f"    - {status}: {count}건")
    
    print(f"\n📊 통계:")
    print(f"    - 총 생성 주문: {len(orders)}건")
    print(f"    - 총 생성 배차: {len(dispatches)}건")
    print(f"    - 총 배정 주문: {total_orders_assigned}건")
    print(f"    - 총 주행 거리: {total_distance:.2f} km")
    
    # 차량 상태 확인
    vehicles = db.query(Vehicle).filter(
        Vehicle.id.in_([d.vehicle_id for d in dispatches])
    ).all()
    
    vehicle_status_counts = {}
    for vehicle in vehicles:
        status = vehicle.status.value
        vehicle_status_counts[status] = vehicle_status_counts.get(status, 0) + 1
    
    print(f"\n🚗 차량 상태 ({len(vehicles)}대):")
    for status, count in vehicle_status_counts.items():
        print(f"    - {status}: {count}대")


async def main():
    """메인 실행 함수"""
    print("\n" + "🚀 "  * 40)
    print("전체 배차 프로세스 End-to-End 테스트")
    print("🚀 " * 40)
    
    db = SessionLocal()
    
    try:
        # Step 1: 주문 등록
        orders = create_test_orders(db, count=10)
        
        if not orders:
            print_error("주문 생성 실패")
            return
        
        # Step 2: AI 배차 최적화
        dispatches = await optimize_and_create_dispatch(db, orders)
        
        if not dispatches:
            print_error("배차 생성 실패")
            return
        
        # Step 3: 배차 확정
        confirmed = confirm_dispatches(db, dispatches)
        
        # Step 4: 배차 진행
        in_progress = start_dispatches(db, confirmed)
        
        # Step 5: 배차 완료
        completed = complete_dispatches(db, in_progress)
        
        # 최종 요약
        print_summary(db, orders, dispatches)
        
    except Exception as e:
        print_error(f"테스트 실행 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
