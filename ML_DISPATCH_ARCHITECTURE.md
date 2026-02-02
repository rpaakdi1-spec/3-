# 🤖 UVIS ML 기반 배차 학습 시스템 아키텍처

## 📋 개요

UVIS의 복잡한 배차 조건들(17가지 제약사항)을 효율적으로 학습하고 최적화하는 ML 시스템 설계입니다.

---

## 🎯 핵심 전략: Multi-Agent 학습 시스템

### 왜 Multi-Agent인가?

**단일 모델의 문제점:**
- 17가지 제약조건을 한 모델이 학습 → 과적합/복잡도 폭발
- 신규 제약조건 추가 시 전체 모델 재학습 필요
- 디버깅 및 개선이 어려움

**Multi-Agent의 장점:**
- 각 제약조건별 전문 에이전트 학습
- 독립적 개선 가능 (A/B 테스트 용이)
- 병렬 학습 및 추론 가능
- 해석 가능성(Interpretability) 향상

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                     배차 요청 (Orders)                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Feature Engineering Layer                        │
│  - 차량 상태 벡터화                                           │
│  - 주문 특성 추출                                            │
│  - 시공간 컨텍스트 생성                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
┌─────────────────┐                   ┌─────────────────┐
│  Hard Rules     │                   │  ML Agents      │
│  Filtering      │                   │  Optimization   │
└─────────────────┘                   └─────────────────┘
        ↓                                       ↓
┌─────────────────┐                   ┌─────────────────┐
│ 1) 온도대 매칭   │                   │ Agent 1: 거리   │
│ 2) 팔렛트 타입   │                   │ Agent 2: 회전수 │
│ 3) 용량 제약     │                   │ Agent 3: 근무일 │
│ 4) 고정배차      │                   │ Agent 4: 시간   │
│ 5) 기피차량      │                   │ Agent 5: 비용   │
└─────────────────┘                   └─────────────────┘
        ↓                                       ↓
        └───────────────────┬───────────────────┘
                            ↓
                   ┌─────────────────┐
                   │ Meta Coordinator │
                   │   (Ensemble)     │
                   └─────────────────┘
                            ↓
                   ┌─────────────────┐
                   │ 최종 배차 결정   │
                   └─────────────────┘
```

---

## 🧠 Agent 상세 설계

### 1️⃣ Agent 분류 전략

#### **Tier 1: Hard Rules (필터링)**
ML 학습 불필요, 규칙 기반 필터링:
- ✅ 온도대 매칭 (냉동/냉장/상온)
- ✅ 팔렛트 타입 (11형/12형)
- ✅ 용량 제약 (max_pallets, 차량 길이)
- ✅ 고정배차 (특정 차량-거래처 고정)
- ✅ 기피차량 (거래처별 기피 차량)

**구현:**
```python
def hard_filter_vehicles(orders: List[Order], vehicles: List[Vehicle]) -> Dict[int, List[Vehicle]]:
    """각 주문에 대해 가능한 차량만 필터링"""
    eligible = {}
    
    for order in orders:
        candidates = []
        for vehicle in vehicles:
            # 온도대 체크
            if not is_temperature_compatible(vehicle, order.temperature_zone):
                continue
            
            # 팔렛트 타입 체크
            if not check_pallet_capacity(vehicle, order.pallet_type, order.pallet_count):
                continue
            
            # 고정배차 체크
            if order.client_id in vehicle.fixed_clients:
                candidates.insert(0, vehicle)  # 최우선
            elif vehicle.id in order.client.blocked_vehicles:
                continue  # 기피차량 제외
            else:
                candidates.append(vehicle)
        
        eligible[order.id] = candidates
    
    return eligible
```

---

#### **Tier 2: Soft Constraints (ML 최적화)**
학습 기반 의사결정:

##### **Agent 1: Distance Optimizer** 🛣️
- **목적:** 공차 거리 최소화 (150km 기준)
- **입력:** 
  - 차량 현위치 (GPS or 차고지)
  - 상차지 위치
  - 하차지 위치
- **출력:** Distance Score (0~1, 낮을수록 좋음)
- **모델:** Gradient Boosting (LightGBM)
- **학습 데이터:** 과거 배차 → 실제 공차 거리 기록

```python
class DistanceOptimizer:
    def __init__(self):
        self.model = lgb.LGBMRegressor(
            objective='regression',
            n_estimators=100,
            max_depth=5
        )
    
    def compute_score(self, vehicle, order):
        features = [
            haversine(vehicle.current_lat, vehicle.current_lon, order.pickup_lat, order.pickup_lon),
            haversine(order.pickup_lat, order.pickup_lon, order.delivery_lat, order.delivery_lon),
            haversine(order.delivery_lat, order.delivery_lon, vehicle.garage_lat, vehicle.garage_lon),
            vehicle.fuel_efficiency_km_per_liter,
            order.priority
        ]
        
        # 예측: 총 주행 거리
        predicted_distance = self.model.predict([features])[0]
        
        # 150km 기준 정규화
        score = min(predicted_distance / 150.0, 2.0)  # 150km 넘으면 페널티
        return score
```

##### **Agent 2: Rotation Equalizer** 🔄
- **목적:** 차량 회전수 평준화 (월급 공정성)
- **입력:**
  - 차량별 당월 회전수
  - 차량별 당월 경유 횟수
  - 차량별 당월 근무일수
- **출력:** Fairness Score (0~1, 낮을수록 평등)
- **모델:** Neural Network (Fairness Loss)

```python
import torch
import torch.nn as nn

class RotationEqualizer(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(5, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
    
    def forward(self, vehicle_stats):
        """
        vehicle_stats: [
            vehicle.rotation_count_this_month,
            vehicle.waypoint_count_this_month,
            vehicle.work_days_this_month,
            avg_rotation_count,  # 전체 차량 평균
            avg_work_days
        ]
        """
        return self.net(vehicle_stats)
    
    def fairness_loss(self, predictions, targets):
        """회전수 편차를 최소화하는 손실 함수"""
        variance = torch.var(predictions)
        mse = nn.MSELoss()(predictions, targets)
        return mse + 0.3 * variance  # 편차 페널티
```

##### **Agent 3: Time Window Checker** ⏰
- **목적:** 하차 가능 시간 준수 (24시간 기준)
- **입력:**
  - 현재 시각
  - 예상 상차 시각
  - 하차 가능 시간 (start, end)
  - 운행 예상 시간 (ETA)
- **출력:** Time Feasibility Score (0~1, 1=완벽 매칭)
- **모델:** RNN (시계열 예측)

```python
import torch.nn as nn

class TimeWindowChecker(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=6, hidden_size=32, num_layers=2, batch_first=True)
        self.fc = nn.Linear(32, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, time_sequence):
        """
        time_sequence: [batch, seq_len, 6]
        - seq_len: 과거 5개 주문의 시간 패턴
        - 6 features: [hour, minute, pickup_duration, driving_duration, delivery_duration, buffer]
        """
        lstm_out, _ = self.lstm(time_sequence)
        last_hidden = lstm_out[:, -1, :]
        score = self.sigmoid(self.fc(last_hidden))
        return score
```

##### **Agent 4: Vehicle Preference Matcher** 🎯
- **목적:** 고정배차 우선순위 & 선호 하차지
- **입력:**
  - 차량 선호 하차지 리스트
  - 주문 하차지
  - 고정배차 여부
- **출력:** Preference Score (0~1, 1=최우선)
- **모델:** Decision Tree (해석 가능)

```python
from sklearn.tree import DecisionTreeClassifier

class VehiclePreferenceMatcher:
    def __init__(self):
        self.model = DecisionTreeClassifier(max_depth=4, random_state=42)
    
    def compute_score(self, vehicle, order):
        features = [
            1.0 if order.delivery_client_id in vehicle.preferred_delivery_clients else 0.0,
            1.0 if order.is_fixed_dispatch and vehicle.id in order.fixed_vehicles else 0.0,
            1.0 if vehicle.is_one_way_fixed else 0.0,
            vehicle.priority_level  # 1~5
        ]
        
        # 이진 분류: 우선배차 여부 (0 or 1)
        is_priority = self.model.predict([features])[0]
        
        # 점수 변환
        score = 1.0 if is_priority == 1 else 0.5
        return score
```

##### **Agent 5: Voltage Alert Monitor** 🔋
- **목적:** 저전압 차량 배제 (안전)
- **입력:**
  - 차량 현재 전압 (UVIS GPS)
  - 시동 상태 (ON/OFF)
- **출력:** Safety Score (0 or 1, 1=안전)
- **모델:** Rule-based (ML 불필요)

```python
def voltage_safety_check(vehicle, uvis_data):
    """저전압 차량 필터링"""
    if uvis_data['engine_on']:
        # 시동 ON: 26V 미만 경고
        if uvis_data['voltage'] < 26.0:
            logger.warning(f"Vehicle {vehicle.code}: Low voltage {uvis_data['voltage']}V (engine ON)")
            return 0.0  # 배차 불가
    else:
        # 시동 OFF: 24V 미만 경고
        if uvis_data['voltage'] < 24.0:
            logger.warning(f"Vehicle {vehicle.code}: Low voltage {uvis_data['voltage']}V (engine OFF)")
            return 0.0
    
    return 1.0  # 안전
```

---

### 2️⃣ Meta Coordinator (앙상블)

모든 Agent의 점수를 조합하여 최종 결정:

```python
class MetaCoordinator:
    def __init__(self):
        self.weights = {
            'distance': 0.25,      # 거리 중요도
            'rotation': 0.20,      # 회전수 평등 중요도
            'time_window': 0.25,   # 시간 준수 중요도
            'preference': 0.15,    # 선호 매칭 중요도
            'voltage': 0.15        # 안전 중요도
        }
    
    def compute_final_score(self, agent_scores: Dict[str, float]) -> float:
        """가중치 기반 최종 점수 계산"""
        final_score = 0.0
        
        for agent_name, score in agent_scores.items():
            final_score += self.weights[agent_name] * score
        
        return final_score
    
    def rank_vehicles(self, order: Order, candidates: List[Vehicle]) -> List[Tuple[Vehicle, float]]:
        """차량 순위 매기기"""
        rankings = []
        
        for vehicle in candidates:
            scores = {
                'distance': distance_optimizer.compute_score(vehicle, order),
                'rotation': rotation_equalizer.compute_score(vehicle),
                'time_window': time_window_checker.compute_score(vehicle, order),
                'preference': preference_matcher.compute_score(vehicle, order),
                'voltage': voltage_safety_check(vehicle, uvis_gps_data[vehicle.id])
            }
            
            # 전압 0점이면 즉시 제외
            if scores['voltage'] == 0.0:
                continue
            
            final_score = self.compute_final_score(scores)
            rankings.append((vehicle, final_score))
        
        # 점수 높은 순 정렬
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        return rankings
```

---

## 📊 학습 데이터 구조

### 1️⃣ 데이터 수집

```sql
-- 학습용 배차 이력 테이블
CREATE TABLE dispatch_training_data (
    id SERIAL PRIMARY KEY,
    dispatch_id INTEGER REFERENCES dispatches(id),
    order_id INTEGER REFERENCES orders(id),
    vehicle_id INTEGER REFERENCES vehicles(id),
    
    -- Feature columns
    vehicle_distance_km FLOAT,           -- 공차 거리
    vehicle_rotation_count INTEGER,      -- 당시 회전수
    time_window_slack_minutes INTEGER,   -- 여유 시간
    is_preferred_match BOOLEAN,          -- 선호 매칭 여부
    voltage_at_dispatch FLOAT,           -- 배차 시 전압
    
    -- Target columns (실제 결과)
    actual_total_distance_km FLOAT,      -- 실제 주행 거리
    actual_arrival_time TIMESTAMP,       -- 실제 도착 시간
    was_delayed BOOLEAN,                 -- 지연 여부
    driver_satisfaction INTEGER,         -- 기사 만족도 (1~5)
    
    -- Metadata
    assigned_by VARCHAR(50),             -- 'human' or 'ml'
    created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_training_vehicle ON dispatch_training_data(vehicle_id);
CREATE INDEX idx_training_order ON dispatch_training_data(order_id);
CREATE INDEX idx_training_date ON dispatch_training_data(created_at);
```

### 2️⃣ Feature Engineering

```python
def extract_features(order: Order, vehicle: Vehicle, context: Dict) -> np.ndarray:
    """주문-차량 쌍에서 학습 특징 추출"""
    features = []
    
    # 거리 관련
    features.append(haversine(vehicle.current_lat, vehicle.current_lon, order.pickup_lat, order.pickup_lon))
    features.append(haversine(order.pickup_lat, order.pickup_lon, order.delivery_lat, order.delivery_lon))
    
    # 차량 상태
    features.append(vehicle.rotation_count_this_month)
    features.append(vehicle.work_days_this_month)
    features.append(vehicle.waypoint_count_this_month)
    
    # 시간 관련
    features.append(context['current_hour'])
    features.append(context['day_of_week'])
    features.append(order.delivery_time_window_slack)
    
    # 선호도
    features.append(1.0 if order.delivery_client_id in vehicle.preferred_clients else 0.0)
    features.append(1.0 if order.is_fixed_dispatch else 0.0)
    
    # 안전
    features.append(context.get('voltage', 26.0))
    
    return np.array(features)
```

---

## 🚀 학습 파이프라인

### Phase 1: 오프라인 학습 (초기)

```python
# 1. 과거 데이터 로드
df = pd.read_sql("""
    SELECT * FROM dispatch_training_data
    WHERE created_at >= NOW() - INTERVAL '6 months'
      AND assigned_by = 'human'
""", engine)

# 2. Feature 생성
X = []
y = []

for row in df.itertuples():
    features = extract_features(row.order, row.vehicle, row.context)
    X.append(features)
    
    # Target: 배차 성공 여부 (거리 + 지연 고려)
    success_score = (
        (1.0 - min(row.actual_total_distance_km / 150.0, 2.0)) * 0.4 +  # 거리 점수
        (1.0 if not row.was_delayed else 0.0) * 0.4 +                    # 지연 점수
        (row.driver_satisfaction / 5.0) * 0.2                            # 만족도 점수
    )
    y.append(success_score)

X = np.array(X)
y = np.array(y)

# 3. Agent별 학습
distance_optimizer.fit(X, y)
rotation_equalizer.fit(X, y)
time_window_checker.fit(X, y)

# 4. 모델 저장
joblib.dump(distance_optimizer, 'models/distance_optimizer_v1.pkl')
```

### Phase 2: 온라인 학습 (지속 개선)

```python
class OnlineLearner:
    def __init__(self):
        self.buffer = []
        self.batch_size = 100
        
    def add_feedback(self, dispatch_id: int, feedback: Dict):
        """실시간 피드백 수집"""
        self.buffer.append({
            'dispatch_id': dispatch_id,
            'feedback': feedback,
            'timestamp': datetime.now()
        })
        
        # 버퍼가 가득 차면 학습
        if len(self.buffer) >= self.batch_size:
            self.update_models()
    
    def update_models(self):
        """모델 증분 업데이트"""
        logger.info(f"Updating models with {len(self.buffer)} new samples...")
        
        # 새 데이터로 모델 fine-tuning
        for agent in [distance_optimizer, rotation_equalizer, time_window_checker]:
            X_new, y_new = self._prepare_batch(self.buffer)
            agent.partial_fit(X_new, y_new)
        
        # 버퍼 초기화
        self.buffer.clear()
        
        logger.info("Models updated successfully!")
```

---

## 🎮 실전 배차 플로우

```python
async def optimize_dispatch(orders: List[Order], vehicles: List[Vehicle]) -> List[Dispatch]:
    """ML 기반 최적 배차 생성"""
    
    # Step 1: Hard Filter
    eligible = hard_filter_vehicles(orders, vehicles)
    logger.info(f"Hard filtering: {sum(len(v) for v in eligible.values())} candidates")
    
    # Step 2: ML Agent 점수 계산
    dispatches = []
    
    for order in orders:
        candidates = eligible[order.id]
        
        if not candidates:
            logger.warning(f"No eligible vehicles for order {order.order_number}")
            # 용차 수배 로직으로 이동
            continue
        
        # Meta Coordinator로 순위 결정
        rankings = meta_coordinator.rank_vehicles(order, candidates)
        
        # 최고 점수 차량 선택
        best_vehicle, best_score = rankings[0]
        
        logger.info(f"Order {order.order_number} → Vehicle {best_vehicle.code} (score: {best_score:.3f})")
        
        # Dispatch 생성
        dispatch = Dispatch(
            order_id=order.id,
            vehicle_id=best_vehicle.id,
            optimization_score=best_score,
            assigned_by='ml',
            status=DispatchStatus.ASSIGNED
        )
        dispatches.append(dispatch)
    
    # Step 3: TSP로 경로 최적화
    for dispatch in dispatches:
        routes = await tsp_optimizer.optimize_routes([dispatch.order])
        dispatch.routes = routes
    
    return dispatches
```

---

## 📈 성능 지표 (KPIs)

### 1️⃣ 모델 성능

```python
# Metrics 계산
from sklearn.metrics import mean_squared_error, r2_score

def evaluate_agents():
    metrics = {}
    
    # Distance Optimizer
    y_pred_dist = distance_optimizer.predict(X_test)
    metrics['distance_mae'] = mean_absolute_error(y_test_distance, y_pred_dist)
    metrics['distance_r2'] = r2_score(y_test_distance, y_pred_dist)
    
    # Rotation Equalizer
    rotation_variance = np.var([v.rotation_count for v in vehicles])
    metrics['rotation_fairness'] = 1.0 / (1.0 + rotation_variance)  # 편차가 작을수록 1에 가까움
    
    # Time Window Checker
    on_time_rate = np.mean([1 if not d.was_delayed else 0 for d in dispatches])
    metrics['time_window_accuracy'] = on_time_rate
    
    logger.info(f"Model Performance: {metrics}")
    return metrics
```

### 2️⃣ 비즈니스 KPIs

- **공차 거리:** 평균 100km 이하 (목표 150km 대비 33% 개선)
- **회전수 편차:** 월별 표준편차 2회 이하
- **시간 준수율:** 95% 이상
- **용차 수배율:** 10% 이하 (90% 자사 차량 배차)
- **기사 만족도:** 평균 4.0/5.0 이상

---

## 🔄 지속 개선 사이클

```
┌─────────────┐
│  배차 실행   │
└──────┬──────┘
       ↓
┌─────────────┐
│  실시간 추적 │ (GPS, ETA)
└──────┬──────┘
       ↓
┌─────────────┐
│  결과 수집   │ (거리, 시간, 만족도)
└──────┬──────┘
       ↓
┌─────────────┐
│  모델 재학습 │ (Online Learning)
└──────┬──────┘
       ↓
┌─────────────┐
│ 가중치 조정  │ (Meta Coordinator)
└──────┬──────┘
       ↓
       └──────→ (반복)
```

### A/B 테스트 전략

```python
class ABTestingController:
    def __init__(self):
        self.test_groups = {
            'control': 0.7,    # 70%: 기존 알고리즘
            'ml_v1': 0.15,     # 15%: ML Agent 버전 1
            'ml_v2': 0.15      # 15%: ML Agent 버전 2
        }
    
    def assign_dispatch_method(self, order: Order) -> str:
        """주문을 랜덤하게 그룹 배정"""
        rand = random.random()
        
        cumulative = 0.0
        for group, ratio in self.test_groups.items():
            cumulative += ratio
            if rand < cumulative:
                return group
        
        return 'control'
    
    def compare_results(self):
        """그룹별 성과 비교"""
        results = {}
        
        for group in self.test_groups.keys():
            dispatches = Dispatch.query.filter_by(test_group=group).all()
            
            results[group] = {
                'avg_distance': np.mean([d.total_distance_km for d in dispatches]),
                'on_time_rate': np.mean([1 if not d.was_delayed else 0 for d in dispatches]),
                'satisfaction': np.mean([d.driver_satisfaction for d in dispatches])
            }
        
        logger.info(f"A/B Test Results: {results}")
        return results
```

---

## 🛠️ 구현 로드맵

### **Week 1-2: 인프라 구축**
- [ ] `dispatch_training_data` 테이블 생성
- [ ] Feature extraction 파이프라인 구축
- [ ] 과거 6개월 데이터 수집 및 라벨링

### **Week 3-4: Agent 개발**
- [ ] Distance Optimizer 학습 및 검증
- [ ] Rotation Equalizer 학습 및 검증
- [ ] Time Window Checker 학습 및 검증
- [ ] Meta Coordinator 가중치 튜닝

### **Week 5-6: 통합 및 테스트**
- [ ] Hard Rules + ML Agents 통합
- [ ] 시뮬레이션 테스트 (과거 데이터 재생)
- [ ] 성능 벤치마크 (기존 vs ML)

### **Week 7-8: 파일럿 런**
- [ ] 10% 트래픽으로 A/B 테스트
- [ ] 실시간 모니터링 대시보드
- [ ] 피드백 수집 및 모델 개선

### **Week 9-10: 전체 롤아웃**
- [ ] 70% 트래픽 확대
- [ ] Online Learning 활성화
- [ ] 자동 재학습 파이프라인 구축

---

## 📚 참고 자료

### 논문
- [Deep Reinforcement Learning for Vehicle Routing](https://arxiv.org/abs/1802.04240)
- [Learning to Dispatch for Ride-Sharing](https://dl.acm.org/doi/10.1145/3292500.3330978)

### 오픈소스
- **OR-Tools:** Google의 최적화 라이브러리
- **Gym-VRP:** 차량 경로 최적화 강화학습 환경
- **LightGBM:** Gradient Boosting 프레임워크

---

## ✅ 요약

### 핵심 전략
1. **Multi-Agent 아키텍처:** 17개 제약조건을 5개 전문 Agent로 분산
2. **Hybrid 접근:** Hard Rules (필터링) + ML (최적화)
3. **지속 학습:** 온라인 학습으로 실시간 개선
4. **A/B 테스트:** 안전한 점진적 배포

### 예상 효과
- 🚀 **공차 거리:** 30% 감소
- ⚖️ **회전수 편차:** 50% 감소
- ⏰ **시간 준수율:** 95% 달성
- 💰 **운영 비용:** 연 20% 절감

---

**다음 단계:** `backend/app/services/ml_dispatch_service.py` 구현 시작! 🚀
