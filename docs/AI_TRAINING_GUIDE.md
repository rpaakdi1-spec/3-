# 🤖 UVIS AI 학습 가이드

> **목적**: 운영 데이터를 활용한 AI 모델 학습 및 배차 최적화

## 🗺️ 네이버 지도 API 자동 계산

**중요**: AI 학습 데이터 업로드 시, **거리(km)**와 **실제소요시간(분)**은 네이버 지도 API를 통해 **자동으로 계산**됩니다.

- 사용자는 **출발지주소**와 **도착지주소**만 입력하면 됩니다
- 시스템이 자동으로 주소를 좌표로 변환 후, 최적 경로의 거리/소요시간을 계산합니다
- API 미설정 시, 하버사인 공식 기반 시뮬레이션으로 대체됩니다

### 네이버 지도 API 설정 (선택사항)

`.env` 파일에 다음을 추가하세요:

```env
NAVER_MAP_CLIENT_ID=your_naver_client_id_here
NAVER_MAP_CLIENT_SECRET=your_naver_client_secret_here
```

**네이버 클라우드 플랫폼** (https://www.ncloud.com/)에서 발급 가능합니다.

---

## 📋 목차

1. [개요](#개요)
2. [AI 모델 종류](#ai-모델-종류)
3. [학습 데이터](#학습-데이터)
4. [학습 방법](#학습-방법)
5. [모델 배포](#모델-배포)
6. [실전 예제](#실전-예제)

---

## 개요

### 🎯 UVIS에서 AI를 활용하는 분야

1. **배차 최적화** (Dispatch Optimization)
   - 차량-주문 매칭 최적화
   - 경로 최적화
   - 비용 최소화

2. **수요 예측** (Demand Forecasting)
   - 일별/주별 주문량 예측
   - 계절성 패턴 분석
   - 특정 거래처 주문 예측

3. **고장 예측** (Predictive Maintenance)
   - 차량 고장 사전 예측
   - 냉동기 이상 감지
   - 정비 시기 추천

4. **배송 시간 예측** (Delivery Time Prediction)
   - 도착 시간 예측
   - 교통 상황 반영
   - 지연 가능성 예측

---

## AI 모델 종류

### 1. 배차 최적화 모델

#### 📌 모델: **강화학습 (Reinforcement Learning)**

```python
# backend/app/ml/dispatch_optimizer.py

import numpy as np
from tensorflow import keras
from tensorflow.keras import layers

class DispatchOptimizer:
    """
    배차 최적화를 위한 강화학습 모델
    
    State: 주문 정보, 차량 상태, 현재 위치
    Action: 차량 배정 결정
    Reward: 비용 절감, 시간 단축, 만족도
    """
    
    def __init__(self):
        self.model = self._build_model()
        self.memory = []  # 경험 저장
        self.epsilon = 1.0  # 탐험률
        self.epsilon_decay = 0.995
        self.gamma = 0.95  # 할인율
        
    def _build_model(self):
        """Q-Network 모델 생성"""
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(20,)),  # 상태 입력
            layers.Dense(64, activation='relu'),
            layers.Dense(32, activation='relu'),
            layers.Dense(10, activation='linear')  # 행동 출력 (차량 선택)
        ])
        model.compile(optimizer='adam', loss='mse')
        return model
    
    def get_state(self, order, vehicles):
        """현재 상태를 벡터로 변환"""
        return np.array([
            order.weight_kg / 5000,  # 정규화된 무게
            order.pallet_count / 20,  # 정규화된 팔레트 수
            order.temperature_zone_encoded,  # 온도대 (0: 냉동, 1: 냉장, 2: 상온)
            order.priority / 3,  # 우선순위
            len([v for v in vehicles if v.status == 'AVAILABLE']) / 10,  # 가용 차량 수
            # ... 추가 특성들
        ])
    
    def choose_action(self, state, vehicles):
        """행동 선택 (epsilon-greedy)"""
        if np.random.random() < self.epsilon:
            # 탐험: 랜덤 선택
            return np.random.choice(len(vehicles))
        else:
            # 활용: 모델 예측
            q_values = self.model.predict(state.reshape(1, -1), verbose=0)
            return np.argmax(q_values[0])
    
    def train(self, batch_size=32):
        """경험 리플레이를 통한 학습"""
        if len(self.memory) < batch_size:
            return
        
        batch = random.sample(self.memory, batch_size)
        
        for state, action, reward, next_state, done in batch:
            target = reward
            if not done:
                target += self.gamma * np.max(
                    self.model.predict(next_state.reshape(1, -1), verbose=0)[0]
                )
            
            target_f = self.model.predict(state.reshape(1, -1), verbose=0)
            target_f[0][action] = target
            
            self.model.fit(state.reshape(1, -1), target_f, epochs=1, verbose=0)
        
        # epsilon 감소 (탐험 → 활용)
        self.epsilon *= self.epsilon_decay
```

---

### 2. 수요 예측 모델

#### 📌 모델: **시계열 예측 (LSTM/Prophet)**

```python
# backend/app/ml/demand_forecaster.py

import pandas as pd
from prophet import Prophet
from sklearn.preprocessing import StandardScaler

class DemandForecaster:
    """
    주문량 예측 모델 (Facebook Prophet 사용)
    """
    
    def __init__(self):
        self.model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05
        )
        self.scaler = StandardScaler()
    
    def prepare_data(self, orders_df):
        """
        학습 데이터 준비
        
        Args:
            orders_df: DataFrame with columns [order_date, order_count]
        """
        # Prophet 형식으로 변환 (ds, y)
        df = orders_df.groupby('order_date').size().reset_index()
        df.columns = ['ds', 'y']
        
        # 추가 특성 (공휴일, 프로모션 등)
        df['holiday'] = df['ds'].apply(self._is_holiday)
        
        return df
    
    def train(self, orders_df):
        """모델 학습"""
        df = self.prepare_data(orders_df)
        self.model.fit(df)
        
        logger.info(f"수요 예측 모델 학습 완료: {len(df)}건")
    
    def predict(self, days=30):
        """향후 N일 예측"""
        future = self.model.make_future_dataframe(periods=days)
        forecast = self.model.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    
    def _is_holiday(self, date):
        """공휴일 판정"""
        # 한국 공휴일 체크
        holidays = ['2026-01-01', '2026-03-01', '2026-05-05', ...]
        return date.strftime('%Y-%m-%d') in holidays
```

---

### 3. 고장 예측 모델

#### 📌 모델: **이상 탐지 (Anomaly Detection)**

```python
# backend/app/ml/failure_predictor.py

from sklearn.ensemble import IsolationForest
import numpy as np

class FailurePredictor:
    """
    차량 고장 예측 모델 (UVIS GPS 데이터 활용)
    """
    
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.1,  # 이상치 비율 10%
            random_state=42
        )
    
    def prepare_features(self, gps_logs):
        """
        GPS 로그에서 특성 추출
        
        Features:
        - 냉동기 온도 평균/분산
        - 속도 패턴 이상
        - 배터리 전압 저하
        - 엔진 상태 변화
        """
        features = []
        
        for log in gps_logs:
            features.append([
                log.temperature_a_avg,
                log.temperature_a_std,
                log.speed_kmh_max,
                log.speed_kmh_min,
                log.battery_voltage,
                log.engine_on_duration,
                # ... 추가 특성
            ])
        
        return np.array(features)
    
    def train(self, gps_logs):
        """정상 데이터로 학습"""
        X = self.prepare_features(gps_logs)
        self.model.fit(X)
        
        logger.info(f"고장 예측 모델 학습 완료: {len(gps_logs)}건")
    
    def predict_failure_risk(self, vehicle_id, recent_logs):
        """고장 위험도 예측"""
        X = self.prepare_features(recent_logs)
        
        # -1: 이상, 1: 정상
        predictions = self.model.predict(X)
        anomaly_scores = self.model.score_samples(X)
        
        # 위험도 계산 (0~100%)
        risk_score = (1 - anomaly_scores.mean()) * 100
        
        return {
            'vehicle_id': vehicle_id,
            'risk_score': risk_score,
            'is_anomaly': predictions[-1] == -1,
            'recommendation': self._get_recommendation(risk_score)
        }
    
    def _get_recommendation(self, risk_score):
        """위험도별 권장 조치"""
        if risk_score > 80:
            return "🔴 즉시 정비 필요"
        elif risk_score > 50:
            return "🟡 조속한 점검 권장"
        else:
            return "🟢 정상"
```

---

## 학습 데이터

### 📊 필요한 데이터

#### 1. **배차 최적화**

```sql
-- 과거 배차 데이터
SELECT 
    d.id,
    d.dispatch_date,
    d.vehicle_id,
    v.vehicle_type,
    v.max_weight_kg,
    o.weight_kg,
    o.pallet_count,
    o.temperature_zone,
    d.status,
    d.actual_cost,
    d.actual_duration_minutes,
    -- 거리, 시간, 비용 등
FROM dispatches d
JOIN vehicles v ON d.vehicle_id = v.id
JOIN orders o ON d.order_id = o.id
WHERE d.dispatch_date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
```

#### 2. **수요 예측**

```sql
-- 일별 주문량
SELECT 
    DATE(order_date) as date,
    COUNT(*) as order_count,
    SUM(weight_kg) as total_weight,
    AVG(weight_kg) as avg_weight,
    temperature_zone
FROM orders
WHERE order_date >= DATE_SUB(NOW(), INTERVAL 2 YEAR)
GROUP BY DATE(order_date), temperature_zone
ORDER BY date
```

#### 3. **고장 예측**

```sql
-- 차량 GPS/센서 데이터
SELECT 
    vehicle_id,
    gps_datetime,
    temperature_a,
    temperature_b,
    speed_kmh,
    battery_voltage,
    is_engine_on
FROM vehicle_gps_logs
WHERE gps_datetime >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
ORDER BY vehicle_id, gps_datetime
```

---

## 학습 방법

### 🔄 학습 프로세스

```
1. 데이터 수집 (Data Collection)
   ↓
2. 데이터 전처리 (Preprocessing)
   ↓
3. 특성 추출 (Feature Engineering)
   ↓
4. 모델 학습 (Training)
   ↓
5. 모델 평가 (Evaluation)
   ↓
6. 모델 배포 (Deployment)
   ↓
7. 모니터링 & 재학습 (Monitoring & Retraining)
```

---

### 방법 1: **수동 학습** (개발 환경)

```bash
# 1. 학습 스크립트 실행
cd /home/user/webapp/backend
python -m app.ml.train_models

# 2. 특정 모델만 학습
python -m app.ml.train_dispatch_optimizer
python -m app.ml.train_demand_forecaster
python -m app.ml.train_failure_predictor
```

**학습 스크립트 예시:**

```python
# backend/app/ml/train_models.py

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.ml.dispatch_optimizer import DispatchOptimizer
from app.ml.demand_forecaster import DemandForecaster
from app.models.dispatch import Dispatch
from app.models.order import Order
import pandas as pd

def train_all_models():
    """모든 ML 모델 학습"""
    db = SessionLocal()
    
    try:
        # 1. 배차 최적화 모델
        print("🤖 배차 최적화 모델 학습 중...")
        optimizer = DispatchOptimizer()
        
        # 과거 6개월 배차 데이터
        dispatches = db.query(Dispatch).filter(
            Dispatch.dispatch_date >= datetime.now() - timedelta(days=180)
        ).all()
        
        optimizer.train(dispatches)
        optimizer.save_model('models/dispatch_optimizer.h5')
        
        # 2. 수요 예측 모델
        print("📊 수요 예측 모델 학습 중...")
        forecaster = DemandForecaster()
        
        # 과거 2년 주문 데이터
        orders = db.query(Order).filter(
            Order.order_date >= datetime.now() - timedelta(days=730)
        ).all()
        
        orders_df = pd.DataFrame([{
            'order_date': o.order_date,
            'weight_kg': o.weight_kg,
            'temperature_zone': o.temperature_zone
        } for o in orders])
        
        forecaster.train(orders_df)
        forecaster.save_model('models/demand_forecaster.pkl')
        
        print("✅ 모든 모델 학습 완료!")
        
    finally:
        db.close()

if __name__ == "__main__":
    train_all_models()
```

---

### 방법 2: **자동 학습** (스케줄링)

#### API를 통한 학습 트리거

```python
# backend/app/api/ml_models.py (기존 파일 확장)

@router.post("/train")
async def train_model(
    model_type: str,  # dispatch, demand, failure
    db: Session = Depends(get_db)
):
    """
    ML 모델 학습 트리거
    
    Args:
        model_type: 학습할 모델 종류
    """
    
    if model_type == "dispatch":
        # 배차 최적화 모델 학습
        optimizer = DispatchOptimizer()
        dispatches = db.query(Dispatch).limit(10000).all()
        optimizer.train(dispatches)
        optimizer.save_model('models/dispatch_optimizer.h5')
        
    elif model_type == "demand":
        # 수요 예측 모델 학습
        forecaster = DemandForecaster()
        orders = db.query(Order).limit(10000).all()
        orders_df = pd.DataFrame([...])
        forecaster.train(orders_df)
        
    return {
        "success": True,
        "model_type": model_type,
        "message": "모델 학습이 시작되었습니다"
    }
```

#### Cron Job으로 자동 학습

```bash
# crontab -e

# 매주 일요일 새벽 2시에 모델 재학습
0 2 * * 0 cd /root/uvis/backend && python -m app.ml.train_models
```

---

### 방법 3: **온라인 학습** (실시간)

```python
# backend/app/services/online_learning_service.py

class OnlineLearningService:
    """실시간 학습 서비스"""
    
    def __init__(self):
        self.optimizer = DispatchOptimizer()
        self.optimizer.load_model('models/dispatch_optimizer.h5')
    
    async def update_from_dispatch(self, dispatch_id: int):
        """
        배차 완료 시 모델 업데이트
        
        Args:
            dispatch_id: 완료된 배차 ID
        """
        dispatch = await self._get_dispatch(dispatch_id)
        
        # State, Action, Reward 추출
        state = self._extract_state(dispatch)
        action = self._extract_action(dispatch)
        reward = self._calculate_reward(dispatch)
        
        # 모델 업데이트
        self.optimizer.memory.append((state, action, reward, None, True))
        self.optimizer.train(batch_size=32)
        
        # 주기적으로 모델 저장
        if len(self.optimizer.memory) % 100 == 0:
            self.optimizer.save_model('models/dispatch_optimizer.h5')
```

---

## 모델 배포

### 📦 모델 파일 관리

```
backend/
├── models/                          # 학습된 모델 저장
│   ├── dispatch_optimizer.h5        # 배차 최적화 모델
│   ├── demand_forecaster.pkl        # 수요 예측 모델
│   ├── failure_predictor.pkl        # 고장 예측 모델
│   └── version.json                 # 모델 버전 정보
```

### 🚀 모델 로딩

```python
# backend/app/core/ml_manager.py

class MLModelManager:
    """ML 모델 관리자 (싱글톤)"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.dispatch_optimizer = None
        self.demand_forecaster = None
        self.failure_predictor = None
        
        self._load_models()
        self._initialized = True
    
    def _load_models(self):
        """모델 로딩"""
        try:
            self.dispatch_optimizer = DispatchOptimizer()
            self.dispatch_optimizer.load_model('models/dispatch_optimizer.h5')
            
            self.demand_forecaster = DemandForecaster()
            self.demand_forecaster.load_model('models/demand_forecaster.pkl')
            
            logger.info("✅ ML 모델 로딩 완료")
        except Exception as e:
            logger.warning(f"⚠️ ML 모델 로딩 실패: {e}")
    
    def get_dispatch_optimizer(self):
        return self.dispatch_optimizer
    
    def get_demand_forecaster(self):
        return self.demand_forecaster

# 전역 인스턴스
ml_manager = MLModelManager()
```

---

## 실전 예제

### 예제 1: 배차 최적화 학습

```python
# 1. 데이터 수집
db = SessionLocal()
dispatches = db.query(Dispatch).filter(
    Dispatch.status == DispatchStatus.COMPLETED
).all()

# 2. 모델 초기화
optimizer = DispatchOptimizer()

# 3. 에피소드 학습
for episode in range(1000):
    # 랜덤 샘플링
    dispatch = random.choice(dispatches)
    
    # State 추출
    state = optimizer.get_state(dispatch.order, vehicles)
    
    # Action 선택
    action = optimizer.choose_action(state, vehicles)
    
    # Reward 계산 (실제 비용 vs 최적 비용)
    actual_cost = dispatch.actual_cost
    optimal_cost = calculate_optimal_cost(dispatch)
    reward = (optimal_cost - actual_cost) / optimal_cost * 100
    
    # 경험 저장
    optimizer.memory.append((state, action, reward, None, True))
    
    # 학습
    if len(optimizer.memory) >= 32:
        optimizer.train(batch_size=32)
    
    if episode % 100 == 0:
        print(f"Episode {episode}, Epsilon: {optimizer.epsilon:.3f}")

# 4. 모델 저장
optimizer.save_model('models/dispatch_optimizer.h5')
```

### 예제 2: 수요 예측 학습

```python
# 1. 데이터 수집 (과거 2년)
orders = db.query(Order).filter(
    Order.order_date >= datetime.now() - timedelta(days=730)
).all()

# 2. DataFrame 변환
df = pd.DataFrame([{
    'ds': o.order_date,
    'y': 1  # 주문 1건
} for o in orders])

# 3. 일별 집계
df = df.groupby('ds').size().reset_index()
df.columns = ['ds', 'y']

# 4. 모델 학습
forecaster = DemandForecaster()
forecaster.train(df)

# 5. 예측 (향후 30일)
forecast = forecaster.predict(days=30)
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])

# 6. 모델 저장
forecaster.save_model('models/demand_forecaster.pkl')
```

---

## 📊 학습 모니터링

### 학습 진행 상황 확인

```python
# backend/app/api/ml_models.py

@router.get("/training/status")
async def get_training_status():
    """학습 진행 상황 조회"""
    return {
        "dispatch_optimizer": {
            "status": "training",
            "progress": 75,  # %
            "episodes": 750,
            "total_episodes": 1000
        },
        "demand_forecaster": {
            "status": "completed",
            "trained_at": "2026-01-30T14:00:00"
        }
    }
```

---

## 🎯 학습 시작하기

### 1단계: 최소 데이터 확보

```bash
# 최소 필요 데이터
- 배차 기록: 100건 이상
- 주문 기록: 1,000건 이상 (1년)
- GPS 로그: 10,000건 이상
```

### 2단계: 학습 실행

```bash
cd /root/uvis/backend
python -m app.ml.train_models
```

### 3단계: 모델 평가

```bash
python -m app.ml.evaluate_models
```

### 4단계: 프로덕션 배포

```bash
# 모델 파일 복사
cp models/*.h5 /root/uvis/backend/models/
cp models/*.pkl /root/uvis/backend/models/

# 서비스 재시작
docker-compose -f docker-compose.prod.yml restart backend
```

---

## 💡 추천 학습 스케줄

- **배차 최적화**: 매주 1회 (일요일 새벽)
- **수요 예측**: 매월 1회 (월초)
- **고장 예측**: 매일 1회 (새벽)

---

**작성일**: 2026-01-30  
**작성자**: GenSpark AI Developer  
**문서 버전**: 1.0
