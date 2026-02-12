"""
Phase 15: Data Collection Service
실시간 배차 데이터 수집 및 Feature Engineering
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import json
import logging

from app.models.ml_training import (
    DispatchTrainingData,
    DispatchFeature,
    RLRewardHistory
)
from app.models.dispatch import Dispatch
from app.models.vehicle import Vehicle
from app.models.order import Order

logger = logging.getLogger(__name__)


class DispatchDataCollector:
    """배차 데이터 수집 및 Feature 추출"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def collect_dispatch_data(
        self,
        dispatch_id: int,
        vehicle_id: int,
        order_id: int,
        episode_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        배차 발생 시 데이터 수집
        """
        try:
            # 배차 정보 조회
            dispatch = self.db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
            vehicle = self.db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
            order = self.db.query(Order).filter(Order.id == order_id).first()
            
            if not all([dispatch, vehicle, order]):
                logger.error(f"Missing data: dispatch={dispatch}, vehicle={vehicle}, order={order}")
                return {}
            
            # State Features 추출
            state_features = await self._extract_state_features(vehicle, order)
            
            # Action
            action_taken = vehicle_id
            
            # Reward 계산 (나중에 업데이트)
            reward = 0.0  # 초기값, 배차 완료 후 계산
            
            # Episode ID 생성
            if not episode_id:
                episode_id = f"episode_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{dispatch_id}"
            
            # 학습 데이터 저장
            training_data = DispatchTrainingData(
                episode_id=episode_id,
                step=0,
                state_features=state_features,
                action_taken=action_taken,
                action_vehicle_id=vehicle_id,
                reward=reward,
                immediate_reward=0.0,
                actual_dispatch_id=dispatch_id,
                done=False
            )
            
            self.db.add(training_data)
            self.db.commit()
            self.db.refresh(training_data)
            
            logger.info(f"Collected training data: {training_data.id}, episode: {episode_id}")
            
            return {
                "training_data_id": training_data.id,
                "episode_id": episode_id,
                "state_features": state_features,
                "action": action_taken
            }
            
        except Exception as e:
            logger.error(f"Error collecting dispatch data: {str(e)}")
            self.db.rollback()
            return {}
    
    async def _extract_state_features(
        self,
        vehicle: Vehicle,
        order: Order
    ) -> Dict[str, Any]:
        """
        상태 특성 추출
        """
        now = datetime.utcnow()
        
        # 차량 특성
        vehicle_features = {
            "vehicle_id": vehicle.id,
            "vehicle_status": vehicle.status,
            "vehicle_type": vehicle.vehicle_type,
            "vehicle_capacity": vehicle.max_weight,
            "vehicle_temperature_type": vehicle.temperature_type,
            "vehicle_location": {
                "lat": getattr(vehicle, "latitude", 0.0),
                "lon": getattr(vehicle, "longitude", 0.0)
            }
        }
        
        # 주문 특성
        order_features = {
            "order_id": order.id,
            "pickup_location": order.pickup_address,
            "delivery_location": order.delivery_address,
            "order_priority": getattr(order, "priority", 0),
            "order_weight": order.total_weight,
            "temperature_requirement": order.temperature_requirement,
            "delivery_time": order.requested_delivery_time.isoformat() if order.requested_delivery_time else None
        }
        
        # 시간 특성
        time_features = {
            "hour": now.hour,
            "day_of_week": now.weekday(),
            "is_peak_hour": now.hour in [8, 9, 10, 17, 18, 19],
            "is_weekend": now.weekday() >= 5,
            "timestamp": now.isoformat()
        }
        
        # 환경 특성
        environment_features = await self._get_environment_features()
        
        # 통합 특성
        state = {
            "vehicle": vehicle_features,
            "order": order_features,
            "time": time_features,
            "environment": environment_features
        }
        
        return state
    
    async def _get_environment_features(self) -> Dict[str, Any]:
        """
        환경 특성 조회
        """
        # 현재 활성 차량 수
        active_vehicles = self.db.query(func.count(Vehicle.id)).filter(
            Vehicle.status == "AVAILABLE"
        ).scalar()
        
        # 대기 중인 주문 수
        pending_orders = self.db.query(func.count(Order.id)).filter(
            Order.status == "PENDING"
        ).scalar()
        
        # 최근 1시간 평균 배차 시간
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        avg_dispatch_time = self.db.query(
            func.avg(Dispatch.completion_time)
        ).filter(
            Dispatch.created_at >= one_hour_ago,
            Dispatch.status == "COMPLETED"
        ).scalar()
        
        return {
            "active_vehicles": active_vehicles or 0,
            "pending_orders": pending_orders or 0,
            "avg_dispatch_time_last_hour": float(avg_dispatch_time) if avg_dispatch_time else None,
            "weather": None,  # Phase 11-A 통합 후 사용
            "traffic": None   # Phase 11-B 통합 후 사용
        }
    
    async def update_reward(
        self,
        training_data_id: int,
        completion_time: float,
        distance: float,
        success: bool
    ) -> Dict[str, Any]:
        """
        배차 완료 후 보상 계산 및 업데이트
        """
        try:
            training_data = self.db.query(DispatchTrainingData).filter(
                DispatchTrainingData.id == training_data_id
            ).first()
            
            if not training_data:
                logger.error(f"Training data not found: {training_data_id}")
                return {}
            
            # 보상 계산
            reward_components = self._calculate_reward(
                completion_time=completion_time,
                distance=distance,
                success=success
            )
            
            # 업데이트
            training_data.reward = reward_components["total_reward"]
            training_data.immediate_reward = reward_components["total_reward"]
            training_data.actual_completion_time = completion_time
            training_data.actual_distance = distance
            training_data.actual_success = success
            training_data.done = True
            
            self.db.commit()
            
            # Reward History 저장
            reward_history = RLRewardHistory(
                dispatch_id=training_data.actual_dispatch_id,
                vehicle_id=training_data.action_vehicle_id,
                order_id=training_data.state_features.get("order", {}).get("order_id"),
                time_reward=reward_components["time_reward"],
                success_reward=reward_components["success_reward"],
                efficiency_reward=reward_components["efficiency_reward"],
                customer_satisfaction_reward=reward_components.get("satisfaction_reward", 0.0),
                total_reward=reward_components["total_reward"],
                normalized_reward=reward_components["normalized_reward"],
                state_features=training_data.state_features,
                action_taken=training_data.action_taken,
                actual_completion_time=completion_time
            )
            
            self.db.add(reward_history)
            self.db.commit()
            
            logger.info(f"Updated reward for training_data {training_data_id}: {reward_components['total_reward']}")
            
            return reward_components
            
        except Exception as e:
            logger.error(f"Error updating reward: {str(e)}")
            self.db.rollback()
            return {}
    
    def _calculate_reward(
        self,
        completion_time: float,
        distance: float,
        success: bool
    ) -> Dict[str, float]:
        """
        보상 계산 로직
        
        보상 구성:
        1. 시간 보상: 빠를수록 높음 (-1 ~ 1)
        2. 성공 보상: 성공 시 +1, 실패 시 -1
        3. 효율성 보상: 거리 대비 시간 효율
        """
        # 1. 시간 보상 (30분 기준)
        target_time = 30.0  # 목표: 30분
        if completion_time <= target_time:
            time_reward = 1.0
        else:
            # 30분 초과 시 감소 (최대 60분까지)
            time_reward = max(0.0, 1.0 - (completion_time - target_time) / target_time)
        
        # 2. 성공 보상
        success_reward = 1.0 if success else -1.0
        
        # 3. 효율성 보상 (거리 대비 시간)
        if distance > 0:
            # 1km당 2분 기준
            expected_time = distance * 2.0
            if completion_time <= expected_time:
                efficiency_reward = 1.0
            else:
                efficiency_reward = max(0.0, 1.0 - (completion_time - expected_time) / expected_time)
        else:
            efficiency_reward = 0.5
        
        # 총 보상 (가중 평균)
        total_reward = (
            time_reward * 0.4 +
            success_reward * 0.4 +
            efficiency_reward * 0.2
        )
        
        # 정규화 (-1 ~ 1)
        normalized_reward = max(-1.0, min(1.0, total_reward))
        
        return {
            "time_reward": time_reward,
            "success_reward": success_reward,
            "efficiency_reward": efficiency_reward,
            "satisfaction_reward": 0.0,  # 향후 구현
            "total_reward": total_reward,
            "normalized_reward": normalized_reward
        }
    
    async def get_training_dataset(
        self,
        limit: int = 1000,
        min_reward: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        학습 데이터셋 조회
        """
        query = self.db.query(DispatchTrainingData).filter(
            DispatchTrainingData.done == True
        )
        
        if min_reward is not None:
            query = query.filter(DispatchTrainingData.reward >= min_reward)
        
        training_data = query.order_by(
            DispatchTrainingData.collected_at.desc()
        ).limit(limit).all()
        
        dataset = []
        for data in training_data:
            dataset.append({
                "id": data.id,
                "episode_id": data.episode_id,
                "state": data.state_features,
                "action": data.action_taken,
                "reward": data.reward,
                "next_state": data.next_state_features,
                "done": data.done,
                "timestamp": data.collected_at.isoformat()
            })
        
        return dataset
