-- Add driver_name and driver_phone columns to vehicles table
ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS driver_name VARCHAR(100);
ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS driver_phone VARCHAR(20);

-- Add comments
COMMENT ON COLUMN vehicles.driver_name IS '운전자명';
COMMENT ON COLUMN vehicles.driver_phone IS '운전자 연락처';
