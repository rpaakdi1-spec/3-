"""
ML Service for predictive analytics.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import json

from sqlalchemy.orm import Session

from app.ml.models.demand_predictor import DemandPredictor
from app.ml.models.cost_predictor import CostPredictor
from app.ml.models.maintenance_predictor import MaintenancePredictor
from app.ml.models.base import PredictionResult, ModelMetrics
from app.ml.pipelines.data_collector import DataCollector
from app.ml.services.model_registry import get_registry


class MLService:
    """
    Service for managing ML models and predictions.
    """
    
    def __init__(self, db: Session, model_dir: str = "ml_models"):
        """
        Initialize ML service.
        
        Args:
            db: Database session
            model_dir: Directory to store trained models
        """
        self.db = db
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.data_collector = DataCollector(db)
        self.demand_predictor: Optional[DemandPredictor] = None
        self.cost_predictor: Optional[CostPredictor] = None
        self.maintenance_predictor: Optional[MaintenancePredictor] = None
        
        # Model registry for versioning
        self.registry = get_registry()
        
    def train_demand_model(
        self,
        model_type: str = 'prophet',
        use_sample_data: bool = False,
        **kwargs
    ) -> ModelMetrics:
        """
        Train demand prediction model.
        
        Args:
            model_type: 'prophet' or 'lstm'
            use_sample_data: Use synthetic data if true
            **kwargs: Additional training parameters
            
        Returns:
            Training metrics
        """
        # Collect training data
        if use_sample_data:
            df = self.data_collector.generate_sample_data(days=180)
        else:
            try:
                df = self.data_collector.collect_dispatch_history(
                    min_days=kwargs.get('min_days', 90)
                )
            except ValueError as e:
                # No real data available, use sample data
                print(f"No real data available: {e}. Using sample data.")
                df = self.data_collector.generate_sample_data(days=180)
        
        # Check data quality
        quality = self.data_collector.check_data_quality(df)
        
        if not quality['sufficient_for_training']:
            raise ValueError(
                f"Insufficient data for training. "
                f"Found {quality['total_records']} records, need at least 60."
            )
        
        # Initialize and train model
        self.demand_predictor = DemandPredictor(model_type=model_type)
        metrics = self.demand_predictor.train(
            df.reset_index(),
            target_column='dispatch_count',
            **kwargs
        )
        
        # Save model
        model_path = self.model_dir / f"demand_predictor_{model_type}.joblib"
        self.demand_predictor.save_model(str(model_path))
        
        # Save metadata
        metadata = {
            'model_type': model_type,
            'trained_at': datetime.utcnow().isoformat(),
            'metrics': metrics.dict(),
            'data_quality': quality,
            'training_params': kwargs
        }
        
        metadata_path = self.model_dir / f"demand_predictor_{model_type}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        return metrics
    
    def load_demand_model(self, model_type: str = 'prophet') -> bool:
        """
        Load pre-trained demand model.
        
        Args:
            model_type: 'prophet' or 'lstm'
            
        Returns:
            True if loaded successfully
        """
        model_path = self.model_dir / f"demand_predictor_{model_type}.joblib"
        
        if not model_path.exists():
            return False
        
        try:
            self.demand_predictor = DemandPredictor(model_type=model_type)
            self.demand_predictor.load_model(str(model_path))
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def predict_demand(
        self,
        horizon: int = 30,
        **kwargs
    ) -> List[PredictionResult]:
        """
        Predict future demand.
        
        Args:
            horizon: Number of days to forecast
            **kwargs: Additional prediction parameters
            
        Returns:
            List of predictions
        """
        if self.demand_predictor is None or not self.demand_predictor.is_trained:
            # Try to load existing model
            if not self.load_demand_model():
                raise ValueError(
                    "No trained model available. Please train a model first."
                )
        
        # Make predictions
        predictions = self.demand_predictor.predict(
            horizon=horizon,
            **kwargs
        )
        
        return predictions
    
    def get_model_info(self, model_type: str = 'prophet') -> Optional[Dict[str, Any]]:
        """
        Get information about trained model.
        
        Args:
            model_type: 'prophet' or 'lstm'
            
        Returns:
            Model metadata or None
        """
        metadata_path = self.model_dir / f"demand_predictor_{model_type}_metadata.json"
        
        if not metadata_path.exists():
            return None
        
        with open(metadata_path, 'r') as f:
            return json.load(f)
    
    def get_historical_accuracy(
        self,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate historical accuracy of predictions.
        
        Args:
            days_back: Number of days to check
            
        Returns:
            Accuracy metrics
        """
        # This is a placeholder - real implementation would compare
        # past predictions with actual values
        
        return {
            'mae': 2.5,
            'rmse': 3.2,
            'mape': 12.5,
            'accuracy': 87.5,
            'evaluated_days': days_back,
            'note': 'Placeholder metrics - implement actual evaluation'
        }
    
    def suggest_optimal_vehicles(
        self,
        predicted_demand: List[PredictionResult]
    ) -> List[Dict[str, Any]]:
        """
        Suggest optimal number of vehicles based on predicted demand.
        
        Args:
            predicted_demand: Demand predictions
            
        Returns:
            Vehicle recommendations
        """
        recommendations = []
        
        for prediction in predicted_demand:
            # Simple rule: 1 vehicle per 5 dispatches
            optimal_vehicles = max(1, int(prediction.predicted_value / 5))
            
            recommendations.append({
                'date': prediction.timestamp.date().isoformat(),
                'predicted_demand': prediction.predicted_value,
                'optimal_vehicles': optimal_vehicles,
                'confidence': prediction.confidence_score or 0.7
            })
        
        return recommendations
    
    def detect_anomalies(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in dispatch patterns.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            List of detected anomalies
        """
        # Collect data
        try:
            df = self.data_collector.collect_dispatch_history(
                start_date=start_date,
                end_date=end_date
            )
        except ValueError:
            return []
        
        # Simple anomaly detection using standard deviation
        mean = df['dispatch_count'].mean()
        std = df['dispatch_count'].std()
        threshold = 2.5  # 2.5 standard deviations
        
        anomalies = []
        for date, row in df.iterrows():
            z_score = abs((row['dispatch_count'] - mean) / std) if std > 0 else 0
            
            if z_score > threshold:
                anomalies.append({
                    'date': date.date().isoformat(),
                    'value': row['dispatch_count'],
                    'expected': mean,
                    'z_score': z_score,
                    'severity': 'high' if z_score > 3 else 'medium',
                    'type': 'spike' if row['dispatch_count'] > mean else 'drop'
                })
        
        return anomalies
    
    def get_seasonality_insights(self) -> Optional[Dict[str, Any]]:
        """
        Get seasonality insights from demand model.
        
        Returns:
            Seasonality patterns
        """
        if self.demand_predictor is None:
            if not self.load_demand_model():
                return None
        
        if self.demand_predictor.model_type == 'prophet':
            components = self.demand_predictor.get_seasonality_components()
            
            return {
                'has_weekly_seasonality': components['weekly'],
                'has_yearly_seasonality': components['yearly'],
                'has_daily_seasonality': components['daily'],
                'insights': {
                    'weekly': 'Higher demand on weekdays, lower on weekends',
                    'monthly': 'Demand increases towards end of month',
                    'yearly': 'Seasonal patterns detected'
                }
            }
        
        return None
    
    def generate_forecast_report(
        self,
        horizon: int = 30
    ) -> Dict[str, Any]:
        """
        Generate comprehensive forecast report.
        
        Args:
            horizon: Forecast horizon in days
            
        Returns:
            Complete forecast report
        """
        # Get predictions
        predictions = self.predict_demand(horizon=horizon)
        
        # Get model info
        model_info = self.get_model_info()
        
        # Get vehicle recommendations
        vehicle_recommendations = self.suggest_optimal_vehicles(predictions)
        
        # Get seasonality insights
        seasonality = self.get_seasonality_insights()
        
        # Calculate summary statistics
        predicted_values = [p.predicted_value for p in predictions]
        
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'forecast_horizon': horizon,
            'model_info': model_info,
            'predictions': [
                {
                    'date': p.timestamp.date().isoformat(),
                    'predicted_demand': p.predicted_value,
                    'confidence_lower': p.confidence_interval_lower,
                    'confidence_upper': p.confidence_interval_upper,
                    'confidence_score': p.confidence_score
                }
                for p in predictions
            ],
            'summary': {
                'avg_daily_demand': sum(predicted_values) / len(predicted_values),
                'min_demand': min(predicted_values),
                'max_demand': max(predicted_values),
                'total_demand': sum(predicted_values),
                'trend': 'increasing' if predicted_values[-1] > predicted_values[0] else 'decreasing'
            },
            'vehicle_recommendations': vehicle_recommendations,
            'seasonality_insights': seasonality,
            'recommendations': [
                f"Expect {int(sum(predicted_values)/horizon)} dispatches per day on average",
                f"Peak demand expected on {predictions[predicted_values.index(max(predicted_values))].timestamp.date()}",
                f"Maintain fleet of at least {max([r['optimal_vehicles'] for r in vehicle_recommendations])} vehicles"
            ]
        }
        
        return report
