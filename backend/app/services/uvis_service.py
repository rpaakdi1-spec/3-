"""
Samsung UVIS API 연동 서비스
- 실시간 GPS 위치 조회
- 차량 온도 모니터링
- 차량 상태 추적
"""

import httpx
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from loguru import logger

from app.core.config import settings


class UVISService:
    """Samsung UVIS API 연동 서비스"""
    
    def __init__(self):
        self.api_url = settings.UVIS_API_URL
        self.api_key = settings.UVIS_API_KEY
        self._client = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """HTTP 클라이언트 가져오기"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client
    
    async def close(self):
        """클라이언트 종료"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def get_vehicle_location(
        self,
        terminal_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        차량 GPS 위치 조회
        
        Args:
            terminal_id: UVIS 단말기 ID
            
        Returns:
            {
                'terminal_id': str,
                'latitude': float,
                'longitude': float,
                'speed': float,  # km/h
                'heading': float,  # 0-360 degrees
                'timestamp': str,  # ISO format
                'accuracy': float  # meters
            }
        """
        try:
            client = await self._get_client()
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = await client.get(
                f"{self.api_url}/vehicles/{terminal_id}/location",
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"UVIS API error: HTTP {response.status_code}")
                return None
            
            data = response.json()
            
            location = {
                'terminal_id': terminal_id,
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'speed': data.get('speed', 0),
                'heading': data.get('heading', 0),
                'timestamp': data.get('timestamp', datetime.now().isoformat()),
                'accuracy': data.get('accuracy', 0)
            }
            
            logger.debug(f"Location for {terminal_id}: ({location['latitude']}, {location['longitude']})")
            return location
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting location for {terminal_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting location for {terminal_id}: {e}")
            return None
    
    async def get_vehicle_temperature(
        self,
        terminal_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        차량 온도 조회
        
        Args:
            terminal_id: UVIS 단말기 ID
            
        Returns:
            {
                'terminal_id': str,
                'temperature': float,  # Celsius
                'unit': str,  # 'celsius'
                'timestamp': str,
                'zone': str,  # 'frozen', 'chilled', 'ambient'
                'status': str  # 'normal', 'warning', 'critical'
            }
        """
        try:
            client = await self._get_client()
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = await client.get(
                f"{self.api_url}/vehicles/{terminal_id}/temperature",
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"UVIS API error: HTTP {response.status_code}")
                return None
            
            data = response.json()
            temp = data.get('temperature', 0)
            
            # 온도대 판별
            if temp < -15:
                zone = 'frozen'
                status = 'normal' if -25 <= temp <= -18 else 'warning'
            elif temp < 10:
                zone = 'chilled'
                status = 'normal' if 0 <= temp <= 6 else 'warning'
            else:
                zone = 'ambient'
                status = 'normal' if temp < 30 else 'warning'
            
            temperature = {
                'terminal_id': terminal_id,
                'temperature': temp,
                'unit': 'celsius',
                'timestamp': data.get('timestamp', datetime.now().isoformat()),
                'zone': zone,
                'status': status
            }
            
            if status == 'warning':
                logger.warning(f"Temperature warning for {terminal_id}: {temp}°C (zone: {zone})")
            
            return temperature
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting temperature for {terminal_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting temperature for {terminal_id}: {e}")
            return None
    
    async def get_vehicle_status(
        self,
        terminal_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        차량 종합 상태 조회
        
        Args:
            terminal_id: UVIS 단말기 ID
            
        Returns:
            {
                'terminal_id': str,
                'engine_status': str,  # 'ON', 'OFF'
                'door_status': str,  # 'OPEN', 'CLOSED'
                'refrigeration_status': str,  # 'ON', 'OFF'
                'battery_level': float,  # 0-100%
                'timestamp': str
            }
        """
        try:
            client = await self._get_client()
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = await client.get(
                f"{self.api_url}/vehicles/{terminal_id}/status",
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"UVIS API error: HTTP {response.status_code}")
                return None
            
            data = response.json()
            
            status = {
                'terminal_id': terminal_id,
                'engine_status': data.get('engine_status', 'UNKNOWN'),
                'door_status': data.get('door_status', 'UNKNOWN'),
                'refrigeration_status': data.get('refrigeration_status', 'UNKNOWN'),
                'battery_level': data.get('battery_level', 0),
                'timestamp': data.get('timestamp', datetime.now().isoformat())
            }
            
            return status
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting status for {terminal_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting status for {terminal_id}: {e}")
            return None
    
    async def get_bulk_vehicle_locations(
        self,
        terminal_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        여러 차량의 위치 일괄 조회
        
        Args:
            terminal_ids: UVIS 단말기 ID 리스트
            
        Returns:
            위치 정보 리스트
        """
        logger.info(f"Bulk location query for {len(terminal_ids)} vehicles")
        
        results = []
        for terminal_id in terminal_ids:
            location = await self.get_vehicle_location(terminal_id)
            if location:
                results.append(location)
        
        logger.info(f"Retrieved {len(results)}/{len(terminal_ids)} locations")
        return results
    
    async def get_bulk_vehicle_temperatures(
        self,
        terminal_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        여러 차량의 온도 일괄 조회
        
        Args:
            terminal_ids: UVIS 단말기 ID 리스트
            
        Returns:
            온도 정보 리스트
        """
        logger.info(f"Bulk temperature query for {len(terminal_ids)} vehicles")
        
        results = []
        for terminal_id in terminal_ids:
            temperature = await self.get_vehicle_temperature(terminal_id)
            if temperature:
                results.append(temperature)
        
        # 경고 상태 요약
        warning_count = sum(1 for t in results if t['status'] == 'warning')
        if warning_count > 0:
            logger.warning(f"Temperature warnings: {warning_count}/{len(results)} vehicles")
        
        return results
    
    async def monitor_vehicle(
        self,
        terminal_id: str
    ) -> Dict[str, Any]:
        """
        차량 종합 모니터링 (위치 + 온도 + 상태)
        
        Args:
            terminal_id: UVIS 단말기 ID
            
        Returns:
            종합 모니터링 정보
        """
        location = await self.get_vehicle_location(terminal_id)
        temperature = await self.get_vehicle_temperature(terminal_id)
        status = await self.get_vehicle_status(terminal_id)
        
        return {
            'terminal_id': terminal_id,
            'timestamp': datetime.now().isoformat(),
            'location': location,
            'temperature': temperature,
            'status': status,
            'alerts': self._check_alerts(location, temperature, status)
        }
    
    def _check_alerts(
        self,
        location: Optional[Dict],
        temperature: Optional[Dict],
        status: Optional[Dict]
    ) -> List[Dict[str, str]]:
        """알림 체크"""
        alerts = []
        
        # 온도 이상
        if temperature and temperature['status'] == 'warning':
            alerts.append({
                'type': 'temperature',
                'severity': 'warning',
                'message': f"온도 이상: {temperature['temperature']}°C (zone: {temperature['zone']})"
            })
        
        # GPS 신호 약함
        if location and location['accuracy'] > 100:
            alerts.append({
                'type': 'gps',
                'severity': 'info',
                'message': f"GPS 정확도 낮음: {location['accuracy']:.0f}m"
            })
        
        # 냉동 장치 꺼짐
        if status and status['refrigeration_status'] == 'OFF':
            alerts.append({
                'type': 'refrigeration',
                'severity': 'critical',
                'message': "냉동 장치가 꺼져 있습니다"
            })
        
        # 배터리 낮음
        if status and status['battery_level'] < 20:
            alerts.append({
                'type': 'battery',
                'severity': 'warning',
                'message': f"배터리 부족: {status['battery_level']:.0f}%"
            })
        
        return alerts


# Mock 데이터 생성 함수 (실제 UVIS API가 없을 때)
class MockUVISService(UVISService):
    """Mock UVIS 서비스 (테스트용)"""
    
    async def get_vehicle_location(self, terminal_id: str) -> Optional[Dict[str, Any]]:
        """Mock GPS 위치"""
        import random
        
        # 서울 중심 좌표 (랜덤)
        base_lat = 37.5665
        base_lon = 126.9780
        
        return {
            'terminal_id': terminal_id,
            'latitude': base_lat + random.uniform(-0.1, 0.1),
            'longitude': base_lon + random.uniform(-0.1, 0.1),
            'speed': random.uniform(0, 80),
            'heading': random.uniform(0, 360),
            'timestamp': datetime.now().isoformat(),
            'accuracy': random.uniform(5, 20)
        }
    
    async def get_vehicle_temperature(self, terminal_id: str) -> Optional[Dict[str, Any]]:
        """Mock 온도"""
        import random
        
        # 온도대별 랜덤 온도
        zone_temps = {
            'frozen': random.uniform(-25, -18),
            'chilled': random.uniform(0, 6),
            'ambient': random.uniform(15, 25)
        }
        
        zone = random.choice(['frozen', 'chilled', 'ambient'])
        temp = zone_temps[zone]
        
        return {
            'terminal_id': terminal_id,
            'temperature': temp,
            'unit': 'celsius',
            'timestamp': datetime.now().isoformat(),
            'zone': zone,
            'status': 'normal'
        }
    
    async def get_vehicle_status(self, terminal_id: str) -> Optional[Dict[str, Any]]:
        """Mock 차량 상태"""
        import random
        
        return {
            'terminal_id': terminal_id,
            'engine_status': random.choice(['ON', 'ON', 'OFF']),
            'door_status': random.choice(['CLOSED', 'CLOSED', 'OPEN']),
            'refrigeration_status': random.choice(['ON', 'ON', 'OFF']),
            'battery_level': random.uniform(30, 100),
            'timestamp': datetime.now().isoformat()
        }


# 환경에 따라 Mock 또는 실제 서비스 선택
def get_uvis_service() -> UVISService:
    """UVIS 서비스 인스턴스 가져오기"""
    # UVIS API 키가 설정되어 있으면 실제 서비스 사용
    if settings.UVIS_API_KEY and settings.UVIS_API_KEY != 'your_uvis_api_key_here':
        logger.info("Using real UVIS service")
        return UVISService()
    else:
        logger.info("Using mock UVIS service (for testing)")
        return MockUVISService()
