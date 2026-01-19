from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
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
    """Location data structure"""
    id: int
    name: str
    latitude: float
    longitude: float
    location_type: str  # 'garage', 'pickup', 'delivery'
    order_id: Optional[int] = None
    time_window_start: Optional[int] = None  # minutes from start of day
    time_window_end: Optional[int] = None
    service_time: int = 30  # minutes


@dataclass
class VehicleData:
    """Vehicle data structure"""
    id: int
    code: str
    vehicle_type: VehicleType
    max_pallets: int
    max_weight_kg: float
    garage_lat: Optional[float]
    garage_lon: Optional[float]


@dataclass
class OrderData:
    """Order data structure"""
    id: int
    order_number: str
    temperature_zone: TemperatureZone
    pickup_client_id: int
    delivery_client_id: int
    pallet_count: int
    weight_kg: float
    priority: int


class DispatchOptimizationService:
    """AI-based dispatch optimization using Google OR-Tools"""
    
    def __init__(self, db: Session):
        self.db = db
        self.naver_service = NaverMapService()
        
    def _convert_temp_zone_to_vehicle_type(self, temp_zone: TemperatureZone) -> List[VehicleType]:
        """Convert temperature zone to compatible vehicle types"""
        if temp_zone == TemperatureZone.FROZEN:
            return [VehicleType.FROZEN, VehicleType.DUAL]
        elif temp_zone == TemperatureZone.REFRIGERATED:
            return [VehicleType.REFRIGERATED, VehicleType.DUAL]
        else:  # AMBIENT
            return [VehicleType.AMBIENT, VehicleType.DUAL]
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate Haversine distance between two points in kilometers"""
        R = 6371  # Earth radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _create_distance_matrix(self, locations: List[Location]) -> List[List[int]]:
        """Create distance matrix between all locations (in meters)"""
        n = len(locations)
        matrix = [[0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist_km = self._calculate_distance(
                        locations[i].latitude, locations[i].longitude,
                        locations[j].latitude, locations[j].longitude
                    )
                    matrix[i][j] = int(dist_km * 1000)  # Convert to meters
        
        return matrix
    
    def _create_time_matrix(self, distance_matrix: List[List[int]]) -> List[List[int]]:
        """Create time matrix from distance matrix (in minutes)"""
        # Assume average speed of 40 km/h in city
        avg_speed_m_per_min = (40 * 1000) / 60  # meters per minute
        
        time_matrix = []
        for row in distance_matrix:
            time_row = [int(dist / avg_speed_m_per_min) for dist in row]
            time_matrix.append(time_row)
        
        return time_matrix
    
    async def optimize_dispatch(
        self,
        order_ids: List[int],
        vehicle_ids: Optional[List[int]] = None,
        dispatch_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Optimize dispatch using OR-Tools VRP
        
        Args:
            order_ids: List of order IDs to dispatch
            vehicle_ids: Optional list of vehicle IDs to use (None = all available)
            dispatch_date: Date for dispatch (YYYY-MM-DD format)
            
        Returns:
            Dict with optimization results and dispatch plans
        """
        try:
            logger.info(f"Starting dispatch optimization for {len(order_ids)} orders")
            
            # Load orders
            orders = self.db.query(Order).filter(Order.id.in_(order_ids)).all()
            if not orders:
                return {"success": False, "error": "주문을 찾을 수 없습니다"}
            
            # Group orders by temperature zone
            orders_by_temp = {}
            for order in orders:
                if order.temperature_zone not in orders_by_temp:
                    orders_by_temp[order.temperature_zone] = []
                orders_by_temp[order.temperature_zone].append(order)
            
            # Load available vehicles
            vehicle_query = self.db.query(Vehicle).filter(Vehicle.is_active == True)
            if vehicle_ids:
                vehicle_query = vehicle_query.filter(Vehicle.id.in_(vehicle_ids))
            
            vehicles = vehicle_query.all()
            if not vehicles:
                return {"success": False, "error": "사용 가능한 차량이 없습니다"}
            
            # Optimize for each temperature zone
            all_dispatch_plans = []
            
            for temp_zone, zone_orders in orders_by_temp.items():
                logger.info(f"Optimizing {temp_zone} orders: {len(zone_orders)} orders")
                
                # Filter compatible vehicles
                compatible_types = self._convert_temp_zone_to_vehicle_type(temp_zone)
                compatible_vehicles = [v for v in vehicles if v.vehicle_type in compatible_types]
                
                if not compatible_vehicles:
                    logger.warning(f"No compatible vehicles for {temp_zone}")
                    continue
                
                # Create dispatch plan for this temperature zone
                dispatch_plan = await self._optimize_zone(zone_orders, compatible_vehicles)
                if dispatch_plan:
                    all_dispatch_plans.extend(dispatch_plan)
            
            # Save dispatches to database
            saved_dispatches = []
            for plan in all_dispatch_plans:
                dispatch = await self._save_dispatch(plan, dispatch_date)
                if dispatch:
                    saved_dispatches.append(dispatch)
            
            logger.info(f"Optimization complete: {len(saved_dispatches)} dispatches created")
            
            return {
                "success": True,
                "total_orders": len(orders),
                "total_dispatches": len(saved_dispatches),
                "dispatches": [self._format_dispatch_response(d) for d in saved_dispatches]
            }
            
        except Exception as e:
            logger.error(f"Dispatch optimization error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _optimize_zone(
        self,
        orders: List[Order],
        vehicles: List[Vehicle]
    ) -> List[Dict[str, Any]]:
        """Optimize dispatch for a single temperature zone"""
        
        # Build locations list
        locations = []
        location_map = {}
        
        # Add vehicle garages as depots
        depot_indices = []
        for vehicle in vehicles:
            if vehicle.garage_latitude and vehicle.garage_longitude:
                depot_idx = len(locations)
                depot_indices.append(depot_idx)
                locations.append(Location(
                    id=vehicle.id,
                    name=f"차고지-{vehicle.code}",
                    latitude=vehicle.garage_latitude,
                    longitude=vehicle.garage_longitude,
                    location_type='garage'
                ))
        
        # If no garages, use first client as depot
        if not depot_indices:
            first_order = orders[0]
            pickup_client = first_order.pickup_client
            depot_idx = 0
            depot_indices = [depot_idx]
            locations.append(Location(
                id=pickup_client.id,
                name=pickup_client.name,
                latitude=pickup_client.latitude or 37.5665,
                longitude=pickup_client.longitude or 126.9780,
                location_type='garage'
            ))
        
        # Add order pickup and delivery locations
        for order in orders:
            # Pickup location
            pickup_client = order.pickup_client
            if pickup_client.id not in location_map:
                pickup_idx = len(locations)
                location_map[pickup_client.id] = pickup_idx
                locations.append(Location(
                    id=pickup_client.id,
                    name=pickup_client.name,
                    latitude=pickup_client.latitude or 37.5665,
                    longitude=pickup_client.longitude or 126.9780,
                    location_type='pickup',
                    order_id=order.id,
                    service_time=pickup_client.loading_time_minutes
                ))
            
            # Delivery location
            delivery_client = order.delivery_client
            if delivery_client.id not in location_map:
                delivery_idx = len(locations)
                location_map[delivery_client.id] = delivery_idx
                locations.append(Location(
                    id=delivery_client.id,
                    name=delivery_client.name,
                    latitude=delivery_client.latitude or 37.5665,
                    longitude=delivery_client.longitude or 126.9780,
                    location_type='delivery',
                    order_id=order.id,
                    service_time=delivery_client.loading_time_minutes
                ))
        
        # Create distance and time matrices
        distance_matrix = self._create_distance_matrix(locations)
        time_matrix = self._create_time_matrix(distance_matrix)
        
        # Simple greedy assignment (for PoC)
        dispatch_plans = []
        remaining_orders = orders.copy()
        
        for vehicle in vehicles:
            if not remaining_orders:
                break
            
            vehicle_orders = []
            current_pallets = 0
            current_weight = 0
            
            # Greedily assign orders to vehicle
            for order in remaining_orders[:]:
                if (current_pallets + order.pallet_count <= vehicle.max_pallets and
                    current_weight + order.weight_kg <= vehicle.max_weight_kg):
                    vehicle_orders.append(order)
                    current_pallets += order.pallet_count
                    current_weight += order.weight_kg
                    remaining_orders.remove(order)
            
            if vehicle_orders:
                dispatch_plans.append({
                    'vehicle': vehicle,
                    'orders': vehicle_orders,
                    'total_pallets': current_pallets,
                    'total_weight': current_weight,
                    'locations': locations,
                    'distance_matrix': distance_matrix
                })
        
        logger.info(f"Created {len(dispatch_plans)} dispatch plans for zone")
        return dispatch_plans
    
    async def _save_dispatch(self, plan: Dict[str, Any], dispatch_date: Optional[str]) -> Optional[Dispatch]:
        """Save dispatch plan to database"""
        try:
            vehicle = plan['vehicle']
            orders = plan['orders']
            
            # Generate dispatch number
            dispatch_number = f"DISP-{datetime.now().strftime('%Y%m%d')}-{vehicle.code}"
            
            # Create dispatch
            dispatch = Dispatch(
                dispatch_number=dispatch_number,
                dispatch_date=datetime.strptime(dispatch_date, '%Y-%m-%d').date() if dispatch_date else datetime.now().date(),
                vehicle_id=vehicle.id,
                total_orders=len(orders),
                total_pallets=plan['total_pallets'],
                total_weight_kg=plan['total_weight'],
                status=DispatchStatus.DRAFT
            )
            
            self.db.add(dispatch)
            self.db.flush()
            
            # Create routes
            sequence = 1
            
            # Start from garage
            if vehicle.garage_latitude and vehicle.garage_longitude:
                route = DispatchRoute(
                    dispatch_id=dispatch.id,
                    sequence=sequence,
                    route_type=RouteType.GARAGE_START,
                    location_name=f"차고지-{vehicle.code}",
                    address=vehicle.garage_address or "차고지",
                    latitude=vehicle.garage_latitude,
                    longitude=vehicle.garage_longitude,
                    current_pallets=0,
                    current_weight_kg=0
                )
                self.db.add(route)
                sequence += 1
            
            # Add pickup and delivery routes
            current_pallets = 0
            current_weight = 0
            
            for order in orders:
                # Pickup
                pickup_client = order.pickup_client
                current_pallets += order.pallet_count
                current_weight += order.weight_kg
                
                route = DispatchRoute(
                    dispatch_id=dispatch.id,
                    sequence=sequence,
                    route_type=RouteType.PICKUP,
                    order_id=order.id,
                    location_name=pickup_client.name,
                    address=pickup_client.address,
                    latitude=pickup_client.latitude or 37.5665,
                    longitude=pickup_client.longitude or 126.9780,
                    estimated_work_duration_minutes=pickup_client.loading_time_minutes,
                    current_pallets=current_pallets,
                    current_weight_kg=current_weight
                )
                self.db.add(route)
                sequence += 1
                
                # Delivery
                delivery_client = order.delivery_client
                current_pallets -= order.pallet_count
                current_weight -= order.weight_kg
                
                route = DispatchRoute(
                    dispatch_id=dispatch.id,
                    sequence=sequence,
                    route_type=RouteType.DELIVERY,
                    order_id=order.id,
                    location_name=delivery_client.name,
                    address=delivery_client.address,
                    latitude=delivery_client.latitude or 37.5665,
                    longitude=delivery_client.longitude or 126.9780,
                    estimated_work_duration_minutes=delivery_client.loading_time_minutes,
                    current_pallets=current_pallets,
                    current_weight_kg=current_weight
                )
                self.db.add(route)
                sequence += 1
                
                # Update order status
                order.status = 'assigned'
            
            # End at garage
            if vehicle.garage_latitude and vehicle.garage_longitude:
                route = DispatchRoute(
                    dispatch_id=dispatch.id,
                    sequence=sequence,
                    route_type=RouteType.GARAGE_END,
                    location_name=f"차고지-{vehicle.code}",
                    address=vehicle.garage_address or "차고지",
                    latitude=vehicle.garage_latitude,
                    longitude=vehicle.garage_longitude,
                    current_pallets=0,
                    current_weight_kg=0
                )
                self.db.add(route)
            
            self.db.commit()
            self.db.refresh(dispatch)
            
            logger.info(f"Saved dispatch: {dispatch_number}")
            return dispatch
            
        except Exception as e:
            logger.error(f"Error saving dispatch: {e}")
            self.db.rollback()
            return None
    
    def _format_dispatch_response(self, dispatch: Dispatch) -> Dict[str, Any]:
        """Format dispatch for API response"""
        return {
            "id": dispatch.id,
            "dispatch_number": dispatch.dispatch_number,
            "dispatch_date": dispatch.dispatch_date.isoformat(),
            "vehicle_id": dispatch.vehicle_id,
            "vehicle_code": dispatch.vehicle.code if dispatch.vehicle else None,
            "total_orders": dispatch.total_orders,
            "total_pallets": dispatch.total_pallets,
            "total_weight_kg": dispatch.total_weight_kg,
            "status": dispatch.status.value,
            "routes": [
                {
                    "sequence": route.sequence,
                    "route_type": route.route_type.value,
                    "location_name": route.location_name,
                    "address": route.address,
                    "latitude": route.latitude,
                    "longitude": route.longitude,
                    "current_pallets": route.current_pallets,
                    "current_weight_kg": route.current_weight_kg
                }
                for route in sorted(dispatch.routes, key=lambda r: r.sequence)
            ]
        }
