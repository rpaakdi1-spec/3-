"""
A/B Test API Endpoints

ML Dispatch 점진적 롤아웃을 위한 A/B 테스트 관리 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from loguru import logger
import os

from app.api.auth import get_current_user
from app.models.user import User
from app.services.ab_test_service import ABTestService, ABTestMetricsService
from redis import Redis
from pydantic import BaseModel, Field


# Dependency for Redis connection
def get_redis():
    """Get Redis connection"""
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    
    return Redis(host=redis_host, port=redis_port, decode_responses=False)


router = APIRouter(prefix="/api/v1/ab-test")


class RolloutUpdateRequest(BaseModel):
    """롤아웃 비율 업데이트 요청"""
    percentage: int = Field(..., ge=0, le=100, description="0-100 사이의 롤아웃 비율")


class UserGroupResponse(BaseModel):
    """사용자 그룹 응답"""
    user_id: int
    group: str
    rollout_percentage: int


class StatsResponse(BaseModel):
    """A/B 테스트 통계 응답"""
    total_users: int
    control_count: int
    treatment_count: int
    actual_treatment_percentage: float
    target_rollout_percentage: int
    last_updated: str
    stats_cache: Dict[str, int]


@router.get("/stats", response_model=StatsResponse)
async def get_ab_test_stats(
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """
    A/B 테스트 통계 조회
    
    Returns:
        - total_users: 총 사용자 수
        - control_count: Control 그룹 사용자 수
        - treatment_count: Treatment 그룹 사용자 수
        - actual_treatment_percentage: 실제 Treatment 비율
        - target_rollout_percentage: 목표 롤아웃 비율
        - last_updated: 마지막 업데이트 시간
    """
    try:
        ab_service = ABTestService(redis)
        stats = ab_service.get_experiment_stats()
        
        logger.info(f"AB Test stats retrieved by user {current_user.id}: {stats}")
        
        return stats
    
    except Exception as e:
        logger.error(f"Failed to get AB test stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve AB test statistics: {str(e)}"
        )


@router.get("/rollout", response_model=Dict[str, int])
async def get_rollout_percentage(
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """
    현재 롤아웃 비율 조회
    
    Returns:
        - rollout_percentage: 0-100 사이의 롤아웃 비율
    """
    try:
        ab_service = ABTestService(redis)
        percentage = ab_service._get_rollout_percentage()
        
        return {"rollout_percentage": percentage}
    
    except Exception as e:
        logger.error(f"Failed to get rollout percentage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve rollout percentage: {str(e)}"
        )


@router.put("/rollout", response_model=Dict[str, Any])
async def update_rollout_percentage(
    request: RolloutUpdateRequest,
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """
    롤아웃 비율 업데이트
    
    Args:
        percentage: 0-100 사이의 롤아웃 비율
    
    Returns:
        - old_percentage: 이전 롤아웃 비율
        - new_percentage: 새 롤아웃 비율
        - message: 성공 메시지
    """
    try:
        ab_service = ABTestService(redis)
        
        old_percentage = ab_service._get_rollout_percentage()
        ab_service.set_rollout_percentage(request.percentage)
        
        logger.info(
            f"Rollout percentage updated by user {current_user.id}: "
            f"{old_percentage}% → {request.percentage}%"
        )
        
        return {
            "old_percentage": old_percentage,
            "new_percentage": request.percentage,
            "message": f"Rollout percentage updated from {old_percentage}% to {request.percentage}%"
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Failed to update rollout percentage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update rollout percentage: {str(e)}"
        )


@router.get("/user-group", response_model=UserGroupResponse)
async def get_user_group(
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """
    현재 사용자의 A/B 테스트 그룹 조회
    
    Returns:
        - user_id: 사용자 ID
        - group: 'control' 또는 'treatment'
        - rollout_percentage: 현재 롤아웃 비율
    """
    try:
        ab_service = ABTestService(redis)
        
        # 그룹 할당 (없으면 자동 할당)
        group = ab_service.assign_user_to_group(current_user.id)
        rollout_percentage = ab_service._get_rollout_percentage()
        
        return {
            "user_id": current_user.id,
            "group": group,
            "rollout_percentage": rollout_percentage
        }
    
    except Exception as e:
        logger.error(f"Failed to get user group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user group: {str(e)}"
        )


@router.get("/metrics/compare")
async def compare_group_metrics(
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """
    Control vs Treatment 그룹 메트릭 비교
    
    Returns:
        - control: Control 그룹 메트릭
        - treatment: Treatment 그룹 메트릭
        - improvements: 개선율
        - winner: 승자 그룹
    """
    try:
        from app.core.deps import get_db
        from sqlalchemy.orm import Session
        
        # DB 세션은 여기서 직접 생성
        db: Session = next(get_db())
        
        metrics_service = ABTestMetricsService(db, redis)
        comparison = metrics_service.compare_groups()
        
        logger.info(f"Group metrics compared by user {current_user.id}")
        
        return comparison
    
    except Exception as e:
        logger.error(f"Failed to compare group metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare group metrics: {str(e)}"
        )


@router.get("/rollout/history")
async def get_rollout_history(
    limit: int = 20,
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """
    롤아웃 변경 이력 조회
    
    Args:
        limit: 조회할 이력 개수 (기본값: 20)
    
    Returns:
        - history: 롤아웃 변경 이력 리스트
    """
    try:
        ab_service = ABTestService(redis)
        history = ab_service.get_rollout_history(limit)
        
        return {"history": history}
    
    except Exception as e:
        logger.error(f"Failed to get rollout history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve rollout history: {str(e)}"
        )


@router.post("/reset")
async def reset_experiment(
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """
    A/B 테스트 초기화 (모든 사용자 할당 제거)
    
    ⚠️ 주의: 이 작업은 되돌릴 수 없습니다!
    
    Returns:
        - message: 성공 메시지
    """
    try:
        ab_service = ABTestService(redis)
        ab_service.reset_experiment()
        
        logger.warning(f"Experiment reset by user {current_user.id}")
        
        return {
            "message": "Experiment reset successfully. All user assignments cleared."
        }
    
    except Exception as e:
        logger.error(f"Failed to reset experiment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset experiment: {str(e)}"
        )
