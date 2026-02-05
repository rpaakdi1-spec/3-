"""
데이터 로더 유틸리티
PostgreSQL에서 데이터를 가져와 ML 모델에 사용
"""
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

# Database configuration (읽어올 환경변수 또는 설정 파일)
DB_CONFIG = {
    'host': 'localhost',  # Docker 환경에서는 'postgres' 서비스명 사용
    'port': 5432,
    'database': 'uvis',
    'user': 'postgres',
    'password': 'HQINTE6OI9hgLlclwtSNaWvz0'  # 실제 환경에서는 환경변수로 관리
}


class DataLoader:
    """데이터 로더 클래스"""
    
    def __init__(self, db_config: Optional[Dict] = None):
        """
        초기화
        
        Args:
            db_config: 데이터베이스 연결 설정 (선택사항)
        """
        self.db_config = db_config or DB_CONFIG
        self.conn = None
    
    def connect(self):
        """데이터베이스 연결"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            logger.info("✅ 데이터베이스 연결 성공")
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {e}")
            raise
    
    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()
            logger.info("🔌 데이터베이스 연결 종료")
    
    def load_order_history(self, days: int = 90) -> pd.DataFrame:
        """
        주문 이력 데이터 로드
        
        Args:
            days: 조회할 일수 (기본값: 90일)
            
        Returns:
            pd.DataFrame: 주문 이력 데이터프레임
        """
        query = f"""
        SELECT 
            o.id,
            o.order_number,
            o.order_date,
            o.delivery_date,
            o.temperature_zone,
            o.status,
            o.priority,
            o.pallet_count,
            o.volume_cbm,
            o.pickup_client_id,
            o.delivery_client_id,
            o.created_at,
            pc.name as pickup_client_name,
            pc.address as pickup_address,
            pc.latitude as pickup_lat,
            pc.longitude as pickup_lng,
            dc.name as delivery_client_name,
            dc.address as delivery_address,
            dc.latitude as delivery_lat,
            dc.longitude as delivery_lng
        FROM orders o
        LEFT JOIN clients pc ON o.pickup_client_id = pc.id
        LEFT JOIN clients dc ON o.delivery_client_id = dc.id
        WHERE o.order_date >= CURRENT_DATE - INTERVAL '{days} days'
        ORDER BY o.order_date DESC
        """
        
        try:
            if not self.conn:
                self.connect()
            
            df = pd.read_sql_query(query, self.conn)
            logger.info(f"✅ 주문 이력 로드 완료: {len(df)} 건")
            return df
        except Exception as e:
            logger.error(f"❌ 주문 이력 로드 실패: {e}")
            raise
    
    def load_dispatch_history(self, days: int = 90) -> pd.DataFrame:
        """
        배차 이력 데이터 로드
        
        Args:
            days: 조회할 일수 (기본값: 90일)
            
        Returns:
            pd.DataFrame: 배차 이력 데이터프레임
        """
        query = f"""
        SELECT 
            d.id,
            d.dispatch_date,
            d.vehicle_id,
            d.driver_id,
            d.status,
            d.total_distance_km,
            d.total_duration_minutes,
            d.created_at,
            v.vehicle_number,
            v.vehicle_type,
            v.temperature_zone as vehicle_temp_zone,
            v.max_pallets,
            v.max_weight_kg,
            v.max_volume_cbm,
            dr.name as driver_name,
            dr.phone as driver_phone
        FROM dispatches d
        LEFT JOIN vehicles v ON d.vehicle_id = v.id
        LEFT JOIN drivers dr ON d.driver_id = dr.id
        WHERE d.dispatch_date >= CURRENT_DATE - INTERVAL '{days} days'
        ORDER BY d.dispatch_date DESC
        """
        
        try:
            if not self.conn:
                self.connect()
            
            df = pd.read_sql_query(query, self.conn)
            logger.info(f"✅ 배차 이력 로드 완료: {len(df)} 건")
            return df
        except Exception as e:
            logger.error(f"❌ 배차 이력 로드 실패: {e}")
            raise
    
    def load_vehicle_data(self) -> pd.DataFrame:
        """
        차량 데이터 로드
        
        Returns:
            pd.DataFrame: 차량 데이터프레임
        """
        query = """
        SELECT 
            id,
            vehicle_number,
            vehicle_type,
            temperature_zone,
            max_pallets,
            max_weight_kg,
            max_volume_cbm,
            length_m,
            width_m,
            height_m,
            min_temp_celsius,
            max_temp_celsius,
            forklift_operator_available,
            status,
            created_at
        FROM vehicles
        WHERE status = 'ACTIVE'
        ORDER BY vehicle_number
        """
        
        try:
            if not self.conn:
                self.connect()
            
            df = pd.read_sql_query(query, self.conn)
            logger.info(f"✅ 차량 데이터 로드 완료: {len(df)} 건")
            return df
        except Exception as e:
            logger.error(f"❌ 차량 데이터 로드 실패: {e}")
            raise
    
    def aggregate_daily_demand(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        일별 수요 집계
        
        Args:
            df: 주문 이력 데이터프레임
            
        Returns:
            pd.DataFrame: 일별 집계 데이터프레임
        """
        # order_date를 datetime으로 변환
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        # 일별 집계
        daily = df.groupby('order_date').agg({
            'id': 'count',  # 주문 건수
            'pallet_count': 'sum',  # 총 팔레트 수
            'volume_cbm': 'sum',  # 총 용적
        }).reset_index()
        
        # 컬럼명 변경
        daily.columns = ['date', 'order_count', 'total_pallets', 'total_volume']
        
        # 날짜 정렬
        daily = daily.sort_values('date')
        
        logger.info(f"✅ 일별 수요 집계 완료: {len(daily)} 일")
        return daily
    
    def load_gps_logs(self, vehicle_id: int, hours: int = 24) -> pd.DataFrame:
        """
        GPS 로그 데이터 로드
        
        Args:
            vehicle_id: 차량 ID
            hours: 조회할 시간 (기본값: 24시간)
            
        Returns:
            pd.DataFrame: GPS 로그 데이터프레임
        """
        query = f"""
        SELECT 
            id,
            vehicle_id,
            latitude,
            longitude,
            speed_kmh,
            ignition_on,
            temperature_celsius,
            battery_voltage,
            recorded_at,
            created_at
        FROM vehicle_gps_logs
        WHERE vehicle_id = {vehicle_id}
          AND recorded_at >= NOW() - INTERVAL '{hours} hours'
        ORDER BY recorded_at DESC
        """
        
        try:
            if not self.conn:
                self.connect()
            
            df = pd.read_sql_query(query, self.conn)
            logger.info(f"✅ GPS 로그 로드 완료: {len(df)} 건")
            return df
        except Exception as e:
            logger.error(f"❌ GPS 로그 로드 실패: {e}")
            raise


# 사용 예시
if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 데이터 로더 초기화
    loader = DataLoader()
    
    try:
        # 주문 이력 로드 (최근 90일)
        orders_df = loader.load_order_history(days=90)
        print(f"\n📦 주문 이력: {len(orders_df)} 건")
        print(orders_df.head())
        
        # 일별 수요 집계
        daily_df = loader.aggregate_daily_demand(orders_df)
        print(f"\n📊 일별 수요: {len(daily_df)} 일")
        print(daily_df.head())
        
        # 배차 이력 로드
        dispatch_df = loader.load_dispatch_history(days=90)
        print(f"\n🚚 배차 이력: {len(dispatch_df)} 건")
        print(dispatch_df.head())
        
        # 차량 데이터 로드
        vehicle_df = loader.load_vehicle_data()
        print(f"\n🚗 차량 데이터: {len(vehicle_df)} 건")
        print(vehicle_df.head())
        
    finally:
        # 연결 종료
        loader.close()
