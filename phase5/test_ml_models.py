#!/usr/bin/env python3
"""
Phase 5 ML 모델 테스트 스크립트
수요 예측 및 이상 탐지 모델을 테스트합니다.
"""
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.append('/home/user/webapp/phase5')
sys.path.append('/home/user/webapp')

import logging
from datetime import datetime
import pandas as pd
import numpy as np

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_data_loader():
    """데이터 로더 테스트"""
    logger.info("\n" + "="*60)
    logger.info("🧪 Test 1: 데이터 로더")
    logger.info("="*60)
    
    try:
        from ml_advanced.utils.data_loader import DataLoader
        
        loader = DataLoader()
        
        # 주문 이력 로드 테스트
        logger.info("📦 주문 이력 로드 테스트...")
        orders_df = loader.load_order_history(days=90)
        logger.info(f"✅ 주문 이력 로드 성공: {len(orders_df)} 건")
        
        # 일별 수요 집계 테스트
        logger.info("\n📊 일별 수요 집계 테스트...")
        daily_df = loader.aggregate_daily_demand(orders_df)
        logger.info(f"✅ 일별 수요 집계 성공: {len(daily_df)} 일")
        logger.info(f"  기간: {daily_df['date'].min()} ~ {daily_df['date'].max()}")
        logger.info(f"  평균 주문: {daily_df['order_count'].mean():.1f} 건/일")
        
        # 배차 이력 로드 테스트
        logger.info("\n🚚 배차 이력 로드 테스트...")
        dispatch_df = loader.load_dispatch_history(days=90)
        logger.info(f"✅ 배차 이력 로드 성공: {len(dispatch_df)} 건")
        
        # 차량 데이터 로드 테스트
        logger.info("\n🚗 차량 데이터 로드 테스트...")
        vehicle_df = loader.load_vehicle_data()
        logger.info(f"✅ 차량 데이터 로드 성공: {len(vehicle_df)} 건")
        
        loader.close()
        
        logger.info("\n✅ 데이터 로더 테스트 통과!")
        return True, daily_df, dispatch_df
        
    except Exception as e:
        logger.error(f"❌ 데이터 로더 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None


def test_demand_forecaster(daily_df):
    """수요 예측 모델 테스트"""
    logger.info("\n" + "="*60)
    logger.info("🧪 Test 2: 수요 예측 모델")
    logger.info("="*60)
    
    try:
        from ml_advanced.demand_forecast.random_forest_predictor import DemandForecaster
        
        # 모델 초기화
        logger.info("🤖 모델 초기화...")
        forecaster = DemandForecaster(n_estimators=50, max_depth=8)
        
        # 모델 학습
        logger.info("\n📚 모델 학습 시작...")
        metrics = forecaster.train(daily_df, target_column='order_count', test_size=0.2)
        
        # 성능 평가
        logger.info("\n📈 모델 성능 평가:")
        logger.info(f"  Test MAE: {metrics['test']['mae']:.2f} 건")
        logger.info(f"  Test RMSE: {metrics['test']['rmse']:.2f} 건")
        logger.info(f"  Test R²: {metrics['test']['r2']:.3f}")
        
        # 미래 예측
        logger.info("\n🔮 7일 수요 예측...")
        predictions = forecaster.predict(daily_df, days_ahead=7)
        logger.info("\n예측 결과:")
        print(predictions.to_string(index=False))
        
        # 모델 저장
        model_dir = '/home/user/webapp/phase5/models'
        os.makedirs(model_dir, exist_ok=True)
        model_path = f'{model_dir}/demand_forecast_model.pkl'
        
        logger.info(f"\n💾 모델 저장 중: {model_path}")
        forecaster.save_model(model_path)
        
        # 모델 로드 테스트
        logger.info("\n📂 모델 로드 테스트...")
        new_forecaster = DemandForecaster()
        new_forecaster.load_model(model_path)
        
        logger.info("\n✅ 수요 예측 모델 테스트 통과!")
        return True, predictions
        
    except Exception as e:
        logger.error(f"❌ 수요 예측 모델 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_anomaly_detector(dispatch_df):
    """이상 탐지 모델 테스트"""
    logger.info("\n" + "="*60)
    logger.info("🧪 Test 3: 이상 탐지 모델")
    logger.info("="*60)
    
    try:
        from ml_advanced.anomaly_detection.isolation_forest_detector import AnomalyDetector
        
        # 모델 초기화
        logger.info("🤖 모델 초기화...")
        detector = AnomalyDetector(contamination=0.1)
        
        # 모델 학습
        logger.info("\n📚 모델 학습 시작...")
        stats = detector.train(dispatch_df, feature_type='dispatch')
        
        # 이상 탐지
        logger.info("\n🔍 이상 탐지 실행...")
        results = detector.detect(dispatch_df, feature_type='dispatch')
        
        # 이상치 분석
        anomalies = results[results['is_anomaly'] == 1]
        logger.info(f"\n⚠️ 탐지된 이상 배차: {len(anomalies)} 건")
        
        if len(anomalies) > 0:
            logger.info("\n상위 5개 이상 패턴:")
            top_anomalies = anomalies.nsmallest(5, 'anomaly_score')
            print(top_anomalies[['dispatch_date', 'vehicle_number', 
                                 'total_distance_km', 'anomaly_score']].to_string())
            
            # 이상치 특징 분석
            logger.info("\n📊 이상치 특징 분석...")
            feature_analysis = detector.get_anomaly_features(results, feature_type='dispatch')
        
        # 모델 저장
        model_dir = '/home/user/webapp/phase5/models'
        os.makedirs(model_dir, exist_ok=True)
        model_path = f'{model_dir}/anomaly_detector_model.pkl'
        
        logger.info(f"\n💾 모델 저장 중: {model_path}")
        detector.save_model(model_path)
        
        # 모델 로드 테스트
        logger.info("\n📂 모델 로드 테스트...")
        new_detector = AnomalyDetector()
        new_detector.load_model(model_path)
        
        logger.info("\n✅ 이상 탐지 모델 테스트 통과!")
        return True, results
        
    except Exception as e:
        logger.error(f"❌ 이상 탐지 모델 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def generate_test_summary(results: dict):
    """테스트 결과 요약 생성"""
    logger.info("\n" + "="*60)
    logger.info("📋 테스트 결과 요약")
    logger.info("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    
    logger.info(f"\n총 테스트: {total_tests}")
    logger.info(f"통과: {passed_tests} ✅")
    logger.info(f"실패: {total_tests - passed_tests} ❌")
    logger.info(f"성공률: {passed_tests/total_tests*100:.1f}%")
    
    logger.info("\n개별 테스트 결과:")
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"  {test_name}: {status}")
    
    if passed_tests == total_tests:
        logger.info("\n🎉 모든 테스트 통과! Phase 5 ML 구현 완료!")
    else:
        logger.info(f"\n⚠️ {total_tests - passed_tests}개 테스트 실패. 수정이 필요합니다.")


def main():
    """메인 테스트 실행"""
    logger.info("="*60)
    logger.info("🚀 Phase 5 ML 모델 테스트 시작")
    logger.info("="*60)
    logger.info(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test 1: 데이터 로더
    success, daily_df, dispatch_df = test_data_loader()
    results['데이터 로더'] = success
    
    if not success:
        logger.error("\n❌ 데이터 로더 테스트 실패로 인해 후속 테스트를 건너뜁니다.")
        generate_test_summary(results)
        return
    
    # Test 2: 수요 예측 모델
    if daily_df is not None and len(daily_df) > 30:
        success, predictions = test_demand_forecaster(daily_df)
        results['수요 예측 모델'] = success
    else:
        logger.warning("\n⚠️ 충분한 주문 데이터가 없어 수요 예측 테스트를 건너뜁니다.")
        results['수요 예측 모델'] = False
    
    # Test 3: 이상 탐지 모델
    if dispatch_df is not None and len(dispatch_df) > 10:
        success, anomaly_results = test_anomaly_detector(dispatch_df)
        results['이상 탐지 모델'] = success
    else:
        logger.warning("\n⚠️ 충분한 배차 데이터가 없어 이상 탐지 테스트를 건너뜁니다.")
        results['이상 탐지 모델'] = False
    
    # 테스트 결과 요약
    generate_test_summary(results)
    
    logger.info(f"\n종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)


if __name__ == "__main__":
    main()
