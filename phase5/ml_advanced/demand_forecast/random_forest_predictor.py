"""
수요 예측 모델 (Random Forest)
주문 수요를 예측하여 배차 계획 최적화
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import logging
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class DemandForecaster:
    """수요 예측 모델 클래스"""
    
    def __init__(self, n_estimators: int = 100, max_depth: int = 10, 
                 random_state: int = 42):
        """
        초기화
        
        Args:
            n_estimators: 트리 개수 (기본값: 100)
            max_depth: 최대 깊이 (기본값: 10)
            random_state: 랜덤 시드 (기본값: 42)
        """
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1  # 모든 CPU 코어 사용
        )
        self.feature_names = None
        self.is_trained = False
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        시계열 특징 생성
        
        Args:
            df: 날짜와 타겟 변수가 포함된 데이터프레임
            
        Returns:
            pd.DataFrame: 특징이 추가된 데이터프레임
        """
        df = df.copy()
        
        # 날짜를 datetime으로 변환
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])
        
        # 기본 시간 특징
        df['day_of_week'] = df['date'].dt.dayofweek  # 0=월요일, 6=일요일
        df['month'] = df['date'].dt.month
        df['day_of_month'] = df['date'].dt.day
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
        df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
        
        # 이동 평균 특징 (7일, 14일, 30일)
        for col in ['order_count', 'total_pallets', 'total_volume']:
            if col in df.columns:
                df[f'{col}_ma7'] = df[col].rolling(window=7, min_periods=1).mean()
                df[f'{col}_ma14'] = df[col].rolling(window=14, min_periods=1).mean()
                df[f'{col}_ma30'] = df[col].rolling(window=30, min_periods=1).mean()
        
        # Lag 특징 (1일, 7일, 14일 전)
        for col in ['order_count', 'total_pallets', 'total_volume']:
            if col in df.columns:
                df[f'{col}_lag1'] = df[col].shift(1)
                df[f'{col}_lag7'] = df[col].shift(7)
                df[f'{col}_lag14'] = df[col].shift(14)
        
        # NaN 값 제거 (초기 lag 기간)
        df = df.dropna()
        
        logger.info(f"✅ 특징 생성 완료: {len(df)} 행, {len(df.columns)} 컬럼")
        return df
    
    def train(self, df: pd.DataFrame, target_column: str = 'order_count',
              test_size: float = 0.2) -> Dict:
        """
        모델 학습
        
        Args:
            df: 학습 데이터프레임 (date, order_count 등 포함)
            target_column: 예측할 타겟 변수명
            test_size: 테스트 데이터 비율 (기본값: 0.2)
            
        Returns:
            Dict: 평가 지표
        """
        # 특징 생성
        df_features = self.create_features(df)
        
        # 특징과 타겟 분리
        feature_cols = [col for col in df_features.columns 
                       if col not in ['date', target_column]]
        X = df_features[feature_cols]
        y = df_features[target_column]
        
        self.feature_names = feature_cols
        
        # Train/Test 분할
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False  # 시계열이므로 shuffle=False
        )
        
        logger.info(f"📊 학습 데이터: {len(X_train)} 행, 테스트 데이터: {len(X_test)} 행")
        
        # 모델 학습
        logger.info("🤖 모델 학습 시작...")
        self.model.fit(X_train, y_train)
        logger.info("✅ 모델 학습 완료!")
        
        self.is_trained = True
        
        # 예측
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)
        
        # 평가 지표 계산
        metrics = {
            'train': {
                'mae': mean_absolute_error(y_train, y_train_pred),
                'rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
                'r2': r2_score(y_train, y_train_pred)
            },
            'test': {
                'mae': mean_absolute_error(y_test, y_test_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
                'r2': r2_score(y_test, y_test_pred)
            }
        }
        
        logger.info(f"\n📈 모델 성능:")
        logger.info(f"  Train - MAE: {metrics['train']['mae']:.2f}, "
                   f"RMSE: {metrics['train']['rmse']:.2f}, "
                   f"R²: {metrics['train']['r2']:.3f}")
        logger.info(f"  Test  - MAE: {metrics['test']['mae']:.2f}, "
                   f"RMSE: {metrics['test']['rmse']:.2f}, "
                   f"R²: {metrics['test']['r2']:.3f}")
        
        # 특징 중요도
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info(f"\n🎯 상위 10개 중요 특징:")
        for idx, row in feature_importance.head(10).iterrows():
            logger.info(f"  {row['feature']}: {row['importance']:.4f}")
        
        return metrics
    
    def predict(self, df: pd.DataFrame, days_ahead: int = 7) -> pd.DataFrame:
        """
        미래 수요 예측
        
        Args:
            df: 과거 데이터프레임
            days_ahead: 예측할 일수 (기본값: 7일)
            
        Returns:
            pd.DataFrame: 예측 결과 (date, predicted_order_count)
        """
        if not self.is_trained:
            raise ValueError("모델이 학습되지 않았습니다. train() 메서드를 먼저 실행하세요.")
        
        # 특징 생성
        df_features = self.create_features(df)
        
        # 마지막 날짜
        last_date = df_features['date'].max()
        
        # 미래 날짜 생성
        future_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=days_ahead
        )
        
        predictions = []
        
        # 각 날짜에 대해 예측
        for future_date in future_dates:
            # 임시 행 생성
            temp_row = pd.DataFrame([{
                'date': future_date,
                'order_count': 0,  # 임시 값
                'total_pallets': 0,
                'total_volume': 0
            }])
            
            # 기존 데이터에 임시 행 추가
            temp_df = pd.concat([df, temp_row], ignore_index=True)
            
            # 특징 생성
            temp_features = self.create_features(temp_df)
            
            # 마지막 행의 특징 추출
            last_features = temp_features[self.feature_names].iloc[-1:]
            
            # 예측
            pred = self.model.predict(last_features)[0]
            
            predictions.append({
                'date': future_date,
                'predicted_order_count': max(0, round(pred))  # 음수 방지 및 반올림
            })
            
            # 예측 값을 실제 값으로 업데이트 (다음 예측에 사용)
            df = pd.concat([df, pd.DataFrame([{
                'date': future_date,
                'order_count': pred,
                'total_pallets': pred * df['total_pallets'].mean() / df['order_count'].mean(),
                'total_volume': pred * df['total_volume'].mean() / df['order_count'].mean()
            }])], ignore_index=True)
        
        result_df = pd.DataFrame(predictions)
        
        logger.info(f"🔮 {days_ahead}일 수요 예측 완료:")
        for idx, row in result_df.iterrows():
            logger.info(f"  {row['date'].date()}: {row['predicted_order_count']} 건")
        
        return result_df
    
    def save_model(self, path: str):
        """
        모델 저장
        
        Args:
            path: 저장 경로
        """
        if not self.is_trained:
            raise ValueError("학습된 모델이 없습니다.")
        
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, path)
        logger.info(f"💾 모델 저장 완료: {path}")
    
    def load_model(self, path: str):
        """
        모델 로드
        
        Args:
            path: 모델 파일 경로
        """
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        self.is_trained = model_data['is_trained']
        logger.info(f"📂 모델 로드 완료: {path}")


# 사용 예시
if __name__ == "__main__":
    import sys
    sys.path.append('/home/user/webapp/phase5')
    
    from ml_advanced.utils.data_loader import DataLoader
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 1. 데이터 로드
    loader = DataLoader()
    
    try:
        # 주문 이력 로드 (최근 180일)
        logger.info("📊 데이터 로드 시작...")
        orders_df = loader.load_order_history(days=180)
        
        # 일별 수요 집계
        daily_df = loader.aggregate_daily_demand(orders_df)
        
        # 2. 모델 학습
        forecaster = DemandForecaster()
        metrics = forecaster.train(daily_df, target_column='order_count')
        
        # 3. 미래 예측 (7일)
        predictions = forecaster.predict(daily_df, days_ahead=7)
        print("\n🔮 예측 결과:")
        print(predictions)
        
        # 4. 모델 저장
        model_path = '/home/user/webapp/phase5/models/demand_forecast_model.pkl'
        forecaster.save_model(model_path)
        
    finally:
        loader.close()
