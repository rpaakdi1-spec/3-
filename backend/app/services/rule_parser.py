"""
Rule Parser - JSON 규칙 조건을 파싱하고 검증
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, time
import re


class RuleParser:
    """규칙 조건 파서"""
    
    # 지원하는 연산자
    OPERATORS = {
        'eq': lambda a, b: a == b,
        'ne': lambda a, b: a != b,
        'gt': lambda a, b: a > b,
        'gte': lambda a, b: a >= b,
        'lt': lambda a, b: a < b,
        'lte': lambda a, b: a <= b,
        'in': lambda a, b: a in b,
        'not_in': lambda a, b: a not in b,
        'contains': lambda a, b: b in a if isinstance(a, (list, str)) else False,
        'startswith': lambda a, b: a.startswith(b) if isinstance(a, str) else False,
        'endswith': lambda a, b: a.endswith(b) if isinstance(a, str) else False,
        'regex': lambda a, b: bool(re.match(b, str(a))),
        'between': lambda a, b: b[0] <= a <= b[1] if isinstance(b, (list, tuple)) and len(b) == 2 else False,
    }
    
    def __init__(self):
        pass
    
    def parse_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        규칙 조건을 파싱하고 평가
        
        Args:
            conditions: 규칙 조건 JSON
            context: 평가 컨텍스트 (order, vehicle, driver 등의 데이터)
            
        Returns:
            bool: 조건이 참이면 True, 거짓이면 False
        """
        if not conditions:
            return True
        
        # AND/OR 로직 처리
        if 'AND' in conditions:
            return all(self.parse_conditions(cond, context) for cond in conditions['AND'])
        
        if 'OR' in conditions:
            return any(self.parse_conditions(cond, context) for cond in conditions['OR'])
        
        if 'NOT' in conditions:
            return not self.parse_conditions(conditions['NOT'], context)
        
        # if 블록 처리
        if 'if' in conditions:
            return self._evaluate_if_block(conditions['if'], context)
        
        # 단일 조건 처리
        return self._evaluate_single_condition(conditions, context)
    
    def _evaluate_if_block(self, if_block: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """if 블록 평가"""
        results = []
        
        for key, value in if_block.items():
            if key in ['AND', 'OR', 'NOT']:
                # 재귀 처리
                result = self.parse_conditions({key: value}, context)
                results.append(result)
            else:
                # 필드 조건 평가
                result = self._evaluate_field_condition(key, value, context)
                results.append(result)
        
        # 기본은 AND 로직
        return all(results)
    
    def _evaluate_single_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """단일 조건 평가"""
        for key, value in condition.items():
            if key in ['AND', 'OR', 'NOT']:
                continue
            return self._evaluate_field_condition(key, value, context)
        return True
    
    def _evaluate_field_condition(self, field_path: str, condition_value: Any, context: Dict[str, Any]) -> bool:
        """
        필드 조건 평가
        
        Args:
            field_path: 필드 경로 (예: "order.weight_kg", "vehicle.type")
            condition_value: 조건 값 또는 연산자 객체
            context: 평가 컨텍스트
            
        Returns:
            bool: 조건 만족 여부
        """
        # 필드 값 가져오기
        actual_value = self._get_field_value(field_path, context)
        
        # 조건 값이 딕셔너리면 연산자 사용
        if isinstance(condition_value, dict):
            return self._evaluate_operator_condition(actual_value, condition_value)
        
        # 단순 비교 (equals)
        return actual_value == condition_value
    
    def _get_field_value(self, field_path: str, context: Dict[str, Any]) -> Any:
        """
        필드 경로에서 값 추출
        
        예: "order.weight_kg" -> context['order']['weight_kg']
        """
        parts = field_path.split('.')
        value = context
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return None
            
            if value is None:
                return None
        
        return value
    
    def _evaluate_operator_condition(self, actual_value: Any, operator_dict: Dict[str, Any]) -> bool:
        """
        연산자 조건 평가
        
        예: {"$gt": 100} -> actual_value > 100
        """
        for operator_key, expected_value in operator_dict.items():
            # $ 제거
            operator = operator_key.lstrip('$')
            
            if operator not in self.OPERATORS:
                raise ValueError(f"Unsupported operator: {operator}")
            
            operator_func = self.OPERATORS[operator]
            
            # 특수 값 처리
            if isinstance(expected_value, str):
                expected_value = self._resolve_special_value(expected_value, actual_value)
            
            try:
                result = operator_func(actual_value, expected_value)
                if not result:
                    return False
            except Exception as e:
                # 비교 실패 시 False 반환
                return False
        
        return True
    
    def _resolve_special_value(self, value_str: str, context_value: Any = None) -> Any:
        """
        특수 값 처리
        
        예: "NOW()", "TODAY()", "order.weight_kg * 1.2"
        """
        value_str = value_str.strip()
        
        # NOW()
        if value_str == 'NOW()':
            return datetime.now()
        
        # TODAY()
        if value_str == 'TODAY()':
            return datetime.now().date()
        
        # 수식 평가 (간단한 경우만)
        if '*' in value_str or '+' in value_str or '-' in value_str:
            try:
                # 안전한 eval (제한적)
                return eval(value_str, {"__builtins__": {}}, {})
            except:
                return value_str
        
        return value_str
    
    def validate_rule(self, rule: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        규칙 검증
        
        Returns:
            (is_valid, error_message)
        """
        # 필수 필드 확인
        if 'conditions' not in rule:
            return False, "Missing 'conditions' field"
        
        if 'actions' not in rule:
            return False, "Missing 'actions' field"
        
        # 조건 구조 검증
        try:
            self._validate_conditions(rule['conditions'])
        except Exception as e:
            return False, f"Invalid conditions: {str(e)}"
        
        # 액션 구조 검증
        try:
            self._validate_actions(rule['actions'])
        except Exception as e:
            return False, f"Invalid actions: {str(e)}"
        
        return True, None
    
    def _validate_conditions(self, conditions: Any):
        """조건 구조 검증"""
        if not isinstance(conditions, dict):
            raise ValueError("Conditions must be a dictionary")
        
        # 재귀 검증
        for key, value in conditions.items():
            if key in ['AND', 'OR']:
                if not isinstance(value, list):
                    raise ValueError(f"{key} must be a list")
                for item in value:
                    self._validate_conditions(item)
            elif key == 'NOT':
                self._validate_conditions(value)
    
    def _validate_actions(self, actions: Any):
        """액션 구조 검증"""
        if not isinstance(actions, dict):
            raise ValueError("Actions must be a dictionary")
        
        # 최소한 하나의 액션 필요
        if not actions:
            raise ValueError("At least one action is required")
