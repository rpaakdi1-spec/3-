"""
Phase 2 실제 규모 테스트 데이터 생성 스크립트 (단순화 버전)
- 40대 차량
- 110건 주문
- 100개 거래처
"""

import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import random
from datetime import date, timedelta
import pandas as pd
from loguru import logger

# 데이터 생성 함수

def generate_clients_data(count=100):
    """거래처 데이터 생성"""
    logger.info(f"거래처 {count}개 데이터 생성...")
    
    # 서울/경기 지역
    regions = ["강남", "강서", "송파", "서초", "마포", "성동", "광진", "고양", "성남", "수원"]
    client_types = ["양쪽", "상차", "하차"]
    
    clients = []
    for i in range(count):
        region = random.choice(regions)
        clients.append({
            "거래처코드": f"C-{i+1:04d}",
            "거래처명": f"{region} 식자재마트-{i+1}",
            "구분": random.choice(client_types),
            "주소": f"서울시 {region}구 샘플동 {random.randint(1, 999)}",
            "상세주소": f"{random.randint(1, 20)}층",
            "상차가능시작": f"{random.randint(6, 9):02d}:00",
            "상차가능종료": "18:00",
            "하차가능시작": "08:00",
            "하차가능종료": f"{random.randint(18, 22):02d}:00",
            "지게차유무": random.choice(["Y", "N"])
        })
    
    return pd.DataFrame(clients)


def generate_vehicles_data(count=40):
    """차량 데이터 생성 (40대)"""
    logger.info(f"차량 {count}대 데이터 생성...")
    
    vehicles = []
    
    # 냉동 차량 18대
    for i in range(18):
        tonnage = 5.0 if i < 10 else 3.5
        vehicles.append({
            "차량코드": f"VH-FROZEN-{i+1:03d}",
            "차량번호": f"{random.randint(11, 99)}가{random.randint(1000, 9999)}",
            "온도대": "냉동",
            "UVIS단말기ID": f"UVIS-F-{i+1:03d}",
            "최대팔레트": random.randint(12, 14) if tonnage == 5.0 else random.randint(8, 10),
            "최대중량": tonnage * 1000,
            "톤수": tonnage,
            "최저온도": -25,
            "최고온도": -18,
            "상태": "운행가능"
        })
    
    # 냉장 차량 16대
    for i in range(16):
        tonnage = 5.0 if i < 9 else 3.5
        vehicles.append({
            "차량코드": f"VH-CHILLED-{i+1:03d}",
            "차량번호": f"{random.randint(11, 99)}나{random.randint(1000, 9999)}",
            "온도대": "냉장",
            "UVIS단말기ID": f"UVIS-C-{i+1:03d}",
            "최대팔레트": random.randint(12, 14) if tonnage == 5.0 else random.randint(8, 10),
            "최대중량": tonnage * 1000,
            "톤수": tonnage,
            "최저온도": 0,
            "최고온도": 6,
            "상태": "운행가능"
        })
    
    # 상온 차량 6대
    for i in range(6):
        tonnage = 5.0 if i < 4 else 3.5
        vehicles.append({
            "차량코드": f"VH-AMBIENT-{i+1:03d}",
            "차량번호": f"{random.randint(11, 99)}다{random.randint(1000, 9999)}",
            "온도대": "상온",
            "UVIS단말기ID": f"UVIS-A-{i+1:03d}",
            "최대팔레트": random.randint(12, 14) if tonnage == 5.0 else random.randint(8, 10),
            "최대중량": tonnage * 1000,
            "톤수": tonnage,
            "최저온도": None,
            "최고온도": None,
            "상태": "운행가능"
        })
    
    return pd.DataFrame(vehicles)


def generate_drivers_data(count=40):
    """운전자 데이터 생성"""
    logger.info(f"운전자 {count}명 데이터 생성...")
    
    drivers = []
    for i in range(count):
        drivers.append({
            "이름": f"운전자{i+1:02d}",
            "면허번호": f"{random.randint(11, 99)}-{random.randint(10, 99)}-{random.randint(100000, 999999)}",
            "전화번호": f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            "상태": "대기중"
        })
    
    return pd.DataFrame(drivers)


def generate_orders_data(client_count=100, order_count=110):
    """주문 데이터 생성 (110건)"""
    logger.info(f"주문 {order_count}건 데이터 생성...")
    
    delivery_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 온도대별 분포: 냉동 50, 냉장 44, 상온 16
    temp_zones = ["냉동"] * 50 + ["냉장"] * 44 + ["상온"] * 16
    random.shuffle(temp_zones)
    
    orders = []
    for i in range(order_count):
        temp_zone = temp_zones[i]
        
        # 팔레트 수 분포
        if i < 40:  # 소량 (1-3)
            pallet_count = random.randint(1, 3)
        elif i < 90:  # 중량 (4-7)
            pallet_count = random.randint(4, 7)
        else:  # 대량 (8-12)
            pallet_count = random.randint(8, 12)
        
        weight_kg = pallet_count * random.uniform(80, 120)
        
        # 배송 시간대
        if i < 40:  # 오전
            delivery_start = f"{random.randint(8, 11):02d}:00"
            delivery_end = f"{random.randint(10, 12):02d}:00"
        elif i < 90:  # 오후
            delivery_start = f"{random.randint(13, 16):02d}:00"
            delivery_end = f"{random.randint(15, 17):02d}:00"
        else:  # 야간
            delivery_start = f"{random.randint(18, 20):02d}:00"
            delivery_end = f"{random.randint(20, 22):02d}:00"
        
        orders.append({
            "주문번호": f"ORD-{delivery_date.replace('-', '')}-{i+1:04d}",
            "주문일자": delivery_date,
            "온도대": temp_zone,
            "상차거래처코드": f"C-{random.randint(1, client_count//2):04d}",
            "하차거래처코드": f"C-{random.randint(client_count//2 + 1, client_count):04d}",
            "팔레트수": pallet_count,
            "중량(kg)": round(weight_kg, 2),
            "상차시작": "08:00",
            "상차종료": "10:00",
            "하차시작": delivery_start,
            "하차종료": delivery_end,
            "희망배송일": delivery_date,
            "우선순위": random.randint(1, 10),
            "지게차필요": random.choice(["Y", "N"]),
            "상태": "배차대기"
        })
    
    return pd.DataFrame(orders)


def main():
    """메인 실행"""
    logger.info("=" * 60)
    logger.info("Phase 2 실제 규모 테스트 데이터 생성")
    logger.info("=" * 60)
    
    # 출력 디렉토리
    output_dir = Path(__file__).parent.parent / "data" / "test_data"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 거래처 데이터
    df_clients = generate_clients_data(count=100)
    df_clients.to_excel(output_dir / "clients_phase2.xlsx", index=False)
    logger.success(f"✓ 거래처 데이터: {len(df_clients)}개 → {output_dir}/clients_phase2.xlsx")
    
    # 2. 차량 데이터
    df_vehicles = generate_vehicles_data(count=40)
    df_vehicles.to_excel(output_dir / "vehicles_phase2.xlsx", index=False)
    logger.success(f"✓ 차량 데이터: {len(df_vehicles)}대 → {output_dir}/vehicles_phase2.xlsx")
    logger.info(f"  - 냉동: {len(df_vehicles[df_vehicles['온도대'] == '냉동'])}대")
    logger.info(f"  - 냉장: {len(df_vehicles[df_vehicles['온도대'] == '냉장'])}대")
    logger.info(f"  - 상온: {len(df_vehicles[df_vehicles['온도대'] == '상온'])}대")
    
    # 3. 운전자 데이터
    df_drivers = generate_drivers_data(count=40)
    df_drivers.to_excel(output_dir / "drivers_phase2.xlsx", index=False)
    logger.success(f"✓ 운전자 데이터: {len(df_drivers)}명 → {output_dir}/drivers_phase2.xlsx")
    
    # 4. 주문 데이터
    df_orders = generate_orders_data(client_count=100, order_count=110)
    df_orders.to_excel(output_dir / "orders_phase2.xlsx", index=False)
    logger.success(f"✓ 주문 데이터: {len(df_orders)}건 → {output_dir}/orders_phase2.xlsx")
    logger.info(f"  - 냉동: {len(df_orders[df_orders['온도대'] == '냉동'])}건")
    logger.info(f"  - 냉장: {len(df_orders[df_orders['온도대'] == '냉장'])}건")
    logger.info(f"  - 상온: {len(df_orders[df_orders['온도대'] == '상온'])}건")
    
    # 5. 통계 요약
    logger.info("=" * 60)
    logger.info("📊 생성된 데이터 통계")
    logger.info("=" * 60)
    logger.info(f"거래처: {len(df_clients)}개")
    logger.info(f"차량: {len(df_vehicles)}대 (냉동 18 + 냉장 16 + 상온 6)")
    logger.info(f"운전자: {len(df_drivers)}명")
    logger.info(f"주문: {len(df_orders)}건 (냉동 50 + 냉장 44 + 상온 16)")
    logger.info("=" * 60)
    logger.success("✅ Phase 2 테스트 데이터 생성 완료!")
    logger.info(f"📁 저장 위치: {output_dir}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
