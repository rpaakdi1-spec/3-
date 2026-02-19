"""
차량 위치 예측 알고리즘
- 과거 GPS 데이터 기반 위치 예측
- 배차 경로 기반 예상 위치 계산
- 시간대별 이동 패턴 학습
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from loguru import logger
import statistics
import math

from app.models.vehicle import Vehicle
from app.models.vehicle_location import VehicleLocation
from app.models.dispatch import Dispatch, DispatchRoute, DispatchStatus


class VehicleLocationPredictor:
    """차량 위치 예측 서비스"""
    
    # 예측 설정
    PREDICTION_HORIZON_MINUTES = 30    # 30분 후 위치 예측
    HISTORY_WINDOW_DAYS = 7            # 7일간 이력 사용
    MIN_HISTORY_POINTS = 10            # 최소 이력 포인트 수
    
    # 평균 속도 (km/h) - 도로 타입별
    AVERAGE_SPEEDS = {
        'highway': 80,      # 고속도로
        'arterial': 50,     # 간선도로
        'local': 30,        # 지역도로
        'default': 40       # 기본
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    async def predict_vehicle_location(
        self,
        vehicle_id: int,
        prediction_minutes: int = 30
    ) -> Dict[str, Any]:
        """
        차량의 미래 위치 예측
        
        Args:
            vehicle_id: 차량 ID
            prediction_minutes: 예측 시간 (분)
        
        Returns:
            예측 결과
        """
        logger.info(f"🔮 차량 {vehicle_id} 위치 예측 시작 ({prediction_minutes}분 후)")
        
        vehicle = self.db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            return {"success": False, "error": "Vehicle not found"}
        
        # 1. 최신 GPS 위치
        latest_location = self.db.query(VehicleLocation).filter(
            VehicleLocation.vehicle_id == vehicle_id
        ).order_by(VehicleLocation.recorded_at.desc()).first()
        
        if not latest_location:
            return {
                "success": False,
                "error": "No GPS data available",
                "vehicle_id": vehicle_id,
                "vehicle_code": vehicle.vehicle_code
            }
        
        # 2. 배차 정보 확인
        active_dispatch = self.db.query(Dispatch).filter(
            and_(
                Dispatch.vehicle_id == vehicle_id,
                Dispatch.status.in_([
                    DispatchStatus.ASSIGNED,
                    DispatchStatus.IN_PROGRESS
                ])
            )
        ).order_by(Dispatch.dispatch_date.desc()).first()
        
        # 3. 예측 방법 선택
        if active_dispatch and active_dispatch.routes:
            # 배차 경로 기반 예측
            predicted = await self._predict_by_dispatch_route(
                latest_location, active_dispatch, prediction_minutes
            )
        else:
            # 이력 기반 예측
            predicted = await self._predict_by_history(
                vehicle_id, latest_location, prediction_minutes
            )
        
        result = {
            "success": True,
            "vehicle_id": vehicle_id,
            "vehicle_code": vehicle.vehicle_code,
            "current_location": {
                "latitude": latest_location.latitude,
                "longitude": latest_location.longitude,
                "recorded_at": latest_location.recorded_at.isoformat(),
                "speed": latest_location.speed,
                "heading": latest_location.heading
            },
            "predicted_location": predicted,
            "prediction_time_minutes": prediction_minutes,
            "has_active_dispatch": active_dispatch is not None,
            "prediction_confidence": predicted.get("confidence", 0)
        }
        
        logger.info(
            f"✅ 위치 예측 완료: ({predicted['latitude']:.6f}, {predicted['longitude']:.6f}), "
            f"신뢰도 {predicted.get('confidence', 0)}%"
        )
        
        return result
    
    async def _predict_by_dispatch_route(
        self,
        current_location: VehicleLocation,
        dispatch: Dispatch,
        prediction_minutes: int
    ) -> Dict[str, Any]:
        """
        배차 경로 기반 위치 예측
        
        Args:
            current_location: 현재 위치
            dispatch: 배차 정보
            prediction_minutes: 예측 시간
        
        Returns:
            예측 위치
        """
        logger.info("📍 배차 경로 기반 예측 사용")
        
        # 다음 목적지 찾기
        routes = sorted(dispatch.routes, key=lambda r: r.sequence_number)
        
        next_destination = None
        for route in routes:
            # 아직 방문하지 않은 경로
            if not route.actual_arrival_time:
                next_destination = route
                break
        
        if not next_destination:
            # 모든 경로 완료 - 차고지로 복귀 예측
            if dispatch.vehicle.garage_latitude and dispatch.vehicle.garage_longitude:
                dest_lat = dispatch.vehicle.garage_latitude
                dest_lon = dispatch.vehicle.garage_longitude
            else:
                # 현재 위치 유지 예측
                return {
                    "latitude": current_location.latitude,
                    "longitude": current_location.longitude,
                    "method": "dispatch_route",
                    "confidence": 50,
                    "note": "All routes completed, predicting return to garage or stay at current location"
                }
        else:
            # 다음 목적지 좌표
            dest_lat = next_destination.destination_latitude
            dest_lon = next_destination.destination_longitude
        
        # 현재 위치에서 목적지까지 거리
        distance_km = self._calculate_distance(
            current_location.latitude,
            current_location.longitude,
            dest_lat,
            dest_lon
        )
        
        # 평균 속도 추정 (배차 경로 타입 또는 기본값)
        avg_speed_kmh = self.AVERAGE_SPEEDS.get('default', 40)
        
        # 현재 속도 정보가 있으면 사용
        if current_location.speed:
            avg_speed_kmh = current_location.speed
        
        # 예측 시간 동안 이동 가능 거리
        travel_distance_km = (avg_speed_kmh * prediction_minutes) / 60
        
        # 목적지까지 거리가 이동 가능 거리보다 짧으면 목적지 도착 예측
        if distance_km <= travel_distance_km:
            predicted_lat = dest_lat
            predicted_lon = dest_lon
            confidence = 80
        else:
            # 중간 지점 예측 (현재 → 목적지 방향)
            progress_ratio = travel_distance_km / distance_km
            predicted_lat, predicted_lon = self._interpolate_location(
                current_location.latitude,
                current_location.longitude,
                dest_lat,
                dest_lon,
                progress_ratio
            )
            confidence = 70
        
        return {
            "latitude": predicted_lat,
            "longitude": predicted_lon,
            "method": "dispatch_route",
            "confidence": confidence,
            "next_destination": {
                "latitude": dest_lat,
                "longitude": dest_lon,
                "distance_km": round(distance_km, 2)
            }
        }
    
    async def _predict_by_history(
        self,
        vehicle_id: int,
        current_location: VehicleLocation,
        prediction_minutes: int
    ) -> Dict[str, Any]:
        """
        과거 이력 기반 위치 예측
        
        Args:
            vehicle_id: 차량 ID
            current_location: 현재 위치
            prediction_minutes: 예측 시간
        
        Returns:
            예측 위치
        """
        logger.info("📊 과거 이력 기반 예측 사용")
        
        # 최근 이력 조회
        since = datetime.now(timezone.utc) - timedelta(days=self.HISTORY_WINDOW_DAYS)
        
        history = self.db.query(VehicleLocation).filter(
            and_(
                VehicleLocation.vehicle_id == vehicle_id,
                VehicleLocation.recorded_at >= since
            )
        ).order_by(VehicleLocation.recorded_at).all()
        
        if len(history) < self.MIN_HISTORY_POINTS:
            # 이력 부족 - 현재 위치 유지 예측
            return {
                "latitude": current_location.latitude,
                "longitude": current_location.longitude,
                "method": "history_insufficient",
                "confidence": 30,
                "note": f"Insufficient history ({len(history)} points)"
            }
        
        # 평균 이동 속도 계산
        speeds = [loc.speed for loc in history if loc.speed]
        avg_speed_kmh = statistics.mean(speeds) if speeds else self.AVERAGE_SPEEDS['default']
        
        # 평균 방향 계산 (최근 10개 포인트)
        recent_history = history[-10:] if len(history) >= 10 else history
        headings = [loc.heading for loc in recent_history if loc.heading]
        avg_heading = statistics.mean(headings) if headings else None
        
        # 현재 속도와 방향 사용 (있으면)
        if current_location.speed:
            speed_kmh = current_location.speed
        else:
            speed_kmh = avg_speed_kmh
        
        if current_location.heading:
            heading = current_location.heading
        elif avg_heading:
            heading = avg_heading
        else:
            # 방향 정보 없음 - 현재 위치 유지
            return {
                "latitude": current_location.latitude,
                "longitude": current_location.longitude,
                "method": "history_no_heading",
                "confidence": 40,
                "note": "No heading information available"
            }
        
        # 예측 시간 동안 이동 거리
        distance_km = (speed_kmh * prediction_minutes) / 60
        
        # 방향과 거리로 예측 위치 계산
        predicted_lat, predicted_lon = self._calculate_destination(
            current_location.latitude,
            current_location.longitude,
            heading,
            distance_km
        )
        
        return {
            "latitude": predicted_lat,
            "longitude": predicted_lon,
            "method": "history",
            "confidence": 60,
            "average_speed_kmh": round(speed_kmh, 2),
            "heading_degrees": round(heading, 2),
            "predicted_distance_km": round(distance_km, 2)
        }
    
    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        두 지점 간 거리 계산 (Haversine)
        
        Returns:
            거리 (km)
        """
        R = 6371  # 지구 반지름 (km)
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) *
            math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _interpolate_location(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
        ratio: float
    ) -> Tuple[float, float]:
        """
        두 지점 사이의 중간 위치 계산
        
        Args:
            lat1, lon1: 시작점
            lat2, lon2: 끝점
            ratio: 진행률 (0~1)
        
        Returns:
            중간 위치 (latitude, longitude)
        """
        lat = lat1 + (lat2 - lat1) * ratio
        lon = lon1 + (lon2 - lon1) * ratio
        
        return lat, lon
    
    def _calculate_destination(
        self,
        lat: float,
        lon: float,
        heading: float,
        distance_km: float
    ) -> Tuple[float, float]:
        """
        시작점, 방향, 거리로 목적지 계산
        
        Args:
            lat, lon: 시작점
            heading: 방향 (도, 북쪽 기준 시계방향)
            distance_km: 거리 (km)
        
        Returns:
            목적지 (latitude, longitude)
        """
        R = 6371  # 지구 반지름 (km)
        
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        heading_rad = math.radians(heading)
        
        # 새로운 위도
        new_lat_rad = math.asin(
            math.sin(lat_rad) * math.cos(distance_km / R) +
            math.cos(lat_rad) * math.sin(distance_km / R) * math.cos(heading_rad)
        )
        
        # 새로운 경도
        new_lon_rad = lon_rad + math.atan2(
            math.sin(heading_rad) * math.sin(distance_km / R) * math.cos(lat_rad),
            math.cos(distance_km / R) - math.sin(lat_rad) * math.sin(new_lat_rad)
        )
        
        return math.degrees(new_lat_rad), math.degrees(new_lon_rad)
    
    async def predict_multiple_vehicles(
        self,
        vehicle_ids: Optional[List[int]] = None,
        prediction_minutes: int = 30
    ) -> Dict[str, Any]:
        """
        여러 차량의 위치 예측
        
        Args:
            vehicle_ids: 차량 ID 리스트 (None이면 모든 활성 차량)
            prediction_minutes: 예측 시간
        
        Returns:
            차량별 예측 결과
        """
        logger.info(f"🔮 여러 차량 위치 예측 시작 ({prediction_minutes}분 후)")
        
        # 차량 목록
        if vehicle_ids:
            vehicles = self.db.query(Vehicle).filter(
                Vehicle.id.in_(vehicle_ids)
            ).all()
        else:
            # 모든 활성 차량
            vehicles = self.db.query(Vehicle).filter(
                Vehicle.status != 'OUT_OF_SERVICE'
            ).all()
        
        predictions = []
        
        for vehicle in vehicles:
            try:
                prediction = await self.predict_vehicle_location(
                    vehicle.id,
                    prediction_minutes
                )
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"차량 {vehicle.id} 예측 실패: {e}")
                predictions.append({
                    "success": False,
                    "vehicle_id": vehicle.id,
                    "vehicle_code": vehicle.vehicle_code,
                    "error": str(e)
                })
        
        successful = len([p for p in predictions if p.get("success")])
        
        result = {
            "total_vehicles": len(vehicles),
            "successful_predictions": successful,
            "failed_predictions": len(vehicles) - successful,
            "prediction_time_minutes": prediction_minutes,
            "predictions": predictions
        }
        
        logger.info(
            f"✅ 여러 차량 예측 완료: {successful}/{len(vehicles)}대 성공"
        )
        
        return result
    
    async def evaluate_prediction_accuracy(
        self,
        vehicle_id: int,
        test_period_days: int = 7
    ) -> Dict[str, Any]:
        """
        예측 정확도 평가
        
        Args:
            vehicle_id: 차량 ID
            test_period_days: 평가 기간 (일)
        
        Returns:
            정확도 평가 결과
        """
        logger.info(f"📊 차량 {vehicle_id} 예측 정확도 평가 시작")
        
        since = datetime.now(timezone.utc) - timedelta(days=test_period_days)
        
        # 과거 GPS 데이터
        history = self.db.query(VehicleLocation).filter(
            and_(
                VehicleLocation.vehicle_id == vehicle_id,
                VehicleLocation.recorded_at >= since
            )
        ).order_by(VehicleLocation.recorded_at).all()
        
        if len(history) < 20:
            return {
                "success": False,
                "error": "Insufficient history for evaluation",
                "vehicle_id": vehicle_id
            }
        
        # 샘플링: 매 10번째 포인트를 실제값으로, 이전 포인트로 예측
        errors = []
        
        for i in range(10, len(history), 10):
            actual = history[i]
            previous = history[i - 1]
            
            # 30분 후 예측 (실제 시간 차이 사용)
            time_diff_minutes = (
                actual.recorded_at - previous.recorded_at
            ).total_seconds() / 60
            
            if time_diff_minutes > 60:  # 1시간 이상 차이나면 스킵
                continue
            
            # 예측 (간단한 선형 예측)
            if previous.speed and previous.heading:
                distance_km = (previous.speed * time_diff_minutes) / 60
                pred_lat, pred_lon = self._calculate_destination(
                    previous.latitude,
                    previous.longitude,
                    previous.heading,
                    distance_km
                )
                
                # 오차 계산
                error_km = self._calculate_distance(
                    pred_lat, pred_lon,
                    actual.latitude, actual.longitude
                )
                errors.append(error_km)
        
        if not errors:
            return {
                "success": False,
                "error": "No valid prediction samples",
                "vehicle_id": vehicle_id
            }
        
        # 통계
        avg_error = statistics.mean(errors)
        median_error = statistics.median(errors)
        max_error = max(errors)
        
        # 정확도 평가 (오차 1km 이내면 우수)
        good_predictions = len([e for e in errors if e <= 1.0])
        accuracy_percentage = (good_predictions / len(errors)) * 100
        
        result = {
            "success": True,
            "vehicle_id": vehicle_id,
            "test_period_days": test_period_days,
            "total_samples": len(errors),
            "average_error_km": round(avg_error, 2),
            "median_error_km": round(median_error, 2),
            "max_error_km": round(max_error, 2),
            "accuracy_percentage": round(accuracy_percentage, 2),
            "good_predictions": good_predictions,
            "evaluation": (
                "Excellent" if accuracy_percentage >= 80 else
                "Good" if accuracy_percentage >= 60 else
                "Fair" if accuracy_percentage >= 40 else
                "Poor"
            )
        }
        
        logger.info(
            f"✅ 예측 정확도: {accuracy_percentage:.1f}% "
            f"(평균 오차 {avg_error:.2f}km)"
        )
        
        return result
