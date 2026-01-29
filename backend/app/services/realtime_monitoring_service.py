"""
실시간 모니터링 서비스
- UVIS GPS/온도 데이터 실시간 수집
- 온도 이탈 자동 감지 및 알림
- WebSocket을 통한 실시간 업데이트
- 대시보드 통합
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from loguru import logger
import asyncio

from app.models.vehicle import Vehicle
from app.models.dispatch import Dispatch
from app.services.uvis_service import get_uvis_service
from app.services.uvis_gps_service import UvisGPSService
from app.services.email_service import EmailService


class RealtimeMonitoringService:
    """실시간 모니터링 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.uvis_service = get_uvis_service()
        self.uvis_gps_service = UvisGPSService(db)
        self.email_service = EmailService()
        
        # 알림 임계값 설정
        self.temperature_thresholds = {
            '냉동': {'min': -25.0, 'max': -18.0, 'critical_min': -30.0, 'critical_max': -15.0},
            '냉장': {'min': 0.0, 'max': 6.0, 'critical_min': -5.0, 'critical_max': 10.0},
            '상온': {'min': 10.0, 'max': 30.0, 'critical_min': 5.0, 'critical_max': 35.0}
        }
        
        # WebSocket 연결 관리
        self.websocket_connections = []
    
    async def monitor_all_vehicles(self) -> Dict[str, Any]:
        """
        모든 차량 실시간 모니터링
        
        Returns:
            {
                'total_vehicles': int,
                'monitored': int,
                'alerts': List[Dict],
                'summary': Dict
            }
        """
        logger.info("Starting real-time monitoring for all vehicles")
        
        # 활성 차량 조회
        active_vehicles = self.db.query(Vehicle).filter(
            Vehicle.is_active == True,
            Vehicle.uvis_device_id.isnot(None)
        ).all()
        
        total_vehicles = len(active_vehicles)
        monitored_count = 0
        all_alerts = []
        
        # 각 차량 모니터링
        for vehicle in active_vehicles:
            try:
                vehicle_data = await self._monitor_single_vehicle(vehicle)
                
                if vehicle_data:
                    monitored_count += 1
                    
                    # 알림이 있으면 수집
                    if vehicle_data.get('alerts'):
                        all_alerts.extend(vehicle_data['alerts'])
                        
                        # 중요 알림은 이메일 발송
                        for alert in vehicle_data['alerts']:
                            if alert['severity'] in ['critical', 'warning']:
                                await self._send_alert_email(vehicle, alert)
                
            except Exception as e:
                logger.error(f"Error monitoring vehicle {vehicle.id}: {e}")
                continue
        
        # 요약 통계
        summary = self._generate_monitoring_summary(active_vehicles, all_alerts)
        
        # WebSocket으로 실시간 업데이트 브로드캐스트
        await self._broadcast_update({
            'type': 'monitoring_update',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'total_vehicles': total_vehicles,
                'monitored': monitored_count,
                'alerts_count': len(all_alerts),
                'summary': summary
            }
        })
        
        logger.info(f"Monitoring complete: {monitored_count}/{total_vehicles} vehicles, {len(all_alerts)} alerts")
        
        return {
            'total_vehicles': total_vehicles,
            'monitored': monitored_count,
            'alerts': all_alerts,
            'summary': summary
        }
    
    async def _monitor_single_vehicle(self, vehicle: Vehicle) -> Optional[Dict[str, Any]]:
        """
        단일 차량 모니터링
        
        Args:
            vehicle: 차량 객체
            
        Returns:
            차량 모니터링 데이터
        """
        try:
            terminal_id = vehicle.uvis_device_id
            
            # UVIS 종합 모니터링 (위치 + 온도 + 상태)
            monitor_data = await self.uvis_service.monitor_vehicle(terminal_id)
            
            if not monitor_data:
                return None
            
            # GPS 로그 저장
            if monitor_data.get('location'):
                await self.uvis_gps_service._save_gps_data([{
                    'TID_ID': terminal_id,
                    'BI_X_POSITION': str(monitor_data['location']['latitude']),
                    'BI_Y_POSITION': str(monitor_data['location']['longitude']),
                    'BI_GPS_SPEED': monitor_data['location']['speed'],
                    'BI_TURN_ONOFF': 'ON' if monitor_data.get('status', {}).get('engine_status') == 'ON' else 'OFF',
                    'BI_DATE': datetime.now().strftime('%Y%m%d'),
                    'BI_TIME': datetime.now().strftime('%H%M%S'),
                    'CM_NUMBER': vehicle.license_plate
                }])
            
            # 온도 로그 저장 및 알림 체크
            alerts = []
            if monitor_data.get('temperature'):
                temp_data = monitor_data['temperature']
                
                # 온도 로그 저장
                await self.uvis_gps_service._save_temperature_data([{
                    'TID_ID': terminal_id,
                    'TPL_X_POSITION': str(monitor_data['location']['latitude']) if monitor_data.get('location') else '0',
                    'TPL_Y_POSITION': str(monitor_data['location']['longitude']) if monitor_data.get('location') else '0',
                    'TPL_SIGNAL_A': '0' if temp_data['temperature'] >= 0 else '1',
                    'TPL_DEGREE_A': str(abs(temp_data['temperature'])),
                    'TPL_DATE': datetime.now().strftime('%Y%m%d'),
                    'TPL_TIME': datetime.now().strftime('%H%M%S'),
                    'CM_NUMBER': vehicle.license_plate
                }])
                
                # 온도 알림 체크
                temp_alert = self._check_temperature_alert(
                    vehicle,
                    temp_data['temperature'],
                    temp_data['zone']
                )
                
                if temp_alert:
                    alerts.append(temp_alert)
            
            # UVIS 기본 알림 추가
            if monitor_data.get('alerts'):
                alerts.extend(monitor_data['alerts'])
            
            return {
                'vehicle_id': vehicle.id,
                'vehicle_name': vehicle.license_plate,
                'location': monitor_data.get('location'),
                'temperature': monitor_data.get('temperature'),
                'status': monitor_data.get('status'),
                'alerts': alerts,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error monitoring vehicle {vehicle.id}: {e}")
            return None
    
    def _check_temperature_alert(
        self,
        vehicle: Vehicle,
        temperature: float,
        zone: str
    ) -> Optional[Dict[str, Any]]:
        """
        온도 알림 체크
        
        Args:
            vehicle: 차량 객체
            temperature: 현재 온도
            zone: 온도대 (frozen/chilled/ambient)
            
        Returns:
            알림 정보 또는 None
        """
        # 차량 온도대 매핑
        vehicle_type_map = {
            '냉동': 'frozen',
            '냉장': 'chilled',
            '상온': 'ambient'
        }
        
        vehicle_zone = None
        for korean_type, english_zone in vehicle_type_map.items():
            if english_zone == zone or vehicle.vehicle_type == korean_type:
                vehicle_zone = korean_type
                break
        
        if not vehicle_zone or vehicle_zone not in self.temperature_thresholds:
            return None
        
        threshold = self.temperature_thresholds[vehicle_zone]
        
        # 온도 이탈 체크
        alert_type = None
        severity = None
        
        if temperature < threshold['critical_min']:
            alert_type = 'critical_too_cold'
            severity = 'critical'
        elif temperature < threshold['min']:
            alert_type = 'warning_too_cold'
            severity = 'warning'
        elif temperature > threshold['critical_max']:
            alert_type = 'critical_too_hot'
            severity = 'critical'
        elif temperature > threshold['max']:
            alert_type = 'warning_too_hot'
            severity = 'warning'
        
        if not alert_type:
            return None
        
        return {
            'type': 'temperature',
            'alert_type': alert_type,
            'severity': severity,
            'vehicle_id': vehicle.id,
            'vehicle_name': vehicle.license_plate,
            'temperature': temperature,
            'zone': vehicle_zone,
            'threshold_min': threshold['min'],
            'threshold_max': threshold['max'],
            'message': f"차량 {vehicle.license_plate} 온도 이탈: {temperature:.1f}°C (허용 범위: {threshold['min']}~{threshold['max']}°C)",
            'timestamp': datetime.now().isoformat()
        }
    
    async def _send_alert_email(self, vehicle: Vehicle, alert: Dict[str, Any]):
        """
        알림 이메일 발송
        
        Args:
            vehicle: 차량 객체
            alert: 알림 정보
        """
        try:
            # 배차 정보 조회 (해당 차량의 진행 중인 배차)
            dispatch = self.db.query(Dispatch).filter(
                Dispatch.vehicle_id == vehicle.id,
                Dispatch.status.in_(['assigned', 'in_transit'])
            ).first()
            
            # 이메일 수신자 결정 (관리자 + 담당 운전자)
            recipients = ['admin@coldchain.com']  # 기본 관리자
            
            if dispatch and dispatch.driver:
                recipients.append(f"{dispatch.driver.username}@coldchain.com")
            
            # 이메일 전송
            await self.email_service.send_temperature_alert(
                recipients=recipients,
                vehicle_name=vehicle.license_plate,
                temperature=alert['temperature'],
                threshold_min=alert['threshold_min'],
                threshold_max=alert['threshold_max'],
                location=f"{alert.get('latitude', 'N/A')}, {alert.get('longitude', 'N/A')}",
                severity=alert['severity']
            )
            
            logger.info(f"Alert email sent for vehicle {vehicle.id}, alert: {alert['alert_type']}")
            
        except Exception as e:
            logger.error(f"Error sending alert email: {e}")
    
    def _generate_monitoring_summary(
        self,
        vehicles: List[Vehicle],
        alerts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        모니터링 요약 생성
        
        Args:
            vehicles: 차량 목록
            alerts: 알림 목록
            
        Returns:
            요약 통계
        """
        # 온도대별 차량 수
        zone_counts = {'냉동': 0, '냉장': 0, '상온': 0}
        for vehicle in vehicles:
            if vehicle.vehicle_type in zone_counts:
                zone_counts[vehicle.vehicle_type] += 1
        
        # 심각도별 알림 수
        severity_counts = {'critical': 0, 'warning': 0, 'info': 0}
        for alert in alerts:
            severity = alert.get('severity', 'info')
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # 알림 유형별 수
        type_counts = {}
        for alert in alerts:
            alert_type = alert.get('type', 'unknown')
            type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
        
        return {
            'vehicle_zones': zone_counts,
            'alert_severity': severity_counts,
            'alert_types': type_counts,
            'total_alerts': len(alerts),
            'critical_alerts': severity_counts['critical'],
            'timestamp': datetime.now().isoformat()
        }
    
    async def _broadcast_update(self, message: Dict[str, Any]):
        """
        WebSocket으로 실시간 업데이트 브로드캐스트
        
        Args:
            message: 브로드캐스트할 메시지
        """
        if not self.websocket_connections:
            return
        
        # 연결된 모든 WebSocket 클라이언트에 메시지 전송
        disconnected = []
        for ws in self.websocket_connections:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"WebSocket send error: {e}")
                disconnected.append(ws)
        
        # 연결이 끊긴 클라이언트 제거
        for ws in disconnected:
            self.websocket_connections.remove(ws)
    
    def add_websocket_connection(self, websocket):
        """WebSocket 연결 추가"""
        self.websocket_connections.append(websocket)
        logger.info(f"WebSocket connection added. Total: {len(self.websocket_connections)}")
    
    def remove_websocket_connection(self, websocket):
        """WebSocket 연결 제거"""
        if websocket in self.websocket_connections:
            self.websocket_connections.remove(websocket)
            logger.info(f"WebSocket connection removed. Total: {len(self.websocket_connections)}")
    
    async def get_monitoring_dashboard_data(self) -> Dict[str, Any]:
        """
        실시간 모니터링 대시보드 데이터 조회
        
        Returns:
            대시보드 데이터
        """
        # 최근 1시간 내 GPS 로그
        one_hour_ago = datetime.now() - timedelta(hours=1)
        
        # 활성 차량
        active_vehicles = self.db.query(Vehicle).filter(
            Vehicle.is_active == True
        ).all()
        
        # 각 차량의 최신 위치/온도
        vehicle_status = []
        for vehicle in active_vehicles:
            latest_gps = self.uvis_gps_service.get_latest_gps_by_vehicle(vehicle.id)
            latest_temp = self.uvis_gps_service.get_latest_temperature_by_vehicle(vehicle.id)
            
            vehicle_status.append({
                'vehicle_id': vehicle.id,
                'license_plate': vehicle.license_plate,
                'vehicle_type': vehicle.vehicle_type,
                'location': {
                    'latitude': latest_gps.latitude if latest_gps else None,
                    'longitude': latest_gps.longitude if latest_gps else None,
                    'speed': latest_gps.speed_kmh if latest_gps else None,
                    'engine_on': latest_gps.is_engine_on if latest_gps else None,
                    'timestamp': latest_gps.created_at.isoformat() if latest_gps else None
                },
                'temperature': {
                    'value': latest_temp.temperature_a if latest_temp else None,
                    'timestamp': latest_temp.created_at.isoformat() if latest_temp else None
                }
            })
        
        return {
            'total_vehicles': len(active_vehicles),
            'vehicles': vehicle_status,
            'timestamp': datetime.now().isoformat()
        }
    
    async def start_background_monitoring(self, interval_seconds: int = 60):
        """
        백그라운드 모니터링 시작 (주기적 실행)
        
        Args:
            interval_seconds: 모니터링 주기 (초)
        """
        logger.info(f"Starting background monitoring (interval: {interval_seconds}s)")
        
        while True:
            try:
                await self.monitor_all_vehicles()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Background monitoring error: {e}")
                await asyncio.sleep(interval_seconds)


# 싱글톤 인스턴스
_monitoring_service_instance = None


def get_monitoring_service(db: Session) -> RealtimeMonitoringService:
    """모니터링 서비스 인스턴스 가져오기"""
    global _monitoring_service_instance
    
    if _monitoring_service_instance is None:
        _monitoring_service_instance = RealtimeMonitoringService(db)
    
    return _monitoring_service_instance
