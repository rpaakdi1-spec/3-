"""
ML/Predictive Analytics API endpoints.
"""
from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.ml.services.ml_service import MLService
from app.ml.models.base import PredictionResult, ModelMetrics
from app.ml.pipelines.retraining_pipeline import RetrainingPipeline, ModelMonitor


router = APIRouter(prefix="/ml", tags=["ml", "analytics"])


# Request/Response Models

class TrainModelRequest(BaseModel):
    """Request to train a model."""
    model_type: str = Field("prophet", description="Model type: 'prophet' or 'lstm'")
    use_sample_data: bool = Field(False, description="Use synthetic data for testing")
    min_days: int = Field(90, description="Minimum days of historical data required")
    
    class Config:
        schema_extra = {
            "example": {
                "model_type": "prophet",
                "use_sample_data": False,
                "min_days": 90
            }
        }


class PredictionResponse(BaseModel):
    """Prediction result response."""
    timestamp: datetime
    predicted_value: float
    confidence_interval_lower: Optional[float] = None
    confidence_interval_upper: Optional[float] = None
    confidence_score: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "timestamp": "2026-02-01T00:00:00",
                "predicted_value": 25.5,
                "confidence_interval_lower": 22.0,
                "confidence_interval_upper": 29.0,
                "confidence_score": 0.85
            }
        }


class ModelInfoResponse(BaseModel):
    """Model information response."""
    model_type: str
    trained_at: str
    metrics: dict
    data_quality: dict
    is_loaded: bool


class ForecastReportResponse(BaseModel):
    """Forecast report response."""
    generated_at: str
    forecast_horizon: int
    predictions: List[dict]
    summary: dict
    vehicle_recommendations: List[dict]
    seasonality_insights: Optional[dict]
    recommendations: List[str]


# Dependency to get ML service
def get_ml_service(db: Session = Depends(get_db)) -> MLService:
    """Get ML service instance."""
    return MLService(db)


# Dependency to get retraining pipeline
def get_retraining_pipeline(db: Session = Depends(get_db)) -> RetrainingPipeline:
    """Get retraining pipeline instance."""
    return RetrainingPipeline(db)


# API Endpoints

@router.post("/models/train", response_model=ModelMetrics)
async def train_model(
    request: TrainModelRequest,
    background_tasks: BackgroundTasks,
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Train a predictive model.
    
    This endpoint trains a demand prediction model using historical data.
    Training can take several minutes depending on data size.
    
    **Model Types:**
    - `prophet`: Facebook Prophet (time series forecasting)
    - `lstm`: LSTM neural network (deep learning)
    
    **Note:** Requires at least 90 days of historical data.
    Use `use_sample_data=true` for testing without real data.
    """
    try:
        metrics = ml_service.train_demand_model(
            model_type=request.model_type,
            use_sample_data=request.use_sample_data,
            min_days=request.min_days
        )
        return metrics
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.get("/models/{model_type}/info", response_model=ModelInfoResponse)
async def get_model_info(
    model_type: str,
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Get information about a trained model.
    
    Returns model metadata, training metrics, and data quality information.
    """
    info = ml_service.get_model_info(model_type)
    
    if info is None:
        raise HTTPException(
            status_code=404,
            detail=f"Model '{model_type}' not found. Please train the model first."
        )
    
    # Check if model is loaded in memory
    is_loaded = (
        ml_service.demand_predictor is not None and
        ml_service.demand_predictor.is_trained
    )
    
    return ModelInfoResponse(
        model_type=info['model_type'],
        trained_at=info['trained_at'],
        metrics=info['metrics'],
        data_quality=info['data_quality'],
        is_loaded=is_loaded
    )


@router.get("/predictions/demand", response_model=List[PredictionResponse])
async def predict_demand(
    horizon: int = 30,
    model_type: str = "prophet",
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Predict future dispatch demand.
    
    **Parameters:**
    - `horizon`: Number of days to forecast (default: 30)
    - `model_type`: Model to use for prediction (default: 'prophet')
    
    **Returns:** List of daily predictions with confidence intervals
    """
    try:
        # Load model if not already loaded
        if ml_service.demand_predictor is None:
            if not ml_service.load_demand_model(model_type):
                raise HTTPException(
                    status_code=404,
                    detail=f"Model '{model_type}' not found. Please train the model first."
                )
        
        predictions = ml_service.predict_demand(horizon=horizon)
        
        return [
            PredictionResponse(
                timestamp=p.timestamp,
                predicted_value=p.predicted_value,
                confidence_interval_lower=p.confidence_interval_lower,
                confidence_interval_upper=p.confidence_interval_upper,
                confidence_score=p.confidence_score
            )
            for p in predictions
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/reports/forecast", response_model=ForecastReportResponse)
async def generate_forecast_report(
    horizon: int = 30,
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Generate comprehensive forecast report.
    
    Includes:
    - Demand predictions
    - Summary statistics
    - Vehicle recommendations
    - Seasonality insights
    - Actionable recommendations
    
    **Parameters:**
    - `horizon`: Forecast horizon in days (default: 30)
    """
    try:
        report = ml_service.generate_forecast_report(horizon=horizon)
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/analytics/anomalies")
async def detect_anomalies(
    days_back: int = 30,
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Detect anomalies in dispatch patterns.
    
    Analyzes historical data to identify unusual spikes or drops in demand.
    
    **Parameters:**
    - `days_back`: Number of days to analyze (default: 30)
    
    **Returns:** List of detected anomalies with severity and type
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days_back)
    
    anomalies = ml_service.detect_anomalies(
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "analyzed_period": {
            "start_date": start_date.date().isoformat(),
            "end_date": end_date.date().isoformat(),
            "days": days_back
        },
        "anomalies_found": len(anomalies),
        "anomalies": anomalies
    }


@router.get("/analytics/seasonality")
async def get_seasonality_insights(
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Get seasonality insights from demand model.
    
    Analyzes seasonal patterns in dispatch demand (daily, weekly, yearly).
    
    **Note:** Requires a trained Prophet model.
    """
    insights = ml_service.get_seasonality_insights()
    
    if insights is None:
        raise HTTPException(
            status_code=404,
            detail="No seasonality data available. Please train a Prophet model first."
        )
    
    return insights


@router.get("/analytics/accuracy")
async def get_historical_accuracy(
    days_back: int = 30,
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Get historical prediction accuracy.
    
    Compares past predictions with actual values to evaluate model performance.
    
    **Parameters:**
    - `days_back`: Number of days to evaluate (default: 30)
    
    **Returns:** Accuracy metrics (MAE, RMSE, MAPE)
    """
    accuracy = ml_service.get_historical_accuracy(days_back=days_back)
    return accuracy


@router.get("/recommendations/vehicles")
async def get_vehicle_recommendations(
    horizon: int = 7,
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Get optimal vehicle fleet recommendations.
    
    Based on predicted demand, suggests the optimal number of vehicles needed.
    
    **Parameters:**
    - `horizon`: Number of days to plan for (default: 7)
    """
    try:
        # Get predictions
        predictions = ml_service.predict_demand(horizon=horizon)
        
        # Get recommendations
        recommendations = ml_service.suggest_optimal_vehicles(predictions)
        
        return {
            "planning_horizon": horizon,
            "recommendations": recommendations,
            "summary": {
                "min_vehicles": min([r['optimal_vehicles'] for r in recommendations]),
                "max_vehicles": max([r['optimal_vehicles'] for r in recommendations]),
                "avg_vehicles": sum([r['optimal_vehicles'] for r in recommendations]) / len(recommendations)
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health")
async def health_check(ml_service: MLService = Depends(get_ml_service)):
    """
    Health check for ML service.
    
    Returns status of available models and system readiness.
    """
    prophet_info = ml_service.get_model_info('prophet')
    lstm_info = ml_service.get_model_info('lstm')
    
    return {
        "status": "healthy",
        "models": {
            "prophet": {
                "available": prophet_info is not None,
                "trained_at": prophet_info['trained_at'] if prophet_info else None
            },
            "lstm": {
                "available": lstm_info is not None,
                "trained_at": lstm_info['trained_at'] if lstm_info else None
            }
        },
        "service": "ML Predictive Analytics",
        "version": "1.0.0"
    }


# Automatic Retraining Endpoints

@router.post("/retraining/check")
async def check_and_retrain(
    model_type: str = "prophet",
    force: bool = False,
    use_sample_data: bool = False,
    background_tasks: BackgroundTasks = None,
    pipeline: RetrainingPipeline = Depends(get_retraining_pipeline)
):
    """
    Check if retraining is needed and trigger if necessary.
    
    **Parameters:**
    - `model_type`: Model to check ('prophet' or 'lstm')
    - `force`: Force retraining regardless of conditions
    - `use_sample_data`: Use synthetic data for testing
    
    **Returns:** Retraining status and metrics
    
    **Triggers retraining when:**
    - Model is older than 30 days
    - More than 100 new data points available
    - Model performance degraded by >10%
    - Force flag is set to true
    """
    result = pipeline.check_and_retrain(
        model_type=model_type,
        force=force,
        use_sample_data=use_sample_data
    )
    
    return result


@router.post("/retraining/trigger")
async def trigger_retraining(
    model_type: str = "prophet",
    reason: str = "Manual retraining",
    use_sample_data: bool = False,
    background_tasks: BackgroundTasks = None,
    pipeline: RetrainingPipeline = Depends(get_retraining_pipeline)
):
    """
    Manually trigger model retraining.
    
    **Parameters:**
    - `model_type`: Model to retrain ('prophet' or 'lstm')
    - `reason`: Reason for retraining
    - `use_sample_data`: Use synthetic data for testing
    
    **Returns:** Training result with metrics
    
    **Note:** This endpoint forces retraining regardless of conditions.
    Use `/retraining/check` for conditional retraining.
    """
    result = pipeline.retrain_model(
        model_type=model_type,
        reason=reason,
        use_sample_data=use_sample_data
    )
    
    return result


@router.get("/retraining/history")
async def get_retraining_history(
    limit: int = 50,
    event_type: Optional[str] = None,
    pipeline: RetrainingPipeline = Depends(get_retraining_pipeline)
):
    """
    Get retraining history.
    
    **Parameters:**
    - `limit`: Maximum number of events to return (default: 50)
    - `event_type`: Filter by event type ('check', 'retrain', 'deploy', 'error')
    
    **Returns:** List of retraining events with timestamps and metrics
    """
    history = pipeline.get_retraining_history(
        limit=limit,
        event_type=event_type
    )
    
    return {
        "total_events": len(history),
        "events": history
    }


@router.get("/retraining/stats")
async def get_retraining_stats(
    pipeline: RetrainingPipeline = Depends(get_retraining_pipeline)
):
    """
    Get statistics about retraining history.
    
    **Returns:**
    - Total number of retraining events
    - Success/failure rates
    - Average training duration
    - Last retraining timestamp
    """
    stats = pipeline.get_retraining_stats()
    return stats


@router.post("/retraining/schedule")
async def schedule_retraining(
    interval_days: int = 7,
    model_types: List[str] = ["prophet"],
    pipeline: RetrainingPipeline = Depends(get_retraining_pipeline)
):
    """
    Schedule automatic retraining for multiple models.
    
    **Parameters:**
    - `interval_days`: Days between retraining checks (default: 7)
    - `model_types`: List of model types to check (default: ['prophet'])
    
    **Returns:** Schedule results for all models
    
    **Note:** This would typically be called by a cron job or scheduler.
    """
    results = pipeline.schedule_retraining(
        interval_days=interval_days,
        model_types=model_types
    )
    
    return results


@router.get("/monitoring/performance")
async def monitor_model_performance(
    days_back: int = 7,
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Monitor recent model performance.
    
    **Parameters:**
    - `days_back`: Number of days to evaluate (default: 7)
    
    **Returns:** Performance metrics comparing predictions to actual values
    """
    monitor = ModelMonitor(ml_service)
    performance = monitor.evaluate_recent_predictions(days_back=days_back)
    
    return {
        "evaluated_period": {
            "days": days_back,
            "note": "Recent predictions vs actual values"
        },
        "performance": performance
    }


@router.get("/monitoring/drift")
async def detect_model_drift(
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Detect if model has drifted from expected performance.
    
    **Returns:** Drift detection results with confidence score
    
    **Note:** High drift indicates model may need retraining.
    """
    monitor = ModelMonitor(ml_service)
    drift = monitor.detect_model_drift()
    
    return {
        "drift_detection": drift,
        "recommendation": (
            "Consider retraining the model"
            if drift.get('drift_detected')
            else "Model performance is stable"
        )
    }
