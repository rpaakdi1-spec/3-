"""
고급 VRP 최적화 서비스 (OR-Tools CVRPTW)
- Capacitated VRP: 용량 제약
- Time Windows: 시간 제약
- Multiple Depots: 다중 차고지
- Temperature Zones: 온도대 제약
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, time as dt_time
import math

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from sqlalchemy.orm import Session
from loguru import logger

from app.models.client import Client
from app.models.vehicle import Vehicle, VehicleType
from app.models.order import Order, TemperatureZone
from app.models.dispatch import Dispatch, DispatchRoute, RouteType, DispatchStatus
from app.services.naver_map_service import NaverMapService


@dataclass
class Location:
    """위치 데이터 구조"""
    id: int
    name: str
    latitude: float
    longitude: float
    location_type: str  # 'depot', 'pickup', 'delivery'
    order_id: Optional[int] = None
    client_id: Optional[int] = None
    time_window_start: int = 0  # minutes from start of day (e.g., 480 = 08:00)
    time_window_end: int = 1440  # minutes from start of day (e.g., 1080 = 18:00)
    service_time: int = 30  # minutes
    pallet_demand: int = 0  # positive for pickup, negative for delivery
    weight_demand: float = 0.0


@dataclass
class VehicleInfo:
    """차량 정보 구조"""
    id: int
    code: str
    vehicle_type: VehicleType
    max_pallets: int
    max_weight_kg: float
    depot_index: int  # Index in locations list
    start_time: int = 480  # 08:00
    end_time: int = 1080  # 18:00


class CVRPTWSolver:
    """OR-Tools CVRPTW 솔버"""
    
    def __init__(
        self,
        locations: List[Location],
        vehicles: List[VehicleInfo],
        distance_matrix: List[List[int]],
        time_matrix: List[List[int]],
        use_time_windows: bool = True
    ):
        self.locations = locations
        self.vehicles = vehicles
        self.distance_matrix = distance_matrix
        self.time_matrix = time_matrix
        self.use_time_windows = use_time_windows
        
        # OR-Tools 모델
        self.manager = None
        self.routing = None
        self.solution = None
        
    def solve(self, time_limit_seconds: int = 30) -> Optional[Dict[str, Any]]:
        """
        CVRPTW 문제 해결
        
        Args:
            time_limit_seconds: 최대 실행 시간 (초)
            
        Returns:
            최적화 결과 (routes, total_distance, total_time, etc.)
        """
        try:
            logger.info(f"CVRPTW 솔버 시작: {len(self.locations)} 위치, {len(self.vehicles)} 차량")
            
            # 1. 인덱스 매니저 생성
            depot_indices = [v.depot_index for v in self.vehicles]
            self.manager = pywrapcp.RoutingIndexManager(
                len(self.locations),
                len(self.vehicles),
                depot_indices,  # starts
                depot_indices   # ends
            )
            
            # 2. 라우팅 모델 생성
            self.routing = pywrapcp.RoutingModel(self.manager)
            
            # 3. 거리 콜백 등록
            def distance_callback(from_index: int, to_index: int) -> int:
                from_node = self.manager.IndexToNode(from_index)
                to_node = self.manager.IndexToNode(to_index)
                return self.distance_matrix[from_node][to_node]
            
            transit_callback_index = self.routing.RegisterTransitCallback(distance_callback)
            self.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
            
            # 4. 용량 제약 (팔레트)
            def pallet_demand_callback(from_index: int) -> int:
                from_node = self.manager.IndexToNode(from_index)
                return abs(self.locations[from_node].pallet_demand)
            
            pallet_callback_index = self.routing.RegisterUnaryTransitCallback(pallet_demand_callback)
            self.routing.AddDimensionWithVehicleCapacity(
                pallet_callback_index,
                0,  # null capacity slack
                [v.max_pallets for v in self.vehicles],  # vehicle maximum capacities
                True,  # start cumul to zero
                'Pallets'
            )
            
            # 5. 중량 제약
            def weight_demand_callback(from_index: int) -> int:
                from_node = self.manager.IndexToNode(from_index)
                return int(abs(self.locations[from_node].weight_demand))
            
            weight_callback_index = self.routing.RegisterUnaryTransitCallback(weight_demand_callback)
            self.routing.AddDimensionWithVehicleCapacity(
                weight_callback_index,
                0,  # null capacity slack
                [int(v.max_weight_kg) for v in self.vehicles],  # vehicle maximum capacities
                True,  # start cumul to zero
                'Weight'
            )
            
            # 6. 시간 제약 (Time Windows)
            if self.use_time_windows:
                def time_callback(from_index: int, to_index: int) -> int:
                    from_node = self.manager.IndexToNode(from_index)
                    to_node = self.manager.IndexToNode(to_index)
                    travel_time = self.time_matrix[from_node][to_node]
                    service_time = self.locations[from_node].service_time
                    return travel_time + service_time
                
                time_callback_index = self.routing.RegisterTransitCallback(time_callback)
                
                # Time dimension
                time_dimension_name = 'Time'
                self.routing.AddDimension(
                    time_callback_index,
                    60,  # allow waiting time (60 minutes slack)
                    1440,  # maximum time per vehicle (24 hours)
                    False,  # Don't force start cumul to zero
                    time_dimension_name
                )
                
                time_dimension = self.routing.GetDimensionOrDie(time_dimension_name)
                
                # Time windows for each location
                for location_idx, location in enumerate(self.locations):
                    if location.location_type == 'depot':
                        continue  # Skip depot time windows
                    
                    index = self.manager.NodeToIndex(location_idx)
                    time_dimension.CumulVar(index).SetRange(
                        location.time_window_start,
                        location.time_window_end
                    )
                
                # Vehicle time windows
                for vehicle_idx, vehicle in enumerate(self.vehicles):
                    start_index = self.routing.Start(vehicle_idx)
                    end_index = self.routing.End(vehicle_idx)
                    time_dimension.CumulVar(start_index).SetRange(vehicle.start_time, vehicle.end_time)
                    time_dimension.CumulVar(end_index).SetRange(vehicle.start_time, vehicle.end_time)
                
                # Minimize time
                time_dimension.SetGlobalSpanCostCoefficient(100)
            
            # 7. 검색 전략 설정
            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            
            # First solution strategy
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
            )
            
            # Local search metaheuristic
            search_parameters.local_search_metaheuristic = (
                routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
            )
            
            # Time limit
            search_parameters.time_limit.seconds = time_limit_seconds
            
            # Log search progress
            search_parameters.log_search = True
            
            # 8. 솔루션 찾기
            logger.info("OR-Tools 검색 시작...")
            self.solution = self.routing.SolveWithParameters(search_parameters)
            
            if self.solution:
                logger.success("✓ 최적 솔루션 발견!")
                return self._extract_solution()
            else:
                logger.warning("솔루션을 찾지 못했습니다")
                return None
                
        except Exception as e:
            logger.error(f"CVRPTW 솔버 오류: {e}")
            return None
    
    def _extract_solution(self) -> Dict[str, Any]:
        """솔루션에서 경로 추출"""
        routes = []
        total_distance = 0
        total_time = 0
        total_load = 0
        
        for vehicle_idx in range(len(self.vehicles)):
            vehicle = self.vehicles[vehicle_idx]
            index = self.routing.Start(vehicle_idx)
            
            route_distance = 0
            route_time = 0
            route_load = 0
            route_locations = []
            
            while not self.routing.IsEnd(index):
                node_index = self.manager.IndexToNode(index)
                location = self.locations[node_index]
                
                # Time information
                time_var = None
                if self.use_time_windows:
                    time_dimension = self.routing.GetDimensionOrDie('Time')
                    time_var = self.solution.Min(time_dimension.CumulVar(index))
                
                # Capacity information
                pallet_dimension = self.routing.GetDimensionOrDie('Pallets')
                load_var = self.solution.Value(pallet_dimension.CumulVar(index))
                
                route_locations.append({
                    'location_idx': node_index,
                    'location': location,
                    'arrival_time': time_var,
                    'current_load': load_var
                })
                
                # Move to next location
                previous_index = index
                index = self.solution.Value(self.routing.NextVar(index))
                route_distance += self.routing.GetArcCostForVehicle(previous_index, index, vehicle_idx)
            
            # Add final depot
            node_index = self.manager.IndexToNode(index)
            location = self.locations[node_index]
            
            if self.use_time_windows:
                time_dimension = self.routing.GetDimensionOrDie('Time')
                time_var = self.solution.Min(time_dimension.CumulVar(index))
            else:
                time_var = None
            
            route_locations.append({
                'location_idx': node_index,
                'location': location,
                'arrival_time': time_var,
                'current_load': 0
            })
            
            # Only add route if it has more than just start and end depot
            if len(route_locations) > 2:
                route_time = route_locations[-1]['arrival_time'] - route_locations[0]['arrival_time'] if self.use_time_windows else 0
                
                routes.append({
                    'vehicle': vehicle,
                    'locations': route_locations,
                    'distance': route_distance,
                    'time': route_time,
                    'num_stops': len(route_locations) - 2  # Exclude start and end depot
                })
                
                total_distance += route_distance
                total_time += route_time
        
        return {
            'routes': routes,
            'total_distance': total_distance,
            'total_time': total_time,
            'num_vehicles_used': len(routes),
            'objective_value': self.solution.ObjectiveValue()
        }


class AdvancedDispatchOptimizationService:
    """고급 배차 최적화 서비스 (CVRPTW)"""
    
    def __init__(self, db: Session):
        self.db = db
        self.naver_service = NaverMapService()
        
    def _calculate_haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine 거리 계산 (km)"""
        R = 6371  # Earth radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _create_distance_matrix(self, locations: List[Location]) -> List[List[int]]:
        """거리 행렬 생성 (미터) - Haversine"""
        n = len(locations)
        matrix = [[0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist_km = self._calculate_haversine_distance(
                        locations[i].latitude, locations[i].longitude,
                        locations[j].latitude, locations[j].longitude
                    )
                    matrix[i][j] = int(dist_km * 1000)  # Convert to meters
        
        return matrix
    
    async def _create_distance_matrix_naver(self, locations: List[Location]) -> Tuple[List[List[int]], List[List[int]]]:
        """거리/시간 행렬 생성 - Naver Directions API"""
        logger.info(f"Naver Directions API로 거리 행렬 생성 중...")
        
        # 좌표 리스트 추출
        coords = [(loc.latitude, loc.longitude) for loc in locations]
        
        # Naver API 호출
        distance_matrix, time_matrix = await self.naver_service.create_distance_matrix(
            locations=coords,
            use_cache=True,
            batch_size=50,
            delay_ms=100
        )
        
        logger.success(f"✓ Naver API 거리 행렬 생성 완료")
        return distance_matrix, time_matrix
    
    def _create_time_matrix(self, distance_matrix: List[List[int]]) -> List[List[int]]:
        """시간 행렬 생성 (분)"""
        # 평균 속도 40 km/h 가정
        avg_speed_m_per_min = (40 * 1000) / 60  # meters per minute
        
        time_matrix = []
        for row in distance_matrix:
            time_row = [int(dist / avg_speed_m_per_min) for dist in row]
            time_matrix.append(time_row)
        
        return time_matrix
    
    def _time_str_to_minutes(self, time_str: str) -> int:
        """시간 문자열을 분으로 변환 (e.g., "08:00" -> 480)"""
        if not time_str:
            return 0
        
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except:
            return 0
    
    def _convert_temp_zone_to_vehicle_types(self, temp_zone: TemperatureZone) -> List[VehicleType]:
        """온도대를 호환 가능한 차량 타입으로 변환"""
        mapping = {
            TemperatureZone.FROZEN: [VehicleType.FROZEN, VehicleType.DUAL],
            TemperatureZone.REFRIGERATED: [VehicleType.REFRIGERATED, VehicleType.DUAL],
            TemperatureZone.AMBIENT: [VehicleType.AMBIENT, VehicleType.DUAL]
        }
        return mapping.get(temp_zone, [VehicleType.DUAL])
    
    async def optimize_dispatch_cvrptw(
        self,
        order_ids: List[int],
        vehicle_ids: Optional[List[int]] = None,
        dispatch_date: Optional[str] = None,
        time_limit_seconds: int = 30,
        use_time_windows: bool = True,
        use_real_routing: bool = False
    ) -> Dict[str, Any]:
        """
        CVRPTW 알고리즘을 사용한 배차 최적화
        
        Args:
            order_ids: 주문 ID 리스트
            vehicle_ids: 사용할 차량 ID (None = 모든 가용 차량)
            dispatch_date: 배차 날짜 (YYYY-MM-DD)
            time_limit_seconds: 최대 실행 시간 (초)
            use_time_windows: 시간 제약 사용 여부
            use_real_routing: Naver Directions API 사용 여부 (False = Haversine)
            
        Returns:
            최적화 결과
        """
        try:
            logger.info(f"=== CVRPTW 배차 최적화 시작 ===")
            logger.info(f"주문: {len(order_ids)}건, 시간 제한: {time_limit_seconds}초")
            logger.info(f"실제 경로: {'ON (Naver API)' if use_real_routing else 'OFF (Haversine)'}")
            
            # 1. 주문 로드
            orders = self.db.query(Order).filter(Order.id.in_(order_ids)).all()
            if not orders:
                return {"success": False, "error": "주문을 찾을 수 없습니다"}
            
            # 2. 차량 로드
            vehicle_query = self.db.query(Vehicle).filter(Vehicle.is_active == True)
            if vehicle_ids:
                vehicle_query = vehicle_query.filter(Vehicle.id.in_(vehicle_ids))
            vehicles = vehicle_query.all()
            
            if not vehicles:
                return {"success": False, "error": "사용 가능한 차량이 없습니다"}
            
            # 3. 온도대별로 주문 그룹화
            orders_by_temp = {}
            for order in orders:
                if order.temperature_zone not in orders_by_temp:
                    orders_by_temp[order.temperature_zone] = []
                orders_by_temp[order.temperature_zone].append(order)
            
            # 4. 각 온도대별로 최적화
            all_results = []
            
            for temp_zone, zone_orders in orders_by_temp.items():
                logger.info(f"\n온도대 [{temp_zone.value}] 최적화: {len(zone_orders)}건")
                
                # 호환 가능한 차량 필터링
                compatible_types = self._convert_temp_zone_to_vehicle_types(temp_zone)
                compatible_vehicles = [v for v in vehicles if v.vehicle_type in compatible_types]
                
                if not compatible_vehicles:
                    logger.warning(f"온도대 [{temp_zone.value}]에 호환 차량 없음")
                    continue
                
                # 온도대별 최적화 실행
                result = await self._optimize_temperature_zone(
                    zone_orders,
                    compatible_vehicles,
                    dispatch_date,
                    time_limit_seconds,
                    use_time_windows,
                    use_real_routing
                )
                
                if result:
                    all_results.append(result)
            
            # 5. 결과 취합
            total_dispatches = sum(r['num_dispatches'] for r in all_results)
            total_distance = sum(r['total_distance'] for r in all_results)
            
            logger.success(f"\n=== 최적화 완료 ===")
            logger.info(f"생성된 배차: {total_dispatches}개")
            logger.info(f"총 거리: {total_distance/1000:.2f} km")
            
            return {
                "success": True,
                "total_orders": len(orders),
                "total_dispatches": total_dispatches,
                "total_distance_km": round(total_distance / 1000, 2),
                "temperature_zones": [
                    {
                        "zone": temp_zone.value,
                        "orders": len(zone_orders),
                        "dispatches": result['num_dispatches'],
                        "distance_km": round(result['total_distance'] / 1000, 2)
                    }
                    for (temp_zone, zone_orders), result in zip(orders_by_temp.items(), all_results)
                ],
                "dispatches": [d for r in all_results for d in r['dispatches']]
            }
            
        except Exception as e:
            logger.error(f"CVRPTW 최적화 오류: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def _optimize_temperature_zone(
        self,
        orders: List[Order],
        vehicles: List[Vehicle],
        dispatch_date: Optional[str],
        time_limit_seconds: int,
        use_time_windows: bool,
        use_real_routing: bool
    ) -> Optional[Dict[str, Any]]:
        """특정 온도대의 주문을 최적화"""
        
        # 위치 리스트 구축
        locations = []
        location_map = {}
        
        # 차고지 추가 (depot)
        depot_lat = 37.5665  # 서울 기본 좌표
        depot_lon = 126.9780
        
        # 첫 번째 차량의 차고지 사용 (또는 기본 좌표)
        if vehicles[0].garage_latitude and vehicles[0].garage_longitude:
            depot_lat = vehicles[0].garage_latitude
            depot_lon = vehicles[0].garage_longitude
        
        depot_idx = 0
        locations.append(Location(
            id=0,
            name="차고지",
            latitude=depot_lat,
            longitude=depot_lon,
            location_type='depot'
        ))
        
        # 주문의 상차/하차 위치 추가
        for order in orders:
            # 상차 위치
            pickup_client = order.pickup_client
            if pickup_client.id not in location_map:
                loc_idx = len(locations)
                location_map[f"pickup_{pickup_client.id}"] = loc_idx
                
                locations.append(Location(
                    id=loc_idx,
                    name=f"{pickup_client.name} (상차)",
                    latitude=pickup_client.latitude or depot_lat,
                    longitude=pickup_client.longitude or depot_lon,
                    location_type='pickup',
                    order_id=order.id,
                    client_id=pickup_client.id,
                    time_window_start=self._time_str_to_minutes(pickup_client.pickup_start_time or "08:00"),
                    time_window_end=self._time_str_to_minutes(pickup_client.pickup_end_time or "18:00"),
                    service_time=pickup_client.loading_time_minutes,
                    pallet_demand=order.pallet_count,
                    weight_demand=order.weight_kg
                ))
            
            # 하차 위치
            delivery_client = order.delivery_client
            if delivery_client.id not in location_map:
                loc_idx = len(locations)
                location_map[f"delivery_{delivery_client.id}"] = loc_idx
                
                locations.append(Location(
                    id=loc_idx,
                    name=f"{delivery_client.name} (하차)",
                    latitude=delivery_client.latitude or depot_lat,
                    longitude=delivery_client.longitude or depot_lon,
                    location_type='delivery',
                    order_id=order.id,
                    client_id=delivery_client.id,
                    time_window_start=self._time_str_to_minutes(delivery_client.delivery_start_time or "08:00"),
                    time_window_end=self._time_str_to_minutes(delivery_client.delivery_end_time or "18:00"),
                    service_time=delivery_client.loading_time_minutes,
                    pallet_demand=-order.pallet_count,
                    weight_demand=-order.weight_kg
                ))
        
        logger.info(f"위치: {len(locations)}개 (차고지 1 + 주문 위치 {len(locations)-1})")
        
        # 차량 정보 구축
        vehicle_infos = []
        for vehicle in vehicles:
            vehicle_infos.append(VehicleInfo(
                id=vehicle.id,
                code=vehicle.code,
                vehicle_type=vehicle.vehicle_type,
                max_pallets=vehicle.max_pallets,
                max_weight_kg=vehicle.max_weight_kg,
                depot_index=depot_idx,
                start_time=480,  # 08:00
                end_time=1080    # 18:00
            ))
        
        logger.info(f"차량: {len(vehicle_infos)}대")
        
        # 거리/시간 행렬 생성
        if use_real_routing:
            logger.info("🗺️  Naver Directions API 사용")
            distance_matrix, time_matrix = await self._create_distance_matrix_naver(locations)
        else:
            logger.info("📐 Haversine 거리 사용")
            distance_matrix = self._create_distance_matrix(locations)
            time_matrix = self._create_time_matrix(distance_matrix)
        
        # CVRPTW 솔버 실행
        solver = CVRPTWSolver(
            locations=locations,
            vehicles=vehicle_infos,
            distance_matrix=distance_matrix,
            time_matrix=time_matrix,
            use_time_windows=use_time_windows
        )
        
        solution = solver.solve(time_limit_seconds=time_limit_seconds)
        
        if not solution:
            logger.warning("솔루션을 찾지 못했습니다")
            return None
        
        # 데이터베이스에 저장
        saved_dispatches = await self._save_solution_to_db(
            solution,
            orders,
            vehicles,
            locations,
            dispatch_date
        )
        
        return {
            'num_dispatches': len(saved_dispatches),
            'total_distance': solution['total_distance'],
            'total_time': solution['total_time'],
            'dispatches': saved_dispatches
        }
    
    async def _save_solution_to_db(
        self,
        solution: Dict[str, Any],
        orders: List[Order],
        vehicles: List[Vehicle],
        locations: List[Location],
        dispatch_date: Optional[str]
    ) -> List[Dict[str, Any]]:
        """솔루션을 데이터베이스에 저장"""
        
        saved_dispatches = []
        
        for route_data in solution['routes']:
            vehicle_info = route_data['vehicle']
            vehicle = next(v for v in vehicles if v.id == vehicle_info.id)
            
            # 배차 번호 생성
            dispatch_number = f"DISP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{vehicle.code}"
            
            # 배차 생성
            dispatch = Dispatch(
                dispatch_number=dispatch_number,
                dispatch_date=datetime.strptime(dispatch_date, '%Y-%m-%d').date() if dispatch_date else datetime.now().date(),
                vehicle_id=vehicle.id,
                total_orders=route_data['num_stops'],
                total_distance_km=route_data['distance'] / 1000,
                estimated_duration_minutes=route_data['time'] if route_data['time'] else 0,
                status=DispatchStatus.DRAFT
            )
            
            self.db.add(dispatch)
            self.db.flush()
            
            # 경로 생성
            for seq, loc_data in enumerate(route_data['locations'], start=1):
                location = loc_data['location']
                
                # 경로 타입 결정
                if location.location_type == 'depot':
                    route_type = RouteType.GARAGE_START if seq == 1 else RouteType.GARAGE_END
                elif location.location_type == 'pickup':
                    route_type = RouteType.PICKUP
                else:
                    route_type = RouteType.DELIVERY
                
                route = DispatchRoute(
                    dispatch_id=dispatch.id,
                    sequence=seq,
                    route_type=route_type,
                    order_id=location.order_id,
                    location_name=location.name,
                    address=f"주소-{location.name}",
                    latitude=location.latitude,
                    longitude=location.longitude,
                    estimated_arrival_time=f"{loc_data['arrival_time']//60:02d}:{loc_data['arrival_time']%60:02d}" if loc_data['arrival_time'] else None,
                    current_pallets=loc_data['current_load']
                )
                
                self.db.add(route)
            
            self.db.commit()
            self.db.refresh(dispatch)
            
            saved_dispatches.append({
                'id': dispatch.id,
                'dispatch_number': dispatch.dispatch_number,
                'vehicle_code': vehicle.code,
                'num_stops': route_data['num_stops'],
                'distance_km': round(route_data['distance'] / 1000, 2),
                'duration_min': route_data['time']
            })
            
            logger.info(f"✓ 배차 저장: {dispatch_number} ({route_data['num_stops']}개 정류장)")
        
        return saved_dispatches
