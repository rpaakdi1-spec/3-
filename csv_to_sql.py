#!/usr/bin/env python3
"""
CSV 배차 템플릿 -> SQL 변환기
"""
import csv
import sys
import json
from pathlib import Path

def calculate_tonnage(pallet_count):
    """팔레트 수 -> 톤수 계산"""
    if pallet_count >= 18:
        return 15
    elif pallet_count >= 16:
        return 11
    elif pallet_count >= 14:
        return 10
    elif pallet_count >= 12:
        return 8
    elif pallet_count >= 10:
        return 5
    else:
        return 3

def make_client_code(name):
    """거래처명 -> 코드 변환"""
    # 공백 제거 후 대문자로
    return name.replace(" ", "_").replace("(", "_").replace(")", "").upper()

def convert_csv_to_sql(csv_path):
    """CSV 파일을 SQL로 변환"""
    
    sql_lines = []
    sql_lines.append("-- Auto-generated from CSV")
    sql_lines.append("-- Generated at: " + str(Path(csv_path).name))
    sql_lines.append("")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for idx, row in enumerate(reader, 1):
            template_name = row['템플릿명'].strip()
            pickup_client = row['상차거래처'].strip()
            delivery_client = row['하차거래처'].strip()
            category = row['카테고리'].strip()
            pickup_time = row['상차시간'].strip()
            pallet_count = int(row['팔레트'].strip())
            temperature = row['온도'].strip()
            pickup_addr = row['상차주소'].strip()
            pickup_lat = float(row['상차위도'].strip())
            pickup_lon = float(row['상차경도'].strip())
            delivery_addr = row['하차주소'].strip()
            delivery_lat = float(row['하차위도'].strip())
            delivery_lon = float(row['하차경도'].strip())
            delivery_time = row['하차완료시간'].strip()
            notes = row.get('비고', '').strip()
            
            # 톤수 계산
            tonnage = calculate_tonnage(pallet_count)
            
            # 클라이언트 코드 생성
            pickup_code = make_client_code(pickup_client)
            delivery_code = make_client_code(delivery_client)
            
            # 차량 타입 (예: "냉동16팔레트")
            vehicle_type = f"{temperature}{pallet_count}팔레트"
            
            # 제품명
            product_type = f"{temperature}식품 {tonnage}톤"
            
            # 비고 조합
            full_notes = f"상차 {pickup_time}, 하차 완료 {delivery_time}까지"
            if notes:
                full_notes += f" ({notes})"
            
            sql_lines.append(f"-- Template {idx}: {template_name}")
            
            # 1. 상차지 거래처 INSERT
            sql_lines.append(f"""
INSERT INTO clients (code, name, client_type, address, latitude, longitude, geocoded, loading_time_minutes, is_active)
VALUES (
  '{pickup_code}',
  '{pickup_client}',
  'PICKUP',
  '{pickup_addr}',
  {pickup_lat},
  {pickup_lon},
  true,
  30,
  true
)
ON CONFLICT (code) DO UPDATE SET
  address = EXCLUDED.address,
  latitude = EXCLUDED.latitude,
  longitude = EXCLUDED.longitude,
  geocoded = EXCLUDED.geocoded;
""")
            
            # 2. 하차지 거래처 INSERT (다른 경우만)
            if pickup_client != delivery_client:
                sql_lines.append(f"""
INSERT INTO clients (code, name, client_type, address, latitude, longitude, geocoded, loading_time_minutes, is_active)
VALUES (
  '{delivery_code}',
  '{delivery_client}',
  'DELIVERY',
  '{delivery_addr}',
  {delivery_lat},
  {delivery_lon},
  true,
  30,
  true
)
ON CONFLICT (code) DO UPDATE SET
  address = EXCLUDED.address,
  latitude = EXCLUDED.latitude,
  longitude = EXCLUDED.longitude,
  geocoded = EXCLUDED.geocoded;
""")
            
            # 3. 템플릿 데이터 JSON 생성
            template_data = {
                "dispatches": [
                    {
                        "time": pickup_time,
                        "vehicle_type": vehicle_type,
                        "tonnage": tonnage,
                        "product_type": product_type,
                        "temperature": temperature,
                        "pallet_count": pallet_count,
                        "notes": full_notes
                    }
                ],
                "default_pickup": pickup_addr,
                "default_delivery": delivery_addr,
                "default_notes": full_notes
            }
            
            template_json = json.dumps(template_data, ensure_ascii=False)
            # SQL에서 작은따옴표 이스케이프
            template_json_escaped = template_json.replace("'", "''")
            
            # 4. 템플릿 INSERT
            description = f"{pickup_client} → {delivery_client} 배차 템플릿 ({pickup_time}, {vehicle_type})"
            
            sql_lines.append(f"""
INSERT INTO dispatch_form_templates (name, client_name, category, description, template_data, created_by, is_active)
VALUES (
  '{template_name}',
  '{pickup_client}',
  '{category}',
  '{description}',
  '{template_json_escaped}'::jsonb,
  1,
  true
)
ON CONFLICT (name, client_name) DO UPDATE SET
  category = EXCLUDED.category,
  description = EXCLUDED.description,
  template_data = EXCLUDED.template_data,
  is_active = EXCLUDED.is_active;
""")
            
            sql_lines.append("")
    
    # 확인 쿼리
    sql_lines.append("""
-- 확인
SELECT 
    id,
    name AS 템플릿명,
    client_name AS 거래처,
    category AS 카테고리,
    template_data->'dispatches'->0->>'time' AS 시간,
    template_data->'dispatches'->0->>'pallet_count' AS 팔레트,
    template_data->'dispatches'->0->>'temperature' AS 온도,
    template_data->>'default_pickup' AS 상차지,
    template_data->>'default_delivery' AS 하차지
FROM dispatch_form_templates
ORDER BY client_name, name;
""")
    
    return "\n".join(sql_lines)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python3 csv_to_sql.py <csv파일경로>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    if not Path(csv_path).exists():
        print(f"❌ 파일을 찾을 수 없습니다: {csv_path}")
        sys.exit(1)
    
    sql = convert_csv_to_sql(csv_path)
    print(sql)
