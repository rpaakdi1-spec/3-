"""
ETA (Estimated Time of Arrival) 예측 서비스
- 배차 경로 기반 예상 도착 시간 계산
- 실시간 교통 정보 반영 (선택적)
- 적재/하역 시간 포함
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class LocationStop:
    """경유지 정보"""
    location_id: int
    location_type: str  # 'depot', 'pickup', 'delivery'
    latitude: float
    longitude: float
    service_time_minutes: int  # 적재/하역 시간
    time_window_start: Optional[str] = None  # HH:MM
    time_window_end: Optional[str] = None  # HH:MM


@dataclass
class ETAResult:
    """ETA 계산 결과"""
    location_id: int
    location_type: str
    estimated_arrival_time: datetime
    estimated_departure_time: datetime
    cumulative_distance_km: float
    cumulative_duration_minutes: float
    is_within_time_window: bool
    time_window_violation_minutes: float = 0.0


class ETAService:
    """ETA 예측 서비스"""
    
    # 기본 설정
    DEFAULT_SPEED_KMH = 40  # 도심 평균 속도
    HIGHWAY_SPEED_KMH = 80  # 고속도로 속도
    TRAFFIC_FACTOR = 1.2  # 교통 혼잡도 계수 (1.0 = 정상, 1.5 = 혼잡)
    
    def __init__(self, average_speed_kmh: float = DEFAULT_SPEED_KMH, traffic_factor: float = TRAFFIC_FACTOR):
        """
        Args:
            average_speed_kmh: 평균 속도 (km/h)
            traffic_factor: 교통 혼잡도 계수
        """
        self.average_speed_kmh = average_speed_kmh
        self.traffic_factor = traffic_factor
    
    def calculate_eta(
        self,
        start_time: datetime,
        route_stops: List[LocationStop],
        distance_matrix_km: List[List[float]]
    ) -> List[ETAResult]:
        """
        경로의 ETA 계산
        
        Args:
            start_time: 출발 시간
            route_stops: 경유지 리스트 (순서대로)
            distance_matrix_km: 거리 행렬 (km)
            
        Returns:
            각 경유지별 ETA 결과
        """
        results = []
        current_time = start_time
        cumulative_distance = 0.0
        cumulative_duration = 0.0
        
        for i, stop in enumerate(route_stops):
            # 이전 경유지와의 거리 및 이동 시간 계산
            if i > 0:
                distance_km = distance_matrix_km[i-1][i]
                travel_time_minutes = self._calculate_travel_time(distance_km)
                
                current_time += timedelta(minutes=travel_time_minutes)
                cumulative_distance += distance_km
                cumulative_duration += travel_time_minutes
            
            # 도착 시간
            arrival_time = current_time
            
            # Time Window 검증
            is_within_tw, violation_minutes = self._check_time_window(
                arrival_time, 
                stop.time_window_start, 
                stop.time_window_end
            )
            
            # Time Window 위반 시 대기
            if stop.time_window_start and arrival_time.time() < self._parse_time(stop.time_window_start):
                tw_start = datetime.combine(arrival_time.date(), self._parse_time(stop.time_window_start))
                wait_time_minutes = (tw_start - arrival_time).total_seconds() / 60
                current_time = tw_start
                cumulative_duration += wait_time_minutes
                arrival_time = tw_start
                is_within_tw = True
                violation_minutes = 0.0
            
            # 출발 시간 (도착 + 작업 시간)
            departure_time = current_time + timedelta(minutes=stop.service_time_minutes)
            cumulative_duration += stop.service_time_minutes
            
            # 결과 저장
            result = ETAResult(
                location_id=stop.location_id,
                location_type=stop.location_type,
                estimated_arrival_time=arrival_time,
                estimated_departure_time=departure_time,
                cumulative_distance_km=cumulative_distance,
                cumulative_duration_minutes=cumulative_duration,
                is_within_time_window=is_within_tw,
                time_window_violation_minutes=violation_minutes
            )
            results.append(result)
            
            # 다음 경유지 준비
            current_time = departure_time
        
        return results
    
    def estimate_delivery_time(
        self,
        current_location: LocationStop,
        destination: LocationStop,
        distance_km: float,
        current_time: Optional[datetime] = None
    ) -> datetime:
        """
        단일 배송 ETA 계산
        
        Args:
            current_location: 현재 위치
            destination: 목적지
            distance_km: 거리
            current_time: 현재 시간 (기본값: 지금)
            
        Returns:
            예상 도착 시간
        """
        if current_time is None:
            current_time = datetime.now()
        
        # 이동 시간 계산
        travel_time_minutes = self._calculate_travel_time(distance_km)
        
        # 출발지 작업 시간 포함
        departure_time = current_time + timedelta(minutes=current_location.service_time_minutes)
        
        # 예상 도착 시간
        eta = departure_time + timedelta(minutes=travel_time_minutes)
        
        return eta
    
    def calculate_route_duration(
        self,
        distance_km: float,
        num_stops: int,
        avg_service_time_minutes: float = 30
    ) -> float:
        """
        경로 총 소요 시간 계산
        
        Args:
            distance_km: 총 거리
            num_stops: 경유지 수
            avg_service_time_minutes: 평균 작업 시간
            
        Returns:
            총 소요 시간 (분)
        """
        travel_time = self._calculate_travel_time(distance_km)
        service_time = num_stops * avg_service_time_minutes
        
        return travel_time + service_time
    
    def _calculate_travel_time(self, distance_km: float) -> float:
        """
        이동 시간 계산
        
        Args:
            distance_km: 거리 (km)
            
        Returns:
            이동 시간 (분)
        """
        # 기본 이동 시간
        base_time_hours = distance_km / self.average_speed_kmh
        
        # 교통 혼잡도 반영
        adjusted_time_hours = base_time_hours * self.traffic_factor
        
        # 분 단위 변환
        time_minutes = adjusted_time_hours * 60
        
        return time_minutes
    
    def _check_time_window(
        self,
        arrival_time: datetime,
        tw_start: Optional[str],
        tw_end: Optional[str]
    ) -> tuple[bool, float]:
        """
        Time Window 검증
        
        Args:
            arrival_time: 도착 시간
            tw_start: Time Window 시작 (HH:MM)
            tw_end: Time Window 종료 (HH:MM)
            
        Returns:
            (Time Window 준수 여부, 위반 시간(분))
        """
        if not tw_start and not tw_end:
            return True, 0.0
        
        arrival_time_only = arrival_time.time()
        
        if tw_start:
            start_time = self._parse_time(tw_start)
            if arrival_time_only < start_time:
                # 너무 일찍 도착 (대기 필요)
                return False, 0.0
        
        if tw_end:
            end_time = self._parse_time(tw_end)
            if arrival_time_only > end_time:
                # 너무 늦게 도착 (위반)
                start_dt = datetime.combine(arrival_time.date(), start_time if tw_start else datetime.min.time())
                end_dt = datetime.combine(arrival_time.date(), end_time)
                violation_minutes = (arrival_time - end_dt).total_seconds() / 60
                return False, violation_minutes
        
        return True, 0.0
    
    @staticmethod
    def _parse_time(time_str: str) -> datetime.time:
        """HH:MM 문자열을 time 객체로 변환"""
        from datetime import datetime
        return datetime.strptime(time_str, "%H:%M").time()
    
    def update_traffic_factor(self, new_factor: float):
        """교통 혼잡도 업데이트"""
        self.traffic_factor = new_factor
        logger.info(f"Traffic factor updated to {new_factor}")
    
    def get_eta_summary(self, eta_results: List[ETAResult]) -> Dict[str, Any]:
        """ETA 결과 요약"""
        if not eta_results:
            return {}
        
        total_violations = sum(1 for r in eta_results if not r.is_within_time_window)
        total_violation_time = sum(r.time_window_violation_minutes for r in eta_results)
        
        return {
            'total_stops': len(eta_results),
            'total_distance_km': eta_results[-1].cumulative_distance_km,
            'total_duration_minutes': eta_results[-1].cumulative_duration_minutes,
            'total_duration_hours': eta_results[-1].cumulative_duration_minutes / 60,
            'start_time': eta_results[0].estimated_arrival_time.isoformat(),
            'end_time': eta_results[-1].estimated_departure_time.isoformat(),
            'time_window_violations': total_violations,
            'total_violation_minutes': total_violation_time,
            'on_time_rate': (len(eta_results) - total_violations) / len(eta_results) * 100
        }


# 전역 ETA 서비스 인스턴스
_eta_service = None


def get_eta_service() -> ETAService:
    """ETA 서비스 싱글톤 인스턴스"""
    global _eta_service
    if _eta_service is None:
        _eta_service = ETAService()
        logger.info("ETA service initialized")
    return _eta_service
