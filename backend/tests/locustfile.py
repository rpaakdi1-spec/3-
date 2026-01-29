"""
성능 테스트 (Locust)
"""
from locust import HttpUser, task, between
import random
from datetime import datetime, timedelta


class ColdChainUser(HttpUser):
    """Cold Chain 시스템 사용자 시뮬레이션"""
    
    wait_time = between(1, 3)  # 1-3초 대기
    
    def on_start(self):
        """시작 시 로그인"""
        # 로그인
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testpassword123"
        })
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            self.headers = {}
    
    @task(3)
    def get_orders(self):
        """주문 목록 조회"""
        self.client.get("/api/v1/orders/", headers=self.headers)
    
    @task(2)
    def get_dispatches(self):
        """배차 목록 조회"""
        self.client.get("/api/v1/dispatches/", headers=self.headers)
    
    @task(2)
    def get_vehicles(self):
        """차량 목록 조회"""
        self.client.get("/api/v1/vehicles/", headers=self.headers)
    
    @task(1)
    def create_order(self):
        """주문 생성"""
        self.client.post("/api/v1/orders/", headers=self.headers, json={
            "order_date": datetime.now().isoformat(),
            "pickup_client_id": random.randint(1, 10),
            "delivery_client_id": random.randint(1, 10),
            "pallet_count": random.randint(5, 30),
            "weight_kg": random.randint(100, 1000),
            "product_name": f"테스트 상품 {random.randint(1, 100)}",
            "temperature_zone": random.choice(["FROZEN", "REFRIGERATED", "AMBIENT"]),
            "requested_delivery_date": (datetime.now() + timedelta(days=1)).isoformat()
        })
    
    @task(1)
    def health_check(self):
        """헬스 체크"""
        self.client.get("/api/v1/monitoring/health")
    
    @task(1)
    def get_tracking_status(self):
        """배송 추적 상태 조회"""
        order_id = random.randint(1, 100)
        self.client.get(f"/api/v1/delivery-tracking/status?order_id={order_id}", headers=self.headers)


class AdminUser(HttpUser):
    """관리자 사용자 시뮬레이션"""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """시작 시 관리자 로그인"""
        response = self.client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "adminpassword123"
        })
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            self.headers = {}
    
    @task(2)
    def get_dashboard(self):
        """대시보드 조회"""
        self.client.get("/api/v1/monitoring/dashboard", headers=self.headers)
    
    @task(1)
    def get_metrics(self):
        """메트릭 조회"""
        self.client.get("/api/v1/monitoring/metrics", headers=self.headers)
    
    @task(1)
    def get_analytics(self):
        """분석 데이터 조회"""
        self.client.get("/api/v1/analytics/", headers=self.headers)
    
    @task(1)
    def optimize_dispatch(self):
        """배차 최적화"""
        self.client.post("/api/v1/dispatches/optimize", headers=self.headers, json={
            "order_ids": [random.randint(1, 50) for _ in range(random.randint(3, 10))],
            "vehicle_id": random.randint(1, 10),
            "driver_id": random.randint(1, 10)
        })


class PublicUser(HttpUser):
    """공개 사용자 시뮬레이션 (배송 추적)"""
    
    wait_time = between(3, 7)
    
    @task
    def track_delivery(self):
        """배송 추적"""
        # 임의의 추적번호 생성 (실제로는 유효하지 않을 수 있음)
        tracking_number = f"TRK-20260127-{random.randint(10000000, 99999999):08d}"
        self.client.get(f"/api/v1/delivery-tracking/public/{tracking_number}")
