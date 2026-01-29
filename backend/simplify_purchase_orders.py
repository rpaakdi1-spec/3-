#!/usr/bin/env python3
"""
발주서 테이블 간소화 마이그레이션
불필요한 컬럼 제거: po_number, supplier, order_date, delivery_date, total_amount, status
유지: id, title, content, image_urls, author, is_active, created_at, updated_at
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "dispatch.db"

def simplify_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. 현재 테이블 스키마 확인
        cursor.execute("PRAGMA table_info(purchase_orders)")
        columns = {row[1]: row for row in cursor.fetchall()}
        
        print("현재 테이블 컬럼:")
        for col_name in columns.keys():
            print(f"  - {col_name}")
        
        # 2. 데이터 개수 확인
        cursor.execute("SELECT COUNT(*) FROM purchase_orders")
        count = cursor.fetchone()[0]
        print(f"\n현재 데이터 개수: {count}개")
        
        # 3. 간소화된 테이블 생성
        print("\n간소화된 테이블 생성 중...")
        cursor.execute("""
            CREATE TABLE purchase_orders_simple (
                id INTEGER PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                content TEXT,
                image_urls TEXT,
                author VARCHAR(100) NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        # 4. 필요한 데이터만 복사
        if count > 0:
            print("필수 데이터만 복사 중...")
            cursor.execute("""
                INSERT INTO purchase_orders_simple 
                (id, title, content, image_urls, author, is_active, created_at, updated_at)
                SELECT id, title, content, image_urls, author, is_active, created_at, updated_at
                FROM purchase_orders
            """)
            print(f"✅ {count}개의 데이터가 복사되었습니다.")
        
        # 5. 기존 테이블 삭제 및 새 테이블 이름 변경
        print("\n테이블 교체 중...")
        cursor.execute("DROP TABLE purchase_orders")
        cursor.execute("ALTER TABLE purchase_orders_simple RENAME TO purchase_orders")
        
        conn.commit()
        print("\n✅ 테이블 간소화가 성공적으로 완료되었습니다!")
        
        # 6. 결과 확인
        cursor.execute("PRAGMA table_info(purchase_orders)")
        new_columns = cursor.fetchall()
        print("\n최종 테이블 스키마:")
        for col in new_columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # 7. 데이터 샘플 확인
        cursor.execute("SELECT id, title, author, created_at FROM purchase_orders LIMIT 3")
        samples = cursor.fetchall()
        if samples:
            print("\n데이터 샘플:")
            for row in samples:
                print(f"  ID: {row[0]}, 제목: {row[1]}, 작성자: {row[2]}, 작성일: {row[3]}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 간소화 실패: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("발주서 테이블 간소화")
    print("불필요한 컬럼 제거")
    print("=" * 60)
    simplify_table()
