"""
초기 데이터 생성 엔진 (Seed Data Generator)
현실적인 테스트/시연용 데이터를 자동으로 생성
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
import string
from sqlalchemy.orm import Session
import logging

from app.models.client import Client
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.order import Order
from app.models.dispatch import Dispatch
from app.database import get_db

logger = logging.getLogger(__name__)


class SeedDataGenerator:
    """초기 데이터 생성 엔진"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # 실제 서울/경기 지역 주소 샘플
        self.addresses = [
            "서울시 강남구 테헤란로 123",
            "서울시 송파구 올림픽로 456",
            "서울시 서초구 서초대로 789",
            "서울시 영등포구 여의대로 321",
            "서울시 마포구 상암로 654",
            "서울시 강서구 공항대로 987",
            "서울시 광진구 능동로 111",
            "서울시 성동구 왕십리로 222",
            "경기도 성남시 분당구 판교역로 333",
            "경기도 고양시 일산동구 중앙로 444",
            "경기도 수원시 영통구 광교로 555",
            "경기도 안양시 동안구 시민대로 666",
            "경기도 부천시 원미구 길주로 777",
            "경기도 평택시 소사벌대로 888",
            "인천시 남동구 논현로 999",
            "인천시 연수구 송도과학로 100",
            "경기도 용인시 수지구 포은대로 200",
            "경기도 화성시 동탄대로 300",
            "경기도 의정부시 의정부로 400",
            "경기도 광명시 광명로 500"
        ]
        
        # 고객사 이름 샘플
        self.company_names = [
            "한국식품", "서울물산", "대한유통", "경기냉동", "인천식자재",
            "수도권물류", "강남푸드", "송파식품", "서초마트", "영등포상사",
            "마포유통", "강서냉장", "광진물산", "성동식품", "분당푸드",
            "일산마트", "광교물류", "안양식자재", "부천냉동", "평택유통",
            "남동식품", "송도마트", "수지물산", "동탄식품", "의정부상사",
            "광명푸드", "강동유통", "관악물류", "동작식품", "구로마트",
            "금천냉동", "노원식자재", "도봉물산", "동대문푸드", "중랑식품",
            "성북마트", "강북유통", "은평물류", "서대문식품", "종로상사",
            "중구푸드", "용산마트", "양천냉동", "강남식자재", "서초물산",
            "송파푸드", "강동식품", "광진마트", "성동유통", "중랑물류"
        ]
        
        # 차량 번호판 샘플
        self.plate_regions = ["서울", "경기", "인천", "부산", "대구", "광주", "대전", "울산"]
        self.plate_chars = ["가", "나", "다", "라", "마", "바", "사", "아", "자", "차", "카", "타", "파", "하"]
        
        # 기사 이름 샘플
        self.driver_names = [
            "김철수", "이영희", "박민수", "정수진", "최동욱",
            "강미래", "윤서준", "임지우", "한예준", "오서연",
            "신우진", "장서윤", "권도현", "황지민", "송하은",
            "홍시우", "노예린", "배준서", "문지후", "양서아",
            "구민준", "천지안", "표하윤", "방서준", "석다인",
            "선예서", "설시윤", "류서현", "복하준", "옥유준",
            "빙서영", "하지호", "채은서", "현서준", "탁민서"
        ]
        
    # =====================================
    # 1. 전체 데이터 생성
    # =====================================
    
    def generate_all(
        self, 
        num_clients: int = 100,
        num_vehicles: int = 50,
        num_drivers: int = 60,
        num_orders: int = 1000,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        전체 데이터 생성
        
        Args:
            num_clients: 생성할 고객사 수
            num_vehicles: 생성할 차량 수
            num_drivers: 생성할 기사 수
            num_orders: 생성할 주문 수
            days: 주문 생성 기간 (일)
        """
        logger.info("Starting seed data generation...")
        
        result = {
            "clients": 0,
            "vehicles": 0,
            "drivers": 0,
            "orders": 0,
            "dispatches": 0
        }
        
        try:
            # 1. 고객사 생성
            clients = self.generate_clients(num_clients)
            result["clients"] = len(clients)
            logger.info(f"Generated {len(clients)} clients")
            
            # 2. 차량 생성
            vehicles = self.generate_vehicles(num_vehicles)
            result["vehicles"] = len(vehicles)
            logger.info(f"Generated {len(vehicles)} vehicles")
            
            # 3. 기사 생성 및 차량 할당
            drivers = self.generate_drivers(num_drivers, vehicles)
            result["drivers"] = len(drivers)
            logger.info(f"Generated {len(drivers)} drivers")
            
            # 4. 주문 생성 (계절/요일 패턴 반영)
            orders = self.generate_orders(num_orders, clients, days)
            result["orders"] = len(orders)
            logger.info(f"Generated {len(orders)} orders")
            
            # 5. 배차 생성 (주문의 80%)
            dispatches = self.generate_dispatches(orders, vehicles, drivers)
            result["dispatches"] = len(dispatches)
            logger.info(f"Generated {len(dispatches)} dispatches")
            
            # 6. 차량 위치 히스토리 생성 (배차에 대해)
            # locations = self.generate_vehicle_locations(dispatches)
            # result["locations"] = len(locations)
            
            self.db.commit()
            logger.info("Seed data generation completed successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Seed data generation failed: {str(e)}")
            self.db.rollback()
            raise
    
    # =====================================
    # 2. 고객사 생성
    # =====================================
    
    def generate_clients(self, num: int) -> List[Client]:
        """고객사 데이터 생성"""
        clients = []
        
        for i in range(num):
            # 고유한 이름 생성
            name = f"{random.choice(self.company_names)} ({i+1})"
            
            # 전화번호 생성
            phone = f"02-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            
            # 주소 선택
            address = random.choice(self.addresses)
            
            # 고객 타입 (80% REGULAR, 15% VIP, 5% NEW)
            client_type_rand = random.random()
            if client_type_rand < 0.80:
                client_type = "REGULAR"
            elif client_type_rand < 0.95:
                client_type = "VIP"
            else:
                client_type = "NEW"
            
            client = Client(
                name=name,
                phone=phone,
                address=address,
                address_detail=f"{random.randint(1, 20)}층 {random.randint(1, 10)}호",
                contact_person=random.choice(self.driver_names),
                email=f"contact{i+1}@{name.split()[0].lower()}.com",
                business_number=f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10000, 99999)}",
                client_type=client_type,
                notes=None if random.random() < 0.7 else f"특이사항 {i+1}"
            )
            
            self.db.add(client)
            clients.append(client)
            
            # 100개마다 flush (메모리 관리)
            if (i + 1) % 100 == 0:
                self.db.flush()
        
        self.db.flush()
        return clients
    
    # =====================================
    # 3. 차량 생성
    # =====================================
    
    def generate_vehicles(self, num: int) -> List[Vehicle]:
        """차량 데이터 생성"""
        vehicles = []
        
        vehicle_types = ["TRUCK", "VAN", "LORRY"]
        temp_types = ["FROZEN", "CHILLED", "AMBIENT"]
        
        for i in range(num):
            # 번호판 생성
            region = random.choice(self.plate_regions)
            char = random.choice(self.plate_chars)
            numbers = f"{random.randint(1000, 9999)}"
            license_plate = f"{region}{random.randint(10, 99)}{char}{numbers}"
            
            # 차량 타입
            vehicle_type = random.choice(vehicle_types)
            
            # 온도 타입 (70% FROZEN, 20% CHILLED, 10% AMBIENT)
            temp_rand = random.random()
            if temp_rand < 0.70:
                temperature_type = "FROZEN"
            elif temp_rand < 0.90:
                temperature_type = "CHILLED"
            else:
                temperature_type = "AMBIENT"
            
            # 용량 (차량 타입에 따라)
            if vehicle_type == "TRUCK":
                capacity_kg = random.randint(3000, 5000)
                capacity_cbm = random.randint(15, 25)
            elif vehicle_type == "VAN":
                capacity_kg = random.randint(1000, 2000)
                capacity_cbm = random.randint(8, 15)
            else:  # LORRY
                capacity_kg = random.randint(5000, 10000)
                capacity_cbm = random.randint(25, 40)
            
            # 상태 (90% available, 5% maintenance, 5% offline)
            status_rand = random.random()
            if status_rand < 0.90:
                status = "available"
            elif status_rand < 0.95:
                status = "maintenance"
            else:
                status = "offline"
            
            vehicle = Vehicle(
                license_plate=license_plate,
                vehicle_type=vehicle_type,
                model=f"현대 {vehicle_type.capitalize()} {random.randint(2018, 2024)}",
                year=random.randint(2018, 2024),
                capacity_kg=capacity_kg,
                capacity_cbm=capacity_cbm,
                temperature_type=temperature_type,
                status=status,
                notes=None if random.random() < 0.8 else f"정비 예정 {random.randint(1, 30)}일 후"
            )
            
            self.db.add(vehicle)
            vehicles.append(vehicle)
            
            if (i + 1) % 50 == 0:
                self.db.flush()
        
        self.db.flush()
        return vehicles
    
    # =====================================
    # 4. 기사 생성
    # =====================================
    
    def generate_drivers(self, num: int, vehicles: List[Vehicle]) -> List[Driver]:
        """기사 데이터 생성 및 차량 할당"""
        drivers = []
        
        # 사용 가능한 차량만 필터링
        available_vehicles = [v for v in vehicles if v.status == "available"]
        
        for i in range(num):
            # 이름
            name = f"{random.choice(self.driver_names)} ({i+1})"
            
            # 전화번호
            phone = f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            
            # 면허 번호
            license_number = f"{random.randint(10, 99)}-{random.randint(10, 99)}-{random.randint(100000, 999999)}-{random.randint(10, 99)}"
            
            # 면허 타입
            license_type = random.choice(["1종 보통", "1종 대형", "2종 보통"])
            
            # 상태 (85% available, 10% busy, 5% on_leave)
            status_rand = random.random()
            if status_rand < 0.85:
                status = "available"
            elif status_rand < 0.95:
                status = "busy"
            else:
                status = "on_leave"
            
            driver = Driver(
                name=name,
                phone=phone,
                license_number=license_number,
                license_type=license_type,
                status=status,
                notes=None if random.random() < 0.9 else "우수 기사"
            )
            
            # 차량 할당 (80% 확률)
            if i < len(available_vehicles) and random.random() < 0.80:
                driver.vehicle_id = available_vehicles[i].id
            
            self.db.add(driver)
            drivers.append(driver)
            
            if (i + 1) % 60 == 0:
                self.db.flush()
        
        self.db.flush()
        return drivers
    
    # =====================================
    # 5. 주문 생성 (계절/요일 패턴)
    # =====================================
    
    def generate_orders(self, num: int, clients: List[Client], days: int) -> List[Order]:
        """주문 데이터 생성 (계절/요일 패턴 반영)"""
        orders = []
        
        # 시작일 (과거 N일전부터)
        start_date = datetime.now() - timedelta(days=days)
        
        for i in range(num):
            # 랜덤 날짜 생성 (가중치 적용)
            # 최근일수록 더 많은 주문
            day_offset = int(random.triangular(0, days, days * 0.8))
            order_date = start_date + timedelta(days=day_offset)
            
            # 요일 (0=월요일, 6=일요일)
            weekday = order_date.weekday()
            
            # 요일별 주문량 조정
            # 월~금: 높음, 토: 중간, 일: 낮음
            if weekday >= 5:  # 주말
                if random.random() > 0.3:  # 70% 확률로 스킵
                    continue
            
            # 시간 생성 (업무 시간: 8~18시, 가중치 9~11시 피크)
            hour = int(random.triangular(8, 18, 10))
            minute = random.randint(0, 59)
            
            pickup_datetime = order_date.replace(hour=hour, minute=minute, second=0)
            
            # 배송 시간 (픽업 후 2~6시간)
            delivery_hours = random.randint(2, 6)
            delivery_datetime = pickup_datetime + timedelta(hours=delivery_hours)
            
            # 고객 선택 (VIP는 더 많은 주문)
            client = random.choice(clients)
            if client.client_type == "VIP" and random.random() < 0.3:
                # VIP는 30% 확률로 한 번 더 선택 기회
                client = random.choice([c for c in clients if c.client_type == "VIP"])
            
            # 주소
            pickup_address = random.choice(self.addresses)
            delivery_address = random.choice(self.addresses)
            
            # 같은 주소면 다시 선택
            while delivery_address == pickup_address:
                delivery_address = random.choice(self.addresses)
            
            # 무게/부피 (정규분포)
            weight_kg = abs(random.gauss(500, 200))
            volume_cbm = abs(random.gauss(5, 2))
            
            # 온도 타입 (70% FROZEN, 20% CHILLED, 10% AMBIENT)
            temp_rand = random.random()
            if temp_rand < 0.70:
                temperature_type = "FROZEN"
            elif temp_rand < 0.90:
                temperature_type = "CHILLED"
            else:
                temperature_type = "AMBIENT"
            
            # 상태 (과거: 완료, 최근: 대기/진행중)
            if (datetime.now() - order_date).days > 7:
                status = "완료"
            elif (datetime.now() - order_date).days > 3:
                status = random.choice(["완료", "배송중", "배차완료"])
            else:
                status = random.choice(["배차대기", "배차완료", "배송중"])
            
            order = Order(
                client_id=client.id,
                order_number=f"ORD-{order_date.strftime('%Y%m%d')}-{i+1:04d}",
                pickup_address=pickup_address,
                delivery_address=delivery_address,
                pickup_datetime=pickup_datetime,
                delivery_datetime=delivery_datetime,
                weight_kg=weight_kg,
                volume_cbm=volume_cbm,
                temperature_type=temperature_type,
                status=status,
                notes=None if random.random() < 0.85 else f"긴급 배송" if random.random() < 0.3 else "조심 취급"
            )
            
            self.db.add(order)
            orders.append(order)
            
            if (i + 1) % 100 == 0:
                self.db.flush()
        
        self.db.flush()
        return orders
    
    # =====================================
    # 6. 배차 생성
    # =====================================
    
    def generate_dispatches(
        self, 
        orders: List[Order], 
        vehicles: List[Vehicle],
        drivers: List[Driver]
    ) -> List[Dispatch]:
        """배차 데이터 생성 (주문의 80%)"""
        dispatches = []
        
        # 배차 가능한 차량/기사 필터링
        available_vehicles = [v for v in vehicles if v.status == "available"]
        available_drivers = [d for d in drivers if d.status in ["available", "busy"]]
        
        # 배차 대상 주문 (배차대기가 아닌 것들)
        dispatch_orders = [o for o in orders if o.status != "배차대기"]
        
        for order in dispatch_orders[:int(len(orders) * 0.80)]:  # 80%만 배차
            if not available_vehicles or not available_drivers:
                break
            
            # 온도 타입에 맞는 차량 선택
            suitable_vehicles = [v for v in available_vehicles 
                                if v.temperature_type == order.temperature_type]
            
            if not suitable_vehicles:
                suitable_vehicles = available_vehicles  # 없으면 아무 차량
            
            vehicle = random.choice(suitable_vehicles)
            driver = random.choice(available_drivers)
            
            # 배차 상태
            if order.status == "완료":
                dispatch_status = "완료"
            elif order.status == "배송중":
                dispatch_status = "배송중"
            else:
                dispatch_status = "배차완료"
            
            dispatch = Dispatch(
                order_id=order.id,
                vehicle_id=vehicle.id,
                driver_id=driver.id,
                status=dispatch_status,
                assigned_at=order.pickup_datetime - timedelta(hours=random.randint(1, 24)),
                notes=None if random.random() < 0.9 else "최적 경로 배정"
            )
            
            self.db.add(dispatch)
            dispatches.append(dispatch)
            
            if len(dispatches) % 100 == 0:
                self.db.flush()
        
        self.db.flush()
        return dispatches
    
    # =====================================
    # 7. 엣지 케이스 생성
    # =====================================
    
    def generate_edge_cases(self) -> Dict[str, int]:
        """엣지 케이스 데이터 생성"""
        result = {
            "urgent_orders": 0,
            "failed_dispatches": 0,
            "temperature_alerts": 0
        }
        
        # TODO: 구현
        # 1. 긴급 주문
        # 2. 배차 실패 케이스
        # 3. 온도 이탈 케이스
        
        return result
