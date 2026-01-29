"""
밴드 메시지 생성 서비스
화물 수배 메시지를 자동으로 생성하고 변형합니다.
"""

import random
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from ..models.dispatch import Dispatch
from ..models.vehicle import Vehicle
from ..models.driver import Driver


class BandMessageGenerator:
    """밴드 메시지 생성기"""
    
    # 메시지 변형 요소
    ICONS = ["🚛", "🚚", "📦", "📢", "✅", "⚡", "🔥", "💼", "🎯", "📍"]
    PREFIXES = [
        "[긴급수배]",
        "[화물정보]",
        "【배차완료】",
        "◈긴급◈",
        "★화물★",
        "▶수배",
        "◆긴급배차◆",
        "●화물수배●",
    ]
    URGENCY_MARKERS = [
        "⚠️ 긴급",
        "🔴 급함",
        "🆘 시급",
        "⏰ 당일",
        "💨 급송",
    ]
    
    @staticmethod
    def generate_message(
        db: Session,
        dispatch_id: int,
        variation_seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        배차 정보를 기반으로 메시지 생성
        
        Args:
            db: 데이터베이스 세션
            dispatch_id: 배차 ID
            variation_seed: 변형 시드 (랜덤 재현용)
            
        Returns:
            생성된 메시지와 메타데이터
        """
        # 배차 정보 조회
        dispatch = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
        if not dispatch:
            raise ValueError(f"배차 ID {dispatch_id}를 찾을 수 없습니다")
        
        # 차량 및 기사 정보 조회
        vehicle = db.query(Vehicle).filter(Vehicle.id == dispatch.vehicle_id).first()
        driver = None
        if dispatch.driver_id:
            driver = db.query(Driver).filter(Driver.id == dispatch.driver_id).first()
        
        # 변형 시드 설정
        if variation_seed is None:
            variation_seed = random.randint(1000, 9999)
        
        random.seed(variation_seed)
        
        # 메시지 구성 요소 선택
        icon = random.choice(BandMessageGenerator.ICONS)
        prefix = random.choice(BandMessageGenerator.PREFIXES)
        urgency = random.choice(BandMessageGenerator.URGENCY_MARKERS) if random.random() > 0.5 else ""
        
        # 시간 정보
        now = datetime.now()
        timestamp = now.strftime("%H:%M")
        date_str = now.strftime("%m/%d")
        
        # 차량 정보
        vehicle_info = f"{vehicle.vehicle_type} {vehicle.license_plate}" if vehicle else "차량 미배정"
        temp_range = ""
        if vehicle and vehicle.temperature_type:
            if vehicle.temperature_type == "냉동":
                temp_range = " (-18℃ ~ -25℃)"
            elif vehicle.temperature_type == "냉장":
                temp_range = " (0℃ ~ 6℃)"
        
        # 기사 정보
        driver_info = f"기사: {driver.name} ({driver.phone})" if driver else "기사 미배정"
        
        # 배차 상세 정보
        routes_info = []
        if dispatch.routes:
            for i, route in enumerate(dispatch.routes, 1):
                if route.route_type.value in ["상차", "하차"]:
                    routes_info.append(f"{i}. {route.route_type.value}: {route.location_name}")
        
        # 메시지 포맷 랜덤 선택
        message_format = random.randint(1, 4)
        
        if message_format == 1:
            # 포맷 1: 심플
            message = f"""{icon} {prefix} {urgency}

🚚 차량: {vehicle_info}{temp_range}
📦 팔레트: {dispatch.total_pallets}개 / 중량: {dispatch.total_weight_kg:.1f}kg
📍 경로: {len(dispatch.routes)}개 지점
{chr(10).join(routes_info[:3])}

👤 {driver_info}
📅 {date_str} {timestamp} 기준"""
        
        elif message_format == 2:
            # 포맷 2: 상세
            distance_info = f"📏 거리: {dispatch.total_distance_km:.1f}km" if dispatch.total_distance_km else ""
            time_info = f"⏱️ 예상시간: {dispatch.estimated_duration_minutes}분" if dispatch.estimated_duration_minutes else ""
            
            message = f"""{icon} {prefix}

【차량정보】
{vehicle_info}{temp_range}

【화물정보】
팔레트: {dispatch.total_pallets}개
중량: {dispatch.total_weight_kg:.1f}kg
{distance_info}
{time_info}

【경로】
{chr(10).join(routes_info[:3])}

【담당】
{driver_info}

※ {timestamp} 업데이트"""
        
        elif message_format == 3:
            # 포맷 3: 간결
            first_pickup = None
            last_delivery = None
            for route in dispatch.routes:
                if route.route_type.value == "상차" and not first_pickup:
                    first_pickup = route.location_name
                if route.route_type.value == "하차":
                    last_delivery = route.location_name
            
            message = f"""{icon} {prefix} {urgency}

▶ {vehicle_info}{temp_range}
▶ {dispatch.total_pallets}PLT / {dispatch.total_weight_kg:.1f}kg
▶ {first_pickup or '상차지'} → {last_delivery or '하차지'}
▶ {driver_info}

[{timestamp}]"""
        
        else:
            # 포맷 4: 이모지 강조
            message = f"""{icon * 2} {prefix} {icon * 2}

🚛 차량정보
   └ {vehicle_info}{temp_range}

📦 화물정보
   └ {dispatch.total_pallets}개 팔레트
   └ {dispatch.total_weight_kg:.1f}kg

📍 배송경로
{chr(10).join(['   └ ' + r for r in routes_info[:3]])}

👤 담당기사
   └ {driver_info}

⏰ {date_str} {timestamp} 현재"""
        
        # 랜덤 시드 초기화
        random.seed()
        
        return {
            "message": message,
            "variation_seed": variation_seed,
            "format_type": message_format,
            "generated_at": now.isoformat()
        }
    
    @staticmethod
    def generate_next_interval(
        min_seconds: int = 180,
        max_seconds: int = 300
    ) -> int:
        """
        다음 메시지 생성 간격 계산 (랜덤)
        
        Args:
            min_seconds: 최소 간격 (초)
            max_seconds: 최대 간격 (초)
            
        Returns:
            간격 (초)
        """
        return random.randint(min_seconds, max_seconds)
