"""
ML Dispatch API Endpoints

Phase 2: Historical data simulation and performance benchmarking
"""

from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleStatus
from app.models.order import Order, OrderStatus
from app.models.dispatch import Dispatch, DispatchStatus
from app.api.auth import get_current_user
from app.services.ml_dispatch_service import MLDispatchService
from app.services.ab_test_service import ABTestService, ABTestMetricsService


router = APIRouter(prefix="/api/ml-dispatch", tags=["ML Dispatch"])


# Dependency for Redis connection
def get_redis():
    """Get Redis connection (placeholder - implement based on your setup)"""
    from redis import Redis
    import os
    
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    
    return Redis(host=redis_host, port=redis_port, decode_responses=False)


# ============================================
# Phase 2: Historical Simulation
# ============================================

@router.post("/simulate")
async def simulate_historical_dispatch(
    target_date: str = Query(..., description="Target date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    과거 데이터로 ML 배차 시뮬레이션
    
    실제 배차된 결과와 ML 추천을 비교하여 성능을 평가합니다.
    
    Example:
        POST /api/ml-dispatch/simulate?target_date=2026-02-01
    
    Returns:
        {
            "date": "2026-02-01",
            "total_orders": 45,
            "ml_match_rate": 0.73,
            "performance_metrics": {...},
            "comparisons": [...]
        }
    """
    try:
        # 날짜 파싱
        target_dt = datetime.strptime(target_date, "%Y-%m-%d").date()
        logger.info(f"Simulating ML dispatch for {target_date}")
        
        # 해당 날짜 주문 조회
        orders = (
            db.query(Order)
            .filter(Order.order_date == target_dt)
            .filter(Order.status != OrderStatus.CANCELLED)
            .all()
        )
        
        if not orders:
            return {
                "date": target_date,
                "total_orders": 0,
                "message": "No orders found for this date",
                "comparisons": []
            }
        
        # 당시 활성 차량 조회
        vehicles = (
            db.query(Vehicle)
            .filter(Vehicle.is_active == True)
            .all()
        )
        
        if not vehicles:
            raise HTTPException(status_code=400, detail="No active vehicles found")
        
        # ML 서비스 초기화
        ml_service = MLDispatchService(db)
        
        # 시뮬레이션 실행
        comparisons = []
        ml_matches = 0
        total_simulated = 0
        
        for order in orders:
            # ML 추천 생성
            rankings = await ml_service.optimize_single_order(order, vehicles)
            
            if not rankings:
                logger.warning(f"No ML recommendation for order {order.order_number}")
                continue
            
            ml_top = rankings[0]
            total_simulated += 1
            
            # 실제 배차 내역 조회
            actual_dispatch = (
                db.query(Dispatch)
                .filter(Dispatch.order_id == order.id)
                .first()
            )
            
            # 매칭 여부 확인
            is_match = False
            if actual_dispatch:
                is_match = (ml_top.vehicle.id == actual_dispatch.vehicle_id)
                if is_match:
                    ml_matches += 1
            
            # 비교 데이터 생성
            comparison = {
                "order_id": order.id,
                "order_number": order.order_number,
                "temperature_zone": order.temperature_zone.value,
                "pallet_count": order.pallet_count,
                "ml_recommendation": {
                    "vehicle_id": ml_top.vehicle.id,
                    "vehicle_code": ml_top.vehicle.code,
                    "score": round(ml_top.total_score, 3),
                    "reason": ml_top.reason,
                    "scores": {
                        "distance": round(ml_top.agent_scores.distance, 3),
                        "rotation": round(ml_top.agent_scores.rotation, 3),
                        "time_window": round(ml_top.agent_scores.time_window, 3),
                        "preference": round(ml_top.agent_scores.preference, 3),
                        "voltage": ml_top.agent_scores.voltage
                    }
                },
                "actual_dispatch": {
                    "vehicle_id": actual_dispatch.vehicle_id if actual_dispatch else None,
                    "vehicle_code": actual_dispatch.vehicle.code if actual_dispatch else None,
                    "assigned_by": actual_dispatch.assigned_by if actual_dispatch else None
                } if actual_dispatch else None,
                "match": is_match,
                "top_3": [
                    {
                        "rank": i + 1,
                        "vehicle_code": rank.vehicle.code,
                        "score": round(rank.total_score, 3),
                        "reason": rank.reason
                    }
                    for i, rank in enumerate(rankings[:3])
                ]
            }
            
            comparisons.append(comparison)
        
        # 매칭률 계산
        match_rate = ml_matches / total_simulated if total_simulated > 0 else 0.0
        
        # 성능 메트릭 계산
        performance = _calculate_performance_metrics(comparisons)
        
        logger.info(
            f"Simulation complete: {total_simulated} orders, "
            f"{ml_matches} matches ({match_rate:.1%})"
        )
        
        return {
            "date": target_date,
            "total_orders": len(orders),
            "simulated_orders": total_simulated,
            "ml_match_rate": round(match_rate, 3),
            "ml_matches": ml_matches,
            "performance_metrics": performance,
            "comparisons": comparisons
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/simulate/metrics")
async def get_simulation_metrics(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    기간별 시뮬레이션 메트릭 조회
    
    Example:
        GET /api/ml-dispatch/simulate/metrics?start_date=2026-02-01&end_date=2026-02-07
    
    Returns:
        {
            "period": {"start": "2026-02-01", "end": "2026-02-07"},
            "daily_metrics": [...],
            "summary": {...}
        }
    """
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        # 기간별 주문 조회
        orders = (
            db.query(Order)
            .filter(Order.order_date >= start_dt)
            .filter(Order.order_date <= end_dt)
            .filter(Order.status != OrderStatus.CANCELLED)
            .all()
        )
        
        # 날짜별 그룹화
        daily_data = {}
        for order in orders:
            date_key = order.order_date.strftime("%Y-%m-%d")
            if date_key not in daily_data:
                daily_data[date_key] = []
            daily_data[date_key].append(order)
        
        # 날짜별 메트릭 계산
        daily_metrics = []
        total_orders = 0
        total_matches = 0
        
        for date_key in sorted(daily_data.keys()):
            date_orders = daily_data[date_key]
            
            # 간단한 메트릭만 계산 (전체 시뮬레이션은 비용이 큼)
            dispatches = (
                db.query(Dispatch)
                .join(Order)
                .filter(Order.order_date == datetime.strptime(date_key, "%Y-%m-%d").date())
                .all()
            )
            
            daily_metrics.append({
                "date": date_key,
                "total_orders": len(date_orders),
                "total_dispatches": len(dispatches),
                "dispatch_rate": len(dispatches) / len(date_orders) if date_orders else 0.0
            })
            
            total_orders += len(date_orders)
            total_matches += len(dispatches)
        
        summary = {
            "total_days": len(daily_data),
            "total_orders": total_orders,
            "total_dispatches": total_matches,
            "avg_orders_per_day": total_orders / len(daily_data) if daily_data else 0.0,
            "overall_dispatch_rate": total_matches / total_orders if total_orders > 0 else 0.0
        }
        
        return {
            "period": {
                "start": start_date,
                "end": end_date
            },
            "daily_metrics": daily_metrics,
            "summary": summary
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Phase 2: Real-time ML Optimization
# ============================================

@router.post("/optimize")
async def optimize_dispatch_ml(
    order_ids: List[int],
    mode: str = Query("recommend", regex="^(recommend|auto)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ML 기반 배차 최적화
    
    Args:
        order_ids: 배차할 주문 ID 리스트
        mode: 'recommend' (추천만) or 'auto' (자동 배차)
    
    Example:
        POST /api/ml-dispatch/optimize?mode=recommend
        {
            "order_ids": [123, 124, 125]
        }
    
    Returns:
        {
            "mode": "recommend",
            "results": [
                {
                    "order_id": 123,
                    "order_number": "ORD-2026-001",
                    "top_3": [
                        {
                            "rank": 1,
                            "vehicle_code": "V001",
                            "score": 0.823,
                            "reason": "근거리, 회전수적음, 시간여유"
                        }
                    ]
                }
            ]
        }
    """
    try:
        # 주문 조회
        orders = (
            db.query(Order)
            .filter(Order.id.in_(order_ids))
            .filter(Order.status == OrderStatus.PENDING)
            .all()
        )
        
        if not orders:
            raise HTTPException(status_code=404, detail="No pending orders found")
        
        # 가용 차량 조회
        vehicles = (
            db.query(Vehicle)
            .filter(Vehicle.status == VehicleStatus.AVAILABLE)
            .filter(Vehicle.is_active == True)
            .all()
        )
        
        if not vehicles:
            raise HTTPException(status_code=400, detail="No available vehicles")
        
        # ML 서비스 실행
        ml_service = MLDispatchService(db)
        optimization_results = await ml_service.optimize_dispatch(orders, vehicles)
        
        # 결과 포맷팅
        results = []
        dispatches_created = []
        
        for result in optimization_results:
            order = result['order']
            rankings = result['rankings']
            
            if not rankings:
                logger.warning(f"No vehicles available for order {order.order_number}")
                results.append({
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "error": "No eligible vehicles",
                    "top_3": []
                })
                continue
            
            # Auto mode: 자동 배차
            if mode == "auto":
                best = rankings[0]
                
                dispatch = Dispatch(
                    order_id=order.id,
                    vehicle_id=best.vehicle.id,
                    optimization_score=best.total_score,
                    assigned_by='ml_auto',
                    assigned_user_id=current_user.id,
                    status=DispatchStatus.ASSIGNED
                )
                
                db.add(dispatch)
                dispatches_created.append(dispatch)
                
                logger.info(
                    f"Auto-assigned: Order {order.order_number} → "
                    f"Vehicle {best.vehicle.code} (score: {best.total_score:.3f})"
                )
            
            # 결과 추가
            results.append({
                "order_id": order.id,
                "order_number": order.order_number,
                "temperature_zone": order.temperature_zone.value,
                "pallet_count": order.pallet_count,
                "top_3": [
                    {
                        "rank": i + 1,
                        "vehicle_id": rank.vehicle.id,
                        "vehicle_code": rank.vehicle.code,
                        "score": round(rank.total_score, 3),
                        "reason": rank.reason,
                        "details": {
                            "distance_score": round(rank.agent_scores.distance, 3),
                            "rotation_score": round(rank.agent_scores.rotation, 3),
                            "time_score": round(rank.agent_scores.time_window, 3),
                            "preference_score": round(rank.agent_scores.preference, 3),
                            "voltage_ok": rank.agent_scores.voltage == 1.0
                        }
                    }
                    for i, rank in enumerate(rankings[:3])
                ]
            })
        
        # Auto mode: DB 커밋
        if mode == "auto":
            db.commit()
            logger.info(f"Auto-dispatch complete: {len(dispatches_created)} dispatches created")
        
        return {
            "mode": mode,
            "total_orders": len(orders),
            "successful": len([r for r in results if 'error' not in r]),
            "failed": len([r for r in results if 'error' in r]),
            "dispatches_created": len(dispatches_created) if mode == "auto" else 0,
            "results": results
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"ML optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def get_ml_performance(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ML 배차 성과 분석
    
    Example:
        GET /api/ml-dispatch/performance?start_date=2026-02-01&end_date=2026-02-07
    
    Returns:
        {
            "ml_dispatches": {...},
            "human_dispatches": {...},
            "comparison": {...}
        }
    """
    try:
        query = db.query(Dispatch)
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Dispatch.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(Dispatch.created_at <= end_dt)
        
        all_dispatches = query.all()
        
        # ML vs Human 분류
        ml_dispatches = [d for d in all_dispatches if d.assigned_by and 'ml' in d.assigned_by.lower()]
        human_dispatches = [d for d in all_dispatches if d.assigned_by and 'ml' not in d.assigned_by.lower()]
        
        # 메트릭 계산
        ml_metrics = _calculate_dispatch_metrics(ml_dispatches)
        human_metrics = _calculate_dispatch_metrics(human_dispatches)
        
        # 비교 분석
        comparison = {
            "improvement": {
                "avg_score": ml_metrics.get('avg_score', 0) - human_metrics.get('avg_score', 0),
                "dispatch_count": len(ml_dispatches) - len(human_dispatches)
            }
        }
        
        return {
            "period": {
                "start": start_date,
                "end": end_date
            },
            "ml_dispatches": {
                "count": len(ml_dispatches),
                "metrics": ml_metrics
            },
            "human_dispatches": {
                "count": len(human_dispatches),
                "metrics": human_metrics
            },
            "comparison": comparison
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"Performance analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Helper Functions
# ============================================

def _calculate_performance_metrics(comparisons: List[dict]) -> dict:
    """시뮬레이션 성능 메트릭 계산"""
    if not comparisons:
        return {}
    
    # 평균 점수
    scores = [c['ml_recommendation']['score'] for c in comparisons]
    avg_score = sum(scores) / len(scores)
    
    # 점수 분포
    high_score_count = len([s for s in scores if s >= 0.7])
    medium_score_count = len([s for s in scores if 0.5 <= s < 0.7])
    low_score_count = len([s for s in scores if s < 0.5])
    
    # Agent별 평균 점수
    agent_scores = {
        'distance': [],
        'rotation': [],
        'time_window': [],
        'preference': []
    }
    
    for comp in comparisons:
        scores_dict = comp['ml_recommendation']['scores']
        for key in agent_scores:
            agent_scores[key].append(scores_dict[key])
    
    agent_averages = {
        key: sum(values) / len(values) if values else 0.0
        for key, values in agent_scores.items()
    }
    
    return {
        "avg_score": round(avg_score, 3),
        "score_distribution": {
            "high": high_score_count,
            "medium": medium_score_count,
            "low": low_score_count
        },
        "agent_averages": {
            key: round(val, 3)
            for key, val in agent_averages.items()
        }
    }


def _calculate_dispatch_metrics(dispatches: List[Dispatch]) -> dict:
    """배차 메트릭 계산"""
    if not dispatches:
        return {
            "count": 0,
            "avg_score": 0.0
        }
    
    # 평균 점수 (optimization_score가 있는 경우만)
    scores = [d.optimization_score for d in dispatches if d.optimization_score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    
    return {
        "count": len(dispatches),
        "avg_score": round(avg_score, 3),
        "with_scores": len(scores)
    }


# ============================================
# Phase 3: A/B Testing
# ============================================

@router.get("/ab-test/assignment")
async def get_ab_test_assignment(
    current_user: User = Depends(get_current_user),
    redis = Depends(get_redis)
):
    """
    현재 사용자의 A/B 테스트 그룹 조회
    
    Returns:
        {
            "user_id": 123,
            "group": "treatment" | "control",
            "ml_enabled": true | false,
            "rollout_percentage": 10
        }
    """
    try:
        ab_service = ABTestService(redis)
        group = ab_service.assign_user_to_group(current_user.id)
        
        return {
            "user_id": current_user.id,
            "group": group,
            "ml_enabled": (group == "treatment"),
            "rollout_percentage": ab_service._get_rollout_percentage()
        }
    except Exception as e:
        logger.error(f"A/B test assignment error: {e}")
        # Fallback to control
        return {
            "user_id": current_user.id,
            "group": "control",
            "ml_enabled": False,
            "error": str(e)
        }


@router.post("/ab-test/rollout")
async def update_rollout_percentage(
    percentage: int = Query(..., ge=0, le=100),
    current_user: User = Depends(get_current_user),
    redis = Depends(get_redis)
):
    """
    롤아웃 비율 업데이트 (관리자 전용)
    
    Args:
        percentage: 0-100 (treatment 그룹 비율)
    
    Returns:
        {
            "success": true,
            "old_percentage": 10,
            "new_percentage": 30,
            "stats": {...}
        }
    """
    # TODO: Admin 권한 체크
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin only")
    
    try:
        ab_service = ABTestService(redis)
        old_percentage = ab_service._get_rollout_percentage()
        
        ab_service.set_rollout_percentage(percentage)
        
        stats = ab_service.get_experiment_stats()
        
        logger.info(
            f"Rollout updated by user {current_user.id}: "
            f"{old_percentage}% → {percentage}%"
        )
        
        return {
            "success": True,
            "old_percentage": old_percentage,
            "new_percentage": percentage,
            "stats": stats
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Rollout update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ab-test/stats")
async def get_ab_test_stats(
    current_user: User = Depends(get_current_user),
    redis = Depends(get_redis)
):
    """
    A/B 테스트 통계 조회
    
    Returns:
        {
            "total_users": 1250,
            "control_count": 1125,
            "treatment_count": 125,
            "actual_treatment_percentage": 10.0,
            "target_rollout_percentage": 10
        }
    """
    try:
        ab_service = ABTestService(redis)
        stats = ab_service.get_experiment_stats()
        
        return stats
    except Exception as e:
        logger.error(f"A/B test stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ab-test/metrics")
async def get_ab_test_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    A/B 테스트 메트릭 비교
    
    Returns:
        {
            "control": {
                "total_dispatches": 450,
                "success_rate": 0.956,
                "avg_response_time": 1.23
            },
            "treatment": {
                "total_dispatches": 50,
                "success_rate": 0.980,
                "avg_score": 0.756,
                "avg_response_time": 1.45
            },
            "improvements": {
                "success_rate": 0.024,
                "success_rate_percentage": 2.4
            },
            "winner": "treatment"
        }
    """
    try:
        metrics_service = ABTestMetricsService(db, redis)
        comparison = metrics_service.compare_groups()
        
        return comparison
    except Exception as e:
        logger.error(f"A/B test metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ab-test/history")
async def get_rollout_history(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    redis = Depends(get_redis)
):
    """
    롤아웃 변경 이력 조회
    
    Returns:
        [
            {
                "timestamp": "2026-02-02T10:30:00",
                "old_percentage": 10,
                "new_percentage": 30
            },
            ...
        ]
    """
    try:
        ab_service = ABTestService(redis)
        history = ab_service.get_rollout_history(limit)
        
        return {
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        logger.error(f"Rollout history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ab-test/force-assign")
async def force_assign_user(
    user_id: int,
    group: str = Query(..., regex="^(control|treatment)$"),
    current_user: User = Depends(get_current_user),
    redis = Depends(get_redis)
):
    """
    사용자를 특정 그룹에 강제 할당 (테스트용)
    
    Args:
        user_id: 대상 사용자 ID
        group: 'control' or 'treatment'
    """
    # TODO: Admin 권한 체크
    
    try:
        ab_service = ABTestService(redis)
        ab_service.force_assign_user(user_id, group)
        
        logger.warning(
            f"User {user_id} force assigned to {group} "
            f"by admin {current_user.id}"
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "group": group
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Force assign error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
