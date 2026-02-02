"""
Phase 1: Basic Constraints Utility Functions

이 모듈은 Phase 1의 4가지 핵심 기능을 구현합니다:
1. 파렛트 타입 구분 (11형/12형)
2. 온도대별 차량 매칭
3. 24시간 기준 하차시간 계산
4. 차량 길이별 적재량 계산
"""

from datetime import datetime, time, timedelta
from typing import Optional, Dict, Tuple
from enum import Enum


class PalletType(str, Enum):
    """파렛트 타입"""
    TYPE_11 = "11형"
    TYPE_12 = "12형"


class TemperatureZone(str, Enum):
    """온도대 구분"""
    FROZEN = "냉동"
    CHILLED = "냉장"
    AMBIENT = "상온"


# ============================================
# 1. 파렛트 타입 관련 함수
# ============================================

VEHICLE_CAPACITY_RULES = {
    9.5: {"11형": 20, "12형": 17},
    11.0: {"11형": 24, "12형": 20},
    12.0: {"11형": 26, "12형": 22},
    14.0: {"11형": 30, "12형": 26},
}


def get_vehicle_capacity_by_pallet_type(
    vehicle_length_m: float,
    pallet_type: str
) -> int:
    """차량 길이와 파렛트 타입에 따른 최대 적재량 반환
    
    Args:
        vehicle_length_m: 차량 길이 (미터)
        pallet_type: 파렛트 타입 ("11형" 또는 "12형")
    
    Returns:
        int: 최대 적재 가능 팔레트 수
    
    Example:
        >>> get_vehicle_capacity_by_pallet_type(9.5, "12형")
        17
    """
    if vehicle_length_m in VEHICLE_CAPACITY_RULES:
        return VEHICLE_CAPACITY_RULES[vehicle_length_m].get(pallet_type, 0)
    
    # 길이 정보가 없는 경우 가장 가까운 값 사용
    closest_length = min(
        VEHICLE_CAPACITY_RULES.keys(),
        key=lambda x: abs(x - vehicle_length_m)
    )
    return VEHICLE_CAPACITY_RULES[closest_length].get(pallet_type, 0)


def calculate_remaining_capacity(
    vehicle_length_m: float,
    current_load_11: int,
    current_load_12: int
) -> Dict[str, int]:
    """차량의 남은 적재 공간 계산
    
    Args:
        vehicle_length_m: 차량 길이 (미터)
        current_load_11: 현재 적재된 11형 팔레트 수
        current_load_12: 현재 적재된 12형 팔레트 수
    
    Returns:
        dict: {"11형": 남은_팔레트_수, "12형": 남은_팔레트_수}
    
    Example:
        >>> calculate_remaining_capacity(9.5, 10, 5)
        {"11형": 10, "12형": 12}
    """
    max_11 = get_vehicle_capacity_by_pallet_type(vehicle_length_m, "11형")
    max_12 = get_vehicle_capacity_by_pallet_type(vehicle_length_m, "12형")
    
    return {
        "11형": max(0, max_11 - current_load_11),
        "12형": max(0, max_12 - current_load_12)
    }


# ============================================
# 2. 온도대별 차량 매칭
# ============================================

def is_temperature_compatible(
    vehicle_supports: Dict[str, bool],
    order_temperature_zone: str
) -> bool:
    """차량과 주문의 온도대 호환성 체크
    
    Args:
        vehicle_supports: {
            "supports_frozen": bool,
            "supports_chilled": bool,
            "supports_ambient": bool
        }
        order_temperature_zone: 주문 온도대 ("냉동", "냉장", "상온")
    
    Returns:
        bool: 호환 가능 여부
    
    Example:
        >>> vehicle = {"supports_frozen": True, "supports_chilled": True, "supports_ambient": False}
        >>> is_temperature_compatible(vehicle, "냉동")
        True
        >>> is_temperature_compatible(vehicle, "상온")
        False
    """
    if order_temperature_zone == TemperatureZone.FROZEN:
        return vehicle_supports.get("supports_frozen", False)
    elif order_temperature_zone == TemperatureZone.CHILLED:
        return vehicle_supports.get("supports_chilled", False)
    elif order_temperature_zone == TemperatureZone.AMBIENT:
        return vehicle_supports.get("supports_ambient", True)
    
    return False


def get_compatible_vehicles(
    vehicles: list,
    order_temperature_zone: str
) -> list:
    """주문 온도대와 호환되는 차량 필터링
    
    Args:
        vehicles: 차량 리스트
        order_temperature_zone: 주문 온도대
    
    Returns:
        list: 호환 가능한 차량 리스트
    """
    compatible = []
    
    for vehicle in vehicles:
        supports = {
            "supports_frozen": getattr(vehicle, "supports_frozen", False),
            "supports_chilled": getattr(vehicle, "supports_chilled", False),
            "supports_ambient": getattr(vehicle, "supports_ambient", True)
        }
        
        if is_temperature_compatible(supports, order_temperature_zone):
            compatible.append(vehicle)
    
    return compatible


# ============================================
# 3. 24시간 기준 하차시간 계산
# ============================================

def calculate_delivery_datetime(
    order_datetime: datetime,
    delivery_time_str: str
) -> datetime:
    """24시간 기준으로 하차시간 자동 계산
    
    현재 시간이 20시이고 하차시간이 04시면 다음날로 자동 인식
    
    Args:
        order_datetime: 주문 일시
        delivery_time_str: 하차시간 문자열 ("HH:MM" 형식)
    
    Returns:
        datetime: 계산된 하차 일시
    
    Example:
        >>> order_time = datetime(2026, 2, 2, 20, 0)  # 2026-02-02 20:00
        >>> calculate_delivery_datetime(order_time, "04:00")
        datetime(2026, 2, 3, 4, 0)  # 다음날 새벽 4시
        
        >>> order_time = datetime(2026, 2, 2, 10, 0)  # 2026-02-02 10:00
        >>> calculate_delivery_datetime(order_time, "14:00")
        datetime(2026, 2, 2, 14, 0)  # 같은 날 오후 2시
    """
    # 시간 문자열 파싱
    try:
        hour, minute = map(int, delivery_time_str.split(':'))
    except (ValueError, AttributeError):
        raise ValueError(f"Invalid time format: {delivery_time_str}. Expected 'HH:MM'")
    
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"Invalid time: {hour}:{minute}")
    
    order_hour = order_datetime.hour
    
    # 기본 하차 일시 설정 (같은 날)
    delivery_datetime = order_datetime.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0
    )
    
    # 로직 1: 하차시간이 주문시간보다 이르면 다음날로 간주
    if hour < order_hour:
        delivery_datetime += timedelta(days=1)
    
    # 로직 2: 자정 넘는 특수 케이스 (22:00 ~ 06:00 사이)
    # 예: 23시 주문, 01시 하차 → 다음날
    elif order_hour >= 22 and hour <= 6:
        delivery_datetime += timedelta(days=1)
    
    return delivery_datetime


def parse_time_window(
    start_time_str: Optional[str],
    end_time_str: Optional[str]
) -> Tuple[Optional[time], Optional[time]]:
    """타임 윈도우 문자열을 time 객체로 변환
    
    Args:
        start_time_str: 시작시간 ("HH:MM")
        end_time_str: 종료시간 ("HH:MM")
    
    Returns:
        tuple: (start_time, end_time)
    """
    start_time = None
    end_time = None
    
    if start_time_str:
        try:
            hour, minute = map(int, start_time_str.split(':'))
            start_time = time(hour, minute)
        except (ValueError, AttributeError):
            pass
    
    if end_time_str:
        try:
            hour, minute = map(int, end_time_str.split(':'))
            end_time = time(hour, minute)
        except (ValueError, AttributeError):
            pass
    
    return start_time, end_time


# ============================================
# 4. 차량 길이별 적재량 계산
# ============================================

def validate_vehicle_capacity(
    vehicle_length_m: float,
    pallet_type: str,
    requested_pallets: int
) -> Tuple[bool, str]:
    """차량 적재 가능 여부 검증
    
    Args:
        vehicle_length_m: 차량 길이
        pallet_type: 파렛트 타입
        requested_pallets: 요청 팔레트 수
    
    Returns:
        tuple: (가능여부, 메시지)
    
    Example:
        >>> validate_vehicle_capacity(9.5, "12형", 15)
        (True, "가능: 15/17 팔레트")
        
        >>> validate_vehicle_capacity(9.5, "12형", 20)
        (False, "불가능: 20팔레트 요청, 최대 17팔레트")
    """
    max_capacity = get_vehicle_capacity_by_pallet_type(vehicle_length_m, pallet_type)
    
    if requested_pallets <= max_capacity:
        return True, f"가능: {requested_pallets}/{max_capacity} 팔레트"
    else:
        return False, f"불가능: {requested_pallets}팔레트 요청, 최대 {max_capacity}팔레트"


def calculate_vehicle_utilization(
    vehicle_length_m: float,
    pallet_type: str,
    current_load: int
) -> float:
    """차량 적재율 계산
    
    Args:
        vehicle_length_m: 차량 길이
        pallet_type: 파렛트 타입
        current_load: 현재 적재량
    
    Returns:
        float: 적재율 (0.0 ~ 1.0)
    
    Example:
        >>> calculate_vehicle_utilization(9.5, "12형", 10)
        0.588  # 10/17 = 58.8%
    """
    max_capacity = get_vehicle_capacity_by_pallet_type(vehicle_length_m, pallet_type)
    
    if max_capacity == 0:
        return 0.0
    
    return min(1.0, current_load / max_capacity)


# ============================================
# 통합 검증 함수
# ============================================

def validate_dispatch_constraints(
    vehicle: dict,
    order: dict
) -> Tuple[bool, list]:
    """배차 제약조건 종합 검증
    
    Args:
        vehicle: 차량 정보 딕셔너리
        order: 주문 정보 딕셔너리
    
    Returns:
        tuple: (검증_성공, 오류_메시지_리스트)
    
    Example:
        >>> vehicle = {
        ...     "length_m": 9.5,
        ...     "supports_frozen": True,
        ...     "supports_chilled": False,
        ...     "supports_ambient": False,
        ...     "current_load_11": 10,
        ...     "current_load_12": 5
        ... }
        >>> order = {
        ...     "pallet_type": "12형",
        ...     "pallet_count": 8,
        ...     "temperature_zone": "냉동"
        ... }
        >>> validate_dispatch_constraints(vehicle, order)
        (True, [])
    """
    errors = []
    
    # 1. 온도대 호환성 체크
    vehicle_supports = {
        "supports_frozen": vehicle.get("supports_frozen", False),
        "supports_chilled": vehicle.get("supports_chilled", False),
        "supports_ambient": vehicle.get("supports_ambient", True)
    }
    
    if not is_temperature_compatible(vehicle_supports, order.get("temperature_zone")):
        errors.append(
            f"온도대 불일치: 차량은 {order.get('temperature_zone')} 화물을 운송할 수 없습니다."
        )
    
    # 2. 적재 용량 체크
    pallet_type = order.get("pallet_type", "11형")
    pallet_count = order.get("pallet_count", 0)
    
    current_load_key = f"current_load_{pallet_type.replace('형', '')}"
    current_load = vehicle.get(current_load_key, 0)
    
    max_capacity = get_vehicle_capacity_by_pallet_type(
        vehicle.get("length_m", 9.5),
        pallet_type
    )
    
    if current_load + pallet_count > max_capacity:
        errors.append(
            f"적재 용량 초과: {current_load + pallet_count}/{max_capacity} 팔레트 ({pallet_type})"
        )
    
    return len(errors) == 0, errors


# ============================================
# 디버그/테스트 함수
# ============================================

def print_capacity_rules():
    """차량 용량 규칙 출력 (디버그용)"""
    print("=" * 60)
    print("차량 길이별 팔레트 용량 규칙")
    print("=" * 60)
    for length, capacities in VEHICLE_CAPACITY_RULES.items():
        print(f"\n{length}m 차량:")
        for pallet_type, capacity in capacities.items():
            print(f"  - {pallet_type}: {capacity}개")
    print("=" * 60)


if __name__ == "__main__":
    # 테스트 코드
    print_capacity_rules()
    
    # 테스트 1: 파렛트 용량 계산
    print("\n[TEST 1] 파렛트 용량 계산")
    print(f"9.5m 차량 12형: {get_vehicle_capacity_by_pallet_type(9.5, '12형')}개")
    print(f"11m 차량 11형: {get_vehicle_capacity_by_pallet_type(11.0, '11형')}개")
    
    # 테스트 2: 24시간 하차시간 계산
    print("\n[TEST 2] 24시간 하차시간 계산")
    order_time = datetime(2026, 2, 2, 20, 0)
    delivery = calculate_delivery_datetime(order_time, "04:00")
    print(f"주문: 2026-02-02 20:00, 하차: 04:00 → {delivery}")
    
    # 테스트 3: 온도대 호환성
    print("\n[TEST 3] 온도대 호환성")
    vehicle_supports = {
        "supports_frozen": True,
        "supports_chilled": True,
        "supports_ambient": False
    }
    print(f"냉동 가능: {is_temperature_compatible(vehicle_supports, '냉동')}")
    print(f"상온 가능: {is_temperature_compatible(vehicle_supports, '상온')}")
