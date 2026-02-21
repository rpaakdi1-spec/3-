"""
Dispatch Rules API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.dispatch_rule import DispatchRule, RuleExecutionLog
from app.services.rule_engine import RuleEngine
from app.services.rule_parser import RuleParser

router = APIRouter()

# ============ Pydantic Schemas ============

class RuleCondition(BaseModel):
    """규칙 조건"""
    pass  # 자유 형식 JSON

class RuleAction(BaseModel):
    """규칙 액션"""
    pass  # 자유 형식 JSON

class DispatchRuleCreate(BaseModel):
    """규칙 생성 스키마"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    rule_type: str = Field(..., pattern="^(assignment|constraint|optimization)$")
    priority: int = Field(default=0, ge=0, le=1000)
    conditions: dict
    actions: dict
    apply_time_start: Optional[str] = None  # HH:MM
    apply_time_end: Optional[str] = None
    apply_days: Optional[str] = None  # MON,TUE,WED

class DispatchRuleUpdate(BaseModel):
    """규칙 수정 스키마"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=0, le=1000)
    is_active: Optional[bool] = None
    conditions: Optional[dict] = None
    actions: Optional[dict] = None
    apply_time_start: Optional[str] = None
    apply_time_end: Optional[str] = None
    apply_days: Optional[str] = None

class DispatchRuleResponse(BaseModel):
    """규칙 응답 스키마"""
    id: int
    name: str
    description: Optional[str]
    rule_type: str
    priority: int
    is_active: bool
    conditions: dict
    actions: dict
    version: int
    execution_count: int
    avg_execution_time_ms: Optional[float]
    success_rate: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RuleTestRequest(BaseModel):
    """규칙 테스트 요청"""
    test_data: dict

class RuleTestResponse(BaseModel):
    """규칙 테스트 응답"""
    rule_id: int
    rule_name: str
    matched: bool
    conditions: dict
    actions: Optional[dict]
    test_data: dict

# ============ API Endpoints ============

@router.post("/", response_model=DispatchRuleResponse, status_code=201)
async def create_rule(
    rule: DispatchRuleCreate,
    db: Session = Depends(get_db)
):
    """
    새로운 배차 규칙 생성
    """
    # 규칙 검증
    parser = RuleParser()
    is_valid, error_message = parser.validate_rule(rule.dict())
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid rule: {error_message}")
    
    # 규칙 생성
    db_rule = DispatchRule(
        name=rule.name,
        description=rule.description,
        rule_type=rule.rule_type,
        priority=rule.priority,
        conditions=rule.conditions,
        actions=rule.actions,
        apply_time_start=rule.apply_time_start,
        apply_time_end=rule.apply_time_end,
        apply_days=rule.apply_days,
        created_by=None
    )
    
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    
    return db_rule

@router.get("/", response_model=List[DispatchRuleResponse])
async def list_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    rule_type: Optional[str] = Query(None, pattern="^(assignment|constraint|optimization)$"),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = None
):
    """
    배차 규칙 목록 조회
    """
    query = db.query(DispatchRule)
    
    if rule_type:
        query = query.filter(DispatchRule.rule_type == rule_type)
    if is_active is not None:
        query = query.filter(DispatchRule.is_active == is_active)
    
    rules = query.order_by(
        DispatchRule.priority.desc(),
        DispatchRule.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return rules

@router.get("/{rule_id}", response_model=DispatchRuleResponse)
async def get_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = None
):
    """
    특정 배차 규칙 조회
    """
    rule = db.query(DispatchRule).filter(DispatchRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.put("/{rule_id}", response_model=DispatchRuleResponse)
async def update_rule(
    rule_id: int,
    rule_update: DispatchRuleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = None
):
    """
    배차 규칙 수정
    """
    db_rule = db.query(DispatchRule).filter(DispatchRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # 버전 증가
    db_rule.version += 1
    
    # 업데이트
    update_data = rule_update.dict(exclude_unset=True)
    
    # 규칙 검증 (conditions나 actions가 업데이트되는 경우)
    if 'conditions' in update_data or 'actions' in update_data:
        test_rule = {
            'conditions': update_data.get('conditions', db_rule.conditions),
            'actions': update_data.get('actions', db_rule.actions)
        }
        parser = RuleParser()
        is_valid, error_message = parser.validate_rule(test_rule)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid rule: {error_message}")
    
    for field, value in update_data.items():
        setattr(db_rule, field, value)
    
    db.commit()
    db.refresh(db_rule)
    
    return db_rule

@router.delete("/{rule_id}", status_code=204)
async def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = None
):
    """
    배차 규칙 삭제 (soft delete)
    """
    db_rule = db.query(DispatchRule).filter(DispatchRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db_rule.is_active = False
    db.commit()
    
    return

@router.post("/{rule_id}/test")
async def test_rule(
    rule_id: int,
    request_body: dict,
    db: Session = Depends(get_db),
    current_user: dict = None
):
    """
    규칙 테스트 (dry run)
    
    Request body: { "test_data": { ... } }
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Test request received for rule {rule_id}: {request_body}")
    
    rule = db.query(DispatchRule).filter(DispatchRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Extract test_data from request body
    test_data = request_body.get("test_data", {})
    
    try:
        engine = RuleEngine(db)
        result = engine.evaluate_single_rule(rule_id, test_data)
        
        if 'error' in result:
            logger.error(f"Rule evaluation error: {result['error']}")
            return {"success": False, "error": result['error']}
        
        logger.info(f"Test completed successfully: {result}")
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return {"success": False, "error": str(e)}

@router.post("/{rule_id}/activate")
async def activate_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = None
):
    """
    규칙 활성화
    """
    rule = db.query(DispatchRule).filter(DispatchRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    rule.is_active = True
    db.commit()
    
    return {"message": "Rule activated", "rule_id": rule_id}

@router.post("/{rule_id}/deactivate")
async def deactivate_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = None
):
    """
    규칙 비활성화
    """
    rule = db.query(DispatchRule).filter(DispatchRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    rule.is_active = False
    db.commit()
    
    return {"message": "Rule deactivated", "rule_id": rule_id}

@router.get("/{rule_id}/logs")
async def get_rule_logs(
    rule_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = None
):
    """
    규칙 실행 로그 조회
    """
    logs = db.query(RuleExecutionLog).filter(
        RuleExecutionLog.rule_id == rule_id
    ).order_by(
        RuleExecutionLog.executed_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [
        {
            'id': log.id,
            'executed_at': log.executed_at.isoformat(),
            'execution_time_ms': log.execution_time_ms,
            'success': log.success,
            'error_message': log.error_message,
            'distance_saved_km': log.distance_saved_km,
            'cost_saved': log.cost_saved
        }
        for log in logs
    ]

@router.get("/{rule_id}/performance")
async def get_rule_performance(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = None
):
    """
    규칙 성능 메트릭 조회
    """
    rule = db.query(DispatchRule).filter(DispatchRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # 통계 계산
    stats = db.query(
        func.count(RuleExecutionLog.id).label('total'),
        func.sum(func.cast(RuleExecutionLog.success, Integer)).label('success_count'),
        func.avg(RuleExecutionLog.execution_time_ms).label('avg_time'),
        func.sum(RuleExecutionLog.distance_saved_km).label('total_distance_saved'),
        func.sum(RuleExecutionLog.cost_saved).label('total_cost_saved')
    ).filter(
        RuleExecutionLog.rule_id == rule_id
    ).first()
    
    total = stats.total or 0
    success_count = stats.success_count or 0
    
    return {
        'rule_id': rule_id,
        'rule_name': rule.name,
        'total_executions': total,
        'success_count': success_count,
        'success_rate': (success_count / total * 100) if total > 0 else 0,
        'avg_execution_time_ms': round(stats.avg_time, 2) if stats.avg_time else 0,
        'total_distance_saved_km': round(stats.total_distance_saved, 2) if stats.total_distance_saved else 0,
        'total_cost_saved': round(stats.total_cost_saved, 2) if stats.total_cost_saved else 0
    }

@router.post("/simulate")
async def simulate_rules(
    test_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = None
):
    """
    규칙 시뮬레이션
    """
    engine = RuleEngine(db)
    result = engine.simulate_rules(test_data)
    
    return result

@router.post("/optimize-order/{order_id}")
async def optimize_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = None
):
    """
    주문에 최적 차량 찾기 (규칙 + 최적화)
    """
    engine = RuleEngine(db)
    result = engine.find_best_vehicle(order_id)
    
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    
    return result
