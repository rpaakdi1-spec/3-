"""
Scheduler Service
스케줄러 서비스 - 정기 작업 자동 실행
"""
import os
import redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
from datetime import datetime

from app.core.database import SessionLocal
from app.core.config import settings
from app.services.recurring_order_generator import RecurringOrderGeneratorService
from app.services.temperature_monitoring import TemperatureMonitoringService
from app.services.maintenance_alert_service import MaintenanceAlertService
from app.services.driver_mileage_service import DriverMileageService
from app.services.uvis_gps_service import UvisGPSService


class SchedulerService:
    """스케줄러 서비스"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """싱글톤 패턴 구현"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 이미 초기화된 경우 스킵 (멀티 워커 환경 대응)
        if SchedulerService._initialized:
            return
            
        self.scheduler = AsyncIOScheduler()
        self.redis_client = None
        self._setup_redis()
        self._setup_jobs()
        SchedulerService._initialized = True
    
    def _setup_redis(self):
        """Redis 클라이언트 설정 (분산 락 사용)"""
        try:
            redis_url = settings.REDIS_URL
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # 연결 테스트
            self.redis_client.ping()
            logger.info("✅ Redis client connected for scheduler lock")
        except Exception as e:
            logger.warning(f"⚠️  Redis connection failed: {e}. Scheduler will run without distributed lock.")
            self.redis_client = None
    
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
        
        # GPS 위치 데이터 자동 수집 (5분마다) - 실시간 차량 추적
        self.scheduler.add_job(
            self._sync_vehicle_gps_data,
            trigger=IntervalTrigger(minutes=5),
            id='sync_vehicle_gps_data',
            name='GPS 위치 데이터 자동 수집',
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
        
        # 운전자 주행거리 자동 계산 (매일 자정 + 5분) - 차량 주행거리 계산 후 실행
        self.scheduler.add_job(
            self._calculate_driver_mileage,
            trigger=CronTrigger(hour=0, minute=5),
            id='calculate_driver_mileage',
            name='운전자 주행거리 자동 계산',
            replace_existing=True
        )

        # GPS 이력 자동삭제 (매일 새벽 2시) - 3일치만 보관
        self.scheduler.add_job(
            self._cleanup_old_gps_logs,
            trigger=CronTrigger(hour=2, minute=0),
            id='cleanup_old_gps_logs',
            name='GPS 이력 자동삭제 (3일 초과분)',
            replace_existing=True
        )

        logger.info("✅ Scheduled jobs configured:")
        logger.info("  - 정기 주문 자동 생성: 매일 오전 6시")
        logger.info("  - GPS 위치 데이터 자동 수집: 5분마다")
        logger.info("  - 온도 데이터 자동 수집: 5분마다")
        logger.info("  - 운전자 주행거리 자동 계산: 매일 오전 00:05 (자정 5분 후)")
        logger.info("  - GPS 이력 자동삭제: 매일 새벽 2시 (3일 초과분)")
    
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
    
    async def _sync_vehicle_gps_data(self):
        """GPS 위치 데이터 자동 수집 (스케줄 작업) - 5분마다"""
        logger.info("📍 Starting scheduled GPS data synchronization...")
        
        db = SessionLocal()
        try:
            service = UvisGPSService(db)
            gps_data = await service.get_vehicle_gps_data()
            
            if gps_data:
                logger.info(
                    f"✅ GPS synchronization completed: "
                    f"{len(gps_data)} vehicle locations updated"
                )
                
                # 최근 업데이트된 차량 수 카운트
                active_vehicles = len([v for v in gps_data if v.get('latitude') and v.get('longitude')])
                logger.info(f"📊 Active vehicles with GPS: {active_vehicles}/{len(gps_data)}")
            else:
                logger.warning("⚠️  No GPS data collected")
            
        except Exception as e:
            logger.error(f"❌ Failed to synchronize GPS data: {e}")
            # GPS 동기화 실패는 치명적이지 않으므로 계속 진행
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
    
    async def _calculate_driver_mileage(self):
        """운전자 주행거리 자동 계산 (스케줄 작업) - 매일 자정"""
        from datetime import date, timedelta
        import asyncio
        
        yesterday = date.today() - timedelta(days=1)
        logger.info(f"🚗 Starting scheduled driver mileage calculation for {yesterday}...")
        
        db = SessionLocal()
        max_retries = 3
        retry_delay = 300  # 5분 (초)
        
        for attempt in range(1, max_retries + 1):
            try:
                service = DriverMileageService(db)
                results = service.calculate_driver_mileage_from_vehicle(yesterday)
                
                if results:
                    total_distance = sum(r.total_distance_km for r in results)
                    total_drivers = len(results)
                    
                    logger.info(
                        f"✅ Driver mileage calculation completed (attempt {attempt}/{max_retries}): "
                        f"{total_drivers} drivers, {total_distance:.2f}km total"
                    )
                    
                    # 상위 5명 운전자 로깅
                    top_drivers = sorted(results, key=lambda x: x.total_distance_km, reverse=True)[:5]
                    logger.info("📊 Top 5 drivers:")
                    for i, driver in enumerate(top_drivers, 1):
                        driver_name = driver.notes.replace("차량기반:", "")
                        logger.info(
                            f"  {i}. {driver_name}: {driver.total_distance_km:.2f}km, "
                            f"{driver.vehicle_count} vehicles"
                        )
                    
                    # 성공 시 반환
                    return
                else:
                    logger.warning(f"⚠️  No drivers calculated on attempt {attempt}/{max_retries}")
                    
                    if attempt < max_retries:
                        logger.info(f"🔄 Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                    
            except Exception as e:
                logger.error(f"❌ Driver mileage calculation failed (attempt {attempt}/{max_retries}): {e}")
                
                if attempt < max_retries:
                    logger.info(f"🔄 Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"❌ All {max_retries} attempts failed for driver mileage calculation")
            finally:
                if attempt == max_retries:
                    db.close()
    
    async def start(self):
        """스케줄러 시작 (멀티 워커 환경에서는 한 번만 실행)"""
        # 이미 스케줄러가 실행 중이면 스킵
        if self.scheduler.running:
            logger.info("ℹ️  Scheduler already running, skipping start")
            return
        
        # Redis 분산 락을 사용하여 하나의 워커에서만 스케줄러 실행
        lock_acquired = self._acquire_scheduler_lock()
        
        if not lock_acquired:
            logger.info("ℹ️  Scheduler lock already acquired by another worker, skipping start")
            return
        
        # 멀티 워커 환경에서는 첫 번째 워커에서만 스케줄러 실행
        worker_id = os.getpid()
        logger.info(f"🔍 Worker process ID: {worker_id}")
        
        # 환경 변수로 스케줄러 실행 제어 가능
        scheduler_enabled = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"
        if not scheduler_enabled:
            logger.info("⚠️  Scheduler disabled by SCHEDULER_ENABLED env var")
            return
            
        logger.info("🚀 Starting scheduler...")
        self.scheduler.start()
        logger.info("✅ Scheduler started successfully")
        logger.info(f"📋 Active jobs: {len(self.scheduler.get_jobs())}")
    
    def _acquire_scheduler_lock(self) -> bool:
        """Redis를 사용하여 스케줄러 락 획득"""
        if not self.redis_client:
            # Redis가 없으면 락 없이 진행 (단일 워커 환경)
            logger.warning("⚠️  Redis not available, running scheduler without distributed lock")
            return True
        
        try:
            # 락 키: scheduler:lock
            # TTL: 3600초 (1시간) - 스케줄러가 계속 실행되므로 충분한 시간
            lock_key = "scheduler:lock"
            lock_ttl = 3600
            
            # NX: 키가 존재하지 않을 때만 설정
            # EX: TTL 설정 (초)
            result = self.redis_client.set(lock_key, os.getpid(), nx=True, ex=lock_ttl)
            
            if result:
                logger.info(f"✅ Scheduler lock acquired (PID: {os.getpid()})")
                return True
            else:
                lock_holder = self.redis_client.get(lock_key)
                logger.info(f"ℹ️  Scheduler lock held by PID: {lock_holder}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to acquire scheduler lock: {e}")
            # 락 획득 실패 시 안전하게 스케줄러를 시작하지 않음
            return False
    
    async def stop(self):
        """스케줄러 중지"""
        logger.info("🛑 Stopping scheduler...")
        
        # 스케줄러 중지
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("✅ Scheduler stopped")
        
        # Redis 락 해제
        if self.redis_client:
            try:
                lock_key = "scheduler:lock"
                current_holder = self.redis_client.get(lock_key)
                
                # 현재 프로세스가 락을 보유하고 있는 경우에만 해제
                if current_holder and int(current_holder) == os.getpid():
                    self.redis_client.delete(lock_key)
                    logger.info(f"✅ Scheduler lock released (PID: {os.getpid()})")
            except Exception as e:
                logger.error(f"❌ Failed to release scheduler lock: {e}")
    
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

    async def _cleanup_old_gps_logs(self):
        """GPS/온도 이력 자동삭제 - 3일치만 보관 (매일 새벽 2시)"""
        from datetime import timedelta
        from app.models.uvis_gps import VehicleGPSLog, VehicleTemperatureLog

        logger.info("🗑️  Starting GPS history cleanup (keeping 3 days)...")
        cutoff = datetime.utcnow() - timedelta(days=3)
        cutoff_date = cutoff.strftime("%Y%m%d")  # YYYYMMDD

        db: Session = SessionLocal()
        try:
            # VehicleGPSLog 삭제
            gps_deleted = db.query(VehicleGPSLog).filter(
                VehicleGPSLog.bi_date < cutoff_date
            ).delete(synchronize_session=False)

            # VehicleTemperatureLog 삭제
            temp_deleted = db.query(VehicleTemperatureLog).filter(
                VehicleTemperatureLog.tpl_date < cutoff_date
            ).delete(synchronize_session=False)

            db.commit()
            logger.info(
                f"✅ GPS cleanup done: "
                f"GPS {gps_deleted}건 삭제, 온도 {temp_deleted}건 삭제 "
                f"(기준: {cutoff_date} 이전)"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"❌ GPS cleanup failed: {e}")
        finally:
            db.close()


# 싱글톤 인스턴스
scheduler_service = SchedulerService()
