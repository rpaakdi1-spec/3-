#!/usr/bin/env python3
"""
실시간 모니터링 페이지 디버그 테스트
"""
import requests
import json

# API 테스트
print("=" * 50)
print("실시간 모니터링 API 테스트")
print("=" * 50)

url = "http://localhost:8000/api/v1/uvis-gps/realtime/vehicles"
print(f"\n📡 API 요청: {url}")

try:
    response = requests.get(url, timeout=10)
    print(f"✅ 응답 코드: {response.status_code}")
    
    data = response.json()
    total = data.get('total', 0)
    items = data.get('items', [])
    
    print(f"\n📊 데이터 요약:")
    print(f"  - 총 차량: {total}대")
    print(f"  - 데이터 개수: {len(items)}개")
    
    if len(items) > 0:
        v = items[0]
        print(f"\n🚗 샘플 차량 (첫 번째):")
        print(f"  - 차량번호: {v.get('vehicle_plate_number')}")
        print(f"  - TID: {v.get('tid_id')}")
        print(f"  - 위도: {v.get('latitude')}")
        print(f"  - 경도: {v.get('longitude')}")
        print(f"  - 시동: {v.get('is_engine_on')}")
        print(f"  - 속도: {v.get('speed_kmh')} km/h")
        
        # GPS 위치 있는 차량 확인
        vehicles_with_gps = [
            item for item in items 
            if item.get('latitude') and item.get('longitude') 
            and item.get('latitude') != 0 and item.get('longitude') != 0
        ]
        print(f"\n📍 GPS 위치 있는 차량: {len(vehicles_with_gps)}대")
        
        if len(vehicles_with_gps) == 0:
            print("⚠️ 경고: GPS 위치가 있는 차량이 없습니다!")
        else:
            print("✅ 지도에 표시될 차량이 있습니다!")
            
            # 샘플 3대
            print(f"\n🗺️ 지도 마커 샘플 (3대):")
            for i, v in enumerate(vehicles_with_gps[:3], 1):
                print(f"{i}. {v.get('vehicle_plate_number')} - ({v.get('latitude'):.6f}, {v.get('longitude'):.6f})")
    else:
        print("⚠️ 데이터가 없습니다!")
        
except Exception as e:
    print(f"❌ 오류 발생: {e}")

print("\n" + "=" * 50)
print("테스트 완료")
print("=" * 50)
