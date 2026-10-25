"""
위치공유 방(Room) 테이블 마이그레이션

새로 생성되는 테이블:
- location_rooms: 위치공유 방 정보
- room_locations: 방 GPS 위치 이력
- room_documents: 방 서류(사진) 업로드
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

# DB URL
DATABASE_URL = settings.DATABASE_URL
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./dispatch.db"

print(f"[Migration] DB: {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)


def run_migration():
    """마이그레이션 실행"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    print(f"[Migration] 기존 테이블: {existing_tables}")

    with engine.connect() as conn:
        is_sqlite = "sqlite" in DATABASE_URL

        # ===== location_rooms 테이블 =====
        if "location_rooms" not in existing_tables:
            print("[Migration] location_rooms 테이블 생성 중...")
            if is_sqlite:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS location_rooms (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        room_code VARCHAR(20) NOT NULL UNIQUE,
                        title VARCHAR(200) NOT NULL,
                        description TEXT,
                        status VARCHAR(20) NOT NULL DEFAULT '대기중',
                        created_by INTEGER REFERENCES users(id),
                        driver_name VARCHAR(100),
                        driver_phone VARCHAR(20),
                        vehicle_plate VARCHAR(20),
                        client_name VARCHAR(200),
                        driver_token VARCHAR(100) NOT NULL UNIQUE,
                        client_token VARCHAR(100) NOT NULL UNIQUE,
                        expires_at DATETIME,
                        driver_joined_at DATETIME,
                        driver_last_seen DATETIME,
                        completed_at DATETIME,
                        last_latitude REAL,
                        last_longitude REAL,
                        last_location_at DATETIME,
                        client_view_count INTEGER NOT NULL DEFAULT 0,
                        notes TEXT,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """))
            else:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS location_rooms (
                        id SERIAL PRIMARY KEY,
                        room_code VARCHAR(20) NOT NULL UNIQUE,
                        title VARCHAR(200) NOT NULL,
                        description TEXT,
                        status VARCHAR(20) NOT NULL DEFAULT '대기중',
                        created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                        driver_name VARCHAR(100),
                        driver_phone VARCHAR(20),
                        vehicle_plate VARCHAR(20),
                        client_name VARCHAR(200),
                        driver_token VARCHAR(100) NOT NULL UNIQUE,
                        client_token VARCHAR(100) NOT NULL UNIQUE,
                        expires_at TIMESTAMP WITH TIME ZONE,
                        driver_joined_at TIMESTAMP WITH TIME ZONE,
                        driver_last_seen TIMESTAMP WITH TIME ZONE,
                        completed_at TIMESTAMP WITH TIME ZONE,
                        last_latitude FLOAT,
                        last_longitude FLOAT,
                        last_location_at TIMESTAMP WITH TIME ZONE,
                        client_view_count INTEGER NOT NULL DEFAULT 0,
                        notes TEXT,
                        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                    )
                """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_location_rooms_room_code ON location_rooms(room_code)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_location_rooms_driver_token ON location_rooms(driver_token)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_location_rooms_client_token ON location_rooms(client_token)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_location_rooms_status ON location_rooms(status)"))
            conn.commit()
            print("[Migration] ✅ location_rooms 테이블 생성 완료")
        else:
            print("[Migration] ⏭️  location_rooms 테이블 이미 존재")

        # ===== room_locations 테이블 =====
        if "room_locations" not in existing_tables:
            print("[Migration] room_locations 테이블 생성 중...")
            if is_sqlite:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS room_locations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        room_id INTEGER NOT NULL REFERENCES location_rooms(id) ON DELETE CASCADE,
                        latitude REAL NOT NULL,
                        longitude REAL NOT NULL,
                        accuracy REAL,
                        speed REAL,
                        heading REAL,
                        address VARCHAR(500),
                        recorded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """))
            else:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS room_locations (
                        id SERIAL PRIMARY KEY,
                        room_id INTEGER NOT NULL REFERENCES location_rooms(id) ON DELETE CASCADE,
                        latitude FLOAT NOT NULL,
                        longitude FLOAT NOT NULL,
                        accuracy FLOAT,
                        speed FLOAT,
                        heading FLOAT,
                        address VARCHAR(500),
                        recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    )
                """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_room_locations_room_id ON room_locations(room_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_room_locations_recorded_at ON room_locations(recorded_at)"))
            conn.commit()
            print("[Migration] ✅ room_locations 테이블 생성 완료")
        else:
            print("[Migration] ⏭️  room_locations 테이블 이미 존재")

        # ===== room_documents 테이블 =====
        if "room_documents" not in existing_tables:
            print("[Migration] room_documents 테이블 생성 중...")
            if is_sqlite:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS room_documents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        room_id INTEGER NOT NULL REFERENCES location_rooms(id) ON DELETE CASCADE,
                        document_type VARCHAR(20) NOT NULL,
                        stage VARCHAR(10) NOT NULL,
                        file_url VARCHAR(500) NOT NULL,
                        file_path VARCHAR(500),
                        file_name VARCHAR(255) NOT NULL,
                        file_size INTEGER,
                        mime_type VARCHAR(100),
                        uploaded_lat REAL,
                        uploaded_lon REAL,
                        notes TEXT,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """))
            else:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS room_documents (
                        id SERIAL PRIMARY KEY,
                        room_id INTEGER NOT NULL REFERENCES location_rooms(id) ON DELETE CASCADE,
                        document_type VARCHAR(20) NOT NULL,
                        stage VARCHAR(10) NOT NULL,
                        file_url VARCHAR(500) NOT NULL,
                        file_path VARCHAR(500),
                        file_name VARCHAR(255) NOT NULL,
                        file_size INTEGER,
                        mime_type VARCHAR(100),
                        uploaded_lat FLOAT,
                        uploaded_lon FLOAT,
                        notes TEXT,
                        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                    )
                """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_room_documents_room_id ON room_documents(room_id)"))
            conn.commit()
            print("[Migration] ✅ room_documents 테이블 생성 완료")
        else:
            print("[Migration] ⏭️  room_documents 테이블 이미 존재")

    print("\n[Migration] 🎉 마이그레이션 완료!")


if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"[Migration] ❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
