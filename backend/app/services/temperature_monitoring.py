"""
Temperature Monitoring Service
자동 온도 기록 수집 및 모니터링 서비스
Phase 3-A Part 4: 온도 기록 자동 수집
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
import logging

from app.models.uvis_gps import VehicleTemperatureLog
from app.models.vehicle_location import VehicleLocation, TemperatureAlert
from app.models.vehicle import Vehicle
from app.models.dispatch import Dispatch
from app.services.uvis_gps_service import UvisGPSService
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class TemperatureThreshold:
    """온도 임계값 설정"""
    # 냉동 (-25°C ~ -15°C)
    FROZEN_MIN = -25.0
    FROZEN_MAX = -15.0
    FROZEN_WARNING_MIN = -22.0  # Warning: -22°C 이상
    FROZEN_WARNING_MAX = -18.0  # Warning: -18°C 이하
    
    # 냉장 (0°C ~ 5°C)
    CHILLED_MIN = 0.0
    CHILLED_MAX = 5.0
    CHILLED_WARNING_MIN = 2.0   # Warning: 2°C 미만
    CHILLED_WARNING_MAX = 7.0   # Warning: 7°C 초과
    
    # 상온 (10°C ~ 25°C)
    AMBIENT_MIN = 10.0
    AMBIENT_MAX = 25.0


class TemperatureMonitoringService:
    """온도 모니터링 자동 수집 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.uvis_service = UvisGPSService(db)
        self.notification_service = NotificationService(db)
    
    async def collect_all_temperatures(self) -> Dict[str, Any]:
        """
        모든 차량의 온도 데이터 자동 수집
        
        Returns:
            수집 통계 및 알림 정보
        """
        logger.info("🌡️ 온도 데이터 자동 수집 시작")
        
        try:
            # 1. UVIS API에서 온도 데이터 가져오기
            temperature_data_list = await self.uvis_service.get_vehicle_temperature_data()
            
            if not temperature_data_list:
                logger.warning("⚠️ 수집된 온도 데이터가 없습니다")
                return {
                    "success": False,
                    "collected_count": 0,
                    "alerts_created": 0,
                    "message": "No temperature data collected"
                }
            
            collected_count = 0
            alerts_created = 0
            critical_alerts = []
            
            # 2. 각 온도 데이터 처리
            for temp_data in temperature_data_list:
                try:
                    # 차량 매칭
                    vehicle = self._match_vehicle(temp_data)
                    
                    if vehicle:
                        # 온도 로그 저장
                        temp_log = self._save_temperature_log(temp_data, vehicle)
                        collected_count += 1
                        
                        # 온도 임계값 체크 및 알림 생성
                        alerts = await self._check_temperature_thresholds(temp_log, vehicle)
                        alerts_created += len(alerts)
                        
                        # Critical 알림 수집
                        for alert in alerts:
                            if alert.severity == "CRITICAL":
                                critical_alerts.append({
                                    "vehicle_id": vehicle.id,
                                    "vehicle_number": vehicle.plate_number,
                                    "alert_type": alert.alert_type,
                                    "temperature": alert.temperature_celsius,
                                    "detected_at": alert.detected_at
                                })
                    
                except Exception as e:
                    logger.error(f"❌ 온도 데이터 처리 실패: {e}")
                    continue
            
            # 3. 결과 반환
            result = {
                "success": True,
                "collected_count": collected_count,
                "alerts_created": alerts_created,
                "critical_alerts": len(critical_alerts),
                "critical_alert_details": critical_alerts,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ 온도 수집 완료: {collected_count}건, 알림: {alerts_created}건")
            return result
            
        except Exception as e:
            logger.error(f"❌ 온도 수집 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _match_vehicle(self, temp_data: Dict[str, Any]) -> Optional[Vehicle]:
        """
        온도 데이터를 차량과 매칭
        
        Args:
            temp_data: UVIS 온도 데이터
            
        Returns:
            매칭된 Vehicle 객체 또는 None
        """
        vehicle_number = temp_data.get("cm_number")
        tid_id = temp_data.get("tid_id")
        
        if vehicle_number:
            # 차량번호로 매칭
            vehicle = self.db.query(Vehicle).filter(
                Vehicle.plate_number == vehicle_number
            ).first()
            if vehicle:
                return vehicle
        
        if tid_id:
            # TID로 매칭 (UVIS 디바이스 ID와 연결)
            vehicle = self.db.query(Vehicle).filter(
                Vehicle.uvis_device_id == tid_id
            ).first()
            if vehicle:
                return vehicle
        
        return None
    
    def _save_temperature_log(
        self, 
        temp_data: Dict[str, Any], 
        vehicle: Vehicle
    ) -> VehicleTemperatureLog:
        """
        온도 로그 저장
        
        Args:
            temp_data: UVIS 온도 데이터
            vehicle: 차량 객체
            
        Returns:
            저장된 VehicleTemperatureLog
        """
        temp_log = VehicleTemperatureLog(
            vehicle_id=vehicle.id,
            off_key=temp_data.get("off_key"),
            tid_id=temp_data.get("tid_id"),
            tpl_date=temp_data.get("tpl_date"),
            tpl_time=temp_data.get("tpl_time"),
            cm_number=temp_data.get("cm_number"),
            tpl_x_position=temp_data.get("tpl_x_position"),
            tpl_y_position=temp_data.get("tpl_y_position"),
            tpl_signal_a=temp_data.get("tpl_signal_a"),
            tpl_degree_a=temp_data.get("tpl_degree_a"),
            temperature_a=temp_data.get("temperature_a"),
            tpl_signal_b=temp_data.get("tpl_signal_b"),
            tpl_degree_b=temp_data.get("tpl_degree_b"),
            temperature_b=temp_data.get("temperature_b"),
            latitude=temp_data.get("latitude"),
            longitude=temp_data.get("longitude")
        )
        
        self.db.add(temp_log)
        self.db.commit()
        self.db.refresh(temp_log)
        
        return temp_log
    
    async def _check_temperature_thresholds(
        self, 
        temp_log: VehicleTemperatureLog, 
        vehicle: Vehicle
    ) -> List[TemperatureAlert]:
        """
        온도 임계값 체크 및 알림 생성
        
        Args:
            temp_log: 온도 로그
            vehicle: 차량 객체
            
        Returns:
            생성된 알림 리스트
        """
        alerts = []
        
        # 현재 진행 중인 배차 찾기
        active_dispatch = self.db.query(Dispatch).filter(
            Dispatch.vehicle_id == vehicle.id,
            Dispatch.status.in_(["ASSIGNED", "IN_PROGRESS"])
        ).first()
        
        # Temperature A 체크
        if temp_log.temperature_a is not None:
            alert = await self._check_single_temperature(
                vehicle=vehicle,
                dispatch=active_dispatch,
                temperature=temp_log.temperature_a,
                sensor_name="A",
                temp_log=temp_log
            )
            if alert:
                alerts.append(alert)
        
        # Temperature B 체크
        if temp_log.temperature_b is not None:
            alert = await self._check_single_temperature(
                vehicle=vehicle,
                dispatch=active_dispatch,
                temperature=temp_log.temperature_b,
                sensor_name="B",
                temp_log=temp_log
            )
            if alert:
                alerts.append(alert)
        
        return alerts
    
    async def _check_single_temperature(
        self,
        vehicle: Vehicle,
        dispatch: Optional[Dispatch],
        temperature: float,
        sensor_name: str,
        temp_log: VehicleTemperatureLog
    ) -> Optional[TemperatureAlert]:
        """
        단일 온도 센서 임계값 체크
        
        Args:
            vehicle: 차량
            dispatch: 배차 (optional)
            temperature: 온도 값
            sensor_name: 센서 이름 (A 또는 B)
            temp_log: 온도 로그
            
        Returns:
            생성된 알림 또는 None
        """
        alert_type = None
        severity = None
        threshold_min = None
        threshold_max = None
        
        # 차량 타입에 따른 임계값 설정
        vehicle_type = vehicle.vehicle_type if vehicle else "냉동"
        
        if vehicle_type == "냉동":
            threshold_min = TemperatureThreshold.FROZEN_MIN
            threshold_max = TemperatureThreshold.FROZEN_MAX
            
            if temperature < TemperatureThreshold.FROZEN_MIN:
                alert_type = "TOO_COLD"
                severity = "CRITICAL"
            elif temperature > TemperatureThreshold.FROZEN_MAX:
                alert_type = "TOO_HOT"
                severity = "CRITICAL"
            elif temperature > TemperatureThreshold.FROZEN_WARNING_MAX:
                alert_type = "TOO_HOT"
                severity = "WARNING"
            elif temperature < TemperatureThreshold.FROZEN_WARNING_MIN:
                alert_type = "TOO_COLD"
                severity = "WARNING"
                
        elif vehicle_type == "냉장":
            threshold_min = TemperatureThreshold.CHILLED_MIN
            threshold_max = TemperatureThreshold.CHILLED_MAX
            
            if temperature < TemperatureThreshold.CHILLED_MIN:
                alert_type = "TOO_COLD"
                severity = "CRITICAL"
            elif temperature > TemperatureThreshold.CHILLED_MAX:
                alert_type = "TOO_HOT"
                severity = "CRITICAL"
            elif temperature < TemperatureThreshold.CHILLED_WARNING_MIN:
                alert_type = "TOO_COLD"
                severity = "WARNING"
            elif temperature > TemperatureThreshold.CHILLED_WARNING_MAX:
                alert_type = "TOO_HOT"
                severity = "WARNING"
        
        # 알림 생성 필요 없으면 None 반환
        if not alert_type:
            return None
        
        # 중복 알림 체크 (최근 30분 내 동일 알림)
        recent_alert = self.db.query(TemperatureAlert).filter(
            TemperatureAlert.vehicle_id == vehicle.id,
            TemperatureAlert.alert_type == alert_type,
            TemperatureAlert.is_resolved == False,
            TemperatureAlert.detected_at > datetime.utcnow() - timedelta(minutes=30)
        ).first()
        
        if recent_alert:
            # 이미 알림이 있으면 새로 생성하지 않음
            return None
        
        # 새 알림 생성
        message = self._generate_alert_message(
            vehicle=vehicle,
            temperature=temperature,
            sensor_name=sensor_name,
            alert_type=alert_type,
            severity=severity
        )
        
        alert = TemperatureAlert(
            vehicle_id=vehicle.id,
            dispatch_id=dispatch.id if dispatch else None,
            location_id=None,
            alert_type=alert_type,
            severity=severity,
            temperature_celsius=temperature,
            threshold_min=threshold_min,
            threshold_max=threshold_max,
            detected_at=datetime.utcnow(),
            is_resolved=False,
            notification_sent=False,
            message=message
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        # Critical 알림인 경우 즉시 전송
        if severity == "CRITICAL":
            await self._send_temperature_alert_notification(alert, vehicle, dispatch)
        
        return alert
    
    def _generate_alert_message(
        self,
        vehicle: Vehicle,
        temperature: float,
        sensor_name: str,
        alert_type: str,
        severity: str
    ) -> str:
        """알림 메시지 생성"""
        severity_emoji = "🚨" if severity == "CRITICAL" else "⚠️"
        
        if alert_type == "TOO_HOT":
            message = f"{severity_emoji} 온도 과열 경고! 차량 {vehicle.plate_number} 센서 {sensor_name}: {temperature:.1f}°C (과열)"
        elif alert_type == "TOO_COLD":
            message = f"{severity_emoji} 온도 과냉 경고! 차량 {vehicle.plate_number} 센서 {sensor_name}: {temperature:.1f}°C (과냉)"
        else:
            message = f"{severity_emoji} 온도 이상 감지! 차량 {vehicle.plate_number} 센서 {sensor_name}: {temperature:.1f}°C"
        
        return message
    
    async def _send_temperature_alert_notification(
        self,
        alert: TemperatureAlert,
        vehicle: Vehicle,
        dispatch: Optional[Dispatch]
    ):
        """온도 알림 전송"""
        try:
            # 알림 수신자 결정
            recipients = []
            
            # 차량 담당 기사
            if vehicle.driver and vehicle.driver.phone:
                recipients.append({
                    "phone": vehicle.driver.phone,
                    "name": vehicle.driver.name
                })
            
            # 배차 담당자 (있는 경우)
            if dispatch and dispatch.order:
                # 주문 담당자 등 추가 가능
                pass
            
            # SMS 알림 전송
            for recipient in recipients:
                await self.notification_service.send_notification(
                    notification_type="TEMPERATURE_ALERT",
                    channel="SMS",
                    recipient_phone=recipient["phone"],
                    title=f"온도 이상 알림 - {vehicle.plate_number}",
                    message=alert.message,
                    metadata={
                        "vehicle_id": vehicle.id,
                        "alert_id": alert.id,
                        "temperature": alert.temperature_celsius,
                        "severity": alert.severity
                    }
                )
            
            # 알림 전송 상태 업데이트
            alert.notification_sent = True
            alert.notification_channels = "sms"
            self.db.commit()
            
        except Exception as e:
            logger.error(f"❌ 온도 알림 전송 실패: {e}")
    
    def get_vehicle_temperature_history(
        self,
        vehicle_id: int,
        hours: int = 24,
        sensor: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        차량 온도 이력 조회
        
        Args:
            vehicle_id: 차량 ID
            hours: 조회 기간 (시간)
            sensor: 센서 선택 ("A", "B", 또는 None for both)
            
        Returns:
            온도 이력 데이터 리스트
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = self.db.query(VehicleTemperatureLog).filter(
            VehicleTemperatureLog.vehicle_id == vehicle_id,
            VehicleTemperatureLog.created_at >= start_time
        ).order_by(VehicleTemperatureLog.created_at)
        
        logs = query.all()
        
        history = []
        for log in logs:
            if sensor == "A" and log.temperature_a is not None:
                history.append({
                    "timestamp": log.created_at.isoformat(),
                    "sensor": "A",
                    "temperature": log.temperature_a,
                    "latitude": log.latitude,
                    "longitude": log.longitude
                })
            elif sensor == "B" and log.temperature_b is not None:
                history.append({
                    "timestamp": log.created_at.isoformat(),
                    "sensor": "B",
                    "temperature": log.temperature_b,
                    "latitude": log.latitude,
                    "longitude": log.longitude
                })
            elif sensor is None:
                if log.temperature_a is not None:
                    history.append({
                        "timestamp": log.created_at.isoformat(),
                        "sensor": "A",
                        "temperature": log.temperature_a,
                        "latitude": log.latitude,
                        "longitude": log.longitude
                    })
                if log.temperature_b is not None:
                    history.append({
                        "timestamp": log.created_at.isoformat(),
                        "sensor": "B",
                        "temperature": log.temperature_b,
                        "latitude": log.latitude,
                        "longitude": log.longitude
                    })
        
        return history
    
    def get_temperature_statistics(
        self,
        vehicle_id: int,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        차량 온도 통계
        
        Args:
            vehicle_id: 차량 ID
            hours: 통계 기간 (시간)
            
        Returns:
            온도 통계 데이터
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Sensor A 통계
        stats_a = self.db.query(
            func.min(VehicleTemperatureLog.temperature_a).label("min_temp"),
            func.max(VehicleTemperatureLog.temperature_a).label("max_temp"),
            func.avg(VehicleTemperatureLog.temperature_a).label("avg_temp"),
            func.count(VehicleTemperatureLog.id).label("sample_count")
        ).filter(
            VehicleTemperatureLog.vehicle_id == vehicle_id,
            VehicleTemperatureLog.created_at >= start_time,
            VehicleTemperatureLog.temperature_a.isnot(None)
        ).first()
        
        # Sensor B 통계
        stats_b = self.db.query(
            func.min(VehicleTemperatureLog.temperature_b).label("min_temp"),
            func.max(VehicleTemperatureLog.temperature_b).label("max_temp"),
            func.avg(VehicleTemperatureLog.temperature_b).label("avg_temp"),
            func.count(VehicleTemperatureLog.id).label("sample_count")
        ).filter(
            VehicleTemperatureLog.vehicle_id == vehicle_id,
            VehicleTemperatureLog.created_at >= start_time,
            VehicleTemperatureLog.temperature_b.isnot(None)
        ).first()
        
        # 알림 통계
        alert_count = self.db.query(func.count(TemperatureAlert.id)).filter(
            TemperatureAlert.vehicle_id == vehicle_id,
            TemperatureAlert.detected_at >= start_time
        ).scalar()
        
        critical_count = self.db.query(func.count(TemperatureAlert.id)).filter(
            TemperatureAlert.vehicle_id == vehicle_id,
            TemperatureAlert.detected_at >= start_time,
            TemperatureAlert.severity == "CRITICAL"
        ).scalar()
        
        return {
            "vehicle_id": vehicle_id,
            "period_hours": hours,
            "sensor_a": {
                "min_temperature": float(stats_a.min_temp) if stats_a.min_temp else None,
                "max_temperature": float(stats_a.max_temp) if stats_a.max_temp else None,
                "avg_temperature": float(stats_a.avg_temp) if stats_a.avg_temp else None,
                "sample_count": stats_a.sample_count
            },
            "sensor_b": {
                "min_temperature": float(stats_b.min_temp) if stats_b.min_temp else None,
                "max_temperature": float(stats_b.max_temp) if stats_b.max_temp else None,
                "avg_temperature": float(stats_b.avg_temp) if stats_b.avg_temp else None,
                "sample_count": stats_b.sample_count
            },
            "alerts": {
                "total_count": alert_count,
                "critical_count": critical_count
            }
        }
    
    def get_active_temperature_alerts(
        self,
        vehicle_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        활성 온도 알림 조회
        
        Args:
            vehicle_id: 차량 ID (optional, None이면 전체 조회)
            
        Returns:
            활성 알림 리스트
        """
        query = self.db.query(TemperatureAlert).filter(
            TemperatureAlert.is_resolved == False
        )
        
        if vehicle_id:
            query = query.filter(TemperatureAlert.vehicle_id == vehicle_id)
        
        alerts = query.order_by(desc(TemperatureAlert.detected_at)).all()
        
        result = []
        for alert in alerts:
            vehicle = alert.vehicle
            result.append({
                "id": alert.id,
                "vehicle_id": alert.vehicle_id,
                "vehicle_number": vehicle.plate_number if vehicle else None,
                "dispatch_id": alert.dispatch_id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "temperature": alert.temperature_celsius,
                "threshold_min": alert.threshold_min,
                "threshold_max": alert.threshold_max,
                "detected_at": alert.detected_at.isoformat(),
                "message": alert.message,
                "notification_sent": alert.notification_sent
            })
        
        return result
    
    async def resolve_temperature_alert(
        self,
        alert_id: int,
        notes: Optional[str] = None
    ) -> bool:
        """
        온도 알림 해결 처리
        
        Args:
            alert_id: 알림 ID
            notes: 해결 메모
            
        Returns:
            성공 여부
        """
        alert = self.db.query(TemperatureAlert).filter(
            TemperatureAlert.id == alert_id
        ).first()
        
        if not alert:
            return False
        
        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        if notes:
            alert.notes = notes
        
        self.db.commit()
        
        return True
