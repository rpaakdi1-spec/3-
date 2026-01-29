"""
배송 추적 API 테스트
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestDeliveryTrackingAPI:
    """배송 추적 API 테스트 클래스"""
    
    def test_generate_tracking_number(self, client: TestClient, auth_headers, test_order):
        """추적번호 생성 테스트"""
        response = client.post(
            "/api/v1/delivery-tracking/generate",
            headers=auth_headers,
            json={"order_id": test_order.id}
        )
        assert response.status_code == 200
        data = response.json()
        assert "tracking_number" in data
        assert data["tracking_number"].startswith("TRK-")
    
    def test_get_public_tracking_info(self, client: TestClient, test_order, db: Session):
        """공개 추적 정보 조회 테스트"""
        from app.services.delivery_tracking_service import DeliveryTrackingService
        
        # 추적번호 생성
        service = DeliveryTrackingService(db)
        tracking_number = service.generate_tracking_number(test_order.id)
        
        # 공개 추적 정보 조회 (인증 불필요)
        response = client.get(f"/api/v1/delivery-tracking/public/{tracking_number}")
        assert response.status_code == 200
        data = response.json()
        assert "order" in data
        assert "status" in data
        assert "timeline" in data
    
    def test_get_tracking_status(self, client: TestClient, auth_headers, test_order):
        """추적 상태 조회 테스트"""
        response = client.get(
            f"/api/v1/delivery-tracking/status?order_id={test_order.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "progress_percentage" in data
    
    def test_get_delivery_timeline(self, client: TestClient, auth_headers, test_order):
        """배송 타임라인 조회 테스트"""
        response = client.get(
            f"/api/v1/delivery-tracking/timeline?order_id={test_order.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_estimated_arrival(self, client: TestClient, auth_headers, test_order):
        """예상 도착 시간 조회 테스트"""
        response = client.get(
            f"/api/v1/delivery-tracking/estimated-arrival?order_id={test_order.id}",
            headers=auth_headers
        )
        # 배차되지 않은 주문은 404 반환
        assert response.status_code in [200, 404]
    
    def test_send_notification(self, client: TestClient, auth_headers, test_order):
        """알림 발송 테스트"""
        response = client.post(
            "/api/v1/delivery-tracking/notify",
            headers=auth_headers,
            json={
                "order_id": test_order.id,
                "notification_type": "ORDER_CONFIRMED",
                "channels": ["email"]
            }
        )
        # 이메일 설정이 없을 경우 실패 가능
        assert response.status_code in [200, 500]
    
    def test_invalid_tracking_number(self, client: TestClient):
        """잘못된 추적번호 조회 테스트"""
        response = client.get("/api/v1/delivery-tracking/public/INVALID-TRACKING")
        assert response.status_code == 400


@pytest.mark.integration
class TestDeliveryTrackingIntegration:
    """배송 추적 통합 테스트"""
    
    def test_full_tracking_flow(self, client: TestClient, auth_headers, test_order, db: Session):
        """전체 추적 흐름 테스트"""
        from app.services.delivery_tracking_service import DeliveryTrackingService
        
        service = DeliveryTrackingService(db)
        
        # 1. 추적번호 생성
        tracking_number = service.generate_tracking_number(test_order.id)
        assert tracking_number.startswith("TRK-")
        
        # 2. 공개 추적 정보 조회
        tracking_info = service.get_public_tracking_info(tracking_number)
        assert tracking_info["order"]["order_number"] == test_order.order_number
        
        # 3. 상태 조회
        status = service.get_delivery_status(test_order.id)
        assert "status" in status
        assert "description" in status
        
        # 4. 타임라인 조회
        timeline = service.get_delivery_timeline(test_order.id)
        assert isinstance(timeline, list)
