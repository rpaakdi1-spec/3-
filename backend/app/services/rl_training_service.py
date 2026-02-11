"""
Phase 15: Reinforcement Learning Training Service
PPO (Proximal Policy Optimization) Agent for Dispatch
"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import numpy as np
import logging
import json
from sqlalchemy.orm import Session

from app.models.ml_training import (
    MLExperiment,
    ModelVersion,
    DispatchTrainingData
)

logger = logging.getLogger(__name__)


class RLTrainingService:
    """강화학습 학습 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.state_dim = 20  # State feature 차원
        self.action_dim = 50  # 최대 차량 수
    
    async def create_experiment(
        self,
        experiment_name: str,
        hyperparameters: Dict[str, Any],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        새로운 학습 실험 생성
        """
        try:
            experiment = MLExperiment(
                experiment_name=experiment_name,
                experiment_type="RL_PPO",
                description=description,
                hyperparameters=hyperparameters,
                training_config={
                    "state_dim": self.state_dim,
                    "action_dim": self.action_dim,
                    "algorithm": "PPO"
                },
                status="initialized"
            )
            
            self.db.add(experiment)
            self.db.commit()
            self.db.refresh(experiment)
            
            logger.info(f"Created experiment: {experiment.id} - {experiment_name}")
            
            return {
                "experiment_id": experiment.id,
                "experiment_name": experiment_name,
                "status": "initialized",
                "hyperparameters": hyperparameters
            }
            
        except Exception as e:
            logger.error(f"Error creating experiment: {str(e)}")
            self.db.rollback()
            raise
    
    async def start_training(
        self,
        experiment_id: int,
        epochs: int = 100,
        batch_size: int = 32
    ) -> Dict[str, Any]:
        """
        학습 시작 (시뮬레이션)
        실제 환경에서는 Ray RLlib, Stable-Baselines3 등을 사용
        """
        try:
            experiment = self.db.query(MLExperiment).filter(
                MLExperiment.id == experiment_id
            ).first()
            
            if not experiment:
                raise ValueError(f"Experiment not found: {experiment_id}")
            
            # 상태 업데이트
            experiment.status = "running"
            experiment.started_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Starting training for experiment {experiment_id}")
            
            # 학습 데이터 로드
            training_data = self.db.query(DispatchTrainingData).filter(
                DispatchTrainingData.done == True
            ).limit(1000).all()
            
            if len(training_data) < 100:
                raise ValueError(f"Insufficient training data: {len(training_data)} samples")
            
            # 시뮬레이션된 학습 (실제로는 PPO 알고리즘 실행)
            metrics = await self._simulate_training(
                training_data=training_data,
                epochs=epochs,
                batch_size=batch_size,
                hyperparameters=experiment.hyperparameters
            )
            
            # 실험 완료
            experiment.status = "completed"
            experiment.completed_at = datetime.utcnow()
            experiment.duration_seconds = (
                experiment.completed_at - experiment.started_at
            ).total_seconds()
            experiment.metrics = metrics
            experiment.best_reward = metrics.get("best_reward")
            experiment.best_epoch = metrics.get("best_epoch")
            
            self.db.commit()
            
            logger.info(f"Training completed for experiment {experiment_id}")
            
            return {
                "experiment_id": experiment_id,
                "status": "completed",
                "metrics": metrics,
                "duration_seconds": experiment.duration_seconds
            }
            
        except Exception as e:
            logger.error(f"Error in training: {str(e)}")
            if experiment:
                experiment.status = "failed"
                self.db.commit()
            raise
    
    async def _simulate_training(
        self,
        training_data: List[DispatchTrainingData],
        epochs: int,
        batch_size: int,
        hyperparameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        학습 시뮬레이션
        실제 환경에서는 PPO 알고리즘 실행
        """
        # 시뮬레이션된 메트릭
        learning_rate = hyperparameters.get("learning_rate", 0.0003)
        gamma = hyperparameters.get("gamma", 0.99)
        
        # 초기 성능
        initial_reward = np.mean([d.reward for d in training_data if d.reward])
        
        # 시뮬레이션: 에포크마다 개선
        epoch_rewards = []
        best_reward = initial_reward
        best_epoch = 0
        
        for epoch in range(epochs):
            # 시뮬레이션된 개선 (실제로는 모델 학습)
            improvement = epoch * 0.01  # 에포크당 1% 개선
            current_reward = initial_reward * (1 + improvement)
            
            if current_reward > best_reward:
                best_reward = current_reward
                best_epoch = epoch
            
            epoch_rewards.append(current_reward)
        
        metrics = {
            "epochs": epochs,
            "batch_size": batch_size,
            "training_samples": len(training_data),
            "initial_reward": float(initial_reward),
            "final_reward": float(epoch_rewards[-1]),
            "best_reward": float(best_reward),
            "best_epoch": best_epoch,
            "improvement_percent": float((best_reward - initial_reward) / abs(initial_reward) * 100),
            "epoch_rewards": [float(r) for r in epoch_rewards[-10:]],  # 마지막 10개
            "hyperparameters": hyperparameters
        }
        
        return metrics
    
    async def create_model_version(
        self,
        experiment_id: int,
        version: str,
        model_name: str = "PPO_Dispatch"
    ) -> Dict[str, Any]:
        """
        모델 버전 생성
        """
        try:
            experiment = self.db.query(MLExperiment).filter(
                MLExperiment.id == experiment_id
            ).first()
            
            if not experiment:
                raise ValueError(f"Experiment not found: {experiment_id}")
            
            # 모델 버전 생성
            model_version = ModelVersion(
                version=version,
                model_name=model_name,
                model_type="PPO",
                experiment_id=experiment_id,
                model_path=f"/models/{model_name}_{version}.pkl",
                performance_metrics=experiment.metrics or {},
                status="validated",
                is_active=False,
                training_episodes=experiment.metrics.get("epochs", 0) if experiment.metrics else 0
            )
            
            self.db.add(model_version)
            self.db.commit()
            self.db.refresh(model_version)
            
            logger.info(f"Created model version: {version}")
            
            return {
                "model_id": model_version.id,
                "version": version,
                "model_name": model_name,
                "status": "validated",
                "performance_metrics": model_version.performance_metrics
            }
            
        except Exception as e:
            logger.error(f"Error creating model version: {str(e)}")
            self.db.rollback()
            raise
    
    async def deploy_model(
        self,
        model_id: int,
        ab_test_traffic: float = 0.1
    ) -> Dict[str, Any]:
        """
        모델 배포 (A/B 테스트)
        """
        try:
            model = self.db.query(ModelVersion).filter(
                ModelVersion.id == model_id
            ).first()
            
            if not model:
                raise ValueError(f"Model not found: {model_id}")
            
            # 기존 활성 모델 비활성화
            self.db.query(ModelVersion).filter(
                ModelVersion.is_active == True
            ).update({"is_active": False})
            
            # 새 모델 활성화
            model.is_active = True
            model.status = "deployed"
            model.deployed_at = datetime.utcnow()
            model.ab_test_group = "B"
            model.ab_test_traffic_percent = ab_test_traffic
            
            self.db.commit()
            
            logger.info(f"Deployed model {model_id} with {ab_test_traffic*100}% traffic")
            
            return {
                "model_id": model_id,
                "version": model.version,
                "status": "deployed",
                "ab_test_traffic": ab_test_traffic,
                "deployed_at": model.deployed_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error deploying model: {str(e)}")
            self.db.rollback()
            raise
    
    async def get_model_prediction(
        self,
        state_features: Dict[str, Any],
        model_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        모델 예측 (추론)
        """
        try:
            # 활성 모델 조회
            query = self.db.query(ModelVersion).filter(
                ModelVersion.is_active == True
            )
            
            if model_version:
                query = query.filter(ModelVersion.version == model_version)
            
            model = query.first()
            
            if not model:
                # 모델이 없으면 랜덤 배차 (기본 규칙)
                return {
                    "model_version": "baseline",
                    "recommended_vehicle_id": None,
                    "confidence": 0.0,
                    "method": "random"
                }
            
            # 시뮬레이션된 예측 (실제로는 모델 로드 및 추론)
            prediction = await self._simulate_prediction(state_features, model)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error in model prediction: {str(e)}")
            return {
                "model_version": "error",
                "recommended_vehicle_id": None,
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def _simulate_prediction(
        self,
        state_features: Dict[str, Any],
        model: ModelVersion
    ) -> Dict[str, Any]:
        """
        예측 시뮬레이션
        실제로는 학습된 PPO 모델로 추론
        """
        # 시뮬레이션: 차량 특성 기반 점수 계산
        vehicle_info = state_features.get("vehicle", {})
        order_info = state_features.get("order", {})
        
        # 간단한 휴리스틱 (실제로는 신경망 예측)
        vehicle_id = vehicle_info.get("vehicle_id")
        
        # 시뮬레이션된 신뢰도
        confidence = 0.85 + (np.random.random() * 0.15)  # 0.85 ~ 1.0
        
        return {
            "model_version": model.version,
            "recommended_vehicle_id": vehicle_id,
            "confidence": float(confidence),
            "method": "rl_model",
            "model_type": model.model_type,
            "alternative_vehicles": []  # Top-k 예측
        }
    
    async def get_training_progress(
        self,
        experiment_id: int
    ) -> Dict[str, Any]:
        """
        학습 진행 상황 조회
        """
        experiment = self.db.query(MLExperiment).filter(
            MLExperiment.id == experiment_id
        ).first()
        
        if not experiment:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        progress = {
            "experiment_id": experiment_id,
            "experiment_name": experiment.experiment_name,
            "status": experiment.status,
            "started_at": experiment.started_at.isoformat() if experiment.started_at else None,
            "duration_seconds": experiment.duration_seconds,
            "metrics": experiment.metrics,
            "best_reward": experiment.best_reward,
            "best_epoch": experiment.best_epoch
        }
        
        return progress
