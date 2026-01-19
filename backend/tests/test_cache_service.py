"""
단위 테스트 - 캐싱 서비스
"""

import pytest
from datetime import datetime, timedelta
from app.services.cache_service import CacheService, calculate_haversine_distance


class TestCacheService:
    """캐싱 서비스 테스트"""
    
    def setup_method(self):
        """각 테스트 전에 실행"""
        self.cache = CacheService()
    
    def teardown_method(self):
        """각 테스트 후에 실행"""
        self.cache.clear_all()
    
    def test_distance_cache(self):
        """거리 캐시 테스트"""
        # Given
        start_lat, start_lon = 37.5665, 126.9780
        end_lat, end_lon = 37.5755, 126.9869
        distance = 10500.0  # 10.5km
        
        # When
        self.cache.set_distance(start_lat, start_lon, end_lat, end_lon, distance)
        cached_distance = self.cache.get_distance(start_lat, start_lon, end_lat, end_lon)
        
        # Then
        assert cached_distance == distance
    
    def test_distance_cache_miss(self):
        """거리 캐시 미스 테스트"""
        # Given
        start_lat, start_lon = 37.5665, 126.9780
        end_lat, end_lon = 37.5755, 126.9869
        
        # When
        cached_distance = self.cache.get_distance(start_lat, start_lon, end_lat, end_lon)
        
        # Then
        assert cached_distance is None
    
    def test_geocode_cache(self):
        """지오코딩 캐시 테스트"""
        # Given
        address = "서울특별시 강남구 테헤란로 427"
        latitude, longitude = 37.5012, 127.0396
        
        # When
        self.cache.set_geocode(address, latitude, longitude)
        cached_result = self.cache.get_geocode(address)
        
        # Then
        assert cached_result == (latitude, longitude)
    
    def test_geocode_cache_normalization(self):
        """지오코딩 캐시 주소 정규화 테스트"""
        # Given
        address1 = "서울특별시 강남구 테헤란로 427"
        address2 = "  서울특별시 강남구 테헤란로 427  "  # 공백 있음
        latitude, longitude = 37.5012, 127.0396
        
        # When
        self.cache.set_geocode(address1, latitude, longitude)
        cached_result = self.cache.get_geocode(address2)  # 공백 있는 주소로 조회
        
        # Then
        assert cached_result == (latitude, longitude)
    
    def test_cache_stats(self):
        """캐시 통계 테스트"""
        # Given
        self.cache.set_distance(37.5, 127.0, 37.6, 127.1, 10000)
        self.cache.set_geocode("서울시", 37.5, 127.0)
        
        # When
        stats = self.cache.get_stats()
        
        # Then
        assert stats['distance_cache_size'] == 1
        assert stats['geocode_cache_size'] == 1
        assert stats['total_entries'] == 2
    
    def test_cache_clear_all(self):
        """전체 캐시 삭제 테스트"""
        # Given
        self.cache.set_distance(37.5, 127.0, 37.6, 127.1, 10000)
        self.cache.set_geocode("서울시", 37.5, 127.0)
        
        # When
        self.cache.clear_all()
        stats = self.cache.get_stats()
        
        # Then
        assert stats['total_entries'] == 0
    
    def test_haversine_distance(self):
        """Haversine 거리 계산 테스트"""
        # Given
        lat1, lon1 = 37.5665, 126.9780  # 서울
        lat2, lon2 = 35.1796, 129.0756  # 부산
        
        # When
        distance = calculate_haversine_distance(lat1, lon1, lat2, lon2)
        
        # Then
        assert 320 < distance < 330  # 약 325km
    
    def test_haversine_distance_same_point(self):
        """동일 지점 거리 계산 테스트"""
        # Given
        lat, lon = 37.5665, 126.9780
        
        # When
        distance = calculate_haversine_distance(lat, lon, lat, lon)
        
        # Then
        assert distance == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
