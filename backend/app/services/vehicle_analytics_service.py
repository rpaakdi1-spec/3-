"""
Vehicle Analytics Service
차량 주행 거리 계산 및 통계 분석

Features:
- GPS 기반 주행 거리 계산
- 차량별 일/주/월 주행 거리
- 평균 속도, 최대 속도 통계
- 엔진 가동 시간 계산
- 정차 시간 계산
"""

from datetime import datetime, timedelta, date, timezone
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from math import radians, cos, sin, asin, sqrt
from loguru import logger

from app.models.vehicle import Vehicle
from app.models.uvis_gps import VehicleGPSLog


class VehicleAnalyticsService:
    """차량 분석 서비스"""
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Haversine 공식을 사용한 두 GPS 좌표 간 거리 계산 (km)
        
        Args:
            lat1, lon1: 시작점 좌표
            lat2, lon2: 종료점 좌표
        
        Returns:
            거리 (km)
        """
        # 지구 반지름 (km)
        R = 6371
        
        # 라디안 변환
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine 공식
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        return R * c
    
    @classmethod
    def calculate_vehicle_distance(
        cls,
        db: Session,
        vehicle_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        차량 주행 거리 계산
        
        Args:
            db: Database session
            vehicle_id: 차량 ID
            start_date: 시작 날짜 (기본: 오늘)
            end_date: 종료 날짜 (기본: 오늘)
        
        Returns:
            통계 딕셔너리
        """
        if not start_date:
            start_date = date.today()
        if not end_date:
            end_date = date.today()
        
        # 차량 정보 조회
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle or not vehicle.uvis_device_id:
            return {
                "vehicle_id": vehicle_id,
                "total_distance_km": 0,
                "data_points": 0,
                "error": "Vehicle not found or no UVIS device"
            }
        
        # GPS 로그 조회 (시간순 정렬)
        gps_logs = db.query(VehicleGPSLog).filter(
            and_(
                VehicleGPSLog.tid_id == vehicle.uvis_device_id,
                VehicleGPSLog.latitude.isnot(None),
                VehicleGPSLog.longitude.isnot(None),
                func.date(VehicleGPSLog.created_at) >= start_date,
                func.date(VehicleGPSLog.created_at) <= end_date
            )
        ).order_by(VehicleGPSLog.created_at).all()
        
        if len(gps_logs) < 2:
            return {
                "vehicle_id": vehicle_id,
                "vehicle_plate": vehicle.plate_number,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_distance_km": 0,
                "data_points": len(gps_logs),
                "error": "Insufficient GPS data"
            }
        
        # 주행 거리 계산
        total_distance = 0
        max_speed = 0
        speed_sum = 0
        engine_on_count = 0
        
        for i in range(1, len(gps_logs)):
            prev_log = gps_logs[i-1]
            curr_log = gps_logs[i]
            
            # 두 점 사이 거리 계산
            if prev_log.latitude and prev_log.longitude and curr_log.latitude and curr_log.longitude:
                distance = cls.calculate_distance(
                    prev_log.latitude,
                    prev_log.longitude,
                    curr_log.latitude,
                    curr_log.longitude
                )
                
                # 비정상적인 거리 필터링 (1km 이상 점프는 무시)
                if distance < 1.0:
                    total_distance += distance
            
            # 속도 통계
            if curr_log.speed_kmh:
                speed_sum += curr_log.speed_kmh
                max_speed = max(max_speed, curr_log.speed_kmh)
            
            # 엔진 가동 통계
            if curr_log.is_engine_on:
                engine_on_count += 1
        
        avg_speed = speed_sum / len(gps_logs) if len(gps_logs) > 0 else 0
        
        return {
            "vehicle_id": vehicle_id,
            "vehicle_plate": vehicle.plate_number,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_distance_km": round(total_distance, 2),
            "data_points": len(gps_logs),
            "max_speed_kmh": round(max_speed, 1),
            "avg_speed_kmh": round(avg_speed, 1),
            "engine_on_ratio": round(engine_on_count / len(gps_logs) * 100, 1) if len(gps_logs) > 0 else 0
        }
    
    @classmethod
    def get_fleet_statistics(
        cls,
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        전체 차량 통계 (vehicle_daily_mileage 테이블 사용)
        
        Returns:
            통계 딕셔너리
        """
        from app.models.vehicle_daily_mileage import VehicleDailyMileage
        
        if not start_date:
            start_date = date.today() - timedelta(days=7)  # 기본 최근 7일
        if not end_date:
            end_date = date.today()
        
        # 모든 활성 차량 조회
        vehicles = db.query(Vehicle).filter(Vehicle.is_active == True).all()
        total_vehicles = len(vehicles)
        
        # vehicle_daily_mileage에서 주행거리 데이터 조회
        mileage_data = db.query(VehicleDailyMileage).filter(
            and_(
                VehicleDailyMileage.date >= start_date,
                VehicleDailyMileage.date <= end_date,
                VehicleDailyMileage.is_calculated == True
            )
        ).all()
        
        # 차량별 통계 집계
        vehicle_map = {}
        for mileage in mileage_data:
            if mileage.vehicle_id not in vehicle_map:
                vehicle_map[mileage.vehicle_id] = {
                    "total_distance_km": 0,
                    "max_speed_kmh": 0,
                    "speed_sum": 0,
                    "speed_count": 0,
                    "data_points": 0
                }
            
            vehicle_map[mileage.vehicle_id]["total_distance_km"] += mileage.total_distance_km
            vehicle_map[mileage.vehicle_id]["max_speed_kmh"] = max(
                vehicle_map[mileage.vehicle_id]["max_speed_kmh"],
                mileage.max_speed_kmh or 0
            )
            if mileage.avg_speed_kmh and mileage.avg_speed_kmh > 0:
                vehicle_map[mileage.vehicle_id]["speed_sum"] += mileage.avg_speed_kmh
                vehicle_map[mileage.vehicle_id]["speed_count"] += 1
            vehicle_map[mileage.vehicle_id]["data_points"] += 1
        
        # 차량 정보와 결합
        vehicle_stats = []
        total_distance = 0
        active_vehicles = 0
        
        for vehicle in vehicles:
            if vehicle.id in vehicle_map:
                stats = vehicle_map[vehicle.id]
                avg_speed = stats["speed_sum"] / stats["speed_count"] if stats["speed_count"] > 0 else 0
                
                vehicle_stats.append({
                    "vehicle_id": vehicle.id,
                    "vehicle_plate": vehicle.plate_number,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_distance_km": round(stats["total_distance_km"], 2),
                    "data_points": stats["data_points"],
                    "max_speed_kmh": round(stats["max_speed_kmh"], 1),
                    "avg_speed_kmh": round(avg_speed, 1),
                    "engine_on_ratio": 0  # 계산된 주행거리 데이터에는 없음
                })
                
                total_distance += stats["total_distance_km"]
                active_vehicles += 1
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "total_vehicles": total_vehicles,
            "active_vehicles": active_vehicles,
            "total_distance_km": round(total_distance, 2),
            "avg_distance_per_vehicle_km": round(total_distance / active_vehicles, 2) if active_vehicles > 0 else 0,
            "vehicle_stats": vehicle_stats
        }
    
    @classmethod
    def get_vehicle_realtime_status(
        cls,
        db: Session,
        vehicle_id: int
    ) -> Dict[str, Any]:
        """
        차량 실시간 상태
        
        Returns:
            상태 딕셔너리
        """
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle or not vehicle.uvis_device_id:
            return {"error": "Vehicle not found"}
        
        # 최근 GPS 로그
        latest_gps = db.query(VehicleGPSLog).filter(
            VehicleGPSLog.tid_id == vehicle.uvis_device_id
        ).order_by(VehicleGPSLog.created_at.desc()).first()
        
        if not latest_gps:
            return {
                "vehicle_id": vehicle_id,
                "vehicle_plate": vehicle.plate_number,
                "status": "offline",
                "message": "GPS 데이터 없음"
            }
        
        # 마지막 업데이트 시간
        time_since_update = datetime.now(timezone.utc) - latest_gps.created_at
        
        # 상태 판단
        if time_since_update > timedelta(hours=24):  # 1시간 → 24시간으로 완화
            status = "offline"
            message = f"{int(time_since_update.total_seconds() / 3600)}시간 전 마지막 신호"
        elif latest_gps.is_engine_on:
            status = "running"
            message = f"운행 중 ({latest_gps.speed_kmh} km/h)"
        else:
            status = "stopped"
            message = "정차 중"
        
        return {
            "vehicle_id": vehicle_id,
            "vehicle_plate": vehicle.plate_number,
            "status": status,
            "message": message,
            "gps": {
                "latitude": latest_gps.latitude,
                "longitude": latest_gps.longitude,
                "speed_kmh": latest_gps.speed_kmh,
                "is_engine_on": latest_gps.is_engine_on,
                "last_updated": latest_gps.created_at.isoformat()
            },
            "time_since_update_minutes": int(time_since_update.total_seconds() / 60)
        }
