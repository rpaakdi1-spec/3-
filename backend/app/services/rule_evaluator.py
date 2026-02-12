"""
Rule Evaluator - 규칙 평가 및 실행
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, time
import time as time_module
from sqlalchemy.orm import Session

from app.services.rule_parser import RuleParser
from app.models.dispatch_rule import DispatchRule, RuleExecutionLog
from app.models.dispatch import Dispatch
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.order import Order


class RuleEvaluator:
    """규칙 평가 및 실행"""
    
    def __init__(self, db: Session):
        self.db = db
        self.parser = RuleParser()
    
    def evaluate_rules(self, context: Dict[str, Any], rule_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        모든 활성 규칙을 평가하고 매칭되는 규칙 반환
        
        Args:
            context: 평가 컨텍스트 (order, vehicle, driver 등)
            rule_type: 규칙 타입 필터 (assignment, constraint, optimization)
            
        Returns:
            매칭된 규칙 리스트
        """
        # 활성 규칙 조회
        query = self.db.query(DispatchRule).filter(DispatchRule.is_active == True)
        
        if rule_type:
            query = query.filter(DispatchRule.rule_type == rule_type)
        
        # 우선순위 순으로 정렬
        rules = query.order_by(DispatchRule.priority.desc()).all()
        
        matched_rules = []
        
        for rule in rules:
            # 시간 제약 확인
            if not self._check_time_constraints(rule):
                continue
            
            # 규칙 평가
            start_time = time_module.time()
            try:
                if self.parser.parse_conditions(rule.conditions, context):
                    execution_time = int((time_module.time() - start_time) * 1000)
                    matched_rules.append({
                        'rule': rule,
                        'actions': rule.actions,
                        'execution_time_ms': execution_time
                    })
            except Exception as e:
                # 평가 실패 시 로그
                self._log_execution(rule, context, success=False, error_message=str(e))
        
        return matched_rules
    
    def execute_rules(self, matched_rules: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        매칭된 규칙들의 액션 실행
        
        Args:
            matched_rules: 매칭된 규칙 리스트
            context: 실행 컨텍스트
            
        Returns:
            실행 결과
        """
        results = {
            'executed_rules': [],
            'actions_taken': [],
            'constraints_applied': [],
            'assignment_result': None
        }
        
        for matched_rule in matched_rules:
            rule = matched_rule['rule']
            actions = matched_rule['actions']
            
            try:
                # 액션 실행
                action_result = self._execute_actions(rule, actions, context)
                
                results['executed_rules'].append({
                    'rule_id': rule.id,
                    'rule_name': rule.name,
                    'rule_type': rule.rule_type,
                    'priority': rule.priority
                })
                
                if action_result:
                    if rule.rule_type == 'assignment':
                        results['assignment_result'] = action_result
                    elif rule.rule_type == 'constraint':
                        results['constraints_applied'].append(action_result)
                    
                    results['actions_taken'].append(action_result)
                
                # 성공 로그
                self._log_execution(rule, context, success=True, output_data=action_result)
                
                # 통계 업데이트
                self._update_rule_stats(rule, success=True, execution_time_ms=matched_rule['execution_time_ms'])
                
            except Exception as e:
                # 실패 로그
                self._log_execution(rule, context, success=False, error_message=str(e))
                self._update_rule_stats(rule, success=False)
        
        return results
    
    def _check_time_constraints(self, rule: DispatchRule) -> bool:
        """시간 제약 확인"""
        now = datetime.now()
        current_time = now.time()
        current_day = now.strftime('%a').upper()[:3]  # MON, TUE, ...
        
        # 시간 제약
        if rule.apply_time_start and rule.apply_time_end:
            if not (rule.apply_time_start <= current_time <= rule.apply_time_end):
                return False
        
        # 요일 제약
        if rule.apply_days:
            days = [d.strip() for d in rule.apply_days.split(',')]
            
            if 'WEEKEND' in days:
                if current_day not in ['SAT', 'SUN']:
                    return False
            elif 'WEEKDAY' in days:
                if current_day in ['SAT', 'SUN']:
                    return False
            elif current_day not in days:
                return False
        
        return True
    
    def _execute_actions(self, rule: DispatchRule, actions: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        액션 실행
        
        Args:
            rule: 규칙
            actions: 액션 정의
            context: 실행 컨텍스트
            
        Returns:
            액션 실행 결과
        """
        result = {
            'rule_id': rule.id,
            'rule_name': rule.name,
            'actions_executed': []
        }
        
        for action_key, action_value in actions.items():
            action_result = self._execute_single_action(action_key, action_value, context)
            if action_result:
                result['actions_executed'].append({
                    'action': action_key,
                    'value': action_value,
                    'result': action_result
                })
        
        return result
    
    def _execute_single_action(self, action_key: str, action_value: Any, context: Dict[str, Any]) -> Any:
        """단일 액션 실행"""
        
        # assign_to 액션
        if action_key == 'assign_to':
            return self._handle_assignment_action(action_value, context)
        
        # require_vehicle_type 액션
        elif action_key == 'require_vehicle_type':
            return self._handle_vehicle_type_constraint(action_value, context)
        
        # max_distance_km 액션
        elif action_key == 'max_distance_km':
            return {'constraint': 'max_distance', 'value': action_value}
        
        # notify 액션
        elif action_key in ['notify_dispatcher', 'notify_client', 'notify_driver']:
            return {'notification': action_key, 'enabled': action_value}
        
        # 일반 액션
        else:
            return {'action': action_key, 'value': action_value}
    
    def _handle_assignment_action(self, assign_to: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """배차 할당 액션 처리"""
        
        if assign_to == 'nearest_available_vehicle':
            return self._find_nearest_vehicle(context)
        
        elif assign_to == 'driver':
            # 특정 드라이버 조건 확인
            return {'assign_to': 'driver', 'criteria': context.get('driver_tags')}
        
        elif assign_to == 'vehicle':
            return {'assign_to': 'vehicle', 'criteria': context.get('vehicle_condition')}
        
        return {'assign_to': assign_to}
    
    def _find_nearest_vehicle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """가장 가까운 차량 찾기"""
        order = context.get('order')
        if not order:
            return None
        
        # 가용 차량 조회 (간단한 예시)
        available_vehicles = self.db.query(Vehicle).filter(
            Vehicle.status == 'AVAILABLE'
        ).limit(10).all()
        
        if not available_vehicles:
            return None
        
        # 거리 계산 (실제로는 좌표 기반 계산 필요)
        # 여기서는 첫 번째 차량 반환
        nearest = available_vehicles[0]
        
        return {
            'vehicle_id': nearest.id,
            'vehicle_number': nearest.vehicle_number,
            'method': 'nearest_available'
        }
    
    def _handle_vehicle_type_constraint(self, vehicle_types: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """차량 타입 제약 처리"""
        
        if isinstance(vehicle_types, str):
            vehicle_types = [vehicle_types]
        
        return {
            'constraint': 'vehicle_type',
            'required_types': vehicle_types
        }
    
    def _log_execution(self, rule: DispatchRule, context: Dict[str, Any], 
                       success: bool, output_data: Optional[Dict] = None,
                       error_message: Optional[str] = None):
        """규칙 실행 로그 저장"""
        
        log = RuleExecutionLog(
            rule_id=rule.id,
            dispatch_id=context.get('dispatch_id'),
            executed_at=datetime.now(),
            input_data=self._sanitize_context(context),
            output_data=output_data,
            success=success,
            error_message=error_message
        )
        
        self.db.add(log)
        self.db.commit()
    
    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """컨텍스트를 JSON 저장 가능한 형태로 변환"""
        sanitized = {}
        
        for key, value in context.items():
            if hasattr(value, '__dict__'):
                # ORM 객체를 dict로 변환
                sanitized[key] = {
                    'id': getattr(value, 'id', None),
                    'type': type(value).__name__
                }
            elif isinstance(value, (str, int, float, bool, list, dict)):
                sanitized[key] = value
        
        return sanitized
    
    def _update_rule_stats(self, rule: DispatchRule, success: bool, execution_time_ms: Optional[int] = None):
        """규칙 통계 업데이트"""
        
        rule.execution_count += 1
        
        if execution_time_ms:
            if rule.avg_execution_time_ms:
                # 이동 평균
                rule.avg_execution_time_ms = (rule.avg_execution_time_ms * 0.9) + (execution_time_ms * 0.1)
            else:
                rule.avg_execution_time_ms = float(execution_time_ms)
        
        # 성공률 계산
        if success:
            if rule.success_rate is None:
                rule.success_rate = 1.0
            else:
                # 이동 평균
                rule.success_rate = (rule.success_rate * 0.95) + 0.05
        else:
            if rule.success_rate is None:
                rule.success_rate = 0.0
            else:
                rule.success_rate = rule.success_rate * 0.95
        
        self.db.commit()
