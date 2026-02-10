"""
Advanced Condition Parser for Rule Simulation
복잡한 조건 조합 (AND, OR, NOT) 처리
"""
from typing import Dict, Any, List, Union
from enum import Enum


class ConditionOperator(str, Enum):
    """조건 연산자"""
    EQ = "=="
    NE = "!="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"


class LogicalOperator(str, Enum):
    """논리 연산자"""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class ConditionParser:
    """고급 조건 파서"""
    
    def __init__(self):
        self.operators = {
            "==": self._eq,
            "!=": self._ne,
            ">": self._gt,
            ">=": self._gte,
            "<": self._lt,
            "<=": self._lte,
            "in": self._in,
            "not_in": self._not_in,
            "contains": self._contains,
            "starts_with": self._starts_with,
            "ends_with": self._ends_with,
        }
    
    def evaluate(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        조건 평가
        
        Args:
            conditions: 조건 정의
            context: 평가 컨텍스트 (실제 데이터)
            
        Returns:
            bool: 조건 만족 여부
            
        Examples:
            # 단순 조건
            conditions = {"distance_km": {"<=": 5}}
            context = {"distance_km": 3}
            
            # 복합 조건 (AND)
            conditions = {
                "AND": [
                    {"distance_km": {"<=": 5}},
                    {"driver_rating": {">=": 4.5}}
                ]
            }
            
            # 복합 조건 (OR + AND)
            conditions = {
                "AND": [
                    {"distance_km": {"<=": 5}},
                    {"OR": [
                        {"vehicle_type": "냉동차"},
                        {"vehicle_type": "냉장차"}
                    ]}
                ]
            }
        """
        return self._evaluate_recursive(conditions, context)
    
    def _evaluate_recursive(self, conditions: Union[Dict, List], context: Dict[str, Any]) -> bool:
        """재귀적 조건 평가"""
        
        if isinstance(conditions, list):
            # 리스트는 AND로 처리
            return all(self._evaluate_recursive(cond, context) for cond in conditions)
        
        if not isinstance(conditions, dict):
            raise ValueError(f"Invalid condition type: {type(conditions)}")
        
        # 논리 연산자 처리
        if "AND" in conditions:
            return self._evaluate_and(conditions["AND"], context)
        
        if "OR" in conditions:
            return self._evaluate_or(conditions["OR"], context)
        
        if "NOT" in conditions:
            return not self._evaluate_recursive(conditions["NOT"], context)
        
        # 단순 조건 평가
        return self._evaluate_simple_conditions(conditions, context)
    
    def _evaluate_and(self, conditions: List[Dict], context: Dict[str, Any]) -> bool:
        """AND 연산 평가"""
        return all(self._evaluate_recursive(cond, context) for cond in conditions)
    
    def _evaluate_or(self, conditions: List[Dict], context: Dict[str, Any]) -> bool:
        """OR 연산 평가"""
        return any(self._evaluate_recursive(cond, context) for cond in conditions)
    
    def _evaluate_simple_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """단순 조건들 평가 (AND 결합)"""
        for field, condition in conditions.items():
            if not self._evaluate_single_condition(field, condition, context):
                return False
        return True
    
    def _evaluate_single_condition(
        self, 
        field: str, 
        condition: Union[Dict, Any], 
        context: Dict[str, Any]
    ) -> bool:
        """단일 조건 평가"""
        
        # 컨텍스트에서 필드 값 가져오기 (중첩 필드 지원)
        value = self._get_nested_value(context, field)
        
        if isinstance(condition, dict):
            # 연산자 기반 조건
            for op, expected in condition.items():
                if op in self.operators:
                    if not self.operators[op](value, expected):
                        return False
                else:
                    raise ValueError(f"Unknown operator: {op}")
            return True
        else:
            # 직접 비교 (==)
            return value == condition
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """중첩된 필드 값 가져오기 (예: "order.client.name")"""
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
    
    # 연산자 구현
    def _eq(self, value: Any, expected: Any) -> bool:
        return value == expected
    
    def _ne(self, value: Any, expected: Any) -> bool:
        return value != expected
    
    def _gt(self, value: Any, expected: Any) -> bool:
        if value is None:
            return False
        return value > expected
    
    def _gte(self, value: Any, expected: Any) -> bool:
        if value is None:
            return False
        return value >= expected
    
    def _lt(self, value: Any, expected: Any) -> bool:
        if value is None:
            return False
        return value < expected
    
    def _lte(self, value: Any, expected: Any) -> bool:
        if value is None:
            return False
        return value <= expected
    
    def _in(self, value: Any, expected: List) -> bool:
        if value is None:
            return False
        return value in expected
    
    def _not_in(self, value: Any, expected: List) -> bool:
        if value is None:
            return True
        return value not in expected
    
    def _contains(self, value: Any, expected: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return expected in value
        if isinstance(value, (list, tuple)):
            return expected in value
        return False
    
    def _starts_with(self, value: Any, expected: str) -> bool:
        if value is None or not isinstance(value, str):
            return False
        return value.startswith(expected)
    
    def _ends_with(self, value: Any, expected: str) -> bool:
        if value is None or not isinstance(value, str):
            return False
        return value.endswith(expected)


def validate_conditions(conditions: Dict[str, Any]) -> List[str]:
    """
    조건 구조 검증
    
    Returns:
        List[str]: 오류 메시지 리스트 (빈 리스트면 유효함)
    """
    errors = []
    
    try:
        _validate_recursive(conditions, errors, path="root")
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")
    
    return errors


def _validate_recursive(conditions: Union[Dict, List], errors: List[str], path: str):
    """재귀적 조건 검증"""
    
    if isinstance(conditions, list):
        for i, cond in enumerate(conditions):
            _validate_recursive(cond, errors, f"{path}[{i}]")
        return
    
    if not isinstance(conditions, dict):
        errors.append(f"{path}: Must be dict or list, got {type(conditions)}")
        return
    
    # 논리 연산자 검증
    logical_ops = ["AND", "OR", "NOT"]
    logical_found = [op for op in logical_ops if op in conditions]
    
    if len(logical_found) > 1:
        errors.append(f"{path}: Multiple logical operators found: {logical_found}")
    
    if logical_found:
        op = logical_found[0]
        if op in ["AND", "OR"]:
            if not isinstance(conditions[op], list):
                errors.append(f"{path}.{op}: Must be a list")
            else:
                for i, cond in enumerate(conditions[op]):
                    _validate_recursive(cond, errors, f"{path}.{op}[{i}]")
        elif op == "NOT":
            _validate_recursive(conditions[op], errors, f"{path}.NOT")
    else:
        # 단순 조건 검증
        for field, condition in conditions.items():
            if isinstance(condition, dict):
                valid_operators = ["==", "!=", ">", ">=", "<", "<=", "in", "not_in", 
                                 "contains", "starts_with", "ends_with"]
                for op in condition.keys():
                    if op not in valid_operators:
                        errors.append(f"{path}.{field}: Unknown operator '{op}'")
