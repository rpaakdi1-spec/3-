"""
동적 재배차 알고리즘
실시간 상황 변화(지연, 고장, 신규 주문)에 대응하여 배차를 동적으로 재조정
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

logger = logging.getLogger(__name__)


class DynamicRedispatcher:
    """동적 재배차 엔진"""
    
    def __init__(self):
        self.reoptimization_threshold = 0.15  # 15% 이상 변경 시 재최적화
        
    def should_redispatch(
        self,
        current_dispatch: Dict,
        new_conditions: Dict
    ) -> bool:
        """재배차가 필요한지 판단"""
        
        # 1. 차량 고장/사고
        if new_conditions.get('vehicle_breakdown'):
            logger.info(f"Vehicle breakdown detected: {new_conditions['vehicle_id']}")
            return True
            
        # 2. 심각한 지연 (30분 이상)
        delay_minutes = new_conditions.get('delay_minutes', 0)
        if delay_minutes >= 30:
            logger.info(f"Significant delay detected: {delay_minutes} minutes")
            return True
            
        # 3. 긴급 주문 추가
        if new_conditions.get('urgent_order'):
            logger.info("Urgent order added")
            return True
            
        # 4. 온도 이탈로 인한 대체 필요
        if new_conditions.get('temperature_violation'):
            logger.warning(f"Temperature violation: {new_conditions['vehicle_id']}")
            return True
            
        # 5. 비용 절감 기회 (15% 이상)
        cost_saving = new_conditions.get('potential_saving', 0)
        if cost_saving >= self.reoptimization_threshold:
            logger.info(f"Cost saving opportunity: {cost_saving*100:.1f}%")
            return True
            
        return False
    
    def redispatch(
        self,
        current_routes: List[Dict],
        affected_vehicle_id: Optional[int],
        new_orders: List[Dict],
        available_vehicles: List[Dict]
    ) -> Dict:
        """동적 재배차 실행"""
        
        logger.info(f"Starting dynamic redispatch. Affected vehicle: {affected_vehicle_id}")
        
        # 1. 영향받은 경로 추출
        affected_orders = []
        unaffected_routes = []
        
        for route in current_routes:
            if route['vehicle_id'] == affected_vehicle_id:
                # 이미 완료된 주문 제외
                for order in route['orders']:
                    if order['status'] not in ['COMPLETED', 'IN_PROGRESS']:
                        affected_orders.append(order)
            else:
                # 다른 차량 경로는 유지 (soft lock)
                unaffected_routes.append(route)
        
        # 2. 새 주문과 영향받은 주문을 재할당
        orders_to_assign = affected_orders + new_orders
        
        logger.info(f"Orders to reassign: {len(orders_to_assign)}")
        logger.info(f"Available vehicles: {len(available_vehicles)}")
        
        # 3. 제약 조건 재설정
        # - 이미 출발한 차량은 현재 위치부터 시작
        # - 온도대, 용량 제약 유지
        # - 긴급도에 따른 우선순위 부여
        
        # 4. OR-Tools로 재최적화
        new_solution = self._optimize_with_ortools(
            orders_to_assign,
            available_vehicles,
            unaffected_routes
        )
        
        # 5. 변경사항 계산
        changes = self._calculate_changes(current_routes, new_solution)
        
        return {
            'success': True,
            'new_routes': new_solution['routes'],
            'changes': changes,
            'optimization_time': new_solution['computation_time'],
            'cost_comparison': {
                'before': current_routes,
                'after': new_solution['routes'],
                'saving_percent': new_solution.get('improvement', 0)
            }
        }
    
    def _optimize_with_ortools(
        self,
        orders: List[Dict],
        vehicles: List[Dict],
        fixed_routes: List[Dict]
    ) -> Dict:
        """OR-Tools를 사용한 재최적화"""
        
        # 간소화된 구현 (실제로는 더 복잡)
        # 거리 행렬, 시간 창, 용량 제약 등 설정
        
        num_vehicles = len(vehicles)
        num_locations = len(orders) + 1  # depot 포함
        
        # 거리 행렬 생성 (실제로는 Naver API 호출)
        distance_matrix = self._create_distance_matrix(orders, vehicles)
        
        # Routing 모델 생성
        manager = pywrapcp.RoutingIndexManager(
            num_locations,
            num_vehicles,
            0  # depot index
        )
        routing = pywrapcp.RoutingModel(manager)
        
        # 거리 콜백 등록
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distance_matrix[from_node][to_node]
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # 용량 제약
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            if from_node == 0:
                return 0
            return orders[from_node - 1].get('pallets', 0)
        
        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            [v.get('max_pallets', 16) for v in vehicles],
            True,  # start cumul to zero
            'Capacity'
        )
        
        # 검색 파라미터
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.time_limit.seconds = 30  # 30초 제한 (실시간 대응)
        
        # 해 찾기
        solution = routing.SolveWithParameters(search_parameters)
        
        if solution:
            routes = self._extract_routes(manager, routing, solution, orders, vehicles)
            return {
                'routes': routes,
                'total_distance': solution.ObjectiveValue(),
                'computation_time': 30,  # 실제 측정 필요
                'improvement': 0.1  # 10% 개선
            }
        else:
            logger.error("No solution found for redispatch")
            return {'routes': [], 'total_distance': 0, 'computation_time': 0}
    
    def _create_distance_matrix(self, orders: List[Dict], vehicles: List[Dict]) -> List[List[int]]:
        """거리 행렬 생성 (간소화)"""
        size = len(orders) + 1
        # 실제로는 Naver Directions API 호출
        # 여기서는 더미 데이터
        import random
        return [[random.randint(1000, 50000) for _ in range(size)] for _ in range(size)]
    
    def _extract_routes(
        self,
        manager,
        routing,
        solution,
        orders: List[Dict],
        vehicles: List[Dict]
    ) -> List[Dict]:
        """솔루션에서 경로 추출"""
        routes = []
        
        for vehicle_id in range(len(vehicles)):
            index = routing.Start(vehicle_id)
            route_orders = []
            route_distance = 0
            
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                if node_index != 0:  # depot이 아니면
                    route_orders.append(orders[node_index - 1])
                
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )
            
            if route_orders:
                routes.append({
                    'vehicle_id': vehicles[vehicle_id]['id'],
                    'vehicle_number': vehicles[vehicle_id]['vehicle_number'],
                    'orders': route_orders,
                    'total_distance': route_distance,
                    'status': 'PLANNED'
                })
        
        return routes
    
    def _calculate_changes(self, old_routes: List[Dict], new_routes: List[Dict]) -> Dict:
        """변경사항 계산"""
        
        changes = {
            'reassigned_orders': [],
            'affected_vehicles': set(),
            'added_stops': 0,
            'removed_stops': 0
        }
        
        # 주문별 차량 변경 추적
        old_assignment = {}
        for route in old_routes:
            for order in route.get('orders', []):
                old_assignment[order['id']] = route['vehicle_id']
        
        for route in new_routes:
            for order in route.get('orders', []):
                old_vehicle = old_assignment.get(order['id'])
                new_vehicle = route['vehicle_id']
                
                if old_vehicle != new_vehicle:
                    changes['reassigned_orders'].append({
                        'order_id': order['id'],
                        'from_vehicle': old_vehicle,
                        'to_vehicle': new_vehicle
                    })
                    changes['affected_vehicles'].add(old_vehicle)
                    changes['affected_vehicles'].add(new_vehicle)
        
        changes['affected_vehicles'] = list(changes['affected_vehicles'])
        
        return changes


class PredictiveDispatch:
    """예측 기반 선제적 배차"""
    
    def __init__(self):
        self.prediction_horizon = timedelta(hours=2)
    
    def predict_delays(self, routes: List[Dict]) -> List[Dict]:
        """지연 예측"""
        predictions = []
        
        for route in routes:
            # 실제로는 ML 모델 사용
            # - 과거 데이터
            # - 교통 상황
            # - 날씨
            # - 기사 패턴
            
            delay_probability = 0.2  # 20% 확률
            estimated_delay = 15  # 15분
            
            if delay_probability > 0.3:
                predictions.append({
                    'vehicle_id': route['vehicle_id'],
                    'predicted_delay_minutes': estimated_delay,
                    'confidence': delay_probability,
                    'suggested_action': 'Consider alternative vehicle'
                })
        
        return predictions
