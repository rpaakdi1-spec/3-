"""
Dispatch Rules API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.models.dispatch_rule import DispatchRule, RuleExecutionLog
from app.services.rule_engine import RuleEngine
from app.services.rule_parser import RuleParser

logger = logging.getLogger(__name__)
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
    rule_type: Optional[str] = Field(None, pattern="^(assignment|constraint|optimization)$")
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

@router.get("/conflicts")
async def detect_rule_conflicts(
    db: Session = Depends(get_db),
):
    """
    규칙 충돌 감지
    
    활성화된 모든 규칙을 분석하여 충돌 가능성을 감지합니다.
    """
    try:
        # 활성 규칙만 조회
        rules = db.query(DispatchRule).filter(
            DispatchRule.is_active == True
        ).all()
        
        # 규칙을 dict로 변환
        rules_dict = [
            {
                'id': rule.id,
                'name': rule.name,
                'is_active': rule.is_active,
                'priority': rule.priority,
                'conditions': rule.conditions or {},
                'actions': rule.actions or {},
            }
            for rule in rules
        ]
        
        # 충돌 감지 (간단한 로직)
        conflicts = []
        
        # 우선순위 충돌 검사
        priority_groups = {}
        for rule in rules_dict:
            priority = rule['priority']
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(rule)
        
        for priority, group in priority_groups.items():
            if len(group) > 1:
                # 동일 우선순위 규칙들끼리 조건 유사도 검사
                for i, rule1 in enumerate(group):
                    for rule2 in group[i+1:]:
                        cond1_keys = set(rule1['conditions'].keys())
                        cond2_keys = set(rule2['conditions'].keys())
                        
                        if cond1_keys & cond2_keys:  # 조건 키가 겹치면
                            conflicts.append({
                                'rule1_id': rule1['id'],
                                'rule1_name': rule1['name'],
                                'rule2_id': rule2['id'],
                                'rule2_name': rule2['name'],
                                'type': 'priority_conflict',
                                'type_name': '우선순위 충돌',
                                'description': f"규칙 '{rule1['name']}'와 '{rule2['name']}'이(가) 동일한 우선순위({priority})를 가지며 조건이 유사합니다.",
                                'severity': 'medium',
                                'recommendation': f"우선순위를 다르게 설정하거나 조건을 명확히 구분하세요."
                            })
        
        return {
            'total_conflicts': len(conflicts),
            'by_severity': {
                'high': len([c for c in conflicts if c.get('severity') == 'high']),
                'medium': len([c for c in conflicts if c.get('severity') == 'medium']),
                'low': len([c for c in conflicts if c.get('severity') == 'low']),
            },
            'conflicts': conflicts
        }
    
    except Exception as e:
        logger.error(f"Conflict detection failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect conflicts: {str(e)}"
        )

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
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = None
):
    """
    배차 규칙 수정
    """
    # Parse request body directly to avoid FastAPI parameter name conflicts
    update_data = await request.json()
    
    logger.info(f"Update request for rule {rule_id}: {update_data}")
    
    db_rule = db.query(DispatchRule).filter(DispatchRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # 버전 증가
    db_rule.version += 1
    
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
    
    logger.info(f"Successfully updated rule {rule_id}, new version: {db_rule.version}")
    return db_rule

@router.delete("/{rule_id}", status_code=204)
async def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = None
):
    """
    배차 규칙 삭제 (hard delete)
    """
    db_rule = db.query(DispatchRule).filter(DispatchRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Hard delete: 규칙과 관련된 로그도 함께 삭제
    db.query(RuleExecutionLog).filter(RuleExecutionLog.rule_id == rule_id).delete()
    db.delete(db_rule)
    db.commit()
    
    logger.info(f"Successfully deleted rule {rule_id}")
    return

@router.post("/{rule_id}/test")
async def test_rule(
    rule_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = None
):
    """
    규칙 테스트 (dry run)
    
    Request body: { "test_data": { ... } }
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Parse request body
    request_body = await request.json()
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

# ============ AI Rule Generation ============

class RuleGenerateRequest(BaseModel):
    """AI 규칙 생성 요청"""
    name: str = Field(..., min_length=1, max_length=200, description="규칙 이름")
    description: str = Field(default="", max_length=1000, description="규칙 설명")
    rule_type: str = Field(default="assignment", pattern="^(assignment|constraint|optimization)$")

@router.post("/generate-ai", summary="AI로 규칙 자동 생성")
async def generate_rule_with_ai(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = None
):
    """
    AI를 사용하여 규칙 이름과 설명으로부터 conditions와 actions 자동 생성
    
    Example:
        POST /api/v1/dispatch-rules/generate-ai
        {
            "name": "지게차가능거래처 -> 지게차가능기사로 배차",
            "description": "지게차운전필요한거래처 -> 지게차 운전 가능한 기사로 배차",
            "rule_type": "assignment"
        }
    
    Returns:
        {
            "conditions": {...},
            "actions": {...},
            "confidence": 0.85,
            "reasoning": "..."
        }
    """
    from app.services.rule_ai_generator import RuleAIGenerator
    
    try:
        # Parse request body
        data = await request.json()
        logger.info(f"AI generation request: {data}")
        
        # Validate required fields
        name = data.get("name")
        if not name or len(name) == 0:
            raise HTTPException(status_code=400, detail="name is required")
        
        description = data.get("description", "")
        rule_type = data.get("rule_type", "assignment")
        
        # Validate rule_type
        if rule_type not in ["assignment", "constraint", "optimization"]:
            raise HTTPException(status_code=400, detail="rule_type must be assignment, constraint, or optimization")
        
        generator = RuleAIGenerator()
        result = await generator.generate_rule(
            name=name,
            description=description,
            rule_type=rule_type
        )
        
        logger.info(f"AI generation result: {result}")
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI rule generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate rule: {str(e)}"
        )


