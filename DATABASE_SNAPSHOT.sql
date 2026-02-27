-- ============================================================================
-- Database Snapshot: error-fully-corrected (2026-02-27)
-- ============================================================================
-- 이 파일은 "error-fully-corrected" 상태의 데이터베이스 스키마 변경사항을 
-- 문서화합니다. 롤백 시 이 스크립트를 참조하여 스키마를 복원할 수 있습니다.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. VehicleLocation 테이블 - timestamp 컬럼 추가
-- ----------------------------------------------------------------------------
-- 목적: Telemetry API 500 에러 해결
-- 커밋: eac74cd, 1587141
-- 날짜: 2026-02-27

-- 변경 전 체크
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'vehicle_locations' 
        AND column_name = 'timestamp'
    ) THEN
        -- timestamp 컬럼 추가
        ALTER TABLE vehicle_locations 
        ADD COLUMN timestamp TIMESTAMP;
        
        -- 기존 데이터에 대해 recorded_at 값으로 초기화
        UPDATE vehicle_locations 
        SET timestamp = recorded_at 
        WHERE timestamp IS NULL;
        
        RAISE NOTICE 'Added timestamp column to vehicle_locations';
    ELSE
        RAISE NOTICE 'timestamp column already exists in vehicle_locations';
    END IF;
END $$;

-- 인덱스 추가 (성능 향상)
CREATE INDEX IF NOT EXISTS idx_vehicle_locations_timestamp 
ON vehicle_locations(timestamp DESC);

-- ----------------------------------------------------------------------------
-- 2. Clients 테이블 - 누락된 컬럼 추가
-- ----------------------------------------------------------------------------
-- 목적: Clients API 500 에러 해결
-- 날짜: 2026-02-27

-- 변경 전 체크 및 컬럼 추가
DO $$
BEGIN
    -- address_detail 컬럼
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'clients' 
        AND column_name = 'address_detail'
    ) THEN
        ALTER TABLE clients 
        ADD COLUMN address_detail TEXT;
        RAISE NOTICE 'Added address_detail column to clients';
    END IF;

    -- geocoded 컬럼
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'clients' 
        AND column_name = 'geocoded'
    ) THEN
        ALTER TABLE clients 
        ADD COLUMN geocoded BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added geocoded column to clients';
    END IF;

    -- latitude 컬럼
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'clients' 
        AND column_name = 'latitude'
    ) THEN
        ALTER TABLE clients 
        ADD COLUMN latitude DECIMAL(10, 8);
        RAISE NOTICE 'Added latitude column to clients';
    END IF;

    -- longitude 컬럼
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'clients' 
        AND column_name = 'longitude'
    ) THEN
        ALTER TABLE clients 
        ADD COLUMN longitude DECIMAL(11, 8);
        RAISE NOTICE 'Added longitude column to clients';
    END IF;
END $$;

-- 인덱스 추가 (지리적 쿼리 성능 향상)
CREATE INDEX IF NOT EXISTS idx_clients_location 
ON clients(latitude, longitude) 
WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

-- ----------------------------------------------------------------------------
-- 3. 데이터베이스 현재 상태 확인
-- ----------------------------------------------------------------------------

-- 테이블별 레코드 수
SELECT 
    'orders' as table_name, 
    COUNT(*) as record_count 
FROM orders
UNION ALL
SELECT 
    'dispatches', 
    COUNT(*) 
FROM dispatches
UNION ALL
SELECT 
    'clients', 
    COUNT(*) 
FROM clients
UNION ALL
SELECT 
    'vehicles', 
    COUNT(*) 
FROM vehicles
UNION ALL
SELECT 
    'vehicle_locations', 
    COUNT(*) 
FROM vehicle_locations
UNION ALL
SELECT 
    'temperature_alerts', 
    COUNT(*) 
FROM temperature_alerts
ORDER BY table_name;

-- ----------------------------------------------------------------------------
-- 4. 스키마 검증 쿼리
-- ----------------------------------------------------------------------------

-- vehicle_locations 테이블 스키마 확인
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'vehicle_locations'
ORDER BY ordinal_position;

-- clients 테이블 스키마 확인
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'clients'
ORDER BY ordinal_position;

-- ----------------------------------------------------------------------------
-- 5. 롤백 스크립트 (필요 시 사용)
-- ----------------------------------------------------------------------------

-- ⚠️ 주의: 이 스크립트는 스키마 변경을 롤백합니다
-- 데이터 손실이 발생할 수 있으므로 백업 후 실행하세요

/*
-- VehicleLocation timestamp 컬럼 제거
ALTER TABLE vehicle_locations DROP COLUMN IF EXISTS timestamp;

-- Clients 추가 컬럼 제거
ALTER TABLE clients DROP COLUMN IF EXISTS address_detail;
ALTER TABLE clients DROP COLUMN IF EXISTS geocoded;
ALTER TABLE clients DROP COLUMN IF EXISTS latitude;
ALTER TABLE clients DROP COLUMN IF EXISTS longitude;

-- 인덱스 제거
DROP INDEX IF EXISTS idx_vehicle_locations_timestamp;
DROP INDEX IF EXISTS idx_clients_location;
*/

-- ----------------------------------------------------------------------------
-- 6. 데이터베이스 백업 명령
-- ----------------------------------------------------------------------------

-- 백업 생성 (서버에서 실행)
-- docker-compose exec db pg_dump -U uvis_user -d uvis_db > backup_error_corrected_$(date +%Y%m%d_%H%M%S).sql

-- 백업 복원 (서버에서 실행)
-- docker-compose exec -T db psql -U uvis_user -d uvis_db < backup_error_corrected_YYYYMMDD_HHMMSS.sql

-- ----------------------------------------------------------------------------
-- 7. 테스트 데이터 확인
-- ----------------------------------------------------------------------------

-- 최근 vehicle_location 레코드 (timestamp 포함)
SELECT 
    id,
    vehicle_id,
    latitude,
    longitude,
    recorded_at,
    timestamp,
    created_at
FROM vehicle_locations
ORDER BY created_at DESC
LIMIT 5;

-- 클라이언트 데이터 (새 컬럼 포함)
SELECT 
    id,
    name,
    phone,
    address,
    address_detail,
    geocoded,
    latitude,
    longitude
FROM clients
LIMIT 5;

-- ----------------------------------------------------------------------------
-- 8. 성능 통계
-- ----------------------------------------------------------------------------

-- 테이블 크기 확인
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 인덱스 사용 통계
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- ----------------------------------------------------------------------------
-- 9. 데이터 무결성 검증
-- ----------------------------------------------------------------------------

-- vehicle_locations 무결성 체크
SELECT 
    COUNT(*) as total_records,
    COUNT(timestamp) as records_with_timestamp,
    COUNT(*) - COUNT(timestamp) as records_without_timestamp,
    MIN(timestamp) as earliest_timestamp,
    MAX(timestamp) as latest_timestamp
FROM vehicle_locations;

-- clients 무결성 체크
SELECT 
    COUNT(*) as total_clients,
    COUNT(geocoded) as clients_with_geocoded_flag,
    SUM(CASE WHEN geocoded THEN 1 ELSE 0 END) as geocoded_clients,
    COUNT(latitude) as clients_with_latitude,
    COUNT(longitude) as clients_with_longitude
FROM clients;

-- ----------------------------------------------------------------------------
-- 생성일: 2026-02-27
-- 버전: 1.0.0
-- 상태: error-fully-corrected
-- 태그: error-fully-corrected, v1.0.0-all-errors-fixed
-- ============================================================================
