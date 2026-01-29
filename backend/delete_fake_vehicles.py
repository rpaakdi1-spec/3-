"""
UVIS 가상차량 삭제 스크립트
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.vehicle import Vehicle

db = SessionLocal()

try:
    print("\n" + "="*60)
    print("🗑️  UVIS 가상차량 삭제 시작")
    print("="*60)
    
    # UVIS 연동 안 된 차량 조회
    fake_vehicles = db.query(Vehicle).filter(
        (Vehicle.uvis_device_id == None) | 
        (Vehicle.uvis_device_id.like('UVIS-DVC-%'))
    ).all()
    
    print(f"\n🔍 삭제 대상 차량: {len(fake_vehicles)}대")
    
    for vehicle in fake_vehicles:
        print(f"  - {vehicle.plate_number} (UVIS ID: {vehicle.uvis_device_id})")
    
    # 삭제 확인
    print(f"\n⚠️  {len(fake_vehicles)}대의 가상차량을 삭제합니다...")
    
    # 삭제 실행
    from app.models import Dispatch, VehicleGPSLog, VehicleTemperatureLog
    
    for vehicle in fake_vehicles:
        # 관련 데이터 먼저 삭제
        # 1. 배차 데이터 삭제
        db.query(Dispatch).filter(Dispatch.vehicle_id == vehicle.id).delete()
        
        # 2. GPS 로그 삭제
        db.query(VehicleGPSLog).filter(VehicleGPSLog.vehicle_id == vehicle.id).delete()
        
        # 3. 온도 로그 삭제
        db.query(VehicleTemperatureLog).filter(VehicleTemperatureLog.vehicle_id == vehicle.id).delete()
        
        # 4. 차량 삭제
        db.delete(vehicle)
    
    db.commit()
    
    print("\n✅ 가상차량 삭제 완료!")
    
    # 최종 통계
    remaining_vehicles = db.query(Vehicle).count()
    real_uvis_vehicles = db.query(Vehicle).filter(
        Vehicle.uvis_device_id != None,
        ~Vehicle.uvis_device_id.like('UVIS-DVC-%')
    ).count()
    
    print("\n" + "="*60)
    print("📊 최종 통계")
    print("="*60)
    print(f"  - 남은 차량: {remaining_vehicles}대")
    print(f"  - 실제 UVIS 차량: {real_uvis_vehicles}대")
    print(f"  - 삭제된 차량: {len(fake_vehicles)}대")
    
except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
    db.rollback()
finally:
    db.close()
