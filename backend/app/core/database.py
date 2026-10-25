from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .config import settings

__all__ = ["engine", "SessionLocal", "get_db", "init_db", "Base"]

# Create database engine
if "postgresql" in settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=settings.APP_ENV == "development"
    )
else:
    # SQLite 성능 최적화
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 30,
        },
        # SQLite는 pool_size 불필요하지만 연결 재사용
        pool_pre_ping=True,
        echo=settings.APP_ENV == "development"
    )

    # SQLite PRAGMA 최적화 (연결 생성 시 자동 적용)
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        # WAL 모드: 읽기/쓰기 동시성 향상 (가장 중요)
        cursor.execute("PRAGMA journal_mode=WAL")
        # 캐시 크기: 64MB (기본 2MB → 32배)
        cursor.execute("PRAGMA cache_size=-65536")
        # 동기 모드 완화: NORMAL (기본 FULL보다 3~5배 빠름)
        cursor.execute("PRAGMA synchronous=NORMAL")
        # 임시 테이블 메모리에 유지
        cursor.execute("PRAGMA temp_store=MEMORY")
        # mmap 크기: 256MB (대용량 읽기 가속)
        cursor.execute("PRAGMA mmap_size=268435456")
        cursor.close()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    from app.models.base import Base
    import app.models  # Import all models
    
    Base.metadata.create_all(bind=engine)  # Disabled: Use Alembic migrations instead


# Import Base at the end to avoid circular imports
from app.models.base import Base  # noqa: E402
