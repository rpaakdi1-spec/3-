"""
Automatic Model Retraining Pipeline.

Monitors model performance and triggers retraining when needed.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging
from sqlalchemy.orm import Session

from app.ml.services.ml_service import MLService
from app.ml.models.base import ModelMetrics
from app.ml.pipelines.data_collector import DataCollector

logger = logging.getLogger(__name__)


class RetrainingTrigger:
    """
    Determines when a model should be retrained.
    """
    
    def __init__(
        self,
        min_accuracy_drop: float = 0.10,  # 10% accuracy drop
        min_data_points: int = 100,  # Minimum new data points
        max_days_since_training: int = 30,  # Maximum 30 days
        min_rmse_increase: float = 0.15  # 15% RMSE increase
    ):
        """
        Initialize retraining trigger.
        
        Args:
            min_accuracy_drop: Minimum accuracy drop to trigger
            min_data_points: Minimum new data points needed
            max_days_since_training: Maximum days before forced retrain
            min_rmse_increase: Minimum RMSE increase to trigger
        """
        self.min_accuracy_drop = min_accuracy_drop
        self.min_data_points = min_data_points
        self.max_days_since_training = max_days_since_training
        self.min_rmse_increase = min_rmse_increase
    
    def should_retrain(
        self,
        current_metrics: Optional[ModelMetrics],
        model_metadata: Optional[Dict[str, Any]],
        new_data_count: int
    ) -> tuple[bool, str]:
        """
        Determine if model should be retrained.
        
        Args:
            current_metrics: Current model performance metrics
            model_metadata: Model training metadata
            new_data_count: Number of new data points available
            
        Returns:
            Tuple of (should_retrain: bool, reason: str)
        """
        if model_metadata is None:
            return True, "No existing model found - initial training required"
        
        # Check if model is too old
        trained_at = datetime.fromisoformat(model_metadata['trained_at'])
        days_since_training = (datetime.utcnow() - trained_at).days
        
        if days_since_training >= self.max_days_since_training:
            return True, f"Model is {days_since_training} days old (max: {self.max_days_since_training})"
        
        # Check if enough new data is available
        if new_data_count >= self.min_data_points:
            return True, f"Sufficient new data available: {new_data_count} points"
        
        # Check performance degradation
        if current_metrics is not None and 'metrics' in model_metadata:
            old_metrics = model_metadata['metrics']
            
            # Check RMSE increase
            if 'rmse' in old_metrics and current_metrics.rmse:
                rmse_increase = (
                    (current_metrics.rmse - old_metrics['rmse']) / old_metrics['rmse']
                )
                if rmse_increase >= self.min_rmse_increase:
                    return True, f"RMSE increased by {rmse_increase:.1%}"
            
            # Check R² decrease
            if 'r2_score' in old_metrics and current_metrics.r2_score:
                r2_decrease = old_metrics['r2_score'] - current_metrics.r2_score
                if r2_decrease >= self.min_accuracy_drop:
                    return True, f"R² score decreased by {r2_decrease:.1%}"
        
        return False, "Model performance is acceptable"


class RetrainingPipeline:
    """
    Automatic retraining pipeline for ML models.
    """
    
    def __init__(
        self,
        db: Session,
        model_dir: str = "ml_models",
        log_dir: str = "ml_logs"
    ):
        """
        Initialize retraining pipeline.
        
        Args:
            db: Database session
            model_dir: Directory for model storage
            log_dir: Directory for training logs
        """
        self.db = db
        self.ml_service = MLService(db, model_dir=model_dir)
        self.data_collector = DataCollector(db)
        self.trigger = RetrainingTrigger()
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.retraining_log_path = self.log_dir / "retraining_history.json"
        self._init_log_file()
    
    def _init_log_file(self):
        """Initialize retraining log file."""
        if not self.retraining_log_path.exists():
            with open(self.retraining_log_path, 'w') as f:
                json.dump([], f)
    
    def _log_retraining_event(
        self,
        event_type: str,
        model_type: str,
        metrics: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None
    ):
        """
        Log a retraining event.
        
        Args:
            event_type: 'check', 'retrain', 'deploy', 'error'
            model_type: Type of model
            metrics: Training metrics
            reason: Reason for retraining
            success: Whether operation succeeded
            error: Error message if failed
        """
        # Read existing log
        with open(self.retraining_log_path, 'r') as f:
            log = json.load(f)
        
        # Add new event
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'model_type': model_type,
            'reason': reason,
            'success': success,
            'error': error,
            'metrics': metrics
        }
        
        log.append(event)
        
        # Keep only last 1000 events
        if len(log) > 1000:
            log = log[-1000:]
        
        # Write back
        with open(self.retraining_log_path, 'w') as f:
            json.dump(log, f, indent=2, default=str)
        
        logger.info(f"Retraining event logged: {event_type} for {model_type}")
    
    def check_and_retrain(
        self,
        model_type: str = 'prophet',
        force: bool = False,
        use_sample_data: bool = False
    ) -> Dict[str, Any]:
        """
        Check if retraining is needed and retrain if necessary.
        
        Args:
            model_type: 'prophet' or 'lstm'
            force: Force retraining regardless of conditions
            use_sample_data: Use synthetic data for testing
            
        Returns:
            Result dictionary with status and metrics
        """
        logger.info(f"Checking retraining status for {model_type} model...")
        
        try:
            # Get current model metadata
            model_metadata = self.ml_service.get_model_info(model_type)
            
            # Check if we have enough new data
            try:
                df = self.data_collector.collect_dispatch_history(min_days=90)
                new_data_count = len(df)
                data_available = True
            except ValueError:
                logger.warning("No real data available, will use sample data")
                new_data_count = 0
                data_available = False
                use_sample_data = True
            
            # Check if retraining is needed
            if not force:
                should_retrain, reason = self.trigger.should_retrain(
                    current_metrics=None,  # Would need to evaluate on recent data
                    model_metadata=model_metadata,
                    new_data_count=new_data_count
                )
            else:
                should_retrain = True
                reason = "Forced retraining requested"
            
            # Log check event
            self._log_retraining_event(
                event_type='check',
                model_type=model_type,
                reason=reason,
                metrics={'new_data_count': new_data_count}
            )
            
            if not should_retrain:
                logger.info(f"Retraining not needed: {reason}")
                return {
                    'status': 'skipped',
                    'reason': reason,
                    'model_type': model_type,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Retrain model
            logger.info(f"Starting retraining: {reason}")
            result = self.retrain_model(
                model_type=model_type,
                reason=reason,
                use_sample_data=use_sample_data
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in check_and_retrain: {e}", exc_info=True)
            self._log_retraining_event(
                event_type='error',
                model_type=model_type,
                success=False,
                error=str(e)
            )
            
            return {
                'status': 'error',
                'error': str(e),
                'model_type': model_type,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def retrain_model(
        self,
        model_type: str = 'prophet',
        reason: str = 'Manual retraining',
        use_sample_data: bool = False,
        **training_kwargs
    ) -> Dict[str, Any]:
        """
        Retrain a model.
        
        Args:
            model_type: 'prophet' or 'lstm'
            reason: Reason for retraining
            use_sample_data: Use synthetic data
            **training_kwargs: Additional training parameters
            
        Returns:
            Training result with metrics
        """
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Retraining {model_type} model: {reason}")
            
            # Train model
            metrics = self.ml_service.train_demand_model(
                model_type=model_type,
                use_sample_data=use_sample_data,
                **training_kwargs
            )
            
            end_time = datetime.utcnow()
            training_duration = (end_time - start_time).total_seconds()
            
            # Log success
            self._log_retraining_event(
                event_type='retrain',
                model_type=model_type,
                reason=reason,
                metrics={
                    'mae': metrics.mae,
                    'rmse': metrics.rmse,
                    'r2_score': metrics.r2_score,
                    'training_duration_seconds': training_duration
                },
                success=True
            )
            
            logger.info(
                f"Retraining completed successfully in {training_duration:.1f}s. "
                f"RMSE: {metrics.rmse:.2f}, R²: {metrics.r2_score:.3f}"
            )
            
            return {
                'status': 'success',
                'model_type': model_type,
                'reason': reason,
                'metrics': {
                    'mae': metrics.mae,
                    'rmse': metrics.rmse,
                    'mape': metrics.mape,
                    'r2_score': metrics.r2_score
                },
                'training_duration_seconds': training_duration,
                'trained_at': end_time.isoformat(),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error retraining model: {e}", exc_info=True)
            
            self._log_retraining_event(
                event_type='retrain',
                model_type=model_type,
                reason=reason,
                success=False,
                error=str(e)
            )
            
            return {
                'status': 'error',
                'model_type': model_type,
                'reason': reason,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_retraining_history(
        self,
        limit: int = 50,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get retraining history.
        
        Args:
            limit: Maximum number of events to return
            event_type: Filter by event type
            
        Returns:
            List of retraining events
        """
        try:
            with open(self.retraining_log_path, 'r') as f:
                log = json.load(f)
            
            # Filter by event type if specified
            if event_type:
                log = [e for e in log if e.get('event_type') == event_type]
            
            # Return most recent events
            return log[-limit:]
            
        except Exception as e:
            logger.error(f"Error reading retraining history: {e}")
            return []
    
    def get_retraining_stats(self) -> Dict[str, Any]:
        """
        Get statistics about retraining history.
        
        Returns:
            Statistics dictionary
        """
        try:
            history = self.get_retraining_history(limit=1000)
            
            if not history:
                return {'total_events': 0}
            
            # Calculate stats
            total_events = len(history)
            retrainings = [e for e in history if e.get('event_type') == 'retrain']
            successful_retrainings = [e for e in retrainings if e.get('success')]
            failed_retrainings = [e for e in retrainings if not e.get('success')]
            
            # Get last retraining
            last_retraining = retrainings[-1] if retrainings else None
            
            # Calculate success rate
            success_rate = (
                len(successful_retrainings) / len(retrainings)
                if retrainings else 0
            )
            
            # Average training duration
            durations = [
                e.get('metrics', {}).get('training_duration_seconds', 0)
                for e in successful_retrainings
                if e.get('metrics')
            ]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            return {
                'total_events': total_events,
                'total_retrainings': len(retrainings),
                'successful_retrainings': len(successful_retrainings),
                'failed_retrainings': len(failed_retrainings),
                'success_rate': success_rate,
                'average_training_duration_seconds': avg_duration,
                'last_retraining': last_retraining,
                'last_retraining_timestamp': (
                    last_retraining.get('timestamp')
                    if last_retraining else None
                )
            }
            
        except Exception as e:
            logger.error(f"Error calculating retraining stats: {e}")
            return {'error': str(e)}
    
    def schedule_retraining(
        self,
        interval_days: int = 7,
        model_types: List[str] = ['prophet']
    ) -> Dict[str, Any]:
        """
        Schedule automatic retraining.
        
        This would be called by a cron job or scheduler.
        
        Args:
            interval_days: Days between retraining checks
            model_types: List of model types to check
            
        Returns:
            Schedule results
        """
        results = {}
        
        for model_type in model_types:
            result = self.check_and_retrain(
                model_type=model_type,
                force=False
            )
            results[model_type] = result
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'interval_days': interval_days,
            'results': results
        }


class ModelMonitor:
    """
    Monitors model performance in production.
    """
    
    def __init__(self, ml_service: MLService):
        """
        Initialize model monitor.
        
        Args:
            ml_service: ML service instance
        """
        self.ml_service = ml_service
    
    def evaluate_recent_predictions(
        self,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """
        Evaluate model predictions against actual values.
        
        Args:
            days_back: Number of days to evaluate
            
        Returns:
            Evaluation metrics
        """
        # This would compare predictions made N days ago
        # with actual values observed
        
        # Placeholder implementation
        return {
            'days_evaluated': days_back,
            'mae': 2.5,
            'rmse': 3.2,
            'mape': 12.5,
            'note': 'Placeholder - implement actual prediction comparison'
        }
    
    def detect_model_drift(self) -> Dict[str, Any]:
        """
        Detect if model has drifted from expected performance.
        
        Returns:
            Drift detection results
        """
        # Placeholder for drift detection logic
        return {
            'drift_detected': False,
            'confidence': 0.95,
            'note': 'Placeholder - implement drift detection'
        }
