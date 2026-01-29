"""
테스트 설정 및 픽스처
"""
import os
import sys
from typing import Generator, AsyncGenerator
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import Base, get_db
from app.core.config import settings
from main import app


# 테스트용 인메모리 SQLite 데이터베이스
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """이벤트 루프 픽스처"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """데이터베이스 세션 픽스처"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """FastAPI 테스트 클라이언트 픽스처"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_client(db: Session) -> AsyncGenerator[AsyncClient, None]:
    """비동기 테스트 클라이언트 픽스처"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db: Session):
    """테스트 사용자 픽스처"""
    from app.models.user import User
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=pwd_context.hash("testpassword123"),
        is_active=True,
        is_admin=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_admin(db: Session):
    """테스트 관리자 픽스처"""
    from app.models.user import User
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=pwd_context.hash("adminpassword123"),
        is_active=True,
        is_admin=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def auth_headers(client: TestClient, test_user) -> dict:
    """인증 헤더 픽스처"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def admin_headers(client: TestClient, test_admin) -> dict:
    """관리자 인증 헤더 픽스처"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "admin",
            "password": "adminpassword123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def test_client_data(db: Session):
    """테스트 거래처 데이터 픽스처"""
    from app.models.client import Client
    
    client = Client(
        name="테스트 거래처",
        business_number="123-45-67890",
        representative="홍길동",
        phone="02-1234-5678",
        address="서울시 강남구 테스트로 123",
        latitude=37.5665,
        longitude=126.9780
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@pytest.fixture(scope="function")
def test_vehicle(db: Session):
    """테스트 차량 픽스처"""
    from app.models.vehicle import Vehicle, TemperatureZone
    
    vehicle = Vehicle(
        vehicle_number="12가3456",
        vehicle_type="냉동탑차",
        temperature_zone=TemperatureZone.FROZEN,
        max_capacity_pallets=30,
        max_weight_kg=5000,
        fuel_efficiency_kmpl=5.5,
        status="available"
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@pytest.fixture(scope="function")
def test_driver(db: Session):
    """테스트 기사 픽스처"""
    from app.models.driver import Driver
    
    driver = Driver(
        name="김기사",
        phone="010-1234-5678",
        license_number="12-34-567890-12",
        license_type="1종 대형",
        status="available"
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@pytest.fixture(scope="function")
def test_order(db: Session, test_client_data):
    """테스트 주문 픽스처"""
    from app.models.order import Order, OrderStatus, TemperatureZone
    from datetime import datetime, timedelta
    
    order = Order(
        order_number="ORD-20260127-001",
        order_date=datetime.now(),
        pickup_client_id=test_client_data.id,
        delivery_client_id=test_client_data.id,
        pickup_address="서울시 강남구 픽업로 123",
        delivery_address="서울시 서초구 배송로 456",
        pickup_latitude=37.5665,
        pickup_longitude=126.9780,
        delivery_latitude=37.4830,
        delivery_longitude=127.0322,
        pallet_count=10,
        weight_kg=500,
        volume_cbm=15.5,
        product_name="냉동식품",
        temperature_zone=TemperatureZone.FROZEN,
        requested_delivery_date=datetime.now() + timedelta(days=1),
        status=OrderStatus.PENDING
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@pytest.fixture(scope="function")
def test_dispatch(db: Session, test_vehicle, test_driver, test_order):
    """테스트 배차 픽스처"""
    from app.models.dispatch import Dispatch, DispatchStatus
    from datetime import datetime
    
    dispatch = Dispatch(
        dispatch_number="DISP-20260127-001",
        dispatch_date=datetime.now(),
        vehicle_id=test_vehicle.id,
        driver_id=test_driver.id,
        total_orders=1,
        total_pallets=10,
        total_weight_kg=500,
        total_distance_km=15.5,
        status=DispatchStatus.DRAFT
    )
    db.add(dispatch)
    db.commit()
    db.refresh(dispatch)
    return dispatch
