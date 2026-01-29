"""
ETA Prediction ML Model - Phase 8.2
AI-powered delivery time estimation using historical data
"""
from typing import Dict, List, Optional
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import logging

logger = logging.getLogger(__name__)


class ETAPredictor:
    """
    Machine Learning model for predicting Estimated Time of Arrival (ETA)
    Uses Random Forest Regressor with historical delivery data
    """
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            'distance_km',
            'traffic_score',
            'weather_score',
            'time_of_day',
            'day_of_week',
            'temperature_zone',
            'pallet_count',
            'weight_kg',
            'stop_count',
            'vehicle_speed_avg',
        ]
    
    def prepare_features(self, delivery_data: Dict) -> np.ndarray:
        """
        Prepare features for prediction from delivery data
        
        Args:
            delivery_data: Dictionary containing delivery information
            
        Returns:
            Feature array for model input
        """
        features = []
        
        # Extract and normalize features
        features.append(delivery_data.get('distance_km', 0))
        features.append(delivery_data.get('traffic_score', 0.5))  # 0-1 scale
        features.append(delivery_data.get('weather_score', 0.8))  # 0-1 scale
        
        # Time features
        now = datetime.now()
        features.append(now.hour + now.minute / 60)  # Time of day as decimal
        features.append(now.weekday())  # Day of week (0-6)
        
        # Order features
        temp_zone_map = {'냉장': 0, '냉동': 1, '상온': 2}
        features.append(temp_zone_map.get(delivery_data.get('temperature_zone'), 0))
        features.append(delivery_data.get('pallet_count', 1))
        features.append(delivery_data.get('weight_kg', 0))
        features.append(delivery_data.get('stop_count', 1))
        
        # Vehicle features
        features.append(delivery_data.get('vehicle_speed_avg', 40))  # km/h
        
        return np.array(features).reshape(1, -1)
    
    def train(self, training_data: List[Dict], targets: List[float]):
        """
        Train the ETA prediction model
        
        Args:
            training_data: List of historical delivery data
            targets: Actual delivery times in minutes
        """
        if len(training_data) < 10:
            logger.warning("Insufficient training data (minimum 10 samples required)")
            return False
        
        # Prepare feature matrix
        X = np.array([
            self.prepare_features(data).flatten()
            for data in training_data
        ])
        y = np.array(targets)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Calculate training score
        score = self.model.score(X_scaled, y)
        logger.info(f"ETA model trained with R² score: {score:.4f}")
        
        return True
    
    def predict(self, delivery_data: Dict) -> Dict:
        """
        Predict ETA for a delivery
        
        Args:
            delivery_data: Delivery information
            
        Returns:
            Dictionary with ETA prediction and confidence
        """
        if not self.is_trained:
            logger.warning("Model not trained, using fallback estimation")
            return self._fallback_estimation(delivery_data)
        
        try:
            # Prepare features
            X = self.prepare_features(delivery_data)
            X_scaled = self.scaler.transform(X)
            
            # Predict
            eta_minutes = self.model.predict(X_scaled)[0]
            
            # Calculate confidence based on feature importances
            confidence = self._calculate_confidence(X)
            
            # Calculate arrival time
            now = datetime.now()
            eta_datetime = now + timedelta(minutes=eta_minutes)
            
            return {
                'eta_minutes': round(eta_minutes, 1),
                'eta_datetime': eta_datetime.isoformat(),
                'confidence': confidence,
                'algorithm': 'RandomForest',
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._fallback_estimation(delivery_data)
    
    def _calculate_confidence(self, features: np.ndarray) -> float:
        """
        Calculate prediction confidence based on feature values
        
        Args:
            features: Input features
            
        Returns:
            Confidence score (0-1)
        """
        # Use tree predictions variance as confidence indicator
        predictions = np.array([
            tree.predict(features)[0]
            for tree in self.model.estimators_
        ])
        
        variance = np.var(predictions)
        max_variance = 100  # Minutes squared
        
        # Convert variance to confidence (inverse relationship)
        confidence = max(0.5, 1.0 - (variance / max_variance))
        
        return round(confidence, 2)
    
    def _fallback_estimation(self, delivery_data: Dict) -> Dict:
        """
        Fallback ETA estimation when ML model is unavailable
        Uses simple distance-based calculation
        
        Args:
            delivery_data: Delivery information
            
        Returns:
            Dictionary with estimated ETA
        """
        distance_km = delivery_data.get('distance_km', 10)
        avg_speed = delivery_data.get('vehicle_speed_avg', 40)
        traffic_factor = delivery_data.get('traffic_score', 0.5)
        
        # Adjust speed based on traffic
        effective_speed = avg_speed * (1 - traffic_factor * 0.3)
        
        # Calculate time
        eta_minutes = (distance_km / effective_speed) * 60
        
        # Add buffer for stops
        stop_count = delivery_data.get('stop_count', 1)
        eta_minutes += stop_count * 5  # 5 minutes per stop
        
        now = datetime.now()
        eta_datetime = now + timedelta(minutes=eta_minutes)
        
        return {
            'eta_minutes': round(eta_minutes, 1),
            'eta_datetime': eta_datetime.isoformat(),
            'confidence': 0.6,
            'algorithm': 'Fallback',
        }
    
    def save_model(self, filepath: str):
        """Save trained model to disk"""
        if self.is_trained:
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
            }, filepath)
            logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load trained model from disk"""
        try:
            data = joblib.load(filepath)
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_names = data['feature_names']
            self.is_trained = True
            logger.info(f"Model loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


# Global ETA predictor instance
eta_predictor = ETAPredictor()
