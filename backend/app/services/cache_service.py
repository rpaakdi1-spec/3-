"""
캐싱 서비스
- 거리 행렬 캐싱
- 지오코딩 결과 캐싱
- API 응답 캐싱
"""

from typing import Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
from functools import lru_cache
import hashlib
import json
from loguru import logger


class CacheService:
    """인메모리 캐싱 서비스"""
    
    def __init__(self):
        self._distance_cache: Dict[str, float] = {}
        self._geocode_cache: Dict[str, Tuple[Optional[float], Optional[float]]] = {}
        self._route_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = timedelta(hours=24)  # 24시간 TTL
        self._cache_timestamps: Dict[str, datetime] = {}
    
    def get_distance(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> Optional[float]:
        """
        거리 캐시 조회
        
        Args:
            start_lat: 출발지 위도
            start_lon: 출발지 경도
            end_lat: 도착지 위도
            end_lon: 도착지 경도
            
        Returns:
            캐시된 거리 (m) 또는 None
        """
        key = self._make_distance_key(start_lat, start_lon, end_lat, end_lon)
        
        # TTL 확인
        if key in self._cache_timestamps:
            if datetime.now() - self._cache_timestamps[key] > self._cache_ttl:
                self._distance_cache.pop(key, None)
                self._cache_timestamps.pop(key, None)
                return None
        
        return self._distance_cache.get(key)
    
    def set_distance(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float, distance: float):
        """
        거리 캐시 저장
        
        Args:
            start_lat: 출발지 위도
            start_lon: 출발지 경도
            end_lat: 도착지 위도
            end_lon: 도착지 경도
            distance: 거리 (m)
        """
        key = self._make_distance_key(start_lat, start_lon, end_lat, end_lon)
        self._distance_cache[key] = distance
        self._cache_timestamps[key] = datetime.now()
    
    def get_geocode(self, address: str) -> Optional[Tuple[Optional[float], Optional[float]]]:
        """
        지오코딩 캐시 조회
        
        Args:
            address: 주소
            
        Returns:
            (위도, 경도) 튜플 또는 None
        """
        key = self._make_address_key(address)
        
        # TTL 확인
        if key in self._cache_timestamps:
            if datetime.now() - self._cache_timestamps[key] > self._cache_ttl:
                self._geocode_cache.pop(key, None)
                self._cache_timestamps.pop(key, None)
                return None
        
        return self._geocode_cache.get(key)
    
    def set_geocode(self, address: str, latitude: Optional[float], longitude: Optional[float]):
        """
        지오코딩 캐시 저장
        
        Args:
            address: 주소
            latitude: 위도
            longitude: 경도
        """
        key = self._make_address_key(address)
        self._geocode_cache[key] = (latitude, longitude)
        self._cache_timestamps[key] = datetime.now()
    
    def get_route(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> Optional[Dict[str, Any]]:
        """
        경로 캐시 조회
        
        Args:
            start_lat: 출발지 위도
            start_lon: 출발지 경도
            end_lat: 도착지 위도
            end_lon: 도착지 경도
            
        Returns:
            경로 정보 또는 None
        """
        key = self._make_distance_key(start_lat, start_lon, end_lat, end_lon)
        
        # TTL 확인
        if key in self._cache_timestamps:
            if datetime.now() - self._cache_timestamps[key] > self._cache_ttl:
                self._route_cache.pop(key, None)
                self._cache_timestamps.pop(key, None)
                return None
        
        return self._route_cache.get(key)
    
    def set_route(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float, route_data: Dict[str, Any]):
        """
        경로 캐시 저장
        
        Args:
            start_lat: 출발지 위도
            start_lon: 출발지 경도
            end_lat: 도착지 위도
            end_lon: 도착지 경도
            route_data: 경로 정보
        """
        key = self._make_distance_key(start_lat, start_lon, end_lat, end_lon)
        self._route_cache[key] = route_data
        self._cache_timestamps[key] = datetime.now()
    
    def clear_expired(self):
        """만료된 캐시 삭제"""
        now = datetime.now()
        expired_keys = [
            key for key, timestamp in self._cache_timestamps.items()
            if now - timestamp > self._cache_ttl
        ]
        
        for key in expired_keys:
            self._distance_cache.pop(key, None)
            self._geocode_cache.pop(key, None)
            self._route_cache.pop(key, None)
            self._cache_timestamps.pop(key, None)
        
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 조회"""
        return {
            'distance_cache_size': len(self._distance_cache),
            'geocode_cache_size': len(self._geocode_cache),
            'route_cache_size': len(self._route_cache),
            'total_entries': len(self._cache_timestamps),
            'cache_ttl_hours': self._cache_ttl.total_seconds() / 3600
        }
    
    def clear_all(self):
        """모든 캐시 삭제"""
        self._distance_cache.clear()
        self._geocode_cache.clear()
        self._route_cache.clear()
        self._cache_timestamps.clear()
        logger.info("All caches cleared")
    
    @staticmethod
    def _make_distance_key(start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> str:
        """거리 캐시 키 생성"""
        # 소수점 6자리까지만 사용 (약 0.1m 정확도)
        start = f"{start_lat:.6f},{start_lon:.6f}"
        end = f"{end_lat:.6f},{end_lon:.6f}"
        return f"{start}_{end}"
    
    @staticmethod
    def _make_address_key(address: str) -> str:
        """주소 캐시 키 생성"""
        # 주소 정규화 (공백 제거, 소문자 변환)
        normalized = address.strip().lower()
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()


# 전역 캐시 인스턴스
_cache_service = None


def get_cache_service() -> CacheService:
    """캐시 서비스 싱글톤 인스턴스 가져오기"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
        logger.info("Cache service initialized")
    return _cache_service


# LRU 캐시 데코레이터 사용 예시
@lru_cache(maxsize=1000)
def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Haversine 거리 계산 (LRU 캐시 적용)
    
    Args:
        lat1, lon1: 시작점 좌표
        lat2, lon2: 종료점 좌표
        
    Returns:
        거리 (km)
    """
    from math import radians, cos, sin, asin, sqrt
    
    # 지구 반지름 (km)
    R = 6371.0
    
    # 라디안으로 변환
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    # Haversine 공식
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    
    distance = R * c
    return distance
