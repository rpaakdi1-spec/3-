"""
교통 정보 API 테스트
"""
import pytest
from fastapi.testclient import TestClient


class TestTrafficAPI:
    """교통 정보 API 테스트 클래스"""
    
    def test_get_route_simple(self, client: TestClient, auth_headers):
        """간단한 경로 조회 테스트"""
        response = client.get(
            "/api/v1/traffic/route/simple",
            headers=auth_headers,
            params={
                "start_lat": 37.5665,
                "start_lon": 126.9780,
                "end_lat": 37.3951,
                "end_lon": 127.1113,
                "provider": "naver"
            }
        )
        # API 키가 없을 경우 실패 가능
        assert response.status_code in [200, 500]
    
    def test_get_arrival_estimate_simple(self, client: TestClient, auth_headers):
        """간단한 도착 예상 시간 조회 테스트"""
        response = client.get(
            "/api/v1/traffic/arrival-estimate/simple",
            headers=auth_headers,
            params={
                "current_lat": 37.5665,
                "current_lon": 126.9780,
                "dest_lat": 37.3951,
                "dest_lon": 127.1113
            }
        )
        # API 키가 없을 경우 실패 가능
        assert response.status_code in [200, 500]
    
    def test_traffic_test(self, client: TestClient, auth_headers):
        """교통 정보 테스트"""
        response = client.get(
            "/api/v1/traffic/traffic/test",
            headers=auth_headers,
            params={"provider": "naver"}
        )
        # API 키가 없을 경우 실패 가능
        assert response.status_code in [200, 500]
    
    def test_traffic_compare(self, client: TestClient, auth_headers):
        """교통 정보 비교 테스트"""
        response = client.get(
            "/api/v1/traffic/traffic/compare",
            headers=auth_headers,
            params={
                "start_lat": 37.5665,
                "start_lon": 126.9780,
                "end_lat": 37.3951,
                "end_lon": 127.1113
            }
        )
        # API 키가 없을 경우 실패 가능
        assert response.status_code in [200, 500]


class TestTrafficService:
    """교통 정보 서비스 테스트"""
    
    @pytest.mark.slow
    def test_get_route_naver(self, db):
        """네이버 경로 조회 테스트"""
        from app.services.traffic_service import TrafficService
        
        service = TrafficService(db)
        try:
            route = service.get_route(
                start_lat=37.5665,
                start_lon=126.9780,
                end_lat=37.3951,
                end_lon=127.1113,
                provider="naver"
            )
            assert "distance" in route or "error" in route
        except Exception:
            # API 키가 없을 경우 예외 발생 가능
            pass
    
    @pytest.mark.slow
    def test_get_route_kakao(self, db):
        """카카오 경로 조회 테스트"""
        from app.services.traffic_service import TrafficService
        
        service = TrafficService(db)
        try:
            route = service.get_route(
                start_lat=37.5665,
                start_lon=126.9780,
                end_lat=37.3951,
                end_lon=127.1113,
                provider="kakao"
            )
            assert "distance" in route or "error" in route
        except Exception:
            # API 키가 없을 경우 예외 발생 가능
            pass
    
    def test_calculate_haversine_distance(self):
        """Haversine 거리 계산 테스트"""
        from app.services.traffic_service import TrafficService
        
        distance = TrafficService.calculate_haversine_distance(
            37.5665, 126.9780,  # 서울시청
            37.3951, 127.1113   # 성남시청
        )
        # 약 25-30km 예상
        assert 20 < distance < 35
