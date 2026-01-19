"""
실제 규모 테스트 데이터 생성 스크립트
- 40대 차량
- 110건 주문
- 100개 거래처 (서울/경기)
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import random
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
from app.core.database import SessionLocal, init_db
from app.models.client import Client, ClientType
from app.models.vehicle import Vehicle, VehicleType, TemperatureZone, VehicleStatus
from app.models.driver import Driver, DriverStatus
from app.models.order import Order, OrderStatus
from loguru import logger

# 서울/경기 주요 지역 좌표
SEOUL_AREAS = {
    "강남/서초/송파": [(37.4979, 127.0276), (37.4839, 127.0324), (37.5145, 127.1059)],
    "강서/양천/구로": [(37.5509, 126.8495), (37.5172, 126.8664), (37.5029, 126.8873)],
    "성동/광진/동대문": [(37.5633, 127.0365), (37.5385, 127.0823), (37.5744, 127.0399)],
    "종로/중구/용산": [(37.5735, 126.9788), (37.5641, 126.9971), (37.5326, 126.9908)],
    "은평/서대문/마포": [(37.6176, 126.9227), (37.5791, 126.9368), (37.5663, 126.9019)],
}

GYEONGGI_AREAS = {
    "고양/파주": [(37.6584, 126.8320), (37.7601, 126.7800)],
    "성남/광주/하남": [(37.4449, 127.1388), (37.4291, 127.2550), (37.5394, 127.2065)],
    "안양/군포/의왕": [(37.3943, 126.9568), (37.3616, 126.9352), (37.3449, 127.0350)],
    "부천/김포": [(37.5034, 126.7660), (37.6152, 126.7156)],
    "수원/화성": [(37.2636, 127.0286), (37.1995, 126.8312)],
    "용인/평택": [(37.2411, 127.1776), (36.9920, 127.1129)],
}

# 거래처명 템플릿
CLIENT_NAME_TEMPLATES = [
    "{area} 식자재마트", "{area} 대형마트", "{area} 물류센터", 
    "{area} 냉동창고", "{area} 식품도매", "{area} 수산시장",
    "{area} 농수산물센터", "{area} 프레시마트", "{area} 할인마트",
    "{area} 냉장유통센터"
]


def generate_clients(session, count: int = 100) -> List[Client]:
    """거래처 데이터 생성"""
    logger.info(f"거래처 {count}개 생성 시작...")
    
    clients = []
    client_code_counter = 1
    
    # 서울 거래처 (50개)
    for area_name, coords_list in SEOUL_AREAS.items():
        for i in range(10):  # 지역당 10개
            coord = random.choice(coords_list)
            lat = coord[0] + random.uniform(-0.01, 0.01)
            lon = coord[1] + random.uniform(-0.01, 0.01)
            
            area_short = area_name.split('/')[0]
            template = random.choice(CLIENT_NAME_TEMPLATES)
            name = template.format(area=area_short)
            
            client = Client(
                code=f"C-{client_code_counter:04d}",
                name=f"{name}-{i+1}",
                type=random.choice([ClientType.RETAIL, ClientType.WHOLESALE, ClientType.WAREHOUSE]),
                address=f"서울시 {area_short} 샘플동 {random.randint(1, 999)}",
                latitude=lat,
                longitude=lon,
                loading_start_time=f"{random.randint(6, 9):02d}:00",
                has_forklift=random.choice([True, False])
            )
            clients.append(client)
            client_code_counter += 1
    
    # 경기 거래처 (50개)
    for area_name, coords_list in GYEONGGI_AREAS.items():
        for i in range(8):  # 지역당 8개 (약 50개)
            coord = random.choice(coords_list)
            lat = coord[0] + random.uniform(-0.01, 0.01)
            lon = coord[1] + random.uniform(-0.01, 0.01)
            
            area_short = area_name.split('/')[0]
            template = random.choice(CLIENT_NAME_TEMPLATES)
            name = template.format(area=area_short)
            
            client = Client(
                code=f"C-{client_code_counter:04d}",
                name=f"{name}-{i+1}",
                type=random.choice([ClientType.RETAIL, ClientType.WHOLESALE, ClientType.WAREHOUSE]),
                address=f"경기도 {area_short} 샘플동 {random.randint(1, 999)}",
                latitude=lat,
                longitude=lon,
                loading_start_time=f"{random.randint(6, 9):02d}:00",
                has_forklift=random.choice([True, False])
            )
            clients.append(client)
            client_code_counter += 1
    
    # 데이터베이스에 저장
    session.add_all(clients[:count])
    session.commit()
    
    logger.success(f"거래처 {len(clients[:count])}개 생성 완료")
    return clients[:count]


def generate_vehicles(session, count: int = 40) -> List[Vehicle]:
    """차량 데이터 생성 (40대)"""
    logger.info(f"차량 {count}개 생성 시작...")
    
    vehicles = []
    
    # 냉동 차량 18대 (45%)
    for i in range(18):
        is_5ton = i < 10  # 5톤 10대, 3.5톤 8대
        vehicles.append(Vehicle(
            code=f"VH-FROZEN-{i+1:03d}",
            uvis_terminal_id=f"UVIS-F-{i+1:03d}",
            vehicle_type=VehicleType.TRUCK_5TON if is_5ton else VehicleType.TRUCK_3_5TON,
            temperature_zone=TemperatureZone.FROZEN,
            max_pallet_count=random.randint(12, 14) if is_5ton else random.randint(8, 10),
            status=VehicleStatus.AVAILABLE
        ))
    
    # 냉장 차량 16대 (40%)
    for i in range(16):
        is_5ton = i < 9  # 5톤 9대, 3.5톤 7대
        vehicles.append(Vehicle(
            code=f"VH-CHILLED-{i+1:03d}",
            uvis_terminal_id=f"UVIS-C-{i+1:03d}",
            vehicle_type=VehicleType.TRUCK_5TON if is_5ton else VehicleType.TRUCK_3_5TON,
            temperature_zone=TemperatureZone.CHILLED,
            max_pallet_count=random.randint(12, 14) if is_5ton else random.randint(8, 10),
            status=VehicleStatus.AVAILABLE
        ))
    
    # 상온 차량 6대 (15%)
    for i in range(6):
        is_5ton = i < 4  # 5톤 4대, 3.5톤 2대
        vehicles.append(Vehicle(
            code=f"VH-AMBIENT-{i+1:03d}",
            uvis_terminal_id=f"UVIS-A-{i+1:03d}",
            vehicle_type=VehicleType.TRUCK_5TON if is_5ton else VehicleType.TRUCK_3_5TON,
            temperature_zone=TemperatureZone.AMBIENT,
            max_pallet_count=random.randint(12, 14) if is_5ton else random.randint(8, 10),
            status=VehicleStatus.AVAILABLE
        ))
    
    session.add_all(vehicles)
    session.commit()
    
    logger.success(f"차량 {len(vehicles)}개 생성 완료")
    logger.info(f"- 냉동: 18대, 냉장: 16대, 상온: 6대")
    return vehicles


def generate_drivers(session, count: int = 40) -> List[Driver]:
    """운전자 데이터 생성"""
    logger.info(f"운전자 {count}개 생성 시작...")
    
    drivers = []
    for i in range(count):
        drivers.append(Driver(
            name=f"운전자{i+1:02d}",
            license_number=f"{random.randint(11, 99)}-{random.randint(10, 99)}-{random.randint(100000, 999999)}",
            phone_number=f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            status=DriverStatus.AVAILABLE
        ))
    
    session.add_all(drivers)
    session.commit()
    
    logger.success(f"운전자 {len(drivers)}개 생성 완료")
    return drivers


def generate_orders(session, clients: List[Client], count: int = 110) -> List[Order]:
    """주문 데이터 생성 (110건)"""
    logger.info(f"주문 {count}개 생성 시작...")
    
    orders = []
    delivery_date = datetime.now().date() + timedelta(days=1)
    
    # 온도대별 분포
    # 냉동: 50건, 냉장: 44건, 상온: 16건
    temp_zones = (
        [TemperatureZone.FROZEN] * 50 + 
        [TemperatureZone.CHILLED] * 44 + 
        [TemperatureZone.AMBIENT] * 16
    )
    random.shuffle(temp_zones)
    
    for i in range(count):
        client = random.choice(clients)
        temp_zone = temp_zones[i]
        
        # 팔레트 수 분포
        if i < 40:  # 소량 (1-3)
            pallet_count = random.randint(1, 3)
        elif i < 90:  # 중량 (4-7)
            pallet_count = random.randint(4, 7)
        else:  # 대량 (8-12)
            pallet_count = random.randint(8, 12)
        
        # 중량 계산 (팔레트당 평균 80-120kg)
        weight_kg = pallet_count * random.uniform(80, 120)
        
        # 배송 시간대
        if i < 40:  # 오전
            delivery_window_start = f"{random.randint(8, 11):02d}:00"
            delivery_window_end = f"{random.randint(10, 12):02d}:00"
        elif i < 90:  # 오후
            delivery_window_start = f"{random.randint(13, 16):02d}:00"
            delivery_window_end = f"{random.randint(15, 17):02d}:00"
        else:  # 야간
            delivery_window_start = f"{random.randint(18, 20):02d}:00"
            delivery_window_end = f"{random.randint(20, 22):02d}:00"
        
        order = Order(
            order_number=f"ORD-{delivery_date.strftime('%Y%m%d')}-{i+1:04d}",
            client_id=client.id,
            temperature_zone=temp_zone,
            pallet_count=pallet_count,
            weight_kg=round(weight_kg, 2),
            delivery_date=delivery_date,
            delivery_window_start=delivery_window_start,
            delivery_window_end=delivery_window_end,
            status=OrderStatus.PENDING,
            special_instructions=None
        )
        orders.append(order)
    
    session.add_all(orders)
    session.commit()
    
    logger.success(f"주문 {len(orders)}개 생성 완료")
    logger.info(f"- 냉동: 50건, 냉장: 44건, 상온: 16건")
    logger.info(f"- 소량(1-3팔레트): 40건, 중량(4-7): 50건, 대량(8-12): 20건")
    return orders


def export_to_excel(clients: List[Client], vehicles: List[Vehicle], 
                    drivers: List[Driver], orders: List[Order]):
    """생성된 데이터를 Excel로 내보내기"""
    logger.info("Excel 파일 생성 중...")
    
    output_dir = Path(__file__).parent.parent / "data" / "test_data"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 거래처 데이터
    clients_data = [{
        "거래처코드": c.code,
        "거래처명": c.name,
        "구분": c.type.value,
        "주소": c.address,
        "위도": c.latitude,
        "경도": c.longitude,
        "상차가능시작": c.loading_start_time,
        "지게차유무": "Y" if c.has_forklift else "N"
    } for c in clients]
    
    df_clients = pd.DataFrame(clients_data)
    df_clients.to_excel(output_dir / "clients_test_data.xlsx", index=False)
    
    # 차량 데이터
    vehicles_data = [{
        "차량코드": v.code,
        "UVIS단말기ID": v.uvis_terminal_id,
        "차량타입": v.vehicle_type.value,
        "온도대": v.temperature_zone.value,
        "최대팔레트": v.max_pallet_count,
        "상태": v.status.value
    } for v in vehicles]
    
    df_vehicles = pd.DataFrame(vehicles_data)
    df_vehicles.to_excel(output_dir / "vehicles_test_data.xlsx", index=False)
    
    # 운전자 데이터
    drivers_data = [{
        "이름": d.name,
        "면허번호": d.license_number,
        "전화번호": d.phone_number,
        "상태": d.status.value
    } for d in drivers]
    
    df_drivers = pd.DataFrame(drivers_data)
    df_drivers.to_excel(output_dir / "drivers_test_data.xlsx", index=False)
    
    # 주문 데이터
    orders_data = [{
        "주문번호": o.order_number,
        "거래처코드": next((c.code for c in clients if c.id == o.client_id), None),
        "온도대": o.temperature_zone.value,
        "팔레트수": o.pallet_count,
        "중량(kg)": o.weight_kg,
        "배송일자": o.delivery_date.strftime("%Y-%m-%d"),
        "배송시작시간": o.delivery_window_start,
        "배송종료시간": o.delivery_window_end
    } for o in orders]
    
    df_orders = pd.DataFrame(orders_data)
    df_orders.to_excel(output_dir / "orders_test_data.xlsx", index=False)
    
    logger.success(f"Excel 파일 저장 완료: {output_dir}")


def main():
    """메인 실행 함수"""
    logger.info("=" * 60)
    logger.info("실제 규모 테스트 데이터 생성 시작")
    logger.info("=" * 60)
    
    # 데이터베이스 초기화
    init_db()
    session = SessionLocal()
    
    try:
        # 1. 거래처 생성 (100개)
        clients = generate_clients(session, count=100)
        
        # 2. 차량 생성 (40대)
        vehicles = generate_vehicles(session, count=40)
        
        # 3. 운전자 생성 (40명)
        drivers = generate_drivers(session, count=40)
        
        # 4. 주문 생성 (110건)
        orders = generate_orders(session, clients, count=110)
        
        # 5. Excel 내보내기
        export_to_excel(clients, vehicles, drivers, orders)
        
        logger.info("=" * 60)
        logger.success("테스트 데이터 생성 완료!")
        logger.info(f"- 거래처: {len(clients)}개")
        logger.info(f"- 차량: {len(vehicles)}대")
        logger.info(f"- 운전자: {len(drivers)}명")
        logger.info(f"- 주문: {len(orders)}건")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"데이터 생성 중 오류 발생: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
