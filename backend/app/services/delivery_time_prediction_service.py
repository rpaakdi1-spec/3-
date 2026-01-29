"""
배송 시간 예측 ML 모델
- 과거 배송 데이터 기반 배송 시간 예측
- Random Forest Regressor 사용
- 실시간 예측 및 자동 학습
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
from pathlib import Path
from loguru import logger

from app.models.dispatch import Dispatch
from app.models.order import Order
from app.models.vehicle import Vehicle
from app.models.client import Client


class DeliveryTimePredictionService:
    """배송 시간 예측 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        import os
        model_base = os.getenv("ML_MODELS_DIR", "./ml_models")
        self.model_path = Path(model_base)
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        self.model_file = self.model_path / "delivery_time_model.pkl"
        self.model = None
        self.feature_columns = [
            'distance_km',
            'order_quantity_pallets',
            'vehicle_capacity_pallets',
            'hour_of_day',
            'day_of_week',
            'is_rush_hour',
            'temperature_zone',  # 0=냉동, 1=냉장, 2=상온
            'order_count',
            'avg_stop_duration_minutes'
        ]
        
        # 모델 로드 시도
        self._load_model()
    
    def _load_model(self):
        """저장된 모델 로드"""
        try:
            if self.model_file.exists():
                self.model = joblib.load(self.model_file)
                logger.info(f"Loaded delivery time prediction model from {self.model_file}")
            else:
                logger.info("No existing model found. Will train on first prediction.")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
    
    def _save_model(self):
        """모델 저장"""
        try:
            joblib.dump(self.model, self.model_file)
            logger.info(f"Saved delivery time prediction model to {self.model_file}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def prepare_training_data(self, min_samples: int = 100) -> Optional[Tuple[pd.DataFrame, pd.Series]]:
        """
        훈련 데이터 준비
        
        Args:
            min_samples: 최소 샘플 수
            
        Returns:
            (features, target) 또는 None
        """
        try:
            # 완료된 배차 조회 (실제 배송 시간이 있는 것)
            completed_dispatches = self.db.query(Dispatch).filter(
                Dispatch.status == 'completed',
                Dispatch.actual_duration_minutes.isnot(None),
                Dispatch.actual_duration_minutes > 0
            ).all()
            
            if len(completed_dispatches) < min_samples:
                logger.warning(f"Insufficient training data: {len(completed_dispatches)} < {min_samples}")
                return None
            
            # 데이터 추출
            data = []
            for dispatch in completed_dispatches:
                # 주문 정보
                orders = dispatch.orders
                total_pallets = sum(o.quantity_pallets for o in orders)
                order_count = len(orders)
                
                # 차량 정보
                vehicle = dispatch.vehicle
                vehicle_capacity = vehicle.capacity_pallets if vehicle else 20
                
                # 온도대 매핑
                temp_zone = 0  # 기본값 냉동
                if vehicle and vehicle.vehicle_type == '냉장':
                    temp_zone = 1
                elif vehicle and vehicle.vehicle_type == '상온':
                    temp_zone = 2
                
                # 시간 정보
                dispatch_time = dispatch.dispatch_date
                hour_of_day = dispatch_time.hour if dispatch_time else 9
                day_of_week = dispatch_time.weekday() if dispatch_time else 0
                is_rush_hour = 1 if hour_of_day in [7, 8, 9, 17, 18, 19] else 0
                
                # 거리 정보
                distance_km = dispatch.total_distance_km or 50.0
                
                # 평균 정차 시간 (분)
                avg_stop_duration = 15.0  # 기본값
                if order_count > 0:
                    # 전체 시간에서 이동 시간을 빼고 주문 수로 나눔
                    # 이동 시간 ≈ distance_km / 30 * 60 (30km/h 평균 속도)
                    travel_time = (distance_km / 30.0) * 60
                    stop_time = dispatch.actual_duration_minutes - travel_time
                    avg_stop_duration = max(stop_time / order_count, 5.0)
                
                data.append({
                    'distance_km': distance_km,
                    'order_quantity_pallets': total_pallets,
                    'vehicle_capacity_pallets': vehicle_capacity,
                    'hour_of_day': hour_of_day,
                    'day_of_week': day_of_week,
                    'is_rush_hour': is_rush_hour,
                    'temperature_zone': temp_zone,
                    'order_count': order_count,
                    'avg_stop_duration_minutes': avg_stop_duration,
                    'actual_duration_minutes': dispatch.actual_duration_minutes
                })
            
            df = pd.DataFrame(data)
            
            # 이상치 제거 (배송 시간이 너무 짧거나 긴 경우)
            df = df[(df['actual_duration_minutes'] >= 30) & (df['actual_duration_minutes'] <= 720)]
            
            X = df[self.feature_columns]
            y = df['actual_duration_minutes']
            
            logger.info(f"Prepared {len(df)} training samples")
            return X, y
            
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
        training_data = self.prepare_training_data(min_samples=100)
        
        if training_data is None:
            return {
                "status": "error",
                "message": "Insufficient training data (minimum 100 samples required)"
            }
        
        X, y = training_data
        
        # 데이터 분할
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # 모델 훈련
        logger.info("Training Random Forest model...")
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # 평가
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # 모델 저장
        self._save_model()
        
        logger.info(f"Model training complete. MAE: {mae:.2f} minutes, R²: {r2:.3f}")
        
        return {
            "status": "success",
            "samples": len(X),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "mae_minutes": round(mae, 2),
            "r2_score": round(r2, 3),
            "feature_importance": dict(zip(
                self.feature_columns,
                [round(imp, 4) for imp in self.model.feature_importances_]
            ))
        }
    
    def predict_delivery_time(
        self,
        distance_km: float,
        order_quantity_pallets: int,
        vehicle_capacity_pallets: int,
        dispatch_time: datetime,
        temperature_zone: str,  # '냉동', '냉장', '상온'
        order_count: int = 1
    ) -> Dict[str, Any]:
        """
        배송 시간 예측
        
        Args:
            distance_km: 총 거리
            order_quantity_pallets: 총 팔레트 수
            vehicle_capacity_pallets: 차량 용량
            dispatch_time: 배차 시간
            temperature_zone: 온도대
            order_count: 주문 수
            
        Returns:
            예측 결과
        """
        # 모델이 없으면 훈련 시도
        if self.model is None:
            logger.info("No model loaded. Attempting to train...")
            train_result = self.train_model()
            
            if train_result['status'] != 'success':
                # 훈련 실패 시 휴리스틱 기반 예측
                return self._heuristic_prediction(
                    distance_km, order_quantity_pallets, order_count
                )
        
        try:
            # 특징 추출
            hour_of_day = dispatch_time.hour
            day_of_week = dispatch_time.weekday()
            is_rush_hour = 1 if hour_of_day in [7, 8, 9, 17, 18, 19] else 0
            
            # 온도대 매핑
            temp_zone_map = {'냉동': 0, '냉장': 1, '상온': 2}
            temp_zone_encoded = temp_zone_map.get(temperature_zone, 0)
            
            # 평균 정차 시간 추정 (온도대에 따라)
            avg_stop_duration_map = {'냉동': 20.0, '냉장': 15.0, '상온': 10.0}
            avg_stop_duration = avg_stop_duration_map.get(temperature_zone, 15.0)
            
            # 특징 벡터 생성
            features = pd.DataFrame([{
                'distance_km': distance_km,
                'order_quantity_pallets': order_quantity_pallets,
                'vehicle_capacity_pallets': vehicle_capacity_pallets,
                'hour_of_day': hour_of_day,
                'day_of_week': day_of_week,
                'is_rush_hour': is_rush_hour,
                'temperature_zone': temp_zone_encoded,
                'order_count': order_count,
                'avg_stop_duration_minutes': avg_stop_duration
            }])
            
            # 예측
            predicted_minutes = self.model.predict(features)[0]
            
            # 신뢰구간 계산 (단순 추정)
            confidence_interval = predicted_minutes * 0.15  # ±15%
            
            return {
                "predicted_duration_minutes": round(predicted_minutes, 1),
                "predicted_duration_hours": round(predicted_minutes / 60, 2),
                "confidence_interval_minutes": round(confidence_interval, 1),
                "estimated_arrival_time": (dispatch_time + timedelta(minutes=predicted_minutes)).isoformat(),
                "factors": {
                    "distance_km": distance_km,
                    "order_count": order_count,
                    "temperature_zone": temperature_zone,
                    "is_rush_hour": bool(is_rush_hour),
                    "hour_of_day": hour_of_day
                },
                "model": "random_forest"
            }
            
        except Exception as e:
            logger.error(f"Error predicting delivery time: {e}")
            return self._heuristic_prediction(
                distance_km, order_quantity_pallets, order_count
            )
    
    def _heuristic_prediction(
        self,
        distance_km: float,
        order_quantity_pallets: int,
        order_count: int
    ) -> Dict[str, Any]:
        """
        휴리스틱 기반 배송 시간 예측 (모델이 없을 때)
        
        기본 공식:
        - 이동 시간 = distance_km / 30 * 60 (30km/h 평균 속도)
        - 정차 시간 = order_count * 15 (주문당 15분)
        - 적재/하역 시간 = order_quantity_pallets * 2 (팔레트당 2분)
        """
        travel_time = (distance_km / 30.0) * 60  # 분
        stop_time = order_count * 15
        loading_time = order_quantity_pallets * 2
        
        total_time = travel_time + stop_time + loading_time
        
        return {
            "predicted_duration_minutes": round(total_time, 1),
            "predicted_duration_hours": round(total_time / 60, 2),
            "confidence_interval_minutes": round(total_time * 0.2, 1),
            "factors": {
                "travel_time_minutes": round(travel_time, 1),
                "stop_time_minutes": round(stop_time, 1),
                "loading_time_minutes": round(loading_time, 1)
            },
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
            "n_estimators": self.model.n_estimators,
            "feature_importance": dict(zip(
                self.feature_columns,
                [round(imp, 4) for imp in self.model.feature_importances_]
            ))
        }


# 싱글톤 인스턴스
_prediction_service_instance = None


def get_delivery_time_prediction_service(db: Session) -> DeliveryTimePredictionService:
    """배송 시간 예측 서비스 인스턴스 가져오기"""
    global _prediction_service_instance
    
    if _prediction_service_instance is None:
        _prediction_service_instance = DeliveryTimePredictionService(db)
    
    return _prediction_service_instance
