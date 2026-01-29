"""
수요 예측 ML 모델
- 과거 주문 데이터 기반 수요 예측
- 시계열 분석 및 패턴 인식
- 요일/월/계절별 트렌드 분석
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path
from loguru import logger

from app.models.order import Order
from app.models.client import Client


class DemandForecastingService:
    """수요 예측 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        import os
        model_base = os.getenv("ML_MODELS_DIR", "./ml_models")
        self.model_path = Path(model_base)
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        self.model_file = self.model_path / "demand_forecast_model.pkl"
        self.scaler_file = self.model_path / "demand_scaler.pkl"
        
        self.model = None
        self.scaler = None
        
        self.feature_columns = [
            'day_of_week',
            'day_of_month',
            'month',
            'week_of_year',
            'is_weekend',
            'is_holiday',
            'is_month_end',
            'is_month_start',
            'temperature_zone_frozen_ratio',  # 냉동 비율
            'temperature_zone_chilled_ratio',  # 냉장 비율
            'avg_order_size_pallets',
            'unique_clients_count',
            'prev_week_orders',  # 지난주 주문 수
            'prev_month_orders'  # 지난달 주문 수
        ]
        
        # 모델 로드 시도
        self._load_model()
    
    def _load_model(self):
        """저장된 모델 로드"""
        try:
            if self.model_file.exists() and self.scaler_file.exists():
                self.model = joblib.load(self.model_file)
                self.scaler = joblib.load(self.scaler_file)
                logger.info(f"Loaded demand forecasting model from {self.model_file}")
            else:
                logger.info("No existing model found. Will train on first forecast.")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
            self.scaler = None
    
    def _save_model(self):
        """모델 저장"""
        try:
            joblib.dump(self.model, self.model_file)
            joblib.dump(self.scaler, self.scaler_file)
            logger.info(f"Saved demand forecasting model to {self.model_file}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def prepare_training_data(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_days: int = 90
    ) -> Optional[pd.DataFrame]:
        """
        훈련 데이터 준비 (일별 집계)
        
        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜
            min_days: 최소 일 수
            
        Returns:
            훈련 데이터 DataFrame 또는 None
        """
        try:
            # 기간 설정
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(days=365)  # 1년
            
            # 모든 주문 조회
            orders = self.db.query(Order).filter(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            ).all()
            
            if len(orders) < min_days:
                logger.warning(f"Insufficient data: {len(orders)} orders < {min_days} days")
                return None
            
            # 일별 데이터로 변환
            daily_data = {}
            
            for order in orders:
                order_date = order.created_at.date()
                
                if order_date not in daily_data:
                    daily_data[order_date] = {
                        'date': order_date,
                        'order_count': 0,
                        'total_pallets': 0,
                        'frozen_orders': 0,
                        'chilled_orders': 0,
                        'ambient_orders': 0,
                        'unique_clients': set()
                    }
                
                daily_data[order_date]['order_count'] += 1
                daily_data[order_date]['total_pallets'] += order.quantity_pallets
                daily_data[order_date]['unique_clients'].add(order.client_id)
                
                # 온도대별 분류
                if order.temperature_zone == '냉동':
                    daily_data[order_date]['frozen_orders'] += 1
                elif order.temperature_zone == '냉장':
                    daily_data[order_date]['chilled_orders'] += 1
                else:
                    daily_data[order_date]['ambient_orders'] += 1
            
            # DataFrame 생성
            rows = []
            for date_key in sorted(daily_data.keys()):
                data = daily_data[date_key]
                date = data['date']
                
                # 날짜 특징
                day_of_week = date.weekday()
                day_of_month = date.day
                month = date.month
                week_of_year = date.isocalendar()[1]
                is_weekend = 1 if day_of_week >= 5 else 0
                is_month_end = 1 if day_of_month >= 28 else 0
                is_month_start = 1 if day_of_month <= 3 else 0
                
                # 공휴일 (간단 버전: 일요일)
                is_holiday = 1 if day_of_week == 6 else 0
                
                # 온도대별 비율
                order_count = data['order_count']
                frozen_ratio = data['frozen_orders'] / order_count if order_count > 0 else 0
                chilled_ratio = data['chilled_orders'] / order_count if order_count > 0 else 0
                
                # 평균 주문 크기
                avg_order_size = data['total_pallets'] / order_count if order_count > 0 else 0
                
                # 고유 고객 수
                unique_clients_count = len(data['unique_clients'])
                
                rows.append({
                    'date': date,
                    'order_count': order_count,
                    'day_of_week': day_of_week,
                    'day_of_month': day_of_month,
                    'month': month,
                    'week_of_year': week_of_year,
                    'is_weekend': is_weekend,
                    'is_holiday': is_holiday,
                    'is_month_end': is_month_end,
                    'is_month_start': is_month_start,
                    'temperature_zone_frozen_ratio': frozen_ratio,
                    'temperature_zone_chilled_ratio': chilled_ratio,
                    'avg_order_size_pallets': avg_order_size,
                    'unique_clients_count': unique_clients_count
                })
            
            df = pd.DataFrame(rows)
            df = df.sort_values('date')
            
            # 지난주/지난달 주문 수 추가
            df['prev_week_orders'] = df['order_count'].shift(7).fillna(df['order_count'].mean())
            df['prev_month_orders'] = df['order_count'].shift(30).fillna(df['order_count'].mean())
            
            logger.info(f"Prepared {len(df)} days of training data")
            return df
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            return None
    
    def train_model(self, force_retrain: bool = False) -> Dict[str, Any]:
        """
        모델 훈련
        
        Args:
            force_retrain: 기존 모델이 있어도 재훈련
            
        Returns:
            훈련 결과 메트릭
        """
        # 이미 모델이 있고 재훈련이 아니면 스킵
        if self.model is not None and not force_retrain:
            logger.info("Model already loaded. Use force_retrain=True to retrain.")
            return {"status": "skipped", "message": "Model already loaded"}
        
        # 훈련 데이터 준비
        df = self.prepare_training_data(min_days=90)
        
        if df is None or len(df) < 90:
            return {
                "status": "error",
                "message": "Insufficient training data (minimum 90 days required)"
            }
        
        # 특징과 타겟 분리
        X = df[self.feature_columns]
        y = df['order_count']
        
        # 데이터 정규화
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # 모델 훈련
        logger.info("Training Random Forest model for demand forecasting...")
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_scaled, y)
        
        # 평가 (전체 데이터)
        y_pred = self.model.predict(X_scaled)
        mae = np.mean(np.abs(y - y_pred))
        rmse = np.sqrt(np.mean((y - y_pred) ** 2))
        mape = np.mean(np.abs((y - y_pred) / y)) * 100
        
        # 모델 저장
        self._save_model()
        
        logger.info(f"Model training complete. MAE: {mae:.2f}, RMSE: {rmse:.2f}, MAPE: {mape:.2f}%")
        
        return {
            "status": "success",
            "samples": len(df),
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "mape_percent": round(mape, 2),
            "feature_importance": dict(zip(
                self.feature_columns,
                [round(imp, 4) for imp in self.model.feature_importances_]
            ))
        }
    
    def forecast_demand(
        self,
        forecast_date: datetime,
        prev_week_orders: Optional[int] = None,
        prev_month_orders: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        특정 날짜의 수요 예측
        
        Args:
            forecast_date: 예측 날짜
            prev_week_orders: 지난주 주문 수
            prev_month_orders: 지난달 주문 수
            
        Returns:
            예측 결과
        """
        # 모델이 없으면 훈련 시도
        if self.model is None or self.scaler is None:
            logger.info("No model loaded. Attempting to train...")
            train_result = self.train_model()
            
            if train_result['status'] != 'success':
                # 훈련 실패 시 휴리스틱 기반 예측
                return self._heuristic_forecast(forecast_date)
        
        try:
            # 과거 데이터 조회 (지난주/지난달)
            if prev_week_orders is None:
                week_ago = forecast_date - timedelta(days=7)
                prev_week_orders = self.db.query(func.count(Order.id)).filter(
                    func.date(Order.created_at) == week_ago.date()
                ).scalar() or 0
            
            if prev_month_orders is None:
                month_ago = forecast_date - timedelta(days=30)
                prev_month_orders = self.db.query(func.count(Order.id)).filter(
                    func.date(Order.created_at) == month_ago.date()
                ).scalar() or 0
            
            # 최근 온도대 비율 및 평균 주문 크기 계산
            recent_orders = self.db.query(Order).filter(
                Order.created_at >= forecast_date - timedelta(days=30)
            ).all()
            
            if recent_orders:
                frozen_count = sum(1 for o in recent_orders if o.temperature_zone == '냉동')
                chilled_count = sum(1 for o in recent_orders if o.temperature_zone == '냉장')
                total_recent = len(recent_orders)
                
                frozen_ratio = frozen_count / total_recent if total_recent > 0 else 0.4
                chilled_ratio = chilled_count / total_recent if total_recent > 0 else 0.4
                avg_order_size = sum(o.quantity_pallets for o in recent_orders) / total_recent if total_recent > 0 else 10
                unique_clients = len(set(o.client_id for o in recent_orders))
            else:
                frozen_ratio = 0.4
                chilled_ratio = 0.4
                avg_order_size = 10
                unique_clients = 20
            
            # 날짜 특징 추출
            day_of_week = forecast_date.weekday()
            day_of_month = forecast_date.day
            month = forecast_date.month
            week_of_year = forecast_date.isocalendar()[1]
            is_weekend = 1 if day_of_week >= 5 else 0
            is_holiday = 1 if day_of_week == 6 else 0
            is_month_end = 1 if day_of_month >= 28 else 0
            is_month_start = 1 if day_of_month <= 3 else 0
            
            # 특징 벡터 생성
            features = pd.DataFrame([{
                'day_of_week': day_of_week,
                'day_of_month': day_of_month,
                'month': month,
                'week_of_year': week_of_year,
                'is_weekend': is_weekend,
                'is_holiday': is_holiday,
                'is_month_end': is_month_end,
                'is_month_start': is_month_start,
                'temperature_zone_frozen_ratio': frozen_ratio,
                'temperature_zone_chilled_ratio': chilled_ratio,
                'avg_order_size_pallets': avg_order_size,
                'unique_clients_count': unique_clients,
                'prev_week_orders': prev_week_orders,
                'prev_month_orders': prev_month_orders
            }])
            
            # 정규화 및 예측
            features_scaled = self.scaler.transform(features)
            predicted_orders = self.model.predict(features_scaled)[0]
            
            # 신뢰구간
            confidence_interval = predicted_orders * 0.2  # ±20%
            
            return {
                "forecast_date": forecast_date.date().isoformat(),
                "predicted_order_count": max(int(round(predicted_orders)), 0),
                "confidence_interval": int(round(confidence_interval)),
                "min_orders": max(int(round(predicted_orders - confidence_interval)), 0),
                "max_orders": int(round(predicted_orders + confidence_interval)),
                "day_of_week": ["월", "화", "수", "목", "금", "토", "일"][day_of_week],
                "is_weekend": bool(is_weekend),
                "is_holiday": bool(is_holiday),
                "factors": {
                    "prev_week_orders": prev_week_orders,
                    "prev_month_orders": prev_month_orders,
                    "frozen_ratio": round(frozen_ratio, 2),
                    "chilled_ratio": round(chilled_ratio, 2),
                    "avg_order_size_pallets": round(avg_order_size, 1)
                },
                "model": "random_forest"
            }
            
        except Exception as e:
            logger.error(f"Error forecasting demand: {e}")
            return self._heuristic_forecast(forecast_date)
    
    def forecast_next_n_days(self, n_days: int = 7) -> List[Dict[str, Any]]:
        """
        향후 N일 수요 예측
        
        Args:
            n_days: 예측할 일 수
            
        Returns:
            일별 예측 결과 리스트
        """
        forecasts = []
        today = datetime.now()
        
        for i in range(n_days):
            forecast_date = today + timedelta(days=i)
            forecast = self.forecast_demand(forecast_date)
            forecasts.append(forecast)
        
        return forecasts
    
    def _heuristic_forecast(self, forecast_date: datetime) -> Dict[str, Any]:
        """
        휴리스틱 기반 수요 예측 (모델이 없을 때)
        
        기본 공식:
        - 평일: 평균 주문 수
        - 주말: 평균 주문 수 * 0.6
        - 월초/월말: 평균 주문 수 * 1.2
        """
        # 최근 30일 평균 주문 수
        thirty_days_ago = forecast_date - timedelta(days=30)
        avg_orders = self.db.query(func.count(Order.id)).filter(
            Order.created_at >= thirty_days_ago,
            Order.created_at < forecast_date
        ).scalar() / 30.0 or 10.0
        
        day_of_week = forecast_date.weekday()
        day_of_month = forecast_date.day
        
        # 요일 보정
        if day_of_week >= 5:  # 주말
            multiplier = 0.6
        else:
            multiplier = 1.0
        
        # 월초/월말 보정
        if day_of_month <= 3 or day_of_month >= 28:
            multiplier *= 1.2
        
        predicted_orders = avg_orders * multiplier
        
        return {
            "forecast_date": forecast_date.date().isoformat(),
            "predicted_order_count": int(round(predicted_orders)),
            "confidence_interval": int(round(predicted_orders * 0.3)),
            "min_orders": max(int(round(predicted_orders * 0.7)), 0),
            "max_orders": int(round(predicted_orders * 1.3)),
            "day_of_week": ["월", "화", "수", "목", "금", "토", "일"][day_of_week],
            "is_weekend": day_of_week >= 5,
            "model": "heuristic"
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보 조회"""
        if self.model is None:
            return {
                "status": "not_trained",
                "message": "Model not trained yet"
            }
        
        return {
            "status": "trained",
            "model_type": "RandomForestRegressor",
            "features": self.feature_columns,
            "model_file": str(self.model_file),
            "scaler_file": str(self.scaler_file),
            "n_estimators": self.model.n_estimators,
            "feature_importance": dict(zip(
                self.feature_columns,
                [round(imp, 4) for imp in self.model.feature_importances_]
            ))
        }


# 싱글톤 인스턴스
_forecasting_service_instance = None


def get_demand_forecasting_service(db: Session) -> DemandForecastingService:
    """수요 예측 서비스 인스턴스 가져오기"""
    global _forecasting_service_instance
    
    if _forecasting_service_instance is None:
        _forecasting_service_instance = DemandForecastingService(db)
    
    return _forecasting_service_instance
