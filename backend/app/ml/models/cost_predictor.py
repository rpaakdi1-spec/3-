"""
Cost prediction model for fleet operations.

Predicts operational costs based on historical data and various factors.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import joblib
from pathlib import Path

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .base import BaseModel


class CostPredictor(BaseModel):
    """
    Cost prediction model using ensemble methods.
    
    Predicts:
    - Daily operational costs
    - Vehicle-specific costs
    - Route-based costs
    - Maintenance costs
    - Fuel costs
    """
    
    def __init__(self, model_type: str = "random_forest"):
        """
        Initialize cost predictor.
        
        Args:
            model_type: Type of model ('random_forest' or 'gradient_boosting')
        """
        super().__init__()
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.target_name = "total_cost"
        
        # Initialize model based on type
        if model_type == "random_forest":
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == "gradient_boosting":
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for cost prediction.
        
        Args:
            df: DataFrame with dispatch and cost data
            
        Returns:
            DataFrame with engineered features
        """
        features = df.copy()
        
        # Date features
        if 'date' in features.columns:
            features['date'] = pd.to_datetime(features['date'])
            features['day_of_week'] = features['date'].dt.dayofweek
            features['day_of_month'] = features['date'].dt.day
            features['month'] = features['date'].dt.month
            features['quarter'] = features['date'].dt.quarter
            features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
            features['is_month_start'] = (features['day_of_month'] <= 7).astype(int)
            features['is_month_end'] = (features['day_of_month'] >= 24).astype(int)
        
        # Lag features (previous costs)
        if 'total_cost' in features.columns:
            for lag in [1, 7, 14, 30]:
                features[f'cost_lag_{lag}'] = features['total_cost'].shift(lag)
        
        # Rolling statistics
        if 'total_cost' in features.columns:
            for window in [7, 14, 30]:
                features[f'cost_rolling_mean_{window}'] = (
                    features['total_cost'].rolling(window=window, min_periods=1).mean()
                )
                features[f'cost_rolling_std_{window}'] = (
                    features['total_cost'].rolling(window=window, min_periods=1).std()
                )
        
        # Operational features
        if 'distance_km' in features.columns:
            features['distance_per_dispatch'] = (
                features['distance_km'] / features.get('dispatch_count', 1)
            )
        
        if 'fuel_liters' in features.columns and 'distance_km' in features.columns:
            features['fuel_efficiency'] = (
                features['distance_km'] / (features['fuel_liters'] + 1)  # +1 to avoid division by zero
            )
        
        # Vehicle utilization
        if 'active_vehicles' in features.columns and 'total_vehicles' in features.columns:
            features['vehicle_utilization'] = (
                features['active_vehicles'] / features['total_vehicles']
            )
        
        # Cost per unit metrics
        if 'total_cost' in features.columns:
            if 'distance_km' in features.columns:
                features['cost_per_km'] = (
                    features['total_cost'] / (features['distance_km'] + 1)
                )
            if 'dispatch_count' in features.columns:
                features['cost_per_dispatch'] = (
                    features['total_cost'] / (features['dispatch_count'] + 1)
                )
        
        # Fill NaN values
        features = features.fillna(method='ffill').fillna(method='bfill').fillna(0)
        
        return features
    
    def train(
        self,
        df: pd.DataFrame,
        target_column: str = "total_cost",
        test_size: float = 0.2
    ) -> Dict:
        """
        Train cost prediction model.
        
        Args:
            df: Training data with features and target
            target_column: Name of target column
            test_size: Proportion of data for testing
            
        Returns:
            Dictionary with training metrics
        """
        # Prepare features
        df_prepared = self.prepare_features(df)
        
        # Select features (exclude date and target columns)
        exclude_cols = ['date', target_column, 'timestamp']
        feature_cols = [
            col for col in df_prepared.columns 
            if col not in exclude_cols and not col.startswith('Unnamed')
        ]
        
        X = df_prepared[feature_cols]
        y = df_prepared[target_column]
        
        # Store feature names
        self.feature_names = feature_cols
        self.target_name = target_column
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, shuffle=False
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_train_pred = self.model.predict(X_train_scaled)
        y_test_pred = self.model.predict(X_test_scaled)
        
        # Calculate metrics
        metrics = {
            'train_mae': mean_absolute_error(y_train, y_train_pred),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
            'train_r2': r2_score(y_train, y_train_pred),
            'test_mae': mean_absolute_error(y_test, y_test_pred),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
            'test_r2': r2_score(y_test, y_test_pred),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'feature_count': len(self.feature_names),
            'model_type': self.model_type
        }
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            metrics['feature_importance'] = feature_importance.to_dict('records')
        
        # Store metadata
        self.metadata = {
            'trained_at': datetime.now().isoformat(),
            'model_type': self.model_type,
            'metrics': metrics,
            'feature_names': self.feature_names,
            'target_name': self.target_name
        }
        
        self.is_trained = True
        
        return metrics
    
    def predict(
        self,
        df: pd.DataFrame,
        return_confidence: bool = False
    ) -> pd.DataFrame:
        """
        Predict costs for given data.
        
        Args:
            df: DataFrame with features
            return_confidence: Whether to return prediction intervals
            
        Returns:
            DataFrame with predictions
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        # Prepare features
        df_prepared = self.prepare_features(df)
        
        # Select features
        X = df_prepared[self.feature_names]
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make predictions
        predictions = self.model.predict(X_scaled)
        
        # Create result DataFrame
        result = pd.DataFrame({
            'predicted_cost': predictions
        }, index=df.index)
        
        # Add confidence intervals if requested
        if return_confidence and hasattr(self.model, 'estimators_'):
            # For ensemble models, use prediction variance
            predictions_all = np.array([
                estimator.predict(X_scaled)
                for estimator in self.model.estimators_
            ])
            
            std = predictions_all.std(axis=0)
            result['prediction_lower'] = predictions - 1.96 * std
            result['prediction_upper'] = predictions + 1.96 * std
            result['prediction_std'] = std
        
        return result
    
    def predict_cost_breakdown(
        self,
        operational_data: Dict
    ) -> Dict:
        """
        Predict cost breakdown by category.
        
        Args:
            operational_data: Dictionary with operational metrics
            
        Returns:
            Dictionary with cost breakdown
        """
        # This is a simplified version
        # In production, you'd have separate models for each cost category
        
        total_cost = self.predict(
            pd.DataFrame([operational_data])
        )['predicted_cost'].iloc[0]
        
        # Estimated breakdown (simplified)
        # In production, use historical proportions or separate models
        breakdown = {
            'fuel_cost': total_cost * 0.45,
            'maintenance_cost': total_cost * 0.20,
            'labor_cost': total_cost * 0.25,
            'insurance_cost': total_cost * 0.05,
            'other_cost': total_cost * 0.05,
            'total_cost': total_cost
        }
        
        return breakdown
    
    def save(self, path: Optional[str] = None):
        """Save model to disk."""
        if path is None:
            path = f"ml_models/cost_predictor_{self.model_type}.joblib"
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'target_name': self.target_name,
            'metadata': self.metadata,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, path)
        
        # Save metadata separately
        self.save_metadata(path.replace('.joblib', '_metadata.json'))
    
    def load(self, path: str):
        """Load model from disk."""
        model_data = joblib.load(path)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.target_name = model_data['target_name']
        self.metadata = model_data['metadata']
        self.is_trained = model_data['is_trained']
