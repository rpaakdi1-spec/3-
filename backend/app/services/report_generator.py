"""
Report Generation Service - PDF Reports
Generates comprehensive PDF reports for various business metrics
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from io import BytesIO
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.models.dispatch import Dispatch
from app.models.order import Order
from app.models.vehicle import Vehicle
from app.models.user import User
from app.models.client import Client


class PDFReportGenerator:
    """PDF Report Generator using ReportLab"""
    
    def __init__(self, db: Session):
        self.db = db
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Normal style
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
    
    def generate_dispatch_report(
        self,
        start_date: date,
        end_date: date
    ) -> BytesIO:
        """Generate dispatch report PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for PDF elements
        elements = []
        
        # Title
        title = Paragraph(
            f"Dispatch Report<br/>{start_date} to {end_date}",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Query dispatches
        dispatches = self.db.query(Dispatch).filter(
            and_(
                Dispatch.dispatch_date >= start_date,
                Dispatch.dispatch_date <= end_date
            )
        ).all()
        
        # Summary statistics
        total_dispatches = len(dispatches)
        completed = sum(1 for d in dispatches if d.status == 'completed')
        in_progress = sum(1 for d in dispatches if d.status == 'in_progress')
        pending = sum(1 for d in dispatches if d.status == 'pending')
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Dispatches', str(total_dispatches)],
            ['Completed', str(completed)],
            ['In Progress', str(in_progress)],
            ['Pending', str(pending)],
            ['Completion Rate', f"{(completed/total_dispatches*100):.1f}%" if total_dispatches > 0 else "0%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 30))
        
        # Dispatch details
        heading = Paragraph("Dispatch Details", self.styles['CustomHeading'])
        elements.append(heading)
        
        if dispatches:
            dispatch_data = [['Dispatch#', 'Date', 'Vehicle', 'Orders', 'Status']]
            
            for dispatch in dispatches[:50]:  # Limit to 50 for PDF size
                dispatch_data.append([
                    dispatch.dispatch_number,
                    str(dispatch.dispatch_date),
                    dispatch.vehicle.vehicle_number if dispatch.vehicle else 'N/A',
                    str(len(dispatch.orders)),
                    dispatch.status.upper()
                ])
            
            dispatch_table = Table(dispatch_data, colWidths=[1.2*inch, 1*inch, 1.2*inch, 0.8*inch, 1*inch])
            dispatch_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8)
            ]))
            
            elements.append(dispatch_table)
        else:
            no_data = Paragraph("No dispatch data for the selected period.", self.styles['CustomNormal'])
            elements.append(no_data)
        
        # Footer
        elements.append(Spacer(1, 30))
        footer_text = Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>Cold Chain Management System v2.0",
            self.styles['CustomNormal']
        )
        elements.append(footer_text)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_vehicle_performance_report(
        self,
        start_date: date,
        end_date: date,
        vehicle_id: Optional[int] = None
    ) -> BytesIO:
        """Generate vehicle performance report PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        elements = []
        
        # Title
        title_text = "Vehicle Performance Report"
        if vehicle_id:
            vehicle = self.db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
            if vehicle:
                title_text = f"Vehicle Performance Report<br/>{vehicle.vehicle_number}"
        
        title = Paragraph(f"{title_text}<br/>{start_date} to {end_date}", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Query vehicles
        vehicle_query = self.db.query(Vehicle)
        if vehicle_id:
            vehicle_query = vehicle_query.filter(Vehicle.id == vehicle_id)
        vehicles = vehicle_query.all()
        
        # Vehicle performance data
        performance_data = [['Vehicle', 'Type', 'Dispatches', 'Utilization', 'Avg Load']]
        
        for vehicle in vehicles:
            # Get dispatches for this vehicle
            dispatches = self.db.query(Dispatch).filter(
                and_(
                    Dispatch.vehicle_id == vehicle.id,
                    Dispatch.dispatch_date >= start_date,
                    Dispatch.dispatch_date <= end_date
                )
            ).all()
            
            total_dispatches = len(dispatches)
            
            # Calculate utilization (simplified)
            days_in_period = (end_date - start_date).days + 1
            utilization = (total_dispatches / days_in_period * 100) if days_in_period > 0 else 0
            
            # Calculate average load
            avg_pallets = sum(d.total_pallets for d in dispatches) / total_dispatches if total_dispatches > 0 else 0
            avg_load_pct = (avg_pallets / vehicle.pallet_capacity * 100) if vehicle.pallet_capacity > 0 else 0
            
            performance_data.append([
                vehicle.vehicle_number,
                vehicle.vehicle_type,
                str(total_dispatches),
                f"{utilization:.1f}%",
                f"{avg_load_pct:.1f}%"
            ])
        
        if len(performance_data) > 1:
            perf_table = Table(performance_data, colWidths=[1.5*inch, 1.2*inch, 1*inch, 1*inch, 1*inch])
            perf_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(perf_table)
        else:
            no_data = Paragraph("No vehicle data for the selected period.", self.styles['CustomNormal'])
            elements.append(no_data)
        
        # Footer
        elements.append(Spacer(1, 30))
        footer_text = Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>Cold Chain Management System v2.0",
            self.styles['CustomNormal']
        )
        elements.append(footer_text)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_driver_evaluation_report(
        self,
        start_date: date,
        end_date: date,
        driver_id: Optional[int] = None
    ) -> BytesIO:
        """Generate driver evaluation report PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        elements = []
        
        # Title
        title = Paragraph(
            f"Driver Evaluation Report<br/>{start_date} to {end_date}",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Query drivers
        driver_query = self.db.query(User).filter(User.role == 'driver')
        if driver_id:
            driver_query = driver_query.filter(User.id == driver_id)
        drivers = driver_query.all()
        
        # Driver evaluation data
        eval_data = [['Driver', 'Dispatches', 'Completed', 'Completion Rate', 'Avg Orders']]
        
        for driver in drivers:
            # Get dispatches for this driver
            dispatches = self.db.query(Dispatch).filter(
                and_(
                    Dispatch.driver_id == driver.id,
                    Dispatch.dispatch_date >= start_date,
                    Dispatch.dispatch_date <= end_date
                )
            ).all()
            
            total_dispatches = len(dispatches)
            completed = sum(1 for d in dispatches if d.status == 'completed')
            completion_rate = (completed / total_dispatches * 100) if total_dispatches > 0 else 0
            avg_orders = sum(len(d.orders) for d in dispatches) / total_dispatches if total_dispatches > 0 else 0
            
            eval_data.append([
                driver.full_name,
                str(total_dispatches),
                str(completed),
                f"{completion_rate:.1f}%",
                f"{avg_orders:.1f}"
            ])
        
        if len(eval_data) > 1:
            eval_table = Table(eval_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1.2*inch, 1*inch])
            eval_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(eval_table)
        else:
            no_data = Paragraph("No driver data for the selected period.", self.styles['CustomNormal'])
            elements.append(no_data)
        
        # Footer
        elements.append(Spacer(1, 30))
        footer_text = Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>Cold Chain Management System v2.0",
            self.styles['CustomNormal']
        )
        elements.append(footer_text)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer


def get_report_generator(db: Session) -> PDFReportGenerator:
    """Factory function to get report generator instance"""
    return PDFReportGenerator(db)
