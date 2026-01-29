"""
Multi-order TSP optimization service
한 차량에 여러 주문을 배정하고 최적 경로 순서를 계산
"""
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import math
from loguru import logger

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


class TSPOptimizer:
    """TSP (Traveling Salesman Problem) 최적화 서비스"""
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine 거리 계산 (km)"""
        R = 6371  # Earth radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    @staticmethod
    def optimize_route_sequence(
        start_location: Tuple[float, float],
        locations: List[Dict],
        return_to_start: bool = True
    ) -> Tuple[List[int], float]:
        """
        최적 경로 순서 계산
        
        Args:
            start_location: (latitude, longitude) - 시작점 (차고지 또는 현재 위치)
            locations: List of dicts with 'latitude', 'longitude', 'type' (pickup/delivery)
            return_to_start: 시작점으로 돌아올지 여부
        
        Returns:
            (optimized_indices, total_distance)
        """
        if not locations:
            return [], 0.0
        
        # 위치 리스트 생성: [start] + locations
        all_locations = [start_location] + [(loc['latitude'], loc['longitude']) for loc in locations]
        num_locations = len(all_locations)
        
        # 거리 행렬 생성
        distance_matrix = []
        for i in range(num_locations):
            row = []
            for j in range(num_locations):
                if i == j:
                    row.append(0)
                else:
                    dist = TSPOptimizer.calculate_distance(
                        all_locations[i][0], all_locations[i][1],
                        all_locations[j][0], all_locations[j][1]
                    )
                    # Convert to meters for OR-Tools
                    row.append(int(dist * 1000))
            distance_matrix.append(row)
        
        # OR-Tools TSP 설정
        manager = pywrapcp.RoutingIndexManager(num_locations, 1, 0)  # 1 vehicle, start at 0
        routing = pywrapcp.RoutingModel(manager)
        
        # 거리 콜백
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distance_matrix[from_node][to_node]
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Pickup-Delivery 제약 추가
        pickup_deliveries = []
        for i, loc in enumerate(locations):
            if loc.get('type') == 'pickup' and loc.get('order_id'):
                # Find matching delivery
                for j, other_loc in enumerate(locations):
                    if (other_loc.get('type') == 'delivery' and 
                        other_loc.get('order_id') == loc['order_id']):
                        # pickup must come before delivery
                        pickup_idx = manager.NodeToIndex(i + 1)  # +1 because 0 is start
                        delivery_idx = manager.NodeToIndex(j + 1)
                        pickup_deliveries.append([pickup_idx, delivery_idx])
                        break
        
        for pickup_delivery in pickup_deliveries:
            routing.AddPickupAndDelivery(pickup_delivery[0], pickup_delivery[1])
            routing.solver().Add(
                routing.VehicleVar(pickup_delivery[0]) == routing.VehicleVar(pickup_delivery[1])
            )
        
        # 검색 파라미터
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = 5
        
        # 최적화 실행
        solution = routing.SolveWithParameters(search_parameters)
        
        if solution:
            # 최적 경로 추출
            optimized_indices = []
            total_distance = 0
            
            index = routing.Start(0)
            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                if node > 0:  # Skip start location
                    optimized_indices.append(node - 1)  # -1 to get original location index
                
                next_index = solution.Value(routing.NextVar(index))
                if not routing.IsEnd(next_index):
                    from_node = manager.IndexToNode(index)
                    to_node = manager.IndexToNode(next_index)
                    total_distance += distance_matrix[from_node][to_node]
                
                index = next_index
            
            total_distance_km = total_distance / 1000.0
            
            logger.info(f"TSP optimized route: {len(optimized_indices)} stops, total distance: {total_distance_km:.2f} km")
            return optimized_indices, total_distance_km
        else:
            # Fallback: 원래 순서 반환
            logger.warning("TSP optimization failed, using original order")
            return list(range(len(locations))), 0.0
    
    @staticmethod
    def optimize_pickup_delivery_order(orders: List[Dict]) -> List[Dict]:
        """
        주문들의 픽업-배송 순서 최적화
        
        Args:
            orders: List of order dicts with pickup/delivery locations
        
        Returns:
            Optimized list of route stops
        """
        if not orders:
            return []
        
        # 모든 픽업/배송 위치 수집
        locations = []
        
        for order in orders:
            # Pickup location
            locations.append({
                'order_id': order['id'],
                'type': 'pickup',
                'latitude': order['pickup_latitude'],
                'longitude': order['pickup_longitude'],
                'name': order['pickup_name'],
                'address': order['pickup_address'],
                'pallet_count': order['pallet_count'],
                'weight_kg': order['weight_kg']
            })
            
            # Delivery location
            locations.append({
                'order_id': order['id'],
                'type': 'delivery',
                'latitude': order['delivery_latitude'],
                'longitude': order['delivery_longitude'],
                'name': order['delivery_name'],
                'address': order['delivery_address'],
                'pallet_count': -order['pallet_count'],  # Negative for unloading
                'weight_kg': -order['weight_kg']
            })
        
        # 시작 위치 (첫 번째 픽업)
        start_location = (orders[0]['pickup_latitude'], orders[0]['pickup_longitude'])
        
        # TSP 최적화
        optimized_indices, total_distance = TSPOptimizer.optimize_route_sequence(
            start_location, locations, return_to_start=False
        )
        
        # 최적화된 순서대로 재정렬
        optimized_locations = [locations[i] for i in optimized_indices]
        
        return optimized_locations, total_distance
