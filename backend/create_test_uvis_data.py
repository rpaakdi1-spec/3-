"""
UVIS GPS 시스템 테스트 데이터 생성 스크립트
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import random
from app.core.database import SessionLocal
from app.models.vehicle import Vehicle
from app.models.uvis_gps import VehicleGPSLog, VehicleTemperatureLog, UvisAccessKey

def create_test_access_key(db):
    """테스트용 인증키 생성"""
    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=5)
    
    # 기존 키 비활성화
    db.query(UvisAccessKey).update({"is_active": False})
    
    access_key = UvisAccessKey(
        serial_key="S1910-3A84-4559--CC4",
        access_key="TEST-ACCESS-KEY-" + now.strftime("%Y%m%d%H%M%S"),
        issued_at=now,
        expires_at=expires_at,
        is_active=True
    )
    db.add(access_key)
    db.commit()
    print(f"✅ 테스트 인증키 생성 완료: {access_key.access_key}")
    return access_key

def create_test_gps_data(db, vehicles):
    """테스트용 GPS 데이터 생성"""
    # 한국 주요 도시 좌표
    locations = [
        {"name": "서울", "lat": 37.5665, "lng": 126.9780},
        {"name": "부산", "lat": 35.1796, "lng": 129.0756},
        {"name": "인천", "lat": 37.4563, "lng": 126.7052},
        {"name": "대구", "lat": 35.8714, "lng": 128.6014},
        {"name": "광주", "lat": 35.1595, "lng": 126.8526},
        {"name": "대전", "lat": 36.3504, "lng": 127.3845},
        {"name": "울산", "lat": 35.5384, "lng": 129.3114},
    ]
    
    now = datetime.utcnow()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")
    
    created_count = 0
    
    for vehicle in vehicles:
        if not vehicle.uvis_device_id:
            continue
        
        # 랜덤 위치 선택
        location = random.choice(locations)
        
        # 위치에 약간의 변화 추가 (이동 시뮬레이션)
        lat = location["lat"] + random.uniform(-0.01, 0.01)
        lng = location["lng"] + random.uniform(-0.01, 0.01)
        
        # 시동 상태 (70% 확률로 ON)
        is_engine_on = random.random() < 0.7
        turn_onoff = "ON" if is_engine_on else "OFF"
        
        # 속도 (시동 ON일 때만)
        speed = random.randint(30, 80) if is_engine_on else 0
        
        gps_log = VehicleGPSLog(
            vehicle_id=vehicle.id,
            tid_id=vehicle.uvis_device_id,
            bi_date=date_str,
            bi_time=time_str,
            cm_number=vehicle.plate_number,
            bi_turn_onoff=turn_onoff,
            bi_x_position=str(lat),
            bi_y_position=str(lng),
            bi_gps_speed=speed,
            latitude=lat,
            longitude=lng,
            is_engine_on=is_engine_on,
            speed_kmh=speed
        )
        db.add(gps_log)
        created_count += 1
    
    db.commit()
    print(f"✅ 테스트 GPS 데이터 {created_count}건 생성 완료")
    return created_count

def create_test_temperature_data(db, vehicles):
    """테스트용 온도 데이터 생성"""
    now = datetime.utcnow()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")
    
    created_count = 0
    
    for vehicle in vehicles:
        if not vehicle.uvis_device_id:
            continue
        
        # 냉동실 온도 (-25°C ~ -15°C)
        temp_a = random.uniform(-25.0, -15.0)
        signal_a = 1  # 음수
        degree_a = str(abs(temp_a))[:5]
        
        # 냉장실 온도 (0°C ~ 8°C)
        temp_b = random.uniform(0.0, 8.0)
        signal_b = 0  # 양수
        degree_b = str(temp_b)[:5]
        
        # 위치 (GPS와 동일하게)
        lat = 37.5665 + random.uniform(-0.5, 0.5)
        lng = 126.9780 + random.uniform(-0.5, 0.5)
        
        temp_log = VehicleTemperatureLog(
            vehicle_id=vehicle.id,
            off_key="TEST01",
            tid_id=vehicle.uvis_device_id,
            tpl_date=date_str,
            tpl_time=time_str,
            cm_number=vehicle.plate_number,
            tpl_x_position=str(lat),
            tpl_y_position=str(lng),
            tpl_signal_a=signal_a,
            tpl_degree_a=degree_a,
            temperature_a=temp_a,
            tpl_signal_b=signal_b,
            tpl_degree_b=degree_b,
            temperature_b=temp_b,
            latitude=lat,
            longitude=lng
        )
        db.add(temp_log)
        created_count += 1
    
    db.commit()
    print(f"✅ 테스트 온도 데이터 {created_count}건 생성 완료")
    return created_count

def main():
    """메인 실행"""
    print("=" * 60)
    print("🔧 UVIS GPS 테스트 데이터 생성")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 1. 차량 목록 조회
        vehicles = db.query(Vehicle).filter(Vehicle.is_active == True).all()
        print(f"\n📊 활성 차량 수: {len(vehicles)}")
        
        # UVIS 단말기 ID가 없는 차량에 자동 할당
        assigned_count = 0
        for vehicle in vehicles:
            if not vehicle.uvis_device_id:
                vehicle.uvis_device_id = f"UVIS-DVC-{vehicle.id:05d}"
                vehicle.uvis_enabled = True
                assigned_count += 1
        
        if assigned_count > 0:
            db.commit()
            print(f"✅ UVIS 단말기 ID {assigned_count}개 자동 할당 완료")
        
        # 2. 테스트 인증키 생성
        print("\n🔑 테스트 인증키 생성 중...")
        create_test_access_key(db)
        
        # 3. 테스트 GPS 데이터 생성
        print("\n📍 테스트 GPS 데이터 생성 중...")
        gps_count = create_test_gps_data(db, vehicles)
        
        # 4. 테스트 온도 데이터 생성
        print("\n🌡️ 테스트 온도 데이터 생성 중...")
        temp_count = create_test_temperature_data(db, vehicles)
        
        # 5. 결과 요약
        print("\n" + "=" * 60)
        print("✅ 테스트 데이터 생성 완료!")
        print("=" * 60)
        print(f"📊 생성된 데이터:")
        print(f"  - 차량 수: {len(vehicles)}")
        print(f"  - GPS 로그: {gps_count}건")
        print(f"  - 온도 로그: {temp_count}건")
        print(f"  - 인증키: 1개")
        print("\n🌐 프론트엔드에서 확인:")
        print("  1. GPS 관제 메뉴 접속")
        print("  2. '새로고침' 버튼 클릭")
        print("  3. 차량 상태 확인")
        print("\n📝 참고:")
        print("  - 실제 UVIS API 연동은 네트워크 환경에 따라 다를 수 있습니다")
        print("  - 이 데이터는 테스트/데모용입니다")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
