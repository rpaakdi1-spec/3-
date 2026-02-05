"""
Recurring Order Generator Service
정기 주문 자동 생성 서비스
"""
from datetime import date, datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from loguru import logger

from app.models.recurring_order import RecurringOrder
from app.models.order import Order, OrderStatus
from app.models.client import Client


class RecurringOrderGeneratorService:
    """정기 주문 자동 생성 서비스"""
    
    @staticmethod
    def generate_orders_for_date(db: Session, target_date: date = None) -> Dict[str, Any]:
        """특정 날짜의 정기 주문들을 실제 주문으로 생성
        
        Args:
            db: Database session
            target_date: 생성할 날짜 (기본값: 오늘)
            
        Returns:
            {
                'date': 생성 날짜,
                'generated': 생성된 주문 수,
                'failed': 실패한 주문 수,
                'orders': 생성된 주문 ID 목록,
                'errors': 에러 메시지 목록
            }
        """
        if target_date is None:
            target_date = date.today()
        
        logger.info(f"🔄 Starting recurring order generation for {target_date}")
        
        # 활성화된 모든 정기 주문 조회
        recurring_orders = db.query(RecurringOrder).filter(
            RecurringOrder.is_active == True
        ).all()
        
        logger.info(f"📋 Found {len(recurring_orders)} active recurring orders")
        
        generated_orders = []
        failed_orders = []
        errors = []
        
        for recurring_order in recurring_orders:
            try:
                # 오늘 생성해야 하는지 확인
                if not recurring_order.should_generate_today(target_date):
                    logger.debug(f"⏭️  Skipping recurring order {recurring_order.id} ({recurring_order.name}) - not scheduled for today")
                    continue
                
                logger.info(f"✅ Generating order from recurring order {recurring_order.id} ({recurring_order.name})")
                
                # 주문 생성
                order = RecurringOrderGeneratorService._create_order_from_recurring(
                    db, recurring_order, target_date
                )
                
                # 마지막 생성일 업데이트
                recurring_order.last_generated_date = target_date
                
                db.add(order)
                db.commit()
                db.refresh(order)
                
                generated_orders.append(order.id)
                logger.info(f"✅ Created order {order.order_number} from recurring order {recurring_order.id}")
                
            except Exception as e:
                error_msg = f"Failed to generate order from recurring order {recurring_order.id}: {str(e)}"
                logger.error(f"❌ {error_msg}")
                errors.append(error_msg)
                failed_orders.append(recurring_order.id)
                db.rollback()
                continue
        
        # 최종 커밋
        try:
            db.commit()
        except Exception as e:
            logger.error(f"❌ Failed to commit recurring order updates: {e}")
            db.rollback()
        
        result = {
            'date': str(target_date),
            'generated': len(generated_orders),
            'failed': len(failed_orders),
            'orders': generated_orders,
            'errors': errors
        }
        
        logger.info(f"✅ Recurring order generation complete: {result['generated']} created, {result['failed']} failed")
        
        return result
    
    @staticmethod
    def _create_order_from_recurring(
        db: Session,
        recurring_order: RecurringOrder,
        order_date: date
    ) -> Order:
        """정기 주문에서 실제 주문 생성
        
        Args:
            db: Database session
            recurring_order: 정기 주문
            order_date: 주문 날짜
            
        Returns:
            생성된 Order 객체
        """
        # 고유한 주문번호 생성 (정기주문ID-날짜-순번)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        order_number = f"REC-{recurring_order.id}-{timestamp}"
        
        # 거래처명 조회 (존재하는 경우)
        pickup_client_name = None
        delivery_client_name = None
        
        if recurring_order.pickup_client_id:
            pickup_client = db.query(Client).filter(
                Client.id == recurring_order.pickup_client_id
            ).first()
            if pickup_client:
                pickup_client_name = pickup_client.name
        
        if recurring_order.delivery_client_id:
            delivery_client = db.query(Client).filter(
                Client.id == recurring_order.delivery_client_id
            ).first()
            if delivery_client:
                delivery_client_name = delivery_client.name
        
        # 주문 생성
        order = Order(
            order_number=order_number,
            order_date=order_date,
            temperature_zone=recurring_order.temperature_zone,
            
            # 거래처 정보
            pickup_client_id=recurring_order.pickup_client_id,
            delivery_client_id=recurring_order.delivery_client_id,
            pickup_address=recurring_order.pickup_address,
            pickup_address_detail=recurring_order.pickup_address_detail,
            delivery_address=recurring_order.delivery_address,
            delivery_address_detail=recurring_order.delivery_address_detail,
            
            # 물품 정보
            pallet_count=recurring_order.pallet_count,
            weight_kg=recurring_order.weight_kg or 0,
            volume_cbm=recurring_order.volume_cbm or 0,
            product_name=recurring_order.product_name,
            product_code=recurring_order.product_code,
            
            # 시간 정보
            pickup_start_time=recurring_order.pickup_start_time,
            pickup_end_time=recurring_order.pickup_end_time,
            delivery_start_time=recurring_order.delivery_start_time,
            delivery_end_time=recurring_order.delivery_end_time,
            
            # 기타
            priority=recurring_order.priority,
            requires_forklift=recurring_order.requires_forklift,
            is_stackable=recurring_order.is_stackable,
            notes=f"[정기주문 자동생성] {recurring_order.name}\n{recurring_order.notes or ''}",
            
            # 상태
            status=OrderStatus.PENDING,
            
            # 반복 주문 정보
            recurring_type=recurring_order.frequency.value,  # 반복 유형 기록
        )
        
        return order
    
    @staticmethod
    def preview_generation(db: Session, target_date: date = None) -> Dict[str, Any]:
        """정기 주문 생성 미리보기 (실제 생성하지 않음)
        
        Args:
            db: Database session
            target_date: 확인할 날짜 (기본값: 오늘)
            
        Returns:
            {
                'date': 확인 날짜,
                'count': 생성될 주문 수,
                'recurring_orders': 생성될 정기 주문 목록
            }
        """
        if target_date is None:
            target_date = date.today()
        
        # 활성화된 모든 정기 주문 조회
        recurring_orders = db.query(RecurringOrder).filter(
            RecurringOrder.is_active == True
        ).all()
        
        scheduled_orders = []
        
        for recurring_order in recurring_orders:
            if recurring_order.should_generate_today(target_date):
                scheduled_orders.append({
                    'id': recurring_order.id,
                    'name': recurring_order.name,
                    'frequency': recurring_order.frequency.value,
                    'pickup_address': recurring_order.pickup_address,
                    'delivery_address': recurring_order.delivery_address,
                    'pallet_count': recurring_order.pallet_count,
                    'temperature_zone': recurring_order.temperature_zone.value
                })
        
        return {
            'date': str(target_date),
            'count': len(scheduled_orders),
            'recurring_orders': scheduled_orders
        }
