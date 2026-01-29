"""
Data collection pipeline for ML models.

Collects and preprocesses historical data for training.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd

from app.models.dispatch import Dispatch, DispatchStatus
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.order import Order


class DataCollector:
    """
    Collects historical data for ML training.
    """
    
    def __init__(self, db: Session):
        """
        Initialize data collector.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def collect_dispatch_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_days: int = 90
    ) -> pd.DataFrame:
        """
        Collect historical dispatch data.
        
        Args:
            start_date: Start date for collection
            end_date: End date for collection
            min_days: Minimum number of days required
            
        Returns:
            DataFrame with dispatch history
        """
        # Default to last 90 days if not specified
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(days=max(min_days, 90))
        
        # Query dispatches
        query = self.db.query(
            func.date(Dispatch.created_at).label('date'),
            func.count(Dispatch.id).label('dispatch_count'),
            func.count(func.distinct(Dispatch.vehicle_id)).label('unique_vehicles'),
            func.count(func.distinct(Dispatch.driver_id)).label('unique_drivers')
        ).filter(
            Dispatch.created_at >= start_date,
            Dispatch.created_at <= end_date
        ).group_by(
            func.date(Dispatch.created_at)
        ).order_by(
            func.date(Dispatch.created_at)
        )
        
        results = query.all()
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'date': r.date,
                'dispatch_count': r.dispatch_count or 0,
                'unique_vehicles': r.unique_vehicles or 0,
                'unique_drivers': r.unique_drivers or 0,
                'completed_count': r.completed_count or 0,
                'cancelled_count': r.cancelled_count or 0,
                'completion_rate': (
                    r.completed_count / r.dispatch_count
                    if r.dispatch_count > 0 else 0
                )
            }
            for r in results
        ])
        
        if len(df) == 0:
            raise ValueError(
                f"No dispatch data found between {start_date} and {end_date}"
            )
        
        # Fill missing dates
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        df = df.resample('D').sum().fillna(0)
        
        return df
    
    def collect_vehicle_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Collect vehicle usage and maintenance history.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with vehicle history
        """
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(days=90)
        
        # Query vehicle dispatches
        query = self.db.query(
            func.date(Dispatch.created_at).label('date'),
            Dispatch.vehicle_id,
            func.count(Dispatch.id).label('trip_count'),
            func.sum(Dispatch.distance).label('total_distance'),
            func.avg(Dispatch.fuel_consumption).label('avg_fuel_consumption')
        ).filter(
            Dispatch.created_at >= start_date,
            Dispatch.created_at <= end_date,
            Dispatch.vehicle_id.isnot(None)
        ).group_by(
            func.date(Dispatch.created_at),
            Dispatch.vehicle_id
        ).order_by(
            func.date(Dispatch.created_at)
        )
        
        results = query.all()
        
        df = pd.DataFrame([
            {
                'date': r.date,
                'vehicle_id': r.vehicle_id,
                'trip_count': r.trip_count or 0,
                'total_distance': float(r.total_distance or 0),
                'avg_fuel_consumption': float(r.avg_fuel_consumption or 0)
            }
            for r in results
        ])
        
        if len(df) > 0:
            df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def collect_cost_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Collect cost history for dispatches.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with cost history
        """
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(days=90)
        
        # Query dispatch costs
        query = self.db.query(
            func.date(Dispatch.created_at).label('date'),
            func.sum(Dispatch.fuel_cost).label('total_fuel_cost'),
            func.sum(Dispatch.toll_cost).label('total_toll_cost'),
            func.sum(Dispatch.driver_cost).label('total_driver_cost'),
            func.count(Dispatch.id).label('dispatch_count')
        ).filter(
            Dispatch.created_at >= start_date,
            Dispatch.created_at <= end_date
        ).group_by(
            func.date(Dispatch.created_at)
        ).order_by(
            func.date(Dispatch.created_at)
        )
        
        results = query.all()
        
        df = pd.DataFrame([
            {
                'date': r.date,
                'total_fuel_cost': float(r.total_fuel_cost or 0),
                'total_toll_cost': float(r.total_toll_cost or 0),
                'total_driver_cost': float(r.total_driver_cost or 0),
                'total_cost': (
                    float(r.total_fuel_cost or 0) +
                    float(r.total_toll_cost or 0) +
                    float(r.total_driver_cost or 0)
                ),
                'dispatch_count': r.dispatch_count or 0,
                'avg_cost_per_dispatch': (
                    (
                        float(r.total_fuel_cost or 0) +
                        float(r.total_toll_cost or 0) +
                        float(r.total_driver_cost or 0)
                    ) / r.dispatch_count
                    if r.dispatch_count > 0 else 0
                )
            }
            for r in results
        ])
        
        if len(df) > 0:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            df = df.resample('D').sum().fillna(0)
        
        return df
    
    def collect_order_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Collect order history.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with order history
        """
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(days=90)
        
        # Query orders
        query = self.db.query(
            func.date(Order.created_at).label('date'),
            func.count(Order.id).label('order_count'),
            func.sum(Order.quantity).label('total_quantity'),
            func.avg(Order.priority).label('avg_priority')
        ).filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date
        ).group_by(
            func.date(Order.created_at)
        ).order_by(
            func.date(Order.created_at)
        )
        
        results = query.all()
        
        df = pd.DataFrame([
            {
                'date': r.date,
                'order_count': r.order_count or 0,
                'total_quantity': float(r.total_quantity or 0),
                'avg_priority': float(r.avg_priority or 0)
            }
            for r in results
        ])
        
        if len(df) > 0:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            df = df.resample('D').sum().fillna(0)
        
        return df
    
    def generate_sample_data(
        self,
        days: int = 90,
        base_demand: int = 20
    ) -> pd.DataFrame:
        """
        Generate sample data for testing (when no real data exists).
        
        Args:
            days: Number of days to generate
            base_demand: Base daily demand
            
        Returns:
            DataFrame with synthetic data
        """
        import numpy as np
        
        # Create date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate synthetic data with trends and seasonality
        np.random.seed(42)
        
        # Weekly seasonality (weekdays vs weekends)
        weekly_pattern = np.array([1.2, 1.3, 1.1, 1.0, 1.2, 0.7, 0.6])
        
        # Monthly trend (slight growth)
        trend = np.linspace(1.0, 1.3, len(dates))
        
        # Generate dispatch counts
        dispatch_counts = []
        for i, date in enumerate(dates):
            day_of_week = date.dayofweek
            base = base_demand * weekly_pattern[day_of_week] * trend[i]
            noise = np.random.normal(0, base * 0.1)
            count = max(0, int(base + noise))
            dispatch_counts.append(count)
        
        df = pd.DataFrame({
            'date': dates,
            'dispatch_count': dispatch_counts,
            'unique_vehicles': [int(c * 0.6) for c in dispatch_counts],
            'unique_drivers': [int(c * 0.7) for c in dispatch_counts],
            'avg_duration': [120 + np.random.normal(0, 20) for _ in dates],
            'completed_count': [int(c * 0.95) for c in dispatch_counts],
            'cancelled_count': [int(c * 0.05) for c in dispatch_counts],
            'completion_rate': [0.95 for _ in dates]
        })
        
        df = df.set_index('date')
        
        return df
    
    def check_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Check quality of collected data.
        
        Args:
            df: DataFrame to check
            
        Returns:
            Dictionary with quality metrics
        """
        return {
            'total_records': len(df),
            'date_range': {
                'start': df.index.min().isoformat() if len(df) > 0 else None,
                'end': df.index.max().isoformat() if len(df) > 0 else None,
                'days': (df.index.max() - df.index.min()).days if len(df) > 0 else 0
            },
            'missing_values': df.isnull().sum().to_dict(),
            'zero_values': (df == 0).sum().to_dict(),
            'statistics': df.describe().to_dict(),
            'sufficient_for_training': len(df) >= 60  # At least 2 months
        }
