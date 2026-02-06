"""
배차 최적화 API
다중 차량 경로 최적화 REST 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models import User
from app.services.dispatch_optimization_service import (
    DispatchOptimizationService,
    OptimizationResult
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ========================================
# Pydantic 스키마
# ========================================

class OptimizationConstraints(BaseModel):
    """최적화 제약 조건"""
    max_vehicles: Optional[int] = Field(10, description="최대 사용 차량 수")
    max_route_time: Optional[int] = Field(480, description="최대 경로 시간 (분)")
    priority_orders: Optional[List[int]] = Field(default_factory=list, description="우선 처리 주문 ID")
    excluded_vehicles: Optional[List[int]] = Field(default_factory=list, description="제외 차량 ID")


class OptimizationOptions(BaseModel):
    """최적화 옵션"""
    use_traffic_data: bool = Field(True, description="실시간 교통 정보 사용")
    optimize_fuel: bool = Field(True, description="연료 최적화")
    balance_workload: bool = Field(True, description="업무량 균등 배분")


class OptimizeRequest(BaseModel):
    """배차 최적화 요청"""
    order_ids: List[int] = Field(..., description="배차할 주문 ID 리스트")
    date: str = Field(..., description="배차 날짜 (YYYY-MM-DD)")
    constraints: OptimizationConstraints = Field(default_factory=OptimizationConstraints)
    options: OptimizationOptions = Field(default_factory=OptimizationOptions)


class RouteSequencePoint(BaseModel):
    """경로 순서 지점"""
    type: str = Field(..., description="depot 또는 delivery")
    order_id: Optional[int] = None
    location: Dict[str, Any]
    arrival_time: str
    service_time: Optional[int] = None
    departure_time: str
    load_weight: Optional[float] = None
    load_pallets: Optional[int] = None


class RouteResponse(BaseModel):
    """경로 응답"""
    route_id: int
    vehicle_id: int
    driver_id: int
    orders: List[int]
    sequence: List[RouteSequencePoint]
    total_distance: float
    total_time: int
    total_load_weight: float
    total_load_pallets: int
    estimated_cost: float


class OptimizationSummary(BaseModel):
    """최적화 결과 요약"""
    total_vehicles: int
    total_orders: int
    unassigned_orders: int
    total_distance: float
    total_time: int
    empty_distance: float
    estimated_cost: int
    optimization_time: float
    improvement_vs_manual: Dict[str, float]


class OptimizationResponse(BaseModel):
    """최적화 응답"""
    optimization_id: str
    status: str
    summary: OptimizationSummary
    routes: List[RouteResponse]
    unassigned_orders: List[int]
    created_at: datetime


class ReOptimizeRequest(BaseModel):
    """재최적화 요청"""
    optimization_id: str
    reason: str = Field(..., description="재최적화 사유")
    changes: Dict[str, Any] = Field(..., description="변경 사항")


class ApproveRequest(BaseModel):
    """배차 승인 요청"""
    approved_by: int
    notes: Optional[str] = None


class DistanceMatrixRequest(BaseModel):
    """거리/시간 매트릭스 계산 요청"""
    origins: List[Dict[str, float]] = Field(..., description="출발지 좌표 리스트")
    destinations: List[Dict[str, float]] = Field(..., description="목적지 좌표 리스트")
    use_traffic: bool = Field(True, description="교통 정보 사용")


class DistanceMatrixResponse(BaseModel):
    """거리/시간 매트릭스 응답"""
    distance_matrix: List[List[float]] = Field(..., description="거리 행렬 (km)")
    time_matrix: List[List[int]] = Field(..., description="시간 행렬 (분)")


# ========================================
# API 엔드포인트
# ========================================

@router.post("/dispatch-optimization/optimize", response_model=OptimizationResponse)
async def optimize_dispatch(
    request: OptimizeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    배차 최적화 실행
    
    - **order_ids**: 배차할 주문 ID 리스트
    - **date**: 배차 날짜
    - **constraints**: 제약 조건 (최대 차량 수, 경로 시간 등)
    - **options**: 최적화 옵션 (교통 정보, 연료 최적화 등)
    
    Returns:
        최적화된 배차 결과 (경로, 요약 통계)
    """
    try:
        logger.info(f"배차 최적화 시작: 사용자={current_user.username}, 주문={len(request.order_ids)}개")
        
        # 서비스 초기화
        service = DispatchOptimizationService(db)
        
        # 최적화 실행
        result = service.optimize_dispatch(
            order_ids=request.order_ids,
            date=request.date,
            constraints=request.constraints.dict(),
            options=request.options.dict()
        )
        
        # 응답 생성
        response = OptimizationResponse(
            optimization_id=result.optimization_id,
            status=result.status,
            summary=OptimizationSummary(**result.summary),
            routes=[
                RouteResponse(
                    route_id=route.route_id,
                    vehicle_id=route.vehicle_id,
                    driver_id=route.driver_id,
                    orders=route.orders,
                    sequence=[RouteSequencePoint(**point) for point in route.sequence],
                    total_distance=route.total_distance,
                    total_time=route.total_time,
                    total_load_weight=route.total_load_weight,
                    total_load_pallets=route.total_load_pallets,
                    estimated_cost=route.estimated_cost
                )
                for route in result.routes
            ],
            unassigned_orders=result.unassigned_orders,
            created_at=result.created_at
        )
        
        logger.info(f"최적화 완료: {result.optimization_id}, {len(result.routes)}개 경로")
        
        return response
        
    except Exception as e:
        logger.error(f"배차 최적화 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"최적화 실패: {str(e)}")


@router.get("/dispatch-optimization/status/{optimization_id}")
async def get_optimization_status(
    optimization_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    최적화 상태 조회
    
    - **optimization_id**: 최적화 ID
    
    Returns:
        최적화 상태 및 진행률
    """
    try:
        # TODO: 데이터베이스에서 최적화 상태 조회
        return {
            "optimization_id": optimization_id,
            "status": "completed",
            "progress": 100,
            "message": "최적화 완료"
        }
        
    except Exception as e:
        logger.error(f"최적화 상태 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dispatch-optimization/re-optimize")
async def re_optimize_dispatch(
    request: ReOptimizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    실시간 재최적화
    
    - **optimization_id**: 기존 최적화 ID
    - **reason**: 재최적화 사유
    - **changes**: 변경 사항 (신규 주문, 취소 주문, 불가 차량 등)
    
    Returns:
        재최적화된 배차 결과
    """
    try:
        logger.info(f"재최적화 시작: {request.optimization_id}, 사유={request.reason}")
        
        # TODO: 재최적화 로직 구현
        # 1. 기존 최적화 결과 로드
        # 2. 변경 사항 반영
        # 3. 부분 재최적화 실행
        # 4. 결과 반환
        
        return {
            "optimization_id": f"{request.optimization_id}-RE",
            "status": "completed",
            "reason": request.reason,
            "message": "재최적화 완료"
        }
        
    except Exception as e:
        logger.error(f"재최적화 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dispatch-optimization/{optimization_id}/approve")
async def approve_optimization(
    optimization_id: str,
    request: ApproveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    배차 결과 승인 및 적용
    
    - **optimization_id**: 최적화 ID
    - **approved_by**: 승인자 ID
    - **notes**: 승인 메모
    
    Returns:
        승인 결과
    """
    try:
        logger.info(f"배차 승인: {optimization_id}, 승인자={request.approved_by}")
        
        # TODO: 배차 승인 로직
        # 1. 최적화 결과 로드
        # 2. Dispatch 레코드 생성
        # 3. 차량 및 운전자 상태 업데이트
        # 4. 주문 상태 업데이트
        
        return {
            "optimization_id": optimization_id,
            "status": "approved",
            "approved_at": datetime.now(),
            "approved_by": request.approved_by,
            "message": "배차가 승인되었습니다"
        }
        
    except Exception as e:
        logger.error(f"배차 승인 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dispatch-optimization/history")
async def get_optimization_history(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    최적화 이력 조회
    
    - **date_from**: 시작 날짜
    - **date_to**: 종료 날짜
    - **limit**: 최대 결과 수
    
    Returns:
        최적화 이력 리스트
    """
    try:
        # TODO: 데이터베이스에서 이력 조회
        history = [
            {
                "optimization_id": f"OPT-2026-02-05-{i:04d}",
                "date": "2026-02-05",
                "total_orders": 45 - i,
                "total_vehicles": 8,
                "total_distance": 450.5,
                "status": "approved",
                "created_at": datetime.now()
            }
            for i in range(min(limit, 10))
        ]
        
        return {
            "history": history,
            "total": len(history)
        }
        
    except Exception as e:
        logger.error(f"이력 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dispatch-optimization/performance")
async def get_optimization_performance(
    optimization_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    최적화 성과 분석
    
    - **optimization_id**: 최적화 ID
    
    Returns:
        성과 비교 데이터 (수동 vs AI 최적화)
    """
    try:
        # TODO: 실제 성과 데이터 계산
        performance = {
            "optimization_id": optimization_id,
            "comparison": {
                "manual_dispatch": {
                    "total_distance": 630.5,
                    "total_time": 590,
                    "total_cost": 287000,
                    "vehicles_used": 10
                },
                "ai_optimization": {
                    "total_distance": 450.5,
                    "total_time": 385,
                    "total_cost": 245000,
                    "vehicles_used": 8
                },
                "improvement": {
                    "distance_percent": -28.5,
                    "time_percent": -34.7,
                    "cost_saved": 42000,
                    "vehicles_saved": 2
                }
            },
            "metrics": {
                "optimization_time": 2.5,
                "orders_assigned": 45,
                "orders_unassigned": 0,
                "average_route_distance": 56.3,
                "average_route_time": 48
            }
        }
        
        return performance
        
    except Exception as e:
        logger.error(f"성과 분석 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dispatch-optimization/distance-matrix", response_model=DistanceMatrixResponse)
async def calculate_distance_matrix(
    request: DistanceMatrixRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    거리 및 시간 매트릭스 계산
    
    - **origins**: 출발지 좌표 리스트
    - **destinations**: 목적지 좌표 리스트
    - **use_traffic**: 실시간 교통 정보 사용 여부
    
    Returns:
        거리 행렬 및 시간 행렬
    """
    try:
        service = DispatchOptimizationService(db)
        
        # 간단한 거리 계산 (Haversine)
        n_origins = len(request.origins)
        n_destinations = len(request.destinations)
        
        distance_matrix = []
        time_matrix = []
        
        for origin in request.origins:
            distances = []
            times = []
            
            for destination in request.destinations:
                dist = service._haversine_distance(
                    origin['lat'],
                    origin['lng'],
                    destination['lat'],
                    destination['lng']
                )
                distances.append(round(dist, 2))
                
                # 시간 계산 (평균 속도 40km/h)
                time_minutes = int((dist / 40.0) * 60)
                if request.use_traffic:
                    time_minutes = int(time_minutes * 1.2)  # 교통 반영
                times.append(time_minutes)
            
            distance_matrix.append(distances)
            time_matrix.append(times)
        
        return DistanceMatrixResponse(
            distance_matrix=distance_matrix,
            time_matrix=time_matrix
        )
        
    except Exception as e:
        logger.error(f"매트릭스 계산 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dispatch-optimization/simulate")
async def simulate_scenarios(
    scenarios: List[Dict[str, Any]],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    제약 조건 시뮬레이션
    
    - **scenarios**: 시나리오 리스트 (각 시나리오는 제약 조건 포함)
    
    Returns:
        각 시나리오별 최적화 결과 비교
    """
    try:
        logger.info(f"시나리오 시뮬레이션: {len(scenarios)}개")
        
        # TODO: 각 시나리오별 최적화 실행
        results = [
            {
                "scenario_id": i + 1,
                "constraints": scenario,
                "result": {
                    "total_vehicles": scenario.get('max_vehicles', 10),
                    "total_distance": 450.5 + i * 20,
                    "total_cost": 245000 + i * 15000,
                    "feasible": True
                }
            }
            for i, scenario in enumerate(scenarios)
        ]
        
        return {
            "scenarios": results,
            "recommendation": "시나리오 1 (최소 비용)"
        }
        
    except Exception as e:
        logger.error(f"시뮬레이션 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
