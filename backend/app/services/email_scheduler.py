"""
Email Scheduler
Schedules automated email reports and notifications
"""
from datetime import datetime, date, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.core.database import SessionLocal
from app.services.email_service import get_email_service
from app.models.dispatch import Dispatch
from app.models.order import Order
from app.models.vehicle import Vehicle
from app.models.user import User


class EmailScheduler:
    """Email scheduler for automated reports"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.email_service = get_email_service()
    
    def start(self):
        """Start the scheduler"""
        # Daily report at 8 AM
        self.scheduler.add_job(
            self.send_daily_reports,
            CronTrigger(hour=8, minute=0),
            id='daily_report',
            name='Send Daily Report',
            replace_existing=True
        )
        
        # Weekly report on Monday at 9 AM
        self.scheduler.add_job(
            self.send_weekly_reports,
            CronTrigger(day_of_week='mon', hour=9, minute=0),
            id='weekly_report',
            name='Send Weekly Report',
            replace_existing=True
        )
        
        # Monthly report on 1st of month at 10 AM
        self.scheduler.add_job(
            self.send_monthly_reports,
            CronTrigger(day=1, hour=10, minute=0),
            id='monthly_report',
            name='Send Monthly Report',
            replace_existing=True
        )
        
        self.scheduler.start()
        print("Email scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        print("Email scheduler stopped")
    
    async def send_daily_reports(self):
        """Send daily reports to admins"""
        db = SessionLocal()
        try:
            # Get yesterday's date
            report_date = date.today() - timedelta(days=1)
            
            # Query statistics
            dispatches = db.query(Dispatch).filter(
                Dispatch.dispatch_date == report_date
            ).all()
            
            total_dispatches = len(dispatches)
            completed_dispatches = sum(1 for d in dispatches if d.status == 'completed')
            
            orders = db.query(Order).filter(
                func.date(Order.created_at) == report_date
            ).all()
            
            total_orders = len(orders)
            completed_orders = sum(1 for o in orders if o.status == 'completed')
            
            active_vehicles = db.query(Vehicle).filter(
                Vehicle.id.in_([d.vehicle_id for d in dispatches if d.vehicle_id])
            ).count()
            
            total_distance = sum(d.total_distance_km for d in dispatches if d.total_distance_km) or 0
            
            completion_rate = (completed_dispatches / total_dispatches * 100) if total_dispatches > 0 else 0
            
            stats = {
                'total_dispatches': total_dispatches,
                'completed_dispatches': completed_dispatches,
                'total_orders': total_orders,
                'completed_orders': completed_orders,
                'active_vehicles': active_vehicles,
                'total_distance': total_distance,
                'completion_rate': completion_rate
            }
            
            # Get admin emails
            admins = db.query(User).filter(User.role == 'admin').all()
            recipients = [admin.email for admin in admins if admin.email]
            
            if recipients:
                await self.email_service.send_daily_report(
                    report_date=report_date,
                    stats=stats,
                    recipients=recipients
                )
                print(f"Daily report sent to {len(recipients)} recipients")
        
        except Exception as e:
            print(f"Failed to send daily report: {e}")
        finally:
            db.close()
    
    async def send_weekly_reports(self):
        """Send weekly reports to admins"""
        db = SessionLocal()
        try:
            # Get last week's date range
            today = date.today()
            week_end = today - timedelta(days=today.weekday() + 1)  # Last Sunday
            week_start = week_end - timedelta(days=6)  # Last Monday
            
            # Query statistics
            dispatches = db.query(Dispatch).filter(
                and_(
                    Dispatch.dispatch_date >= week_start,
                    Dispatch.dispatch_date <= week_end
                )
            ).all()
            
            total_dispatches = len(dispatches)
            completed_dispatches = sum(1 for d in dispatches if d.status == 'completed')
            
            orders = db.query(Order).filter(
                and_(
                    func.date(Order.created_at) >= week_start,
                    func.date(Order.created_at) <= week_end
                )
            ).all()
            
            total_orders = len(orders)
            completion_rate = (completed_dispatches / total_dispatches * 100) if total_dispatches > 0 else 0
            total_distance = sum(d.total_distance_km for d in dispatches if d.total_distance_km) or 0
            
            # Top vehicles (by dispatch count)
            vehicle_counts = {}
            for dispatch in dispatches:
                if dispatch.vehicle:
                    vid = dispatch.vehicle.vehicle_number
                    vehicle_counts[vid] = vehicle_counts.get(vid, 0) + 1
            
            top_vehicles = sorted(vehicle_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Top drivers (by dispatch count)
            driver_counts = {}
            for dispatch in dispatches:
                if dispatch.driver:
                    dname = dispatch.driver.full_name
                    driver_counts[dname] = driver_counts.get(dname, 0) + 1
            
            top_drivers = sorted(driver_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            stats = {
                'total_dispatches': total_dispatches,
                'total_orders': total_orders,
                'completion_rate': completion_rate,
                'total_distance': total_distance,
                'top_vehicles': [{'name': v[0], 'count': v[1]} for v in top_vehicles],
                'top_drivers': [{'name': d[0], 'count': d[1]} for d in top_drivers]
            }
            
            # Get admin emails
            admins = db.query(User).filter(User.role == 'admin').all()
            recipients = [admin.email for admin in admins if admin.email]
            
            if recipients:
                await self.email_service.send_weekly_report(
                    week_start=week_start,
                    week_end=week_end,
                    stats=stats,
                    recipients=recipients
                )
                print(f"Weekly report sent to {len(recipients)} recipients")
        
        except Exception as e:
            print(f"Failed to send weekly report: {e}")
        finally:
            db.close()
    
    async def send_monthly_reports(self):
        """Send monthly reports to admins"""
        db = SessionLocal()
        try:
            # Get last month
            today = date.today()
            last_month = today.replace(day=1) - timedelta(days=1)
            month_start = last_month.replace(day=1)
            month_end = last_month
            month_str = last_month.strftime('%Y-%m')
            
            # Query statistics (similar to weekly but for month)
            dispatches = db.query(Dispatch).filter(
                and_(
                    Dispatch.dispatch_date >= month_start,
                    Dispatch.dispatch_date <= month_end
                )
            ).all()
            
            total_dispatches = len(dispatches)
            completed_dispatches = sum(1 for d in dispatches if d.status == 'completed')
            
            orders = db.query(Order).filter(
                and_(
                    func.date(Order.created_at) >= month_start,
                    func.date(Order.created_at) <= month_end
                )
            ).all()
            
            total_orders = len(orders)
            completion_rate = (completed_dispatches / total_dispatches * 100) if total_dispatches > 0 else 0
            total_distance = sum(d.total_distance_km for d in dispatches if d.total_distance_km) or 0
            
            stats = {
                'total_dispatches': total_dispatches,
                'total_orders': total_orders,
                'completion_rate': completion_rate,
                'total_distance': total_distance,
                'total_revenue': 0,  # Placeholder
                'top_customers': [],  # Placeholder
                'performance_summary': {}  # Placeholder
            }
            
            # Get admin emails
            admins = db.query(User).filter(User.role == 'admin').all()
            recipients = [admin.email for admin in admins if admin.email]
            
            if recipients:
                await self.email_service.send_monthly_report(
                    month=month_str,
                    stats=stats,
                    recipients=recipients
                )
                print(f"Monthly report sent to {len(recipients)} recipients")
        
        except Exception as e:
            print(f"Failed to send monthly report: {e}")
        finally:
            db.close()


# Singleton instance
email_scheduler = EmailScheduler()


def get_email_scheduler() -> EmailScheduler:
    """Get email scheduler instance"""
    return email_scheduler
