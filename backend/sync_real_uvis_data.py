"""
실제 UVIS 데이터와 DB 차량 동기화 스크립트
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.vehicle import Vehicle
from app.services.uvis_gps_service import UvisGPSService
import asyncio


async def sync_uvis_vehicles():
    """UVIS API에서 실제 차량 데이터 가져와서 DB와 동기화"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("🔄 실제 UVIS 데이터 동기화 시작")
        print("="*60)
        
        # UVIS 서비스 초기화
        service = UvisGPSService(db)
        
        # 1. 인증키 발급
        print("\n🔑 UVIS 인증키 발급 중...")
        access_key = await service.issue_access_key()
        
        if not access_key:
            print("❌ 인증키 발급 실패")
            return
        
        print(f"✅ 인증키 발급 성공: {access_key[:50]}...")
        
        # 2. GPS 데이터 조회
        print("\n📡 실시간 GPS 데이터 조회 중...")
        gps_data = await service.get_vehicle_gps_data()
        
        if not gps_data:
            print("❌ GPS 데이터 조회 실패")
            return
        
        print(f"✅ GPS 데이터 {len(gps_data)}건 조회 성공")
        
        # 3. 차량 매칭 및 업데이트
        print("\n🔄 차량 정보 매칭 및 업데이트 중...")
        
        updated_count = 0
        new_count = 0
        
        for item in gps_data:
            tid_id = item.get("TID_ID")
            cm_number = item.get("CM_NUMBER")
            
            if not tid_id or not cm_number:
                continue
            
            # 차량번호 또는 UVIS ID로 차량 찾기
            vehicle = db.query(Vehicle).filter(
                (Vehicle.plate_number == cm_number) | 
                (Vehicle.uvis_device_id == tid_id)
            ).first()
            
            if vehicle:
                # 기존 차량 업데이트
                vehicle.plate_number = cm_number
                vehicle.uvis_device_id = tid_id
                vehicle.is_active = True
                vehicle.uvis_enabled = True
                updated_count += 1
                
                print(f"  ✅ 업데이트: {cm_number} (UVIS: {tid_id})")
            else:
                # 새 차량 추가
                from app.models.vehicle import VehicleType, VehicleStatus
                new_vehicle = Vehicle(
                    code=f"V{tid_id}",
                    plate_number=cm_number,
                    vehicle_type=VehicleType.REFRIGERATED,
                    max_pallets=10,
                    max_weight_kg=5000.0,
                    tonnage=2.5,
                    status=VehicleStatus.AVAILABLE,
                    uvis_device_id=tid_id,
                    is_active=True,
                    uvis_enabled=True
                )
                db.add(new_vehicle)
                new_count += 1
                
                print(f"  ➕ 신규 추가: {cm_number} (UVIS: {tid_id})")
        
        db.commit()
        
        print("\n" + "="*60)
        print("✅ 차량 동기화 완료")
        print("="*60)
        print(f"📊 업데이트된 차량: {updated_count}대")
        print(f"📊 새로 추가된 차량: {new_count}대")
        print(f"📊 총 UVIS 차량: {updated_count + new_count}대")
        
        # 4. 온도 데이터 조회
        print("\n🌡️  실시간 온도 데이터 조회 중...")
        temp_data = await service.get_vehicle_temperature_data()
        
        if temp_data:
            print(f"✅ 온도 데이터 {len(temp_data)}건 조회 성공")
        
        print("\n" + "="*60)
        print("✅ 실제 UVIS 데이터 동기화 완료")
        print("="*60)
        
        # 5. 최종 통계
        total_vehicles = db.query(Vehicle).count()
        active_vehicles = db.query(Vehicle).filter(Vehicle.is_active == True).count()
        uvis_vehicles = db.query(Vehicle).filter(Vehicle.uvis_enabled == True).count()
        
        print(f"\n📊 최종 통계:")
        print(f"  - 전체 차량: {total_vehicles}대")
        print(f"  - 활성 차량: {active_vehicles}대")
        print(f"  - UVIS 연동 차량: {uvis_vehicles}대")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(sync_uvis_vehicles())
