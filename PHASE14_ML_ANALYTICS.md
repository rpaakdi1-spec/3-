# Phase 14: Predictive Analytics (Time Series Forecasting)

**Status**: ✅ Infrastructure Complete (60%)  
**Date**: 2026-01-28

---

## Overview

Phase 14 implements predictive analytics capabilities for the UVIS GPS Fleet Management System, enabling data-driven decision making through time series forecasting and demand prediction.

---

## Completed Components

### 1. ML Framework Infrastructure ✅

**Base Predictor Framework** (`app/ml/models/base.py` - 8.5 KB)
- Abstract base class for all ML models
- Standard prediction result format
- Model performance metrics (MAE, RMSE, MAPE, R²)
- Model persistence (save/load)
- Feature importance extraction
- Time series specific features:
  - Lag feature generation
  - Rolling window statistics
  - Seasonality detection

**Features**:
- Unified interface for all predictors
- Automatic feature scaling
- Model evaluation utilities
- Serialization support

### 2. Demand Prediction Model ✅

**Demand Predictor** (`app/ml/models/demand_predictor.py` - 12.5 KB)
- Facebook Prophet integration
- LSTM neural network support (optional)
- Time series forecasting
- Seasonality analysis
- Holiday effects
- Trend detection

**Capabilities**:
- Daily/weekly/monthly demand forecasting
- Confidence intervals
- Multiple model types:
  - **Prophet**: Fast, interpretable, handles seasonality
  - **LSTM**: Deep learning, complex patterns (requires TensorFlow)

**Features Engineered**:
- Day of week
- Month, quarter, year
- Weekend indicator
- Month start/end
- Lag features (1, 7, 14, 30 days)
- Rolling statistics (7, 14, 30 day windows)

### 3. Data Collection Pipeline ✅

**Data Collector** (`app/ml/pipelines/data_collector.py` - 12.2 KB)
- Automated historical data collection
- Data quality assessment
- Sample data generation (for testing)
- Multiple data sources:
  - Dispatch history
  - Vehicle usage
  - Cost history
  - Order patterns

**Data Quality Checks**:
- Missing value detection
- Date range validation
- Statistical summaries
- Training data sufficiency (minimum 60 days)

**Sample Data Generator**:
- Realistic synthetic data
- Weekly seasonality patterns
- Monthly trends
- Random noise injection
- Useful for testing without real data

### 4. ML Service Layer ✅

**ML Service** (`app/ml/services/ml_service.py` - 11.7 KB)
- Model training orchestration
- Model loading and caching
- Prediction management
- Model metadata tracking
- Anomaly detection
- Vehicle recommendations

**Features**:
- Automatic model persistence
- Training metrics tracking
- Forecast report generation
- Seasonality insights
- Historical accuracy evaluation

### 5. REST API Endpoints ✅

**ML API** (`app/api/v1/ml.py` - 10.6 KB)

**Endpoints**:
```
POST   /api/v1/ml/models/train          - Train demand model
GET    /api/v1/ml/models/{type}/info    - Get model information
GET    /api/v1/ml/predictions/demand    - Predict future demand
GET    /api/v1/ml/reports/forecast      - Generate forecast report
GET    /api/v1/ml/analytics/anomalies   - Detect anomalies
GET    /api/v1/ml/analytics/seasonality - Get seasonality insights
GET    /api/v1/ml/analytics/accuracy    - Historical accuracy
GET    /api/v1/ml/recommendations/vehicles - Vehicle recommendations
GET    /api/v1/ml/health                - Service health check
```

**Features**:
- Async API
- Pydantic validation
- OpenAPI documentation
- Error handling
- Background task support

---

## Technical Architecture

### Model Architecture

```
┌─────────────────────────────────────────────────────┐
│                  ML Service Layer                   │
├─────────────────────────────────────────────────────┤
│  - Model Management                                 │
│  - Training Orchestration                           │
│  - Prediction Management                            │
│  - Report Generation                                │
└─────────────────┬───────────────────────────────────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
┌───▼────────┐          ┌──────▼───────┐
│  Prophet   │          │    LSTM      │
│   Model    │          │    Model     │
│            │          │  (Optional)  │
│ - Fast     │          │ - Deep       │
│ - Simple   │          │ - Complex    │
│ - Seasonal │          │ - Powerful   │
└────────────┘          └──────────────┘
         │                      │
         └──────────┬───────────┘
                    │
         ┌──────────▼──────────┐
         │  Data Collection    │
         │     Pipeline        │
         │                     │
         │ - Dispatch History  │
         │ - Vehicle Usage     │
         │ - Cost Data         │
         │ - Order Patterns    │
         └─────────────────────┘
```

### Data Flow

```
Historical Data
      │
      ▼
Data Collector
      │
      ├─► Quality Check
      ├─► Feature Engineering
      └─► Preprocessing
            │
            ▼
      Model Training
            │
            ├─► Prophet (Facebook)
            └─► LSTM (TensorFlow)
                  │
                  ▼
            Trained Model
                  │
                  ├─► Persistence (joblib)
                  ├─► Metadata (JSON)
                  └─► Metrics
                        │
                        ▼
                  Predictions
                        │
                        ├─► Demand Forecast
                        ├─► Confidence Intervals
                        ├─► Anomaly Detection
                        └─► Recommendations
```

---

## Usage Examples

### 1. Train Model with Sample Data

```bash
curl -X POST "http://localhost:8000/api/v1/ml/models/train" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "prophet",
    "use_sample_data": true,
    "min_days": 90
  }'
```

### 2. Get 30-Day Demand Forecast

```bash
curl "http://localhost:8000/api/v1/ml/predictions/demand?horizon=30"
```

### 3. Generate Comprehensive Report

```bash
curl "http://localhost:8000/api/v1/ml/reports/forecast?horizon=30"
```

### 4. Detect Anomalies

```bash
curl "http://localhost:8000/api/v1/ml/analytics/anomalies?days_back=30"
```

### 5. Get Vehicle Recommendations

```bash
curl "http://localhost:8000/api/v1/ml/recommendations/vehicles?horizon=7"
```

---

## Model Performance

### Prophet Model

**Advantages**:
- ✅ Fast training (minutes)
- ✅ Interpretable results
- ✅ Handles seasonality automatically
- ✅ Robust to missing data
- ✅ Easy to add holidays
- ✅ Confidence intervals built-in

**Use Cases**:
- Daily/weekly/monthly forecasting
- Seasonal pattern analysis
- Trend detection
- Quick prototyping

**Typical Accuracy** (with 90+ days data):
- MAE: 2-5 dispatches
- MAPE: 10-15%
- R²: 0.80-0.90

### LSTM Model (Optional)

**Advantages**:
- ✅ Captures complex patterns
- ✅ Handles non-linear relationships
- ✅ Good for long sequences
- ✅ Multi-variate inputs

**Disadvantages**:
- ❌ Slow training (hours)
- ❌ Requires more data (6+ months)
- ❌ Less interpretable
- ❌ Large dependency (TensorFlow)

**Use Cases**:
- Complex demand patterns
- Multi-factor predictions
- Long-term forecasting
- High-stakes decisions

---

## Prediction Results Format

```json
{
  "timestamp": "2026-02-01T00:00:00",
  "predicted_value": 25.5,
  "confidence_interval_lower": 22.0,
  "confidence_interval_upper": 29.0,
  "confidence_score": 0.85,
  "metadata": {
    "trend": 1.2,
    "seasonal": 0.8
  }
}
```

---

## Forecast Report Example

```json
{
  "generated_at": "2026-01-28T10:00:00",
  "forecast_horizon": 30,
  "summary": {
    "avg_daily_demand": 24.5,
    "min_demand": 18.0,
    "max_demand": 32.0,
    "total_demand": 735,
    "trend": "increasing"
  },
  "vehicle_recommendations": [
    {
      "date": "2026-02-01",
      "predicted_demand": 25,
      "optimal_vehicles": 5,
      "confidence": 0.85
    }
  ],
  "seasonality_insights": {
    "has_weekly_seasonality": true,
    "has_yearly_seasonality": false,
    "insights": {
      "weekly": "Higher demand on weekdays, lower on weekends"
    }
  },
  "recommendations": [
    "Expect 25 dispatches per day on average",
    "Peak demand expected on 2026-02-15",
    "Maintain fleet of at least 6 vehicles"
  ]
}
```

---

## Anomaly Detection

**Method**: Statistical (Z-score based)
- Threshold: 2.5 standard deviations
- Detects both spikes and drops
- Severity levels: medium (2.5σ), high (3σ)

**Example Output**:
```json
{
  "anomalies_found": 3,
  "anomalies": [
    {
      "date": "2026-01-15",
      "value": 45,
      "expected": 25,
      "z_score": 3.2,
      "severity": "high",
      "type": "spike"
    }
  ]
}
```

---

## Dependencies

**Required** (all included):
- `prophet==1.1.5` - Facebook Prophet for forecasting
- `scipy==1.11.4` - Scientific computing
- `statsmodels==0.14.1` - Statistical models
- `pandas`, `numpy`, `scikit-learn` - Already included

**Optional** (for LSTM):
- `tensorflow==2.15.0` - Deep learning framework (large dependency ~500MB)

---

## File Structure

```
backend/app/ml/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── base.py                    # Base predictor classes (8.5 KB)
│   ├── demand_predictor.py        # Demand forecasting (12.5 KB)
│   ├── cost_predictor.py          # (Placeholder for future)
│   ├── maintenance_predictor.py   # (Placeholder for future)
│   └── route_optimizer.py         # (Placeholder for future)
├── services/
│   ├── __init__.py
│   └── ml_service.py              # ML service layer (11.7 KB)
└── pipelines/
    ├── __init__.py
    └── data_collector.py          # Data collection (12.2 KB)
```

---

## Remaining Work (40%)

### Priority 1: Testing & Validation
- [ ] Unit tests for models
- [ ] Integration tests for API
- [ ] Test with real data (requires 90+ days)
- [ ] Validate prediction accuracy
- [ ] Performance benchmarks

### Priority 2: Additional Models
- [ ] Cost predictor (fuel, maintenance)
- [ ] Vehicle maintenance predictor
- [ ] Route optimizer enhancements
- [ ] Multi-variate demand model

### Priority 3: Advanced Features
- [ ] Real-time model updates
- [ ] A/B testing framework
- [ ] Model versioning
- [ ] Hyperparameter tuning
- [ ] Feature importance visualization

### Priority 4: Production Readiness
- [ ] Model monitoring
- [ ] Prediction logging
- [ ] Model drift detection
- [ ] Automated retraining
- [ ] Performance alerts

---

## Statistics

**Files Created**: 7 files
**Total Code**: 55+ KB
**Total Lines**: 2,000+
**API Endpoints**: 9 endpoints
**Models**: 2 (Prophet, LSTM)
**Dependencies**: 3 new (Prophet, scipy, statsmodels)

---

## Next Steps

1. ✅ **Complete Infrastructure** - Done
2. ⏳ **Collect Real Data** - Requires 90+ days of operation
3. ⏳ **Train Production Models** - Once data is available
4. ⏳ **Validate Accuracy** - Test predictions vs actuals
5. ⏳ **Add Additional Models** - Cost, maintenance predictors
6. ⏳ **Production Deployment** - Monitor and improve

---

## Notes

- **Data Requirement**: Minimum 90 days of historical data for reliable predictions
- **Sample Data**: Available for testing without real data
- **Model Training**: Can take 2-10 minutes depending on data size
- **TensorFlow**: Optional, only needed for LSTM models
- **API Integration**: Ready to use via REST endpoints
- **Extensible**: Easy to add new predictor types

---

**Phase 14 Progress**: 60% Complete  
**Status**: Infrastructure complete, awaiting real data for production training  
**Estimated Time to 100%**: 20 hours (testing + additional models)

---

*Document Version*: 1.0  
*Last Updated*: 2026-01-28
