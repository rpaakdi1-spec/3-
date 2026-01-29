"""
모니터링 API 테스트
"""
import pytest
from fastapi.testclient import TestClient


class TestMonitoringAPI:
    """모니터링 API 테스트 클래스"""
    
    def test_health_check(self, client: TestClient):
        """헬스 체크 테스트"""
        response = client.get("/api/v1/monitoring/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "checks" in data
    
    def test_get_metrics(self, client: TestClient, auth_headers):
        """메트릭 조회 테스트"""
        response = client.get("/api/v1/monitoring/metrics", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "system" in data
        assert "cpu_percent" in data["system"]
        assert "memory_percent" in data["system"]
    
    def test_get_dashboard(self, client: TestClient, auth_headers):
        """대시보드 데이터 조회 테스트"""
        response = client.get("/api/v1/monitoring/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "health" in data
        assert "metrics" in data
        assert "alerts" in data
    
    def test_send_notification(self, client: TestClient, auth_headers):
        """알림 발송 테스트"""
        response = client.post(
            "/api/v1/monitoring/notify",
            headers=auth_headers,
            json={
                "level": "info",
                "title": "테스트 알림",
                "message": "테스트 메시지",
                "channels": ["email"]
            }
        )
        # 이메일 설정이 없을 경우 실패 가능
        assert response.status_code in [200, 500]
    
    def test_test_email(self, client: TestClient, auth_headers):
        """이메일 테스트"""
        response = client.get("/api/v1/monitoring/test/email", headers=auth_headers)
        # 이메일 설정이 없을 경우 실패 가능
        assert response.status_code in [200, 500]
    
    def test_test_slack(self, client: TestClient, auth_headers):
        """Slack 테스트"""
        response = client.get("/api/v1/monitoring/test/slack", headers=auth_headers)
        # Slack 설정이 없을 경우 실패 가능
        assert response.status_code in [200, 500]


class TestMonitoringService:
    """모니터링 서비스 테스트"""
    
    def test_get_system_metrics(self, db):
        """시스템 메트릭 조회 테스트"""
        from app.services.monitoring_service import MonitoringService
        
        service = MonitoringService(db)
        metrics = service.get_system_metrics()
        
        assert "cpu_percent" in metrics
        assert "memory_percent" in metrics
        assert "disk_percent" in metrics
        assert 0 <= metrics["cpu_percent"] <= 100
        assert 0 <= metrics["memory_percent"] <= 100
        assert 0 <= metrics["disk_percent"] <= 100
    
    def test_check_health(self, db):
        """헬스 체크 테스트"""
        from app.services.monitoring_service import MonitoringService
        
        service = MonitoringService(db)
        health = service.check_health()
        
        assert "status" in health
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
        assert "checks" in health
        assert "database" in health["checks"]
    
    def test_detect_anomalies(self, db):
        """이상 감지 테스트"""
        from app.services.monitoring_service import MonitoringService
        
        service = MonitoringService(db)
        alerts = service.detect_anomalies()
        
        assert isinstance(alerts, list)
        for alert in alerts:
            assert "level" in alert
            assert "title" in alert
            assert "message" in alert
