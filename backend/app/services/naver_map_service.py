import httpx
import logging
from typing import Dict, Optional, Tuple
from app.core.config import settings

logger = logging.getLogger(__name__)


class NaverMapService:
    """
    네이버 지도 API 연동 서비스
    - 거리 계산
    - 소요시간 계산
    - 주소 ↔ 좌표 변환
    """
    
    BASE_URL_GEOCODING = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    BASE_URL_REVERSE_GEOCODING = "https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc"
    BASE_URL_DIRECTIONS = "https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving"
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """
        Initialize Naver Map Service
        
        Args:
            client_id: 네이버 클라우드 플랫폼 Client ID (설정 파일에서 읽어옴)
            client_secret: 네이버 클라우드 플랫폼 Client Secret (설정 파일에서 읽어옴)
        """
        self.client_id = client_id or getattr(settings, "NAVER_MAP_CLIENT_ID", None)
        self.client_secret = client_secret or getattr(settings, "NAVER_MAP_CLIENT_SECRET", None)
        
        if not self.client_id or not self.client_secret:
            logger.warning("Naver Map API credentials not configured. Distance/duration calculation will be simulated.")
    
    async def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        주소를 좌표(위도, 경도)로 변환
        
        Args:
            address: 변환할 주소
            
        Returns:
            (latitude, longitude) 튜플 또는 None
        """
        if not self.client_id or not self.client_secret:
            logger.warning("Geocoding skipped: API credentials not configured")
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.BASE_URL_GEOCODING,
                    headers={
                        "X-NCP-APIGW-API-KEY-ID": self.client_id,
                        "X-NCP-APIGW-API-KEY": self.client_secret
                    },
                    params={"query": address}
                )
                
                if response.status_code != 200:
                    logger.error(f"Geocoding failed: {response.status_code} - {response.text}")
                    return None
                
                data = response.json()
                
                if data.get("status") != "OK" or not data.get("addresses"):
                    logger.warning(f"No geocoding results for address: {address}")
                    return None
                
                first_result = data["addresses"][0]
                lat = float(first_result["y"])
                lng = float(first_result["x"])
                
                return (lat, lng)
        
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return None
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[str]:
        """
        좌표(위도, 경도)를 주소로 변환 (역 지오코딩)
        
        Args:
            latitude: 위도
            longitude: 경도
            
        Returns:
            주소 문자열 또는 None
        """
        if not self.client_id or not self.client_secret:
            logger.warning("Reverse geocoding skipped: API credentials not configured")
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.BASE_URL_REVERSE_GEOCODING,
                    headers={
                        "X-NCP-APIGW-API-KEY-ID": self.client_id,
                        "X-NCP-APIGW-API-KEY": self.client_secret
                    },
                    params={
                        "coords": f"{longitude},{latitude}",  # 경도, 위도 순서
                        "orders": "roadaddr,addr",  # 도로명 주소 우선
                        "output": "json"
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Reverse geocoding failed: {response.status_code} - {response.text}")
                    return None
                
                data = response.json()
                
                if data.get("status", {}).get("code") != 0 or not data.get("results"):
                    logger.warning(f"No reverse geocoding results for coords: {latitude}, {longitude}")
                    return None
                
                # 첫 번째 결과 사용 (도로명 주소 or 지번 주소)
                first_result = data["results"][0]
                
                # 도로명 주소 우선
                if first_result.get("name") == "roadaddr":
                    land = first_result.get("land", {})
                    if land:
                        # 도로명 주소 조합
                        area1 = land.get("name", "")
                        area2 = land.get("addition0", {}).get("value", "")
                        number1 = land.get("number1", "")
                        number2 = land.get("number2", "")
                        
                        address_parts = [area1, area2]
                        if number1:
                            if number2:
                                address_parts.append(f"{number1}-{number2}")
                            else:
                                address_parts.append(number1)
                        
                        address = " ".join(filter(None, address_parts))
                        if address:
                            return address
                
                # 도로명 주소가 없으면 지번 주소 사용
                region = first_result.get("region", {})
                area1 = region.get("area1", {}).get("name", "")
                area2 = region.get("area2", {}).get("name", "")
                area3 = region.get("area3", {}).get("name", "")
                area4 = region.get("area4", {}).get("name", "")
                
                land = first_result.get("land", {})
                number1 = land.get("number1", "")
                number2 = land.get("number2", "")
                
                address_parts = [area1, area2, area3, area4]
                if number1:
                    if number2:
                        address_parts.append(f"{number1}-{number2}")
                    else:
                        address_parts.append(number1)
                
                address = " ".join(filter(None, address_parts))
                return address if address else None
        
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
            return None
    
    async def calculate_distance_and_duration(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float
    ) -> Dict[str, Optional[float]]:
        """
        네이버 지도 API를 사용하여 거리와 소요시간 계산
        
        Args:
            origin_lat: 출발지 위도
            origin_lng: 출발지 경도
            dest_lat: 도착지 위도
            dest_lng: 도착지 경도
            
        Returns:
            {
                "distance_km": 거리(킬로미터),
                "duration_minutes": 소요시간(분)
            }
        """
        if not self.client_id or not self.client_secret:
            # API 미설정 시 시뮬레이션 (하버사인 공식 기반 예측)
            logger.warning("Naver Map API not configured. Using simulated distance/duration.")
            return self._simulate_distance_and_duration(origin_lat, origin_lng, dest_lat, dest_lng)
        
        try:
            async with httpx.AsyncClient() as client:
                # 네이버 Directions API 요청
                response = await client.get(
                    self.BASE_URL_DIRECTIONS,
                    headers={
                        "X-NCP-APIGW-API-KEY-ID": self.client_id,
                        "X-NCP-APIGW-API-KEY": self.client_secret
                    },
                    params={
                        "start": f"{origin_lng},{origin_lat}",  # 경도, 위도 순서
                        "goal": f"{dest_lng},{dest_lat}",
                        "option": "trafast"  # 실시간 빠른길
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Directions API failed: {response.status_code} - {response.text}")
                    return self._simulate_distance_and_duration(origin_lat, origin_lng, dest_lat, dest_lng)
                
                data = response.json()
                
                if data.get("code") != 0 or not data.get("route"):
                    logger.warning(f"No route found: {data.get('message', 'Unknown error')}")
                    return self._simulate_distance_and_duration(origin_lat, origin_lng, dest_lat, dest_lng)
                
                # trafast 결과 파싱
                route = data["route"]["trafast"][0]
                summary = route["summary"]
                
                distance_meters = summary["distance"]
                duration_ms = summary["duration"]
                
                distance_km = round(distance_meters / 1000, 2)
                duration_minutes = round(duration_ms / 60000, 0)
                
                logger.info(f"Route calculated: {distance_km}km, {duration_minutes}분")
                
                return {
                    "distance_km": distance_km,
                    "duration_minutes": duration_minutes
                }
        
        except Exception as e:
            logger.error(f"Distance/duration calculation error: {e}")
            return self._simulate_distance_and_duration(origin_lat, origin_lng, dest_lat, dest_lng)
    
    def _simulate_distance_and_duration(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float
    ) -> Dict[str, Optional[float]]:
        """
        API 미설정 시 하버사인 공식 기반 거리/시간 시뮬레이션
        
        Args:
            origin_lat: 출발지 위도
            origin_lng: 출발지 경도
            dest_lat: 도착지 위도
            dest_lng: 도착지 경도
            
        Returns:
            {
                "distance_km": 거리(킬로미터),
                "duration_minutes": 소요시간(분)
            }
        """
        import math
        
        # 하버사인 공식으로 직선거리 계산
        R = 6371  # 지구 반지름 (km)
        
        lat1_rad = math.radians(origin_lat)
        lat2_rad = math.radians(dest_lat)
        delta_lat = math.radians(dest_lat - origin_lat)
        delta_lng = math.radians(dest_lng - origin_lng)
        
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) *
            math.sin(delta_lng / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        straight_distance_km = R * c
        
        # 실제 도로 거리는 직선거리보다 약 1.3배 (도시 내 평균)
        distance_km = round(straight_distance_km * 1.3, 2)
        
        # 평균 속도 40km/h 가정 (도시 내 교통 상황 고려)
        avg_speed_kmh = 40
        duration_minutes = round((distance_km / avg_speed_kmh) * 60, 0)
        
        logger.info(f"Simulated route: {distance_km}km, {duration_minutes}분")
        
        return {
            "distance_km": distance_km,
            "duration_minutes": duration_minutes
        }
    
    async def calculate_from_addresses(
        self,
        origin_address: str,
        dest_address: str
    ) -> Dict[str, Optional[float]]:
        """
        주소 기반 거리/시간 계산
        
        Args:
            origin_address: 출발지 주소
            dest_address: 도착지 주소
            
        Returns:
            {
                "distance_km": 거리(킬로미터),
                "duration_minutes": 소요시간(분),
                "origin_coords": (lat, lng) 또는 None,
                "dest_coords": (lat, lng) 또는 None
            }
        """
        # 주소를 좌표로 변환
        origin_coords = await self.geocode_address(origin_address)
        dest_coords = await self.geocode_address(dest_address)
        
        if not origin_coords or not dest_coords:
            logger.error(f"Failed to geocode addresses: {origin_address} / {dest_address}")
            return {
                "distance_km": None,
                "duration_minutes": None,
                "origin_coords": origin_coords,
                "dest_coords": dest_coords
            }
        
        # 거리/시간 계산
        result = await self.calculate_distance_and_duration(
            origin_coords[0], origin_coords[1],
            dest_coords[0], dest_coords[1]
        )
        
        result["origin_coords"] = origin_coords
        result["dest_coords"] = dest_coords
        
        return result
    
    async def create_distance_matrix(
        self,
        locations: list[tuple[float, float]],
        use_cache: bool = True,
        batch_size: int = 10,
        delay_ms: int = 0,
        **kwargs  # 추가 매개변수 무시 (향후 확장용)
    ) -> tuple[list[list[float]], list[list[float]]]:
        """
        여러 위치 간의 거리 및 시간 행렬 생성
        
        Args:
            locations: [(lat, lng), ...] 형식의 위치 리스트
            use_cache: 캐시 사용 여부 (현재는 미구현, 향후 확장용)
            batch_size: API 호출 배치 크기 (현재는 미구현, 향후 확장용)
            delay_ms: API 호출 간 대기 시간(ms) (현재는 미구현, 향후 Rate Limit 대응용)
            **kwargs: 추가 매개변수 (향후 확장용)
            
        Returns:
            (distance_matrix, duration_matrix) 튜플
            - distance_matrix[i][j]: i번째에서 j번째 위치까지의 거리(km)
            - duration_matrix[i][j]: i번째에서 j번째 위치까지의 시간(분)
        """
        n = len(locations)
        distance_matrix = [[0.0] * n for _ in range(n)]
        duration_matrix = [[0.0] * n for _ in range(n)]
        
        # 모든 위치 쌍에 대해 거리/시간 계산
        for i in range(n):
            for j in range(n):
                if i == j:
                    # 같은 위치는 거리/시간 0
                    distance_matrix[i][j] = 0.0
                    duration_matrix[i][j] = 0.0
                else:
                    # 거리 및 시간 계산
                    result = await self.calculate_distance_and_duration(
                        locations[i][0], locations[i][1],
                        locations[j][0], locations[j][1]
                    )
                    
                    distance_matrix[i][j] = result.get("distance_km", 0.0)
                    duration_matrix[i][j] = result.get("duration_minutes", 0.0)
        
        logger.info(f"Distance matrix created for {n} locations")
        return distance_matrix, duration_matrix
