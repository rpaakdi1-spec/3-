"""
리포트 API 엔드포인트
PDF 및 Excel 리포트 생성 및 다운로드
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date, datetime
from io import BytesIO
from typing import Literal

from app.db.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.services.billing_enhanced import BillingEnhancedService
from app.services.pdf_generator import pdf_generator
from app.services.excel_generator import excel_generator

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/financial-dashboard/pdf")
async def generate_financial_dashboard_pdf(
    start_date: date = Query(..., description="시작일 (YYYY-MM-DD)"),
    end_date: date = Query(..., description="종료일 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    재무 대시보드 PDF 리포트 생성
    
    - **start_date**: 시작일
    - **end_date**: 종료일
    - **Returns**: PDF 파일 다운로드
    """
    try:
        # 재무 데이터 조회
        service = BillingEnhancedService(db)
        
        # 1. 재무 요약
        summary = service.get_financial_dashboard(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # 2. 월별 추이 (최근 12개월)
        monthly_trends = service.get_monthly_trends(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            months=12
        )
        
        # 3. Top 10 고객
        top_clients = service.get_top_clients(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            limit=10
        )
        
        # PDF 생성
        pdf_bytes = pdf_generator.generate_financial_dashboard_pdf(
            summary=summary,
            monthly_trends=monthly_trends,
            top_clients=top_clients,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # 파일명 생성
        filename = f"financial_dashboard_{start_date}_{end_date}.pdf"
        
        # StreamingResponse로 반환
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 생성 실패: {str(e)}")


@router.post("/financial-dashboard/excel")
async def generate_financial_dashboard_excel(
    start_date: date = Query(..., description="시작일 (YYYY-MM-DD)"),
    end_date: date = Query(..., description="종료일 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    재무 대시보드 Excel 리포트 생성
    
    - **start_date**: 시작일
    - **end_date**: 종료일
    - **Returns**: Excel 파일 다운로드
    """
    try:
        # 재무 데이터 조회
        service = BillingEnhancedService(db)
        
        # 1. 재무 요약
        summary = service.get_financial_dashboard(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # 2. 월별 추이 (최근 12개월)
        monthly_trends = service.get_monthly_trends(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            months=12
        )
        
        # 3. Top 10 고객
        top_clients = service.get_top_clients(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            limit=10
        )
        
        # Excel 생성
        excel_bytes = excel_generator.generate_financial_dashboard_excel(
            summary=summary,
            monthly_trends=monthly_trends,
            top_clients=top_clients,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # 파일명 생성
        filename = f"financial_dashboard_{start_date}_{end_date}.xlsx"
        
        # StreamingResponse로 반환
        return StreamingResponse(
            BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel 생성 실패: {str(e)}")
