-- 배차 템플릿 테이블 생성
-- 거래처별 자주 사용하는 배차 폼을 저장하고 재사용

CREATE TABLE IF NOT EXISTS dispatch_form_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,  -- 템플릿 이름 (예: "목우촌 오후배차")
    client_name VARCHAR(200) NOT NULL,  -- 거래처명 (예: "목우촌")
    category VARCHAR(100),  -- 카테고리 (예: "오후배차", "오전배차", "긴급배차")
    description TEXT,  -- 설명
    
    -- 템플릿 내용 (JSON 형식)
    template_data JSONB NOT NULL,
    /* 
    예시:
    {
      "dispatches": [
        {
          "time": "13:00",
          "vehicle_type": "식육18톤(냉동)",
          "tonnage": 18,
          "product_type": "식육",
          "temperature": "냉동",
          "pallet_count": 18,
          "notes": ""
        },
        {
          "time": "13:30",
          "vehicle_type": "식육11톤",
          "tonnage": 11,
          "product_type": "식육",
          "temperature": "냉장",
          "pallet_count": 16,
          "notes": ""
        }
      ],
      "default_pickup": "목우촌 물류센터",
      "default_delivery": "",
      "default_notes": ""
    }
    */
    
    -- 메타 정보
    usage_count INTEGER DEFAULT 0,  -- 사용 횟수
    is_active BOOLEAN DEFAULT TRUE,  -- 활성화 여부
    is_favorite BOOLEAN DEFAULT FALSE,  -- 즐겨찾기 여부
    
    -- 생성자 정보
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,  -- 마지막 사용 시간
    
    -- 검색 최적화를 위한 인덱스
    CONSTRAINT unique_template_name_per_client UNIQUE(client_name, name)
);

-- 인덱스 생성
CREATE INDEX idx_dispatch_form_templates_client_name ON dispatch_form_templates(client_name);
CREATE INDEX idx_dispatch_form_templates_category ON dispatch_form_templates(category);
CREATE INDEX idx_dispatch_form_templates_is_active ON dispatch_form_templates(is_active);
CREATE INDEX idx_dispatch_form_templates_is_favorite ON dispatch_form_templates(is_favorite);
CREATE INDEX idx_dispatch_form_templates_created_by ON dispatch_form_templates(created_by);
CREATE INDEX idx_dispatch_form_templates_name_search ON dispatch_form_templates USING gin(to_tsvector('simple', name));
CREATE INDEX idx_dispatch_form_templates_client_search ON dispatch_form_templates USING gin(to_tsvector('simple', client_name));

-- 업데이트 시간 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_dispatch_form_templates_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_dispatch_form_templates_updated_at
    BEFORE UPDATE ON dispatch_form_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_dispatch_form_templates_updated_at();

-- 샘플 데이터 삽입 (목우촌 오후배차 예시)
INSERT INTO dispatch_form_templates (name, client_name, category, description, template_data, created_by)
VALUES (
    '목우촌 오후배차',
    '목우촌',
    '오후배차',
    '목우촌 일반 오후 배차 템플릿 (13:00~16:30)',
    '{
        "dispatches": [
            {
                "time": "13:00",
                "vehicle_type": "식육18톤(냉동)",
                "tonnage": 18,
                "product_type": "식육",
                "temperature": "냉동",
                "pallet_count": 18,
                "notes": ""
            },
            {
                "time": "13:30",
                "vehicle_type": "식육11톤",
                "tonnage": 11,
                "product_type": "식육",
                "temperature": "냉장",
                "pallet_count": 16,
                "notes": ""
            },
            {
                "time": "15:00",
                "vehicle_type": "식육5톤",
                "tonnage": 5,
                "product_type": "식육",
                "temperature": "냉장",
                "pallet_count": 10,
                "notes": ""
            },
            {
                "time": "15:30",
                "vehicle_type": "육가공11톤",
                "tonnage": 11,
                "product_type": "육가공",
                "temperature": "냉장",
                "pallet_count": 16,
                "notes": ""
            },
            {
                "time": "16:30",
                "vehicle_type": "육가공11톤",
                "tonnage": 11,
                "product_type": "육가공",
                "temperature": "냉장",
                "pallet_count": 16,
                "notes": ""
            }
        ],
        "default_pickup": "목우촌 물류센터",
        "default_delivery": "",
        "default_notes": ""
    }'::jsonb,
    1  -- admin user
)
ON CONFLICT (client_name, name) DO NOTHING;

COMMENT ON TABLE dispatch_form_templates IS '배차 템플릿 저장소 - 거래처별 자주 사용하는 배차 폼';
COMMENT ON COLUMN dispatch_form_templates.name IS '템플릿 이름';
COMMENT ON COLUMN dispatch_form_templates.client_name IS '거래처명';
COMMENT ON COLUMN dispatch_form_templates.category IS '카테고리 (오전배차, 오후배차 등)';
COMMENT ON COLUMN dispatch_form_templates.template_data IS '템플릿 데이터 (JSON 형식)';
COMMENT ON COLUMN dispatch_form_templates.usage_count IS '템플릿 사용 횟수';
COMMENT ON COLUMN dispatch_form_templates.is_favorite IS '즐겨찾기 여부';
