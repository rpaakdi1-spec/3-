"""
운전자 일별 주행거리 계산 서비스

차량 테이블의 운전자 정보를 기반으로 운전자별 주행거리 집계
"""
import logging
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models.driver import Driver
from app.models.vehicle import Vehicle
from app.models.dispatch import Dispatch, DispatchStatus
from app.models.vehicle_daily_mileage import VehicleDailyMileage
from app.models.driver_daily_mileage import DriverDailyMileage

logger = logging.getLogger(__name__)


class DriverMileageService:
    """운전자 주행거리 계산 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_driver_mileage_from_vehicle(self, target_date: date) -> List[DriverDailyMileage]:
        """
        차량 테이블의 운전자 정보 기반으로 주행거리 계산
        
        Args:
            target_date: 대상 날짜
            
        Returns:
            DriverDailyMileage 리스트
        """
        logger.info(f"📊 {target_date} 차량 기반 운전자별 주행거리 계산 시작")
        
        # 1. 해당 날짜에 주행 기록이 있는 차량의 주행거리 조회
        vehicle_mileages = self.db.query(
            VehicleDailyMileage, Vehicle
        ).join(
            Vehicle, VehicleDailyMileage.vehicle_id == Vehicle.id
        ).filter(
            VehicleDailyMileage.date == target_date
        ).all()
        
        if not vehicle_mileages:
            logger.info(f"ℹ️ {target_date} 주행 기록 없음")
            return []
        
        # 2. 운전자명 기준으로 그룹화
        driver_data: Dict[str, dict] = {}
        
        for mileage, vehicle in vehicle_mileages:
            driver_name = vehicle.driver_name
            if not driver_name or driver_name.strip() == "":
                logger.debug(f"⚠️ 차량 {vehicle.plate_number}에 운전자 미등록")
                continue
            
            driver_name = driver_name.strip()
            
            if driver_name not in driver_data:
                driver_data[driver_name] = {
                    "driver_name": driver_name,
                    "driver_phone": vehicle.driver_phone,
                    "total_distance_km": 0.0,
                    "total_driving_minutes": 0,
                    "total_engine_on_minutes": 0,
                    "total_idle_minutes": 0,
                    "max_speed": 0.0,
                    "total_speed": 0.0,
                    "speed_count": 0,
                    "total_gps_points": 0,
                    "vehicle_ids": set(),
                    "start_times": [],
                    "end_times": []
                }
            
            # 주행거리 합산
            data = driver_data[driver_name]
            data["total_distance_km"] += mileage.total_distance_km
            data["total_driving_minutes"] += mileage.total_driving_minutes
            data["total_engine_on_minutes"] += mileage.engine_on_minutes or 0
            data["total_idle_minutes"] += mileage.idle_minutes or 0
            data["total_gps_points"] += mileage.gps_point_count or 0
            data["vehicle_ids"].add(vehicle.id)
            
            if mileage.max_speed_kmh:
                data["max_speed"] = max(data["max_speed"], mileage.max_speed_kmh)
            
            if mileage.avg_speed_kmh:
                data["total_speed"] += mileage.avg_speed_kmh
                data["speed_count"] += 1
            
            if mileage.start_time:
                data["start_times"].append(mileage.start_time)
            if mileage.end_time:
                data["end_times"].append(mileage.end_time)
        
        # 3. DriverDailyMileage 레코드 생성/업데이트
        results = []
        
        for driver_name, data in driver_data.items():
            avg_speed = (data["total_speed"] / data["speed_count"]) if data["speed_count"] > 0 else 0.0
            start_time = min(data["start_times"]) if data["start_times"] else None
            end_time = max(data["end_times"]) if data["end_times"] else None
            vehicle_ids_str = ",".join(str(vid) for vid in sorted(data["vehicle_ids"]))
            
            # vehicles.driver_name으로 drivers 테이블에서 실제 driver_id 찾기
            driver = self.db.query(Driver).filter(Driver.name == driver_name).first()
            driver_id = driver.id if driver else None
            
            if not driver_id:
                logger.warning(f"⚠️ drivers 테이블에서 '{driver_name}' 운전자를 찾을 수 없음")
            
            # driver_id 기준으로 기존 레코드 찾기
            if driver_id:
                mileage = self.db.query(DriverDailyMileage).filter(
                    and_(
                        DriverDailyMileage.driver_id == driver_id,
                        DriverDailyMileage.date == target_date
                    )
                ).first()
            else:
                # driver_id가 없으면 notes로 찾기 (backward compatibility)
                mileage = self.db.query(DriverDailyMileage).filter(
                    and_(
                        DriverDailyMileage.date == target_date,
                        DriverDailyMileage.notes == f"차량기반:{driver_name}"
                    )
                ).first()
            
            if mileage:
                # 업데이트
                mileage.driver_id = driver_id  # driver_id 업데이트
                mileage.total_distance_km = round(data["total_distance_km"], 2)
                mileage.total_driving_minutes = data["total_driving_minutes"]
                mileage.engine_on_minutes = data["total_engine_on_minutes"]
                mileage.idle_minutes = data["total_idle_minutes"]
                mileage.max_speed_kmh = round(data["max_speed"], 2)
                mileage.avg_speed_kmh = round(avg_speed, 2)
                mileage.gps_point_count = data["total_gps_points"]
                mileage.start_time = start_time
                mileage.end_time = end_time
                mileage.vehicle_ids = vehicle_ids_str
                mileage.vehicle_count = len(data["vehicle_ids"])
                mileage.is_calculated = True
                mileage.calculation_method = "vehicle_based"
                logger.info(f"🔄 {driver_name} (ID: {driver_id}) 레코드 업데이트")
            else:
                # 새 레코드 생성 (driver_id 포함)
                mileage = DriverDailyMileage(
                    driver_id=driver_id,  # drivers 테이블의 실제 ID
                    date=target_date,
                    total_distance_km=round(data["total_distance_km"], 2),
                    total_driving_minutes=data["total_driving_minutes"],
                    engine_on_minutes=data["total_engine_on_minutes"],
                    idle_minutes=data["total_idle_minutes"],
                    max_speed_kmh=round(data["max_speed"], 2),
                    avg_speed_kmh=round(avg_speed, 2),
                    gps_point_count=data["total_gps_points"],
                    start_time=start_time,
                    end_time=end_time,
                    vehicle_ids=vehicle_ids_str,
                    vehicle_count=len(data["vehicle_ids"]),
                    is_calculated=True,
                    calculation_method="vehicle_based",
                    notes=f"차량기반:{driver_name}"  # 운전자명도 저장 (참고용)
                )
                self.db.add(mileage)
                logger.info(f"✨ {driver_name} (ID: {driver_id}) 새 레코드 생성")
            
            results.append(mileage)
            
            logger.info(
                f"✅ {driver_name}: {data['total_distance_km']:.2f}km, "
                f"{len(data['vehicle_ids'])}대 차량, 평균 {avg_speed:.1f}km/h"
            )
        
        self.db.commit()
        for m in results:
            self.db.refresh(m)
        
        logger.info(f"✅ 총 {len(results)}명 운전자 계산 완료")
        return results
    
    def calculate_driver_daily_mileage(self, driver_id: int, target_date: date) -> Optional[DriverDailyMileage]:
        """
        특정 운전자의 특정 날짜 주행거리 계산
        
        Args:
            driver_id: 운전자 ID
            target_date: 대상 날짜
            
        Returns:
            DriverDailyMileage 객체 또는 None
        """
        logger.info(f"📊 운전자 ID {driver_id}의 {target_date} 주행거리 계산 시작")
        
        # 1. 운전자 확인
        driver = self.db.query(Driver).filter(Driver.id == driver_id).first()
        if not driver:
            logger.warning(f"⚠️ 운전자 ID {driver_id} 없음")
            return None
        
        # 2. 해당 날짜의 배차 목록 조회 (확정/진행중/완료)
        dispatches = self.db.query(Dispatch).filter(
            and_(
                Dispatch.driver_id == driver_id,
                Dispatch.dispatch_date == target_date,
                Dispatch.status.in_([
                    DispatchStatus.CONFIRMED,
                    DispatchStatus.IN_PROGRESS,
                    DispatchStatus.COMPLETED
                ])
            )
        ).all()
        
        if not dispatches:
            logger.info(f"ℹ️ 운전자 {driver.name}의 {target_date} 배차 없음")
            return None
        
        # 3. 각 배차의 차량 주행거리 조회
        total_distance = 0.0
        total_driving_minutes = 0
        total_engine_on_minutes = 0
        total_idle_minutes = 0
        max_speed = 0.0
        total_speed = 0.0
        speed_count = 0
        total_gps_points = 0
        
        vehicle_ids_set = set()
        start_times = []
        end_times = []
        
        for dispatch in dispatches:
            vehicle_ids_set.add(dispatch.vehicle_id)
            
            # 차량 주행거리 조회
            vehicle_mileage = self.db.query(VehicleDailyMileage).filter(
                and_(
                    VehicleDailyMileage.vehicle_id == dispatch.vehicle_id,
                    VehicleDailyMileage.date == target_date
                )
            ).first()
            
            if vehicle_mileage:
                total_distance += vehicle_mileage.total_distance_km
                total_driving_minutes += vehicle_mileage.total_driving_minutes
                total_engine_on_minutes += vehicle_mileage.engine_on_minutes or 0
                total_idle_minutes += vehicle_mileage.idle_minutes or 0
                total_gps_points += vehicle_mileage.gps_point_count or 0
                
                if vehicle_mileage.max_speed_kmh:
                    max_speed = max(max_speed, vehicle_mileage.max_speed_kmh)
                
                if vehicle_mileage.avg_speed_kmh:
                    total_speed += vehicle_mileage.avg_speed_kmh
                    speed_count += 1
                
                if vehicle_mileage.start_time:
                    start_times.append(vehicle_mileage.start_time)
                if vehicle_mileage.end_time:
                    end_times.append(vehicle_mileage.end_time)
        
        # 4. 평균 속도 계산
        avg_speed = (total_speed / speed_count) if speed_count > 0 else 0.0
        
        # 5. 운행 시간대
        start_time = min(start_times) if start_times else None
        end_time = max(end_times) if end_times else None
        
        # 6. 차량 ID 목록
        vehicle_ids_str = ",".join(str(vid) for vid in sorted(vehicle_ids_set))
        
        # 7. 기존 레코드 확인
        mileage = self.db.query(DriverDailyMileage).filter(
            and_(
                DriverDailyMileage.driver_id == driver_id,
                DriverDailyMileage.date == target_date
            )
        ).first()
        
        if mileage:
            # 업데이트
            mileage.total_distance_km = round(total_distance, 2)
            mileage.total_driving_minutes = total_driving_minutes
            mileage.engine_on_minutes = total_engine_on_minutes
            mileage.idle_minutes = total_idle_minutes
            mileage.max_speed_kmh = round(max_speed, 2)
            mileage.avg_speed_kmh = round(avg_speed, 2)
            mileage.gps_point_count = total_gps_points
            mileage.start_time = start_time
            mileage.end_time = end_time
            mileage.vehicle_ids = vehicle_ids_str
            mileage.vehicle_count = len(vehicle_ids_set)
            mileage.is_calculated = True
            mileage.calculation_method = "dispatch_based"
            logger.info(f"🔄 기존 레코드 업데이트")
        else:
            # 새 레코드 생성
            mileage = DriverDailyMileage(
                driver_id=driver_id,
                date=target_date,
                total_distance_km=round(total_distance, 2),
                total_driving_minutes=total_driving_minutes,
                engine_on_minutes=total_engine_on_minutes,
                idle_minutes=total_idle_minutes,
                max_speed_kmh=round(max_speed, 2),
                avg_speed_kmh=round(avg_speed, 2),
                gps_point_count=total_gps_points,
                start_time=start_time,
                end_time=end_time,
                vehicle_ids=vehicle_ids_str,
                vehicle_count=len(vehicle_ids_set),
                is_calculated=True,
                calculation_method="dispatch_based"
            )
            self.db.add(mileage)
            logger.info(f"✨ 새 레코드 생성")
        
        self.db.commit()
        self.db.refresh(mileage)
        
        logger.info(
            f"✅ 운전자 {driver.name} 주행거리 계산 완료: "
            f"{total_distance:.2f}km, {len(vehicle_ids_set)}대 차량, "
            f"평균 속도: {avg_speed:.1f}km/h"
        )
        
        return mileage
    
    def calculate_all_drivers_yesterday(self) -> List[DriverDailyMileage]:
        """
        모든 운전자의 어제 주행거리 계산 (차량 테이블 기반)
        
        Returns:
            DriverDailyMileage 리스트
        """
        yesterday = date.today() - timedelta(days=1)
        logger.info(f"📊 전체 운전자 {yesterday} 주행거리 계산 시작 (차량 기반)")
        
        # 차량 테이블 기반으로 계산
        return self.calculate_driver_mileage_from_vehicle(yesterday)
    
    def get_driver_mileage_summary(
        self,
        driver_id: int,
        start_date: date,
        end_date: date
    ) -> dict:
        """
        운전자의 기간별 주행거리 요약
        
        Args:
            driver_id: 운전자 ID
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            요약 통계 dict
        """
        mileages = self.db.query(DriverDailyMileage).filter(
            and_(
                DriverDailyMileage.driver_id == driver_id,
                DriverDailyMileage.date >= start_date,
                DriverDailyMileage.date <= end_date
            )
        ).all()
        
        if not mileages:
            return {
                "driver_id": driver_id,
                "start_date": start_date,
                "end_date": end_date,
                "total_distance_km": 0.0,
                "driving_days": 0,
                "avg_distance_per_day": 0.0,
                "total_vehicles_used": 0
            }
        
        total_distance = sum(m.total_distance_km for m in mileages)
        driving_days = len(mileages)
        
        # 운행한 차량 수 (중복 제거)
        all_vehicle_ids = set()
        for m in mileages:
            if m.vehicle_ids:
                all_vehicle_ids.update(m.vehicle_ids.split(','))
        
        return {
            "driver_id": driver_id,
            "start_date": start_date,
            "end_date": end_date,
            "total_distance_km": round(total_distance, 2),
            "driving_days": driving_days,
            "avg_distance_per_day": round(total_distance / driving_days, 2) if driving_days > 0 else 0.0,
            "total_vehicles_used": len(all_vehicle_ids),
            "max_distance_day": max(mileages, key=lambda x: x.total_distance_km).date if mileages else None
        }
