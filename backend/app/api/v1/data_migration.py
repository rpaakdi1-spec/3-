"""
데이터 마이그레이션 API 엔드포인트
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import os
import tempfile
from datetime import datetime

from app.database import get_db
from app.services.data_migration_engine import DataMigrationEngine, create_excel_template
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/data-migration", tags=["Data Migration"])


@router.post("/upload/excel")
async def upload_excel_migration(
    file: UploadFile = File(...),
    entity_type: str = "clients",
    dry_run: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Excel 파일로 데이터 마이그레이션
    
    Parameters:
    - file: Excel 파일 (.xlsx, .xls)
    - entity_type: 엔티티 타입 (clients, vehicles, orders, drivers)
    - dry_run: True면 실제 저장 없이 검증만 수행
    """
    # 파일 확장자 확인
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files are supported (.xlsx, .xls)")
    
    # 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # 마이그레이션 실행
        engine = DataMigrationEngine(db)
        result = engine.migrate_from_excel(
            file_path=tmp_path,
            entity_type=entity_type,
            dry_run=dry_run
        )
        
        # 결과 검증
        validation = engine.validate_migration()
        
        return {
            "message": "Migration completed" if not dry_run else "Dry run completed",
            "dry_run": dry_run,
            "entity_type": entity_type,
            "result": {
                "total_records": result.total_records,
                "success_count": result.success_count,
                "failed_count": result.failed_count,
                "skipped_count": result.skipped_count,
                "errors": result.errors[:10],  # 최대 10개 에러만 반환
                "warnings": result.warnings[:10]
            },
            "validation": validation
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # 임시 파일 삭제
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.post("/upload/csv")
async def upload_csv_migration(
    file: UploadFile = File(...),
    entity_type: str = "clients",
    encoding: str = "utf-8",
    dry_run: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    CSV 파일로 데이터 마이그레이션
    
    Parameters:
    - file: CSV 파일
    - entity_type: 엔티티 타입 (clients, vehicles, orders, drivers)
    - encoding: 파일 인코딩 (utf-8, euc-kr, cp949)
    - dry_run: True면 실제 저장 없이 검증만 수행
    """
    # 파일 확장자 확인
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # 마이그레이션 실행
        engine = DataMigrationEngine(db)
        result = engine.migrate_from_csv(
            file_path=tmp_path,
            entity_type=entity_type,
            encoding=encoding,
            dry_run=dry_run
        )
        
        # 결과 검증
        validation = engine.validate_migration()
        
        return {
            "message": "Migration completed" if not dry_run else "Dry run completed",
            "dry_run": dry_run,
            "entity_type": entity_type,
            "result": {
                "total_records": result.total_records,
                "success_count": result.success_count,
                "failed_count": result.failed_count,
                "skipped_count": result.skipped_count,
                "errors": result.errors[:10],
                "warnings": result.warnings[:10]
            },
            "validation": validation
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # 임시 파일 삭제
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.get("/template/{entity_type}")
async def download_template(
    entity_type: str,
    current_user: User = Depends(get_current_user)
):
    """
    마이그레이션용 Excel 템플릿 다운로드
    
    Parameters:
    - entity_type: 엔티티 타입 (clients, vehicles, orders, drivers)
    """
    from fastapi.responses import FileResponse
    
    # 지원되는 엔티티 타입 확인
    supported_types = ["clients", "vehicles", "orders", "drivers"]
    if entity_type not in supported_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported entity type. Must be one of: {', '.join(supported_types)}"
        )
    
    # 템플릿 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"migration_template_{entity_type}_{timestamp}.xlsx"
    output_path = f"/tmp/{filename}"
    
    try:
        create_excel_template(entity_type, output_path)
        
        return FileResponse(
            path=output_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_migration_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """현재 데이터베이스 통계 조회"""
    from app.models.client import Client
    from app.models.vehicle import Vehicle
    from app.models.order import Order
    from app.models.dispatch import Dispatch
    from app.models.driver import Driver
    
    stats = {
        "clients": db.query(Client).count(),
        "vehicles": db.query(Vehicle).count(),
        "orders": db.query(Order).count(),
        "dispatches": db.query(Dispatch).count(),
        "drivers": db.query(Driver).count()
    }
    
    return {
        "message": "Database statistics",
        "stats": stats,
        "total_records": sum(stats.values())
    }
