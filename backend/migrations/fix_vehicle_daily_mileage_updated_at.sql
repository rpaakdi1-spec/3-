-- Fix updated_at column to have default value
-- Run this if you already created the table with the previous migration

-- Add default to updated_at column
ALTER TABLE vehicle_daily_mileage 
    ALTER COLUMN updated_at SET DEFAULT NOW();

-- Update any existing NULL values
UPDATE vehicle_daily_mileage 
SET updated_at = created_at 
WHERE updated_at IS NULL;

-- Verify the fix
SELECT 
    column_name, 
    column_default, 
    is_nullable 
FROM information_schema.columns 
WHERE table_name = 'vehicle_daily_mileage' 
    AND column_name IN ('created_at', 'updated_at');
