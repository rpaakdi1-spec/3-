"""
데이터베이스 인덱스 최적화 스크립트
- 쿼리 성능 개선을 위한 인덱스 추가
"""

from sqlalchemy import text
from loguru import logger

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import engine


def create_indexes():
    """성능 최적화 인덱스 생성"""
    
    indexes = [
        # Orders 테이블
        ("idx_orders_status", "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)"),
        ("idx_orders_temperature_zone", "CREATE INDEX IF NOT EXISTS idx_orders_temperature_zone ON orders(temperature_zone)"),
        ("idx_orders_order_date", "CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date)"),
        ("idx_orders_pickup_client", "CREATE INDEX IF NOT EXISTS idx_orders_pickup_client ON orders(pickup_client_id)"),
        ("idx_orders_delivery_client", "CREATE INDEX IF NOT EXISTS idx_orders_delivery_client ON orders(delivery_client_id)"),
        ("idx_orders_status_zone", "CREATE INDEX IF NOT EXISTS idx_orders_status_zone ON orders(status, temperature_zone)"),
        
        # Clients 테이블
        ("idx_clients_code", "CREATE INDEX IF NOT EXISTS idx_clients_code ON clients(code)"),
        ("idx_clients_client_type", "CREATE INDEX IF NOT EXISTS idx_clients_client_type ON clients(client_type)"),
        ("idx_clients_geocoded", "CREATE INDEX IF NOT EXISTS idx_clients_geocoded ON clients(geocoded)"),
        ("idx_clients_is_active", "CREATE INDEX IF NOT EXISTS idx_clients_is_active ON clients(is_active)"),
        
        # Vehicles 테이블
        ("idx_vehicles_code", "CREATE INDEX IF NOT EXISTS idx_vehicles_code ON vehicles(code)"),
        ("idx_vehicles_plate_number", "CREATE INDEX IF NOT EXISTS idx_vehicles_plate_number ON vehicles(plate_number)"),
        ("idx_vehicles_type", "CREATE INDEX IF NOT EXISTS idx_vehicles_type ON vehicles(vehicle_type)"),
        ("idx_vehicles_status", "CREATE INDEX IF NOT EXISTS idx_vehicles_status ON vehicles(status)"),
        ("idx_vehicles_is_active", "CREATE INDEX IF NOT EXISTS idx_vehicles_is_active ON vehicles(is_active)"),
        ("idx_vehicles_uvis", "CREATE INDEX IF NOT EXISTS idx_vehicles_uvis ON vehicles(uvis_enabled, uvis_device_id)"),
        
        # Dispatches 테이블
        ("idx_dispatches_date", "CREATE INDEX IF NOT EXISTS idx_dispatches_date ON dispatches(dispatch_date)"),
        ("idx_dispatches_vehicle", "CREATE INDEX IF NOT EXISTS idx_dispatches_vehicle ON dispatches(vehicle_id)"),
        ("idx_dispatches_status", "CREATE INDEX IF NOT EXISTS idx_dispatches_status ON dispatches(status)"),
        ("idx_dispatches_date_status", "CREATE INDEX IF NOT EXISTS idx_dispatches_date_status ON dispatches(dispatch_date, status)"),
        
        # Dispatch Routes 테이블
        ("idx_dispatch_routes_dispatch", "CREATE INDEX IF NOT EXISTS idx_dispatch_routes_dispatch ON dispatch_routes(dispatch_id)"),
        ("idx_dispatch_routes_order", "CREATE INDEX IF NOT EXISTS idx_dispatch_routes_order ON dispatch_routes(order_id)"),
        ("idx_dispatch_routes_sequence", "CREATE INDEX IF NOT EXISTS idx_dispatch_routes_sequence ON dispatch_routes(dispatch_id, sequence_number)"),
    ]
    
    with engine.connect() as conn:
        created_count = 0
        for index_name, sql in indexes:
            try:
                conn.execute(text(sql))
                conn.commit()
                logger.info(f"✓ Created index: {index_name}")
                created_count += 1
            except Exception as e:
                logger.error(f"✗ Failed to create index {index_name}: {e}")
        
        logger.info(f"\nIndexes created: {created_count}/{len(indexes)}")


def analyze_indexes():
    """현재 인덱스 분석"""
    
    with engine.connect() as conn:
        # SQLite 인덱스 조회
        result = conn.execute(text("""
            SELECT name, tbl_name, sql 
            FROM sqlite_master 
            WHERE type='index' AND tbl_name IN ('orders', 'clients', 'vehicles', 'dispatches', 'dispatch_routes')
            ORDER BY tbl_name, name
        """))
        
        indexes = result.fetchall()
        
        logger.info("\n" + "="*80)
        logger.info("DATABASE INDEXES")
        logger.info("="*80)
        
        current_table = None
        for idx_name, tbl_name, sql in indexes:
            if tbl_name != current_table:
                logger.info(f"\nTable: {tbl_name}")
                current_table = tbl_name
            logger.info(f"  - {idx_name}")
        
        logger.info("\n" + "="*80)
        logger.info(f"Total indexes: {len(indexes)}")
        logger.info("="*80)


def optimize_database():
    """데이터베이스 최적화"""
    
    with engine.connect() as conn:
        logger.info("\nOptimizing database...")
        
        # ANALYZE: 통계 정보 업데이트
        conn.execute(text("ANALYZE"))
        conn.commit()
        logger.info("✓ ANALYZE completed")
        
        # VACUUM: 데이터베이스 압축 및 최적화
        conn.execute(text("VACUUM"))
        conn.commit()
        logger.info("✓ VACUUM completed")
        
        logger.info("Database optimization completed!")


def main():
    """메인 실행"""
    logger.info("Starting database optimization...")
    logger.info("="*80)
    
    # 1. 현재 인덱스 분석
    logger.info("\n[Step 1/3] Analyzing current indexes...")
    analyze_indexes()
    
    # 2. 인덱스 생성
    logger.info("\n[Step 2/3] Creating performance indexes...")
    create_indexes()
    
    # 3. 데이터베이스 최적화
    logger.info("\n[Step 3/3] Optimizing database...")
    optimize_database()
    
    # 4. 최종 인덱스 확인
    logger.info("\n[Final] Updated indexes:")
    analyze_indexes()
    
    logger.info("\n" + "="*80)
    logger.info("Database optimization completed successfully!")
    logger.info("="*80)


if __name__ == "__main__":
    main()
