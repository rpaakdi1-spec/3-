"""
실시간 교통 정보 API

네이버/카카오 교통 API 연동 엔드포인트:
- 실시간 경로 탐색
- 교통 상황 조회
- 예상 도착 시간 계산
- 최적 경로 순서
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.services.traffic_service import TrafficService, TrafficProvider, RouteOption
from datetime import datetime

router = APIRouter()


class LocationPoint(BaseModel):
    """위치 좌표"""
    latitude: float = Field(..., description="위도")
    longitude: float = Field(..., description="경도")


class RouteRequest(BaseModel):
    """경로 탐색 요청"""
    start: LocationPoint = Field(..., description="출발지")
    end: LocationPoint = Field(..., description="도착지")
    waypoints: Optional[List[LocationPoint]] = Field(None, description="경유지 목록")
    provider: Optional[TrafficProvider] = Field(TrafficProvider.NAVER, description="교통 정보 제공자")
    option: Optional[RouteOption] = Field(RouteOption.TRAFAST, description="경로 옵션")


class RouteResponse(BaseModel):
    """경로 탐색 응답"""
    provider: str
    distance_km: float
    duration_minutes: float
    duration_with_traffic_minutes: float
    traffic_info: Optional[dict] = None
    path_coordinates: Optional[List[dict]] = None
    fuel_cost: Optional[float] = None
    toll_cost: Optional[float] = None
    retrieved_at: str


class ArrivalEstimateRequest(BaseModel):
    """도착 시간 예측 요청"""
    current_location: LocationPoint = Field(..., description="현재 위치")
    destination: LocationPoint = Field(..., description="목적지")
    departure_time: Optional[str] = Field(None, description="출발 시간 (ISO 8601)")


class ArrivalEstimateResponse(BaseModel):
    """도착 시간 예측 응답"""
    departure_time: str
    estimated_arrival_time: str
    early_arrival_time: str
    late_arrival_time: str
    duration_minutes: float
    distance_km: float
    traffic_info: Optional[dict] = None
    confidence: str
    updated_at: str


@router.post(
    "/route",
    response_model=RouteResponse,
    summary="실시간 경로 탐색",
    description="네이버/카카오 API를 사용하여 실시간 교통 정보를 반영한 경로를 탐색합니다"
)
async def get_route_with_traffic(
    request: RouteRequest,
    db: Session = Depends(get_db)
):
    """
    실시간 경로 탐색
    
    - 네이버 또는 카카오 API 선택 가능
    - 실시간 교통 상황 반영
    - 거리, 시간, 요금 정보 제공
    - 경로 좌표 제공 (지도 표시용)
    
    **경로 옵션 (네이버):**
    - trafast: 실시간 빠른길 (기본)
    - tracomfort: 실시간 편한길
    - traoptimal: 실시간 최적
    - traavoidtoll: 무료 우선
    - traavoidcaronly: 자동차 전용도로 회피
    """
    service = TrafficService()
    
    waypoints = None
    if request.waypoints:
        waypoints = [(wp.latitude, wp.longitude) for wp in request.waypoints]
    
    try:
        route = service.get_route_with_traffic(
            start_lat=request.start.latitude,
            start_lon=request.start.longitude,
            end_lat=request.end.latitude,
            end_lon=request.end.longitude,
            waypoints=waypoints,
            provider=request.provider,
            option=request.option
        )
        
        return route
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"경로 탐색 실패: {str(e)}"
        )


@router.get(
    "/route/simple",
    response_model=RouteResponse,
    summary="간단 경로 탐색",
    description="쿼리 파라미터로 간단하게 경로를 탐색합니다"
)
async def get_simple_route(
    start_lat: float = Query(..., description="출발지 위도"),
    start_lon: float = Query(..., description="출발지 경도"),
    end_lat: float = Query(..., description="도착지 위도"),
    end_lon: float = Query(..., description="도착지 경도"),
    provider: TrafficProvider = Query(TrafficProvider.NAVER, description="교통 정보 제공자"),
    option: RouteOption = Query(RouteOption.TRAFAST, description="경로 옵션"),
    db: Session = Depends(get_db)
):
    """
    간단 경로 탐색 (쿼리 파라미터)
    
    - GET 요청으로 간단하게 경로 조회
    - 출발지와 도착지만 지정
    - 기본 옵션: 네이버 API, 실시간 빠른길
    """
    service = TrafficService()
    
    try:
        route = service.get_route_with_traffic(
            start_lat=start_lat,
            start_lon=start_lon,
            end_lat=end_lat,
            end_lon=end_lon,
            provider=provider,
            option=option
        )
        
        return route
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"경로 탐색 실패: {str(e)}"
        )


@router.post(
    "/arrival-estimate",
    response_model=ArrivalEstimateResponse,
    summary="예상 도착 시간 계산",
    description="실시간 교통 정보를 기반으로 예상 도착 시간을 계산합니다"
)
async def estimate_arrival_time(
    request: ArrivalEstimateRequest,
    db: Session = Depends(get_db)
):
    """
    예상 도착 시간 계산
    
    - 현재 위치에서 목적지까지 소요 시간 계산
    - 실시간 교통 상황 반영
    - 신뢰 구간 제공 (빠른 경우, 늦은 경우)
    - 출발 시간 지정 가능
    
    **활용 사례:**
    - 고객에게 배송 예상 시간 안내
    - 배차 계획 수립
    - 실시간 도착 시간 업데이트
    """
    service = TrafficService()
    
    departure_time = None
    if request.departure_time:
        try:
            departure_time = datetime.fromisoformat(request.departure_time)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="잘못된 날짜 형식입니다. ISO 8601 형식을 사용하세요."
            )
    
    try:
        estimate = service.estimate_arrival_time(
            current_lat=request.current_location.latitude,
            current_lon=request.current_location.longitude,
            destination_lat=request.destination.latitude,
            destination_lon=request.destination.longitude,
            departure_time=departure_time
        )
        
        return estimate
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"도착 시간 예측 실패: {str(e)}"
        )


@router.get(
    "/arrival-estimate/simple",
    summary="간단 도착 시간 예측",
    description="쿼리 파라미터로 간단하게 도착 시간을 예측합니다"
)
async def estimate_simple_arrival(
    current_lat: float = Query(..., description="현재 위도"),
    current_lon: float = Query(..., description="현재 경도"),
    dest_lat: float = Query(..., description="목적지 위도"),
    dest_lon: float = Query(..., description="목적지 경도"),
    db: Session = Depends(get_db)
):
    """
    간단 도착 시간 예측 (쿼리 파라미터)
    
    - GET 요청으로 간단하게 도착 시간 예측
    - 현재 시간 기준으로 계산
    """
    service = TrafficService()
    
    try:
        estimate = service.estimate_arrival_time(
            current_lat=current_lat,
            current_lon=current_lon,
            destination_lat=dest_lat,
            destination_lon=dest_lon
        )
        
        return estimate
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"도착 시간 예측 실패: {str(e)}"
        )


@router.get(
    "/traffic/test",
    summary="교통 정보 API 테스트",
    description="네이버/카카오 API 연결을 테스트합니다"
)
async def test_traffic_api(
    provider: TrafficProvider = Query(TrafficProvider.NAVER, description="테스트할 제공자"),
    db: Session = Depends(get_db)
):
    """
    교통 정보 API 연결 테스트
    
    - API 키 설정 확인
    - 샘플 경로로 연결 테스트
    - 응답 시간 측정
    
    **테스트 경로:**
    - 출발: 서울시청 (37.5665, 126.9780)
    - 도착: 판교역 (37.3951, 127.1113)
    """
    service = TrafficService()
    
    # 서울시청 -> 판교역
    start_lat, start_lon = 37.5665, 126.9780
    end_lat, end_lon = 37.3951, 127.1113
    
    start_time = datetime.now()
    
    try:
        route = service.get_route_with_traffic(
            start_lat=start_lat,
            start_lon=start_lon,
            end_lat=end_lat,
            end_lon=end_lon,
            provider=provider
        )
        
        end_time = datetime.now()
        response_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # API 키 설정 확인
        if provider == TrafficProvider.NAVER:
            api_configured = bool(service.naver_client_id and service.naver_client_secret)
        else:
            api_configured = bool(service.kakao_rest_api_key)
        
        return {
            "status": "success" if route["provider"] != "fallback" else "fallback",
            "provider": provider.value,
            "api_configured": api_configured,
            "response_time_ms": round(response_time_ms, 2),
            "test_route": {
                "from": "서울시청",
                "to": "판교역",
                "distance_km": route["distance_km"],
                "duration_minutes": route["duration_with_traffic_minutes"]
            },
            "message": "API 연결 성공!" if route["provider"] != "fallback" else "API 키가 설정되지 않았거나 연결 실패. Fallback 사용 중."
        }
        
    except Exception as e:
        return {
            "status": "error",
            "provider": provider.value,
            "api_configured": False,
            "error": str(e),
            "message": "API 연결 실패"
        }


@router.get(
    "/traffic/compare",
    summary="경로 비교",
    description="네이버와 카카오 API 결과를 비교합니다"
)
async def compare_routes(
    start_lat: float = Query(..., description="출발지 위도"),
    start_lon: float = Query(..., description="출발지 경도"),
    end_lat: float = Query(..., description="도착지 위도"),
    end_lon: float = Query(..., description="도착지 경도"),
    db: Session = Depends(get_db)
):
    """
    경로 비교 (네이버 vs 카카오)
    
    - 두 API의 결과를 동시에 조회
    - 거리, 시간, 비용 비교
    - 최적 경로 추천
    """
    service = TrafficService()
    
    results = {}
    
    # 네이버 API
    try:
        naver_route = service.get_route_with_traffic(
            start_lat=start_lat,
            start_lon=start_lon,
            end_lat=end_lat,
            end_lon=end_lon,
            provider=TrafficProvider.NAVER
        )
        results["naver"] = naver_route
    except Exception as e:
        results["naver"] = {"error": str(e)}
    
    # 카카오 API
    try:
        kakao_route = service.get_route_with_traffic(
            start_lat=start_lat,
            start_lon=start_lon,
            end_lat=end_lat,
            end_lon=end_lon,
            provider=TrafficProvider.KAKAO
        )
        results["kakao"] = kakao_route
    except Exception as e:
        results["kakao"] = {"error": str(e)}
    
    # 비교 분석
    comparison = {
        "recommendation": None,
        "reason": None
    }
    
    if "error" not in results["naver"] and "error" not in results["kakao"]:
        naver_time = results["naver"]["duration_with_traffic_minutes"]
        kakao_time = results["kakao"]["duration_with_traffic_minutes"]
        
        if naver_time < kakao_time:
            comparison["recommendation"] = "naver"
            comparison["reason"] = f"네이버가 {round(kakao_time - naver_time, 1)}분 더 빠릅니다"
        elif kakao_time < naver_time:
            comparison["recommendation"] = "kakao"
            comparison["reason"] = f"카카오가 {round(naver_time - kakao_time, 1)}분 더 빠릅니다"
        else:
            comparison["recommendation"] = "both"
            comparison["reason"] = "두 경로의 소요 시간이 비슷합니다"
    
    return {
        "routes": results,
        "comparison": comparison
    }
