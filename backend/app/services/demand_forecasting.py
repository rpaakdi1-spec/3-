"""
Demand Forecasting ML Model - Phase 8.3
Predicts future order volumes using time series analysis
"""
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


class DemandForecaster:
    """
    Time series forecasting for order demand prediction
    Uses Gradient Boosting with temporal features
    """
    
    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=150,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.historical_data = []
    
    def prepare_time_features(self, date: datetime) -> List[float]:
        """
        Extract temporal features from date
        
        Args:
            date: Target date for prediction
            
        Returns:
            List of temporal features
        """
        features = [
            date.year,
            date.month,
            date.day,
            date.weekday(),
            date.hour if hasattr(date, 'hour') else 12,
            1 if date.weekday() >= 5 else 0,  # Is weekend
            1 if date.month in [6, 7, 8] else 0,  # Is summer
            1 if date.month in [12, 1, 2] else 0,  # Is winter
            date.timetuple().tm_yday,  # Day of year
        ]
        return features
    
    def add_historical_data(self, date: datetime, order_count: int):
        """
        Add historical order data for training
        
        Args:
            date: Date of orders
            order_count: Number of orders on that date
        """
        self.historical_data.append({
            'date': date,
            'count': order_count,
        })
    
    def train(self, historical_data: Optional[List[Dict]] = None):
        """
        Train demand forecasting model
        
        Args:
            historical_data: Optional list of historical data
        """
        if historical_data:
            self.historical_data = historical_data
        
        if len(self.historical_data) < 30:
            logger.warning("Insufficient data for training (minimum 30 days)")
            return False
        
        # Prepare features and targets
        X = []
        y = []
        
        for data in self.historical_data:
            features = self.prepare_time_features(data['date'])
            X.append(features)
            y.append(data['count'])
        
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Calculate score
        score = self.model.score(X_scaled, y)
        logger.info(f"Demand forecasting model trained with R² score: {score:.4f}")
        
        return True
    
    def forecast(self, target_date: datetime, days_ahead: int = 7) -> List[Dict]:
        """
        Forecast demand for upcoming days
        
        Args:
            target_date: Starting date for forecast
            days_ahead: Number of days to forecast
            
        Returns:
            List of forecasted demands
        """
        if not self.is_trained:
            logger.warning("Model not trained, using historical average")
            return self._fallback_forecast(target_date, days_ahead)
        
        forecasts = []
        
        for i in range(days_ahead):
            date = target_date + timedelta(days=i)
            features = self.prepare_time_features(date)
            X = np.array(features).reshape(1, -1)
            X_scaled = self.scaler.transform(X)
            
            predicted_count = max(0, int(self.model.predict(X_scaled)[0]))
            
            forecasts.append({
                'date': date.strftime('%Y-%m-%d'),
                'predicted_orders': predicted_count,
                'confidence': self._calculate_confidence(date),
            })
        
        return forecasts
    
    def _calculate_confidence(self, date: datetime) -> float:
        """
        Calculate forecast confidence based on historical data density
        
        Args:
            date: Target date
            
        Returns:
            Confidence score (0-1)
        """
        # Check how many similar historical dates we have
        similar_count = sum(
            1 for data in self.historical_data
            if data['date'].weekday() == date.weekday()
        )
        
        # More similar dates = higher confidence
        confidence = min(0.95, 0.5 + (similar_count / len(self.historical_data)))
        return round(confidence, 2)
    
    def _fallback_forecast(self, target_date: datetime, days_ahead: int) -> List[Dict]:
        """
        Fallback forecasting using historical averages
        
        Args:
            target_date: Starting date
            days_ahead: Number of days to forecast
            
        Returns:
            List of forecasted demands
        """
        if not self.historical_data:
            # Use default values
            avg_weekday = 25
            avg_weekend = 15
        else:
            # Calculate averages from historical data
            weekday_orders = [
                d['count'] for d in self.historical_data
                if d['date'].weekday() < 5
            ]
            weekend_orders = [
                d['count'] for d in self.historical_data
                if d['date'].weekday() >= 5
            ]
            
            avg_weekday = np.mean(weekday_orders) if weekday_orders else 25
            avg_weekend = np.mean(weekend_orders) if weekend_orders else 15
        
        forecasts = []
        
        for i in range(days_ahead):
            date = target_date + timedelta(days=i)
            is_weekend = date.weekday() >= 5
            
            predicted_count = int(avg_weekend if is_weekend else avg_weekday)
            
            forecasts.append({
                'date': date.strftime('%Y-%m-%d'),
                'predicted_orders': predicted_count,
                'confidence': 0.6,
            })
        
        return forecasts
    
    def get_statistics(self) -> Dict:
        """
        Get demand statistics from historical data
        
        Returns:
            Dictionary with demand statistics
        """
        if not self.historical_data:
            return {}
        
        counts = [d['count'] for d in self.historical_data]
        
        return {
            'total_days': len(self.historical_data),
            'avg_daily_orders': round(np.mean(counts), 1),
            'max_daily_orders': max(counts),
            'min_daily_orders': min(counts),
            'std_dev': round(np.std(counts), 1),
        }


# Global demand forecaster instance
demand_forecaster = DemandForecaster()
