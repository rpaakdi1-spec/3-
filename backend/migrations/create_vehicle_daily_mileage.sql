-- 차량 일별 주행거리 테이블 생성
CREATE TABLE IF NOT EXISTS vehicle_daily_mileage (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    
    -- 주행거리
    total_distance_km DOUBLE PRECISION DEFAULT 0.0,
    
    -- 운행 시간
    total_driving_minutes INTEGER DEFAULT 0,
    engine_on_minutes INTEGER DEFAULT 0,
    idle_minutes INTEGER DEFAULT 0,
    
    -- 운행 통계
    max_speed_kmh INTEGER DEFAULT 0,
    avg_speed_kmh DOUBLE PRECISION DEFAULT 0.0,
    
    -- GPS 포인트 수
    gps_point_count INTEGER DEFAULT 0,
    
    -- 운행 시작/종료 위치
    start_latitude DOUBLE PRECISION,
    start_longitude DOUBLE PRECISION,
    start_time TIMESTAMP WITH TIME ZONE,
    
    end_latitude DOUBLE PRECISION,
    end_longitude DOUBLE PRECISION,
    end_time TIMESTAMP WITH TIME ZONE,
    
    -- 집계 상태
    is_calculated BOOLEAN DEFAULT FALSE,
    calculation_method VARCHAR(50) DEFAULT 'gps_distance',
    
    -- 메타 정보
    notes VARCHAR(500),
    
    -- 타임스탬프
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 인덱스 생성
CREATE UNIQUE INDEX IF NOT EXISTS idx_vehicle_daily_mileage_vehicle_date 
    ON vehicle_daily_mileage(vehicle_id, date);

CREATE INDEX IF NOT EXISTS idx_vehicle_daily_mileage_date 
    ON vehicle_daily_mileage(date);

CREATE INDEX IF NOT EXISTS idx_vehicle_daily_mileage_calculated 
    ON vehicle_daily_mileage(is_calculated);

-- 업데이트 트리거 함수
CREATE OR REPLACE FUNCTION update_vehicle_daily_mileage_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 생성
DROP TRIGGER IF EXISTS trigger_update_vehicle_daily_mileage_updated_at ON vehicle_daily_mileage;
CREATE TRIGGER trigger_update_vehicle_daily_mileage_updated_at
    BEFORE UPDATE ON vehicle_daily_mileage
    FOR EACH ROW
    EXECUTE FUNCTION update_vehicle_daily_mileage_updated_at();

COMMENT ON TABLE vehicle_daily_mileage IS '차량 일별 주행거리 및 운행 통계';
COMMENT ON COLUMN vehicle_daily_mileage.total_distance_km IS '총 주행거리 (km)';
COMMENT ON COLUMN vehicle_daily_mileage.total_driving_minutes IS '총 운행 시간 (분)';
COMMENT ON COLUMN vehicle_daily_mileage.engine_on_minutes IS '시동 ON 시간 (분)';
COMMENT ON COLUMN vehicle_daily_mileage.idle_minutes IS '공회전 시간 (분, 시동은 켜져있지만 속도가 0인 시간)';
COMMENT ON COLUMN vehicle_daily_mileage.gps_point_count IS '수집된 GPS 포인트 수';
COMMENT ON COLUMN vehicle_daily_mileage.is_calculated IS '집계 완료 여부';
COMMENT ON COLUMN vehicle_daily_mileage.calculation_method IS '계산 방법 (gps_distance: GPS 좌표 기반, haversine: 하버사인 공식)';
