import requests
import json
from datetime import date

API_BASE = "http://localhost:8000/api/v1"

# 테스트용 다중 주문 생성 (3개 주문)
orders_to_create = [
    {
        "order_number": "TSP-TEST-001",
        "order_date": str(date.today()),
        "temperature_zone": "냉동",
        "pickup_client_id": 1,
        "delivery_client_id": 2,
        "pallet_count": 4,
        "weight_kg": 200.0,
        "priority": 3
    },
    {
        "order_number": "TSP-TEST-002",
        "order_date": str(date.today()),
        "temperature_zone": "냉동",
        "pickup_client_id": 1,
        "delivery_client_id": 8,
        "pallet_count": 6,
        "weight_kg": 350.0,
        "priority": 2
    },
    {
        "order_number": "TSP-TEST-003",
        "order_date": str(date.today()),
        "temperature_zone": "냉동",
        "pickup_client_id": 1,
        "delivery_client_id": 9,
        "pallet_count": 3,
        "weight_kg": 150.0,
        "priority": 1
    }
]

print("=== 다중 주문 TSP 테스트용 주문 생성 ===\n")

created_order_ids = []

for order_data in orders_to_create:
    response = requests.post(f"{API_BASE}/orders/", json=order_data)
    if response.status_code == 200:
        order = response.json()
        print(f"✓ 주문 생성: {order['order_number']}")
        print(f"  - ID: {order['id']}")
        print(f"  - 팔레트: {order['pallet_count']}, 중량: {order['weight_kg']} kg")
        print(f"  - 상태: {order['status']}\n")
        created_order_ids.append(order['id'])
    else:
        print(f"✗ 주문 생성 실패: {order_data['order_number']}")
        print(f"  - Error: {response.text}\n")

print(f"\n총 {len(created_order_ids)}개 주문 생성 완료")
print(f"주문 IDs: {created_order_ids}")

# TSP 최적화 배차 실행
print("\n=== TSP 최적화 배차 실행 ===\n")

dispatch_request = {
    "order_ids": created_order_ids,
    "dispatch_date": "2026-01-28",
    "algorithm": "greedy"
}

response = requests.post(f"{API_BASE}/dispatches/optimize", json=dispatch_request)

if response.status_code == 200:
    result = response.json()
    print(f"✓ 배차 최적화 성공")
    print(f"  - 총 주문: {result.get('total_orders')}")
    print(f"  - 총 배차: {result.get('total_dispatches')}")
    
    for dispatch in result.get('dispatches', []):
        print(f"\n배차번호: {dispatch['dispatch_number']}")
        print(f"차량: {dispatch.get('vehicle_code')}")
        print(f"총 팔레트: {dispatch['total_pallets']}, 총 중량: {dispatch['total_weight_kg']} kg")
        print(f"\n경로 순서 (TSP 최적화):")
        for route in dispatch.get('routes', []):
            print(f"  {route['sequence']}. {route['route_type']} - {route['location_name']}")
            print(f"     주소: {route['address']}")
            print(f"     팔레트: {route['current_pallets']}, 중량: {route['current_weight_kg']} kg")
else:
    print(f"✗ 배차 실패: {response.text}")
