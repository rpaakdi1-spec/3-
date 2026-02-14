#!/usr/bin/env python3
"""
테스트 배차 데이터 생성 스크립트
사용법: docker exec -it uvis-backend python3 /app/generate_test_dispatches.py
"""

from app.core.database import SessionLocal
from app.models.dispatch import Dispatch, DispatchStatus
from app.models.vehicle import Vehicle
from datetime import date, timedelta
import random

def generate_test_dispatches():
    db = SessionLocal()
    
    try:
        # 차량 5대 가져오기
        vehicles = db.query(Vehicle).limit(5).all()
        
        if len(vehicles) == 0:
            print("❌ 차량이 없습니다.")
            return
        
        print(f"✅ {len(vehicles)}대의 차량으로 테스트 배차 생성 시작...")
        
        # 최근 7일간 배차 생성
        for i, vehicle in enumerate(vehicles):
            for day_offset in range(7):
                dispatch = Dispatch(
                    dispatch_number=f'TEST-{i+1:03d}-{day_offset+1}',
                    dispatch_date=date.today() - timedelta(days=day_offset),
                    vehicle_id=vehicle.id,
                    total_orders=random.randint(2, 6),
                    total_pallets=random.randint(10, 30),
                    total_weight_kg=round(random.uniform(300, 800), 1),
                    total_distance_km=round(random.uniform(30, 100), 1),
                    empty_distance_km=round(random.uniform(5, 20), 1),
                    estimated_cost=random.randint(40000, 120000),
                    status=DispatchStatus.COMPLETED,
                    optimization_score=round(random.uniform(0.75, 0.95), 2)
                )
                db.add(dispatch)
            print(f"  - {vehicle.vehicle_code}: 7건 생성")
        
        db.commit()
        total_created = len(vehicles) * 7
        print(f"\n✅ 총 {total_created}건의 테스트 배차 생성 완료!")
        
        # 통계 확인
        from sqlalchemy import func
        stats = db.query(
            func.count(Dispatch.id).label('total'),
            func.avg(Dispatch.total_distance_km).label('avg_distance'),
            func.avg(Dispatch.empty_distance_km).label('avg_empty'),
            func.avg(Dispatch.optimization_score).label('avg_score')
        ).first()
        
        print(f"\n📊 현재 배차 통계:")
        print(f"  - 총 배차 건수: {stats.total}건")
        print(f"  - 평균 총 거리: {stats.avg_distance:.1f}km")
        print(f"  - 평균 공차 거리: {stats.avg_empty:.1f}km")
        print(f"  - 평균 최적화 점수: {stats.avg_score:.2f}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_test_dispatches()
