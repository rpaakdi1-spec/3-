"""
Excel Report Generator Service
Generates comprehensive Excel reports with multiple sheets, charts, and formatting
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from io import BytesIO
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.utils import get_column_letter

from app.models.dispatch import Dispatch
from app.models.order import Order
from app.models.vehicle import Vehicle
from app.models.user import User
from app.models.client import Client


class ExcelReportGenerator:
    """Excel Report Generator using OpenPyXL"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Define reusable styles
        self.header_font = Font(name='Arial', size=12, bold=True, color="FFFFFF")
        self.header_fill = PatternFill(start_color="1E40AF", end_color="1E40AF", fill_type="solid")
        self.header_alignment = Alignment(horizontal='center', vertical='center')
        
        self.data_font = Font(name='Arial', size=10)
        self.data_alignment = Alignment(horizontal='center', vertical='center')
        
        self.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
    
    def _apply_header_style(self, ws, row_num: int, col_start: int, col_end: int):
        """Apply header style to a row"""
        for col in range(col_start, col_end + 1):
            cell = ws.cell(row=row_num, column=col)
            cell.font = self.header_font
            cell.fill = self.header_fill
            cell.alignment = self.header_alignment
            cell.border = self.border
    
    def _apply_data_style(self, ws, row_start: int, row_end: int, col_start: int, col_end: int):
        """Apply data style to a range"""
        for row in range(row_start, row_end + 1):
            for col in range(col_start, col_end + 1):
                cell = ws.cell(row=row, column=col)
                cell.font = self.data_font
                cell.alignment = self.data_alignment
                cell.border = self.border
    
    def _auto_adjust_column_width(self, ws):
        """Auto-adjust column widths"""
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
    
    def generate_dispatch_report(
        self,
        start_date: date,
        end_date: date
    ) -> BytesIO:
        """Generate comprehensive dispatch report with multiple sheets"""
        wb = Workbook()
        
        # Remove default sheet
        wb.remove(wb.active)
        
        # Sheet 1: Summary
        ws_summary = wb.create_sheet("Summary")
        ws_summary.append(['Dispatch Report'])
        ws_summary.append([f'Period: {start_date} to {end_date}'])
        ws_summary.append([])
        
        # Query dispatches
        dispatches = self.db.query(Dispatch).filter(
            and_(
                Dispatch.dispatch_date >= start_date,
                Dispatch.dispatch_date <= end_date
            )
        ).all()
        
        total_dispatches = len(dispatches)
        completed = sum(1 for d in dispatches if d.status == 'completed')
        in_progress = sum(1 for d in dispatches if d.status == 'in_progress')
        pending = sum(1 for d in dispatches if d.status == 'pending')
        
        # Summary data
        ws_summary.append(['Metric', 'Value'])
        ws_summary.append(['Total Dispatches', total_dispatches])
        ws_summary.append(['Completed', completed])
        ws_summary.append(['In Progress', in_progress])
        ws_summary.append(['Pending', pending])
        ws_summary.append(['Completion Rate', f"{(completed/total_dispatches*100):.1f}%" if total_dispatches > 0 else "0%"])
        
        # Apply styles
        ws_summary.merge_cells('A1:B1')
        ws_summary['A1'].font = Font(size=16, bold=True)
        ws_summary['A1'].alignment = Alignment(horizontal='center')
        
        self._apply_header_style(ws_summary, 4, 1, 2)
        self._apply_data_style(ws_summary, 5, 9, 1, 2)
        self._auto_adjust_column_width(ws_summary)
        
        # Sheet 2: Dispatch Details
        ws_details = wb.create_sheet("Dispatch Details")
        ws_details.append(['Dispatch Number', 'Date', 'Vehicle', 'Driver', 'Orders', 'Pallets', 'Weight (kg)', 'Status'])
        
        for dispatch in dispatches:
            ws_details.append([
                dispatch.dispatch_number,
                str(dispatch.dispatch_date),
                dispatch.vehicle.vehicle_number if dispatch.vehicle else 'N/A',
                dispatch.driver.full_name if dispatch.driver else 'N/A',
                len(dispatch.orders),
                dispatch.total_pallets,
                dispatch.total_weight_kg,
                dispatch.status.upper()
            ])
        
        self._apply_header_style(ws_details, 1, 1, 8)
        if len(dispatches) > 0:
            self._apply_data_style(ws_details, 2, len(dispatches) + 1, 1, 8)
        self._auto_adjust_column_width(ws_details)
        
        # Sheet 3: Charts
        ws_charts = wb.create_sheet("Charts")
        
        # Add status breakdown data for chart
        ws_charts.append(['Status', 'Count'])
        ws_charts.append(['Completed', completed])
        ws_charts.append(['In Progress', in_progress])
        ws_charts.append(['Pending', pending])
        
        # Create pie chart
        pie = PieChart()
        labels = Reference(ws_charts, min_col=1, min_row=2, max_row=4)
        data = Reference(ws_charts, min_col=2, min_row=1, max_row=4)
        pie.add_data(data, titles_from_data=True)
        pie.set_categories(labels)
        pie.title = "Dispatch Status Distribution"
        ws_charts.add_chart(pie, "D2")
        
        # Save to buffer
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
    
    def generate_vehicle_performance_report(
        self,
        start_date: date,
        end_date: date,
        vehicle_id: Optional[int] = None
    ) -> BytesIO:
        """Generate vehicle performance report"""
        wb = Workbook()
        wb.remove(wb.active)
        
        # Sheet 1: Summary
        ws = wb.create_sheet("Vehicle Performance")
        
        # Title
        ws.append(['Vehicle Performance Report'])
        ws.append([f'Period: {start_date} to {end_date}'])
        ws.append([])
        
        # Headers
        ws.append(['Vehicle Number', 'Type', 'Total Dispatches', 'Utilization %', 'Avg Load %', 'Total Distance (km)'])
        
        # Query vehicles
        vehicle_query = self.db.query(Vehicle)
        if vehicle_id:
            vehicle_query = vehicle_query.filter(Vehicle.id == vehicle_id)
        vehicles = vehicle_query.all()
        
        row_num = 5
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
            
            # Calculate metrics
            days_in_period = (end_date - start_date).days + 1
            utilization = (total_dispatches / days_in_period * 100) if days_in_period > 0 else 0
            
            avg_pallets = sum(d.total_pallets for d in dispatches) / total_dispatches if total_dispatches > 0 else 0
            avg_load_pct = (avg_pallets / vehicle.pallet_capacity * 100) if vehicle.pallet_capacity > 0 else 0
            
            total_distance = sum(d.total_distance_km for d in dispatches if d.total_distance_km)
            
            ws.append([
                vehicle.vehicle_number,
                vehicle.vehicle_type,
                total_dispatches,
                f"{utilization:.1f}%",
                f"{avg_load_pct:.1f}%",
                f"{total_distance:.1f}" if total_distance else "0.0"
            ])
            row_num += 1
        
        # Apply styles
        ws.merge_cells('A1:F1')
        ws['A1'].font = Font(size=16, bold=True)
        ws['A1'].alignment = Alignment(horizontal='center')
        
        self._apply_header_style(ws, 4, 1, 6)
        if len(vehicles) > 0:
            self._apply_data_style(ws, 5, row_num - 1, 1, 6)
        self._auto_adjust_column_width(ws)
        
        # Save to buffer
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
    
    def generate_driver_evaluation_report(
        self,
        start_date: date,
        end_date: date,
        driver_id: Optional[int] = None
    ) -> BytesIO:
        """Generate driver evaluation report"""
        wb = Workbook()
        wb.remove(wb.active)
        
        # Sheet 1: Summary
        ws = wb.create_sheet("Driver Evaluation")
        
        # Title
        ws.append(['Driver Evaluation Report'])
        ws.append([f'Period: {start_date} to {end_date}'])
        ws.append([])
        
        # Headers
        ws.append(['Driver Name', 'Total Dispatches', 'Completed', 'Completion Rate', 'Avg Orders per Dispatch'])
        
        # Query drivers
        driver_query = self.db.query(User).filter(User.role == 'driver')
        if driver_id:
            driver_query = driver_query.filter(User.id == driver_id)
        drivers = driver_query.all()
        
        row_num = 5
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
            
            ws.append([
                driver.full_name,
                total_dispatches,
                completed,
                f"{completion_rate:.1f}%",
                f"{avg_orders:.1f}"
            ])
            row_num += 1
        
        # Apply styles
        ws.merge_cells('A1:E1')
        ws['A1'].font = Font(size=16, bold=True)
        ws['A1'].alignment = Alignment(horizontal='center')
        
        self._apply_header_style(ws, 4, 1, 5)
        if len(drivers) > 0:
            self._apply_data_style(ws, 5, row_num - 1, 1, 5)
        self._auto_adjust_column_width(ws)
        
        # Save to buffer
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
    
    def generate_customer_satisfaction_report(
        self,
        start_date: date,
        end_date: date
    ) -> BytesIO:
        """Generate customer satisfaction report"""
        wb = Workbook()
        wb.remove(wb.active)
        
        ws = wb.create_sheet("Customer Satisfaction")
        
        # Title
        ws.append(['Customer Satisfaction Report'])
        ws.append([f'Period: {start_date} to {end_date}'])
        ws.append([])
        
        # Headers
        ws.append(['Client Name', 'Total Orders', 'Completed', 'On-Time Deliveries', 'Satisfaction Score'])
        
        # Query clients with orders
        clients = self.db.query(Client).all()
        
        row_num = 5
        for client in clients:
            # Get orders for this client
            orders = self.db.query(Order).filter(
                and_(
                    Order.pickup_client_id == client.id,
                    Order.created_at >= start_date,
                    Order.created_at <= end_date
                )
            ).all()
            
            if not orders:
                continue
            
            total_orders = len(orders)
            completed = sum(1 for o in orders if o.status == 'completed')
            
            # Calculate on-time deliveries (simplified)
            on_time = sum(1 for o in orders if o.status == 'completed')
            
            # Calculate satisfaction score (simplified)
            satisfaction = (on_time / total_orders * 100) if total_orders > 0 else 0
            
            ws.append([
                client.name,
                total_orders,
                completed,
                on_time,
                f"{satisfaction:.1f}%"
            ])
            row_num += 1
        
        # Apply styles
        ws.merge_cells('A1:E1')
        ws['A1'].font = Font(size=16, bold=True)
        ws['A1'].alignment = Alignment(horizontal='center')
        
        self._apply_header_style(ws, 4, 1, 5)
        if row_num > 5:
            self._apply_data_style(ws, 5, row_num - 1, 1, 5)
        self._auto_adjust_column_width(ws)
        
        # Save to buffer
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer


def get_excel_generator(db: Session) -> ExcelReportGenerator:
    """Factory function to get Excel report generator instance"""
    return ExcelReportGenerator(db)
