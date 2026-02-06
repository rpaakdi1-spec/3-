"""API Dependencies"""
from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(db: Session = Depends(get_db)):
    return {"id": 1, "username": "admin"}
