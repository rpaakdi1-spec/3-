"""
이상 탐지 모델 (Isolation Forest)
배차 및 차량 데이터에서 이상 패턴 탐지
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import logging
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """이상 탐지 모델 클래스"""
    
    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        """
        초기화
        
        Args:
            contamination: 이상치 비율 (기본값: 0.1 = 10%)
            random_state: 랜덤 시드 (기본값: 42)
        """
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100,
            max_samples='auto',
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_trained = False
    
    def prepare_dispatch_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        배차 데이터 특징 준비
        
        Args:
            df: 배차 이력 데이터프레임
            
        Returns:
            pd.DataFrame: 특징 데이터프레임
        """
        features_df = df.copy()
        
        # 시간 특징
        features_df['dispatch_date'] = pd.to_datetime(features_df['dispatch_date'])
        features_df['day_of_week'] = features_df['dispatch_date'].dt.dayofweek
        features_df['hour'] = features_df['dispatch_date'].dt.hour
        features_df['is_weekend'] = (features_df['day_of_week'] >= 5).astype(int)
        
        # 수치형 특징 선택
        numeric_features = [
            'total_distance_km',
            'total_duration_minutes',
            'max_pallets',
            'max_weight_kg',
            'max_volume_cbm',
            'day_of_week',
            'hour',
            'is_weekend'
        ]
        
        # 존재하는 컬럼만 선택
        available_features = [f for f in numeric_features if f in features_df.columns]
        
        result_df = features_df[available_features].copy()
        
        # 파생 특징 추가
        if 'total_distance_km' in result_df.columns and 'total_duration_minutes' in result_df.columns:
            # 평균 속도 (km/h)
            result_df['avg_speed_kmh'] = np.where(
                result_df['total_duration_minutes'] > 0,
                (result_df['total_distance_km'] / result_df['total_duration_minutes']) * 60,
                0
            )
        
        if 'total_distance_km' in result_df.columns and 'max_volume_cbm' in result_df.columns:
            # 거리 당 용적 (km당 CBM)
            result_df['distance_per_volume'] = np.where(
                result_df['max_volume_cbm'] > 0,
                result_df['total_distance_km'] / result_df['max_volume_cbm'],
                0
            )
        
        # NaN 값을 0으로 대체
        result_df = result_df.fillna(0)
        
        # 무한대 값을 0으로 대체
        result_df = result_df.replace([np.inf, -np.inf], 0)
        
        logger.info(f"✅ 배차 특징 준비 완료: {len(result_df)} 행, {len(result_df.columns)} 특징")
        return result_df
    
    def prepare_vehicle_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        차량 GPS 데이터 특징 준비
        
        Args:
            df: GPS 로그 데이터프레임
            
        Returns:
            pd.DataFrame: 특징 데이터프레임
        """
        features_df = df.copy()
        
        # 수치형 특징
        numeric_features = [
            'speed_kmh',
            'temperature_celsius',
            'battery_voltage'
        ]
        
        # 존재하는 컬럼만 선택
        available_features = [f for f in numeric_features if f in features_df.columns]
        
        result_df = features_df[available_features].copy()
        
        # ignition_on 변환 (boolean -> int)
        if 'ignition_on' in features_df.columns:
            result_df['ignition_on'] = features_df['ignition_on'].astype(int)
        
        # NaN 값을 0으로 대체
        result_df = result_df.fillna(0)
        
        logger.info(f"✅ 차량 특징 준비 완료: {len(result_df)} 행, {len(result_df.columns)} 특징")
        return result_df
    
    def train(self, df: pd.DataFrame, feature_type: str = 'dispatch') -> Dict:
        """
        모델 학습
        
        Args:
            df: 학습 데이터프레임
            feature_type: 특징 유형 ('dispatch' 또는 'vehicle')
            
        Returns:
            Dict: 학습 결과 통계
        """
        # 특징 준비
        if feature_type == 'dispatch':
            features_df = self.prepare_dispatch_features(df)
        elif feature_type == 'vehicle':
            features_df = self.prepare_vehicle_features(df)
        else:
            raise ValueError(f"지원하지 않는 feature_type: {feature_type}")
        
        self.feature_names = features_df.columns.tolist()
        
        # 특징 스케일링
        X_scaled = self.scaler.fit_transform(features_df)
        
        logger.info(f"🤖 이상 탐지 모델 학습 시작... ({len(X_scaled)} 샘플)")
        
        # 모델 학습
        self.model.fit(X_scaled)
        
        # 예측
        predictions = self.model.predict(X_scaled)
        anomaly_scores = self.model.score_samples(X_scaled)
        
        self.is_trained = True
        
        # 통계
        n_anomalies = (predictions == -1).sum()
        n_normal = (predictions == 1).sum()
        anomaly_ratio = n_anomalies / len(predictions) * 100
        
        stats = {
            'total_samples': len(predictions),
            'normal_count': int(n_normal),
            'anomaly_count': int(n_anomalies),
            'anomaly_ratio': float(anomaly_ratio),
            'min_score': float(anomaly_scores.min()),
            'max_score': float(anomaly_scores.max()),
            'mean_score': float(anomaly_scores.mean())
        }
        
        logger.info(f"✅ 모델 학습 완료!")
        logger.info(f"  전체 샘플: {stats['total_samples']}")
        logger.info(f"  정상: {stats['normal_count']} ({100 - anomaly_ratio:.1f}%)")
        logger.info(f"  이상: {stats['anomaly_count']} ({anomaly_ratio:.1f}%)")
        logger.info(f"  이상 점수 범위: [{stats['min_score']:.3f}, {stats['max_score']:.3f}]")
        
        return stats
    
    def detect(self, df: pd.DataFrame, feature_type: str = 'dispatch',
               threshold: Optional[float] = None) -> pd.DataFrame:
        """
        이상 탐지
        
        Args:
            df: 탐지할 데이터프레임
            feature_type: 특징 유형 ('dispatch' 또는 'vehicle')
            threshold: 이상 점수 임계값 (선택사항, 기본값: None)
            
        Returns:
            pd.DataFrame: 원본 데이터 + 예측 결과 + 이상 점수
        """
        if not self.is_trained:
            raise ValueError("모델이 학습되지 않았습니다. train() 메서드를 먼저 실행하세요.")
        
        # 특징 준비
        if feature_type == 'dispatch':
            features_df = self.prepare_dispatch_features(df)
        elif feature_type == 'vehicle':
            features_df = self.prepare_vehicle_features(df)
        else:
            raise ValueError(f"지원하지 않는 feature_type: {feature_type}")
        
        # 특징 스케일링
        X_scaled = self.scaler.transform(features_df)
        
        # 예측
        predictions = self.model.predict(X_scaled)
        anomaly_scores = self.model.score_samples(X_scaled)
        
        # 결과 데이터프레임 생성
        result_df = df.copy()
        result_df['is_anomaly'] = (predictions == -1).astype(int)
        result_df['anomaly_score'] = anomaly_scores
        
        # 임계값 적용 (선택사항)
        if threshold is not None:
            result_df['is_anomaly'] = (anomaly_scores < threshold).astype(int)
        
        # 이상치만 필터링
        anomalies = result_df[result_df['is_anomaly'] == 1]
        
        logger.info(f"🔍 이상 탐지 완료:")
        logger.info(f"  전체: {len(result_df)} 건")
        logger.info(f"  이상: {len(anomalies)} 건 ({len(anomalies)/len(result_df)*100:.1f}%)")
        
        if len(anomalies) > 0:
            logger.info(f"\n⚠️ 상위 5개 이상 패턴:")
            top_anomalies = anomalies.nsmallest(5, 'anomaly_score')
            for idx, row in top_anomalies.iterrows():
                logger.info(f"  Index {idx}: Score {row['anomaly_score']:.3f}")
        
        return result_df
    
    def get_anomaly_features(self, df: pd.DataFrame, 
                            feature_type: str = 'dispatch') -> pd.DataFrame:
        """
        이상치의 주요 특징 분석
        
        Args:
            df: 탐지 결과 데이터프레임 (is_anomaly 컬럼 포함)
            feature_type: 특징 유형
            
        Returns:
            pd.DataFrame: 특징 통계 비교
        """
        if 'is_anomaly' not in df.columns:
            raise ValueError("데이터프레임에 'is_anomaly' 컬럼이 없습니다.")
        
        # 특징 준비
        if feature_type == 'dispatch':
            features_df = self.prepare_dispatch_features(df)
        else:
            features_df = self.prepare_vehicle_features(df)
        
        # 이상치와 정상 데이터 분리
        anomaly_features = features_df[df['is_anomaly'] == 1]
        normal_features = features_df[df['is_anomaly'] == 0]
        
        # 특징별 평균 비교
        comparison = pd.DataFrame({
            'feature': self.feature_names,
            'normal_mean': normal_features.mean(),
            'anomaly_mean': anomaly_features.mean(),
        })
        
        comparison['diff_ratio'] = (
            (comparison['anomaly_mean'] - comparison['normal_mean']) / 
            comparison['normal_mean'].replace(0, 1)
        ).abs()
        
        # 차이가 큰 순서로 정렬
        comparison = comparison.sort_values('diff_ratio', ascending=False)
        
        logger.info(f"\n📊 이상치 주요 특징 (상위 5개):")
        for idx, row in comparison.head(5).iterrows():
            logger.info(f"  {row['feature']}:")
            logger.info(f"    정상 평균: {row['normal_mean']:.2f}")
            logger.info(f"    이상 평균: {row['anomaly_mean']:.2f}")
            logger.info(f"    차이 비율: {row['diff_ratio']:.2%}")
        
        return comparison
    
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
            'scaler': self.scaler,
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
        self.scaler = model_data['scaler']
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
        # 배차 이력 로드 (최근 90일)
        logger.info("📊 데이터 로드 시작...")
        dispatch_df = loader.load_dispatch_history(days=90)
        
        # 2. 모델 학습
        detector = AnomalyDetector(contamination=0.1)
        stats = detector.train(dispatch_df, feature_type='dispatch')
        
        # 3. 이상 탐지
        results = detector.detect(dispatch_df, feature_type='dispatch')
        
        # 이상치만 출력
        anomalies = results[results['is_anomaly'] == 1]
        print(f"\n⚠️ 탐지된 이상 배차: {len(anomalies)} 건")
        print(anomalies[['dispatch_date', 'vehicle_number', 'total_distance_km', 
                        'total_duration_minutes', 'anomaly_score']].head())
        
        # 4. 이상치 특징 분석
        feature_analysis = detector.get_anomaly_features(results, feature_type='dispatch')
        
        # 5. 모델 저장
        model_path = '/home/user/webapp/phase5/models/anomaly_detector_model.pkl'
        detector.save_model(model_path)
        
    finally:
        loader.close()
