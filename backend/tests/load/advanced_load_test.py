"""
Advanced Load Testing Scenarios with Locust

Tests various user scenarios and API endpoints under load
"""

import random
import json
from locust import HttpUser, task, between, events
from datetime import datetime, timedelta


class AdvancedColdChainUser(HttpUser):
    """
    Advanced user behavior simulation for Cold Chain System
    
    Simulates realistic user patterns with different task weights
    """
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a user starts - login"""
        self.client.verify = False  # Disable SSL verification for testing
        
        # Login
        response = self.client.post("/api/v1/auth/login", json={
            "username": f"loadtest_user_{random.randint(1, 100)}",
            "password": "LoadTest123!"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        else:
            # Use test token if login fails
            self.token = "test_token"
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
    
    @task(10)
    def view_dashboard(self):
        """View dashboard - Most frequent action"""
        self.client.get(
            "/api/v1/analytics/dashboard",
            headers=self.headers,
            name="GET Dashboard"
        )
    
    @task(8)
    def list_orders(self):
        """List orders with pagination"""
        page = random.randint(1, 5)
        self.client.get(
            f"/api/v1/orders?page={page}&page_size=20",
            headers=self.headers,
            name="GET Orders List"
        )
    
    @task(6)
    def view_order_detail(self):
        """View specific order details"""
        order_id = random.randint(1, 1000)
        self.client.get(
            f"/api/v1/orders/{order_id}",
            headers=self.headers,
            name="GET Order Detail"
        )
    
    @task(5)
    def create_order(self):
        """Create new order"""
        order_data = {
            "client_id": random.randint(1, 50),
            "pickup_client_id": random.randint(1, 50),
            "delivery_client_id": random.randint(1, 50),
            "temperature_type": random.choice(["냉동", "냉장", "상온"]),
            "pallets": random.randint(1, 30),
            "weight_kg": random.uniform(100, 5000),
            "pickup_location": "Seoul, Korea",
            "delivery_location": "Busan, Korea",
            "notes": f"Load test order created at {datetime.now().isoformat()}"
        }
        
        self.client.post(
            "/api/v1/orders",
            json=order_data,
            headers=self.headers,
            name="POST Create Order"
        )
    
    @task(7)
    def list_dispatches(self):
        """List dispatches"""
        page = random.randint(1, 5)
        status = random.choice(["pending", "assigned", "in_progress", "completed", ""])
        
        params = f"page={page}&page_size=20"
        if status:
            params += f"&status={status}"
        
        self.client.get(
            f"/api/v1/dispatches?{params}",
            headers=self.headers,
            name="GET Dispatches List"
        )
    
    @task(4)
    def view_dispatch_detail(self):
        """View dispatch details"""
        dispatch_id = random.randint(1, 500)
        self.client.get(
            f"/api/v1/dispatches/{dispatch_id}",
            headers=self.headers,
            name="GET Dispatch Detail"
        )
    
    @task(3)
    def optimize_dispatch(self):
        """Trigger dispatch optimization"""
        order_ids = random.sample(range(1, 100), k=random.randint(3, 10))
        
        self.client.post(
            "/api/v1/dispatches/optimize",
            json={"order_ids": order_ids},
            headers=self.headers,
            name="POST Optimize Dispatch"
        )
    
    @task(6)
    def list_vehicles(self):
        """List vehicles"""
        self.client.get(
            "/api/v1/vehicles",
            headers=self.headers,
            name="GET Vehicles List"
        )
    
    @task(3)
    def view_vehicle_detail(self):
        """View vehicle details"""
        vehicle_id = random.randint(1, 100)
        self.client.get(
            f"/api/v1/vehicles/{vehicle_id}",
            headers=self.headers,
            name="GET Vehicle Detail"
        )
    
    @task(5)
    def view_analytics_trends(self):
        """View analytics trends"""
        days = random.choice([7, 30, 90])
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        self.client.get(
            f"/api/v1/analytics/trends?start_date={start_date}&end_date={end_date}&group_by=daily",
            headers=self.headers,
            name="GET Analytics Trends"
        )
    
    @task(4)
    def view_performance_metrics(self):
        """View performance metrics"""
        self.client.get(
            "/api/v1/analytics/performance",
            headers=self.headers,
            name="GET Performance Metrics"
        )
    
    @task(2)
    def generate_report(self):
        """Generate dispatch report"""
        start_date = (datetime.now() - timedelta(days=30)).date()
        end_date = datetime.now().date()
        
        self.client.post(
            "/api/v1/reports/dispatch/excel",
            json={
                "start_date": str(start_date),
                "end_date": str(end_date),
                "template": "standard"
            },
            headers=self.headers,
            name="POST Generate Report"
        )
    
    @task(3)
    def ml_predict_delivery_time(self):
        """ML: Predict delivery time"""
        self.client.post(
            "/api/v1/ml/predict/delivery-time",
            json={
                "distance_km": random.uniform(10, 200),
                "traffic_level": random.choice(["light", "moderate", "heavy"]),
                "vehicle_type": random.choice(["refrigerated_truck", "frozen_truck"]),
                "temperature_type": random.choice(["냉동", "냉장", "상온"]),
                "time_of_day": random.choice(["morning", "afternoon", "evening"]),
                "day_of_week": random.choice(["monday", "tuesday", "wednesday", "thursday", "friday"])
            },
            headers=self.headers,
            name="POST ML Predict Delivery Time"
        )
    
    @task(2)
    def ml_forecast_demand(self):
        """ML: Forecast demand"""
        self.client.post(
            "/api/v1/ml/forecast/demand",
            json={
                "forecast_days": random.choice([7, 14, 30]),
                "temperature_type": random.choice(["냉동", "냉장", "상온", None])
            },
            headers=self.headers,
            name="POST ML Forecast Demand"
        )
    
    @task(4)
    def realtime_monitoring(self):
        """Real-time monitoring endpoint"""
        vehicle_ids = random.sample(range(1, 50), k=random.randint(1, 5))
        
        self.client.get(
            f"/api/v1/realtime/monitor?vehicle_ids={','.join(map(str, vehicle_ids))}",
            headers=self.headers,
            name="GET Realtime Monitor"
        )
    
    @task(3)
    def cache_stats(self):
        """View cache statistics"""
        self.client.get(
            "/api/v1/performance/cache-stats",
            headers=self.headers,
            name="GET Cache Stats"
        )


class AdminUser(HttpUser):
    """
    Admin-specific actions
    """
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Admin login"""
        self.client.verify = False
        
        response = self.client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "Admin123!"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        else:
            self.token = "admin_token"
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
    
    @task(5)
    def view_system_performance(self):
        """View system performance metrics"""
        self.client.get(
            "/api/v1/performance/system",
            headers=self.headers,
            name="GET System Performance"
        )
    
    @task(3)
    def view_query_stats(self):
        """View query statistics"""
        self.client.get(
            "/api/v1/performance/query-stats",
            headers=self.headers,
            name="GET Query Stats"
        )
    
    @task(2)
    def view_audit_logs(self):
        """View audit logs"""
        page = random.randint(1, 10)
        self.client.get(
            f"/api/v1/security/audit-logs?page={page}&page_size=50",
            headers=self.headers,
            name="GET Audit Logs"
        )
    
    @task(3)
    def view_websocket_stats(self):
        """View WebSocket connection statistics"""
        self.client.get(
            "/ws/stats",
            headers=self.headers,
            name="GET WebSocket Stats"
        )
    
    @task(2)
    def flush_cache(self):
        """Flush specific cache pattern"""
        patterns = ["orders:*", "dispatches:*", "dashboard:*"]
        pattern = random.choice(patterns)
        
        self.client.post(
            "/api/v1/performance/cache/flush",
            json={"pattern": pattern},
            headers=self.headers,
            name="POST Flush Cache"
        )


class MobileUser(HttpUser):
    """
    Mobile app user behavior simulation
    """
    
    wait_time = between(3, 8)
    
    def on_start(self):
        """Mobile user login"""
        self.client.verify = False
        
        response = self.client.post("/api/v1/auth/login", json={
            "username": f"driver_{random.randint(1, 50)}",
            "password": "Driver123!"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "ColdChain-Mobile/1.0 (iOS)"
            }
        else:
            self.token = "mobile_token"
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "ColdChain-Mobile/1.0 (iOS)"
            }
    
    @task(10)
    def my_dispatches(self):
        """View driver's assigned dispatches"""
        self.client.get(
            "/api/v1/dispatches?assigned_to_me=true&status=assigned,in_progress",
            headers=self.headers,
            name="GET My Dispatches"
        )
    
    @task(5)
    def update_location(self):
        """Update driver location (GPS)"""
        self.client.post(
            "/api/v1/tracking/location",
            json={
                "latitude": random.uniform(37.4, 37.6),
                "longitude": random.uniform(126.9, 127.1),
                "speed": random.uniform(0, 80),
                "heading": random.uniform(0, 360)
            },
            headers=self.headers,
            name="POST Update Location"
        )
    
    @task(3)
    def update_dispatch_status(self):
        """Update dispatch status"""
        dispatch_id = random.randint(1, 500)
        status = random.choice(["in_progress", "completed"])
        
        self.client.patch(
            f"/api/v1/dispatches/{dispatch_id}/status",
            json={"status": status},
            headers=self.headers,
            name="PATCH Update Dispatch Status"
        )
    
    @task(2)
    def register_fcm_token(self):
        """Register FCM token for push notifications"""
        self.client.post(
            "/api/v1/notifications/register-token",
            json={
                "token": f"fcm_token_{random.randint(10000, 99999)}",
                "device_type": random.choice(["ios", "android"])
            },
            headers=self.headers,
            name="POST Register FCM Token"
        )


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the test starts"""
    print("🚀 Load test starting...")
    print(f"Target host: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the test stops"""
    print("✅ Load test completed")
    
    # Print statistics
    stats = environment.stats
    print(f"\n📊 Test Results:")
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Total failures: {stats.total.num_failures}")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"Max response time: {stats.total.max_response_time:.2f}ms")
    print(f"Requests per second: {stats.total.current_rps:.2f}")
    
    # Check if test passed target metrics
    avg_response_time = stats.total.avg_response_time
    failure_rate = stats.total.num_failures / stats.total.num_requests if stats.total.num_requests > 0 else 0
    
    print(f"\n🎯 Target Metrics:")
    print(f"Average response time: {'✅' if avg_response_time < 200 else '❌'} {avg_response_time:.2f}ms (target: <200ms)")
    print(f"Error rate: {'✅' if failure_rate < 0.01 else '❌'} {failure_rate * 100:.2f}% (target: <1%)")
