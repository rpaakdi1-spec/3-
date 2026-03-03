-- 거래처별 배차 템플릿 테이블 생성
CREATE TABLE IF NOT EXISTS dispatch_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- 식별 패턴
    detection_keywords JSONB NOT NULL,
    
    -- 기본 주소
    default_pickup_address VARCHAR(500),
    default_delivery_address VARCHAR(500),
    
    -- 고정 좌표
    pickup_latitude DOUBLE PRECISION,
    pickup_longitude DOUBLE PRECISION,
    delivery_latitude DOUBLE PRECISION,
    delivery_longitude DOUBLE PRECISION,
    
    -- 파싱 규칙
    parsing_rules JSONB NOT NULL DEFAULT '{}',
    
    -- 사용 통계
    usage_count INTEGER NOT NULL DEFAULT 0,
    
    -- 타임스탬프
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_dispatch_templates_name ON dispatch_templates(name);
CREATE INDEX IF NOT EXISTS idx_dispatch_templates_is_active ON dispatch_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_dispatch_templates_detection_keywords ON dispatch_templates USING GIN(detection_keywords);

-- 목우촌 템플릿 기본 데이터 삽입
INSERT INTO dispatch_templates (
    name,
    description,
    is_active,
    detection_keywords,
    default_pickup_address,
    default_delivery_address,
    pickup_latitude,
    pickup_longitude,
    delivery_latitude,
    delivery_longitude,
    parsing_rules,
    usage_count
) VALUES (
    '목우촌',
    '목우촌 오후배차 자동 파싱 템플릿',
    TRUE,
    '["목우촌", "mokwoojon"]'::jsonb,
    '전북 김제시 금산면 용산리 9-13',
    '경기도 안성시 양성면 양성로 376-106',
    35.8087,
    126.8919,
    37.0088,
    127.2668,
    '{
        "time_pattern": "(\\d{1,2}:\\d{2})",
        "product_pattern": "식육|육가공",
        "tonnage_pattern": "(\\d+\\.?\\d*)톤",
        "temperature_keywords": {
            "냉동": "FROZEN",
            "냉장": "REFRIGERATED"
        },
        "default_temperature": "REFRIGERATED",
        "pallet_calculation": {
            "18": 18,
            "11": 16,
            "5": 10,
            "default_multiplier": 2
        },
        "delivery_time_offset_hours": 4,
        "notes_template": "자동 파싱: 목우촌 배차"
    }'::jsonb,
    0
) ON CONFLICT (name) DO NOTHING;

-- 업데이트 트리거 함수
CREATE OR REPLACE FUNCTION update_dispatch_template_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 생성
DROP TRIGGER IF EXISTS trigger_update_dispatch_template_updated_at ON dispatch_templates;
CREATE TRIGGER trigger_update_dispatch_template_updated_at
    BEFORE UPDATE ON dispatch_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_dispatch_template_updated_at();

COMMENT ON TABLE dispatch_templates IS '거래처별 배차 템플릿 - 자동 파싱 규칙 관리';
COMMENT ON COLUMN dispatch_templates.detection_keywords IS '배차 텍스트에서 이 템플릿을 식별하는 키워드 목록 (JSON array)';
COMMENT ON COLUMN dispatch_templates.parsing_rules IS '파싱 규칙 (정규식 패턴, 온도 매핑, 팔레트 계산 등)';
