"""
Maintenance Alert Service
정비 알림 서비스
Phase 3-B Week 3: 알림 시스템 통합
"""
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

from app.models.vehicle_maintenance import (
    VehicleMaintenanceRecord,
    VehiclePart,
    MaintenanceSchedule,
    VehicleInspection,
    MaintenanceStatus
)
from app.models.vehicle import Vehicle
from app.models.notification import (
    Notification,
    NotificationType,
    NotificationChannel,
    NotificationStatus
)
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class MaintenanceAlertService:
    """정비 알림 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
    
    def check_and_send_maintenance_alerts(self) -> Dict[str, int]:
        """
        모든 정비 관련 알림 체크 및 발송
        
        Returns:
            알림 발송 통계
        """
        stats = {
            'overdue_schedules': 0,
            'upcoming_schedules': 0,
            'low_stock_parts': 0,
            'expiring_inspections': 0,
            'total_sent': 0
        }
        
        try:
            # 1. 연체 스케줄 알림
            overdue = self.check_overdue_schedules()
            stats['overdue_schedules'] = len(overdue)
            
            # 2. 정비 예정 알림
            upcoming = self.check_upcoming_maintenance()
            stats['upcoming_schedules'] = len(upcoming)
            
            # 3. 재고 부족 알림
            low_stock = self.check_low_stock_parts()
            stats['low_stock_parts'] = len(low_stock)
            
            # 4. 검사 만료 임박 알림
            expiring = self.check_expiring_inspections()
            stats['expiring_inspections'] = len(expiring)
            
            stats['total_sent'] = sum([
                stats['overdue_schedules'],
                stats['upcoming_schedules'],
                stats['low_stock_parts'],
                stats['expiring_inspections']
            ])
            
            logger.info(f"정비 알림 발송 완료: {stats}")
            
        except Exception as e:
            logger.error(f"정비 알림 체크 실패: {e}")
        
        return stats
    
    def check_overdue_schedules(self) -> List[MaintenanceSchedule]:
        """
        연체 정비 스케줄 체크 및 알림 발송
        
        Returns:
            연체 스케줄 리스트
        """
        schedules = self.db.query(MaintenanceSchedule).filter(
            and_(
                MaintenanceSchedule.is_active == True,
                MaintenanceSchedule.is_overdue == True
            )
        ).all()
        
        for schedule in schedules:
            try:
                # 알림 생성
                title = f"🚨 정비 연체: {schedule.vehicle.plate_number}"
                
                # 연체 정보
                overdue_info = []
                if schedule.next_maintenance_date:
                    days_overdue = (date.today() - schedule.next_maintenance_date).days
                    overdue_info.append(f"{days_overdue}일 경과")
                
                if schedule.next_maintenance_odometer and schedule.vehicle:
                    # 현재 주행거리는 최근 GPS 로그에서 가져올 수 있음
                    # 여기서는 예시로 표시
                    overdue_info.append(f"주행거리 초과")
                
                message = f"""
정비가 연체되었습니다.

차량: {schedule.vehicle.plate_number}
정비 유형: {schedule.maintenance_type.value}
{' • '.join(overdue_info) if overdue_info else ''}

즉시 정비를 예약해 주세요.
                """.strip()
                
                # 알림 생성
                self.notification_service.create_notification(
                    title=title,
                    message=message,
                    notification_type=NotificationType.MAINTENANCE_ALERT,
                    priority="HIGH",
                    channels=[NotificationChannel.SMS, NotificationChannel.EMAIL],
                    metadata={
                        'schedule_id': schedule.id,
                        'vehicle_id': schedule.vehicle_id,
                        'vehicle_plate': schedule.vehicle.plate_number,
                        'maintenance_type': schedule.maintenance_type.value,
                        'alert_type': 'overdue'
                    }
                )
                
                logger.info(f"연체 알림 발송: {schedule.vehicle.plate_number} - {schedule.maintenance_type.value}")
                
            except Exception as e:
                logger.error(f"연체 알림 발송 실패: schedule_id={schedule.id}, error={e}")
        
        return schedules
    
    def check_upcoming_maintenance(self, days_ahead: int = 7) -> List[MaintenanceSchedule]:
        """
        정비 예정 알림
        
        Args:
            days_ahead: 며칠 전 알림 (기본 7일)
            
        Returns:
            예정 스케줄 리스트
        """
        threshold_date = date.today() + timedelta(days=days_ahead)
        
        schedules = self.db.query(MaintenanceSchedule).filter(
            and_(
                MaintenanceSchedule.is_active == True,
                MaintenanceSchedule.next_maintenance_date != None,
                MaintenanceSchedule.next_maintenance_date <= threshold_date,
                MaintenanceSchedule.next_maintenance_date >= date.today(),
                MaintenanceSchedule.is_overdue == False
            )
        ).all()
        
        for schedule in schedules:
            try:
                days_until = (schedule.next_maintenance_date - date.today()).days
                
                title = f"📅 정비 예정: {schedule.vehicle.plate_number}"
                message = f"""
정비 예정일이 {days_until}일 남았습니다.

차량: {schedule.vehicle.plate_number}
정비 유형: {schedule.maintenance_type.value}
예정일: {schedule.next_maintenance_date.strftime('%Y-%m-%d')}
"""
                
                if schedule.next_maintenance_odometer:
                    message += f"예정 주행거리: {schedule.next_maintenance_odometer:,.0f}km\n"
                
                message += "\n정비소에 예약을 진행해 주세요."
                
                # 알림 생성
                self.notification_service.create_notification(
                    title=title,
                    message=message.strip(),
                    notification_type=NotificationType.MAINTENANCE_REMINDER,
                    priority="MEDIUM",
                    channels=[NotificationChannel.SMS, NotificationChannel.EMAIL],
                    metadata={
                        'schedule_id': schedule.id,
                        'vehicle_id': schedule.vehicle_id,
                        'vehicle_plate': schedule.vehicle.plate_number,
                        'maintenance_type': schedule.maintenance_type.value,
                        'days_until': days_until,
                        'alert_type': 'upcoming'
                    }
                )
                
                logger.info(f"예정 알림 발송: {schedule.vehicle.plate_number} - {days_until}일 후")
                
            except Exception as e:
                logger.error(f"예정 알림 발송 실패: schedule_id={schedule.id}, error={e}")
        
        return schedules
    
    def check_low_stock_parts(self) -> List[VehiclePart]:
        """
        재고 부족 부품 알림
        
        Returns:
            재고 부족 부품 리스트
        """
        parts = self.db.query(VehiclePart).filter(
            and_(
                VehiclePart.is_active == True,
                VehiclePart.quantity_in_stock <= VehiclePart.minimum_stock
            )
        ).all()
        
        if not parts:
            return []
        
        # 재고 부족 부품 목록 생성
        parts_list = []
        for part in parts:
            shortage = part.minimum_stock - part.quantity_in_stock
            parts_list.append(
                f"• {part.part_name} ({part.part_number}): "
                f"{part.quantity_in_stock}{part.unit} "
                f"(부족: {shortage}{part.unit})"
            )
        
        title = f"⚠️ 부품 재고 부족: {len(parts)}개 품목"
        message = f"""
다음 부품의 재고가 최소 수량 이하입니다:

{chr(10).join(parts_list[:10])}
"""
        
        if len(parts) > 10:
            message += f"\n그 외 {len(parts) - 10}개 품목..."
        
        message += "\n\n발주를 진행해 주세요."
        
        try:
            # 알림 생성
            self.notification_service.create_notification(
                title=title,
                message=message.strip(),
                notification_type=NotificationType.INVENTORY_ALERT,
                priority="HIGH",
                channels=[NotificationChannel.SMS, NotificationChannel.EMAIL],
                metadata={
                    'part_count': len(parts),
                    'part_ids': [p.id for p in parts],
                    'alert_type': 'low_stock'
                }
            )
            
            logger.info(f"재고 부족 알림 발송: {len(parts)}개 품목")
            
        except Exception as e:
            logger.error(f"재고 부족 알림 발송 실패: error={e}")
        
        return parts
    
    def check_expiring_inspections(self, days_ahead: int = 30) -> List[VehicleInspection]:
        """
        검사 만료 임박 알림
        
        Args:
            days_ahead: 며칠 전 알림 (기본 30일)
            
        Returns:
            만료 임박 검사 리스트
        """
        threshold_date = date.today() + timedelta(days=days_ahead)
        
        inspections = self.db.query(VehicleInspection).filter(
            and_(
                VehicleInspection.expiry_date <= threshold_date,
                VehicleInspection.expiry_date >= date.today()
            )
        ).all()
        
        for inspection in inspections:
            try:
                days_until = (inspection.expiry_date - date.today()).days
                
                # 긴급도 결정
                if days_until <= 7:
                    priority = "HIGH"
                    icon = "🚨"
                elif days_until <= 14:
                    priority = "MEDIUM"
                    icon = "⚠️"
                else:
                    priority = "MEDIUM"
                    icon = "📅"
                
                title = f"{icon} 검사 만료 임박: {inspection.vehicle.plate_number}"
                message = f"""
차량 검사 만료일이 {days_until}일 남았습니다.

차량: {inspection.vehicle.plate_number}
검사 유형: {inspection.inspection_type}
만료일: {inspection.expiry_date.strftime('%Y-%m-%d')}

검사소에 예약을 진행해 주세요.
                """.strip()
                
                # 알림 생성
                self.notification_service.create_notification(
                    title=title,
                    message=message,
                    notification_type=NotificationType.INSPECTION_ALERT,
                    priority=priority,
                    channels=[NotificationChannel.SMS, NotificationChannel.EMAIL],
                    metadata={
                        'inspection_id': inspection.id,
                        'vehicle_id': inspection.vehicle_id,
                        'vehicle_plate': inspection.vehicle.plate_number,
                        'inspection_type': inspection.inspection_type,
                        'expiry_date': inspection.expiry_date.isoformat(),
                        'days_until': days_until,
                        'alert_type': 'expiring_inspection'
                    }
                )
                
                logger.info(f"검사 만료 알림 발송: {inspection.vehicle.plate_number} - {days_until}일 후")
                
            except Exception as e:
                logger.error(f"검사 만료 알림 발송 실패: inspection_id={inspection.id}, error={e}")
        
        return inspections
    
    def notify_maintenance_started(self, maintenance_id: int):
        """
        정비 시작 알림
        
        Args:
            maintenance_id: 정비 기록 ID
        """
        record = self.db.query(VehicleMaintenanceRecord).filter(
            VehicleMaintenanceRecord.id == maintenance_id
        ).first()
        
        if not record:
            return
        
        title = f"🔧 정비 시작: {record.vehicle.plate_number}"
        message = f"""
정비가 시작되었습니다.

차량: {record.vehicle.plate_number}
정비 번호: {record.maintenance_number}
정비 유형: {record.maintenance_type.value}
정비소: {record.service_center or '미정'}
정비사: {record.mechanic_name or '미정'}

예정 완료 시간을 확인해 주세요.
        """.strip()
        
        try:
            self.notification_service.create_notification(
                title=title,
                message=message,
                notification_type=NotificationType.MAINTENANCE_UPDATE,
                priority="MEDIUM",
                channels=[NotificationChannel.PUSH],
                metadata={
                    'maintenance_id': maintenance_id,
                    'vehicle_id': record.vehicle_id,
                    'vehicle_plate': record.vehicle.plate_number,
                    'status': 'started'
                }
            )
            
            logger.info(f"정비 시작 알림 발송: {record.maintenance_number}")
            
        except Exception as e:
            logger.error(f"정비 시작 알림 발송 실패: error={e}")
    
    def notify_maintenance_completed(self, maintenance_id: int):
        """
        정비 완료 알림
        
        Args:
            maintenance_id: 정비 기록 ID
        """
        record = self.db.query(VehicleMaintenanceRecord).filter(
            VehicleMaintenanceRecord.id == maintenance_id
        ).first()
        
        if not record:
            return
        
        title = f"✅ 정비 완료: {record.vehicle.plate_number}"
        message = f"""
정비가 완료되었습니다.

차량: {record.vehicle.plate_number}
정비 번호: {record.maintenance_number}
정비 유형: {record.maintenance_type.value}
총 비용: {record.total_cost:,.0f}원
"""
        
        if record.findings:
            message += f"\n발견사항:\n{record.findings}\n"
        
        if record.recommendations:
            message += f"\n권고사항:\n{record.recommendations}\n"
        
        if record.next_maintenance_date:
            message += f"\n다음 정비 예정: {record.next_maintenance_date.strftime('%Y-%m-%d')}"
        
        message += "\n\n차량을 인수하실 수 있습니다."
        
        try:
            self.notification_service.create_notification(
                title=title,
                message=message.strip(),
                notification_type=NotificationType.MAINTENANCE_UPDATE,
                priority="MEDIUM",
                channels=[NotificationChannel.SMS, NotificationChannel.PUSH],
                metadata={
                    'maintenance_id': maintenance_id,
                    'vehicle_id': record.vehicle_id,
                    'vehicle_plate': record.vehicle.plate_number,
                    'total_cost': float(record.total_cost),
                    'status': 'completed'
                }
            )
            
            logger.info(f"정비 완료 알림 발송: {record.maintenance_number}")
            
        except Exception as e:
            logger.error(f"정비 완료 알림 발송 실패: error={e}")
    
    def notify_parts_used(self, maintenance_id: int, parts_count: int, total_cost: float):
        """
        부품 사용 알림
        
        Args:
            maintenance_id: 정비 기록 ID
            parts_count: 사용 부품 수
            total_cost: 총 부품 비용
        """
        record = self.db.query(VehicleMaintenanceRecord).filter(
            VehicleMaintenanceRecord.id == maintenance_id
        ).first()
        
        if not record:
            return
        
        title = f"📦 부품 사용: {record.vehicle.plate_number}"
        message = f"""
정비에 부품이 사용되었습니다.

차량: {record.vehicle.plate_number}
정비 번호: {record.maintenance_number}
사용 부품: {parts_count}개
부품 비용: {total_cost:,.0f}원

재고가 자동 차감되었습니다.
        """.strip()
        
        try:
            self.notification_service.create_notification(
                title=title,
                message=message,
                notification_type=NotificationType.INVENTORY_UPDATE,
                priority="LOW",
                channels=[NotificationChannel.PUSH],
                metadata={
                    'maintenance_id': maintenance_id,
                    'vehicle_id': record.vehicle_id,
                    'parts_count': parts_count,
                    'total_cost': float(total_cost)
                }
            )
            
            logger.info(f"부품 사용 알림 발송: {record.maintenance_number}")
            
        except Exception as e:
            logger.error(f"부품 사용 알림 발송 실패: error={e}")
    
    def send_daily_maintenance_summary(self) -> Dict[str, Any]:
        """
        일일 정비 요약 알림
        
        Returns:
            요약 통계
        """
        today = date.today()
        
        # 오늘 예정된 정비
        scheduled_today = self.db.query(VehicleMaintenanceRecord).filter(
            and_(
                VehicleMaintenanceRecord.scheduled_date == today,
                VehicleMaintenanceRecord.status == MaintenanceStatus.SCHEDULED
            )
        ).count()
        
        # 진행중인 정비
        in_progress = self.db.query(VehicleMaintenanceRecord).filter(
            VehicleMaintenanceRecord.status == MaintenanceStatus.IN_PROGRESS
        ).count()
        
        # 오늘 완료된 정비
        completed_today = self.db.query(VehicleMaintenanceRecord).filter(
            and_(
                VehicleMaintenanceRecord.completed_at >= datetime.combine(today, datetime.min.time()),
                VehicleMaintenanceRecord.status == MaintenanceStatus.COMPLETED
            )
        ).count()
        
        # 연체 스케줄
        overdue = self.db.query(MaintenanceSchedule).filter(
            and_(
                MaintenanceSchedule.is_active == True,
                MaintenanceSchedule.is_overdue == True
            )
        ).count()
        
        # 재고 부족
        low_stock = self.db.query(VehiclePart).filter(
            and_(
                VehiclePart.is_active == True,
                VehiclePart.quantity_in_stock <= VehiclePart.minimum_stock
            )
        ).count()
        
        title = f"📊 일일 정비 현황: {today.strftime('%Y-%m-%d')}"
        message = f"""
오늘의 정비 현황입니다.

예정된 정비: {scheduled_today}건
진행중: {in_progress}건
완료: {completed_today}건
연체: {overdue}건
재고 부족: {low_stock}개 품목

정비 관리 시스템을 확인해 주세요.
        """.strip()
        
        summary = {
            'date': today.isoformat(),
            'scheduled_today': scheduled_today,
            'in_progress': in_progress,
            'completed_today': completed_today,
            'overdue': overdue,
            'low_stock': low_stock
        }
        
        try:
            self.notification_service.create_notification(
                title=title,
                message=message,
                notification_type=NotificationType.SYSTEM,
                priority="LOW",
                channels=[NotificationChannel.EMAIL],
                metadata=summary
            )
            
            logger.info(f"일일 요약 알림 발송: {summary}")
            
        except Exception as e:
            logger.error(f"일일 요약 알림 발송 실패: error={e}")
        
        return summary
