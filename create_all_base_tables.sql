-- ====================================================================
-- UVIS 데이터베이스 전체 스키마 생성 스크립트
-- ====================================================================
-- 이 스크립트는 모든 기본 테이블을 생성합니다.
-- baseline 마이그레이션이 비어있어서 수동으로 생성해야 합니다.
-- ====================================================================

-- 1. users 테이블 (가장 먼저 생성 - 다른 테이블들이 참조함)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    phone VARCHAR(20),  -- a6eb2e22dbd2 마이그레이션에서 추가하려던 컬럼
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    department VARCHAR(100),
    position VARCHAR(100),
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. notifications 테이블
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) DEFAULT 'info',
    priority VARCHAR(20) DEFAULT 'normal',
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    meta_data JSONB,  -- a6eb2e22dbd2 마이그레이션에서 추가하려던 컬럼
    link_url VARCHAR(500),
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. clients 테이블
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    business_registration_number VARCHAR(20),
    representative VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    client_type VARCHAR(50) DEFAULT 'REGULAR',
    credit_rating VARCHAR(20),
    payment_terms VARCHAR(100),
    contract_start_date DATE,
    contract_end_date DATE,
    discount_rate DECIMAL(5, 2) DEFAULT 0,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. drivers 테이블
CREATE TABLE IF NOT EXISTS drivers (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    license_number VARCHAR(50),
    license_type VARCHAR(20),
    license_expiry_date DATE,
    employment_type VARCHAR(20),
    hire_date DATE,
    termination_date DATE,
    hourly_rate DECIMAL(10, 2),
    overtime_rate DECIMAL(10, 2),
    status VARCHAR(20) DEFAULT 'AVAILABLE',
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. vehicles 테이블
CREATE TABLE IF NOT EXISTS vehicles (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    plate_number VARCHAR(20) UNIQUE NOT NULL,
    vehicle_type VARCHAR(50),
    uvis_device_id VARCHAR(50),
    uvis_enabled BOOLEAN DEFAULT FALSE,
    max_pallets INTEGER,
    max_weight_kg DECIMAL(10, 2),
    max_volume_cbm DECIMAL(10, 2),
    forklift_operator_available BOOLEAN DEFAULT FALSE,
    tonnage DECIMAL(5, 2),
    length_m DECIMAL(5, 2),
    width_m DECIMAL(5, 2),
    height_m DECIMAL(5, 2),
    driver_name VARCHAR(100),
    driver_phone VARCHAR(20),
    min_temp_celsius DECIMAL(5, 2),
    max_temp_celsius DECIMAL(5, 2),
    fuel_efficiency_km_per_liter DECIMAL(5, 2),
    fuel_cost_per_liter DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'AVAILABLE',
    garage_address TEXT,
    garage_latitude DECIMAL(10, 8),
    garage_longitude DECIMAL(11, 8),
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    -- 긴급 상황 관련 컬럼들
    is_emergency BOOLEAN DEFAULT FALSE,
    emergency_type VARCHAR(50),
    emergency_severity VARCHAR(20),
    emergency_reported_at TIMESTAMP,
    emergency_location TEXT,
    emergency_description TEXT,
    estimated_repair_time INTEGER,
    replacement_vehicle_id INTEGER REFERENCES vehicles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. orders 테이블
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    client_id INTEGER REFERENCES clients(id),
    order_date DATE NOT NULL,
    delivery_date DATE NOT NULL,
    pickup_address TEXT,
    pickup_latitude DECIMAL(10, 8),
    pickup_longitude DECIMAL(11, 8),
    delivery_address TEXT NOT NULL,
    delivery_latitude DECIMAL(10, 8),
    delivery_longitude DECIMAL(11, 8),
    distance_km DECIMAL(10, 2),
    num_pallets INTEGER DEFAULT 0,
    weight_kg DECIMAL(10, 2),
    volume_cbm DECIMAL(10, 2),
    requires_forklift BOOLEAN DEFAULT FALSE,
    temperature_min DECIMAL(5, 2),
    temperature_max DECIMAL(5, 2),
    product_type VARCHAR(100),
    product_name VARCHAR(200),
    delivery_time_start TIME,
    delivery_time_end TIME,
    priority VARCHAR(20) DEFAULT 'NORMAL',
    status VARCHAR(50) DEFAULT 'PENDING',
    notes TEXT,
    special_instructions TEXT,
    -- AI 관련 컬럼들
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_pattern VARCHAR(50),
    recurring_days VARCHAR(20),
    is_urgent BOOLEAN DEFAULT FALSE,
    urgency_level INTEGER,
    urgent_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. dispatches 테이블
CREATE TABLE IF NOT EXISTS dispatches (
    id SERIAL PRIMARY KEY,
    dispatch_number VARCHAR(50) UNIQUE NOT NULL,
    dispatch_date DATE NOT NULL,
    vehicle_id INTEGER REFERENCES vehicles(id),
    driver_id INTEGER REFERENCES drivers(id),
    total_orders INTEGER DEFAULT 0,
    total_pallets INTEGER DEFAULT 0,
    total_weight_kg DECIMAL(10, 2),
    total_distance_km DECIMAL(10, 2),
    empty_distance_km DECIMAL(10, 2),
    estimated_duration_minutes INTEGER,
    planned_start_time TIME,
    planned_end_time TIME,
    estimated_cost DECIMAL(12, 2),
    status VARCHAR(50) DEFAULT 'DRAFT',
    -- 스케줄링 관련
    is_scheduled BOOLEAN DEFAULT FALSE,
    scheduled_for_date DATE,
    auto_confirm_at TIMESTAMP,
    -- 반복 배차 관련
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_pattern VARCHAR(50),
    recurring_days VARCHAR(20),
    -- 긴급 배차 관련
    is_urgent BOOLEAN DEFAULT FALSE,
    urgency_level INTEGER,
    urgent_reason TEXT,
    -- AI 최적화 관련
    optimization_score DECIMAL(5, 2),
    ai_metadata JSONB,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. dispatch_orders 테이블 (배차-주문 매핑)
CREATE TABLE IF NOT EXISTS dispatch_orders (
    id SERIAL PRIMARY KEY,
    dispatch_id INTEGER REFERENCES dispatches(id) ON DELETE CASCADE,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    sequence INTEGER NOT NULL,
    estimated_arrival_time TIME,
    estimated_departure_time TIME,
    distance_from_previous_km DECIMAL(10, 2),
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    actual_arrival_time TIMESTAMP,
    actual_departure_time TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(dispatch_id, order_id)
);

-- 9. temperature_logs 테이블
CREATE TABLE IF NOT EXISTS temperature_logs (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES vehicles(id),
    dispatch_id INTEGER REFERENCES dispatches(id),
    order_id INTEGER REFERENCES orders(id),
    temperature_celsius DECIMAL(5, 2) NOT NULL,
    humidity_percent DECIMAL(5, 2),
    location_latitude DECIMAL(10, 8),
    location_longitude DECIMAL(11, 8),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    device_id VARCHAR(100),
    is_alert BOOLEAN DEFAULT FALSE,
    alert_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. ml_training_data 테이블
CREATE TABLE IF NOT EXISTS ml_training_data (
    id SERIAL PRIMARY KEY,
    data_type VARCHAR(50) NOT NULL,
    feature_data JSONB NOT NULL,
    target_value DECIMAL(12, 2),
    metadata JSONB,
    is_validated BOOLEAN DEFAULT FALSE,
    training_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. api_logs 테이블
CREATE TABLE IF NOT EXISTS api_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    method VARCHAR(10) NOT NULL,
    endpoint VARCHAR(500) NOT NULL,
    status_code INTEGER NOT NULL,
    request_body TEXT,
    response_body TEXT,
    ip_address VARCHAR(50),
    user_agent TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 12. system_settings 테이블
CREATE TABLE IF NOT EXISTS system_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(50) DEFAULT 'string',
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================================
-- 인덱스 생성
-- ====================================================================

-- users 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- notifications 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);

-- clients 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_clients_code ON clients(code);
CREATE INDEX IF NOT EXISTS idx_clients_is_active ON clients(is_active);

-- drivers 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_drivers_code ON drivers(code);
CREATE INDEX IF NOT EXISTS idx_drivers_status ON drivers(status);
CREATE INDEX IF NOT EXISTS idx_drivers_is_active ON drivers(is_active);

-- vehicles 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_vehicles_code ON vehicles(code);
CREATE INDEX IF NOT EXISTS idx_vehicles_plate_number ON vehicles(plate_number);
CREATE INDEX IF NOT EXISTS idx_vehicles_status ON vehicles(status);
CREATE INDEX IF NOT EXISTS idx_vehicles_is_active ON vehicles(is_active);
CREATE INDEX IF NOT EXISTS idx_vehicles_is_emergency ON vehicles(is_emergency);

-- orders 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_orders_order_number ON orders(order_number);
CREATE INDEX IF NOT EXISTS idx_orders_client_id ON orders(client_id);
CREATE INDEX IF NOT EXISTS idx_orders_delivery_date ON orders(delivery_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- dispatches 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_dispatches_dispatch_number ON dispatches(dispatch_number);
CREATE INDEX IF NOT EXISTS idx_dispatches_vehicle_id ON dispatches(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_dispatches_driver_id ON dispatches(driver_id);
CREATE INDEX IF NOT EXISTS idx_dispatches_dispatch_date ON dispatches(dispatch_date);
CREATE INDEX IF NOT EXISTS idx_dispatches_status ON dispatches(status);

-- dispatch_orders 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_dispatch_orders_dispatch_id ON dispatch_orders(dispatch_id);
CREATE INDEX IF NOT EXISTS idx_dispatch_orders_order_id ON dispatch_orders(order_id);

-- temperature_logs 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_temperature_logs_vehicle_id ON temperature_logs(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_temperature_logs_dispatch_id ON temperature_logs(dispatch_id);
CREATE INDEX IF NOT EXISTS idx_temperature_logs_recorded_at ON temperature_logs(recorded_at);
CREATE INDEX IF NOT EXISTS idx_temperature_logs_is_alert ON temperature_logs(is_alert);

-- api_logs 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_api_logs_user_id ON api_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_api_logs_endpoint ON api_logs(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_logs_created_at ON api_logs(created_at);

-- ====================================================================
-- 완료!
-- ====================================================================

-- 테이블 생성 확인
SELECT 
    schemaname,
    tablename
FROM pg_catalog.pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
