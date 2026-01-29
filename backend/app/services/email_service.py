"""
Email Service
Handles sending emails with templates for various notifications
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, date
from jinja2 import Environment, FileSystemLoader, select_autoescape
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from sqlalchemy.orm import Session

from app.core.email_config import email_settings
from app.models.user import User
from app.models.dispatch import Dispatch
from app.models.vehicle import Vehicle
from app.models.order import Order


class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self):
        # FastAPI-Mail configuration
        self.config = ConnectionConfig(
            MAIL_USERNAME=email_settings.MAIL_USERNAME,
            MAIL_PASSWORD=email_settings.MAIL_PASSWORD,
            MAIL_FROM=email_settings.MAIL_FROM,
            MAIL_PORT=email_settings.MAIL_PORT,
            MAIL_SERVER=email_settings.MAIL_SERVER,
            MAIL_STARTTLS=email_settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=email_settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=email_settings.USE_CREDENTIALS,
            VALIDATE_CERTS=email_settings.VALIDATE_CERTS,
            TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates" / "email"
        )
        
        self.fast_mail = FastMail(self.config)
        
        # Jinja2 environment for templates
        template_path = Path(__file__).parent.parent / "templates" / "email"
        template_path.mkdir(parents=True, exist_ok=True)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_path)),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    async def send_email(
        self,
        recipients: List[str],
        subject: str,
        template_name: str,
        context: Dict[str, Any]
    ):
        """
        Send email using template
        
        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            template_name: Name of Jinja2 template (e.g., 'dispatch_created.html')
            context: Template context variables
        """
        try:
            # Render template
            template = self.jinja_env.get_template(template_name)
            html_body = template.render(**context)
            
            # Create message
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=html_body,
                subtype=MessageType.html
            )
            
            # Send email
            await self.fast_mail.send_message(message)
            
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    async def send_dispatch_created(
        self,
        dispatch: Dispatch,
        recipients: List[str]
    ):
        """Send notification when dispatch is created"""
        context = {
            'dispatch_number': dispatch.dispatch_number,
            'dispatch_date': str(dispatch.dispatch_date),
            'vehicle': dispatch.vehicle.vehicle_number if dispatch.vehicle else 'N/A',
            'driver': dispatch.driver.full_name if dispatch.driver else 'N/A',
            'total_orders': len(dispatch.orders),
            'total_pallets': dispatch.total_pallets,
            'total_weight': dispatch.total_weight_kg,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return await self.send_email(
            recipients=recipients,
            subject=f"[Cold Chain] 새로운 배차 생성 - {dispatch.dispatch_number}",
            template_name='dispatch_created.html',
            context=context
        )
    
    async def send_dispatch_assigned(
        self,
        dispatch: Dispatch,
        driver_email: str
    ):
        """Send notification to driver when dispatch is assigned"""
        context = {
            'driver_name': dispatch.driver.full_name if dispatch.driver else 'Driver',
            'dispatch_number': dispatch.dispatch_number,
            'dispatch_date': str(dispatch.dispatch_date),
            'vehicle': dispatch.vehicle.vehicle_number if dispatch.vehicle else 'N/A',
            'total_orders': len(dispatch.orders),
            'total_pallets': dispatch.total_pallets,
            'orders': [
                {
                    'order_number': order.order_number,
                    'pickup': order.pickup_client.name if order.pickup_client else 'N/A',
                    'delivery': order.delivery_client.name if order.delivery_client else 'N/A',
                    'pallets': order.pallets
                }
                for order in dispatch.orders[:10]  # Limit to 10 orders
            ]
        }
        
        return await self.send_email(
            recipients=[driver_email],
            subject=f"[Cold Chain] 배차 할당 - {dispatch.dispatch_number}",
            template_name='dispatch_assigned.html',
            context=context
        )
    
    async def send_dispatch_completed(
        self,
        dispatch: Dispatch,
        recipients: List[str]
    ):
        """Send notification when dispatch is completed"""
        context = {
            'dispatch_number': dispatch.dispatch_number,
            'dispatch_date': str(dispatch.dispatch_date),
            'vehicle': dispatch.vehicle.vehicle_number if dispatch.vehicle else 'N/A',
            'driver': dispatch.driver.full_name if dispatch.driver else 'N/A',
            'total_orders': len(dispatch.orders),
            'completed_orders': sum(1 for o in dispatch.orders if o.status == 'completed'),
            'total_distance': dispatch.total_distance_km or 0,
            'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return await self.send_email(
            recipients=recipients,
            subject=f"[Cold Chain] 배차 완료 - {dispatch.dispatch_number}",
            template_name='dispatch_completed.html',
            context=context
        )
    
    async def send_temperature_alert(
        self,
        vehicle: Vehicle,
        current_temp: float,
        threshold_min: float,
        threshold_max: float,
        recipients: List[str]
    ):
        """Send temperature alert notification"""
        context = {
            'vehicle_number': vehicle.vehicle_number,
            'current_temp': current_temp,
            'threshold_min': threshold_min,
            'threshold_max': threshold_max,
            'alert_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'severity': 'HIGH' if current_temp > threshold_max + 5 or current_temp < threshold_min - 5 else 'MEDIUM'
        }
        
        return await self.send_email(
            recipients=recipients,
            subject=f"[Cold Chain] ⚠️ 온도 이탈 알림 - {vehicle.vehicle_number}",
            template_name='temperature_alert.html',
            context=context
        )
    
    async def send_maintenance_alert(
        self,
        vehicle: Vehicle,
        reason: str,
        recipients: List[str]
    ):
        """Send maintenance alert notification"""
        context = {
            'vehicle_number': vehicle.vehicle_number,
            'vehicle_type': vehicle.vehicle_type,
            'reason': reason,
            'alert_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return await self.send_email(
            recipients=recipients,
            subject=f"[Cold Chain] 🔧 유지보수 필요 - {vehicle.vehicle_number}",
            template_name='maintenance_alert.html',
            context=context
        )
    
    async def send_daily_report(
        self,
        report_date: date,
        stats: Dict[str, Any],
        recipients: List[str]
    ):
        """Send daily report email"""
        context = {
            'report_date': str(report_date),
            'total_dispatches': stats.get('total_dispatches', 0),
            'completed_dispatches': stats.get('completed_dispatches', 0),
            'total_orders': stats.get('total_orders', 0),
            'completed_orders': stats.get('completed_orders', 0),
            'active_vehicles': stats.get('active_vehicles', 0),
            'total_distance': stats.get('total_distance', 0),
            'completion_rate': stats.get('completion_rate', 0),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return await self.send_email(
            recipients=recipients,
            subject=f"[Cold Chain] 일일 리포트 - {report_date}",
            template_name='daily_report.html',
            context=context
        )
    
    async def send_weekly_report(
        self,
        week_start: date,
        week_end: date,
        stats: Dict[str, Any],
        recipients: List[str]
    ):
        """Send weekly report email"""
        context = {
            'week_start': str(week_start),
            'week_end': str(week_end),
            'total_dispatches': stats.get('total_dispatches', 0),
            'total_orders': stats.get('total_orders', 0),
            'completion_rate': stats.get('completion_rate', 0),
            'total_distance': stats.get('total_distance', 0),
            'top_vehicles': stats.get('top_vehicles', []),
            'top_drivers': stats.get('top_drivers', []),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return await self.send_email(
            recipients=recipients,
            subject=f"[Cold Chain] 주간 리포트 - {week_start} ~ {week_end}",
            template_name='weekly_report.html',
            context=context
        )
    
    async def send_monthly_report(
        self,
        month: str,
        stats: Dict[str, Any],
        recipients: List[str]
    ):
        """Send monthly report email"""
        context = {
            'month': month,
            'total_dispatches': stats.get('total_dispatches', 0),
            'total_orders': stats.get('total_orders', 0),
            'completion_rate': stats.get('completion_rate', 0),
            'total_distance': stats.get('total_distance', 0),
            'total_revenue': stats.get('total_revenue', 0),
            'top_customers': stats.get('top_customers', []),
            'performance_summary': stats.get('performance_summary', {}),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return await self.send_email(
            recipients=recipients,
            subject=f"[Cold Chain] 월간 리포트 - {month}",
            template_name='monthly_report.html',
            context=context
        )
    
    async def send_driver_evaluation(
        self,
        driver: User,
        evaluation: Dict[str, Any],
        driver_email: str
    ):
        """Send driver evaluation notification"""
        context = {
            'driver_name': driver.full_name,
            'evaluation_period': evaluation.get('period', 'N/A'),
            'overall_score': evaluation.get('overall_score', 0),
            'grade': evaluation.get('grade', 'N/A'),
            'strengths': evaluation.get('strengths', []),
            'weaknesses': evaluation.get('weaknesses', []),
            'recommendations': evaluation.get('recommendations', []),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return await self.send_email(
            recipients=[driver_email],
            subject=f"[Cold Chain] 운전자 평가 결과 - {driver.full_name}",
            template_name='driver_evaluation.html',
            context=context
        )


# Singleton instance
email_service = EmailService()


def get_email_service() -> EmailService:
    """Get email service instance"""
    return email_service
