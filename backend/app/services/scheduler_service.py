"""
Scheduler Service
스케줄러 서비스 - 정기 작업 자동 실행
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
from datetime import datetime

from app.core.database import SessionLocal
from app.services.recurring_order_generator import RecurringOrderGeneratorService
from app.services.temperature_monitoring import TemperatureMonitoringService
from app.services.maintenance_alert_service import MaintenanceAlertService


class SchedulerService:
    """스케줄러 서비스"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """스케줄 작업 설정"""
        
        # 정기 주문 자동 생성 (매일 오전 6시)
        self.scheduler.add_job(
            self._generate_recurring_orders,
            trigger=CronTrigger(hour=6, minute=0),
            id='generate_recurring_orders',
            name='정기 주문 자동 생성',
            replace_existing=True
        )
        
        # 온도 데이터 자동 수집 (5분마다) - Phase 3-A Part 4
        self.scheduler.add_job(
            self._collect_temperature_data,
            trigger=IntervalTrigger(minutes=5),
            id='collect_temperature_data',
            name='온도 데이터 자동 수집',
            replace_existing=True
        )
        
        logger.info("✅ Scheduled jobs configured:")
        logger.info("  - 정기 주문 자동 생성: 매일 오전 6시")
        logger.info("  - 온도 데이터 자동 수집: 5분마다")
    
    async def _generate_recurring_orders(self):
        """정기 주문 자동 생성 (스케줄 작업)"""
        logger.info("🕐 Starting scheduled recurring order generation...")
        
        db = SessionLocal()
        try:
            result = RecurringOrderGeneratorService.generate_orders_for_date(db)
            
            logger.info(f"✅ Scheduled recurring order generation completed: {result}")
            
            # 실패가 있으면 경고
            if result['failed'] > 0:
                logger.warning(f"⚠️  {result['failed']} recurring orders failed to generate")
                for error in result['errors']:
                    logger.error(f"  - {error}")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate recurring orders: {e}")
        finally:
            db.close()
    
    async def _collect_temperature_data(self):
        """온도 데이터 자동 수집 (스케줄 작업) - Phase 3-A Part 4"""
        logger.info("🌡️  Starting scheduled temperature data collection...")
        
        db = SessionLocal()
        try:
            service = TemperatureMonitoringService(db)
            result = await service.collect_all_temperatures()
            
            if result['success']:
                logger.info(
                    f"✅ Temperature collection completed: "
                    f"{result['collected_count']} records, "
                    f"{result['alerts_created']} alerts"
                )
                
                # Critical 알림이 있으면 경고
                if result['critical_alerts'] > 0:
                    logger.warning(
                        f"🚨 {result['critical_alerts']} critical temperature alerts detected!"
                    )
                    for alert_detail in result['critical_alert_details']:
                        logger.warning(
                            f"  - Vehicle {alert_detail['vehicle_number']}: "
                            f"{alert_detail['temperature']}°C ({alert_detail['alert_type']})"
                        )
            else:
                logger.error(f"❌ Temperature collection failed: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            logger.error(f"❌ Failed to collect temperature data: {e}")
        finally:
            db.close()
    
    async def start(self):
        """스케줄러 시작"""
        logger.info("🚀 Starting scheduler...")
        self.scheduler.start()
        logger.info("✅ Scheduler started")
    
    async def stop(self):
        """스케줄러 중지"""
        logger.info("🛑 Stopping scheduler...")
        self.scheduler.shutdown()
        logger.info("✅ Scheduler stopped")
    
    def get_jobs(self):
        """현재 스케줄된 작업 목록"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs


# 싱글톤 인스턴스
scheduler_service = SchedulerService()
