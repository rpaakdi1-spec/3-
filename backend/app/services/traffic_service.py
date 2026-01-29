"""
실시간 교통 정보 서비스

네이버/카카오 API를 활용한 실시간 교통 정보 연동:
1. 실시간 경로 탐색
2. 소요 시간 계산
3. 교통 상황 분석
4. 최적 경로 추천
5. 배송 시간 예측
"""

import requests
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
from loguru import logger

from app.core.config import settings


class TrafficProvider(str, Enum):
    """교통 정보 제공자"""
    NAVER = "naver"
    KAKAO = "kakao"


class TransportMode(str, Enum):
    """이동 수단"""
    CAR = "car"
    TRUCK = "truck"


class RouteOption(str, Enum):
    """경로 옵션"""
    TRAFAST = "trafast"      # 실시간 빠른길
    TRACOMFORT = "tracomfort"  # 실시간 편한길
    TRAOPTIMAL = "traoptimal"  # 실시간 최적
    TRAAVOIDTOLL = "traavoidtoll"  # 무료 우선
    TRAAVOIDCARONLY = "traavoidcaronly"  # 자동차 전용도로 회피


class TrafficLevel(str, Enum):
    """교통 혼잡도"""
    SMOOTH = "원활"
    NORMAL = "보통"
    SLOW = "서행"
    CONGESTED = "정체"
    BLOCKED = "차단"


class TrafficService:
    """실시간 교통 정보 서비스"""
    
    def __init__(self):
        self.naver_client_id = settings.NAVER_MAP_CLIENT_ID
        self.naver_client_secret = settings.NAVER_MAP_CLIENT_SECRET
        self.kakao_rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY', None)
        
    def get_route_with_traffic(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        waypoints: Optional[List[Tuple[float, float]]] = None,
        provider: TrafficProvider = TrafficProvider.NAVER,
        option: RouteOption = RouteOption.TRAFAST
    ) -> Dict[str, Any]:
        """
        실시간 교통 정보를 반영한 경로 탐색
        
        Args:
            start_lat: 출발지 위도
            start_lon: 출발지 경도
            end_lat: 도착지 위도
            end_lon: 도착지 경도
            waypoints: 경유지 목록 [(위도, 경도), ...]
            provider: 교통 정보 제공자
            option: 경로 옵션
            
        Returns:
            Dict: 경로 정보 (거리, 시간, 교통 상황, 경로 좌표)
        """
        if provider == TrafficProvider.NAVER:
            return self._get_naver_route(
                start_lat, start_lon,
                end_lat, end_lon,
                waypoints, option
            )
        elif provider == TrafficProvider.KAKAO:
            return self._get_kakao_route(
                start_lat, start_lon,
                end_lat, end_lon,
                waypoints
            )
        else:
            raise ValueError(f"Unknown traffic provider: {provider}")
    
    def _get_naver_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        waypoints: Optional[List[Tuple[float, float]]] = None,
        option: RouteOption = RouteOption.TRAFAST
    ) -> Dict[str, Any]:
        """
        네이버 Directions API를 사용한 경로 탐색
        
        네이버 API는 실시간 교통 정보를 자동으로 반영합니다.
        """
        if not self.naver_client_id or not self.naver_client_secret:
            logger.warning("Naver API credentials not configured")
            return self._get_fallback_route(start_lat, start_lon, end_lat, end_lon)
        
        url = "https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving"
        
        # 파라미터 구성
        params = {
            "start": f"{start_lon},{start_lat}",  # 네이버는 경도,위도 순서
            "goal": f"{end_lon},{end_lat}",
            "option": option.value
        }
        
        # 경유지 추가
        if waypoints:
            waypoint_str = "|".join([f"{lon},{lat}" for lat, lon in waypoints])
            params["waypoints"] = waypoint_str
        
        headers = {
            "X-NCP-APIGW-API-KEY-ID": self.naver_client_id,
            "X-NCP-APIGW-API-KEY": self.naver_client_secret
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") == 0 and data.get("route"):
                # 첫 번째 경로 선택
                route = data["route"].get(option.value, [{}])[0]
                summary = route.get("summary", {})
                
                # 경로 좌표 추출
                path_coordinates = []
                for section in route.get("section", []):
                    for road in section.get("road", []):
                        for vertex in road.get("vertexes", []):
                            # 좌표는 [경도, 위도] 쌍으로 제공됨
                            if len(vertex) >= 2:
                                path_coordinates.append({
                                    "latitude": vertex[1],
                                    "longitude": vertex[0]
                                })
                
                # 교통 정보 분석
                traffic_info = self._analyze_naver_traffic(route)
                
                return {
                    "provider": TrafficProvider.NAVER.value,
                    "distance_km": summary.get("distance", 0) / 1000,
                    "duration_minutes": summary.get("duration", 0) / 60000,
                    "duration_with_traffic_minutes": summary.get("duration", 0) / 60000,
                    "fuel_cost": summary.get("fuelPrice", 0),
                    "toll_cost": summary.get("tollFare", 0),
                    "taxi_fare": summary.get("taxiFare", 0),
                    "traffic_info": traffic_info,
                    "path_coordinates": path_coordinates,
                    "option": option.value,
                    "retrieved_at": datetime.now().isoformat()
                }
            else:
                logger.error(f"Naver API error: {data}")
                return self._get_fallback_route(start_lat, start_lon, end_lat, end_lon)
                
        except Exception as e:
            logger.error(f"Failed to get Naver route: {e}")
            return self._get_fallback_route(start_lat, start_lon, end_lat, end_lon)
    
    def _analyze_naver_traffic(self, route: Dict[str, Any]) -> Dict[str, Any]:
        """
        네이버 경로 응답에서 교통 정보 분석
        
        Args:
            route: 네이버 경로 응답
            
        Returns:
            Dict: 교통 정보 분석 결과
        """
        total_distance = 0
        smooth_distance = 0
        slow_distance = 0
        congested_distance = 0
        
        for section in route.get("section", []):
            for road in section.get("road", []):
                distance = road.get("distance", 0)
                total_distance += distance
                
                # 교통 정보가 있으면 분석
                traffic = road.get("traffic", 0)
                if traffic == 0:
                    smooth_distance += distance
                elif traffic == 1:
                    slow_distance += distance
                elif traffic >= 2:
                    congested_distance += distance
        
        if total_distance == 0:
            return {
                "overall_level": TrafficLevel.NORMAL.value,
                "smooth_ratio": 0,
                "slow_ratio": 0,
                "congested_ratio": 0
            }
        
        smooth_ratio = smooth_distance / total_distance
        slow_ratio = slow_distance / total_distance
        congested_ratio = congested_distance / total_distance
        
        # 전체 교통 상황 판단
        if congested_ratio > 0.3:
            overall_level = TrafficLevel.CONGESTED
        elif slow_ratio > 0.4:
            overall_level = TrafficLevel.SLOW
        elif smooth_ratio > 0.7:
            overall_level = TrafficLevel.SMOOTH
        else:
            overall_level = TrafficLevel.NORMAL
        
        return {
            "overall_level": overall_level.value,
            "smooth_ratio": round(smooth_ratio * 100, 1),
            "slow_ratio": round(slow_ratio * 100, 1),
            "congested_ratio": round(congested_ratio * 100, 1),
            "description": self._get_traffic_description(overall_level)
        }
    
    def _get_kakao_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        waypoints: Optional[List[Tuple[float, float]]] = None
    ) -> Dict[str, Any]:
        """
        카카오 길찾기 API를 사용한 경로 탐색
        """
        if not self.kakao_rest_api_key:
            logger.warning("Kakao API key not configured")
            return self._get_fallback_route(start_lat, start_lon, end_lat, end_lon)
        
        url = "https://apis-navi.kakaomobility.com/v1/directions"
        
        # 카카오는 경도,위도 순서
        params = {
            "origin": f"{start_lon},{start_lat}",
            "destination": f"{end_lon},{end_lat}",
            "priority": "RECOMMEND"  # 추천 경로 (실시간 교통 반영)
        }
        
        # 경유지 추가
        if waypoints:
            waypoint_str = "|".join([f"{lon},{lat}" for lat, lon in waypoints])
            params["waypoints"] = waypoint_str
        
        headers = {
            "Authorization": f"KakaoAK {self.kakao_rest_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("routes"):
                route = data["routes"][0]
                summary = route.get("summary", {})
                
                # 경로 좌표 추출
                path_coordinates = []
                for section in route.get("sections", []):
                    for road in section.get("roads", []):
                        for vertex in road.get("vertexes", []):
                            if len(vertex) >= 2:
                                path_coordinates.append({
                                    "latitude": vertex[1],
                                    "longitude": vertex[0]
                                })
                
                return {
                    "provider": TrafficProvider.KAKAO.value,
                    "distance_km": summary.get("distance", 0) / 1000,
                    "duration_minutes": summary.get("duration", 0) / 60,
                    "duration_with_traffic_minutes": summary.get("duration", 0) / 60,
                    "fare": summary.get("fare", {}),
                    "path_coordinates": path_coordinates,
                    "retrieved_at": datetime.now().isoformat()
                }
            else:
                logger.error(f"Kakao API error: {data}")
                return self._get_fallback_route(start_lat, start_lon, end_lat, end_lon)
                
        except Exception as e:
            logger.error(f"Failed to get Kakao route: {e}")
            return self._get_fallback_route(start_lat, start_lon, end_lat, end_lon)
    
    def _get_fallback_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float
    ) -> Dict[str, Any]:
        """
        Fallback: Haversine 거리 기반 추정
        
        API 실패 시 기본 거리 계산으로 대체
        """
        from math import radians, cos, sin, asin, sqrt
        
        def haversine(lon1, lat1, lon2, lat2):
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371
            return c * r
        
        distance = haversine(start_lon, start_lat, end_lon, end_lat)
        
        # 실제 도로 거리 추정 (직선 거리 * 1.3)
        road_distance = distance * 1.3
        
        # 평균 속도 40km/h로 계산
        duration = (road_distance / 40) * 60
        
        # 교통 혼잡 고려 (+30%)
        duration_with_traffic = duration * 1.3
        
        return {
            "provider": "fallback",
            "distance_km": road_distance,
            "duration_minutes": duration,
            "duration_with_traffic_minutes": duration_with_traffic,
            "traffic_info": {
                "overall_level": TrafficLevel.NORMAL.value,
                "description": "교통 정보 API를 사용할 수 없어 기본 계산을 사용했습니다."
            },
            "path_coordinates": [
                {"latitude": start_lat, "longitude": start_lon},
                {"latitude": end_lat, "longitude": end_lon}
            ],
            "retrieved_at": datetime.now().isoformat(),
            "note": "Fallback calculation (Haversine)"
        }
    
    def _get_traffic_description(self, level: TrafficLevel) -> str:
        """교통 상황 설명 반환"""
        descriptions = {
            TrafficLevel.SMOOTH: "원활 - 교통 흐름이 매우 좋습니다",
            TrafficLevel.NORMAL: "보통 - 평균적인 교통 상황입니다",
            TrafficLevel.SLOW: "서행 - 다소 막히는 구간이 있습니다",
            TrafficLevel.CONGESTED: "정체 - 심한 정체가 예상됩니다",
            TrafficLevel.BLOCKED: "차단 - 통행이 불가능합니다"
        }
        return descriptions.get(level, "정보 없음")
    
    def get_optimized_route_order(
        self,
        start_location: Tuple[float, float],
        destinations: List[Tuple[float, float, Any]],
        end_location: Optional[Tuple[float, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        실시간 교통 정보를 고려한 최적 경로 순서 계산
        
        Args:
            start_location: 출발지 (위도, 경도)
            destinations: 목적지 목록 [(위도, 경도, 추가정보), ...]
            end_location: 종료지 (위도, 경도) - 없으면 출발지로 복귀
            
        Returns:
            List[Dict]: 최적화된 경로 순서
        """
        if not destinations:
            return []
        
        if end_location is None:
            end_location = start_location
        
        # 모든 목적지 간 거리 및 시간 매트릭스 생성
        locations = [start_location] + [(lat, lon) for lat, lon, _ in destinations] + [end_location]
        n = len(locations)
        
        distance_matrix = [[0.0] * n for _ in range(n)]
        time_matrix = [[0.0] * n for _ in range(n)]
        
        # 실시간 교통 정보로 거리/시간 계산
        for i in range(n):
            for j in range(i + 1, n):
                route = self.get_route_with_traffic(
                    locations[i][0], locations[i][1],
                    locations[j][0], locations[j][1]
                )
                distance_matrix[i][j] = route["distance_km"]
                distance_matrix[j][i] = route["distance_km"]
                time_matrix[i][j] = route["duration_with_traffic_minutes"]
                time_matrix[j][i] = route["duration_with_traffic_minutes"]
        
        # 간단한 최근접 이웃 알고리즘 (Nearest Neighbor)
        # 실제로는 OR-Tools TSP와 통합 가능
        unvisited = set(range(1, n - 1))  # 출발지와 종료지 제외
        current = 0  # 출발지
        route_order = [0]
        
        while unvisited:
            # 현재 위치에서 가장 가까운 미방문 목적지 선택
            nearest = min(unvisited, key=lambda x: time_matrix[current][x])
            route_order.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        route_order.append(n - 1)  # 종료지 추가
        
        # 결과 구성
        optimized_routes = []
        for i in range(len(route_order) - 1):
            from_idx = route_order[i]
            to_idx = route_order[i + 1]
            
            route_info = self.get_route_with_traffic(
                locations[from_idx][0], locations[from_idx][1],
                locations[to_idx][0], locations[to_idx][1]
            )
            
            optimized_routes.append({
                "sequence": i + 1,
                "from_location": {
                    "latitude": locations[from_idx][0],
                    "longitude": locations[from_idx][1]
                },
                "to_location": {
                    "latitude": locations[to_idx][0],
                    "longitude": locations[to_idx][1]
                },
                "distance_km": route_info["distance_km"],
                "duration_minutes": route_info["duration_with_traffic_minutes"],
                "traffic_info": route_info.get("traffic_info"),
                "path_coordinates": route_info.get("path_coordinates", [])
            })
        
        return optimized_routes
    
    def estimate_arrival_time(
        self,
        current_lat: float,
        current_lon: float,
        destination_lat: float,
        destination_lon: float,
        departure_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        실시간 교통 정보 기반 도착 시간 예측
        
        Args:
            current_lat: 현재 위도
            current_lon: 현재 경도
            destination_lat: 목적지 위도
            destination_lon: 목적지 경도
            departure_time: 출발 시간 (None이면 현재 시간)
            
        Returns:
            Dict: 예상 도착 시간 정보
        """
        if departure_time is None:
            departure_time = datetime.now()
        
        # 실시간 경로 정보 조회
        route = self.get_route_with_traffic(
            current_lat, current_lon,
            destination_lat, destination_lon
        )
        
        # 도착 시간 계산
        duration_minutes = route["duration_with_traffic_minutes"]
        arrival_time = departure_time + timedelta(minutes=duration_minutes)
        
        # 신뢰 구간 계산 (±15%)
        early_arrival = departure_time + timedelta(minutes=duration_minutes * 0.85)
        late_arrival = departure_time + timedelta(minutes=duration_minutes * 1.15)
        
        return {
            "departure_time": departure_time.isoformat(),
            "estimated_arrival_time": arrival_time.isoformat(),
            "early_arrival_time": early_arrival.isoformat(),
            "late_arrival_time": late_arrival.isoformat(),
            "duration_minutes": duration_minutes,
            "distance_km": route["distance_km"],
            "traffic_info": route.get("traffic_info"),
            "confidence": "medium",  # low, medium, high
            "updated_at": datetime.now().isoformat()
        }
    
    def get_traffic_summary(
        self,
        routes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        여러 경로의 교통 상황 요약
        
        Args:
            routes: 경로 목록
            
        Returns:
            Dict: 교통 상황 요약
        """
        if not routes:
            return {
                "total_distance_km": 0,
                "total_duration_minutes": 0,
                "average_speed_kmh": 0,
                "overall_traffic_level": TrafficLevel.NORMAL.value,
                "route_count": 0
            }
        
        total_distance = sum(r["distance_km"] for r in routes)
        total_duration = sum(r["duration_with_traffic_minutes"] for r in routes)
        
        avg_speed = (total_distance / (total_duration / 60)) if total_duration > 0 else 0
        
        # 교통 상황 종합 판단
        traffic_levels = []
        for route in routes:
            if route.get("traffic_info"):
                level = route["traffic_info"].get("overall_level", TrafficLevel.NORMAL.value)
                traffic_levels.append(level)
        
        # 가장 빈번한 교통 레벨
        if traffic_levels:
            from collections import Counter
            overall_level = Counter(traffic_levels).most_common(1)[0][0]
        else:
            overall_level = TrafficLevel.NORMAL.value
        
        return {
            "total_distance_km": round(total_distance, 2),
            "total_duration_minutes": round(total_duration, 1),
            "average_speed_kmh": round(avg_speed, 1),
            "overall_traffic_level": overall_level,
            "route_count": len(routes),
            "summary": f"{len(routes)}개 경로, 총 {round(total_distance, 1)}km, 약 {round(total_duration, 0)}분 소요"
        }
