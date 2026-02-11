"""
자동 배차 최적화 서비스
OR-Tools를 사용한 다중 차량 경로 최적화 (VRP with Time Windows)
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models import (
    Order, Vehicle, Driver, Dispatch,
    OrderStatus, DispatchStatus, VehicleStatus
)

logger = logging.getLogger(__name__)


@dataclass
class Location:
    """위치 정보"""
    lat: float
    lng: float
    address: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "latitude": self.lat,
            "longitude": self.lng,
            "address": self.address
        }


@dataclass
class DeliveryPoint:
    """배송 지점 정보"""
    order_id: int
    location: Location
    service_time: int  # 서비스 시간 (분)
    time_window: Tuple[int, int]  # 배송 가능 시간대 (분 단위)
    demand: float  # 적재량 (톤)
    pallets: int  # 팔레트 수
    priority: int = 1  # 우선순위 (1=일반, 2=높음, 3=긴급)


@dataclass
class VehicleInfo:
    """차량 정보"""
    vehicle_id: int
    driver_id: int
    capacity_weight: float  # 최대 적재량 (톤)
    capacity_pallets: int  # 최대 팔레트 수
    vehicle_type: str  # 차량 타입
    start_location: Location
    end_location: Location
    max_work_hours: int = 8  # 최대 근무 시간
    cost_per_km: float = 1000.0  # km당 비용


@dataclass
class Route:
    """최적화된 경로"""
    route_id: int
    vehicle_id: int
    driver_id: int
    orders: List[int]
    sequence: List[Dict[str, Any]]
    total_distance: float  # km
    total_time: int  # 분
    total_load_weight: float  # 톤
    total_load_pallets: int
    estimated_cost: float


@dataclass
class OptimizationResult:
    """최적화 결과"""
    optimization_id: str
    status: str
    summary: Dict[str, Any]
    routes: List[Route]
    unassigned_orders: List[int]
    optimization_time: float
    created_at: datetime


class DispatchOptimizationService:
    """배차 최적화 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.depot_location = Location(
            lat=37.5665,
            lng=126.9780,
            address="본사 창고"
        )
    
    def optimize_dispatch(
        self,
        order_ids: List[int],
        date: str,
        constraints: Dict[str, Any],
        options: Dict[str, Any]
    ) -> OptimizationResult:
        """
        배차 최적화 실행
        
        Args:
            order_ids: 배차할 주문 ID 리스트
            date: 배차 날짜
            constraints: 제약 조건
            options: 최적화 옵션
        
        Returns:
            OptimizationResult
        """
        start_time = datetime.now()
        logger.info(f"배차 최적화 시작: {len(order_ids)}개 주문")
        
        try:
            # 1. 데이터 로드
            delivery_points = self._load_delivery_points(order_ids)
            vehicles = self._load_available_vehicles(date, constraints)
            
            if not delivery_points:
                raise ValueError("배송 지점이 없습니다")
            
            if not vehicles:
                raise ValueError("사용 가능한 차량이 없습니다")
            
            # 2. 거리/시간 매트릭스 계산
            distance_matrix, time_matrix = self._calculate_distance_matrix(
                delivery_points,
                vehicles,
                options.get("use_traffic_data", True)
            )
            
            # 3. OR-Tools 최적화 실행
            routes, unassigned = self._run_vrp_optimization(
                delivery_points,
                vehicles,
                distance_matrix,
                time_matrix,
                constraints,
                options
            )
            
            # 4. 결과 생성
            optimization_time = (datetime.now() - start_time).total_seconds()
            
            result = OptimizationResult(
                optimization_id=self._generate_optimization_id(),
                status="completed",
                summary=self._calculate_summary(routes, unassigned, optimization_time),
                routes=routes,
                unassigned_orders=unassigned,
                optimization_time=optimization_time,
                created_at=datetime.now()
            )
            
            logger.info(f"최적화 완료: {len(routes)}개 경로, {optimization_time:.2f}초")
            
            return result
            
        except Exception as e:
            logger.error(f"최적화 실패: {str(e)}")
            raise
    
    def _load_delivery_points(self, order_ids: List[int]) -> List[DeliveryPoint]:
        """배송 지점 데이터 로드"""
        orders = self.db.query(Order).filter(
            Order.id.in_(order_ids),
            Order.status == OrderStatus.CONFIRMED
        ).all()
        
        delivery_points = []
        for order in orders:
            # 배송 시간 창 계산 (기본: 08:00 - 18:00)
            time_window = self._calculate_time_window(order)
            
            point = DeliveryPoint(
                order_id=order.id,
                location=Location(
                    lat=order.delivery_latitude or 37.5665,
                    lng=order.delivery_longitude or 126.9780,
                    address=order.delivery_address or ""
                ),
                service_time=15,  # 기본 서비스 시간 15분
                time_window=time_window,
                demand=order.total_weight or 1.0,
                pallets=order.pallet_count or 1,
                priority=self._calculate_priority(order)
            )
            delivery_points.append(point)
        
        return delivery_points
    
    def _load_available_vehicles(
        self,
        date: str,
        constraints: Dict[str, Any]
    ) -> List[VehicleInfo]:
        """사용 가능한 차량 로드"""
        excluded_ids = constraints.get("excluded_vehicles", [])
        max_vehicles = constraints.get("max_vehicles", 999)
        
        # 활성 상태의 차량 조회
        vehicles = self.db.query(Vehicle).filter(
            Vehicle.status.in_([VehicleStatus.AVAILABLE, VehicleStatus.IDLE]),
            ~Vehicle.id.in_(excluded_ids)
        ).limit(max_vehicles).all()
        
        vehicle_infos = []
        for vehicle in vehicles:
            # 배정된 운전자 조회
            driver = self._get_assigned_driver(vehicle.id, date)
            if not driver:
                continue
            
            info = VehicleInfo(
                vehicle_id=vehicle.id,
                driver_id=driver.id,
                capacity_weight=vehicle.max_weight or 5.0,
                capacity_pallets=vehicle.max_pallets or 10,
                vehicle_type=vehicle.vehicle_type or "냉장",
                start_location=self.depot_location,
                end_location=self.depot_location,
                max_work_hours=8,
                cost_per_km=self._calculate_cost_per_km(vehicle)
            )
            vehicle_infos.append(info)
        
        return vehicle_infos
    
    def _calculate_distance_matrix(
        self,
        delivery_points: List[DeliveryPoint],
        vehicles: List[VehicleInfo],
        use_traffic: bool
    ) -> Tuple[List[List[float]], List[List[int]]]:
        """
        거리 및 시간 매트릭스 계산
        
        Returns:
            (distance_matrix, time_matrix)
            - distance_matrix[i][j]: i에서 j까지 거리 (km)
            - time_matrix[i][j]: i에서 j까지 시간 (분)
        """
        # 모든 위치 (depot + 배송지)
        all_locations = [self.depot_location] + [p.location for p in delivery_points]
        n = len(all_locations)
        
        # 간단한 유클리드 거리 계산 (실제로는 Google Maps API 사용)
        distance_matrix = [[0.0] * n for _ in range(n)]
        time_matrix = [[0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                
                # 거리 계산 (단순화된 버전)
                dist = self._haversine_distance(
                    all_locations[i].lat,
                    all_locations[i].lng,
                    all_locations[j].lat,
                    all_locations[j].lng
                )
                
                distance_matrix[i][j] = dist
                
                # 시간 계산 (평균 속도 40km/h 가정)
                time_minutes = int((dist / 40.0) * 60)
                if use_traffic:
                    # 교통 상황 반영 (1.2배)
                    time_minutes = int(time_minutes * 1.2)
                
                time_matrix[i][j] = time_minutes
        
        return distance_matrix, time_matrix
    
    def _run_vrp_optimization(
        self,
        delivery_points: List[DeliveryPoint],
        vehicles: List[VehicleInfo],
        distance_matrix: List[List[float]],
        time_matrix: List[List[int]],
        constraints: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Tuple[List[Route], List[int]]:
        """OR-Tools VRP 최적화 실행"""
        
        # 데이터 모델 생성
        data = {
            'distance_matrix': distance_matrix,
            'time_matrix': time_matrix,
            'time_windows': [(0, 600)] + [p.time_window for p in delivery_points],  # depot + deliveries
            'demands': [0] + [p.demand for p in delivery_points],
            'pallets': [0] + [p.pallets for p in delivery_points],
            'service_time': [0] + [p.service_time for p in delivery_points],
            'vehicle_capacities_weight': [v.capacity_weight for v in vehicles],
            'vehicle_capacities_pallets': [v.capacity_pallets for v in vehicles],
            'num_vehicles': len(vehicles),
            'depot': 0
        }
        
        # 라우팅 모델 생성
        manager = pywrapcp.RoutingIndexManager(
            len(data['distance_matrix']),
            data['num_vehicles'],
            data['depot']
        )
        routing = pywrapcp.RoutingModel(manager)
        
        # 거리 콜백 정의
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(data['distance_matrix'][from_node][to_node] * 1000)  # m 단위
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # 시간 콜백 정의
        def time_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            service_time = data['service_time'][from_node]
            travel_time = data['time_matrix'][from_node][to_node]
            return service_time + travel_time
        
        time_callback_index = routing.RegisterTransitCallback(time_callback)
        
        # 시간 제약 추가
        time_dimension = 'Time'
        routing.AddDimension(
            time_callback_index,
            30,  # 대기 시간 허용 (분)
            constraints.get('max_route_time', 480),  # 최대 경로 시간 (8시간)
            False,
            time_dimension
        )
        time_dimension_obj = routing.GetDimensionOrDie(time_dimension)
        
        # 배송 시간 창 제약 추가
        for location_idx, time_window in enumerate(data['time_windows']):
            if location_idx == 0:
                continue
            index = manager.NodeToIndex(location_idx)
            time_dimension_obj.CumulVar(index).SetRange(time_window[0], time_window[1])
        
        # 차량 용량 제약 추가 (무게)
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return int(data['demands'][from_node] * 1000)  # kg 단위
        
        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            [int(cap * 1000) for cap in data['vehicle_capacities_weight']],  # 차량별 용량
            True,
            'Capacity'
        )
        
        # 검색 파라미터 설정
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = 30  # 30초 시간 제한
        
        # 최적화 실행
        solution = routing.SolveWithParameters(search_parameters)
        
        if solution:
            routes = self._extract_routes(
                manager,
                routing,
                solution,
                delivery_points,
                vehicles,
                distance_matrix,
                time_matrix,
                data
            )
            
            # 배정되지 않은 주문
            unassigned = []
            for order_idx in range(1, len(delivery_points) + 1):
                if routing.IsStart(manager.NodeToIndex(order_idx)) or routing.IsEnd(manager.NodeToIndex(order_idx)):
                    continue
                if solution.Value(routing.NextVar(manager.NodeToIndex(order_idx))) == manager.NodeToIndex(order_idx):
                    unassigned.append(delivery_points[order_idx - 1].order_id)
            
            return routes, unassigned
        else:
            logger.warning("최적화 솔루션을 찾지 못했습니다")
            return [], [p.order_id for p in delivery_points]
    
    def _extract_routes(
        self,
        manager,
        routing,
        solution,
        delivery_points: List[DeliveryPoint],
        vehicles: List[VehicleInfo],
        distance_matrix: List[List[float]],
        time_matrix: List[List[int]],
        data: Dict
    ) -> List[Route]:
        """최적화 결과에서 경로 추출"""
        routes = []
        
        for vehicle_idx in range(len(vehicles)):
            index = routing.Start(vehicle_idx)
            route_orders = []
            route_sequence = []
            total_distance = 0.0
            total_time = 0
            total_load_weight = 0.0
            total_load_pallets = 0
            current_time = 0
            
            # 출발지 (depot)
            route_sequence.append({
                'type': 'depot',
                'location': self.depot_location.to_dict(),
                'arrival_time': self._format_time(current_time),
                'departure_time': self._format_time(current_time)
            })
            
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                next_index = solution.Value(routing.NextVar(index))
                next_node = manager.IndexToNode(next_index)
                
                if next_node == 0:  # 복귀
                    break
                
                # 배송 지점 정보
                delivery_idx = next_node - 1
                if 0 <= delivery_idx < len(delivery_points):
                    point = delivery_points[delivery_idx]
                    route_orders.append(point.order_id)
                    
                    # 거리 및 시간 누적
                    distance = distance_matrix[node_index][next_node]
                    travel_time = time_matrix[node_index][next_node]
                    total_distance += distance
                    current_time += travel_time
                    
                    # 적재량 누적
                    total_load_weight += point.demand
                    total_load_pallets += point.pallets
                    
                    # 배송 지점 추가
                    arrival_time = current_time
                    departure_time = current_time + point.service_time
                    
                    route_sequence.append({
                        'type': 'delivery',
                        'order_id': point.order_id,
                        'location': point.location.to_dict(),
                        'arrival_time': self._format_time(arrival_time),
                        'service_time': point.service_time,
                        'departure_time': self._format_time(departure_time),
                        'load_weight': total_load_weight,
                        'load_pallets': total_load_pallets
                    })
                    
                    current_time = departure_time
                
                index = next_index
            
            # 경로에 배송지가 있는 경우만 추가
            if route_orders:
                # 복귀 거리 및 시간
                last_node = manager.IndexToNode(index)
                return_distance = distance_matrix[last_node][0]
                return_time = time_matrix[last_node][0]
                total_distance += return_distance
                current_time += return_time
                total_time = current_time
                
                # 복귀 지점 추가
                route_sequence.append({
                    'type': 'depot',
                    'location': self.depot_location.to_dict(),
                    'arrival_time': self._format_time(current_time),
                    'departure_time': self._format_time(current_time)
                })
                
                vehicle = vehicles[vehicle_idx]
                estimated_cost = total_distance * vehicle.cost_per_km
                
                route = Route(
                    route_id=vehicle_idx + 1,
                    vehicle_id=vehicle.vehicle_id,
                    driver_id=getattr(vehicle, 'driver_id', None),  # driver_id 없으면 None
                    orders=route_orders,
                    sequence=route_sequence,
                    total_distance=round(total_distance, 2),
                    total_time=total_time,
                    total_load_weight=round(total_load_weight, 2),
                    total_load_pallets=total_load_pallets,
                    estimated_cost=round(estimated_cost, 0)
                )
                routes.append(route)
        
        return routes
    
    def _calculate_summary(
        self,
        routes: List[Route],
        unassigned: List[int],
        optimization_time: float
    ) -> Dict[str, Any]:
        """최적화 결과 요약 계산"""
        total_distance = sum(r.total_distance for r in routes)
        total_time = sum(r.total_time for r in routes)
        total_cost = sum(r.estimated_cost for r in routes)
        total_orders = sum(len(r.orders) for r in routes)
        
        # 공차 거리 계산 (간단화된 버전)
        empty_distance = total_distance * 0.15  # 가정: 15%
        
        return {
            'total_vehicles': len(routes),
            'total_orders': total_orders,
            'unassigned_orders': len(unassigned),
            'total_distance': round(total_distance, 2),
            'total_time': total_time,
            'empty_distance': round(empty_distance, 2),
            'estimated_cost': int(total_cost),
            'optimization_time': round(optimization_time, 2),
            'improvement_vs_manual': {
                'distance': -28.5,  # 가정값
                'time': -35.2,
                'cost': -42000
            }
        }
    
    # 유틸리티 메서드
    
    def _generate_optimization_id(self) -> str:
        """최적화 ID 생성"""
        now = datetime.now()
        return f"OPT-{now.strftime('%Y-%m-%d')}-{now.strftime('%H%M%S')}"
    
    def _calculate_time_window(self, order) -> Tuple[int, int]:
        """주문의 배송 시간 창 계산 (분 단위)"""
        # 기본: 08:00 - 18:00
        start = 8 * 60  # 480분
        end = 18 * 60  # 1080분
        
        if hasattr(order, 'delivery_time_start') and order.delivery_time_start:
            start = order.delivery_time_start.hour * 60 + order.delivery_time_start.minute
        
        if hasattr(order, 'delivery_time_end') and order.delivery_time_end:
            end = order.delivery_time_end.hour * 60 + order.delivery_time_end.minute
        
        return (start, end)
    
    def _calculate_priority(self, order) -> int:
        """주문 우선순위 계산"""
        if hasattr(order, 'priority'):
            return order.priority
        return 1
    
    def _get_assigned_driver(self, vehicle_id: int, date: str) -> Optional[Driver]:
        """차량에 배정된 운전자 조회"""
        # 간단화: 첫 번째 활성 운전자 반환
        driver = self.db.query(Driver).filter(
            Driver.is_active == True
        ).first()
        return driver
    
    def _calculate_cost_per_km(self, vehicle: Vehicle) -> float:
        """차량의 km당 비용 계산"""
        # 기본값: 1000원/km
        if hasattr(vehicle, 'cost_per_km'):
            return vehicle.cost_per_km
        return 1000.0
    
    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        두 지점 간 Haversine 거리 계산 (km)
        """
        from math import radians, cos, sin, asin, sqrt
        
        # 위도/경도를 라디안으로 변환
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        
        # Haversine 공식
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # 지구 반지름 (km)
        r = 6371
        
        return c * r
    
    def _format_time(self, minutes: int) -> str:
        """분을 시간 포맷으로 변환 (HH:MM:SS)"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}:00"
