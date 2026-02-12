"""
Simulation API Endpoints
시뮬레이션 관련 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.simulation import RuleSimulation, SimulationComparison, SimulationTemplate
from app.models.dispatch_rule import DispatchRule
from app.services.simulation_engine import SimulationEngine, compare_simulations
from pydantic import BaseModel, Field


router = APIRouter()


# Pydantic 스키마
class SimulationCreate(BaseModel):
    """시뮬레이션 생성 요청"""
    name: str = Field(..., description="시뮬레이션 이름")
    description: Optional[str] = Field(None, description="시뮬레이션 설명")
    rule_id: Optional[int] = Field(None, description="테스트할 규칙 ID (없으면 임시 규칙 사용)")
    rule_config: dict = Field(..., description="규칙 설정")
    scenario_data: dict = Field(..., description="테스트 시나리오 데이터")
    scenario_type: str = Field("custom", description="시나리오 타입")
    iterations: int = Field(1, ge=1, le=100, description="반복 횟수")
    randomize_data: bool = Field(False, description="데이터 랜덤화 여부")
    created_by: Optional[str] = Field(None, description="생성자")


class SimulationResponse(BaseModel):
    """시뮬레이션 응답"""
    id: int
    name: str
    description: Optional[str]
    rule_id: Optional[int]
    status: str
    match_rate: Optional[float]
    avg_response_time_ms: Optional[float]
    estimated_cost: Optional[float]
    estimated_distance_km: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class SimulationDetailResponse(SimulationResponse):
    """시뮬레이션 상세 응답"""
    rule_config: dict
    scenario_data: dict
    iterations: int
    total_matches: Optional[int]
    successful_matches: Optional[int]
    failed_matches: Optional[int]
    min_response_time_ms: Optional[float]
    max_response_time_ms: Optional[float]
    estimated_time_minutes: Optional[float]
    results: Optional[dict]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]


class ComparisonCreate(BaseModel):
    """비교 테스트 생성 요청"""
    name: str = Field(..., description="비교 테스트 이름")
    description: Optional[str] = Field(None, description="설명")
    simulation_a_id: int = Field(..., description="시뮬레이션 A ID")
    simulation_b_id: int = Field(..., description="시뮬레이션 B ID")


class ComparisonResponse(BaseModel):
    """비교 테스트 응답"""
    id: int
    name: str
    simulation_a_id: int
    simulation_b_id: int
    winner: Optional[str]
    recommendation: Optional[str]
    confidence_score: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TemplateResponse(BaseModel):
    """템플릿 응답"""
    id: int
    name: str
    description: Optional[str]
    category: Optional[str]
    difficulty: str
    complexity_score: Optional[float]
    usage_count: int
    avg_success_rate: Optional[float]
    
    class Config:
        from_attributes = True


# API 엔드포인트
@router.post("/simulations", response_model=SimulationDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_simulation(
    simulation: SimulationCreate,
    db: Session = Depends(get_db)
):
    """
    새로운 시뮬레이션 생성 및 실행
    """
    # 규칙 ID가 제공된 경우 규칙 존재 확인
    if simulation.rule_id:
        rule = db.query(DispatchRule).filter(DispatchRule.id == simulation.rule_id).first()
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule {simulation.rule_id} not found"
            )
    
    # 시뮬레이션 생성
    db_simulation = RuleSimulation(
        name=simulation.name,
        description=simulation.description,
        rule_id=simulation.rule_id,
        rule_config=simulation.rule_config,
        scenario_data=simulation.scenario_data,
        scenario_type=simulation.scenario_type,
        iterations=simulation.iterations,
        randomize_data=simulation.randomize_data,
        created_by=simulation.created_by,
        status="pending"
    )
    
    db.add(db_simulation)
    db.commit()
    db.refresh(db_simulation)
    
    # 시뮬레이션 실행
    try:
        engine = SimulationEngine(db)
        await engine.run_simulation(
            simulation_id=db_simulation.id,
            rule_config=simulation.rule_config,
            scenario_data=simulation.scenario_data,
            iterations=simulation.iterations,
            randomize=simulation.randomize_data
        )
        
        # 최신 상태 조회
        db.refresh(db_simulation)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation execution failed: {str(e)}"
        )
    
    return db_simulation


@router.get("/simulations", response_model=List[SimulationResponse])
def list_simulations(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    rule_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    시뮬레이션 목록 조회
    """
    query = db.query(RuleSimulation)
    
    if status:
        query = query.filter(RuleSimulation.status == status)
    
    if rule_id:
        query = query.filter(RuleSimulation.rule_id == rule_id)
    
    simulations = query.order_by(RuleSimulation.created_at.desc()).offset(skip).limit(limit).all()
    
    return simulations


@router.get("/simulations/{simulation_id}", response_model=SimulationDetailResponse)
def get_simulation(
    simulation_id: int,
    db: Session = Depends(get_db)
):
    """
    시뮬레이션 상세 조회
    """
    simulation = db.query(RuleSimulation).filter(RuleSimulation.id == simulation_id).first()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation {simulation_id} not found"
        )
    
    return simulation


@router.delete("/simulations/{simulation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_simulation(
    simulation_id: int,
    db: Session = Depends(get_db)
):
    """
    시뮬레이션 삭제
    """
    simulation = db.query(RuleSimulation).filter(RuleSimulation.id == simulation_id).first()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation {simulation_id} not found"
        )
    
    db.delete(simulation)
    db.commit()
    
    return None


@router.post("/simulations/compare", response_model=dict)
async def compare_two_simulations(
    comparison: ComparisonCreate,
    db: Session = Depends(get_db)
):
    """
    두 시뮬레이션 비교
    """
    # 시뮬레이션 존재 확인
    sim_a = db.query(RuleSimulation).filter(RuleSimulation.id == comparison.simulation_a_id).first()
    sim_b = db.query(RuleSimulation).filter(RuleSimulation.id == comparison.simulation_b_id).first()
    
    if not sim_a or not sim_b:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both simulations not found"
        )
    
    # 비교 실행
    try:
        result = await compare_simulations(db, comparison.simulation_a_id, comparison.simulation_b_id)
        
        # 비교 결과 저장
        db_comparison = SimulationComparison(
            name=comparison.name,
            description=comparison.description,
            simulation_a_id=comparison.simulation_a_id,
            simulation_b_id=comparison.simulation_b_id,
            winner=result["overall_winner"],
            comparison_metrics=result["metrics"],
            recommendation=result["recommendation"],
            confidence_score=result["confidence_score"]
        )
        
        db.add(db_comparison)
        db.commit()
        db.refresh(db_comparison)
        
        result["comparison_id"] = db_comparison.id
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comparison failed: {str(e)}"
        )


@router.get("/simulations/comparisons", response_model=List[ComparisonResponse])
def list_comparisons(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    비교 테스트 목록 조회
    """
    comparisons = db.query(SimulationComparison)\
        .order_by(SimulationComparison.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return comparisons


@router.get("/templates", response_model=List[TemplateResponse])
def list_templates(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    시뮬레이션 템플릿 목록 조회
    """
    query = db.query(SimulationTemplate).filter(SimulationTemplate.is_active == True)
    
    if category:
        query = query.filter(SimulationTemplate.category == category)
    
    if difficulty:
        query = query.filter(SimulationTemplate.difficulty == difficulty)
    
    templates = query.order_by(SimulationTemplate.usage_count.desc()).all()
    
    return templates


@router.get("/templates/{template_id}", response_model=dict)
def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """
    템플릿 상세 조회 (시나리오 데이터 포함)
    """
    template = db.query(SimulationTemplate).filter(
        SimulationTemplate.id == template_id,
        SimulationTemplate.is_active == True
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found"
        )
    
    # 사용 횟수 증가
    template.usage_count += 1
    db.commit()
    
    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "category": template.category,
        "difficulty": template.difficulty,
        "complexity_score": template.complexity_score,
        "scenario_data": template.scenario_data,
        "expected_results": template.expected_results,
        "usage_count": template.usage_count,
        "avg_success_rate": template.avg_success_rate
    }


@router.get("/statistics/summary", response_model=dict)
def get_simulation_statistics(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    시뮬레이션 통계 요약
    """
    from datetime import timedelta
    
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # 총 시뮬레이션 수
    total_simulations = db.query(func.count(RuleSimulation.id))\
        .filter(RuleSimulation.created_at >= since_date)\
        .scalar()
    
    # 완료된 시뮬레이션 수
    completed_simulations = db.query(func.count(RuleSimulation.id))\
        .filter(
            RuleSimulation.created_at >= since_date,
            RuleSimulation.status == "completed"
        )\
        .scalar()
    
    # 평균 매칭률
    avg_match_rate = db.query(func.avg(RuleSimulation.match_rate))\
        .filter(
            RuleSimulation.created_at >= since_date,
            RuleSimulation.status == "completed"
        )\
        .scalar()
    
    # 평균 응답 시간
    avg_response_time = db.query(func.avg(RuleSimulation.avg_response_time_ms))\
        .filter(
            RuleSimulation.created_at >= since_date,
            RuleSimulation.status == "completed"
        )\
        .scalar()
    
    return {
        "period_days": days,
        "total_simulations": total_simulations or 0,
        "completed_simulations": completed_simulations or 0,
        "avg_match_rate": round(float(avg_match_rate or 0), 2),
        "avg_response_time_ms": round(float(avg_response_time or 0), 2)
    }
