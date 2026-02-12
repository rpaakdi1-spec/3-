"""
Rule Engine - 규칙 엔진 메인 클래스
"""
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.services.rule_parser import RuleParser
from app.services.rule_evaluator import RuleEvaluator
from app.models.dispatch_rule import DispatchRule
from app.models.order import Order
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.dispatch import Dispatch


class RuleEngine:
    """스마트 배차 규칙 엔진"""
    
    def __init__(self, db: Session):
        self.db = db
        self.parser = RuleParser()
        self.evaluator = RuleEvaluator(db)
    
    def apply_rules_to_order(self, order_id: int, dry_run: bool = False) -> Dict[str, Any]:
        """
        주문에 규칙 적용
        
        Args:
            order_id: 주문 ID
            dry_run: True면 실제 변경 없이 시뮬레이션만
            
        Returns:
            규칙 적용 결과
        """
        # 주문 조회
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return {'error': 'Order not found'}
        
        # 컨텍스트 구성
        context = self._build_context(order=order)
        
        # 규칙 평가
        matched_rules = self.evaluator.evaluate_rules(context)
        
        if not matched_rules:
            return {
                'order_id': order_id,
                'matched_rules': 0,
                'message': 'No rules matched'
            }
        
        # 규칙 실행
        if not dry_run:
            result = self.evaluator.execute_rules(matched_rules, context)
        else:
            result = {
                'matched_rules': [
                    {
                        'rule_id': mr['rule'].id,
                        'rule_name': mr['rule'].name,
                        'rule_type': mr['rule'].rule_type,
                        'priority': mr['rule'].priority,
                        'actions': mr['actions']
                    }
                    for mr in matched_rules
                ],
                'dry_run': True
            }
        
        return result
    
    def find_best_vehicle(self, order_id: int, optimization_config_id: Optional[int] = None) -> Dict[str, Any]:
        """
        주문에 최적의 차량 찾기 (규칙 + 최적화)
        
        Args:
            order_id: 주문 ID
            optimization_config_id: 최적화 설정 ID
            
        Returns:
            추천 차량 정보
        """
        # 주문 조회
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return {'error': 'Order not found'}
        
        # 컨텍스트 구성
        context = self._build_context(order=order)
        
        # Step 1: 제약 조건 규칙 평가
        constraint_rules = self.evaluator.evaluate_rules(context, rule_type='constraint')
        constraints = []
        
        for mr in constraint_rules:
            rule = mr['rule']
            actions = mr['actions']
            
            # 제약 조건 수집
            if 'require_vehicle_type' in actions:
                constraints.append({
                    'type': 'vehicle_type',
                    'value': actions['require_vehicle_type']
                })
            
            if 'require_vehicle_capacity_kg' in actions:
                constraints.append({
                    'type': 'capacity',
                    'value': actions['require_vehicle_capacity_kg']
                })
        
        # Step 2: 제약 조건 만족하는 차량 필터링
        query = self.db.query(Vehicle).filter(Vehicle.status == 'AVAILABLE')
        
        for constraint in constraints:
            if constraint['type'] == 'vehicle_type':
                types = constraint['value']
                if isinstance(types, str):
                    types = [types]
                query = query.filter(Vehicle.vehicle_type.in_(types))
            
            elif constraint['type'] == 'capacity':
                min_capacity = constraint['value']
                query = query.filter(Vehicle.capacity_kg >= min_capacity)
        
        candidate_vehicles = query.all()
        
        if not candidate_vehicles:
            return {
                'order_id': order_id,
                'recommended_vehicle': None,
                'reason': 'No vehicles match the constraints',
                'constraints': constraints
            }
        
        # Step 3: 배정 규칙 평가
        assignment_rules = self.evaluator.evaluate_rules(context, rule_type='assignment')
        
        recommended_vehicle = None
        assignment_method = 'default'
        
        if assignment_rules:
            # 가장 높은 우선순위 규칙 사용
            top_rule = assignment_rules[0]
            actions = top_rule['actions']
            
            if 'assign_to' in actions:
                assignment_method = actions['assign_to']
                
                if assignment_method == 'nearest_available_vehicle':
                    # 거리 기반 선택
                    recommended_vehicle = candidate_vehicles[0]  # 간단한 예시
        
        # 기본: 첫 번째 후보
        if not recommended_vehicle:
            recommended_vehicle = candidate_vehicles[0]
        
        return {
            'order_id': order_id,
            'recommended_vehicle': {
                'id': recommended_vehicle.id,
                'vehicle_number': recommended_vehicle.vehicle_number,
                'vehicle_type': recommended_vehicle.vehicle_type,
                'capacity_kg': recommended_vehicle.capacity_kg
            },
            'assignment_method': assignment_method,
            'applied_rules': len(constraint_rules) + len(assignment_rules),
            'constraints': constraints,
            'total_candidates': len(candidate_vehicles)
        }
    
    def simulate_rules(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        규칙 시뮬레이션 (테스트 데이터 사용)
        
        Args:
            test_data: 테스트 주문/차량/드라이버 데이터
            
        Returns:
            시뮬레이션 결과
        """
        context = test_data
        
        # 모든 규칙 평가
        matched_rules = self.evaluator.evaluate_rules(context)
        
        return {
            'test_data': test_data,
            'matched_rules_count': len(matched_rules),
            'matched_rules': [
                {
                    'rule_id': mr['rule'].id,
                    'rule_name': mr['rule'].name,
                    'rule_type': mr['rule'].rule_type,
                    'priority': mr['rule'].priority,
                    'conditions': mr['rule'].conditions,
                    'actions': mr['actions'],
                    'execution_time_ms': mr['execution_time_ms']
                }
                for mr in matched_rules
            ]
        }
    
    def evaluate_single_rule(self, rule_id: int, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        단일 규칙 평가 (테스트용)
        
        Args:
            rule_id: 규칙 ID
            test_data: 테스트 데이터
            
        Returns:
            평가 결과
        """
        rule = self.db.query(DispatchRule).filter(DispatchRule.id == rule_id).first()
        if not rule:
            return {'error': 'Rule not found'}
        
        try:
            matched = self.parser.parse_conditions(rule.conditions, test_data)
            
            return {
                'rule_id': rule_id,
                'rule_name': rule.name,
                'matched': matched,
                'conditions': rule.conditions,
                'actions': rule.actions if matched else None,
                'test_data': test_data
            }
        except Exception as e:
            return {
                'rule_id': rule_id,
                'error': str(e),
                'test_data': test_data
            }
    
    def _build_context(self, order: Optional[Order] = None, 
                      vehicle: Optional[Vehicle] = None,
                      driver: Optional[Driver] = None,
                      dispatch: Optional[Dispatch] = None) -> Dict[str, Any]:
        """규칙 평가 컨텍스트 구성"""
        context = {}
        
        if order:
            context['order'] = {
                'id': order.id,
                'order_number': order.order_number,
                'client_id': order.client_id,
                'pickup_address': order.pickup_address,
                'delivery_address': order.delivery_address,
                'total_weight_kg': order.total_weight_kg,
                'total_pallets': order.total_pallets,
                'is_urgent': order.is_urgent,
                'status': order.status.value if hasattr(order.status, 'value') else order.status,
                'delivery_deadline': order.delivery_deadline,
                'temperature_range': getattr(order, 'temperature_range', None),
                'product_type': getattr(order, 'product_type', None)
            }
            
            # 클라이언트 정보 추가
            if order.client:
                context['client'] = {
                    'id': order.client.id,
                    'name': order.client.company_name,
                    'tier': getattr(order.client, 'tier', 'STANDARD')
                }
        
        if vehicle:
            context['vehicle'] = {
                'id': vehicle.id,
                'vehicle_number': vehicle.vehicle_number,
                'vehicle_type': vehicle.vehicle_type,
                'capacity_kg': vehicle.capacity_kg,
                'status': vehicle.status.value if hasattr(vehicle.status, 'value') else vehicle.status,
                'age_years': getattr(vehicle, 'age_years', 0)
            }
        
        if driver:
            context['driver'] = {
                'id': driver.id,
                'name': driver.name,
                'license_type': driver.license_type,
                'tags': getattr(driver, 'tags', [])
            }
        
        if dispatch:
            context['dispatch'] = {
                'id': dispatch.id,
                'dispatch_number': dispatch.dispatch_number,
                'status': dispatch.status.value if hasattr(dispatch.status, 'value') else dispatch.status
            }
            context['dispatch_id'] = dispatch.id
        
        return context
