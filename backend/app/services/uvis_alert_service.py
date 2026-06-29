"""
UVIS Alert Service
UVIS GPS 데이터 기반 알림 시스템

Features:
- 이상 속도 감지 (과속, 비정상 속도)
- 엔진 ON/OFF 상태 변화 감지
- 온도 이상 감지 (냉동/냉장 온도 범위 벗어남)
- 장시간 정차 감지
- GPS 신호 끊김 감지
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from loguru import logger

from app.models.vehicle import Vehicle
from app.models.uvis_gps import VehicleGPSLog, VehicleTemperatureLog


class UVISAlertService:
    """UVIS 알림 서비스"""
    
    # 알림 임계값 설정
    SPEED_THRESHOLDS = {
        "abnormal_high": 150,  # 비정상 고속 (150 km/h 초과)
        "warning_high": 120,   # 과속 경고 (120 km/h 초과)
        "abnormal_zero": 255,  # 센서 오류 (255는 보통 오류값)
    }
    
    TEMPERATURE_THRESHOLDS = {
        "frozen": {"min": -25, "max": -10},      # 냉동 정상 범위
        "refrigerated": {"min": -2, "max": 8},   # 냉장 정상 범위
        "warning_high": 15,   # 고온 경고
        "critical_high": 20,  # 고온 위험
    }
    
    ENGINE_OFF_THRESHOLD = timedelta(hours=3)  # 3시간 이상 엔진 OFF 경고
    GPS_SIGNAL_THRESHOLD = timedelta(minutes=30)  # 30분 이상 GPS 신호 없음
    
    @classmethod
    def check_speed_alerts(
        cls,
        gps_log: VehicleGPSLog,
        vehicle: Vehicle
    ) -> List[Dict[str, Any]]:
        """
        속도 이상 감지
        
        Returns:
            List of alert dictionaries
        """
        alerts = []
        speed = gps_log.speed_kmh
        
        # 비정상 속도 (센서 오류)
        if speed >= cls.SPEED_THRESHOLDS["abnormal_zero"]:
            alerts.append({
                "type": "speed_abnormal",
                "level": "error",
                "title": f"⚠️ 속도 센서 이상 - {vehicle.plate_number}",
                "message": f"비정상적인 속도 값이 감지되었습니다 (속도: {speed} km/h). 센서를 확인해주세요.",
                "vehicle_id": vehicle.id,
                "vehicle_plate": vehicle.plate_number,
                "data": {
                    "speed": speed,
                    "gps_datetime": gps_log.bi_date + gps_log.bi_time,
                    "latitude": gps_log.latitude,
                    "longitude": gps_log.longitude,
                }
            })
        
        # 과속 경고
        elif speed > cls.SPEED_THRESHOLDS["warning_high"]:
            alerts.append({
                "type": "speed_warning",
                "level": "warning",
                "title": f"🚨 과속 감지 - {vehicle.plate_number}",
                "message": f"차량이 {speed} km/h로 주행 중입니다. 안전 운행에 주의해주세요.",
                "vehicle_id": vehicle.id,
                "vehicle_plate": vehicle.plate_number,
                "data": {
                    "speed": speed,
                    "gps_datetime": gps_log.bi_date + gps_log.bi_time,
                    "latitude": gps_log.latitude,
                    "longitude": gps_log.longitude,
                }
            })
        
        # 고속 주행
        elif speed > cls.SPEED_THRESHOLDS["abnormal_high"]:
            alerts.append({
                "type": "speed_high",
                "level": "error",
                "title": f"🚨 위험 속도 감지 - {vehicle.plate_number}",
                "message": f"차량이 위험 속도({speed} km/h)로 주행 중입니다! 즉시 감속이 필요합니다.",
                "vehicle_id": vehicle.id,
                "vehicle_plate": vehicle.plate_number,
                "data": {
                    "speed": speed,
                    "gps_datetime": gps_log.bi_date + gps_log.bi_time,
                    "latitude": gps_log.latitude,
                    "longitude": gps_log.longitude,
                }
            })
        
        return alerts
    
    @classmethod
    def check_engine_status_change(
        cls,
        current_gps: VehicleGPSLog,
        previous_gps: Optional[VehicleGPSLog],
        vehicle: Vehicle
    ) -> List[Dict[str, Any]]:
        """
        엔진 상태 변화 감지
        
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        if not previous_gps:
            return alerts
        
        # 엔진 OFF → ON
        if not previous_gps.is_engine_on and current_gps.is_engine_on:
            alerts.append({
                "type": "engine_on",
                "level": "info",
                "title": f"🚗 엔진 시동 - {vehicle.plate_number}",
                "message": f"차량 엔진이 켜졌습니다. 운행을 시작합니다.",
                "vehicle_id": vehicle.id,
                "vehicle_plate": vehicle.plate_number,
                "data": {
                    "gps_datetime": current_gps.bi_date + current_gps.bi_time,
                    "latitude": current_gps.latitude,
                    "longitude": current_gps.longitude,
                }
            })
        
        # 엔진 ON → OFF
        elif previous_gps.is_engine_on and not current_gps.is_engine_on:
            alerts.append({
                "type": "engine_off",
                "level": "info",
                "title": f"⏹️ 엔진 정지 - {vehicle.plate_number}",
                "message": f"차량 엔진이 꺼졌습니다. 정차 중입니다.",
                "vehicle_id": vehicle.id,
                "vehicle_plate": vehicle.plate_number,
                "data": {
                    "gps_datetime": current_gps.bi_date + current_gps.bi_time,
                    "latitude": current_gps.latitude,
                    "longitude": current_gps.longitude,
                }
            })
        
        return alerts
    
    @classmethod
    def check_long_engine_off(
        cls,
        db: Session,
        vehicle: Vehicle,
        threshold_hours: int = 3
    ) -> List[Dict[str, Any]]:
        """
        장시간 엔진 OFF 감지
        
        Args:
            db: Database session
            vehicle: Vehicle instance
            threshold_hours: 임계값 (시간)
        
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        # 최근 GPS 로그 조회
        latest_gps = db.query(VehicleGPSLog).filter(
            VehicleGPSLog.tid_id == vehicle.uvis_device_id
        ).order_by(VehicleGPSLog.created_at.desc()).first()
        
        if not latest_gps:
            return alerts
        
        # 엔진이 꺼져있고, 마지막 업데이트가 임계값 이상이면
        if not latest_gps.is_engine_on:
            time_diff = datetime.now() - latest_gps.created_at
            
            if time_diff > timedelta(hours=threshold_hours):
                alerts.append({
                    "type": "engine_off_long",
                    "level": "warning",
                    "title": f"⚠️ 장시간 정차 - {vehicle.plate_number}",
                    "message": f"차량이 {time_diff.total_seconds() / 3600:.1f}시간 동안 정차 중입니다.",
                    "vehicle_id": vehicle.id,
                    "vehicle_plate": vehicle.plate_number,
                    "data": {
                        "off_duration_hours": time_diff.total_seconds() / 3600,
                        "last_gps_datetime": latest_gps.bi_date + latest_gps.bi_time,
                        "latitude": latest_gps.latitude,
                        "longitude": latest_gps.longitude,
                    }
                })
        
        return alerts
    
    @classmethod
    def check_temperature_alerts(
        cls,
        temp_log: VehicleTemperatureLog,
        vehicle: Vehicle
    ) -> List[Dict[str, Any]]:
        """
        온도 이상 감지
        
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        # 온도 A 체크
        if temp_log.temperature_a is not None:
            alerts.extend(cls._check_single_temperature(
                temperature=temp_log.temperature_a,
                sensor="A",
                vehicle=vehicle,
                temp_log=temp_log
            ))
        
        # 온도 B 체크
        if temp_log.temperature_b is not None:
            alerts.extend(cls._check_single_temperature(
                temperature=temp_log.temperature_b,
                sensor="B",
                vehicle=vehicle,
                temp_log=temp_log
            ))
        
        return alerts
    
    @classmethod
    def _check_single_temperature(
        cls,
        temperature: float,
        sensor: str,
        vehicle: Vehicle,
        temp_log: VehicleTemperatureLog
    ) -> List[Dict[str, Any]]:
        """개별 온도 센서 체크"""
        alerts = []
        
        # 차량 설정 온도 범위 확인
        min_temp = vehicle.min_temp_celsius
        max_temp = vehicle.max_temp_celsius
        
        # 차량 설정 온도와 비교
        if min_temp is not None and max_temp is not None:
            # 설정 범위 벗어남
            if temperature < min_temp:
                alerts.append({
                    "type": f"temperature_low_{sensor}",
                    "level": "warning",
                    "title": f"🥶 저온 경고 - {vehicle.plate_number} (센서 {sensor})",
                    "message": f"온도가 설정 범위보다 낮습니다 (현재: {temperature}°C, 최소: {min_temp}°C)",
                    "vehicle_id": vehicle.id,
                    "vehicle_plate": vehicle.plate_number,
                    "data": {
                        "temperature": temperature,
                        "sensor": sensor,
                        "min_temp": min_temp,
                        "max_temp": max_temp,
                        "datetime": temp_log.tpl_date + temp_log.tpl_time,
                    }
                })
            
            elif temperature > max_temp:
                # 고온 위험
                if temperature > cls.TEMPERATURE_THRESHOLDS["critical_high"]:
                    level = "error"
                    emoji = "🔥"
                    severity = "위험"
                # 고온 경고
                elif temperature > cls.TEMPERATURE_THRESHOLDS["warning_high"]:
                    level = "warning"
                    emoji = "🌡️"
                    severity = "경고"
                else:
                    level = "warning"
                    emoji = "⚠️"
                    severity = "주의"
                
                alerts.append({
                    "type": f"temperature_high_{sensor}",
                    "level": level,
                    "title": f"{emoji} 고온 {severity} - {vehicle.plate_number} (센서 {sensor})",
                    "message": f"온도가 설정 범위보다 높습니다 (현재: {temperature}°C, 최대: {max_temp}°C)",
                    "vehicle_id": vehicle.id,
                    "vehicle_plate": vehicle.plate_number,
                    "data": {
                        "temperature": temperature,
                        "sensor": sensor,
                        "min_temp": min_temp,
                        "max_temp": max_temp,
                        "datetime": temp_log.tpl_date + temp_log.tpl_time,
                    }
                })
        
        # 일반 냉동/냉장 범위 체크 (차량 설정이 없을 경우)
        else:
            # 냉동 차량인 경우
            if vehicle.vehicle_type == "FROZEN":
                frozen_range = cls.TEMPERATURE_THRESHOLDS["frozen"]
                if temperature < frozen_range["min"] or temperature > frozen_range["max"]:
                    alerts.append({
                        "type": f"temperature_frozen_{sensor}",
                        "level": "warning",
                        "title": f"❄️ 냉동 온도 이탈 - {vehicle.plate_number} (센서 {sensor})",
                        "message": f"냉동 온도 범위를 벗어났습니다 (현재: {temperature}°C, 권장: {frozen_range['min']}°C ~ {frozen_range['max']}°C)",
                        "vehicle_id": vehicle.id,
                        "vehicle_plate": vehicle.plate_number,
                        "data": {
                            "temperature": temperature,
                            "sensor": sensor,
                            "recommended_min": frozen_range["min"],
                            "recommended_max": frozen_range["max"],
                            "datetime": temp_log.tpl_date + temp_log.tpl_time,
                        }
                    })
            
            # 냉장 차량인 경우
            elif vehicle.vehicle_type == "REFRIGERATED":
                ref_range = cls.TEMPERATURE_THRESHOLDS["refrigerated"]
                if temperature < ref_range["min"] or temperature > ref_range["max"]:
                    alerts.append({
                        "type": f"temperature_refrigerated_{sensor}",
                        "level": "warning",
                        "title": f"🧊 냉장 온도 이탈 - {vehicle.plate_number} (센서 {sensor})",
                        "message": f"냉장 온도 범위를 벗어났습니다 (현재: {temperature}°C, 권장: {ref_range['min']}°C ~ {ref_range['max']}°C)",
                        "vehicle_id": vehicle.id,
                        "vehicle_plate": vehicle.plate_number,
                        "data": {
                            "temperature": temperature,
                            "sensor": sensor,
                            "recommended_min": ref_range["min"],
                            "recommended_max": ref_range["max"],
                            "datetime": temp_log.tpl_date + temp_log.tpl_time,
                        }
                    })
        
        return alerts
    
    @classmethod
    def check_gps_signal_loss(
        cls,
        db: Session,
        vehicle: Vehicle
    ) -> List[Dict[str, Any]]:
        """
        GPS 신호 끊김 감지
        
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        # 최근 GPS 로그 조회
        latest_gps = db.query(VehicleGPSLog).filter(
            VehicleGPSLog.tid_id == vehicle.uvis_device_id
        ).order_by(VehicleGPSLog.created_at.desc()).first()
        
        if not latest_gps:
            # GPS 데이터가 전혀 없음
            alerts.append({
                "type": "gps_no_data",
                "level": "error",
                "title": f"📡 GPS 데이터 없음 - {vehicle.plate_number}",
                "message": f"차량의 GPS 데이터가 수집되지 않고 있습니다. UVIS 장치를 확인해주세요.",
                "vehicle_id": vehicle.id,
                "vehicle_plate": vehicle.plate_number,
                "data": {}
            })
        else:
            # 마지막 업데이트 시간 체크
            time_since_update = datetime.now() - latest_gps.created_at
            
            if time_since_update > cls.GPS_SIGNAL_THRESHOLD:
                alerts.append({
                    "type": "gps_signal_lost",
                    "level": "warning",
                    "title": f"📡 GPS 신호 끊김 - {vehicle.plate_number}",
                    "message": f"GPS 신호가 {time_since_update.total_seconds() / 60:.0f}분 동안 수신되지 않았습니다.",
                    "vehicle_id": vehicle.id,
                    "vehicle_plate": vehicle.plate_number,
                    "data": {
                        "minutes_since_update": time_since_update.total_seconds() / 60,
                        "last_gps_datetime": latest_gps.bi_date + latest_gps.bi_time,
                        "last_latitude": latest_gps.latitude,
                        "last_longitude": latest_gps.longitude,
                    }
                })
        
        return alerts
    
    @classmethod
    def process_all_alerts(
        cls,
        db: Session,
        gps_log: Optional[VehicleGPSLog] = None,
        temp_log: Optional[VehicleTemperatureLog] = None,
        vehicle: Optional[Vehicle] = None
    ) -> List[Dict[str, Any]]:
        """
        모든 알림 체크 통합 처리
        
        Args:
            db: Database session
            gps_log: GPS 로그 (옵션)
            temp_log: 온도 로그 (옵션)
            vehicle: 차량 정보 (옵션)
        
        Returns:
            List of all alerts
        """
        all_alerts = []
        
        try:
            # GPS 로그 기반 알림
            if gps_log and vehicle:
                # 속도 알림
                speed_alerts = cls.check_speed_alerts(gps_log, vehicle)
                all_alerts.extend(speed_alerts)
                
                # 엔진 상태 변화 알림
                # gps_log.id가 None이면(flush 전) created_at 기준으로 이전 로그 조회
                if gps_log.id is not None:
                    previous_gps = db.query(VehicleGPSLog).filter(
                        VehicleGPSLog.tid_id == vehicle.uvis_device_id,
                        VehicleGPSLog.id < gps_log.id
                    ).order_by(VehicleGPSLog.created_at.desc()).first()
                else:
                    previous_gps = db.query(VehicleGPSLog).filter(
                        VehicleGPSLog.tid_id == vehicle.uvis_device_id
                    ).order_by(VehicleGPSLog.created_at.desc()).first()
                
                engine_alerts = cls.check_engine_status_change(
                    gps_log, previous_gps, vehicle
                )
                all_alerts.extend(engine_alerts)
            
            # 온도 로그 기반 알림
            if temp_log and vehicle:
                temp_alerts = cls.check_temperature_alerts(temp_log, vehicle)
                all_alerts.extend(temp_alerts)
            
            # 로그 출력
            if all_alerts:
                logger.info(f"🚨 총 {len(all_alerts)}개 알림 발생 - {vehicle.plate_number if vehicle else 'Unknown'}")
                for alert in all_alerts:
                    logger.info(f"   - [{alert['level'].upper()}] {alert['title']}")
            
        except Exception as e:
            logger.error(f"❌ 알림 처리 중 오류: {e}")
        
        return all_alerts
