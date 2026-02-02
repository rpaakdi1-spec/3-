"""
A/B Test Service for ML Dispatch

점진적 롤아웃을 위한 트래픽 분배 및 실험 관리
"""

import hashlib
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger

from sqlalchemy.orm import Session
from redis import Redis

from app.models.user import User


class ABTestService:
    """A/B 테스트 트래픽 분배 서비스"""
    
    # Experiment Configuration
    EXPERIMENT_KEY = "ml_dispatch:experiment:v1"
    ROLLOUT_KEY = "ml_dispatch:rollout_percentage"
    STATS_KEY = "ml_dispatch:stats"
    
    def __init__(self, redis: Redis):
        self.redis = redis
    
    def assign_user_to_group(self, user_id: int) -> str:
        """
        사용자를 실험 그룹에 할당
        
        일관된 해싱을 사용하여 같은 사용자는 항상 같은 그룹에 할당됩니다.
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            'control' (기존 시스템) or 'treatment' (ML 시스템)
        """
        # 기존 할당 확인
        cache_key = f"user:{user_id}"
        existing_group = self.redis.hget(self.EXPERIMENT_KEY, cache_key)
        
        if existing_group:
            group = existing_group.decode('utf-8')
            logger.debug(f"User {user_id} cached group: {group}")
            return group
        
        # 새 할당
        rollout_percentage = self._get_rollout_percentage()
        
        # 일관된 해싱: user_id를 기반으로 0-99 범위 생성
        hash_input = f"ml_dispatch_v1_{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16) % 100
        
        # 롤아웃 비율에 따라 그룹 결정
        if hash_value < rollout_percentage:
            group = "treatment"  # ML Dispatch
        else:
            group = "control"    # Legacy Dispatch
        
        # Redis에 저장 (TTL: 30일)
        self.redis.hset(self.EXPERIMENT_KEY, cache_key, group)
        self.redis.expire(self.EXPERIMENT_KEY, 30 * 24 * 3600)
        
        # 통계 업데이트
        self._update_assignment_stats(group)
        
        logger.info(f"User {user_id} assigned to group: {group} (hash: {hash_value}, rollout: {rollout_percentage}%)")
        
        return group
    
    def get_user_group(self, user_id: int) -> Optional[str]:
        """사용자의 현재 그룹 조회 (할당하지 않음)"""
        cache_key = f"user:{user_id}"
        group = self.redis.hget(self.EXPERIMENT_KEY, cache_key)
        
        if group:
            return group.decode('utf-8')
        
        return None
    
    def _get_rollout_percentage(self) -> int:
        """
        현재 롤아웃 비율 가져오기
        
        Returns:
            0-100 사이의 정수 (기본값: 10)
        """
        percentage = self.redis.get(self.ROLLOUT_KEY)
        
        if percentage:
            return int(percentage)
        
        # 기본값: 10%
        return 10
    
    def set_rollout_percentage(self, percentage: int) -> None:
        """
        롤아웃 비율 설정
        
        Args:
            percentage: 0-100 사이의 정수
        
        Raises:
            ValueError: percentage가 범위를 벗어난 경우
        """
        if not 0 <= percentage <= 100:
            raise ValueError("Percentage must be between 0 and 100")
        
        old_percentage = self._get_rollout_percentage()
        
        self.redis.set(self.ROLLOUT_KEY, percentage)
        
        # 변경 이력 기록
        self._log_rollout_change(old_percentage, percentage)
        
        logger.info(f"Rollout percentage changed: {old_percentage}% → {percentage}%")
    
    def get_experiment_stats(self) -> Dict[str, Any]:
        """
        실험 통계 조회
        
        Returns:
            {
                "total_users": int,
                "control_count": int,
                "treatment_count": int,
                "treatment_percentage": float,
                "rollout_percentage": int,
                "last_updated": str
            }
        """
        # Redis에서 모든 사용자 그룹 조회
        all_assignments = self.redis.hgetall(self.EXPERIMENT_KEY)
        
        control_count = 0
        treatment_count = 0
        
        for key, value in all_assignments.items():
            if key.decode('utf-8').startswith('user:'):
                group = value.decode('utf-8')
                if group == 'control':
                    control_count += 1
                elif group == 'treatment':
                    treatment_count += 1
        
        total_users = control_count + treatment_count
        
        # 실제 treatment 비율
        actual_treatment_pct = (
            (treatment_count / total_users * 100)
            if total_users > 0 else 0.0
        )
        
        # 통계 캐시에서 추가 정보
        stats_cache = self.redis.hgetall(self.STATS_KEY)
        
        return {
            "total_users": total_users,
            "control_count": control_count,
            "treatment_count": treatment_count,
            "actual_treatment_percentage": round(actual_treatment_pct, 2),
            "target_rollout_percentage": self._get_rollout_percentage(),
            "last_updated": datetime.now().isoformat(),
            "stats_cache": {
                k.decode('utf-8'): int(v.decode('utf-8'))
                for k, v in stats_cache.items()
            } if stats_cache else {}
        }
    
    def force_assign_user(
        self,
        user_id: int,
        group: str
    ) -> None:
        """
        사용자를 특정 그룹에 강제 할당 (테스트용)
        
        Args:
            user_id: 사용자 ID
            group: 'control' or 'treatment'
        
        Raises:
            ValueError: group이 유효하지 않은 경우
        """
        if group not in ['control', 'treatment']:
            raise ValueError("Group must be 'control' or 'treatment'")
        
        cache_key = f"user:{user_id}"
        old_group = self.redis.hget(self.EXPERIMENT_KEY, cache_key)
        
        self.redis.hset(self.EXPERIMENT_KEY, cache_key, group)
        
        logger.warning(
            f"User {user_id} force assigned: "
            f"{old_group.decode('utf-8') if old_group else 'None'} → {group}"
        )
    
    def reset_experiment(self) -> None:
        """
        실험 초기화 (모든 할당 제거)
        
        ⚠️ 주의: 모든 사용자 할당이 삭제됩니다!
        """
        self.redis.delete(self.EXPERIMENT_KEY)
        self.redis.delete(self.STATS_KEY)
        
        logger.warning("Experiment reset: all user assignments cleared")
    
    def _update_assignment_stats(self, group: str) -> None:
        """할당 통계 업데이트"""
        self.redis.hincrby(self.STATS_KEY, f"{group}_total", 1)
        self.redis.hincrby(self.STATS_KEY, "total_assignments", 1)
    
    def _log_rollout_change(
        self,
        old_percentage: int,
        new_percentage: int
    ) -> None:
        """롤아웃 변경 이력 기록"""
        history_key = f"{self.ROLLOUT_KEY}:history"
        
        change_log = {
            "timestamp": datetime.now().isoformat(),
            "old_percentage": old_percentage,
            "new_percentage": new_percentage
        }
        
        # List에 추가 (최근 100개 유지)
        self.redis.lpush(history_key, str(change_log))
        self.redis.ltrim(history_key, 0, 99)
    
    def get_rollout_history(self, limit: int = 20) -> list:
        """롤아웃 변경 이력 조회"""
        history_key = f"{self.ROLLOUT_KEY}:history"
        
        history = self.redis.lrange(history_key, 0, limit - 1)
        
        return [
            eval(h.decode('utf-8'))  # 주의: 프로덕션에서는 json 사용
            for h in history
        ]


class ABTestMetricsService:
    """A/B 테스트 메트릭 수집 및 분석"""
    
    def __init__(self, db: Session, redis: Redis):
        self.db = db
        self.redis = redis
    
    def track_dispatch_outcome(
        self,
        user_id: int,
        group: str,
        success: bool,
        score: Optional[float] = None,
        response_time: Optional[float] = None
    ) -> None:
        """
        배차 결과 추적
        
        Args:
            user_id: 사용자 ID
            group: 'control' or 'treatment'
            success: 성공 여부
            score: ML 점수 (treatment만)
            response_time: 응답 시간 (초)
        """
        metrics_key = f"ml_dispatch:metrics:{group}"
        
        # 카운터 증가
        self.redis.hincrby(metrics_key, "total", 1)
        
        if success:
            self.redis.hincrby(metrics_key, "success", 1)
        else:
            self.redis.hincrby(metrics_key, "failure", 1)
        
        # 점수 기록 (treatment만)
        if group == "treatment" and score is not None:
            score_key = f"{metrics_key}:scores"
            self.redis.lpush(score_key, score)
            self.redis.ltrim(score_key, 0, 999)  # 최근 1000개 유지
        
        # 응답 시간 기록
        if response_time is not None:
            time_key = f"{metrics_key}:response_times"
            self.redis.lpush(time_key, response_time)
            self.redis.ltrim(time_key, 0, 999)
        
        logger.debug(
            f"Tracked dispatch: group={group}, success={success}, "
            f"score={score}, time={response_time}"
        )
    
    def get_group_metrics(self, group: str) -> Dict[str, Any]:
        """그룹별 메트릭 조회"""
        metrics_key = f"ml_dispatch:metrics:{group}"
        
        # 카운터 조회
        total = int(self.redis.hget(metrics_key, "total") or 0)
        success = int(self.redis.hget(metrics_key, "success") or 0)
        failure = int(self.redis.hget(metrics_key, "failure") or 0)
        
        # 성공률
        success_rate = (success / total) if total > 0 else 0.0
        
        # 평균 점수 (treatment만)
        avg_score = None
        if group == "treatment":
            score_key = f"{metrics_key}:scores"
            scores = self.redis.lrange(score_key, 0, -1)
            if scores:
                scores_float = [float(s) for s in scores]
                avg_score = sum(scores_float) / len(scores_float)
        
        # 평균 응답 시간
        time_key = f"{metrics_key}:response_times"
        times = self.redis.lrange(time_key, 0, -1)
        avg_response_time = None
        if times:
            times_float = [float(t) for t in times]
            avg_response_time = sum(times_float) / len(times_float)
        
        return {
            "group": group,
            "total_dispatches": total,
            "success_count": success,
            "failure_count": failure,
            "success_rate": round(success_rate, 3),
            "avg_score": round(avg_score, 3) if avg_score else None,
            "avg_response_time": round(avg_response_time, 3) if avg_response_time else None
        }
    
    def compare_groups(self) -> Dict[str, Any]:
        """두 그룹 비교 분석"""
        control_metrics = self.get_group_metrics("control")
        treatment_metrics = self.get_group_metrics("treatment")
        
        # 개선율 계산
        success_rate_diff = (
            treatment_metrics["success_rate"] - control_metrics["success_rate"]
        )
        
        response_time_diff = None
        if (control_metrics["avg_response_time"] and
            treatment_metrics["avg_response_time"]):
            response_time_diff = (
                treatment_metrics["avg_response_time"] -
                control_metrics["avg_response_time"]
            )
        
        return {
            "control": control_metrics,
            "treatment": treatment_metrics,
            "improvements": {
                "success_rate": round(success_rate_diff, 3),
                "success_rate_percentage": round(success_rate_diff * 100, 2),
                "response_time": round(response_time_diff, 3) if response_time_diff else None
            },
            "winner": self._determine_winner(control_metrics, treatment_metrics)
        }
    
    def _determine_winner(
        self,
        control: Dict,
        treatment: Dict
    ) -> str:
        """승자 결정 (간단한 규칙 기반)"""
        # 성공률 기준
        if treatment["success_rate"] > control["success_rate"] + 0.02:  # 2% 이상 개선
            return "treatment"
        elif control["success_rate"] > treatment["success_rate"] + 0.02:
            return "control"
        else:
            return "no_significant_difference"
