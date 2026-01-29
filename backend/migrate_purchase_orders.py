#!/usr/bin/env python3
"""
발주서 테이블 마이그레이션 스크립트
image_url (단일) -> image_urls (JSON 배열)로 변경
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "dispatch.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. 현재 테이블 스키마 확인
        cursor.execute("PRAGMA table_info(purchase_orders)")
        columns = {row[1]: row for row in cursor.fetchall()}
        
        print("현재 테이블 컬럼:")
        for col_name in columns.keys():
            print(f"  - {col_name}")
        
        # 2. image_urls 컬럼이 있는지 확인
        if 'image_urls' in columns:
            print("\n✅ image_urls 컬럼이 이미 존재합니다.")
            return
        
        # 3. image_url 컬럼이 있는지 확인
        if 'image_url' not in columns:
            print("\n⚠️ image_url 컬럼이 없습니다. 새로운 테이블 생성이 필요합니다.")
            # 새 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchase_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(200) NOT NULL,
                    content TEXT,
                    image_urls TEXT,
                    author VARCHAR(100) NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            conn.commit()
            print("✅ 새로운 purchase_orders 테이블이 생성되었습니다.")
            return
        
        # 4. 기존 데이터 백업
        cursor.execute("SELECT COUNT(*) FROM purchase_orders")
        count = cursor.fetchone()[0]
        print(f"\n현재 데이터 개수: {count}개")
        
        if count > 0:
            print("기존 데이터를 백업합니다...")
            cursor.execute("SELECT * FROM purchase_orders")
            backup_data = cursor.fetchall()
        
        # 5. 임시 테이블 생성 (새 스키마)
        print("\n임시 테이블 생성 중...")
        cursor.execute("""
            CREATE TABLE purchase_orders_new (
                id INTEGER PRIMARY KEY,
                po_number VARCHAR(50),
                title VARCHAR(200) NOT NULL,
                supplier VARCHAR(200),
                order_date DATE,
                delivery_date DATE,
                total_amount FLOAT DEFAULT 0.0,
                status VARCHAR(50) DEFAULT '작성중',
                content TEXT,
                image_urls TEXT,
                author VARCHAR(100) NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        # 6. 데이터 마이그레이션 (image_url -> image_urls, JSON 배열로 변환)
        if count > 0:
            print("데이터 마이그레이션 중...")
            cursor.execute("PRAGMA table_info(purchase_orders)")
            old_columns_info = cursor.fetchall()
            old_column_names = [col[1] for col in old_columns_info]
            
            cursor.execute("SELECT * FROM purchase_orders")
            for row in cursor.fetchall():
                row_dict = dict(zip(old_column_names, row))
                
                # image_url을 image_urls로 변환 (JSON 배열)
                image_url = row_dict.get('image_url')
                if image_url:
                    image_urls = json.dumps([image_url])
                else:
                    image_urls = None
                
                # 새 테이블에 삽입
                cursor.execute("""
                    INSERT INTO purchase_orders_new 
                    (id, po_number, title, supplier, order_date, delivery_date, 
                     total_amount, status, content, image_urls, author, is_active, 
                     created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row_dict.get('id'),
                    row_dict.get('po_number'),
                    row_dict.get('title'),
                    row_dict.get('supplier'),
                    row_dict.get('order_date'),
                    row_dict.get('delivery_date'),
                    row_dict.get('total_amount', 0.0),
                    row_dict.get('status', '작성중'),
                    row_dict.get('content'),
                    image_urls,
                    row_dict.get('author'),
                    row_dict.get('is_active', 1),
                    row_dict.get('created_at'),
                    row_dict.get('updated_at')
                ))
            print(f"✅ {count}개의 데이터가 마이그레이션되었습니다.")
        
        # 7. 기존 테이블 삭제 및 새 테이블 이름 변경
        print("\n테이블 교체 중...")
        cursor.execute("DROP TABLE purchase_orders")
        cursor.execute("ALTER TABLE purchase_orders_new RENAME TO purchase_orders")
        
        conn.commit()
        print("\n✅ 마이그레이션이 성공적으로 완료되었습니다!")
        
        # 8. 결과 확인
        cursor.execute("PRAGMA table_info(purchase_orders)")
        new_columns = cursor.fetchall()
        print("\n새로운 테이블 스키마:")
        for col in new_columns:
            print(f"  - {col[1]} ({col[2]})")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 마이그레이션 실패: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("발주서 테이블 마이그레이션")
    print("image_url (단일) -> image_urls (JSON 배열)")
    print("=" * 60)
    migrate()
