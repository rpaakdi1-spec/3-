"""
주문 API 테스트
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta


class TestOrdersAPI:
    """주문 API 테스트 클래스"""
    
    def test_create_order(self, client: TestClient, auth_headers, test_client_data):
        """주문 생성 테스트"""
        response = client.post(
            "/api/v1/orders/",
            headers=auth_headers,
            json={
                "order_date": datetime.now().isoformat(),
                "pickup_client_id": test_client_data.id,
                "delivery_client_id": test_client_data.id,
                "pickup_address": "서울시 강남구 픽업로 123",
                "delivery_address": "서울시 서초구 배송로 456",
                "pallet_count": 10,
                "weight_kg": 500,
                "volume_cbm": 15.5,
                "product_name": "냉동식품",
                "temperature_zone": "FROZEN",
                "requested_delivery_date": (datetime.now() + timedelta(days=1)).isoformat()
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "order_number" in data
        assert data["pallet_count"] == 10
        assert data["product_name"] == "냉동식품"
    
    def test_get_orders(self, client: TestClient, auth_headers, test_order):
        """주문 목록 조회 테스트"""
        response = client.get("/api/v1/orders/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_order_by_id(self, client: TestClient, auth_headers, test_order):
        """주문 상세 조회 테스트"""
        response = client.get(f"/api/v1/orders/{test_order.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_order.id
        assert data["order_number"] == test_order.order_number
    
    def test_get_nonexistent_order(self, client: TestClient, auth_headers):
        """존재하지 않는 주문 조회 테스트"""
        response = client.get("/api/v1/orders/99999", headers=auth_headers)
        assert response.status_code == 404
    
    def test_update_order(self, client: TestClient, auth_headers, test_order):
        """주문 수정 테스트"""
        response = client.put(
            f"/api/v1/orders/{test_order.id}",
            headers=auth_headers,
            json={
                "pallet_count": 20,
                "product_name": "수정된 상품"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["pallet_count"] == 20
        assert data["product_name"] == "수정된 상품"
    
    def test_delete_order(self, client: TestClient, auth_headers, test_order):
        """주문 삭제 테스트"""
        response = client.delete(f"/api/v1/orders/{test_order.id}", headers=auth_headers)
        assert response.status_code == 200
        
        # 삭제 확인
        response = client.get(f"/api/v1/orders/{test_order.id}", headers=auth_headers)
        assert response.status_code == 404
    
    def test_create_order_unauthorized(self, client: TestClient, test_client_data):
        """인증 없이 주문 생성 실패 테스트"""
        response = client.post(
            "/api/v1/orders/",
            json={
                "order_date": datetime.now().isoformat(),
                "pickup_client_id": test_client_data.id,
                "delivery_client_id": test_client_data.id,
                "pallet_count": 10,
                "product_name": "테스트 상품"
            }
        )
        assert response.status_code == 401


@pytest.mark.database
class TestOrdersDatabase:
    """주문 데이터베이스 테스트"""
    
    def test_order_creation(self, db: Session, test_client_data):
        """주문 생성 데이터베이스 테스트"""
        from app.models.order import Order, OrderStatus, TemperatureZone
        
        order = Order(
            order_number="ORD-TEST-001",
            order_date=datetime.now(),
            pickup_client_id=test_client_data.id,
            delivery_client_id=test_client_data.id,
            pallet_count=10,
            product_name="테스트 상품",
            temperature_zone=TemperatureZone.FROZEN,
            status=OrderStatus.PENDING
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        
        assert order.id is not None
        assert order.order_number == "ORD-TEST-001"
        assert order.status == OrderStatus.PENDING
    
    def test_order_relationships(self, db: Session, test_order, test_client_data):
        """주문 관계 테스트"""
        assert test_order.pickup_client is not None
        assert test_order.delivery_client is not None
        assert test_order.pickup_client.id == test_client_data.id
