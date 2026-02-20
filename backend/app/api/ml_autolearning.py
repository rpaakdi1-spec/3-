"""
Phase 15: ML Auto-Learning API Endpoints
강화학습 기반 자동 학습 시스템
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.dispatch_data_collector import DispatchDataCollector
from app.services.rl_training_service import RLTrainingService
from app.models.ml_training import MLExperiment, ModelVersion

router = APIRouter()


# ==================== 데이터 수집 ====================

@router.post("/ml/collect-dispatch-data")
async def collect_dispatch_data(
    dispatch_id: int,
    vehicle_id: int,
    order_id: int,
    episode_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    배차 데이터 수집
    
    **배차 발생 시 자동으로 호출되어 학습 데이터 수집**
    """
    collector = DispatchDataCollector(db)
    result = await collector.collect_dispatch_data(
        dispatch_id=dispatch_id,
        vehicle_id=vehicle_id,
        order_id=order_id,
        episode_id=episode_id
    )
    
    if not result:
        raise HTTPException(status_code=400, detail="Failed to collect data")
    
    return {
        "success": True,
        "data": result
    }


@router.post("/ml/update-reward/{training_data_id}")
async def update_training_reward(
    training_data_id: int,
    completion_time: float,
    distance: float,
    success: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    학습 데이터 보상 업데이트
    
    **배차 완료 후 호출되어 보상(Reward) 계산**
    """
    collector = DispatchDataCollector(db)
    reward_info = await collector.update_reward(
        training_data_id=training_data_id,
        completion_time=completion_time,
        distance=distance,
        success=success
    )
    
    if not reward_info:
        raise HTTPException(status_code=404, detail="Training data not found")
    
    return {
        "success": True,
        "reward": reward_info
    }


@router.get("/ml/training-data")
async def get_training_data(
    limit: int = Query(100, ge=1, le=1000),
    min_reward: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    학습 데이터셋 조회
    
    **수집된 배차 데이터 확인 및 분석**
    """
    collector = DispatchDataCollector(db)
    dataset = await collector.get_training_dataset(
        limit=limit,
        min_reward=min_reward
    )
    
    return {
        "total": len(dataset),
        "data": dataset
    }


# ==================== 학습 실험 ====================

@router.post("/ml/experiments")
async def create_experiment(
    experiment_name: str,
    hyperparameters: Dict[str, Any],
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    새로운 학습 실험 생성
    
    **하이퍼파라미터 설정하고 실험 시작**
    
    Example hyperparameters:
    ```json
    {
        "learning_rate": 0.0003,
        "gamma": 0.99,
        "clip_range": 0.2,
        "n_steps": 2048
    }
    ```
    """
    trainer = RLTrainingService(db)
    result = await trainer.create_experiment(
        experiment_name=experiment_name,
        hyperparameters=hyperparameters,
        description=description
    )
    
    return result


@router.post("/ml/experiments/{experiment_id}/train")
async def start_training(
    experiment_id: int,
    epochs: int = Query(100, ge=1, le=1000),
    batch_size: int = Query(32, ge=1, le=256),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    학습 시작
    
    **실험 ID로 학습 실행**
    """
    trainer = RLTrainingService(db)
    result = await trainer.start_training(
        experiment_id=experiment_id,
        epochs=epochs,
        batch_size=batch_size
    )
    
    return result


@router.get("/ml/experiments/{experiment_id}/progress")
async def get_training_progress(
    experiment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    학습 진행 상황 조회
    
    **실시간 학습 상태 및 메트릭 확인**
    """
    trainer = RLTrainingService(db)
    progress = await trainer.get_training_progress(experiment_id)
    
    return progress


@router.get("/ml/experiments")
async def list_experiments(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    실험 목록 조회
    
    **모든 학습 실험 이력 확인**
    """
    query = db.query(MLExperiment)
    
    if status:
        query = query.filter(MLExperiment.status == status)
    
    experiments = query.order_by(
        MLExperiment.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    results = []
    for exp in experiments:
        results.append({
            "id": exp.id,
            "experiment_name": exp.experiment_name,
            "experiment_type": exp.experiment_type,
            "status": exp.status,
            "best_reward": exp.best_reward,
            "best_epoch": exp.best_epoch,
            "started_at": exp.started_at.isoformat() if exp.started_at else None,
            "completed_at": exp.completed_at.isoformat() if exp.completed_at else None,
            "duration_seconds": exp.duration_seconds
        })
    
    return {
        "total": len(results),
        "experiments": results
    }


# ==================== 모델 버전 관리 ====================

@router.post("/ml/models")
async def create_model_version(
    experiment_id: int,
    version: str,
    model_name: str = "PPO_Dispatch",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    모델 버전 생성
    
    **학습 완료 후 모델 저장 및 버전 관리**
    """
    trainer = RLTrainingService(db)
    result = await trainer.create_model_version(
        experiment_id=experiment_id,
        version=version,
        model_name=model_name
    )
    
    return result


@router.post("/ml/models/{model_id}/deploy")
async def deploy_model(
    model_id: int,
    ab_test_traffic: float = Query(0.1, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    모델 배포 (A/B 테스트)
    
    **검증된 모델을 프로덕션에 배포**
    
    - ab_test_traffic: A/B 테스트 트래픽 비율 (0.0 ~ 1.0)
      - 0.1 = 10% 트래픽에 새 모델 적용
      - 1.0 = 100% 전체 적용
    """
    trainer = RLTrainingService(db)
    result = await trainer.deploy_model(
        model_id=model_id,
        ab_test_traffic=ab_test_traffic
    )
    
    return result


@router.get("/ml/models")
async def list_models(
    skip: int = 0,
    limit: int = 20,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    모델 버전 목록 조회
    
    **모든 모델 버전 및 배포 상태 확인**
    """
    query = db.query(ModelVersion)
    
    if is_active is not None:
        query = query.filter(ModelVersion.is_active == is_active)
    
    models = query.order_by(
        ModelVersion.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    results = []
    for model in models:
        results.append({
            "id": model.id,
            "version": model.version,
            "model_name": model.model_name,
            "model_type": model.model_type,
            "status": model.status,
            "is_active": model.is_active,
            "deployed_at": model.deployed_at.isoformat() if model.deployed_at else None,
            "ab_test_traffic_percent": model.ab_test_traffic_percent,
            "performance_metrics": model.performance_metrics,
            "created_at": model.created_at.isoformat()
        })
    
    return {
        "total": len(results),
        "models": results
    }


@router.get("/ml/models/active")
async def get_active_model(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    현재 활성 모델 조회
    
    **프로덕션에서 사용 중인 모델 정보**
    """
    active_model = db.query(ModelVersion).filter(
        ModelVersion.is_active == True
    ).first()
    
    if not active_model:
        return {
            "active": False,
            "message": "No active model deployed"
        }
    
    return {
        "active": True,
        "model": {
            "id": active_model.id,
            "version": active_model.version,
            "model_name": active_model.model_name,
            "model_type": active_model.model_type,
            "deployed_at": active_model.deployed_at.isoformat() if active_model.deployed_at else None,
            "ab_test_traffic_percent": active_model.ab_test_traffic_percent,
            "performance_metrics": active_model.performance_metrics
        }
    }


# ==================== 실시간 예측 ====================

@router.post("/ml/predict")
async def predict_dispatch(
    state_features: Dict[str, Any],
    model_version: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    AI 배차 예측
    
    **학습된 모델로 최적 차량 추천**
    
    Example state_features:
    ```json
    {
        "vehicle": {"vehicle_id": 1, "status": "AVAILABLE"},
        "order": {"order_id": 100, "priority": 1},
        "time": {"hour": 10, "is_peak_hour": true},
        "environment": {"active_vehicles": 20}
    }
    ```
    """
    trainer = RLTrainingService(db)
    prediction = await trainer.get_model_prediction(
        state_features=state_features,
        model_version=model_version
    )
    
    return prediction


# ==================== 통계 & 모니터링 ====================

@router.get("/ml/statistics")
async def get_ml_statistics(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ML 시스템 통계
    
    **학습 데이터, 실험, 모델 현황 통계**
    """
    from sqlalchemy import func
    from app.models.ml_training import DispatchTrainingData, RLRewardHistory
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # 학습 데이터 통계
    total_training_data = db.query(func.count(DispatchTrainingData.id)).scalar()
    completed_episodes = db.query(func.count(DispatchTrainingData.id)).filter(
        DispatchTrainingData.done == True
    ).scalar()
    
    avg_reward = db.query(func.avg(DispatchTrainingData.reward)).filter(
        DispatchTrainingData.done == True,
        DispatchTrainingData.collected_at >= since
    ).scalar()
    
    # 실험 통계
    total_experiments = db.query(func.count(MLExperiment.id)).scalar()
    completed_experiments = db.query(func.count(MLExperiment.id)).filter(
        MLExperiment.status == "completed"
    ).scalar()
    
    # 모델 통계
    total_models = db.query(func.count(ModelVersion.id)).scalar()
    deployed_models = db.query(func.count(ModelVersion.id)).filter(
        ModelVersion.status == "deployed"
    ).scalar()
    
    # 최근 보상 추이
    recent_rewards = db.query(
        RLRewardHistory.timestamp,
        RLRewardHistory.total_reward
    ).filter(
        RLRewardHistory.timestamp >= since
    ).order_by(RLRewardHistory.timestamp.desc()).limit(100).all()
    
    reward_trend = [
        {
            "timestamp": r.timestamp.isoformat(),
            "reward": float(r.total_reward)
        }
        for r in recent_rewards
    ]
    
    return {
        "period_days": days,
        "training_data": {
            "total_samples": total_training_data or 0,
            "completed_episodes": completed_episodes or 0,
            "average_reward": float(avg_reward) if avg_reward else 0.0
        },
        "experiments": {
            "total": total_experiments or 0,
            "completed": completed_experiments or 0
        },
        "models": {
            "total": total_models or 0,
            "deployed": deployed_models or 0
        },
        "reward_trend": reward_trend
    }


# ==================== Phase 3: ML-based Rule Suggestions ====================

@router.post("/ml/suggest-rules")
async def suggest_dispatch_rules(
    days_back: int = Query(30, ge=7, le=365, description="분석할 과거 일수"),
    limit: int = Query(10, ge=1, le=50, description="최대 제안 규칙 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🤖 **Phase 3: ML 기반 배차 규칙 자동 제안**
    
    과거 배차 데이터를 분석하여 최적의 배차 규칙을 자동으로 추천합니다.
    
    - **온도대별 차량 할당 패턴**
    - **거리 기반 차량 선택 패턴**
    - **시간대별 배차 패턴**
    - **적재율 최적화 패턴**
    - **고객별 선호 차량 패턴**
    
    **Parameters:**
    - days_back: 분석할 과거 일수 (기본 30일)
    - limit: 최대 제안 규칙 수 (기본 10개)
    
    **Returns:**
    제안된 규칙 목록과 각 규칙의 신뢰도, 지지도, 예상 개선 효과
    """
    from app.services.ml_rule_suggestion_service import MLRuleSuggestionService
    
    service = MLRuleSuggestionService(db)
    suggestions = await service.analyze_and_suggest_rules(
        days_back=days_back,
        limit=limit
    )
    
    return {
        "analysis_period_days": days_back,
        "total_suggestions": len(suggestions),
        "suggestions": [
            {
                "rule_type": s.rule_type,
                "name": s.name,
                "description": s.description,
                "conditions": s.conditions,
                "actions": s.actions,
                "confidence": round(s.confidence, 3),
                "support": s.support,
                "expected_improvement": s.expected_improvement,
                "priority": s.priority
            }
            for s in suggestions
        ],
        "generated_at": datetime.utcnow().isoformat()
    }


@router.post("/ml/apply-suggested-rules")
async def apply_suggested_rules(
    days_back: int = Query(30, ge=7, le=365),
    limit: int = Query(10, ge=1, le=50),
    auto_activate: bool = Query(False, description="자동 활성화 여부"),
    min_confidence: float = Query(0.7, ge=0.0, le=1.0, description="최소 신뢰도"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🚀 **ML이 제안한 규칙을 실제 시스템에 적용**
    
    제안된 규칙 중 신뢰도가 높은 규칙들을 자동으로 생성하고 활성화합니다.
    
    **Parameters:**
    - days_back: 분석할 과거 일수
    - limit: 최대 적용 규칙 수
    - auto_activate: 생성 즉시 활성화 여부 (기본: False)
    - min_confidence: 적용할 규칙의 최소 신뢰도 (기본: 0.7)
    
    **Returns:**
    생성된 규칙 목록과 ID
    """
    from app.services.ml_rule_suggestion_service import MLRuleSuggestionService
    
    service = MLRuleSuggestionService(db)
    
    # 1. 규칙 제안 받기
    suggestions = await service.analyze_and_suggest_rules(
        days_back=days_back,
        limit=limit
    )
    
    # 2. 신뢰도 필터링
    filtered_suggestions = [
        s for s in suggestions
        if s.confidence >= min_confidence
    ]
    
    # 3. 규칙 생성
    created_rules = await service.create_rules_from_suggestions(
        suggestions=filtered_suggestions,
        auto_activate=auto_activate
    )
    
    return {
        "success": True,
        "total_suggestions": len(suggestions),
        "filtered_by_confidence": len(filtered_suggestions),
        "created_rules": len(created_rules),
        "auto_activated": auto_activate,
        "rules": [
            {
                "id": rule.id,
                "name": rule.name,
                "rule_type": rule.rule_type,
                "priority": rule.priority,
                "is_active": rule.is_active,
                "created_at": rule.created_at.isoformat()
            }
            for rule in created_rules
        ]
    }


@router.get("/ml/rule-performance/{rule_id}")
async def get_rule_performance(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📊 **규칙 성능 리포트**
    
    특정 규칙의 실행 통계와 성능 지표를 조회합니다.
    
    **Returns:**
    - 총 실행 횟수
    - 성공률
    - 평균 실행 시간
    - 총 절감 거리/비용/시간
    """
    from app.services.ml_rule_suggestion_service import MLRuleSuggestionService
    
    service = MLRuleSuggestionService(db)
    report = await service.get_rule_performance_report(rule_id)
    
    return report


@router.post("/ml/auto-optimize")
async def auto_optimize_rules(
    days_back: int = Query(30, ge=7, le=365),
    optimization_target: str = Query("balanced", regex="^(distance|cost|time|balanced)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ⚡ **자동 최적화 (한 번에 모든 작업 실행)**
    
    1. 과거 데이터 분석
    2. 규칙 제안
    3. 고신뢰도 규칙 자동 생성
    4. 기존 규칙 성능 평가
    5. 저성능 규칙 비활성화
    
    **Parameters:**
    - days_back: 분석할 과거 일수
    - optimization_target: 최적화 목표 (distance/cost/time/balanced)
    
    **Returns:**
    최적화 결과 요약
    """
    from app.services.ml_rule_suggestion_service import MLRuleSuggestionService
    from app.models.dispatch_rule import DispatchRule, RuleExecutionLog
    
    service = MLRuleSuggestionService(db)
    
    # Step 1: 규칙 제안
    suggestions = await service.analyze_and_suggest_rules(
        days_back=days_back,
        limit=20
    )
    
    # Step 2: 고신뢰도 규칙 생성 (80% 이상)
    high_confidence = [s for s in suggestions if s.confidence >= 0.8]
    created_rules = await service.create_rules_from_suggestions(
        suggestions=high_confidence,
        auto_activate=True
    )
    
    # Step 3: 기존 규칙 성능 평가
    existing_rules = db.query(DispatchRule).filter(
        DispatchRule.is_active == True
    ).all()
    
    poor_performing_rules = []
    for rule in existing_rules:
        if rule.execution_count >= 10:  # 최소 10회 이상 실행된 규칙만
            if rule.success_rate and rule.success_rate < 50:  # 성공률 50% 미만
                rule.is_active = False
                poor_performing_rules.append({
                    "id": rule.id,
                    "name": rule.name,
                    "success_rate": rule.success_rate
                })
    
    db.commit()
    
    return {
        "success": True,
        "optimization_target": optimization_target,
        "analysis_period_days": days_back,
        "summary": {
            "total_suggestions": len(suggestions),
            "high_confidence_suggestions": len(high_confidence),
            "rules_created": len(created_rules),
            "rules_deactivated": len(poor_performing_rules)
        },
        "created_rules": [
            {"id": r.id, "name": r.name, "priority": r.priority}
            for r in created_rules
        ],
        "deactivated_rules": poor_performing_rules,
        "next_review_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
    }

