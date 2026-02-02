-- ============================================
-- Phase 1: Basic Constraints Implementation
-- Date: 2026-02-02
-- ============================================

-- ============================================
-- 1. Clients 테이블 확장
-- ============================================
ALTER TABLE clients 
ADD COLUMN IF NOT EXISTS pallet_type VARCHAR(10) DEFAULT '11형',
ADD COLUMN IF NOT EXISTS unload_start_time TIME,
ADD COLUMN IF NOT EXISTS unload_end_time TIME;

-- Check constraint
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'clients_pallet_type_check'
    ) THEN
        ALTER TABLE clients 
        ADD CONSTRAINT clients_pallet_type_check 
        CHECK (pallet_type IN ('11형', '12형'));
    END IF;
END $$;

COMMENT ON COLUMN clients.pallet_type IS '파렛트 타입 (11형/12형)';
COMMENT ON COLUMN clients.unload_start_time IS '하차 가능 시작시간';
COMMENT ON COLUMN clients.unload_end_time IS '하차 가능 종료시간';

-- ============================================
-- 2. Vehicles 테이블 확장
-- ============================================
ALTER TABLE vehicles
ADD COLUMN IF NOT EXISTS max_pallets_11type INTEGER,
ADD COLUMN IF NOT EXISTS max_pallets_12type INTEGER,
ADD COLUMN IF NOT EXISTS supports_frozen BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS supports_chilled BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS supports_ambient BOOLEAN DEFAULT true;

COMMENT ON COLUMN vehicles.max_pallets_11type IS '11형 팔레트 최대 적재량';
COMMENT ON COLUMN vehicles.max_pallets_12type IS '12형 팔레트 최대 적재량';
COMMENT ON COLUMN vehicles.supports_frozen IS '냉동 화물 가능 여부';
COMMENT ON COLUMN vehicles.supports_chilled IS '냉장 화물 가능 여부';
COMMENT ON COLUMN vehicles.supports_ambient IS '상온 화물 가능 여부';

-- ============================================
-- 3. Orders 테이블 확장
-- ============================================
ALTER TABLE orders
ADD COLUMN IF NOT EXISTS calculated_delivery_datetime TIMESTAMP,
ADD COLUMN IF NOT EXISTS pallet_type VARCHAR(10) DEFAULT '11형';

COMMENT ON COLUMN orders.calculated_delivery_datetime IS '자동 계산된 하차 일시 (24시간 기준)';
COMMENT ON COLUMN orders.pallet_type IS '파렛트 타입 (거래처 기본값 사용)';

-- ============================================
-- 4. 차량 용량 규칙 테이블 생성
-- ============================================
CREATE TABLE IF NOT EXISTS vehicle_capacity_rules (
    id SERIAL PRIMARY KEY,
    vehicle_length_m FLOAT NOT NULL,
    pallet_type VARCHAR(10) NOT NULL,
    max_capacity INTEGER NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_capacity_rule UNIQUE(vehicle_length_m, pallet_type),
    CONSTRAINT chk_pallet_type CHECK (pallet_type IN ('11형', '12형'))
);

COMMENT ON TABLE vehicle_capacity_rules IS '차량 길이별 팔레트 용량 규칙';

-- ============================================
-- 5. 기본 용량 규칙 데이터 삽입
-- ============================================
INSERT INTO vehicle_capacity_rules (vehicle_length_m, pallet_type, max_capacity, notes) VALUES
(9.5, '11형', 20, '9.5m 차량 11형 팔레트'),
(9.5, '12형', 17, '9.5m 차량 12형 팔레트'),
(11.0, '11형', 24, '11m 차량 11형 팔레트'),
(11.0, '12형', 20, '11m 차량 12형 팔레트'),
(12.0, '11형', 26, '12m 차량 11형 팔레트'),
(12.0, '12형', 22, '12m 차량 12형 팔레트'),
(14.0, '11형', 30, '14m 차량 11형 팔레트'),
(14.0, '12형', 26, '14m 차량 12형 팔레트')
ON CONFLICT (vehicle_length_m, pallet_type) DO NOTHING;

-- ============================================
-- 6. 기존 데이터 업데이트
-- ============================================
UPDATE vehicles
SET 
    supports_frozen = CASE 
        WHEN vehicle_type IN ('냉동', '겸용') THEN true 
        ELSE false 
    END,
    supports_chilled = CASE 
        WHEN vehicle_type IN ('냉장', '겸용') THEN true 
        ELSE false 
    END,
    supports_ambient = CASE 
        WHEN vehicle_type IN ('상온', '겸용') THEN true
        ELSE false
    END
WHERE supports_frozen IS NULL;

-- 차량 길이 기반 용량 설정
WITH capacity_data AS (
    SELECT DISTINCT ON (vehicle_length_m, pallet_type)
        vehicle_length_m, pallet_type, max_capacity
    FROM vehicle_capacity_rules
)
UPDATE vehicles v
SET 
    max_pallets_11type = (SELECT max_capacity FROM capacity_data WHERE vehicle_length_m = v.length_m AND pallet_type = '11형'),
    max_pallets_12type = (SELECT max_capacity FROM capacity_data WHERE vehicle_length_m = v.length_m AND pallet_type = '12형')
WHERE v.length_m IS NOT NULL AND v.max_pallets_11type IS NULL;

-- 기본값 설정
UPDATE vehicles
SET 
    max_pallets_11type = COALESCE(max_pallets_11type, max_pallets),
    max_pallets_12type = COALESCE(max_pallets_12type, FLOOR(max_pallets * 0.85)::INTEGER)
WHERE max_pallets_11type IS NULL OR max_pallets_12type IS NULL;

-- ============================================
-- 7. 인덱스 생성
-- ============================================
CREATE INDEX IF NOT EXISTS idx_clients_pallet_type ON clients(pallet_type);
CREATE INDEX IF NOT EXISTS idx_vehicles_temp_support ON vehicles(supports_frozen, supports_chilled, supports_ambient);
CREATE INDEX IF NOT EXISTS idx_orders_pallet_type ON orders(pallet_type);
CREATE INDEX IF NOT EXISTS idx_orders_calc_delivery ON orders(calculated_delivery_datetime);

