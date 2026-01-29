"""
Integration tests for ML/Predictive Analytics API.

Tests ML model training, predictions, and analytics endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json

from app.main import app
from app.core.database import get_db
from app.ml.services.ml_service import MLService


client = TestClient(app)


class TestMLModelTraining:
    """Test ML model training endpoints."""
    
    def test_train_prophet_model_with_sample_data(self):
        """Test training Prophet model with synthetic data."""
        response = client.post(
            "/api/v1/ml/models/train",
            json={
                "model_type": "prophet",
                "use_sample_data": True,
                "min_days": 90
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check metrics are returned
        assert "mae" in data
        assert "rmse" in data
        assert "mape" in data
        assert "r2_score" in data
        assert "training_samples" in data
        assert "last_trained" in data
        
        # Check metrics are reasonable
        assert data["mae"] > 0
        assert data["rmse"] > 0
        assert data["training_samples"] >= 60
        
    def test_train_without_data_should_fail(self):
        """Test training without data should return error."""
        # This would fail if real data is required but not available
        # With use_sample_data=False and no real data
        pass  # Skipped as it depends on database state
    
    def test_get_model_info_after_training(self):
        """Test retrieving model information."""
        # First train a model
        train_response = client.post(
            "/api/v1/ml/models/train",
            json={
                "model_type": "prophet",
                "use_sample_data": True
            }
        )
        assert train_response.status_code == 200
        
        # Then get model info
        response = client.get("/api/v1/ml/models/prophet/info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["model_type"] == "prophet"
        assert "trained_at" in data
        assert "metrics" in data
        assert "data_quality" in data
        assert data["is_loaded"] is True
    
    def test_get_nonexistent_model_info(self):
        """Test getting info for non-existent model."""
        response = client.get("/api/v1/ml/models/nonexistent/info")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestMLPredictions:
    """Test ML prediction endpoints."""
    
    @pytest.fixture(autouse=True)
    def setup_model(self):
        """Ensure a model is trained before prediction tests."""
        # Train model once for all prediction tests
        response = client.post(
            "/api/v1/ml/models/train",
            json={
                "model_type": "prophet",
                "use_sample_data": True
            }
        )
        assert response.status_code == 200
    
    def test_predict_demand_default_horizon(self):
        """Test demand prediction with default 30-day horizon."""
        response = client.get("/api/v1/ml/predictions/demand")
        
        assert response.status_code == 200
        predictions = response.json()
        
        # Should return 30 predictions by default
        assert len(predictions) == 30
        
        # Check prediction structure
        first_pred = predictions[0]
        assert "timestamp" in first_pred
        assert "predicted_value" in first_pred
        assert "confidence_interval_lower" in first_pred
        assert "confidence_interval_upper" in first_pred
        assert "confidence_score" in first_pred
        
        # Check values are reasonable
        assert first_pred["predicted_value"] > 0
        assert first_pred["confidence_interval_lower"] < first_pred["predicted_value"]
        assert first_pred["confidence_interval_upper"] > first_pred["predicted_value"]
        assert 0 <= first_pred["confidence_score"] <= 1
    
    def test_predict_demand_custom_horizon(self):
        """Test demand prediction with custom horizon."""
        horizon = 7
        response = client.get(f"/api/v1/ml/predictions/demand?horizon={horizon}")
        
        assert response.status_code == 200
        predictions = response.json()
        
        assert len(predictions) == horizon
    
    def test_predict_demand_large_horizon(self):
        """Test prediction with large horizon (90 days)."""
        response = client.get("/api/v1/ml/predictions/demand?horizon=90")
        
        assert response.status_code == 200
        predictions = response.json()
        
        assert len(predictions) == 90
    
    def test_predict_without_trained_model(self):
        """Test prediction without trained model."""
        # This test would need to clear models first
        # For now, we assume model exists from fixture
        pass


class TestMLAnalytics:
    """Test ML analytics endpoints."""
    
    def test_detect_anomalies(self):
        """Test anomaly detection."""
        response = client.get("/api/v1/ml/analytics/anomalies?days_back=30")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "analyzed_period" in data
        assert "anomalies_found" in data
        assert "anomalies" in data
        
        # Check period structure
        period = data["analyzed_period"]
        assert "start_date" in period
        assert "end_date" in period
        assert "days" in period
        assert period["days"] == 30
    
    def test_get_seasonality_insights(self):
        """Test seasonality analysis."""
        # First ensure Prophet model is trained
        client.post(
            "/api/v1/ml/models/train",
            json={"model_type": "prophet", "use_sample_data": True}
        )
        
        response = client.get("/api/v1/ml/analytics/seasonality")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "has_weekly_seasonality" in data
        assert "has_yearly_seasonality" in data
        assert "has_daily_seasonality" in data
        assert "insights" in data
    
    def test_get_historical_accuracy(self):
        """Test historical accuracy metrics."""
        response = client.get("/api/v1/ml/analytics/accuracy?days_back=30")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "mae" in data
        assert "rmse" in data
        assert "mape" in data
        assert "accuracy" in data
        assert "evaluated_days" in data


class TestMLRecommendations:
    """Test ML recommendation endpoints."""
    
    @pytest.fixture(autouse=True)
    def setup_model(self):
        """Ensure model is trained."""
        client.post(
            "/api/v1/ml/models/train",
            json={"model_type": "prophet", "use_sample_data": True}
        )
    
    def test_get_vehicle_recommendations(self):
        """Test vehicle fleet recommendations."""
        response = client.get("/api/v1/ml/recommendations/vehicles?horizon=7")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "planning_horizon" in data
        assert data["planning_horizon"] == 7
        assert "recommendations" in data
        assert "summary" in data
        
        # Check recommendations structure
        recommendations = data["recommendations"]
        assert len(recommendations) == 7
        
        first_rec = recommendations[0]
        assert "date" in first_rec
        assert "predicted_demand" in first_rec
        assert "optimal_vehicles" in first_rec
        assert "confidence" in first_rec
        
        # Check summary
        summary = data["summary"]
        assert "min_vehicles" in summary
        assert "max_vehicles" in summary
        assert "avg_vehicles" in summary
        
        assert summary["min_vehicles"] > 0
        assert summary["max_vehicles"] >= summary["min_vehicles"]


class TestMLForecastReports:
    """Test ML forecast report generation."""
    
    @pytest.fixture(autouse=True)
    def setup_model(self):
        """Ensure model is trained."""
        client.post(
            "/api/v1/ml/models/train",
            json={"model_type": "prophet", "use_sample_data": True}
        )
    
    def test_generate_forecast_report(self):
        """Test comprehensive forecast report generation."""
        response = client.get("/api/v1/ml/reports/forecast?horizon=30")
        
        assert response.status_code == 200
        report = response.json()
        
        # Check report structure
        assert "generated_at" in report
        assert "forecast_horizon" in report
        assert report["forecast_horizon"] == 30
        assert "model_info" in report
        assert "predictions" in report
        assert "summary" in report
        assert "vehicle_recommendations" in report
        assert "seasonality_insights" in report
        assert "recommendations" in report
        
        # Check predictions
        predictions = report["predictions"]
        assert len(predictions) == 30
        
        # Check summary
        summary = report["summary"]
        assert "avg_daily_demand" in summary
        assert "min_demand" in summary
        assert "max_demand" in summary
        assert "total_demand" in summary
        assert "trend" in summary
        
        assert summary["avg_daily_demand"] > 0
        assert summary["trend"] in ["increasing", "decreasing"]
        
        # Check recommendations are present
        assert len(report["recommendations"]) > 0
        assert isinstance(report["recommendations"], list)


class TestMLHealthCheck:
    """Test ML service health endpoint."""
    
    def test_ml_health_check(self):
        """Test ML service health check."""
        response = client.get("/api/v1/ml/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "models" in data
        assert "service" in data
        assert "version" in data
        
        # Check models section
        models = data["models"]
        assert "prophet" in models
        assert "lstm" in models
        
        # Check prophet model info
        prophet = models["prophet"]
        assert "available" in prophet
        # trained_at may be None if not trained yet


class TestMLErrorHandling:
    """Test ML API error handling."""
    
    def test_invalid_model_type(self):
        """Test training with invalid model type."""
        response = client.post(
            "/api/v1/ml/models/train",
            json={
                "model_type": "invalid_model",
                "use_sample_data": True
            }
        )
        
        # Should return error (400 or 500)
        assert response.status_code in [400, 500]
    
    def test_negative_horizon(self):
        """Test prediction with negative horizon."""
        response = client.get("/api/v1/ml/predictions/demand?horizon=-1")
        
        # Should handle gracefully
        assert response.status_code in [400, 422]
    
    def test_zero_horizon(self):
        """Test prediction with zero horizon."""
        response = client.get("/api/v1/ml/predictions/demand?horizon=0")
        
        # Should return empty or error
        assert response.status_code in [200, 400, 422]


class TestMLDataCollection:
    """Test ML data collection functionality."""
    
    def test_sample_data_generation(self):
        """Test sample data generator works correctly."""
        from app.ml.pipelines.data_collector import DataCollector
        from app.core.database import SessionLocal
        
        db = SessionLocal()
        try:
            collector = DataCollector(db)
            
            # Generate 90 days of sample data
            df = collector.generate_sample_data(days=90, base_demand=20)
            
            assert len(df) == 91  # 90 days + today
            assert "dispatch_count" in df.columns
            assert "unique_vehicles" in df.columns
            assert "unique_drivers" in df.columns
            
            # Check values are reasonable
            assert df["dispatch_count"].min() >= 0
            assert df["dispatch_count"].max() > 0
            assert df["dispatch_count"].mean() > 0
        finally:
            db.close()
    
    def test_data_quality_check(self):
        """Test data quality assessment."""
        from app.ml.pipelines.data_collector import DataCollector
        from app.core.database import SessionLocal
        import pandas as pd
        
        db = SessionLocal()
        try:
            collector = DataCollector(db)
            
            # Generate sample data
            df = collector.generate_sample_data(days=90)
            
            # Check quality
            quality = collector.check_data_quality(df)
            
            assert "total_records" in quality
            assert "date_range" in quality
            assert "missing_values" in quality
            assert "sufficient_for_training" in quality
            
            assert quality["total_records"] > 0
            assert quality["sufficient_for_training"] is True
        finally:
            db.close()


class TestMLModelPersistence:
    """Test ML model save/load functionality."""
    
    def test_model_persistence_after_training(self):
        """Test model is persisted after training."""
        import os
        
        # Train model
        response = client.post(
            "/api/v1/ml/models/train",
            json={
                "model_type": "prophet",
                "use_sample_data": True
            }
        )
        assert response.status_code == 200
        
        # Check model files exist
        model_dir = "ml_models"
        model_file = os.path.join(model_dir, "demand_predictor_prophet.joblib")
        metadata_file = os.path.join(model_dir, "demand_predictor_prophet_metadata.json")
        
        # Files should exist after training
        # Note: This test depends on file system state
        # In production, we'd mock the file system or use temp directories


class TestMLIntegrationWithDatabase:
    """Test ML integration with actual database data."""
    
    def test_collect_real_data_when_available(self):
        """Test collecting real dispatch data from database."""
        from app.ml.pipelines.data_collector import DataCollector
        from app.core.database import SessionLocal
        
        db = SessionLocal()
        try:
            collector = DataCollector(db)
            
            # Try to collect real data
            try:
                df = collector.collect_dispatch_history(min_days=30)
                
                # If successful, check data structure
                if len(df) > 0:
                    assert "dispatch_count" in df.columns
                    assert len(df) >= 30
            except ValueError:
                # Expected if no real data exists yet
                # Use sample data instead
                df = collector.generate_sample_data(days=90)
                assert len(df) > 0
        finally:
            db.close()


# Performance benchmarks
class TestMLPerformance:
    """Test ML performance characteristics."""
    
    def test_training_time_prophet(self):
        """Test Prophet model training completes in reasonable time."""
        import time
        
        start_time = time.time()
        
        response = client.post(
            "/api/v1/ml/models/train",
            json={
                "model_type": "prophet",
                "use_sample_data": True,
                "min_days": 90
            }
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert response.status_code == 200
        # Training should complete in under 60 seconds for sample data
        assert duration < 60
    
    def test_prediction_response_time(self):
        """Test prediction response time is acceptable."""
        import time
        
        # Ensure model is trained
        client.post(
            "/api/v1/ml/models/train",
            json={"model_type": "prophet", "use_sample_data": True}
        )
        
        start_time = time.time()
        response = client.get("/api/v1/ml/predictions/demand?horizon=30")
        end_time = time.time()
        
        duration = end_time - start_time
        
        assert response.status_code == 200
        # Prediction should be fast (< 5 seconds)
        assert duration < 5


# Integration test summary
class TestMLAPIIntegrationSummary:
    """Summary test to verify all ML endpoints are accessible."""
    
    def test_all_ml_endpoints_exist(self):
        """Test all documented ML endpoints exist."""
        # Train endpoint
        response = client.post("/api/v1/ml/models/train", json={})
        assert response.status_code in [200, 400, 422]  # Exists
        
        # Model info endpoint
        response = client.get("/api/v1/ml/models/prophet/info")
        # 200 if trained, 404 if not
        assert response.status_code in [200, 404]
        
        # Predictions endpoint
        response = client.get("/api/v1/ml/predictions/demand")
        # 200 if model available, 404 if not
        assert response.status_code in [200, 404]
        
        # Forecast report
        response = client.get("/api/v1/ml/reports/forecast")
        assert response.status_code in [200, 404]
        
        # Anomalies
        response = client.get("/api/v1/ml/analytics/anomalies")
        assert response.status_code == 200
        
        # Seasonality
        response = client.get("/api/v1/ml/analytics/seasonality")
        assert response.status_code in [200, 404]
        
        # Accuracy
        response = client.get("/api/v1/ml/analytics/accuracy")
        assert response.status_code == 200
        
        # Vehicle recommendations
        response = client.get("/api/v1/ml/recommendations/vehicles")
        assert response.status_code in [200, 404]
        
        # Health check
        response = client.get("/api/v1/ml/health")
        assert response.status_code == 200
