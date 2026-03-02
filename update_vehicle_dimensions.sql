-- 차량 적재함 길이 일괄 업데이트
-- 5톤 = 6.0m, 11톤 = 9m, 18톤 = 12.2m

-- 1. 5톤 차량 업데이트
UPDATE vehicles 
SET length_m = 6.0,
    width_m = 2.3,
    height_m = 2.3,
    updated_at = NOW()
WHERE tonnage >= 4.5 AND tonnage < 7.5 
  AND is_active = true;

-- 2. 11톤 차량 업데이트
UPDATE vehicles 
SET length_m = 9.0,
    width_m = 2.4,
    height_m = 2.5,
    updated_at = NOW()
WHERE tonnage >= 10 AND tonnage < 15
  AND is_active = true;

-- 3. 18톤 차량 업데이트
UPDATE vehicles 
SET length_m = 12.2,
    width_m = 2.5,
    height_m = 2.7,
    updated_at = NOW()
WHERE tonnage >= 15
  AND is_active = true;

-- 4. 2.5톤 차량 업데이트 (추가)
UPDATE vehicles 
SET length_m = 4.5,
    width_m = 2.0,
    height_m = 2.0,
    updated_at = NOW()
WHERE tonnage >= 2.0 AND tonnage < 4.5
  AND is_active = true;

-- 5. 1톤 차량 업데이트 (추가)
UPDATE vehicles 
SET length_m = 2.4,
    width_m = 1.6,
    height_m = 1.8,
    updated_at = NOW()
WHERE tonnage < 2.0
  AND is_active = true;

-- 업데이트 결과 확인
SELECT tonnage, 
       COUNT(*) as count,
       AVG(length_m) as avg_length,
       AVG(width_m) as avg_width,
       AVG(height_m) as avg_height
FROM vehicles 
WHERE is_active = true
GROUP BY tonnage
ORDER BY tonnage;
