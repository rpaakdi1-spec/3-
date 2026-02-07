"""
Reports API Endpoints
Provides endpoints for generating and downloading PDF and Excel reports
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.report_generator import get_report_generator
from app.services.excel_generator import get_excel_generator

# Phase 9: Billing Enhanced Reports
from app.services.billing_enhanced import BillingEnhancedService
from app.services.pdf_generator import pdf_generator
from app.services.excel_generator import excel_generator as billing_excel_generator
from io import BytesIO


router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/dispatch/pdf", summary="Generate Dispatch Report PDF")
async def generate_dispatch_pdf(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a comprehensive dispatch report in PDF format.
    
    **Parameters**:
    - `start_date`: Report start date
    - `end_date`: Report end date
    
    **Returns**: PDF file download
    
    **Permissions**: Dispatcher or Admin
    """
    try:
        generator = get_report_generator(db)
        pdf_buffer = generator.generate_dispatch_report(start_date, end_date)
        
        filename = f"dispatch_report_{start_date}_{end_date}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")


@router.post("/dispatch/excel", summary="Generate Dispatch Report Excel")
async def generate_dispatch_excel(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a comprehensive dispatch report in Excel format.
    
    **Parameters**:
    - `start_date`: Report start date
    - `end_date`: Report end date
    
    **Returns**: Excel file download
    
    **Permissions**: Dispatcher or Admin
    """
    try:
        generator = get_excel_generator(db)
        excel_buffer = generator.generate_dispatch_report(start_date, end_date)
        
        filename = f"dispatch_report_{start_date}_{end_date}.xlsx"
        
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Excel report: {str(e)}")


@router.post("/vehicles/pdf", summary="Generate Vehicle Performance Report PDF")
async def generate_vehicle_pdf(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    vehicle_id: Optional[int] = Query(None, description="Specific vehicle ID (optional)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate vehicle performance report in PDF format.
    
    **Parameters**:
    - `start_date`: Report start date
    - `end_date`: Report end date
    - `vehicle_id`: Optional - specific vehicle ID (omit for all vehicles)
    
    **Returns**: PDF file download
    
    **Permissions**: Dispatcher or Admin
    """
    try:
        generator = get_report_generator(db)
        pdf_buffer = generator.generate_vehicle_performance_report(start_date, end_date, vehicle_id)
        
        filename = f"vehicle_performance_{start_date}_{end_date}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")


@router.post("/vehicles/excel", summary="Generate Vehicle Performance Report Excel")
async def generate_vehicle_excel(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    vehicle_id: Optional[int] = Query(None, description="Specific vehicle ID (optional)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate vehicle performance report in Excel format.
    
    **Parameters**:
    - `start_date`: Report start date
    - `end_date`: Report end date
    - `vehicle_id`: Optional - specific vehicle ID (omit for all vehicles)
    
    **Returns**: Excel file download
    
    **Permissions**: Dispatcher or Admin
    """
    try:
        generator = get_excel_generator(db)
        excel_buffer = generator.generate_vehicle_performance_report(start_date, end_date, vehicle_id)
        
        filename = f"vehicle_performance_{start_date}_{end_date}.xlsx"
        
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Excel report: {str(e)}")


@router.post("/drivers/pdf", summary="Generate Driver Evaluation Report PDF")
async def generate_driver_pdf(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    driver_id: Optional[int] = Query(None, description="Specific driver ID (optional)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate driver evaluation report in PDF format.
    
    **Parameters**:
    - `start_date`: Report start date
    - `end_date`: Report end date
    - `driver_id`: Optional - specific driver ID (omit for all drivers)
    
    **Returns**: PDF file download
    
    **Permissions**: Admin only
    """
    try:
        generator = get_report_generator(db)
        pdf_buffer = generator.generate_driver_evaluation_report(start_date, end_date, driver_id)
        
        filename = f"driver_evaluation_{start_date}_{end_date}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")


@router.post("/drivers/excel", summary="Generate Driver Evaluation Report Excel")
async def generate_driver_excel(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    driver_id: Optional[int] = Query(None, description="Specific driver ID (optional)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate driver evaluation report in Excel format.
    
    **Parameters**:
    - `start_date`: Report start date
    - `end_date`: Report end date
    - `driver_id`: Optional - specific driver ID (omit for all drivers)
    
    **Returns**: Excel file download
    
    **Permissions**: Admin only
    """
    try:
        generator = get_excel_generator(db)
        excel_buffer = generator.generate_driver_evaluation_report(start_date, end_date, driver_id)
        
        filename = f"driver_evaluation_{start_date}_{end_date}.xlsx"
        
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Excel report: {str(e)}")


@router.post("/customers/excel", summary="Generate Customer Satisfaction Report Excel")
async def generate_customer_excel(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate customer satisfaction report in Excel format.
    
    **Parameters**:
    - `start_date`: Report start date
    - `end_date`: Report end date
    
    **Returns**: Excel file download
    
    **Permissions**: Admin or Dispatcher
    """
    try:
        generator = get_excel_generator(db)
        excel_buffer = generator.generate_customer_satisfaction_report(start_date, end_date)
        
        filename = f"customer_satisfaction_{start_date}_{end_date}.xlsx"
        
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Excel report: {str(e)}")


# ============================================================================
# Phase 9: Billing Enhanced Financial Reports
# ============================================================================

@router.post("/financial-dashboard/pdf", summary="Generate Financial Dashboard Report PDF")
async def generate_financial_dashboard_pdf(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a comprehensive financial dashboard report in PDF format.
    
    **Parameters**:
    - `start_date`: Report start date
    - `end_date`: Report end date
    
    **Returns**: PDF file download with:
    - 14 key financial metrics
    - Monthly trends chart
    - Top 10 clients
    
    **Permissions**: Admin only
    """
    try:
        # Fetch billing data
        billing_service = BillingEnhancedService(db)
        
        # 1. Financial summary
        summary = billing_service.get_financial_dashboard(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # 2. Monthly trends (last 12 months)
        monthly_trends = billing_service.get_monthly_trends(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            months=12
        )
        
        # 3. Top 10 clients
        top_clients = billing_service.get_top_clients(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            limit=10
        )
        
        # Generate PDF
        pdf_bytes = pdf_generator.generate_financial_dashboard_pdf(
            summary=summary,
            monthly_trends=monthly_trends,
            top_clients=top_clients,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        filename = f"financial_dashboard_{start_date}_{end_date}.pdf"
        
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")


@router.post("/financial-dashboard/excel", summary="Generate Financial Dashboard Report Excel")
async def generate_financial_dashboard_excel(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a comprehensive financial dashboard report in Excel format.
    
    **Parameters**:
    - `start_date`: Report start date
    - `end_date`: Report end date
    
    **Returns**: Excel file download with multiple sheets:
    - Summary sheet: 14 key financial metrics
    - Monthly data sheet: Detailed trends
    - Top clients sheet: Revenue by client
    - Charts sheet: Visual representations
    
    **Permissions**: Admin only
    """
    try:
        # Fetch billing data
        billing_service = BillingEnhancedService(db)
        
        # 1. Financial summary
        summary = billing_service.get_financial_dashboard(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # 2. Monthly trends (last 12 months)
        monthly_trends = billing_service.get_monthly_trends(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            months=12
        )
        
        # 3. Top 10 clients
        top_clients = billing_service.get_top_clients(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            limit=10
        )
        
        # Generate Excel
        excel_bytes = billing_excel_generator.generate_financial_dashboard_excel(
            summary=summary,
            monthly_trends=monthly_trends,
            top_clients=top_clients,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        filename = f"financial_dashboard_{start_date}_{end_date}.xlsx"
        
        return StreamingResponse(
            BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Excel report: {str(e)}")
