"""
위치공유방 상/하차지 + 타임라인 컬럼 직접 추가 스크립트
Alembic 체인 문제 우회용 - 직접 PostgreSQL에 컬럼 추가

사용법:
  docker compose exec backend python migrate_location_rooms.py
"""
import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL 환경변수가 없습니다")

print(f"DB 연결 중: {DATABASE_URL[:50]}...")

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = False
cur = conn.cursor()

COLUMNS = [
    # 상차지
    ("loading_name",        "VARCHAR(200)"),
    ("loading_address",     "VARCHAR(500)"),
    ("loading_lat",         "DOUBLE PRECISION"),
    ("loading_lng",         "DOUBLE PRECISION"),
    # 하차지
    ("unloading_name",      "VARCHAR(200)"),
    ("unloading_address",   "VARCHAR(500)"),
    ("unloading_lat",       "DOUBLE PRECISION"),
    ("unloading_lng",       "DOUBLE PRECISION"),
    # 타임라인
    ("arrived_at_loading",    "TIMESTAMPTZ"),
    ("departed_loading",      "TIMESTAMPTZ"),
    ("arrived_at_unloading",  "TIMESTAMPTZ"),
    ("departed_unloading",    "TIMESTAMPTZ"),
    # geofence 플래그
    ("in_loading_zone",    "BOOLEAN NOT NULL DEFAULT FALSE"),
    ("in_unloading_zone",  "BOOLEAN NOT NULL DEFAULT FALSE"),
]

try:
    for col_name, col_type in COLUMNS:
        # 컬럼 존재 여부 체크
        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'location_rooms' AND column_name = %s
        """, (col_name,))
        exists = cur.fetchone()

        if exists:
            print(f"  ✅ {col_name} - 이미 존재, 건너뜀")
        else:
            cur.execute(f'ALTER TABLE location_rooms ADD COLUMN {col_name} {col_type}')
            print(f"  ➕ {col_name} ({col_type}) - 추가 완료")

    # alembic_version 테이블에 이 마이그레이션 기록 (선택적)
    cur.execute("SELECT version_num FROM alembic_version")
    versions = [r[0] for r in cur.fetchall()]
    print(f"\n현재 alembic 버전들: {versions}")

    if 'add_room_loading_unloading_timeline' not in versions:
        # 기존 버전을 유지하면서 새 버전도 추가하면 multi-head가 되므로
        # 현재 20260228_155700이 최신이면 그걸 새 마이그레이션으로 교체
        if '20260228_155700' in versions:
            cur.execute(
                "UPDATE alembic_version SET version_num = %s WHERE version_num = %s",
                ('add_room_loading_unloading_timeline', '20260228_155700')
            )
            print("  alembic_version: 20260228_155700 → add_room_loading_unloading_timeline 업데이트")
        else:
            cur.execute(
                "INSERT INTO alembic_version (version_num) VALUES (%s)",
                ('add_room_loading_unloading_timeline',)
            )
            print("  alembic_version: add_room_loading_unloading_timeline 삽입")
    else:
        print("  alembic_version: 이미 기록됨")

    conn.commit()
    print("\n✅ 마이그레이션 완료!")

except Exception as e:
    conn.rollback()
    print(f"\n❌ 오류 발생: {e}")
    raise
finally:
    cur.close()
    conn.close()
