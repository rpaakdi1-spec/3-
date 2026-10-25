"""
배차 서류 및 추적 테이블 생성 마이그레이션

테이블:
- dispatch_documents: 배차 서류 (거래명세표, 온도기록지)
- dispatch_tracking: 배차 추적 정보 (고객 공개용)
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import engine
from app.models.base import Base
from app.models.dispatch_document import DispatchDocument, DispatchTracking
from loguru import logger


def create_dispatch_document_tables():
    """배차 서류 및 추적 테이블 생성"""
    try:
        logger.info("Creating dispatch document and tracking tables...")
        
        # Create tables
        DispatchDocument.__table__.create(engine, checkfirst=True)
        logger.info("✅ Created dispatch_documents table")
        
        DispatchTracking.__table__.create(engine, checkfirst=True)
        logger.info("✅ Created dispatch_tracking table")
        
        logger.info("✅ All dispatch document tables created successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        raise


if __name__ == "__main__":
    create_dispatch_document_tables()
