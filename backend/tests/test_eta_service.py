"""
단위 테스트 - ETA 서비스
"""

import pytest
from datetime import datetime, time
from app.services.eta_service import ETAService, LocationStop


class TestETAService:
    """ETA 서비스 테스트"""
    
    def setup_method(self):
        """각 테스트 전에 실행"""
        self.eta_service = ETAService(average_speed_kmh=40, traffic_factor=1.0)
    
    def test_estimate_delivery_time(self):
        """단일 배송 ETA 계산 테스트"""
        # Given
        current_location = LocationStop(1, 'depot', 37.5, 127.0, service_time_minutes=0)
        destination = LocationStop(2, 'delivery', 37.6, 127.1, service_time_minutes=20)
        distance_km = 10.0
        current_time = datetime(2026, 1, 19, 9, 0)
        
        # When
        eta = self.eta_service.estimate_delivery_time(
            current_location, destination, distance_km, current_time
        )
        
        # Then
        # 10km / 40km/h = 0.25시간 = 15분
        expected = current_time.replace(hour=9, minute=15)
        assert eta == expected
    
    def test_calculate_route_duration(self):
        """경로 소요 시간 계산 테스트"""
        # Given
        distance_km = 100
        num_stops = 5
        avg_service_time = 30  # minutes
        
        # When
        duration = self.eta_service.calculate_route_duration(
            distance_km, num_stops, avg_service_time
        )
        
        # Then
        # 100km / 40km/h = 2.5시간 = 150분
        # 작업 시간: 5 stops * 30분 = 150분
        # 총: 300분
        assert duration == 300.0
    
    def test_calculate_eta_simple_route(self):
        """간단한 경로 ETA 계산 테스트"""
        # Given
        start_time = datetime(2026, 1, 19, 9, 0)
        route_stops = [
            LocationStop(1, 'depot', 37.5, 127.0, 0),
            LocationStop(2, 'pickup', 37.6, 127.1, 30),
            LocationStop(3, 'delivery', 37.7, 127.2, 20)
        ]
        distance_matrix = [
            [0, 10, 20],
            [10, 0, 8],
            [20, 8, 0]
        ]
        
        # When
        results = self.eta_service.calculate_eta(
            start_time, route_stops, distance_matrix
        )
        
        # Then
        assert len(results) == 3
        assert results[0].location_type == 'depot'
        assert results[1].location_type == 'pickup'
        assert results[2].location_type == 'delivery'
        
        # 첫 번째 stop (depot): 즉시 도착
        assert results[0].estimated_arrival_time == start_time
        
        # 두 번째 stop (pickup): 10km / 40km/h = 15분
        assert results[1].cumulative_distance_km == 10.0
        assert results[1].cumulative_duration_minutes == 45.0  # 15분 이동 + 30분 작업
    
    def test_calculate_eta_with_time_windows(self):
        """Time Window가 있는 경로 ETA 계산 테스트"""
        # Given
        start_time = datetime(2026, 1, 19, 8, 0)
        route_stops = [
            LocationStop(1, 'depot', 37.5, 127.0, 0),
            LocationStop(2, 'pickup', 37.6, 127.1, 30, '09:00', '12:00'),  # 9시 이후만 가능
        ]
        distance_matrix = [
            [0, 10],
            [10, 0]
        ]
        
        # When
        results = self.eta_service.calculate_eta(
            start_time, route_stops, distance_matrix
        )
        
        # Then
        # 8:00 출발 + 15분 이동 = 8:15 도착
        # 하지만 Time Window가 9:00부터이므로 9:00까지 대기
        assert results[1].estimated_arrival_time.time() == time(9, 0)
        assert results[1].is_within_time_window is True
    
    def test_traffic_factor(self):
        """교통 혼잡도 반영 테스트"""
        # Given
        distance_km = 10.0
        
        # When - 정상 교통
        eta_service_normal = ETAService(average_speed_kmh=40, traffic_factor=1.0)
        time_normal = eta_service_normal._calculate_travel_time(distance_km)
        
        # When - 혼잡 교통
        eta_service_congested = ETAService(average_speed_kmh=40, traffic_factor=1.5)
        time_congested = eta_service_congested._calculate_travel_time(distance_km)
        
        # Then
        assert time_congested > time_normal
        assert time_congested == time_normal * 1.5
    
    def test_time_window_violation(self):
        """Time Window 위반 테스트"""
        # Given
        start_time = datetime(2026, 1, 19, 14, 0)  # 14:00 출발
        route_stops = [
            LocationStop(1, 'depot', 37.5, 127.0, 0),
            LocationStop(2, 'delivery', 37.6, 127.1, 20, '09:00', '13:00'),  # 13:00까지만
        ]
        distance_matrix = [
            [0, 10],
            [10, 0]
        ]
        
        # When
        results = self.eta_service.calculate_eta(
            start_time, route_stops, distance_matrix
        )
        
        # Then
        # 14:00 + 15분 = 14:15 도착 (13:00 이후)
        assert results[1].is_within_time_window is False
        assert results[1].time_window_violation_minutes > 0
    
    def test_get_eta_summary(self):
        """ETA 요약 테스트"""
        # Given
        start_time = datetime(2026, 1, 19, 9, 0)
        route_stops = [
            LocationStop(1, 'depot', 37.5, 127.0, 0),
            LocationStop(2, 'pickup', 37.6, 127.1, 30),
            LocationStop(3, 'delivery', 37.7, 127.2, 20)
        ]
        distance_matrix = [
            [0, 10, 20],
            [10, 0, 8],
            [20, 8, 0]
        ]
        
        results = self.eta_service.calculate_eta(
            start_time, route_stops, distance_matrix
        )
        
        # When
        summary = self.eta_service.get_eta_summary(results)
        
        # Then
        assert summary['total_stops'] == 3
        assert summary['total_distance_km'] == 18.0  # 10 + 8
        assert summary['time_window_violations'] == 0
        assert summary['on_time_rate'] == 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
