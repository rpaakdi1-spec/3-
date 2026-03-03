"""
차량 일별 주행거리 계산 서비스

GPS 로그 데이터를 기반으로 일별 주행거리 및 운행 통계 집계
"""
import logging
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.vehicle import Vehicle
from app.models.uvis_gps import VehicleGPSLog
from app.models.vehicle_daily_mileage import VehicleDailyMileage
import math

logger = logging.getLogger(__name__)


class VehicleMileageService:
    """차량 주행거리 계산 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        하버사인 공식으로 두 GPS 좌표 간 거리 계산 (km)
        
        Args:
            lat1, lon1: 시작점 위도/경도
            lat2, lon2: 끝점 위도/경도
            
        Returns:
            거리 (km)
        """
        R = 6371  # 지구 반지름 (km)
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def calculate_daily_mileage(
        self,
        vehicle_id: int,
        target_date: date
    ) -> Optional[VehicleDailyMileage]:
        """
        특정 날짜의 차량 주행거리 계산
        
        Args:
            vehicle_id: 차량 ID
            target_date: 집계 날짜
            
        Returns:
            VehicleDailyMileage 객체 또는 None
        """
        logger.info(f"📊 차량 {vehicle_id}의 {target_date} 주행거리 계산 시작")
        
        # 1. 해당 날짜의 GPS 로그 조회
        target_date_str = target_date.strftime("%Y%m%d")
        
        gps_logs = self.db.query(VehicleGPSLog).filter(
            and_(
                VehicleGPSLog.vehicle_id == vehicle_id,
                VehicleGPSLog.bi_date == target_date_str,
                VehicleGPSLog.latitude.isnot(None),
                VehicleGPSLog.longitude.isnot(None)
            )
        ).order_by(VehicleGPSLog.bi_time).all()
        
        if not gps_logs:
            logger.warning(f"⚠️ 차량 {vehicle_id}의 {target_date} GPS 로그 없음")
            return None
        
        logger.info(f"✅ GPS 로그 {len(gps_logs)}개 조회")
        
        # 2. 중복 제거 (같은 시간/좌표는 1개만 유지)
        unique_logs = []
        prev_key = None
        for log in gps_logs:
            key = (log.bi_time, log.latitude, log.longitude)
            if key != prev_key:
                unique_logs.append(log)
                prev_key = key
        
        if len(unique_logs) < 2:
            logger.warning(f"⚠️ 차량 {vehicle_id}의 {target_date} GPS 로그가 중복 제거 후 {len(unique_logs)}개 (계산 불가)")
            return None
        
        logger.info(f"✅ 중복 제거: {len(gps_logs)}개 → {len(unique_logs)}개")
        gps_logs = unique_logs
        
        # 3. 주행거리 계산
        total_distance = 0.0
        max_speed = 0
        total_speed = 0
        speed_count = 0
        engine_on_count = 0
        idle_count = 0  # 시동은 켜져있지만 속도가 0인 경우
        
        for i in range(len(gps_logs) - 1):
            current_log = gps_logs[i]
            next_log = gps_logs[i + 1]
            
            # 시간 간격 계산 (분)
            try:
                current_time = datetime.strptime(
                    f"{current_log.bi_date}{current_log.bi_time}",
                    "%Y%m%d%H%M%S"
                )
                next_time = datetime.strptime(
                    f"{next_log.bi_date}{next_log.bi_time}",
                    "%Y%m%d%H%M%S"
                )
                time_diff_minutes = (next_time - current_time).total_seconds() / 60
            except:
                time_diff_minutes = 1  # 기본값
            
            # 거리 계산
            distance = self.haversine_distance(
                current_log.latitude, current_log.longitude,
                next_log.latitude, next_log.longitude
            )
            
            # 거리 보정 로직 (보수적 접근)
            if time_diff_minutes <= 2:
                # 짧은 간격 (2분 이하): 하버사인 거리 × 1.2 (도로 굴곡 보정, 보수적)
                adjusted_distance = distance * 1.2
            elif time_diff_minutes <= 5 and current_log.speed_kmh and current_log.speed_kmh > 10:
                # 중간 간격 (5분 이하): 속도 기반과 하버사인 중 작은 값 사용
                speed_based_distance = (current_log.speed_kmh * time_diff_minutes) / 60
                adjusted_distance = min(distance * 1.2, speed_based_distance * 0.9)  # 속도 기반도 10% 할인
            else:
                # 긴 간격 (5분 초과) 또는 저속/정지: 하버사인만 사용
                adjusted_distance = distance * 1.2
            
            # 비정상적으로 큰 거리는 제외 (시속 120km 기준으로 강화)
            max_reasonable_distance = (120 * time_diff_minutes) / 60
            if adjusted_distance <= max_reasonable_distance:
                total_distance += adjusted_distance
            else:
                logger.debug(f"⚠️ 비정상 거리 제외: {adjusted_distance:.2f}km (시간: {time_diff_minutes:.1f}분, 최대: {max_reasonable_distance:.2f}km)")
            
            # 속도 통계
            if current_log.speed_kmh is not None:
                max_speed = max(max_speed, current_log.speed_kmh)
                total_speed += current_log.speed_kmh
                speed_count += 1
                
                # 공회전 체크 (시동 ON + 속도 0)
                if current_log.is_engine_on and current_log.speed_kmh == 0:
                    idle_count += 1
            
            # 시동 ON 카운트
            if current_log.is_engine_on:
                engine_on_count += 1
        
        # 평균 속도 계산
        avg_speed = (total_speed / speed_count) if speed_count > 0 else 0.0
        
        # 시간 계산 (1개 GPS 로그 = 약 1분 간격으로 가정)
        total_driving_minutes = len(gps_logs)
        engine_on_minutes = engine_on_count
        idle_minutes = idle_count
        
        # 시작/종료 위치
        start_log = gps_logs[0]
        end_log = gps_logs[-1]
        
        start_time = datetime.strptime(
            f"{start_log.bi_date}{start_log.bi_time}",
            "%Y%m%d%H%M%S"
        ).replace(tzinfo=timezone.utc)
        
        end_time = datetime.strptime(
            f"{end_log.bi_date}{end_log.bi_time}",
            "%Y%m%d%H%M%S"
        ).replace(tzinfo=timezone.utc)
        
        # 3. 기존 레코드 확인
        mileage = self.db.query(VehicleDailyMileage).filter(
            and_(
                VehicleDailyMileage.vehicle_id == vehicle_id,
                VehicleDailyMileage.date == target_date
            )
        ).first()
        
        if mileage:
            # 업데이트
            mileage.total_distance_km = round(total_distance, 2)
            mileage.total_driving_minutes = total_driving_minutes
            mileage.engine_on_minutes = engine_on_minutes
            mileage.idle_minutes = idle_minutes
            mileage.max_speed_kmh = max_speed
            mileage.avg_speed_kmh = round(avg_speed, 2)
            mileage.gps_point_count = len(gps_logs)
            mileage.start_latitude = start_log.latitude
            mileage.start_longitude = start_log.longitude
            mileage.start_time = start_time
            mileage.end_latitude = end_log.latitude
            mileage.end_longitude = end_log.longitude
            mileage.end_time = end_time
            mileage.is_calculated = True
            mileage.calculation_method = "haversine_speed_hybrid"
            logger.info(f"🔄 기존 레코드 업데이트")
        else:
            # 새 레코드 생성
            mileage = VehicleDailyMileage(
                vehicle_id=vehicle_id,
                date=target_date,
                total_distance_km=round(total_distance, 2),
                total_driving_minutes=total_driving_minutes,
                engine_on_minutes=engine_on_minutes,
                idle_minutes=idle_minutes,
                max_speed_kmh=max_speed,
                avg_speed_kmh=round(avg_speed, 2),
                gps_point_count=len(gps_logs),
                start_latitude=start_log.latitude,
                start_longitude=start_log.longitude,
                start_time=start_time,
                end_latitude=end_log.latitude,
                end_longitude=end_log.longitude,
                end_time=end_time,
                is_calculated=True,
                calculation_method="haversine_speed_hybrid"
            )
            self.db.add(mileage)
            logger.info(f"✨ 새 레코드 생성")
        
        self.db.commit()
        self.db.refresh(mileage)
        
        logger.info(f"✅ 주행거리 계산 완료: {total_distance:.2f}km, 평균 속도: {avg_speed:.1f}km/h")
        
        return mileage
    
    def calculate_all_vehicles_yesterday(self) -> List[VehicleDailyMileage]:
        """
        모든 차량의 어제 주행거리 계산
        
        배치 작업으로 매일 자동 실행
        
        Returns:
            계산된 VehicleDailyMileage 리스트
        """
        yesterday = date.today() - timedelta(days=1)
        logger.info(f"📊 모든 차량의 {yesterday} 주행거리 일괄 계산 시작")
        
        vehicles = self.db.query(Vehicle).filter(Vehicle.is_active == True).all()
        results = []
        
        for vehicle in vehicles:
            try:
                mileage = self.calculate_daily_mileage(vehicle.id, yesterday)
                if mileage:
                    results.append(mileage)
            except Exception as e:
                logger.error(f"❌ 차량 {vehicle.id} ({vehicle.plate_number}) 계산 실패: {e}")
                continue
        
        logger.info(f"✅ 총 {len(results)}개 차량 주행거리 계산 완료")
        return results
    
    def get_vehicle_mileage_summary(
        self,
        vehicle_id: int,
        start_date: date,
        end_date: date
    ) -> dict:
        """
        특정 기간 차량 주행거리 요약
        
        Args:
            vehicle_id: 차량 ID
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            {
                "total_distance_km": float,
                "total_days": int,
                "avg_distance_per_day": float,
                "max_distance_day": date,
                "max_distance_km": float
            }
        """
        mileages = self.db.query(VehicleDailyMileage).filter(
            and_(
                VehicleDailyMileage.vehicle_id == vehicle_id,
                VehicleDailyMileage.date >= start_date,
                VehicleDailyMileage.date <= end_date,
                VehicleDailyMileage.is_calculated == True
            )
        ).all()
        
        if not mileages:
            return {
                "total_distance_km": 0.0,
                "total_days": 0,
                "avg_distance_per_day": 0.0,
                "max_distance_day": None,
                "max_distance_km": 0.0
            }
        
        total_distance = sum(m.total_distance_km for m in mileages)
        total_days = len(mileages)
        avg_distance = total_distance / total_days if total_days > 0 else 0.0
        
        max_mileage = max(mileages, key=lambda m: m.total_distance_km)
        
        return {
            "total_distance_km": round(total_distance, 2),
            "total_days": total_days,
            "avg_distance_per_day": round(avg_distance, 2),
            "max_distance_day": max_mileage.date,
            "max_distance_km": max_mileage.total_distance_km
        }
