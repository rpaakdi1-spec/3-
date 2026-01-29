"""
Base class for all ML predictors.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from pydantic import BaseModel


class PredictionResult(BaseModel):
    """Standard prediction result format."""
    
    timestamp: datetime
    predicted_value: float
    confidence_interval_lower: Optional[float] = None
    confidence_interval_upper: Optional[float] = None
    confidence_score: Optional[float] = None
    metadata: Dict[str, Any] = {}


class ModelMetrics(BaseModel):
    """Model performance metrics."""
    
    mae: Optional[float] = None  # Mean Absolute Error
    rmse: Optional[float] = None  # Root Mean Square Error
    mape: Optional[float] = None  # Mean Absolute Percentage Error
    r2_score: Optional[float] = None  # R-squared
    last_trained: Optional[datetime] = None
    training_samples: Optional[int] = None
    features_used: List[str] = []


class BasePredictor(ABC):
    """
    Abstract base class for all predictors.
    
    Provides common functionality for:
    - Data preprocessing
    - Model training
    - Prediction
    - Model evaluation
    - Model persistence
    """
    
    def __init__(self, model_name: str):
        """
        Initialize predictor.
        
        Args:
            model_name: Unique identifier for this model
        """
        self.model_name = model_name
        self.model = None
        self.scaler = None
        self.is_trained = False
        self.metrics: Optional[ModelMetrics] = None
        
    @abstractmethod
    def prepare_features(
        self,
        data: pd.DataFrame,
        target_column: Optional[str] = None
    ) -> Union[pd.DataFrame, tuple[pd.DataFrame, pd.Series]]:
        """
        Prepare features for training or prediction.
        
        Args:
            data: Raw input data
            target_column: Name of target column (for training)
            
        Returns:
            Features DataFrame, or (Features, Target) tuple for training
        """
        pass
    
    @abstractmethod
    def train(
        self,
        data: pd.DataFrame,
        target_column: str,
        **kwargs
    ) -> ModelMetrics:
        """
        Train the model.
        
        Args:
            data: Training data
            target_column: Name of target column
            **kwargs: Additional training parameters
            
        Returns:
            Model performance metrics
        """
        pass
    
    @abstractmethod
    def predict(
        self,
        data: pd.DataFrame,
        horizon: int = 1,
        **kwargs
    ) -> List[PredictionResult]:
        """
        Make predictions.
        
        Args:
            data: Input data for prediction
            horizon: Number of time steps to predict
            **kwargs: Additional prediction parameters
            
        Returns:
            List of prediction results
        """
        pass
    
    def evaluate(
        self,
        actual: pd.Series,
        predicted: pd.Series
    ) -> ModelMetrics:
        """
        Evaluate model performance.
        
        Args:
            actual: Actual values
            predicted: Predicted values
            
        Returns:
            Performance metrics
        """
        # Calculate metrics
        mae = np.mean(np.abs(actual - predicted))
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        
        # MAPE (avoid division by zero)
        mask = actual != 0
        if mask.sum() > 0:
            mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
        else:
            mape = None
        
        # R-squared
        ss_res = np.sum((actual - predicted) ** 2)
        ss_tot = np.sum((actual - np.mean(actual)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else None
        
        return ModelMetrics(
            mae=float(mae),
            rmse=float(rmse),
            mape=float(mape) if mape is not None else None,
            r2_score=float(r2) if r2 is not None else None,
            training_samples=len(actual),
            last_trained=datetime.utcnow()
        )
    
    def save_model(self, path: str) -> None:
        """
        Save model to disk.
        
        Args:
            path: File path to save model
        """
        import joblib
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'metrics': self.metrics.dict() if self.metrics else None,
            'is_trained': self.is_trained,
            'model_name': self.model_name
        }
        
        joblib.dump(model_data, path)
    
    def load_model(self, path: str) -> None:
        """
        Load model from disk.
        
        Args:
            path: File path to load model from
        """
        import joblib
        
        model_data = joblib.load(path)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.is_trained = model_data['is_trained']
        self.model_name = model_data['model_name']
        
        if model_data['metrics']:
            self.metrics = ModelMetrics(**model_data['metrics'])
    
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """
        Get feature importance (if supported by model).
        
        Returns:
            Dictionary of feature names and importance scores
        """
        if hasattr(self.model, 'feature_importances_'):
            return dict(zip(
                self.metrics.features_used,
                self.model.feature_importances_
            ))
        return None


class TimeSeriesPredictor(BasePredictor):
    """
    Base class for time series predictors.
    
    Adds time series specific functionality:
    - Seasonality detection
    - Trend analysis
    - Lag feature generation
    """
    
    def __init__(self, model_name: str, frequency: str = 'D'):
        """
        Initialize time series predictor.
        
        Args:
            model_name: Unique identifier for this model
            frequency: Time series frequency (D=daily, W=weekly, M=monthly)
        """
        super().__init__(model_name)
        self.frequency = frequency
    
    def create_lag_features(
        self,
        data: pd.DataFrame,
        target_column: str,
        lags: List[int]
    ) -> pd.DataFrame:
        """
        Create lag features for time series.
        
        Args:
            data: Input data with datetime index
            target_column: Column to create lags for
            lags: List of lag periods
            
        Returns:
            DataFrame with lag features
        """
        df = data.copy()
        
        for lag in lags:
            df[f'{target_column}_lag_{lag}'] = df[target_column].shift(lag)
        
        return df
    
    def create_rolling_features(
        self,
        data: pd.DataFrame,
        target_column: str,
        windows: List[int]
    ) -> pd.DataFrame:
        """
        Create rolling window features.
        
        Args:
            data: Input data
            target_column: Column to create rolling features for
            windows: List of window sizes
            
        Returns:
            DataFrame with rolling features
        """
        df = data.copy()
        
        for window in windows:
            df[f'{target_column}_rolling_mean_{window}'] = (
                df[target_column].rolling(window=window).mean()
            )
            df[f'{target_column}_rolling_std_{window}'] = (
                df[target_column].rolling(window=window).std()
            )
        
        return df
    
    def detect_seasonality(
        self,
        data: pd.Series,
        period: int
    ) -> bool:
        """
        Detect if data has seasonality.
        
        Args:
            data: Time series data
            period: Period to check (e.g., 7 for weekly, 365 for yearly)
            
        Returns:
            True if seasonality detected
        """
        from scipy import stats
        
        # Simple autocorrelation check
        if len(data) < period * 2:
            return False
        
        acf_value = data.autocorr(lag=period)
        
        # If autocorrelation at seasonal period is significant (> 0.5)
        return abs(acf_value) > 0.5 if not np.isnan(acf_value) else False
