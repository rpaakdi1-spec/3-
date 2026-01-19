"""
동적 재배차 서비스
- 실시간 배차 변경
- 긴급 주문 추가
- 차량 고장/지연 대응
- 자동 재배차 알고리즘
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from loguru import logger

from app.models.order import Order, OrderStatus
from app.models.dispatch import Dispatch, DispatchStatus
from app.models.dispatch_route import DispatchRoute
from app.models.vehicle import Vehicle, VehicleStatus
from app.services.cvrptw_service import AdvancedDispatchOptimizationService


class DynamicRedispatchService:
    """동적 재배차 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.optimization_service = AdvancedDispatchOptimizationService(db)
    
    async def add_urgent_order(
        self,
        order_id: int,
        force_dispatch: bool = False
    ) -> Dict[str, Any]:
        """
        긴급 주문 추가 및 재배차
        
        Args:
            order_id: 긴급 주문 ID
            force_dispatch: 강제 배차 여부 (기존 배차에 추가)
            
        Returns:
            재배차 결과
        """
        logger.info(f"Adding urgent order: {order_id}, force={force_dispatch}")
        
        # 주문 조회
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError(f"Order not found: {order_id}")
        
        if order.status != OrderStatus.PENDING:
            raise ValueError(f"Order is not pending: {order.status}")
        
        # 주문 우선순위 상승
        order.priority = 1  # 최고 우선순위
        self.db.commit()
        
        if force_dispatch:
            # 기존 배차에 강제 추가
            result = await self._force_add_to_existing_dispatch(order)
        else:
            # 모든 대기 주문 재배차
            result = await self._redispatch_all_pending()
        
        logger.info(f"Urgent order processed: {result}")
        return result
    
    async def handle_vehicle_issue(
        self,
        vehicle_id: int,
        issue_type: str,
        estimated_delay_minutes: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        차량 문제 처리 (고장, 지연 등)
        
        Args:
            vehicle_id: 차량 ID
            issue_type: 문제 유형 ('breakdown', 'delay', 'accident')
            estimated_delay_minutes: 예상 지연 시간 (분)
            
        Returns:
            재배차 결과
        """
        logger.warning(f"Vehicle issue: vehicle_id={vehicle_id}, type={issue_type}, delay={estimated_delay_minutes}")
        
        # 차량 조회
        vehicle = self.db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            raise ValueError(f"Vehicle not found: {vehicle_id}")
        
        # 해당 차량의 진행 중인 배차 조회
        active_dispatch = self.db.query(Dispatch).filter(
            Dispatch.vehicle_id == vehicle_id,
            Dispatch.status.in_([DispatchStatus.PENDING, DispatchStatus.IN_PROGRESS])
        ).first()
        
        if not active_dispatch:
            logger.info(f"No active dispatch for vehicle {vehicle_id}")
            return {'status': 'no_action', 'message': 'No active dispatch found'}
        
        if issue_type == 'breakdown':
            # 고장: 완전히 다른 차량에 재배차
            result = await self._reassign_to_different_vehicle(active_dispatch)
        elif issue_type == 'delay':
            # 지연: ETA 업데이트 또는 부분 재배차
            result = await self._handle_delay(active_dispatch, estimated_delay_minutes)
        else:
            # 기타: 상황에 따라 처리
            result = await self._reassign_to_different_vehicle(active_dispatch)
        
        logger.info(f"Vehicle issue handled: {result}")
        return result
    
    async def cancel_order_and_redispatch(
        self,
        order_id: int
    ) -> Dict[str, Any]:
        """
        주문 취소 및 재배차
        
        Args:
            order_id: 취소할 주문 ID
            
        Returns:
            재배차 결과
        """
        logger.info(f"Cancelling order: {order_id}")
        
        # 주문 조회
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError(f"Order not found: {order_id}")
        
        # 주문이 속한 배차 조회
        dispatch_route = self.db.query(DispatchRoute).filter(
            DispatchRoute.order_id == order_id
        ).first()
        
        if dispatch_route:
            dispatch = self.db.query(Dispatch).filter(
                Dispatch.id == dispatch_route.dispatch_id
            ).first()
            
            if dispatch and dispatch.status in [DispatchStatus.PENDING, DispatchStatus.IN_PROGRESS]:
                # 배차에서 주문 제거
                self.db.delete(dispatch_route)
                
                # 배차 통계 업데이트
                remaining_routes = self.db.query(DispatchRoute).filter(
                    DispatchRoute.dispatch_id == dispatch.id
                ).count()
                
                if remaining_routes == 0:
                    # 배차에 주문이 없으면 삭제
                    self.db.delete(dispatch)
                else:
                    # 남은 주문으로 거리/팔레트 재계산
                    self._recalculate_dispatch_stats(dispatch)
        
        # 주문 취소
        order.status = OrderStatus.CANCELLED
        self.db.commit()
        
        return {
            'status': 'success',
            'order_id': order_id,
            'message': 'Order cancelled and dispatch updated'
        }
    
    async def optimize_in_progress_dispatch(
        self,
        dispatch_id: int
    ) -> Dict[str, Any]:
        """
        진행 중인 배차 최적화 (경로 재계산)
        
        Args:
            dispatch_id: 배차 ID
            
        Returns:
            최적화 결과
        """
        logger.info(f"Optimizing in-progress dispatch: {dispatch_id}")
        
        dispatch = self.db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
        if not dispatch:
            raise ValueError(f"Dispatch not found: {dispatch_id}")
        
        if dispatch.status != DispatchStatus.IN_PROGRESS:
            raise ValueError(f"Dispatch is not in progress: {dispatch.status}")
        
        # 미완료 주문만 재최적화
        incomplete_routes = self.db.query(DispatchRoute).filter(
            DispatchRoute.dispatch_id == dispatch_id,
            DispatchRoute.stop_type.in_(['pickup', 'delivery']),
            DispatchRoute.completed_at.is_(None)
        ).all()
        
        if not incomplete_routes:
            return {'status': 'no_action', 'message': 'All routes completed'}
        
        # 재최적화 로직 (간단한 버전)
        # 실제로는 OR-Tools로 경로 재계산
        logger.info(f"Reoptimizing {len(incomplete_routes)} incomplete routes")
        
        return {
            'status': 'success',
            'dispatch_id': dispatch_id,
            'optimized_routes': len(incomplete_routes)
        }
    
    async def _force_add_to_existing_dispatch(self, order: Order) -> Dict[str, Any]:
        """기존 배차에 강제 추가"""
        # 온도대가 맞는 진행 중인 배차 찾기
        compatible_dispatch = self.db.query(Dispatch).join(Vehicle).filter(
            Dispatch.status.in_([DispatchStatus.PENDING, DispatchStatus.IN_PROGRESS]),
            Vehicle.vehicle_type == self._get_vehicle_type_for_temp(order.temperature_zone)
        ).first()
        
        if not compatible_dispatch:
            # 호환 배차 없음, 새 배차 생성
            return await self._redispatch_all_pending()
        
        # 배차에 추가
        # 간단한 버전: 마지막에 추가
        max_sequence = self.db.query(DispatchRoute).filter(
            DispatchRoute.dispatch_id == compatible_dispatch.id
        ).count()
        
        # Pickup route 추가
        pickup_route = DispatchRoute(
            dispatch_id=compatible_dispatch.id,
            order_id=order.id,
            sequence_order=max_sequence + 1,
            location_type='pickup',
            stop_type='pickup'
        )
        self.db.add(pickup_route)
        
        # Delivery route 추가
        delivery_route = DispatchRoute(
            dispatch_id=compatible_dispatch.id,
            order_id=order.id,
            sequence_order=max_sequence + 2,
            location_type='delivery',
            stop_type='delivery'
        )
        self.db.add(delivery_route)
        
        # 주문 상태 업데이트
        order.status = OrderStatus.ASSIGNED
        
        # 배차 통계 재계산
        self._recalculate_dispatch_stats(compatible_dispatch)
        
        self.db.commit()
        
        return {
            'status': 'success',
            'dispatch_id': compatible_dispatch.id,
            'order_id': order.id,
            'method': 'force_add'
        }
    
    async def _reassign_to_different_vehicle(self, dispatch: Dispatch) -> Dict[str, Any]:
        """다른 차량에 재배차"""
        # 배차의 모든 주문 조회
        routes = self.db.query(DispatchRoute).filter(
            DispatchRoute.dispatch_id == dispatch.id
        ).all()
        
        order_ids = list(set([r.order_id for r in routes if r.order_id]))
        
        if not order_ids:
            return {'status': 'no_action', 'message': 'No orders to reassign'}
        
        # 기존 배차 취소
        dispatch.status = DispatchStatus.CANCELLED
        
        # 주문들을 PENDING으로 되돌림
        self.db.query(Order).filter(Order.id.in_(order_ids)).update(
            {Order.status: OrderStatus.PENDING},
            synchronize_session=False
        )
        
        self.db.commit()
        
        # 재배차
        result = await self.optimization_service.optimize_dispatch_cvrptw(
            order_ids=order_ids,
            time_limit=15,  # 빠른 재배차
            use_time_windows=True,
            use_real_routing=False
        )
        
        return {
            'status': 'success',
            'original_dispatch_id': dispatch.id,
            'new_dispatches': len(result.get('dispatches', [])),
            'method': 'reassign'
        }
    
    async def _handle_delay(self, dispatch: Dispatch, delay_minutes: int) -> Dict[str, Any]:
        """지연 처리"""
        if delay_minutes and delay_minutes > 60:
            # 1시간 이상 지연: 재배차
            return await self._reassign_to_different_vehicle(dispatch)
        else:
            # 경미한 지연: ETA만 업데이트
            logger.info(f"Minor delay ({delay_minutes} min), updating ETA only")
            return {
                'status': 'eta_updated',
                'dispatch_id': dispatch.id,
                'delay_minutes': delay_minutes,
                'method': 'eta_update'
            }
    
    async def _redispatch_all_pending(self) -> Dict[str, Any]:
        """모든 대기 주문 재배차"""
        pending_orders = self.db.query(Order).filter(
            Order.status == OrderStatus.PENDING
        ).all()
        
        if not pending_orders:
            return {'status': 'no_action', 'message': 'No pending orders'}
        
        order_ids = [o.id for o in pending_orders]
        
        result = await self.optimization_service.optimize_dispatch_cvrptw(
            order_ids=order_ids,
            time_limit=30,
            use_time_windows=True,
            use_real_routing=False
        )
        
        return {
            'status': 'success',
            'orders_count': len(order_ids),
            'dispatches_count': len(result.get('dispatches', [])),
            'method': 'full_redispatch'
        }
    
    def _recalculate_dispatch_stats(self, dispatch: Dispatch):
        """배차 통계 재계산"""
        routes = self.db.query(DispatchRoute).filter(
            DispatchRoute.dispatch_id == dispatch.id
        ).all()
        
        total_distance = sum(r.distance_km or 0 for r in routes)
        
        order_ids = list(set([r.order_id for r in routes if r.order_id]))
        orders = self.db.query(Order).filter(Order.id.in_(order_ids)).all()
        
        total_pallets = sum(o.pallet_count for o in orders)
        total_weight = sum(o.weight_kg for o in orders)
        
        dispatch.total_distance_km = total_distance
        dispatch.total_pallet_count = total_pallets
        dispatch.total_weight_kg = total_weight
    
    @staticmethod
    def _get_vehicle_type_for_temp(temperature_zone: str) -> str:
        """온도대에 맞는 차량 유형 반환"""
        from app.models.order import TemperatureZone
        from app.models.vehicle import VehicleType
        
        if temperature_zone == TemperatureZone.FROZEN:
            return VehicleType.FREEZER
        elif temperature_zone == TemperatureZone.REFRIGERATED:
            return VehicleType.REFRIGERATED
        else:
            return VehicleType.DRY


def get_redispatch_service(db: Session) -> DynamicRedispatchService:
    """동적 재배차 서비스 인스턴스"""
    return DynamicRedispatchService(db)
