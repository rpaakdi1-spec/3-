-- 운전자 일별 주행거리 테이블의 driver_id를 NULL 허용으로 변경
-- 차량 테이블 기반 계산을 위해 필요

-- 1. 기존 제약조건 삭제
ALTER TABLE driver_daily_mileage 
DROP CONSTRAINT IF EXISTS uq_driver_daily_mileage_driver_date;

-- 2. driver_id를 NULL 허용으로 변경
ALTER TABLE driver_daily_mileage 
ALTER COLUMN driver_id DROP NOT NULL;

-- 3. 외래키 제약조건 이름 확인 및 삭제
DO $$ 
DECLARE
    constraint_name TEXT;
BEGIN
    -- 외래키 제약조건 이름 찾기
    SELECT conname INTO constraint_name
    FROM pg_constraint
    WHERE conrelid = 'driver_daily_mileage'::regclass
    AND contype = 'f'
    AND confrelid = 'drivers'::regclass
    LIMIT 1;
    
    -- 외래키 제약조건 삭제
    IF constraint_name IS NOT NULL THEN
        EXECUTE format('ALTER TABLE driver_daily_mileage DROP CONSTRAINT %I', constraint_name);
    END IF;
END $$;

-- 4. 외래키 제약조건을 NULL 허용으로 재생성
ALTER TABLE driver_daily_mileage
ADD CONSTRAINT fk_driver_daily_mileage_driver 
FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE CASCADE;

-- 5. 새로운 유니크 제약조건 추가 (driver_id가 NULL이 아닐 때만)
-- PostgreSQL의 partial unique index 사용
DROP INDEX IF EXISTS uq_driver_daily_mileage_driver_date;
CREATE UNIQUE INDEX uq_driver_daily_mileage_driver_date 
ON driver_daily_mileage(driver_id, date) 
WHERE driver_id IS NOT NULL;

-- 6. notes 필드에 대한 유니크 제약조건 추가 (차량 기반 계산용)
CREATE UNIQUE INDEX uq_driver_daily_mileage_notes_date 
ON driver_daily_mileage(notes, date) 
WHERE notes IS NOT NULL AND notes LIKE '차량기반:%';

-- 7. 코멘트 업데이트
COMMENT ON COLUMN driver_daily_mileage.driver_id IS '운전자 ID (NULL 가능: 차량 기반 계산 시)';
COMMENT ON COLUMN driver_daily_mileage.notes IS '메모 (차량기반:운전자명 형식으로 저장)';
COMMENT ON COLUMN driver_daily_mileage.calculation_method IS '계산 방식 (dispatch_based 또는 vehicle_based)';
