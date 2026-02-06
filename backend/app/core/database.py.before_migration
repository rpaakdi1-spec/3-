from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .config import settings

__all__ = ["engine", "SessionLocal", "get_db", "init_db", "Base"]

# Create database engine
# PostgreSQL specific settings
if "postgresql" in settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=20,  # Connection pool size
        max_overflow=10,  # Max overflow connections
        pool_pre_ping=True,  # Enable connection health checks
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=settings.APP_ENV == "development"
    )
else:
    # SQLite fallback
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.APP_ENV == "development"
    )

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
    
    Base.metadata.create_all(bind=engine)


# Import Base at the end to avoid circular imports
from app.models.base import Base  # noqa: E402
