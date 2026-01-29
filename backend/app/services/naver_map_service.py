import httpx
from typing import Optional, Tuple, Dict, Any, List
import asyncio
import hashlib
import json
from app.core.config import settings
from loguru import logger


class NaverMapService:
    """Service for Naver Map API integration"""
    
    GEOCODE_URL = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    DIRECTION_URL = "https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving"
    
    def __init__(self):
        self.client_id = settings.NAVER_MAP_CLIENT_ID
        self.client_secret = settings.NAVER_MAP_CLIENT_SECRET
        self._cache = {}  # In-memory cache (개선: Redis로 대체 가능)
    
    async def geocode_address(self, address: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """
        Convert address to coordinates using Naver Geocoding API
        
        Args:
            address: Address string to geocode
            
        Returns:
            Tuple of (latitude, longitude, error_message)
            Returns (None, None, error_message) if geocoding fails
        """
        # Fallback: Use mock geocoding if API key is not available
        if not self.client_id or not self.client_secret or self.client_id == "your_client_id_here":
            return await self._mock_geocode(address)
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "X-NCP-APIGW-API-KEY-ID": self.client_id,
                    "X-NCP-APIGW-API-KEY": self.client_secret,
                }
                
                params = {
                    "query": address,
                }
                
                response = await client.get(
                    self.GEOCODE_URL,
                    headers=headers,
                    params=params,
                    timeout=10.0
                )
                
                # If API key error (401), fall back to mock
                if response.status_code == 401:
                    logger.warning("Naver API key unauthorized, using mock geocoding")
                    return await self._mock_geocode(address)
                
                if response.status_code != 200:
                    error_msg = f"API 오류: HTTP {response.status_code}"
                    logger.error(f"Geocoding failed for '{address}': {error_msg}")
                    return None, None, error_msg
                
                data = response.json()
                
                if data.get("status") != "OK":
                    error_msg = f"API 상태 오류: {data.get('status')}"
                    logger.error(f"Geocoding failed for '{address}': {error_msg}")
                    return None, None, error_msg
                
                addresses = data.get("addresses", [])
                
                if not addresses:
                    error_msg = "주소를 찾을 수 없습니다"
                    logger.warning(f"No results for address: '{address}'")
                    return None, None, error_msg
                
                # Get first result
                result = addresses[0]
                latitude = float(result.get("y"))
                longitude = float(result.get("x"))
                
                logger.info(f"Geocoded '{address}' -> ({latitude}, {longitude})")
                return latitude, longitude, None
                
        except httpx.TimeoutException:
            error_msg = "API 요청 시간 초과"
            logger.error(f"Geocoding timeout for '{address}'")
            return None, None, error_msg
        except Exception as e:
            error_msg = f"지오코딩 오류: {str(e)}"
            logger.error(f"Geocoding exception for '{address}': {e}")
            return None, None, error_msg
    
    async def _mock_geocode(self, address: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """Mock geocoding for testing (서울 중심 기준 랜덤 좌표)"""
        import hashlib
        
        # 주소를 해시하여 일관된 좌표 생성
        hash_val = int(hashlib.md5(address.encode()).hexdigest(), 16)
        
        # 서울 중심 (37.5665, 126.9780) 기준 ±0.5도 범위
        base_lat = 37.5665
        base_lon = 126.9780
        
        lat_offset = ((hash_val % 1000) / 1000 - 0.5) * 1.0  # ±0.5도
        lon_offset = ((hash_val // 1000 % 1000) / 1000 - 0.5) * 1.0
        
        latitude = base_lat + lat_offset
        longitude = base_lon + lon_offset
        
        logger.info(f"Mock geocoded '{address}' -> ({latitude}, {longitude})")
        return latitude, longitude, None
    
    async def get_driving_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        waypoints: Optional[list] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get driving route between two points using Naver Directions API
        
        Args:
            start_lat: Starting latitude
            start_lon: Starting longitude
            end_lat: Ending latitude
            end_lon: Ending longitude
            waypoints: Optional list of waypoint coordinates [(lat, lon), ...]
            
        Returns:
            Dict with route information including distance and duration
            Returns None if request fails
        """
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "X-NCP-APIGW-API-KEY-ID": self.client_id,
                    "X-NCP-APIGW-API-KEY": self.client_secret,
                }
                
                params = {
                    "start": f"{start_lon},{start_lat}",  # Note: Naver uses lon,lat order
                    "goal": f"{end_lon},{end_lat}",
                }
                
                if waypoints:
                    # Format waypoints as lon,lat
                    waypoint_str = "|".join([f"{lon},{lat}" for lat, lon in waypoints])
                    params["waypoints"] = waypoint_str
                
                response = await client.get(
                    self.DIRECTION_URL,
                    headers=headers,
                    params=params,
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Directions API failed: HTTP {response.status_code}")
                    return None
                
                data = response.json()
                
                if data.get("code") != 0:
                    logger.error(f"Directions API error code: {data.get('code')}")
                    return None
                
                route = data.get("route", {}).get("traoptimal", [])
                
                if not route:
                    logger.warning("No route found")
                    return None
                
                summary = route[0].get("summary", {})
                
                return {
                    "distance_m": summary.get("distance", 0),  # meters
                    "distance_km": summary.get("distance", 0) / 1000,  # kilometers
                    "duration_ms": summary.get("duration", 0),  # milliseconds
                    "duration_minutes": summary.get("duration", 0) / 60000,  # minutes
                    "toll_fee": summary.get("tollFare", 0),  # toll fee in KRW
                    "fuel_price": summary.get("fuelPrice", 0),  # fuel price in KRW
                }
                
        except Exception as e:
            logger.error(f"Directions API exception: {e}")
            return None
    
    async def batch_geocode(self, addresses: list[str]) -> list[Tuple[Optional[float], Optional[float], Optional[str]]]:
        """
        Batch geocode multiple addresses
        
        Args:
            addresses: List of address strings
            
        Returns:
            List of (latitude, longitude, error_message) tuples
        """
        results = []
        for address in addresses:
            result = await self.geocode_address(address)
            results.append(result)
        return results
    
    def _generate_cache_key(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> str:
        """캐시 키 생성"""
        key_str = f"{start_lat:.6f},{start_lon:.6f}|{end_lat:.6f},{end_lon:.6f}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get_distance_and_duration(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        use_cache: bool = True
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        두 지점 간 거리와 소요 시간 조회 (캐싱 지원)
        
        Args:
            start_lat: 출발지 위도
            start_lon: 출발지 경도
            end_lat: 도착지 위도
            end_lon: 도착지 경도
            use_cache: 캐시 사용 여부
            
        Returns:
            Tuple of (distance_meters, duration_minutes)
            실패 시 (None, None) 반환
        """
        # 캐시 확인
        if use_cache:
            cache_key = self._generate_cache_key(start_lat, start_lon, end_lat, end_lon)
            if cache_key in self._cache:
                logger.debug(f"Cache hit for route: {cache_key[:8]}...")
                return self._cache[cache_key]
        
        # API 호출
        route_info = await self.get_driving_route(start_lat, start_lon, end_lat, end_lon)
        
        if route_info:
            distance_m = route_info['distance_m']
            duration_min = int(route_info['duration_minutes'])
            
            # 캐시 저장
            if use_cache:
                self._cache[cache_key] = (distance_m, duration_min)
            
            return distance_m, duration_min
        
        return None, None
    
    async def create_distance_matrix(
        self,
        locations: List[Tuple[float, float]],
        use_cache: bool = True,
        batch_size: int = 50,
        delay_ms: int = 100
    ) -> Tuple[List[List[int]], List[List[int]]]:
        """
        여러 위치 간의 거리/시간 행렬 생성
        
        Args:
            locations: 위치 리스트 [(lat, lon), ...]
            use_cache: 캐시 사용 여부
            batch_size: 배치당 요청 수 (API rate limit 고려)
            delay_ms: 요청 간 지연 시간 (밀리초)
            
        Returns:
            Tuple of (distance_matrix, time_matrix)
            - distance_matrix: 거리 행렬 (미터)
            - time_matrix: 시간 행렬 (분)
        """
        n = len(locations)
        distance_matrix = [[0] * n for _ in range(n)]
        time_matrix = [[0] * n for _ in range(n)]
        
        logger.info(f"거리 행렬 생성 시작: {n}x{n} = {n*n}개 경로")
        
        # 모든 경로 조합 생성
        tasks = []
        indices = []
        
        for i in range(n):
            for j in range(n):
                if i != j:  # 같은 위치는 0으로 유지
                    tasks.append((i, j, locations[i], locations[j]))
        
        total_tasks = len(tasks)
        completed = 0
        
        # 배치 단위로 처리
        for batch_start in range(0, total_tasks, batch_size):
            batch_end = min(batch_start + batch_size, total_tasks)
            batch_tasks = tasks[batch_start:batch_end]
            
            logger.info(f"배치 처리 중: {batch_start+1}-{batch_end} / {total_tasks}")
            
            # 배치 내 모든 요청을 동시에 실행
            batch_results = await asyncio.gather(*[
                self.get_distance_and_duration(
                    start_lat=start[0],
                    start_lon=start[1],
                    end_lat=end[0],
                    end_lon=end[1],
                    use_cache=use_cache
                )
                for i, j, start, end in batch_tasks
            ])
            
            # 결과를 행렬에 저장
            for (i, j, _, _), (distance, duration) in zip(batch_tasks, batch_results):
                if distance is not None and duration is not None:
                    distance_matrix[i][j] = distance
                    time_matrix[i][j] = duration
                else:
                    # API 실패 시 Haversine으로 대체
                    logger.warning(f"API 실패 ({i},{j}), Haversine 사용")
                    distance_matrix[i][j] = int(self._haversine_distance(
                        locations[i][0], locations[i][1],
                        locations[j][0], locations[j][1]
                    ) * 1000)
                    # 평균 속도 40km/h 가정
                    time_matrix[i][j] = int(distance_matrix[i][j] / (40 * 1000 / 60))
            
            completed += len(batch_tasks)
            logger.info(f"진행률: {completed}/{total_tasks} ({completed*100//total_tasks}%)")
            
            # Rate limit 방지를 위한 지연
            if batch_end < total_tasks:
                await asyncio.sleep(delay_ms / 1000)
        
        logger.success(f"✓ 거리 행렬 생성 완료: {n}x{n}")
        logger.info(f"캐시 히트: {len(self._cache)}개")
        
        return distance_matrix, time_matrix
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine 거리 계산 (km) - API 실패 시 대체"""
        import math
        R = 6371  # 지구 반지름 (km)
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    async def get_optimized_route_sequence(
        self,
        depot: Tuple[float, float],
        destinations: List[Tuple[float, float]]
    ) -> List[int]:
        """
        최적 경로 순서 계산 (간단한 nearest neighbor 휴리스틱)
        
        Args:
            depot: 출발/도착 지점 (lat, lon)
            destinations: 방문할 목적지 리스트 [(lat, lon), ...]
            
        Returns:
            최적 방문 순서 인덱스 리스트
        """
        if not destinations:
            return []
        
        n = len(destinations)
        visited = [False] * n
        route = []
        current_pos = depot
        
        for _ in range(n):
            # 현재 위치에서 가장 가까운 미방문 목적지 찾기
            min_distance = float('inf')
            nearest_idx = -1
            
            for i in range(n):
                if not visited[i]:
                    dist_m, _ = await self.get_distance_and_duration(
                        current_pos[0], current_pos[1],
                        destinations[i][0], destinations[i][1]
                    )
                    
                    if dist_m is not None and dist_m < min_distance:
                        min_distance = dist_m
                        nearest_idx = i
            
            if nearest_idx != -1:
                visited[nearest_idx] = True
                route.append(nearest_idx)
                current_pos = destinations[nearest_idx]
        
        return route
    
    def clear_cache(self):
        """캐시 초기화"""
        self._cache.clear()
        logger.info("Naver Map API 캐시 초기화")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """캐시 통계 반환"""
        return {
            "cache_size": len(self._cache),
            "cache_keys": list(self._cache.keys())[:10]  # 첫 10개만
        }
