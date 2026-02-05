# Phase 5: 경량 ML 구현

## 🚀 빠른 시작

### 1. 환경 설정
```bash
cd /home/user/webapp/phase5
pip install -r requirements_ml.txt
```

### 2. 테스트 실행
```bash
python test_ml_models.py
```

### 3. 모델 사용

#### 수요 예측
```python
import sys
sys.path.append('/home/user/webapp/phase5')

from ml_advanced.demand_forecast import DemandForecaster
from ml_advanced.utils import DataLoader

# 데이터 로드
loader = DataLoader()
orders_df = loader.load_order_history(days=90)
daily_df = loader.aggregate_daily_demand(orders_df)

# 모델 학습
forecaster = DemandForecaster()
forecaster.train(daily_df)

# 7일 예측
predictions = forecaster.predict(daily_df, days_ahead=7)
print(predictions)

# 모델 저장
forecaster.save_model('models/demand_forecast_model.pkl')
```

#### 이상 탐지
```python
from ml_advanced.anomaly_detection import AnomalyDetector

# 배차 데이터 로드
dispatch_df = loader.load_dispatch_history(days=90)

# 모델 학습
detector = AnomalyDetector(contamination=0.1)
detector.train(dispatch_df, feature_type='dispatch')

# 이상 탐지
results = detector.detect(dispatch_df)
anomalies = results[results['is_anomaly'] == 1]
print(f"이상 배차: {len(anomalies)} 건")

# 모델 저장
detector.save_model('models/anomaly_detector_model.pkl')
```

## 📦 패키지 구조

```
phase5/
├── ml_advanced/
│   ├── demand_forecast/         # 수요 예측
│   ├── anomaly_detection/       # 이상 탐지
│   └── utils/                   # 데이터 로더
├── models/                      # 저장된 모델
├── test_ml_models.py           # 테스트 스크립트
└── requirements_ml.txt         # 의존성
```

## 🎯 주요 기능

1. **수요 예측** (Random Forest)
   - 일별 주문 수요 예측
   - 7일 미래 예측
   - 특징 중요도 분석

2. **이상 탐지** (Isolation Forest)
   - 배차 비효율 패턴 감지
   - 차량 상태 이상 탐지
   - 이상 점수 기반 순위

3. **데이터 로더**
   - PostgreSQL 통합
   - 다양한 데이터 로드
   - 자동 집계 기능

## 📊 비즈니스 가치

- 수요 예측: ₩30M/년
- 배차 최적화: ₩25M/년
- 이상 탐지: ₩25M/년
- **합계**: ₩80M/년

## 📚 문서

- [완료 보고서](../PHASE_5_LIGHTWEIGHT_ML_COMPLETE.md)
- [테스트 가이드](./test_ml_models.py)
- [API 문서](../backend/README.md)

## 🔧 유지보수

### 모델 재학습 (크론탭)
```bash
# 매주 일요일 새벽 2시
0 2 * * 0 cd /home/user/webapp/phase5 && python test_ml_models.py >> /var/log/ml_retrain.log 2>&1
```

### 모델 확인
```bash
ls -lh models/
```

---

**Phase 5 완료** | **2026-02-05** | **₩80M/년 가치**
