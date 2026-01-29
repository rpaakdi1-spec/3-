"""Database optimization - indexes and performance improvements

Revision ID: db_optimization_001
Revises: performance_001
Create Date: 2026-01-28 18:22:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db_optimization_001'
down_revision = 'performance_001'
branch_labels = None
depends_on = None


def upgrade():
    """데이터베이스 최적화 적용"""
    
    # ====================
    # 1. Orders 테이블 인덱스
    # ====================
    
    # 주문 번호로 빠른 조회
    op.create_index('idx_orders_order_number', 'orders', ['order_number'], unique=True)
    
    # 주문 상태 필터링 (대시보드, 통계)
    op.create_index('idx_orders_status', 'orders', ['status'])
    
    # 배송 날짜 범위 조회
    op.create_index('idx_orders_order_date', 'orders', ['order_date'])
    op.create_index('idx_orders_requested_delivery_date', 'orders', ['requested_delivery_date'])
    
    # 거래처별 주문 조회
    op.create_index('idx_orders_pickup_client', 'orders', ['pickup_client_id'])
    op.create_index('idx_orders_delivery_client', 'orders', ['delivery_client_id'])
    
    # 복합 인덱스: 상태 + 날짜 (자주 사용되는 조회 패턴)
    op.create_index('idx_orders_status_date', 'orders', ['status', 'order_date'])
    
    # 온도대 필터링
    op.create_index('idx_orders_temperature_zone', 'orders', ['temperature_zone'])
    
    # ====================
    # 2. Dispatches 테이블 인덱스
    # ====================
    
    # 배차 번호로 빠른 조회
    op.create_index('idx_dispatches_dispatch_number', 'dispatches', ['dispatch_number'], unique=True)
    
    # 배차 상태 필터링
    op.create_index('idx_dispatches_status', 'dispatches', ['status'])
    
    # 배차 날짜 범위 조회
    op.create_index('idx_dispatches_dispatch_date', 'dispatches', ['dispatch_date'])
    
    # 차량 및 기사별 배차 조회
    op.create_index('idx_dispatches_vehicle', 'dispatches', ['vehicle_id'])
    op.create_index('idx_dispatches_driver', 'dispatches', ['driver_id'])
    
    # 복합 인덱스: 상태 + 날짜
    op.create_index('idx_dispatches_status_date', 'dispatches', ['status', 'dispatch_date'])
    
    # ====================
    # 3. Dispatch Routes 테이블 인덱스
    # ====================
    
    # 배차별 경로 조회 (가장 빈번한 조회)
    op.create_index('idx_dispatch_routes_dispatch', 'dispatch_routes', ['dispatch_id', 'sequence'])
    
    # 주문별 경로 조회
    op.create_index('idx_dispatch_routes_order', 'dispatch_routes', ['order_id'])
    
    # 경로 타입 필터링
    op.create_index('idx_dispatch_routes_type', 'dispatch_routes', ['route_type'])
    
    # ====================
    # 4. Vehicles 테이블 인덱스
    # ====================
    
    # 차량 번호로 빠른 조회
    op.create_index('idx_vehicles_vehicle_number', 'vehicles', ['vehicle_number'], unique=True)
    
    # 차량 상태 필터링 (가용 차량 조회)
    op.create_index('idx_vehicles_status', 'vehicles', ['status'])
    
    # 온도대별 차량 필터링
    op.create_index('idx_vehicles_temperature_zone', 'vehicles', ['temperature_zone'])
    
    # 복합 인덱스: 상태 + 온도대 (배차 시 가용 차량 조회)
    op.create_index('idx_vehicles_status_temp', 'vehicles', ['status', 'temperature_zone'])
    
    # ====================
    # 5. Drivers 테이블 인덱스
    # ====================
    
    # 면허 번호로 빠른 조회
    op.create_index('idx_drivers_license_number', 'drivers', ['license_number'], unique=True)
    
    # 기사 상태 필터링 (가용 기사 조회)
    op.create_index('idx_drivers_status', 'drivers', ['status'])
    
    # 전화번호로 조회
    op.create_index('idx_drivers_phone', 'drivers', ['phone'])
    
    # ====================
    # 6. Clients 테이블 인덱스
    # ====================
    
    # 사업자 번호로 빠른 조회
    op.create_index('idx_clients_business_number', 'clients', ['business_number'], unique=True)
    
    # 이름으로 검색
    op.create_index('idx_clients_name', 'clients', ['name'])
    
    # 위치 기반 검색 (공간 인덱스가 필요한 경우 GiST 사용)
    # PostgreSQL의 경우 GiST 인덱스 사용 권장
    try:
        op.execute('CREATE INDEX idx_clients_location ON clients USING GIST (ST_MakePoint(longitude, latitude)::geography)')
    except:
        # PostGIS가 없는 경우 개별 인덱스
        op.create_index('idx_clients_latitude', 'clients', ['latitude'])
        op.create_index('idx_clients_longitude', 'clients', ['longitude'])
    
    # ====================
    # 7. Vehicle Locations 테이블 인덱스
    # ====================
    
    # 차량별 위치 조회 (최신 위치 우선)
    op.create_index('idx_vehicle_locations_vehicle_time', 'vehicle_locations', 
                   ['vehicle_id', 'timestamp'], postgresql_using='btree')
    
    # 배차별 위치 조회
    op.create_index('idx_vehicle_locations_dispatch', 'vehicle_locations', ['dispatch_id'])
    
    # 시간 범위 조회
    op.create_index('idx_vehicle_locations_timestamp', 'vehicle_locations', ['timestamp'])
    
    # ====================
    # 8. Temperature Alerts 테이블 인덱스
    # ====================
    
    # 배차별 알림 조회
    op.create_index('idx_temp_alerts_dispatch', 'temperature_alerts', ['dispatch_id', 'alert_time'])
    
    # 해결 여부 필터링
    op.create_index('idx_temp_alerts_resolved', 'temperature_alerts', ['is_resolved'])
    
    # 복합 인덱스: 미해결 + 배차 (긴급 알림 조회)
    op.create_index('idx_temp_alerts_unresolved', 'temperature_alerts', 
                   ['is_resolved', 'dispatch_id'], 
                   postgresql_where='is_resolved = false')
    
    # ====================
    # 9. Users 테이블 인덱스
    # ====================
    
    # 사용자명으로 빠른 조회 (로그인)
    op.create_index('idx_users_username', 'users', ['username'], unique=True)
    
    # 이메일로 조회
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    
    # 활성 사용자 필터링
    op.create_index('idx_users_is_active', 'users', ['is_active'])


def downgrade():
    """인덱스 제거 (롤백)"""
    
    # Orders 인덱스 제거
    op.drop_index('idx_orders_temperature_zone', table_name='orders')
    op.drop_index('idx_orders_status_date', table_name='orders')
    op.drop_index('idx_orders_delivery_client', table_name='orders')
    op.drop_index('idx_orders_pickup_client', table_name='orders')
    op.drop_index('idx_orders_requested_delivery_date', table_name='orders')
    op.drop_index('idx_orders_order_date', table_name='orders')
    op.drop_index('idx_orders_status', table_name='orders')
    op.drop_index('idx_orders_order_number', table_name='orders')
    
    # Dispatches 인덱스 제거
    op.drop_index('idx_dispatches_status_date', table_name='dispatches')
    op.drop_index('idx_dispatches_driver', table_name='dispatches')
    op.drop_index('idx_dispatches_vehicle', table_name='dispatches')
    op.drop_index('idx_dispatches_dispatch_date', table_name='dispatches')
    op.drop_index('idx_dispatches_status', table_name='dispatches')
    op.drop_index('idx_dispatches_dispatch_number', table_name='dispatches')
    
    # Dispatch Routes 인덱스 제거
    op.drop_index('idx_dispatch_routes_type', table_name='dispatch_routes')
    op.drop_index('idx_dispatch_routes_order', table_name='dispatch_routes')
    op.drop_index('idx_dispatch_routes_dispatch', table_name='dispatch_routes')
    
    # Vehicles 인덱스 제거
    op.drop_index('idx_vehicles_status_temp', table_name='vehicles')
    op.drop_index('idx_vehicles_temperature_zone', table_name='vehicles')
    op.drop_index('idx_vehicles_status', table_name='vehicles')
    op.drop_index('idx_vehicles_vehicle_number', table_name='vehicles')
    
    # Drivers 인덱스 제거
    op.drop_index('idx_drivers_phone', table_name='drivers')
    op.drop_index('idx_drivers_status', table_name='drivers')
    op.drop_index('idx_drivers_license_number', table_name='drivers')
    
    # Clients 인덱스 제거
    try:
        op.drop_index('idx_clients_location', table_name='clients')
    except:
        op.drop_index('idx_clients_longitude', table_name='clients')
        op.drop_index('idx_clients_latitude', table_name='clients')
    op.drop_index('idx_clients_name', table_name='clients')
    op.drop_index('idx_clients_business_number', table_name='clients')
    
    # Vehicle Locations 인덱스 제거
    op.drop_index('idx_vehicle_locations_timestamp', table_name='vehicle_locations')
    op.drop_index('idx_vehicle_locations_dispatch', table_name='vehicle_locations')
    op.drop_index('idx_vehicle_locations_vehicle_time', table_name='vehicle_locations')
    
    # Temperature Alerts 인덱스 제거
    op.drop_index('idx_temp_alerts_unresolved', table_name='temperature_alerts')
    op.drop_index('idx_temp_alerts_resolved', table_name='temperature_alerts')
    op.drop_index('idx_temp_alerts_dispatch', table_name='temperature_alerts')
    
    # Users 인덱스 제거
    op.drop_index('idx_users_is_active', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_index('idx_users_username', table_name='users')
