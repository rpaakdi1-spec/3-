"""
ML Service for predictive analytics.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import json
import pandas as pd
import numpy as np

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
        
        # Register in model registry
        metadata = {
            'model_type': model_type,
            'trained_at': datetime.utcnow().isoformat(),
            'metrics': metrics.dict(),
            'data_quality': quality,
            'training_params': kwargs
        }
        
        self.registry.register_model(
            model_name='demand_predictor',
            model_path=str(model_path),
            metadata=metadata,
            version=None,  # Auto-generate version
            set_active=True
        )
        
        # Save metadata
        metadata_path = self.model_dir / f"demand_predictor_{model_type}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        return metrics
    
    def train_cost_model(
        self,
        model_type: str = 'random_forest',
        use_sample_data: bool = False,
        **kwargs
    ) -> Dict:
        """
        Train cost prediction model.
        
        Args:
            model_type: 'random_forest' or 'gradient_boosting'
            use_sample_data: Use synthetic data if true
            **kwargs: Additional training parameters
            
        Returns:
            Training metrics
        """
        # Generate or collect cost data
        if use_sample_data:
            # Generate sample cost data
            df = self._generate_sample_cost_data(days=180)
        else:
            # Collect real cost data
            df = self._collect_cost_data(**kwargs)
        
        # Initialize and train model
        self.cost_predictor = CostPredictor(model_type=model_type)
        metrics = self.cost_predictor.train(df, target_column='total_cost')
        
        # Save model
        model_path = self.model_dir / f"cost_predictor_{model_type}.joblib"
        self.cost_predictor.save(str(model_path))
        
        # Register in model registry
        self.registry.register_model(
            model_name='cost_predictor',
            model_path=str(model_path),
            metadata={
                'model_type': model_type,
                'trained_at': datetime.utcnow().isoformat(),
                'metrics': metrics
            },
            set_active=True
        )
        
        return metrics
    
    def train_maintenance_model(
        self,
        use_sample_data: bool = False,
        **kwargs
    ) -> Dict:
        """
        Train maintenance prediction model.
        
        Args:
            use_sample_data: Use synthetic data if true
            **kwargs: Additional training parameters
            
        Returns:
            Training metrics
        """
        # Generate or collect maintenance data
        if use_sample_data:
            df = self._generate_sample_maintenance_data(vehicles=50)
        else:
            df = self._collect_maintenance_data(**kwargs)
        
        # Initialize and train model
        self.maintenance_predictor = MaintenancePredictor()
        metrics = self.maintenance_predictor.train(df, target_column='needs_maintenance')
        
        # Save model
        model_path = self.model_dir / "maintenance_predictor.joblib"
        self.maintenance_predictor.save(str(model_path))
        
        # Register in model registry
        self.registry.register_model(
            model_name='maintenance_predictor',
            model_path=str(model_path),
            metadata={
                'trained_at': datetime.utcnow().isoformat(),
                'metrics': metrics
            },
            set_active=True
        )
        
        return metrics
    
    def _generate_sample_cost_data(self, days: int = 180) -> pd.DataFrame:
        """Generate sample cost data for testing."""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        data = {
            'date': dates,
            'dispatch_count': np.random.randint(15, 35, size=days),
            'distance_km': np.random.uniform(800, 1500, size=days),
            'fuel_liters': np.random.uniform(150, 300, size=days),
            'active_vehicles': np.random.randint(20, 35, size=days),
            'total_vehicles': 40,
            'total_cost': np.random.uniform(500000, 800000, size=days)
        }
        
        return pd.DataFrame(data)
    
    def _generate_sample_maintenance_data(self, vehicles: int = 50) -> pd.DataFrame:
        """Generate sample maintenance data for testing."""
        data = {
            'vehicle_id': range(1, vehicles + 1),
            'vehicle_number': [f'서울{i:02d}가{1000+i}' for i in range(1, vehicles + 1)],
            'vehicle_age_days': np.random.randint(365, 3650, size=vehicles),
            'total_mileage_km': np.random.randint(50000, 300000, size=vehicles),
            'days_since_last_maintenance': np.random.randint(0, 300, size=vehicles),
            'total_trips': np.random.randint(1000, 10000, size=vehicles),
            'total_distance_km': np.random.randint(50000, 300000, size=vehicles),
            'temperature_zone': np.random.choice(['FROZEN', 'CHILLED', 'AMBIENT'], size=vehicles),
            'maintenance_count': np.random.randint(3, 20, size=vehicles),
            'total_maintenance_cost': np.random.uniform(1000000, 5000000, size=vehicles),
            'failure_count': np.random.randint(0, 5, size=vehicles)
        }
        
        df = pd.DataFrame(data)
        
        # Calculate target: needs maintenance if overdue or high mileage
        df['needs_maintenance'] = (
            (df['days_since_last_maintenance'] > 180) |
            (df['total_mileage_km'] > 200000) |
            (df['failure_count'] > 2)
        ).astype(int)
        
        return df
    
    def _collect_cost_data(self, **kwargs) -> pd.DataFrame:
        """Collect real cost data from database."""
        # Implement actual cost data collection from database
        # For now, use sample data
        return self._generate_sample_cost_data()
    
    def _collect_maintenance_data(self, **kwargs) -> pd.DataFrame:
        """Collect real maintenance data from database."""
        # Implement actual maintenance data collection from database
        # For now, use sample data
        return self._generate_sample_maintenance_data()
    
    def predict_costs(
        self,
        operational_data: Dict,
        horizon: int = 30
    ) -> List[Dict]:
        """
        Predict operational costs.
        
        Args:
            operational_data: Current operational metrics
            horizon: Forecast horizon in days
            
        Returns:
            Cost predictions
        """
        if self.cost_predictor is None:
            self.load_cost_model()
        
        # Generate future operational scenarios
        future_data = []
        base_date = datetime.now()
        
        for i in range(horizon):
            date = base_date + timedelta(days=i)
            scenario = operational_data.copy()
            scenario['date'] = date
            future_data.append(scenario)
        
        df = pd.DataFrame(future_data)
        predictions = self.cost_predictor.predict(df, return_confidence=True)
        
        results = []
        for i, (idx, pred) in enumerate(predictions.iterrows()):
            results.append({
                'date': (base_date + timedelta(days=i)).date().isoformat(),
                'predicted_cost': pred['predicted_cost'],
                'prediction_lower': pred.get('prediction_lower', pred['predicted_cost'] * 0.9),
                'prediction_upper': pred.get('prediction_upper', pred['predicted_cost'] * 1.1)
            })
        
        return results
    
    def predict_maintenance(
        self,
        vehicle_data: pd.DataFrame
    ) -> Dict:
        """
        Predict maintenance needs for vehicles.
        
        Args:
            vehicle_data: DataFrame with vehicle operational data
            
        Returns:
            Maintenance predictions and recommendations
        """
        if self.maintenance_predictor is None:
            self.load_maintenance_model()
        
        # Get predictions
        predictions = self.maintenance_predictor.predict(vehicle_data, return_urgency=True)
        
        # Get maintenance schedule
        schedule = self.maintenance_predictor.predict_maintenance_schedule(
            vehicle_data,
            forecast_days=90
        )
        
        # Get insights
        insights = self.maintenance_predictor.get_maintenance_insights(
            predictions,
            vehicle_data
        )
        
        return {
            'predictions': predictions.to_dict('records'),
            'schedule': schedule.to_dict('records'),
            'insights': insights
        }
    
    def load_cost_model(self, version: Optional[str] = None):
        """Load cost prediction model."""
        if version is None:
            # Load active version
            model_version = self.registry.get_active_version('cost_predictor')
            if model_version is None:
                raise ValueError("No active cost predictor model found")
            model_path = model_version.model_path
        else:
            model_version = self.registry.get_version('cost_predictor', version)
            if model_version is None:
                raise ValueError(f"Cost predictor version {version} not found")
            model_path = model_version.model_path
        
        self.cost_predictor = CostPredictor()
        self.cost_predictor.load(model_path)
    
    def load_maintenance_model(self, version: Optional[str] = None):
        """Load maintenance prediction model."""
        if version is None:
            # Load active version
            model_version = self.registry.get_active_version('maintenance_predictor')
            if model_version is None:
                raise ValueError("No active maintenance predictor model found")
            model_path = model_version.model_path
        else:
            model_version = self.registry.get_version('maintenance_predictor', version)
            if model_version is None:
                raise ValueError(f"Maintenance predictor version {version} not found")
            model_path = model_version.model_path
        
        self.maintenance_predictor = MaintenancePredictor()
        self.maintenance_predictor.load(model_path)
    
    def get_all_models_status(self) -> Dict:
        """Get status of all ML models."""
        stats = self.registry.get_registry_stats()
        
        return {
            'registry_stats': stats,
            'loaded_models': {
                'demand_predictor': self.demand_predictor is not None,
                'cost_predictor': self.cost_predictor is not None,
                'maintenance_predictor': self.maintenance_predictor is not None
            },
            'model_directory': str(self.model_dir),
            'timestamp': datetime.utcnow().isoformat()
        }

    # ... existing methods for demand prediction ...
    # (Keep all existing demand prediction methods from original file)
