"""
Auto Rollback System

Phase 3: 자동 롤백 시스템
- 실시간 메트릭 모니터링
- 성능 저하 자동 감지
- 롤백 트리거 및 실행
"""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.ab_test_service import ABTestService, ABTestMetricsService


class AutoRollbackConfig:
    """자동 롤백 설정"""
    
    # 성능 임계값
    ERROR_RATE_THRESHOLD = 0.05  # 5% 에러율
    SUCCESS_RATE_THRESHOLD = 0.90  # 90% 성공률
    AVG_SCORE_THRESHOLD = 0.60  # 평균 점수 0.60
    RESPONSE_TIME_THRESHOLD = 5.0  # 5초
    
    # 모니터링 설정
    CHECK_INTERVAL_SECONDS = 60  # 1분마다 체크
    CONSECUTIVE_FAILURES_THRESHOLD = 3  # 3회 연속 실패 시 롤백
    MIN_SAMPLE_SIZE = 10  # 최소 샘플 수


class RollbackDecision:
    """롤백 결정 결과"""
    
    def __init__(
        self,
        should_rollback: bool,
        reason: str,
        metrics: Dict[str, Any],
        severity: str = "info"
    ):
        self.should_rollback = should_rollback
        self.reason = reason
        self.metrics = metrics
        self.severity = severity  # info, warning, critical
        self.timestamp = datetime.now()


class AutoRollbackSystem:
    """자동 롤백 시스템"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.config = AutoRollbackConfig()
        self.consecutive_failures = 0
        self.last_rollback_time: Optional[datetime] = None
        
    def _get_rollback_cooldown_key(self) -> str:
        """롤백 쿨다운 키"""
        return "ml_dispatch:rollback:cooldown"
    
    def _is_in_cooldown(self) -> bool:
        """롤백 쿨다운 체크 (1시간 내 재롤백 방지)"""
        key = self._get_rollback_cooldown_key()
        return self.redis.exists(key)
    
    def _set_cooldown(self, hours: int = 1):
        """롤백 쿨다운 설정"""
        key = self._get_rollback_cooldown_key()
        self.redis.setex(key, timedelta(hours=hours), "1")
    
    async def check_metrics(self, db: Session) -> RollbackDecision:
        """
        메트릭 체크 및 롤백 결정
        
        Returns:
            RollbackDecision: 롤백 여부 및 이유
        """
        try:
            # A/B 테스트 메트릭 조회
            metrics_service = ABTestMetricsService(db, self.redis)
            comparison = metrics_service.compare_groups()
            
            treatment_metrics = comparison.get('treatment', {})
            
            # 샘플 크기 체크
            total_dispatches = treatment_metrics.get('total_dispatches', 0)
            if total_dispatches < self.config.MIN_SAMPLE_SIZE:
                return RollbackDecision(
                    should_rollback=False,
                    reason=f"샘플 크기 부족 ({total_dispatches} < {self.config.MIN_SAMPLE_SIZE})",
                    metrics=treatment_metrics,
                    severity="info"
                )
            
            # 1. 에러율 체크
            error_rate = 1.0 - treatment_metrics.get('success_rate', 1.0)
            if error_rate > self.config.ERROR_RATE_THRESHOLD:
                return RollbackDecision(
                    should_rollback=True,
                    reason=f"에러율 초과: {error_rate:.1%} > {self.config.ERROR_RATE_THRESHOLD:.1%}",
                    metrics=treatment_metrics,
                    severity="critical"
                )
            
            # 2. 성공률 체크
            success_rate = treatment_metrics.get('success_rate', 0.0)
            if success_rate < self.config.SUCCESS_RATE_THRESHOLD:
                return RollbackDecision(
                    should_rollback=True,
                    reason=f"성공률 미달: {success_rate:.1%} < {self.config.SUCCESS_RATE_THRESHOLD:.1%}",
                    metrics=treatment_metrics,
                    severity="critical"
                )
            
            # 3. ML 점수 체크
            avg_score = treatment_metrics.get('avg_score')
            if avg_score is not None and avg_score < self.config.AVG_SCORE_THRESHOLD:
                return RollbackDecision(
                    should_rollback=True,
                    reason=f"ML 점수 미달: {avg_score:.3f} < {self.config.AVG_SCORE_THRESHOLD}",
                    metrics=treatment_metrics,
                    severity="warning"
                )
            
            # 4. 응답 시간 체크
            avg_response_time = treatment_metrics.get('avg_response_time', 0.0)
            if avg_response_time > self.config.RESPONSE_TIME_THRESHOLD:
                return RollbackDecision(
                    should_rollback=True,
                    reason=f"응답 시간 초과: {avg_response_time:.2f}s > {self.config.RESPONSE_TIME_THRESHOLD}s",
                    metrics=treatment_metrics,
                    severity="warning"
                )
            
            # 모든 체크 통과
            return RollbackDecision(
                should_rollback=False,
                reason="모든 메트릭 정상",
                metrics=treatment_metrics,
                severity="info"
            )
            
        except Exception as e:
            logger.error(f"메트릭 체크 오류: {e}")
            return RollbackDecision(
                should_rollback=False,
                reason=f"메트릭 체크 실패: {e}",
                metrics={},
                severity="info"
            )
    
    async def execute_rollback(self) -> bool:
        """
        롤백 실행
        
        Returns:
            bool: 롤백 성공 여부
        """
        try:
            # 쿨다운 체크
            if self._is_in_cooldown():
                logger.warning("롤백 쿨다운 중 - 1시간 내 재롤백 불가")
                return False
            
            # 롤백: Treatment 비율을 0%로 설정
            ab_service = ABTestService(self.redis)
            old_percentage = ab_service._get_rollout_percentage()
            ab_service.set_rollout_percentage(0)
            
            # 쿨다운 설정
            self._set_cooldown(hours=1)
            
            # 로그 기록
            logger.critical(
                f"🚨 자동 롤백 실행: {old_percentage}% → 0% "
                f"(쿨다운 1시간)"
            )
            
            self.last_rollback_time = datetime.now()
            self.consecutive_failures = 0
            
            return True
            
        except Exception as e:
            logger.error(f"롤백 실행 오류: {e}")
            return False
    
    async def monitor_loop(self):
        """
        모니터링 루프 (백그라운드 태스크)
        
        1분마다 메트릭 체크하고 필요 시 자동 롤백
        """
        logger.info("🔍 자동 롤백 시스템 시작")
        
        while True:
            try:
                db = SessionLocal()
                
                # 메트릭 체크
                decision = await self.check_metrics(db)
                
                # 로그 기록
                if decision.severity == "critical":
                    logger.error(
                        f"❌ {decision.reason} | "
                        f"Metrics: {decision.metrics}"
                    )
                elif decision.severity == "warning":
                    logger.warning(
                        f"⚠️ {decision.reason} | "
                        f"Metrics: {decision.metrics}"
                    )
                else:
                    logger.info(
                        f"✅ {decision.reason} | "
                        f"Metrics: {decision.metrics}"
                    )
                
                # 롤백 결정
                if decision.should_rollback:
                    self.consecutive_failures += 1
                    logger.warning(
                        f"롤백 조건 충족 ({self.consecutive_failures}/"
                        f"{self.config.CONSECUTIVE_FAILURES_THRESHOLD})"
                    )
                    
                    # 연속 실패 임계값 체크
                    if self.consecutive_failures >= self.config.CONSECUTIVE_FAILURES_THRESHOLD:
                        logger.critical("🚨 연속 실패 임계값 초과 - 자동 롤백 실행")
                        success = await self.execute_rollback()
                        
                        if success:
                            logger.critical("✅ 자동 롤백 완료")
                        else:
                            logger.error("❌ 자동 롤백 실패")
                else:
                    # 정상 상태 복구
                    if self.consecutive_failures > 0:
                        logger.info(f"정상 상태 복구 (연속 실패 카운터 리셋)")
                    self.consecutive_failures = 0
                
                db.close()
                
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
            
            # 대기
            await asyncio.sleep(self.config.CHECK_INTERVAL_SECONDS)
    
    def get_status(self) -> Dict[str, Any]:
        """
        현재 상태 조회
        
        Returns:
            Dict: 시스템 상태
        """
        return {
            "monitoring_active": True,
            "check_interval_seconds": self.config.CHECK_INTERVAL_SECONDS,
            "consecutive_failures": self.consecutive_failures,
            "consecutive_failures_threshold": self.config.CONSECUTIVE_FAILURES_THRESHOLD,
            "in_cooldown": self._is_in_cooldown(),
            "last_rollback_time": self.last_rollback_time.isoformat() if self.last_rollback_time else None,
            "thresholds": {
                "error_rate": self.config.ERROR_RATE_THRESHOLD,
                "success_rate": self.config.SUCCESS_RATE_THRESHOLD,
                "avg_score": self.config.AVG_SCORE_THRESHOLD,
                "response_time": self.config.RESPONSE_TIME_THRESHOLD
            }
        }


# 글로벌 인스턴스 (싱글톤)
_rollback_system: Optional[AutoRollbackSystem] = None


def get_rollback_system(redis_client) -> AutoRollbackSystem:
    """자동 롤백 시스템 인스턴스 가져오기"""
    global _rollback_system
    if _rollback_system is None:
        _rollback_system = AutoRollbackSystem(redis_client)
    return _rollback_system
