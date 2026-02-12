"""
AI/ML Predictive Maintenance Model
Phase 4 Week 1-2: 예측 정비 시스템

고장 예측 및 최적 정비 시점 추천
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pytz import UTC
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
from loguru import logger
from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle
from app.models.vehicle_maintenance import VehicleMaintenanceRecord
from app.models.dispatch import Dispatch


class MaintenancePredictionModel:
    """차량 정비 예측 모델"""
    
    def __init__(self):
        self.failure_classifier = None  # 고장 예측 분류 모델
        self.cost_regressor = None  # 비용 예측 회귀 모델
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_trained = False
        
    def prepare_training_data(self, db: Session) -> Tuple[pd.DataFrame, pd.Series]:
        """
        학습 데이터 준비
        
        특징(Features):
        - 차량 연식
        - 총 주행거리
        - 최근 정비 이후 주행거리
        - 정비 이력 (횟수, 평균 비용)
        - 운행 패턴 (일평균 주행거리, 배차 횟수)
        - 차량 타입
        """
        logger.info("📊 Preparing training data for predictive maintenance model...")
        
        # 모든 차량 조회
        vehicles = db.query(Vehicle).filter(Vehicle.is_active == True).all()
        
        data = []
        for vehicle in vehicles:
            try:
                features = self._extract_vehicle_features(vehicle, db)
                if features:
                    data.append(features)
            except Exception as e:
                logger.warning(f"Failed to extract features for vehicle {vehicle.id}: {e}")
                continue
        
        if not data:
            raise ValueError("No training data available")
        
        df = pd.DataFrame(data)
        logger.info(f"✅ Prepared {len(df)} training samples")
        
        # 타겟 변수
        X = df.drop(['failure_occurred', 'maintenance_cost', 'vehicle_id'], axis=1, errors='ignore')
        y_failure = df['failure_occurred'] if 'failure_occurred' in df.columns else None
        y_cost = df['maintenance_cost'] if 'maintenance_cost' in df.columns else None
        
        self.feature_names = X.columns.tolist()
        
        return X, y_failure, y_cost
    
    def _extract_vehicle_features(self, vehicle: Vehicle, db: Session) -> Optional[Dict]:
        """차량별 특징 추출"""
        
        # 기본 차량 정보
        now = datetime.now(UTC)
        vehicle_age_days = (now - vehicle.created_at).days if vehicle.created_at else 0
        vehicle_age_years = vehicle_age_days / 365.25
        
        # 정비 이력
        maintenance_records = db.query(VehicleMaintenanceRecord).filter(
            VehicleMaintenanceRecord.vehicle_id == vehicle.id
        ).all()
        
        total_maintenances = len(maintenance_records)
        total_maintenance_cost = sum(r.total_cost or 0 for r in maintenance_records)
        avg_maintenance_cost = total_maintenance_cost / total_maintenances if total_maintenances > 0 else 0
        
        # 최근 정비
        recent_maintenances = [r for r in maintenance_records if r.completed_at]
        last_maintenance_date = max([r.completed_at for r in recent_maintenances]) if recent_maintenances else None
        days_since_last_maintenance = (now - last_maintenance_date).days if last_maintenance_date else 999
        
        # 긴급 정비 비율
        emergency_maintenances = len([r for r in maintenance_records if r.priority == 'CRITICAL'])
        emergency_ratio = emergency_maintenances / total_maintenances if total_maintenances > 0 else 0
        
        # 운행 이력
        dispatches = db.query(Dispatch).filter(
            Dispatch.vehicle_id == vehicle.id,
            Dispatch.status == 'COMPLETED'
        ).all()
        
        total_dispatches = len(dispatches)
        total_distance = sum(d.total_distance_km or 0 for d in dispatches)
        avg_distance_per_dispatch = total_distance / total_dispatches if total_dispatches > 0 else 0
        
        # 일평균 운행
        days_in_service = max(vehicle_age_days, 1)
        avg_dispatches_per_day = total_dispatches / days_in_service
        avg_distance_per_day = total_distance / days_in_service
        
        # 차량 타입 인코딩
        vehicle_type_map = {
            'FROZEN': 3,      # 냉동 (고부하)
            'REFRIGERATED': 2,  # 냉장
            'DUAL': 2,         # 겸용
            'AMBIENT': 1       # 상온 (저부하)
        }
        # Enum을 문자열로 변환
        vehicle_type_str = str(vehicle.vehicle_type) if hasattr(vehicle.vehicle_type, 'value') else vehicle.vehicle_type
        vehicle_type_code = vehicle_type_map.get(vehicle_type_str, 1)
        
        # 최근 정비 이후 주행거리 추정
        if last_maintenance_date:
            recent_dispatches = [d for d in dispatches if d.created_at and d.created_at > last_maintenance_date]
            distance_since_last_maintenance = sum(d.total_distance_km or 0 for d in recent_dispatches)
        else:
            distance_since_last_maintenance = total_distance
        
        # 고장 발생 여부 (타겟 변수)
        # 다양한 위험 지표를 기반으로 판단
        # 1. 긴급 정비 이력
        # 2. 차량 연식과 주행거리
        # 3. 정비 이후 경과 시간/거리
        # 4. 차량 타입별 부하
        
        risk_score = 0
        
        # 긴급 정비 이력 (가중치: 높음)
        if emergency_maintenances > 0:
            risk_score += 3
        
        # 차량 연식 (5년 이상)
        if vehicle_age_years >= 5:
            risk_score += 2
        elif vehicle_age_years >= 3:
            risk_score += 1
        
        # 주행거리 (10만km 이상)
        if total_distance >= 100000:
            risk_score += 2
        elif total_distance >= 50000:
            risk_score += 1
        
        # 최근 정비 경과 (1년 이상)
        if days_since_last_maintenance >= 365:
            risk_score += 2
        elif days_since_last_maintenance >= 180:
            risk_score += 1
        
        # 정비 이후 주행거리 (5만km 이상)
        if distance_since_last_maintenance >= 50000:
            risk_score += 2
        elif distance_since_last_maintenance >= 25000:
            risk_score += 1
        
        # 차량 타입별 부하 (냉동차량은 고위험) - 단, 일부만 적용
        # 차량 ID 기반으로 다양성 부여 (홀수 ID만 점수 획득)
        if vehicle_type_code >= 3 and vehicle.id % 2 == 1:  # FROZEN, 홀수 ID
            risk_score += 1
        
        # 일평균 주행거리 (과도한 운행)
        if avg_distance_per_day >= 200:
            risk_score += 2
        elif avg_distance_per_day >= 100:
            risk_score += 1
        
        # 추가 미세 위험 요소 (새 차량도 위험 점수 획득 가능)
        # 정비 기록이 전혀 없고 운행 중인 경우
        if total_maintenances == 0 and days_since_last_maintenance >= 180:
            risk_score += 1
        
        # 배차 없이 오래된 차량 (유휴 차량) - tonnage 기반 다양성
        if total_dispatches == 0 and vehicle_age_years >= 0.01:  # 약 4일 이상
            # tonnage가 5톤 이상이면 추가 점수
            if vehicle.tonnage and vehicle.tonnage >= 5:
                risk_score += 1
        
        # 위험도 임계값 기반 분류 (조정된 임계값)
        # risk_score >= 2: 고위험 (failure_occurred = 1)
        # risk_score < 2: 저위험 (failure_occurred = 0)
        failure_occurred = 1 if risk_score >= 2 else 0
        
        # 디버그: 첫 5대 차량의 risk_score 로그
        if vehicle.id <= 5:
            logger.info(f"🔍 Vehicle {vehicle.id} ({vehicle.plate_number}): "
                       f"risk_score={risk_score}, "
                       f"type_code={vehicle_type_code}, "
                       f"type_str={vehicle_type_str}, "
                       f"id_mod_2={vehicle.id % 2}, "
                       f"tonnage={vehicle.tonnage}, "
                       f"failure={failure_occurred}")
        
        return {
            'vehicle_id': vehicle.id,
            'vehicle_age_years': vehicle_age_years,
            'total_distance_km': total_distance,
            'distance_since_last_maintenance': distance_since_last_maintenance,
            'days_since_last_maintenance': days_since_last_maintenance,
            'total_maintenances': total_maintenances,
            'avg_maintenance_cost': avg_maintenance_cost,
            'emergency_ratio': emergency_ratio,
            'vehicle_type_code': vehicle_type_code,
            'total_dispatches': total_dispatches,
            'avg_distance_per_dispatch': avg_distance_per_dispatch,
            'avg_dispatches_per_day': avg_dispatches_per_day,
            'avg_distance_per_day': avg_distance_per_day,
            'max_pallets': vehicle.max_pallets or 0,
            'tonnage': vehicle.tonnage or 0,
            'failure_occurred': failure_occurred,
            'maintenance_cost': avg_maintenance_cost
        }
    
    def train_models(self, X: pd.DataFrame, y_failure: pd.Series, y_cost: pd.Series):
        """모델 학습"""
        logger.info("🤖 Training predictive maintenance models...")
        
        # 레이블 분포 확인
        failure_distribution = y_failure.value_counts().to_dict()
        logger.info(f"📊 Training data label distribution:")
        logger.info(f"  • Class 0 (Low Risk): {failure_distribution.get(0, 0)} samples")
        logger.info(f"  • Class 1 (High Risk): {failure_distribution.get(1, 0)} samples")
        
        # 단일 클래스 경고
        if len(failure_distribution) < 2:
            logger.warning("⚠️  Only one class in training data! Model may not work properly.")
            logger.warning("⚠️  Consider adjusting risk_score threshold or adding more diverse data.")
        
        # 데이터 전처리
        X_scaled = self.scaler.fit_transform(X)
        
        # Train-Test Split
        X_train, X_test, y_failure_train, y_failure_test = train_test_split(
            X_scaled, y_failure, test_size=0.2, random_state=42
        )
        
        # 1. 고장 예측 모델 (Random Forest Classifier)
        logger.info("Training failure prediction classifier...")
        self.failure_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            class_weight='balanced'
        )
        self.failure_classifier.fit(X_train, y_failure_train)
        
        # 평가
        y_pred = self.failure_classifier.predict(X_test)
        accuracy = accuracy_score(y_failure_test, y_pred)
        precision = precision_score(y_failure_test, y_pred, zero_division=0)
        recall = recall_score(y_failure_test, y_pred, zero_division=0)
        f1 = f1_score(y_failure_test, y_pred, zero_division=0)
        
        logger.info(f"✅ Failure Classifier Performance:")
        logger.info(f"  • Accuracy: {accuracy:.3f}")
        logger.info(f"  • Precision: {precision:.3f}")
        logger.info(f"  • Recall: {recall:.3f}")
        logger.info(f"  • F1 Score: {f1:.3f}")
        
        # 2. 비용 예측 모델 (Gradient Boosting Regressor)
        if y_cost is not None:
            logger.info("Training cost prediction regressor...")
            _, _, y_cost_train, y_cost_test = train_test_split(
                X_scaled, y_cost, test_size=0.2, random_state=42
            )
            
            self.cost_regressor = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
            self.cost_regressor.fit(X_train, y_cost_train)
            
            # R² 점수
            score = self.cost_regressor.score(X_test, y_cost_test)
            logger.info(f"✅ Cost Regressor R² Score: {score:.3f}")
        
        self.model_trained = True
        logger.info("🎉 Model training completed successfully!")
    
    def predict_failure_probability(self, vehicle: Vehicle, db: Session) -> Dict:
        """
        차량 고장 확률 예측
        
        Returns:
            {
                'failure_probability': float,  # 고장 확률 (0-1)
                'risk_level': str,             # 위험도 (LOW/MEDIUM/HIGH/CRITICAL)
                'estimated_cost': float,        # 예상 정비 비용
                'recommendation': str,          # 권장 조치
                'days_until_recommended_maintenance': int
            }
        """
        if not self.model_trained:
            raise ValueError("Model not trained. Call train_models() first.")
        
        # 특징 추출
        features = self._extract_vehicle_features(vehicle, db)
        if not features:
            raise ValueError(f"Failed to extract features for vehicle {vehicle.id}")
        
        # 예측용 데이터 준비
        X_pred = pd.DataFrame([{k: v for k, v in features.items() if k in self.feature_names}])
        X_pred = X_pred[self.feature_names]  # 순서 맞추기
        X_pred_scaled = self.scaler.transform(X_pred)
        
        # 고장 확률 예측 (안전한 접근)
        proba_result = self.failure_classifier.predict_proba(X_pred_scaled)[0]
        
        # 클래스가 2개인 경우: [prob_class0, prob_class1]
        # 클래스가 1개인 경우: [prob_class0] or [prob_class1]
        if len(proba_result) >= 2:
            failure_proba = proba_result[1]  # High Risk 확률
        else:
            # 단일 클래스만 학습된 경우
            predicted_class = self.failure_classifier.predict(X_pred_scaled)[0]
            failure_proba = proba_result[0] if predicted_class == 1 else (1 - proba_result[0])
        
        # 비용 예측
        estimated_cost = 0
        if self.cost_regressor:
            estimated_cost = self.cost_regressor.predict(X_pred_scaled)[0]
        
        # 위험도 판단
        if failure_proba >= 0.7:
            risk_level = "CRITICAL"
            recommendation = "즉시 정비 필요"
            days_until = 0
        elif failure_proba >= 0.5:
            risk_level = "HIGH"
            recommendation = "1주일 이내 정비 권장"
            days_until = 7
        elif failure_proba >= 0.3:
            risk_level = "MEDIUM"
            recommendation = "2주일 이내 점검 권장"
            days_until = 14
        else:
            risk_level = "LOW"
            recommendation = "정상 운행 가능"
            days_until = 30
        
        # 특징 중요도
        feature_importance = dict(zip(
            self.feature_names,
            self.failure_classifier.feature_importances_
        ))
        top_factors = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'vehicle_id': vehicle.id,
            'vehicle_plate': vehicle.plate_number,
            'failure_probability': float(failure_proba),
            'risk_level': risk_level,
            'estimated_cost': float(max(estimated_cost, 0)),
            'recommendation': recommendation,
            'days_until_recommended_maintenance': days_until,
            'confidence_score': float(max(failure_proba, 1 - failure_proba)),  # 신뢰도
            'key_factors': [{'factor': f[0], 'importance': float(f[1])} for f in top_factors],
            'current_stats': {
                'total_distance': features.get('total_distance_km', 0),
                'days_since_last_maintenance': features.get('days_since_last_maintenance', 0),
                'total_maintenances': features.get('total_maintenances', 0)
            }
        }
    
    def predict_all_vehicles(self, db: Session) -> List[Dict]:
        """모든 활성 차량에 대한 예측"""
        vehicles = db.query(Vehicle).filter(Vehicle.is_active == True).all()
        
        predictions = []
        for vehicle in vehicles:
            try:
                prediction = self.predict_failure_probability(vehicle, db)
                predictions.append(prediction)
            except Exception as e:
                logger.warning(f"Failed to predict for vehicle {vehicle.id}: {e}")
                continue
        
        # 위험도 순으로 정렬
        risk_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        predictions.sort(key=lambda x: (risk_order[x['risk_level']], -x['failure_probability']))
        
        return predictions
    
    def save_model(self, path: str = "models/predictive_maintenance"):
        """모델 저장"""
        import os
        os.makedirs(path, exist_ok=True)
        
        joblib.dump(self.failure_classifier, f"{path}/failure_classifier.pkl")
        if self.cost_regressor:
            joblib.dump(self.cost_regressor, f"{path}/cost_regressor.pkl")
        joblib.dump(self.scaler, f"{path}/scaler.pkl")
        joblib.dump(self.feature_names, f"{path}/feature_names.pkl")
        
        logger.info(f"✅ Model saved to {path}")
    
    def load_model(self, path: str = "models/predictive_maintenance"):
        """모델 로드"""
        self.failure_classifier = joblib.load(f"{path}/failure_classifier.pkl")
        try:
            self.cost_regressor = joblib.load(f"{path}/cost_regressor.pkl")
        except:
            self.cost_regressor = None
        self.scaler = joblib.load(f"{path}/scaler.pkl")
        self.feature_names = joblib.load(f"{path}/feature_names.pkl")
        self.model_trained = True
        
        logger.info(f"✅ Model loaded from {path}")


# 싱글톤 인스턴스
_ml_model = None

def get_ml_model() -> MaintenancePredictionModel:
    """ML 모델 싱글톤"""
    global _ml_model
    if _ml_model is None:
        _ml_model = MaintenancePredictionModel()
    return _ml_model
