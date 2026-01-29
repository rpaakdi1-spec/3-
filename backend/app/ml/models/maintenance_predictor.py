"""
Maintenance prediction model for vehicle fleet.

Predicts maintenance needs and schedules preventive maintenance.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import joblib
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report
)

from .base import BaseModel


class MaintenancePredictor(BaseModel):
    """
    Maintenance prediction model using Random Forest.
    
    Predicts:
    - Maintenance requirements (binary: needed/not needed)
    - Maintenance urgency (low/medium/high)
    - Failure probability
    - Recommended maintenance date
    """
    
    def __init__(self):
        """Initialize maintenance predictor."""
        super().__init__()
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )
        self.scaler = StandardScaler()
        self.feature_names = []
        
        # Maintenance thresholds
        self.thresholds = {
            'high_urgency': 0.75,  # >75% probability
            'medium_urgency': 0.50,  # 50-75% probability
            'low_urgency': 0.25  # 25-50% probability
        }
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for maintenance prediction.
        
        Args:
            df: DataFrame with vehicle operational data
            
        Returns:
            DataFrame with engineered features
        """
        features = df.copy()
        
        # Age features
        if 'vehicle_age_days' in features.columns:
            features['vehicle_age_years'] = features['vehicle_age_days'] / 365.25
            features['vehicle_age_months'] = features['vehicle_age_days'] / 30.44
        
        # Mileage features
        if 'total_mileage_km' in features.columns:
            features['mileage_per_day'] = (
                features['total_mileage_km'] / features.get('vehicle_age_days', 1)
            )
            features['mileage_category'] = pd.cut(
                features['total_mileage_km'],
                bins=[0, 50000, 100000, 200000, float('inf')],
                labels=[0, 1, 2, 3]
            ).astype(int)
        
        # Usage intensity
        if 'days_since_last_maintenance' in features.columns:
            features['maintenance_overdue'] = (
                features['days_since_last_maintenance'] > 180
            ).astype(int)
            features['maintenance_due_soon'] = (
                features['days_since_last_maintenance'] > 150
            ).astype(int)
        
        # Average features
        if 'total_trips' in features.columns and 'vehicle_age_days' in features.columns:
            features['trips_per_day'] = (
                features['total_trips'] / features['vehicle_age_days']
            )
        
        if 'total_distance_km' in features.columns and 'total_trips' in features.columns:
            features['avg_trip_distance'] = (
                features['total_distance_km'] / (features['total_trips'] + 1)
            )
        
        # Temperature zone stress (냉동/냉장 차량의 경우)
        if 'temperature_zone' in features.columns:
            # Convert temperature zone to numeric stress factor
            zone_stress = {
                'FROZEN': 3,  # 냉동 차량 (highest stress)
                'CHILLED': 2,  # 냉장 차량 (medium stress)
                'AMBIENT': 1  # 상온 차량 (lowest stress)
            }
            features['temp_zone_stress'] = features['temperature_zone'].map(
                zone_stress
            ).fillna(1)
        
        # Maintenance history features
        if 'maintenance_count' in features.columns:
            features['maintenance_frequency'] = (
                features['maintenance_count'] / features.get('vehicle_age_months', 1)
            )
        
        # Cost-based features
        if 'total_maintenance_cost' in features.columns:
            features['avg_maintenance_cost'] = (
                features['total_maintenance_cost'] / (features.get('maintenance_count', 1) + 1)
            )
            features['cost_trend'] = features.groupby('vehicle_id')['total_maintenance_cost'].diff()
        
        # Failure history
        if 'failure_count' in features.columns:
            features['failure_rate'] = (
                features['failure_count'] / features.get('vehicle_age_months', 1)
            )
            features['has_failure_history'] = (features['failure_count'] > 0).astype(int)
        
        # Fill NaN values
        features = features.fillna(method='ffill').fillna(method='bfill').fillna(0)
        
        return features
    
    def train(
        self,
        df: pd.DataFrame,
        target_column: str = "needs_maintenance",
        test_size: float = 0.2
    ) -> Dict:
        """
        Train maintenance prediction model.
        
        Args:
            df: Training data with features and target
            target_column: Name of target column (binary: 0/1)
            test_size: Proportion of data for testing
            
        Returns:
            Dictionary with training metrics
        """
        # Prepare features
        df_prepared = self.prepare_features(df)
        
        # Select features
        exclude_cols = ['date', 'timestamp', target_column, 'vehicle_id', 'vehicle_number']
        feature_cols = [
            col for col in df_prepared.columns 
            if col not in exclude_cols and not col.startswith('Unnamed')
        ]
        
        X = df_prepared[feature_cols]
        y = df_prepared[target_column]
        
        # Store feature names
        self.feature_names = feature_cols
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_train_pred = self.model.predict(X_train_scaled)
        y_test_pred = self.model.predict(X_test_scaled)
        y_test_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate metrics
        metrics = {
            'train_accuracy': accuracy_score(y_train, y_train_pred),
            'test_accuracy': accuracy_score(y_test, y_test_pred),
            'test_precision': precision_score(y_test, y_test_pred, zero_division=0),
            'test_recall': recall_score(y_test, y_test_pred, zero_division=0),
            'test_f1': f1_score(y_test, y_test_pred, zero_division=0),
            'test_roc_auc': roc_auc_score(y_test, y_test_proba),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'positive_samples': int(y.sum()),
            'negative_samples': int(len(y) - y.sum()),
            'feature_count': len(self.feature_names)
        }
        
        # Classification report
        report = classification_report(
            y_test, y_test_pred, output_dict=True, zero_division=0
        )
        metrics['classification_report'] = report
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            metrics['feature_importance'] = feature_importance.head(10).to_dict('records')
        
        # Store metadata
        self.metadata = {
            'trained_at': datetime.now().isoformat(),
            'model_type': 'random_forest_classifier',
            'metrics': metrics,
            'feature_names': self.feature_names,
            'thresholds': self.thresholds
        }
        
        self.is_trained = True
        
        return metrics
    
    def predict(
        self,
        df: pd.DataFrame,
        return_urgency: bool = True
    ) -> pd.DataFrame:
        """
        Predict maintenance needs for vehicles.
        
        Args:
            df: DataFrame with vehicle features
            return_urgency: Whether to return urgency levels
            
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
        probabilities = self.model.predict_proba(X_scaled)[:, 1]
        
        # Create result DataFrame
        result = pd.DataFrame({
            'needs_maintenance': predictions,
            'maintenance_probability': probabilities
        }, index=df.index)
        
        # Add urgency levels
        if return_urgency:
            result['urgency'] = 'none'
            result.loc[
                probabilities >= self.thresholds['low_urgency'], 'urgency'
            ] = 'low'
            result.loc[
                probabilities >= self.thresholds['medium_urgency'], 'urgency'
            ] = 'medium'
            result.loc[
                probabilities >= self.thresholds['high_urgency'], 'urgency'
            ] = 'high'
            
            # Recommended action within days
            result['recommended_action_days'] = 0
            result.loc[result['urgency'] == 'low', 'recommended_action_days'] = 30
            result.loc[result['urgency'] == 'medium', 'recommended_action_days'] = 14
            result.loc[result['urgency'] == 'high', 'recommended_action_days'] = 7
        
        return result
    
    def predict_maintenance_schedule(
        self,
        df: pd.DataFrame,
        forecast_days: int = 90
    ) -> pd.DataFrame:
        """
        Predict maintenance schedule for next N days.
        
        Args:
            df: DataFrame with current vehicle data
            forecast_days: Number of days to forecast
            
        Returns:
            DataFrame with maintenance schedule
        """
        # Get predictions
        predictions = self.predict(df, return_urgency=True)
        
        # Create schedule
        schedule = []
        current_date = datetime.now()
        
        for idx, row in predictions.iterrows():
            if row['needs_maintenance'] == 1:
                recommended_date = current_date + timedelta(
                    days=row['recommended_action_days']
                )
                
                if (recommended_date - current_date).days <= forecast_days:
                    schedule.append({
                        'vehicle_id': df.loc[idx, 'vehicle_id'],
                        'vehicle_number': df.loc[idx, 'vehicle_number'] if 'vehicle_number' in df.columns else 'N/A',
                        'recommended_date': recommended_date.strftime('%Y-%m-%d'),
                        'urgency': row['urgency'],
                        'probability': row['maintenance_probability'],
                        'days_until': row['recommended_action_days']
                    })
        
        schedule_df = pd.DataFrame(schedule)
        schedule_df = schedule_df.sort_values('days_until')
        
        return schedule_df
    
    def get_maintenance_insights(
        self,
        predictions: pd.DataFrame,
        vehicle_data: pd.DataFrame
    ) -> Dict:
        """
        Get maintenance insights and recommendations.
        
        Args:
            predictions: Prediction results
            vehicle_data: Vehicle operational data
            
        Returns:
            Dictionary with insights
        """
        insights = {
            'total_vehicles': len(predictions),
            'needs_maintenance': int(predictions['needs_maintenance'].sum()),
            'high_urgency': int((predictions['urgency'] == 'high').sum()),
            'medium_urgency': int((predictions['urgency'] == 'medium').sum()),
            'low_urgency': int((predictions['urgency'] == 'low').sum()),
            'avg_probability': float(predictions['maintenance_probability'].mean()),
            'max_probability': float(predictions['maintenance_probability'].max())
        }
        
        # Top vehicles needing attention
        top_vehicles = predictions[predictions['needs_maintenance'] == 1].sort_values(
            'maintenance_probability', ascending=False
        ).head(5)
        
        insights['top_priority_vehicles'] = []
        for idx, row in top_vehicles.iterrows():
            insights['top_priority_vehicles'].append({
                'vehicle_id': vehicle_data.loc[idx, 'vehicle_id'],
                'vehicle_number': vehicle_data.loc[idx, 'vehicle_number'] if 'vehicle_number' in vehicle_data.columns else 'N/A',
                'probability': float(row['maintenance_probability']),
                'urgency': row['urgency']
            })
        
        return insights
    
    def save(self, path: Optional[str] = None):
        """Save model to disk."""
        if path is None:
            path = "ml_models/maintenance_predictor.joblib"
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'thresholds': self.thresholds,
            'metadata': self.metadata,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, path)
        self.save_metadata(path.replace('.joblib', '_metadata.json'))
    
    def load(self, path: str):
        """Load model from disk."""
        model_data = joblib.load(path)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.thresholds = model_data['thresholds']
        self.metadata = model_data['metadata']
        self.is_trained = model_data['is_trained']
