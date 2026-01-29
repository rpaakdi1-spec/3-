"""
Demand Prediction Model using Prophet and LSTM.

Predicts future demand for dispatches based on historical data.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from .base import TimeSeriesPredictor, PredictionResult, ModelMetrics


class DemandPredictor(TimeSeriesPredictor):
    """
    Demand prediction using Facebook Prophet.
    
    Predicts:
    - Daily/weekly/monthly dispatch demand
    - Seasonal patterns
    - Holiday effects
    - Trend changes
    """
    
    def __init__(self, model_type: str = 'prophet'):
        """
        Initialize demand predictor.
        
        Args:
            model_type: 'prophet' or 'lstm'
        """
        super().__init__(model_name='demand_predictor', frequency='D')
        self.model_type = model_type
        self.holidays = None
        
    def prepare_features(
        self,
        data: pd.DataFrame,
        target_column: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Prepare features for demand prediction.
        
        Expected columns:
        - date: datetime
        - dispatch_count: number of dispatches
        - temperature: optional weather data
        - is_holiday: optional holiday indicator
        
        Args:
            data: Raw dispatch data
            target_column: Target column name
            
        Returns:
            Prepared features DataFrame
        """
        df = data.copy()
        
        # Ensure datetime index
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
        
        # Add time-based features
        df['day_of_week'] = df.index.dayofweek
        df['day_of_month'] = df.index.day
        df['month'] = df.index.month
        df['quarter'] = df.index.quarter
        df['year'] = df.index.year
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_month_start'] = df.index.is_month_start.astype(int)
        df['is_month_end'] = df.index.is_month_end.astype(int)
        
        # Add lag features (previous 1, 7, 14, 30 days)
        if target_column and target_column in df.columns:
            df = self.create_lag_features(
                df,
                target_column,
                lags=[1, 7, 14, 30]
            )
            
            # Add rolling statistics
            df = self.create_rolling_features(
                df,
                target_column,
                windows=[7, 14, 30]
            )
        
        return df
    
    def train(
        self,
        data: pd.DataFrame,
        target_column: str = 'dispatch_count',
        **kwargs
    ) -> ModelMetrics:
        """
        Train demand prediction model.
        
        Args:
            data: Historical dispatch data
            target_column: Target column to predict
            **kwargs: Additional parameters
                - holidays: DataFrame with holiday dates
                - seasonality_mode: 'additive' or 'multiplicative'
                - changepoint_prior_scale: Flexibility of trend (default 0.05)
                
        Returns:
            Model performance metrics
        """
        if self.model_type == 'prophet':
            return self._train_prophet(data, target_column, **kwargs)
        elif self.model_type == 'lstm':
            return self._train_lstm(data, target_column, **kwargs)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def _train_prophet(
        self,
        data: pd.DataFrame,
        target_column: str,
        **kwargs
    ) -> ModelMetrics:
        """Train using Facebook Prophet."""
        try:
            from prophet import Prophet
        except ImportError:
            raise ImportError("Prophet not installed. Install with: pip install prophet")
        
        # Prepare data for Prophet (needs 'ds' and 'y' columns)
        df = data.copy()
        if not isinstance(df.index, pd.DatetimeIndex):
            df['ds'] = pd.to_datetime(df['date'])
        else:
            df['ds'] = df.index
        
        df['y'] = df[target_column]
        df = df[['ds', 'y']].dropna()
        
        # Initialize Prophet model
        self.model = Prophet(
            seasonality_mode=kwargs.get('seasonality_mode', 'additive'),
            changepoint_prior_scale=kwargs.get('changepoint_prior_scale', 0.05),
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True
        )
        
        # Add holidays if provided
        if 'holidays' in kwargs and kwargs['holidays'] is not None:
            self.model.add_country_holidays(country_name='KR')  # South Korea holidays
        
        # Add additional regressors if available
        if 'temperature' in data.columns:
            self.model.add_regressor('temperature')
            df['temperature'] = data['temperature']
        
        # Train model
        self.model.fit(df)
        self.is_trained = True
        
        # Evaluate on training data
        forecast = self.model.predict(df)
        actual = df['y']
        predicted = forecast['yhat']
        
        self.metrics = self.evaluate(actual, predicted)
        self.metrics.features_used = ['ds'] + (
            ['temperature'] if 'temperature' in data.columns else []
        )
        self.metrics.last_trained = datetime.utcnow()
        
        return self.metrics
    
    def _train_lstm(
        self,
        data: pd.DataFrame,
        target_column: str,
        **kwargs
    ) -> ModelMetrics:
        """Train using LSTM neural network."""
        try:
            import tensorflow as tf
            from tensorflow import keras
            from sklearn.preprocessing import MinMaxScaler
        except ImportError:
            raise ImportError("TensorFlow not installed. Install with: pip install tensorflow")
        
        # Prepare features
        df = self.prepare_features(data, target_column)
        df = df.dropna()
        
        # Select features for LSTM
        feature_cols = [
            target_column,
            'day_of_week',
            'month',
            'is_weekend'
        ]
        
        # Add lag features if available
        lag_cols = [col for col in df.columns if 'lag' in col or 'rolling' in col]
        feature_cols.extend(lag_cols)
        
        X = df[feature_cols].values
        y = df[target_column].values
        
        # Scale data
        self.scaler = MinMaxScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Prepare sequences for LSTM
        sequence_length = kwargs.get('sequence_length', 30)
        X_sequences, y_sequences = self._create_sequences(
            X_scaled,
            y,
            sequence_length
        )
        
        # Split train/validation
        train_size = int(len(X_sequences) * 0.8)
        X_train = X_sequences[:train_size]
        X_val = X_sequences[train_size:]
        y_train = y_sequences[:train_size]
        y_val = y_sequences[train_size:]
        
        # Build LSTM model
        self.model = keras.Sequential([
            keras.layers.LSTM(
                units=kwargs.get('lstm_units', 50),
                activation='relu',
                return_sequences=True,
                input_shape=(sequence_length, X.shape[1])
            ),
            keras.layers.Dropout(0.2),
            keras.layers.LSTM(units=kwargs.get('lstm_units', 50), activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(1)
        ])
        
        self.model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        # Train model
        history = self.model.fit(
            X_train,
            y_train,
            validation_data=(X_val, y_val),
            epochs=kwargs.get('epochs', 50),
            batch_size=kwargs.get('batch_size', 32),
            verbose=0
        )
        
        self.is_trained = True
        
        # Evaluate
        y_pred = self.model.predict(X_val).flatten()
        self.metrics = self.evaluate(pd.Series(y_val), pd.Series(y_pred))
        self.metrics.features_used = feature_cols
        self.metrics.last_trained = datetime.utcnow()
        
        return self.metrics
    
    def predict(
        self,
        data: Optional[pd.DataFrame] = None,
        horizon: int = 30,
        **kwargs
    ) -> List[PredictionResult]:
        """
        Predict future demand.
        
        Args:
            data: Optional recent data for context (for LSTM)
            horizon: Number of days to forecast
            **kwargs: Additional parameters
            
        Returns:
            List of prediction results
        """
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        if self.model_type == 'prophet':
            return self._predict_prophet(horizon, **kwargs)
        elif self.model_type == 'lstm':
            return self._predict_lstm(data, horizon, **kwargs)
    
    def _predict_prophet(
        self,
        horizon: int,
        **kwargs
    ) -> List[PredictionResult]:
        """Predict using Prophet."""
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=horizon)
        
        # Add regressors if needed
        if 'temperature' in kwargs:
            future['temperature'] = kwargs['temperature']
        
        # Make prediction
        forecast = self.model.predict(future)
        
        # Get only future predictions
        forecast = forecast.tail(horizon)
        
        # Convert to PredictionResult format
        results = []
        for _, row in forecast.iterrows():
            results.append(PredictionResult(
                timestamp=row['ds'],
                predicted_value=row['yhat'],
                confidence_interval_lower=row['yhat_lower'],
                confidence_interval_upper=row['yhat_upper'],
                confidence_score=(
                    1 - (row['yhat_upper'] - row['yhat_lower']) / (2 * row['yhat'])
                    if row['yhat'] > 0 else 0.5
                ),
                metadata={
                    'trend': row['trend'],
                    'seasonal': row['seasonal'] if 'seasonal' in row else None
                }
            ))
        
        return results
    
    def _predict_lstm(
        self,
        data: pd.DataFrame,
        horizon: int,
        **kwargs
    ) -> List[PredictionResult]:
        """Predict using LSTM."""
        # Prepare features
        df = self.prepare_features(data, target_column='dispatch_count')
        
        # Make predictions (simplified - actual implementation would be more complex)
        # This is a placeholder for proper LSTM forecasting
        results = []
        last_date = df.index[-1]
        
        for i in range(horizon):
            pred_date = last_date + timedelta(days=i+1)
            # Simplified prediction - real implementation would use rolling window
            predicted_value = df['dispatch_count'].mean()
            
            results.append(PredictionResult(
                timestamp=pred_date,
                predicted_value=predicted_value,
                confidence_score=0.7,
                metadata={'model': 'lstm'}
            ))
        
        return results
    
    def _create_sequences(
        self,
        X: np.ndarray,
        y: np.ndarray,
        sequence_length: int
    ) -> tuple:
        """Create sequences for LSTM training."""
        X_sequences = []
        y_sequences = []
        
        for i in range(len(X) - sequence_length):
            X_sequences.append(X[i:i+sequence_length])
            y_sequences.append(y[i+sequence_length])
        
        return np.array(X_sequences), np.array(y_sequences)
    
    def get_seasonality_components(self) -> Optional[Dict[str, Any]]:
        """
        Get seasonality components (Prophet only).
        
        Returns:
            Dictionary with weekly, yearly seasonality data
        """
        if self.model_type != 'prophet' or not self.is_trained:
            return None
        
        # Extract seasonality from Prophet model
        components = {
            'weekly': self.model.weekly_seasonality,
            'yearly': self.model.yearly_seasonality,
            'daily': self.model.daily_seasonality
        }
        
        return components
