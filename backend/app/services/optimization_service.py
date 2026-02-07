"""
Optimization Service - OR-Tools 기반 배차 최적화
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import math
from sqlalchemy.orm import Session

try:
    from ortools.constraint_solver import routing_enums_pb2, pywrapcp
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False

from app.models.order import Order
from app.models.vehicle import Vehicle
from app.models.dispatch import Dispatch
from app.models.optimization_config import OptimizationConfig


class OptimizationService:
    """배차 최적화 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        if not ORTOOLS_AVAILABLE:
            raise ImportError("OR-Tools not installed. Run: pip install ortools")
    
    def optimize_routes(self, 
                       orders: List[Order], 
                       vehicles: List[Vehicle],
                       config_id: Optional[int] = None) -> Dict[str, Any]:
        """
        배차 루트 최적화
        
        Args:
            orders: 주문 리스트
            vehicles: 차량 리스트
            config_id: 최적화 설정 ID
            
        Returns:
            최적화 결과
        """
        # 설정 로드
        config = self._load_config(config_id)
        
        # 거리 매트릭스 생성
        distance_matrix = self._create_distance_matrix(orders, vehicles)
        
        # OR-Tools 모델 생성
        manager, routing, solution = self._solve_vrp(
            orders, vehicles, distance_matrix, config
        )
        
        if not solution:
            return {
                'success': False,
                'message': 'No solution found'
            }
        
        # 결과 파싱
        routes = self._parse_solution(manager, routing, solution, orders, vehicles)
        
        # 통계 계산
        stats = self._calculate_stats(routes, distance_matrix)
        
        return {
            'success': True,
            'routes': routes,
            'statistics': stats,
            'optimization_config': {
                'objective': config['objective'],
                'algorithm': config['algorithm']
            }
        }
    
    def _load_config(self, config_id: Optional[int]) -> Dict[str, Any]:
        """최적화 설정 로드"""
        
        if config_id:
            config_obj = self.db.query(OptimizationConfig).filter(
                OptimizationConfig.id == config_id
            ).first()
        else:
            # 기본 설정
            config_obj = self.db.query(OptimizationConfig).filter(
                OptimizationConfig.is_default == True
            ).first()
        
        if config_obj:
            return {
                'objective': config_obj.objective,
                'weights': config_obj.weights,
                'algorithm': config_obj.algorithm,
                'max_time': config_obj.max_computation_time_seconds
            }
        
        # Fallback 기본 설정
        return {
            'objective': 'minimize_distance',
            'weights': {
                'distance': 0.6,
                'cost': 0.2,
                'time': 0.2
            },
            'algorithm': 'or_tools',
            'max_time': 60
        }
    
    def _create_distance_matrix(self, orders: List[Order], vehicles: List[Vehicle]) -> List[List[int]]:
        """
        거리 매트릭스 생성
        
        Note: 실제로는 Google Maps API 등을 사용해야 하지만
        여기서는 유클리드 거리로 간단히 계산
        """
        # 위치 리스트 (depot + pickup + delivery locations)
        locations = []
        
        # Depot (창고)
        depot_location = {'lat': 37.5665, 'lng': 126.9780}  # 서울 시청
        locations.append(depot_location)
        
        # 주문 픽업/배송 위치
        for order in orders:
            # 픽업 위치 (간단히 랜덤 좌표로)
            pickup_loc = self._parse_location(order.pickup_address)
            locations.append(pickup_loc)
            
            # 배송 위치
            delivery_loc = self._parse_location(order.delivery_address)
            locations.append(delivery_loc)
        
        # 거리 매트릭스 계산
        num_locations = len(locations)
        distance_matrix = [[0] * num_locations for _ in range(num_locations)]
        
        for i in range(num_locations):
            for j in range(num_locations):
                if i != j:
                    distance_matrix[i][j] = self._calculate_distance(
                        locations[i], locations[j]
                    )
        
        return distance_matrix
    
    def _parse_location(self, address: str) -> Dict[str, float]:
        """주소를 좌표로 변환 (간단한 예시)"""
        # 실제로는 Geocoding API 사용
        # 여기서는 임의의 서울 지역 좌표 반환
        import hashlib
        hash_val = int(hashlib.md5(address.encode()).hexdigest(), 16)
        
        lat = 37.5 + (hash_val % 100) / 1000
        lng = 126.9 + (hash_val % 200) / 1000
        
        return {'lat': lat, 'lng': lng}
    
    def _calculate_distance(self, loc1: Dict[str, float], loc2: Dict[str, float]) -> int:
        """두 지점 간 거리 계산 (미터 단위)"""
        # 하버사인 공식
        R = 6371000  # 지구 반경 (미터)
        
        lat1 = math.radians(loc1['lat'])
        lat2 = math.radians(loc2['lat'])
        dlat = math.radians(loc2['lat'] - loc1['lat'])
        dlng = math.radians(loc2['lng'] - loc1['lng'])
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distance = R * c
        return int(distance)
    
    def _solve_vrp(self, 
                   orders: List[Order], 
                   vehicles: List[Vehicle],
                   distance_matrix: List[List[int]],
                   config: Dict[str, Any]) -> Tuple:
        """OR-Tools VRP 문제 해결"""
        
        # 관리자 생성
        manager = pywrapcp.RoutingIndexManager(
            len(distance_matrix),  # 위치 수
            len(vehicles),          # 차량 수
            0                       # Depot 인덱스
        )
        
        # 라우팅 모델 생성
        routing = pywrapcp.RoutingModel(manager)
        
        # 거리 콜백
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distance_matrix[from_node][to_node]
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        
        # 목적 함수 설정
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # 용량 제약 추가
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            # Depot은 수요 0
            if from_node == 0:
                return 0
            # 주문 수요 (간단히 1로)
            return 1
        
        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        
        # 차량 용량 설정
        vehicle_capacities = [10] * len(vehicles)  # 각 차량 최대 10개 주문
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            vehicle_capacities,
            True,  # start cumul to zero
            'Capacity'
        )
        
        # 검색 파라미터
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = config['max_time']
        
        # 솔루션 찾기
        solution = routing.SolveWithParameters(search_parameters)
        
        return manager, routing, solution
    
    def _parse_solution(self, 
                       manager: Any, 
                       routing: Any, 
                       solution: Any,
                       orders: List[Order],
                       vehicles: List[Vehicle]) -> List[Dict[str, Any]]:
        """솔루션 파싱"""
        
        routes = []
        
        for vehicle_id in range(len(vehicles)):
            vehicle = vehicles[vehicle_id]
            index = routing.Start(vehicle_id)
            
            route = {
                'vehicle_id': vehicle.id,
                'vehicle_number': vehicle.vehicle_number,
                'stops': [],
                'total_distance_m': 0,
                'total_load': 0
            }
            
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                
                if node_index > 0:  # Skip depot
                    # 주문 매핑 (간단히)
                    order_index = (node_index - 1) // 2
                    if order_index < len(orders):
                        order = orders[order_index]
                        
                        stop_type = 'pickup' if node_index % 2 == 1 else 'delivery'
                        
                        route['stops'].append({
                            'order_id': order.id,
                            'order_number': order.order_number,
                            'stop_type': stop_type,
                            'sequence': len(route['stops']) + 1
                        })
                        
                        route['total_load'] += 1
                
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route['total_distance_m'] += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )
            
            if route['stops']:
                routes.append(route)
        
        return routes
    
    def _calculate_stats(self, routes: List[Dict[str, Any]], distance_matrix: List[List[int]]) -> Dict[str, Any]:
        """통계 계산"""
        
        total_distance = sum(r['total_distance_m'] for r in routes)
        total_orders = sum(len(r['stops']) for r in routes)
        
        return {
            'total_routes': len(routes),
            'total_orders_assigned': total_orders,
            'total_distance_km': round(total_distance / 1000, 2),
            'avg_distance_per_route_km': round(total_distance / len(routes) / 1000, 2) if routes else 0,
            'vehicles_used': len(routes)
        }
