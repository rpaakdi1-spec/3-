-- 운전자 일별 주행거리 테이블 생성
CREATE TABLE IF NOT EXISTS driver_daily_mileage (
    id SERIAL PRIMARY KEY,
    driver_id INTEGER NOT NULL REFERENCES drivers(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    
    -- 주행 통계
    total_distance_km DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    total_driving_minutes INTEGER NOT NULL DEFAULT 0,
    engine_on_minutes INTEGER,
    idle_minutes INTEGER,
    
    -- 속도 통계
    max_speed_kmh DOUBLE PRECISION,
    avg_speed_kmh DOUBLE PRECISION,
    
    -- GPS 데이터 품질
    gps_point_count INTEGER,
    
    -- 운행 시간대
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    
    -- 운행한 차량들
    vehicle_ids VARCHAR(200),
    vehicle_count INTEGER DEFAULT 1,
    
    -- 계산 정보
    is_calculated BOOLEAN DEFAULT FALSE,
    calculation_method VARCHAR(50),
    
    -- 메모
    notes TEXT,
    
    -- 타임스탬프
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    
    -- 제약조건
    CONSTRAINT uq_driver_daily_mileage_driver_date UNIQUE (driver_id, date)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_driver_daily_mileage_driver_date ON driver_daily_mileage(driver_id, date);
CREATE INDEX IF NOT EXISTS idx_driver_daily_mileage_date ON driver_daily_mileage(date);
CREATE INDEX IF NOT EXISTS idx_driver_daily_mileage_calculated ON driver_daily_mileage(is_calculated);

-- 코멘트 추가
COMMENT ON TABLE driver_daily_mileage IS '운전자 일별 주행거리 통계';
COMMENT ON COLUMN driver_daily_mileage.driver_id IS '운전자 ID';
COMMENT ON COLUMN driver_daily_mileage.date IS '날짜';
COMMENT ON COLUMN driver_daily_mileage.total_distance_km IS '총 주행거리(km)';
COMMENT ON COLUMN driver_daily_mileage.total_driving_minutes IS '총 운행시간(분)';
COMMENT ON COLUMN driver_daily_mileage.vehicle_ids IS '운행 차량 ID 목록 (콤마 구분)';
COMMENT ON COLUMN driver_daily_mileage.vehicle_count IS '운행한 차량 수';
