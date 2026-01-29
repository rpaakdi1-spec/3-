"""
배차 API 테스트
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime


class TestDispatchAPI:
    """배차 API 테스트 클래스"""
    
    def test_create_dispatch(self, client: TestClient, auth_headers, test_vehicle, test_driver):
        """배차 생성 테스트"""
        response = client.post(
            "/api/v1/dispatches/",
            headers=auth_headers,
            json={
                "dispatch_date": datetime.now().isoformat(),
                "vehicle_id": test_vehicle.id,
                "driver_id": test_driver.id,
                "order_ids": []
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "dispatch_number" in data
        assert data["vehicle_id"] == test_vehicle.id
        assert data["driver_id"] == test_driver.id
    
    def test_get_dispatches(self, client: TestClient, auth_headers, test_dispatch):
        """배차 목록 조회 테스트"""
        response = client.get("/api/v1/dispatches/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_dispatch_by_id(self, client: TestClient, auth_headers, test_dispatch):
        """배차 상세 조회 테스트"""
        response = client.get(f"/api/v1/dispatches/{test_dispatch.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_dispatch.id
        assert data["dispatch_number"] == test_dispatch.dispatch_number
    
    def test_update_dispatch_status(self, client: TestClient, auth_headers, test_dispatch):
        """배차 상태 수정 테스트"""
        response = client.put(
            f"/api/v1/dispatches/{test_dispatch.id}",
            headers=auth_headers,
            json={
                "status": "CONFIRMED"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "CONFIRMED"
    
    def test_optimize_dispatch(self, client: TestClient, auth_headers, test_order, test_vehicle, test_driver):
        """배차 최적화 테스트"""
        response = client.post(
            "/api/v1/dispatches/optimize",
            headers=auth_headers,
            json={
                "order_ids": [test_order.id],
                "vehicle_id": test_vehicle.id,
                "driver_id": test_driver.id
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "routes" in data or "dispatch_number" in data
    
    def test_delete_dispatch(self, client: TestClient, auth_headers, test_dispatch):
        """배차 삭제 테스트"""
        response = client.delete(f"/api/v1/dispatches/{test_dispatch.id}", headers=auth_headers)
        assert response.status_code == 200
        
        # 삭제 확인
        response = client.get(f"/api/v1/dispatches/{test_dispatch.id}", headers=auth_headers)
        assert response.status_code == 404


@pytest.mark.database
class TestDispatchDatabase:
    """배차 데이터베이스 테스트"""
    
    def test_dispatch_creation(self, db: Session, test_vehicle, test_driver):
        """배차 생성 데이터베이스 테스트"""
        from app.models.dispatch import Dispatch, DispatchStatus
        
        dispatch = Dispatch(
            dispatch_number="DISP-TEST-001",
            dispatch_date=datetime.now(),
            vehicle_id=test_vehicle.id,
            driver_id=test_driver.id,
            total_orders=0,
            total_pallets=0,
            total_weight_kg=0,
            status=DispatchStatus.DRAFT
        )
        db.add(dispatch)
        db.commit()
        db.refresh(dispatch)
        
        assert dispatch.id is not None
        assert dispatch.dispatch_number == "DISP-TEST-001"
        assert dispatch.status == DispatchStatus.DRAFT
    
    def test_dispatch_relationships(self, db: Session, test_dispatch, test_vehicle, test_driver):
        """배차 관계 테스트"""
        assert test_dispatch.vehicle is not None
        assert test_dispatch.driver is not None
        assert test_dispatch.vehicle.id == test_vehicle.id
        assert test_dispatch.driver.id == test_driver.id
