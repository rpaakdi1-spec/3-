# Python 예제 코드

이 페이지는 Python을 사용하여 Cold Chain System API를 호출하는 실제 예제 코드를 제공합니다.

---

## 📦 필수 라이브러리 설치

```bash
pip install requests python-dotenv
```

---

## 🔐 인증 및 토큰 관리

### 기본 클라이언트 클래스

```python
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

class ColdChainAPIClient:
    """Cold Chain System API Client"""
    
    def __init__(self, base_url=None, username=None, password=None):
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8000")
        self.username = username or os.getenv("API_USERNAME")
        self.password = password or os.getenv("API_PASSWORD")
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
    
    def login(self):
        """로그인하여 토큰 발급"""
        url = f"{self.base_url}/api/v1/auth/login"
        response = requests.post(url, json={
            "username": self.username,
            "password": self.password
        })
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            expires_in = data["expires_in"]
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            print("✅ 로그인 성공")
            return True
        else:
            print(f"❌ 로그인 실패: {response.status_code}")
            print(response.json())
            return False
    
    def refresh_access_token(self):
        """액세스 토큰 갱신"""
        url = f"{self.base_url}/api/v1/auth/refresh"
        response = requests.post(url, json={
            "refresh_token": self.refresh_token
        })
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            expires_in = data["expires_in"]
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            print("✅ 토큰 갱신 성공")
            return True
        else:
            print(f"❌ 토큰 갱신 실패: {response.status_code}")
            return False
    
    def is_token_expired(self):
        """토큰 만료 여부 확인"""
        if not self.token_expires_at:
            return True
        return datetime.now() >= self.token_expires_at
    
    def ensure_authenticated(self):
        """인증 상태 확인 및 자동 갱신"""
        if not self.access_token:
            return self.login()
        
        if self.is_token_expired():
            return self.refresh_access_token()
        
        return True
    
    def get_headers(self):
        """API 요청 헤더 반환"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def get(self, endpoint):
        """GET 요청"""
        self.ensure_authenticated()
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self.get_headers())
        return response
    
    def post(self, endpoint, data=None, json_data=None):
        """POST 요청"""
        self.ensure_authenticated()
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, data=data, json=json_data, headers=self.get_headers())
        return response
    
    def put(self, endpoint, data=None, json_data=None):
        """PUT 요청"""
        self.ensure_authenticated()
        url = f"{self.base_url}{endpoint}"
        response = requests.put(url, data=data, json=json_data, headers=self.get_headers())
        return response
    
    def delete(self, endpoint):
        """DELETE 요청"""
        self.ensure_authenticated()
        url = f"{self.base_url}{endpoint}"
        response = requests.delete(url, headers=self.get_headers())
        return response
```

---

## 📊 대시보드 데이터 조회

```python
def get_dashboard_stats():
    """대시보드 통계 조회"""
    client = ColdChainAPIClient()
    
    if not client.login():
        return None
    
    response = client.get("/api/v1/analytics/dashboard")
    
    if response.status_code == 200:
        data = response.json()
        print("📊 대시보드 통계:")
        print(f"  - 활성 배차: {data['active_dispatches']}")
        print(f"  - 오늘 완료: {data['completed_today']}")
        print(f"  - 대기 주문: {data['pending_orders']}")
        print(f"  - 운행 중 차량: {data['vehicles_in_transit']}")
        print(f"  - 온도 알림: {data['temperature_alerts']}")
        print(f"  - 평균 배송 시간: {data['avg_delivery_time_minutes']:.1f}분")
        print(f"  - 차량 가동률: {data['fleet_utilization_percent']:.1f}%")
        print(f"  - 정시 배송률: {data['on_time_delivery_rate']:.1f}%")
        return data
    else:
        print(f"❌ 오류: {response.status_code}")
        print(response.json())
        return None

# 실행
if __name__ == "__main__":
    get_dashboard_stats()
```

---

## 🤖 ML 모델 - 배송 시간 예측

```python
def predict_delivery_time(distance_km, traffic_level, vehicle_type, temperature_type):
    """배송 시간 예측"""
    client = ColdChainAPIClient()
    client.login()
    
    response = client.post("/api/v1/ml/predict/delivery-time", json_data={
        "distance_km": distance_km,
        "traffic_level": traffic_level,
        "vehicle_type": vehicle_type,
        "temperature_type": temperature_type,
        "time_of_day": "afternoon",
        "day_of_week": "monday"
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"📦 배송 시간 예측:")
        print(f"  - 예상 시간: {data['predicted_time_minutes']:.1f}분")
        print(f"  - 신뢰 구간: {data['confidence_interval_lower']:.1f} ~ {data['confidence_interval_upper']:.1f}분")
        print(f"  - 모델 버전: {data['model_version']}")
        return data
    else:
        print(f"❌ 오류: {response.status_code}")
        return None

# 실행 예제
if __name__ == "__main__":
    predict_delivery_time(
        distance_km=25.5,
        traffic_level="moderate",
        vehicle_type="refrigerated_truck",
        temperature_type="냉장"
    )
```

---

## 📈 분석 - 월간 트렌드 조회

```python
from datetime import datetime, timedelta

def get_monthly_trends():
    """월간 트렌드 분석"""
    client = ColdChainAPIClient()
    client.login()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    response = client.get(
        f"/api/v1/analytics/trends?"
        f"start_date={start_date.strftime('%Y-%m-%d')}&"
        f"end_date={end_date.strftime('%Y-%m-%d')}&"
        f"group_by=daily"
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"📈 월간 트렌드 ({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}):")
        
        trends = data.get("trends", [])
        for trend in trends[:5]:  # 최근 5일
            print(f"  - {trend['date']}: {trend['total_orders']}건 주문, "
                  f"{trend['total_deliveries']}건 배송, "
                  f"평균 {trend['avg_delivery_time_minutes']:.1f}분")
        
        return data
    else:
        print(f"❌ 오류: {response.status_code}")
        return None

if __name__ == "__main__":
    get_monthly_trends()
```

---

## 🚚 실시간 차량 모니터링

```python
import time

def monitor_vehicle_realtime(vehicle_id, duration_seconds=60):
    """실시간 차량 모니터링 (폴링)"""
    client = ColdChainAPIClient()
    client.login()
    
    print(f"🚚 차량 #{vehicle_id} 실시간 모니터링 시작 ({duration_seconds}초)...")
    
    start_time = time.time()
    
    while time.time() - start_time < duration_seconds:
        response = client.get(f"/api/v1/realtime/monitor?vehicle_ids={vehicle_id}")
        
        if response.status_code == 200:
            data = response.json()
            vehicles = data.get("vehicles", [])
            
            if vehicles:
                vehicle = vehicles[0]
                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')}")
                print(f"  📍 위치: ({vehicle['latitude']:.6f}, {vehicle['longitude']:.6f})")
                print(f"  🌡️  온도: {vehicle['temperature']}°C")
                print(f"  🚗 속도: {vehicle['speed']} km/h")
                print(f"  🔋 배터리: {vehicle['battery_level']}%")
                
                # 알림 확인
                alerts = vehicle.get("alerts", [])
                if alerts:
                    print("  ⚠️  알림:")
                    for alert in alerts:
                        print(f"     - [{alert['severity']}] {alert['message']}")
        
        time.sleep(5)  # 5초마다 폴링
    
    print("\n✅ 모니터링 종료")

if __name__ == "__main__":
    monitor_vehicle_realtime(vehicle_id=1, duration_seconds=30)
```

---

## 📊 리포트 생성 및 다운로드

```python
def generate_dispatch_report(start_date, end_date, format="pdf"):
    """배차 리포트 생성"""
    client = ColdChainAPIClient()
    client.login()
    
    response = client.post(f"/api/v1/reports/dispatch/{format}", json_data={
        "start_date": start_date,
        "end_date": end_date,
        "template": "detailed"
    })
    
    if response.status_code == 200:
        # 파일 다운로드
        filename = f"dispatch_report_{start_date}_{end_date}.{format}"
        
        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"✅ 리포트 생성 완료: {filename}")
        print(f"📄 파일 크기: {len(response.content) / 1024:.2f} KB")
        return filename
    else:
        print(f"❌ 리포트 생성 실패: {response.status_code}")
        return None

if __name__ == "__main__":
    generate_dispatch_report(
        start_date="2026-01-01",
        end_date="2026-01-31",
        format="pdf"
    )
```

---

## 🔔 FCM 푸시 알림 전송

```python
def send_push_notification(user_id, title, body, data=None):
    """푸시 알림 전송"""
    client = ColdChainAPIClient()
    client.login()
    
    response = client.post("/api/v1/notifications/send-notification", json_data={
        "user_id": user_id,
        "title": title,
        "body": body,
        "data": data or {},
        "priority": "high"
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 푸시 알림 전송 성공")
        print(f"  - 메시지 ID: {result.get('message_id')}")
        return result
    else:
        print(f"❌ 푸시 알림 전송 실패: {response.status_code}")
        return None

if __name__ == "__main__":
    send_push_notification(
        user_id=1,
        title="배차 할당 알림",
        body="새로운 배차가 할당되었습니다. (#D-2026-0123)",
        data={
            "dispatch_id": 123,
            "action": "view_dispatch"
        }
    )
```

---

## 🔒 2FA 활성화 예제

```python
import pyotp

def enable_2fa():
    """2FA 활성화"""
    client = ColdChainAPIClient()
    client.login()
    
    # 2FA 활성화 요청
    response = client.post("/api/v1/security/2fa/enable")
    
    if response.status_code == 200:
        data = response.json()
        secret = data["secret"]
        qr_code_url = data["qr_code_url"]
        backup_codes = data["backup_codes"]
        
        print("✅ 2FA 활성화 준비:")
        print(f"  - Secret Key: {secret}")
        print(f"  - QR Code URL: {client.base_url}{qr_code_url}")
        print(f"  - 백업 코드:")
        for code in backup_codes:
            print(f"     {code}")
        
        # TOTP 생성 (테스트용)
        totp = pyotp.TOTP(secret)
        current_code = totp.now()
        print(f"\n  - 현재 TOTP 코드: {current_code}")
        
        # 검증
        verify_response = client.post("/api/v1/security/2fa/verify", json_data={
            "token": current_code
        })
        
        if verify_response.status_code == 200:
            print("✅ 2FA 활성화 완료!")
        else:
            print("❌ 2FA 검증 실패")
    else:
        print(f"❌ 2FA 활성화 실패: {response.status_code}")

if __name__ == "__main__":
    enable_2fa()
```

---

## 📚 완전한 예제 스크립트

모든 기능을 통합한 예제:

```python
"""
Cold Chain System API - 완전한 사용 예제

Usage:
    python cold_chain_example.py
"""

from datetime import datetime, timedelta
import time

def main():
    """메인 함수"""
    client = ColdChainAPIClient(
        base_url="http://localhost:8000",
        username="demo_user",
        password="SecurePass123!"
    )
    
    # 1. 로그인
    print("=" * 50)
    print("1️⃣  로그인")
    print("=" * 50)
    if not client.login():
        return
    
    # 2. 대시보드 조회
    print("\n" + "=" * 50)
    print("2️⃣  대시보드 조회")
    print("=" * 50)
    dashboard = client.get("/api/v1/analytics/dashboard")
    print(dashboard.json())
    
    # 3. 배송 시간 예측
    print("\n" + "=" * 50)
    print("3️⃣  배송 시간 예측")
    print("=" * 50)
    prediction = client.post("/api/v1/ml/predict/delivery-time", json_data={
        "distance_km": 30.0,
        "traffic_level": "moderate",
        "vehicle_type": "refrigerated_truck",
        "temperature_type": "냉장"
    })
    print(prediction.json())
    
    # 4. 실시간 모니터링
    print("\n" + "=" * 50)
    print("4️⃣  실시간 차량 모니터링 (10초)")
    print("=" * 50)
    monitor_vehicle_realtime(vehicle_id=1, duration_seconds=10)
    
    print("\n✅ 모든 작업 완료!")

if __name__ == "__main__":
    main()
```

---

## 📝 .env 파일 예제

```bash
# .env
API_BASE_URL=http://localhost:8000
API_USERNAME=your_username
API_PASSWORD=your_password
```

---

## 🎓 다음 단계

- [JavaScript 예제](javascript-examples.md)
- [cURL 예제](curl-examples.md)
- [API 레퍼런스](../api-reference/index.md)
