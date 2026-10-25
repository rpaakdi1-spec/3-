-- ============================================================
-- 위치공유 방(Room) 시스템 테이블 생성 마이그레이션
-- 파일: backend/migrations/create_location_rooms.sql
-- 실행: cat backend/migrations/create_location_rooms.sql | docker compose exec -T db psql -U uvis_user -d uvis_db
-- ============================================================

-- ===== 1. location_rooms (위치공유 방) =====
CREATE TABLE IF NOT EXISTS location_rooms (
    id SERIAL PRIMARY KEY,

    -- 방 코드 (기사가 입력하는 8자리)
    room_code VARCHAR(20) NOT NULL UNIQUE,

    -- 방 기본 정보
    title VARCHAR(200) NOT NULL,
    description TEXT,

    -- 상태: 대기중 / 진행중 / 완료 / 취소
    status VARCHAR(20) NOT NULL DEFAULT '대기중',

    -- 생성자 (관리자)
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,

    -- 기사/차량 정보
    driver_name VARCHAR(100),
    driver_phone VARCHAR(20),
    vehicle_plate VARCHAR(20),

    -- 고객사 정보
    client_name VARCHAR(200),

    -- 토큰 (URL 공유용)
    driver_token VARCHAR(100) NOT NULL UNIQUE,   -- 기사용
    client_token VARCHAR(100) NOT NULL UNIQUE,   -- 고객사용

    -- 만료 시각 (NULL = 무제한)
    expires_at TIMESTAMP WITH TIME ZONE,

    -- 기사 입장/활동 정보
    driver_joined_at TIMESTAMP WITH TIME ZONE,
    driver_last_seen TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- 최근 위치 캐시 (빠른 조회용)
    last_latitude DOUBLE PRECISION,
    last_longitude DOUBLE PRECISION,
    last_location_at TIMESTAMP WITH TIME ZONE,

    -- 고객사 조회 통계
    client_view_count INTEGER NOT NULL DEFAULT 0,

    -- 메모 (관리자 내부용)
    notes TEXT,

    -- 타임스탬프
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS ix_location_rooms_room_code ON location_rooms(room_code);
CREATE INDEX IF NOT EXISTS ix_location_rooms_driver_token ON location_rooms(driver_token);
CREATE INDEX IF NOT EXISTS ix_location_rooms_client_token ON location_rooms(client_token);
CREATE INDEX IF NOT EXISTS ix_location_rooms_status ON location_rooms(status);
CREATE INDEX IF NOT EXISTS ix_location_rooms_created_at ON location_rooms(created_at DESC);

-- 코멘트
COMMENT ON TABLE location_rooms IS '위치공유 방 - 배차 독립적으로 기사 GPS 위치를 고객사에 공유';
COMMENT ON COLUMN location_rooms.room_code IS '방 입장 코드 (8자리 대문자+숫자)';
COMMENT ON COLUMN location_rooms.driver_token IS '기사용 접근 토큰 (URL 공유)';
COMMENT ON COLUMN location_rooms.client_token IS '고객사용 조회 토큰 (URL 공유)';
COMMENT ON COLUMN location_rooms.status IS '방 상태: 대기중/진행중/완료/취소';


-- ===== 2. room_locations (GPS 위치 이력) =====
CREATE TABLE IF NOT EXISTS room_locations (
    id SERIAL PRIMARY KEY,

    -- 방 참조
    room_id INTEGER NOT NULL REFERENCES location_rooms(id) ON DELETE CASCADE,

    -- GPS 좌표
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    accuracy DOUBLE PRECISION,       -- GPS 정확도 (미터)
    speed DOUBLE PRECISION,          -- 속도 (km/h)
    heading DOUBLE PRECISION,        -- 방향 (0-360도)

    -- 역지오코딩 주소 (선택)
    address VARCHAR(500),

    -- 기록 시각
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS ix_room_locations_room_id ON room_locations(room_id);
CREATE INDEX IF NOT EXISTS ix_room_locations_recorded_at ON room_locations(recorded_at);

-- 코멘트
COMMENT ON TABLE room_locations IS '위치공유 방 GPS 이력';
COMMENT ON COLUMN room_locations.room_id IS '위치공유 방 ID';
COMMENT ON COLUMN room_locations.accuracy IS 'GPS 정확도 (미터)';
COMMENT ON COLUMN room_locations.speed IS '속도 (km/h)';


-- ===== 3. room_documents (서류/사진 업로드) =====
CREATE TABLE IF NOT EXISTS room_documents (
    id SERIAL PRIMARY KEY,

    -- 방 참조
    room_id INTEGER NOT NULL REFERENCES location_rooms(id) ON DELETE CASCADE,

    -- 서류 분류
    document_type VARCHAR(20) NOT NULL,  -- 거래명세표 / 온도기록지 / 기타
    stage VARCHAR(10) NOT NULL,          -- 출발 / 도착

    -- 파일 정보
    file_url VARCHAR(500) NOT NULL,
    file_path VARCHAR(500),
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),

    -- 업로드 위치
    uploaded_lat DOUBLE PRECISION,
    uploaded_lon DOUBLE PRECISION,

    -- 메모
    notes TEXT,

    -- 타임스탬프
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS ix_room_documents_room_id ON room_documents(room_id);
CREATE INDEX IF NOT EXISTS ix_room_documents_stage ON room_documents(stage);

-- 코멘트
COMMENT ON TABLE room_documents IS '위치공유 방 서류(사진) 업로드';
COMMENT ON COLUMN room_documents.document_type IS '거래명세표 / 온도기록지 / 기타';
COMMENT ON COLUMN room_documents.stage IS '출발 / 도착';

-- ===== 완료 메시지 =====
DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE '✅ 위치공유 방(Room) 테이블 마이그레이션 완료!';
    RAISE NOTICE '   - location_rooms';
    RAISE NOTICE '   - room_locations';
    RAISE NOTICE '   - room_documents';
    RAISE NOTICE '=================================================';
END $$;
