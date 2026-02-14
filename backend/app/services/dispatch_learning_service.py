"""
배차 학습 데이터 수집 서비스
실제 배차 결과를 수집하여 ML Agent 가중치 자동 튜닝
"""
import json
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.dispatch import Dispatch, DispatchStatus
from app.models.order import Order
from app.models.vehicle import Vehicle
from loguru import logger


class DispatchLearningService:
    """
    배차 학습 서비스
    
    목적:
    1. 실제 배차 결과 수집 (성공/실패)
    2. Agent 점수 vs 실제 성과 비교
    3. 가중치 자동 튜닝 (Reinforcement Learning)
    4. A/B 테스트 지원
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def record_dispatch_outcome(
        self,
        dispatch_id: int,
        outcome_type: str,  # "success", "partial", "failure"
        metrics: Dict
    ):
        """
        배차 결과 기록
        
        Args:
            dispatch_id: 배차 ID
            outcome_type: 성공/부분성공/실패
            metrics:
                - actual_distance_km: 실제 주행 거리
                - actual_duration_min: 실제 소요 시간
                - fuel_cost: 연료비
                - time_deviation_min: 시간 오차
                - client_satisfaction: 고객 만족도 (1-5)
                - vehicle_utilization: 차량 적재율
        """
        dispatch = self.db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
        if not dispatch:
            logger.warning(f"Dispatch {dispatch_id} not found")
            return
        
        # 학습 데이터 저장
        learning_data = {
            "dispatch_id": dispatch_id,
            "timestamp": datetime.now().isoformat(),
            "outcome_type": outcome_type,
            "metrics": metrics,
            "ai_metadata": dispatch.ai_metadata or {}
        }
        
        # ai_metadata에 학습 데이터 추가
        if not dispatch.ai_metadata:
            dispatch.ai_metadata = {}
        
        dispatch.ai_metadata["outcome"] = learning_data
        
        # 성능 점수 계산
        performance_score = self._calculate_performance_score(metrics)
        dispatch.ai_metadata["performance_score"] = performance_score
        
        self.db.commit()
        
        logger.info(f"Dispatch {dispatch_id} outcome recorded: {outcome_type}, score: {performance_score:.2f}")
    
    def _calculate_performance_score(self, metrics: Dict) -> float:
        """
        배차 성과 점수 계산 (0~100)
        
        Returns:
            종합 성과 점수
        """
        score = 100.0
        
        # 1. 거리 효율 (예상 대비 실제)
        if "actual_distance_km" in metrics and "estimated_distance_km" in metrics:
            distance_ratio = metrics["actual_distance_km"] / metrics["estimated_distance_km"]
            if distance_ratio > 1.2:  # 20% 초과
                score -= 15
            elif distance_ratio > 1.1:  # 10% 초과
                score -= 5
        
        # 2. 시간 준수 (오차)
        if "time_deviation_min" in metrics:
            deviation = abs(metrics["time_deviation_min"])
            if deviation > 30:
                score -= 20
            elif deviation > 15:
                score -= 10
        
        # 3. 고객 만족도
        if "client_satisfaction" in metrics:
            satisfaction = metrics["client_satisfaction"]
            score += (satisfaction - 3) * 10  # 3점 기준, ±10점
        
        # 4. 차량 적재율
        if "vehicle_utilization" in metrics:
            utilization = metrics["vehicle_utilization"]
            if utilization > 0.9:
                score += 10  # 90% 이상 적재
            elif utilization < 0.5:
                score -= 10  # 50% 미만 비효율
        
        return max(0.0, min(100.0, score))
    
    def analyze_agent_performance(self, days: int = 30) -> Dict:
        """
        Agent 성능 분석 (최근 N일)
        
        Returns:
            Agent별 정확도 및 개선 제안
        """
        from datetime import timedelta
        from collections import defaultdict
        
        start_date = datetime.now() - timedelta(days=days)
        
        # 학습 데이터가 있는 배차 조회
        dispatches = self.db.query(Dispatch).filter(
            Dispatch.created_at >= start_date,
            Dispatch.ai_metadata.isnot(None)
        ).all()
        
        # Agent별 통계
        agent_stats = defaultdict(lambda: {"predictions": [], "actuals": []})
        
        for dispatch in dispatches:
            if not dispatch.ai_metadata or "outcome" not in dispatch.ai_metadata:
                continue
            
            # Agent 예측 점수
            if "agent_scores" in dispatch.ai_metadata:
                scores = dispatch.ai_metadata["agent_scores"]
                
                # 실제 성과
                performance = dispatch.ai_metadata.get("performance_score", 0)
                
                for agent_name, agent_score in scores.items():
                    agent_stats[agent_name]["predictions"].append(agent_score)
                    agent_stats[agent_name]["actuals"].append(performance)
        
        # 상관계수 계산
        import numpy as np
        
        results = {}
        for agent_name, data in agent_stats.items():
            if len(data["predictions"]) > 10:  # 최소 10개 샘플
                correlation = np.corrcoef(
                    data["predictions"],
                    data["actuals"]
                )[0, 1]
                
                results[agent_name] = {
                    "correlation": float(correlation),
                    "sample_count": len(data["predictions"]),
                    "recommendation": self._get_recommendation(correlation)
                }
        
        return results
    
    def _get_recommendation(self, correlation: float) -> str:
        """상관계수 기반 개선 제안"""
        if correlation > 0.7:
            return "✅ 우수: Agent 예측이 실제 성과와 강한 양의 상관관계"
        elif correlation > 0.4:
            return "👍 양호: Agent 예측이 어느 정도 유효함"
        elif correlation > 0:
            return "⚠️ 약함: Agent 가중치 재조정 필요"
        else:
            return "❌ 역상관: Agent 로직 재검토 필요"
    
    def suggest_weight_adjustment(self, days: int = 30) -> Dict:
        """
        가중치 자동 조정 제안
        
        Returns:
            새로운 가중치 딕셔너리
        """
        agent_performance = self.analyze_agent_performance(days)
        
        # 현재 가중치
        current_weights = {
            'distance': 0.30,
            'rotation': 0.20,
            'time_window': 0.25,
            'preference': 0.20,
            'voltage': 0.05
        }
        
        # 상관계수 기반 조정
        new_weights = {}
        total_correlation = sum(
            data.get("correlation", 0) 
            for data in agent_performance.values()
        )
        
        if total_correlation > 0:
            for agent_name, data in agent_performance.items():
                correlation = data.get("correlation", 0)
                
                # 상관계수에 비례하여 가중치 재분배
                normalized = correlation / total_correlation
                new_weights[agent_name] = normalized
        else:
            new_weights = current_weights
        
        # 정규화 (합=1.0)
        total = sum(new_weights.values())
        if total > 0:
            new_weights = {k: v/total for k, v in new_weights.items()}
        
        return {
            "current_weights": current_weights,
            "suggested_weights": new_weights,
            "agent_performance": agent_performance
        }
