import httpx
from typing import Optional, Tuple, Dict, Any
from app.core.config import settings
from loguru import logger


class NaverMapService:
    """Service for Naver Map API integration"""
    
    GEOCODE_URL = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    DIRECTION_URL = "https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving"
    
    def __init__(self):
        self.client_id = settings.NAVER_MAP_CLIENT_ID
        self.client_secret = settings.NAVER_MAP_CLIENT_SECRET
    
    async def geocode_address(self, address: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """
        Convert address to coordinates using Naver Geocoding API
        
        Args:
            address: Address string to geocode
            
        Returns:
            Tuple of (latitude, longitude, error_message)
            Returns (None, None, error_message) if geocoding fails
        """
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
