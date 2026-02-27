"""
데이터 마이그레이션 엔진
기존 시스템(Excel, CSV, 구 DB)에서 새 시스템으로 데이터를 안전하게 이전
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import logging
from sqlalchemy.orm import Session
from sqlalchemy import inspect
import json

from app.models.client import Client
from app.models.vehicle import Vehicle
from app.models.order import Order
from app.models.dispatch import Dispatch
from app.models.driver import Driver
from app.database import get_db

logger = logging.getLogger(__name__)


class MigrationResult:
    """마이그레이션 결과"""
    def __init__(self):
        self.total_records = 0
        self.success_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[str] = []
        
    def add_error(self, record_id: str, error: str):
        self.errors.append({
            "record_id": record_id,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        
    def add_warning(self, message: str):
        self.warnings.append(message)


class DataMigrationEngine:
    """데이터 마이그레이션 엔진"""
    
    def __init__(self, db: Session):
        self.db = db
        self.result = MigrationResult()
        
    # ========================================
    # 1. Excel 마이그레이션
    # ========================================
    
    def migrate_from_excel(
        self, 
        file_path: str,
        entity_type: str,
        sheet_name: Optional[str] = None,
        dry_run: bool = False
    ) -> MigrationResult:
        """
        Excel 파일에서 데이터 마이그레이션
        
        Args:
            file_path: Excel 파일 경로
            entity_type: 엔티티 타입 (clients, vehicles, orders, etc.)
            sheet_name: 시트 이름 (None이면 첫 번째 시트)
            dry_run: True면 실제 DB 저장 없이 검증만 수행
        """
        try:
            logger.info(f"Starting Excel migration from {file_path}")
            
            # Excel 파일 읽기
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            self.result.total_records = len(df)
            
            logger.info(f"Found {len(df)} records in Excel file")
            
            # 엔티티 타입별 마이그레이션
            if entity_type == "clients":
                self._migrate_clients_from_dataframe(df, dry_run)
            elif entity_type == "vehicles":
                self._migrate_vehicles_from_dataframe(df, dry_run)
            elif entity_type == "orders":
                self._migrate_orders_from_dataframe(df, dry_run)
            elif entity_type == "drivers":
                self._migrate_drivers_from_dataframe(df, dry_run)
            else:
                raise ValueError(f"Unsupported entity type: {entity_type}")
            
            if not dry_run:
                self.db.commit()
                logger.info("Migration committed to database")
            else:
                logger.info("Dry run completed - no changes committed")
                
            return self.result
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            self.db.rollback()
            raise
    
    def _migrate_clients_from_dataframe(self, df: pd.DataFrame, dry_run: bool):
        """클라이언트 데이터 마이그레이션"""
        required_columns = ['name', 'phone', 'address']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        for idx, row in df.iterrows():
            try:
                # 데이터 검증
                if pd.isna(row['name']) or not row['name'].strip():
                    self.result.add_error(str(idx), "Client name is empty")
                    self.result.failed_count += 1
                    continue
                
                # 중복 체크 (전화번호 기준)
                if not pd.isna(row.get('phone')):
                    existing = self.db.query(Client).filter(
                        Client.phone == row['phone']
                    ).first()
                    
                    if existing:
                        logger.warning(f"Client with phone {row['phone']} already exists, skipping")
                        self.result.skipped_count += 1
                        continue
                
                # 클라이언트 생성
                client = Client(
                    name=row['name'].strip(),
                    phone=row.get('phone', '').strip() if not pd.isna(row.get('phone')) else None,
                    address=row.get('address', '').strip() if not pd.isna(row.get('address')) else None,
                    address_detail=row.get('address_detail', '').strip() if not pd.isna(row.get('address_detail')) else None,
                    contact_person=row.get('contact_person') if not pd.isna(row.get('contact_person')) else None,
                    email=row.get('email') if not pd.isna(row.get('email')) else None,
                    business_number=row.get('business_number') if not pd.isna(row.get('business_number')) else None,
                    client_type=row.get('client_type', 'REGULAR') if not pd.isna(row.get('client_type')) else 'REGULAR',
                    notes=row.get('notes') if not pd.isna(row.get('notes')) else None
                )
                
                if not dry_run:
                    self.db.add(client)
                
                self.result.success_count += 1
                logger.debug(f"Migrated client: {client.name}")
                
            except Exception as e:
                logger.error(f"Failed to migrate client at row {idx}: {str(e)}")
                self.result.add_error(str(idx), str(e))
                self.result.failed_count += 1
    
    def _migrate_vehicles_from_dataframe(self, df: pd.DataFrame, dry_run: bool):
        """차량 데이터 마이그레이션"""
        required_columns = ['license_plate', 'vehicle_type']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        for idx, row in df.iterrows():
            try:
                # 데이터 검증
                if pd.isna(row['license_plate']) or not row['license_plate'].strip():
                    self.result.add_error(str(idx), "License plate is empty")
                    self.result.failed_count += 1
                    continue
                
                # 중복 체크
                existing = self.db.query(Vehicle).filter(
                    Vehicle.license_plate == row['license_plate']
                ).first()
                
                if existing:
                    logger.warning(f"Vehicle {row['license_plate']} already exists, skipping")
                    self.result.skipped_count += 1
                    continue
                
                # 차량 생성
                vehicle = Vehicle(
                    license_plate=row['license_plate'].strip(),
                    vehicle_type=row.get('vehicle_type', 'TRUCK') if not pd.isna(row.get('vehicle_type')) else 'TRUCK',
                    model=row.get('model') if not pd.isna(row.get('model')) else None,
                    year=int(row['year']) if not pd.isna(row.get('year')) else None,
                    capacity_kg=float(row['capacity_kg']) if not pd.isna(row.get('capacity_kg')) else None,
                    capacity_cbm=float(row['capacity_cbm']) if not pd.isna(row.get('capacity_cbm')) else None,
                    temperature_type=row.get('temperature_type', 'FROZEN') if not pd.isna(row.get('temperature_type')) else 'FROZEN',
                    status=row.get('status', 'available') if not pd.isna(row.get('status')) else 'available',
                    notes=row.get('notes') if not pd.isna(row.get('notes')) else None
                )
                
                if not dry_run:
                    self.db.add(vehicle)
                
                self.result.success_count += 1
                logger.debug(f"Migrated vehicle: {vehicle.license_plate}")
                
            except Exception as e:
                logger.error(f"Failed to migrate vehicle at row {idx}: {str(e)}")
                self.result.add_error(str(idx), str(e))
                self.result.failed_count += 1
    
    def _migrate_orders_from_dataframe(self, df: pd.DataFrame, dry_run: bool):
        """주문 데이터 마이그레이션"""
        required_columns = ['client_name', 'pickup_address', 'delivery_address']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        for idx, row in df.iterrows():
            try:
                # 클라이언트 찾기 (이름으로)
                client = self.db.query(Client).filter(
                    Client.name == row['client_name']
                ).first()
                
                if not client:
                    self.result.add_error(str(idx), f"Client not found: {row['client_name']}")
                    self.result.failed_count += 1
                    continue
                
                # 주문 생성
                order = Order(
                    client_id=client.id,
                    order_number=row.get('order_number') if not pd.isna(row.get('order_number')) else None,
                    pickup_address=row['pickup_address'].strip(),
                    delivery_address=row['delivery_address'].strip(),
                    pickup_datetime=pd.to_datetime(row['pickup_datetime']) if not pd.isna(row.get('pickup_datetime')) else None,
                    delivery_datetime=pd.to_datetime(row['delivery_datetime']) if not pd.isna(row.get('delivery_datetime')) else None,
                    weight_kg=float(row['weight_kg']) if not pd.isna(row.get('weight_kg')) else None,
                    volume_cbm=float(row['volume_cbm']) if not pd.isna(row.get('volume_cbm')) else None,
                    temperature_type=row.get('temperature_type', 'FROZEN') if not pd.isna(row.get('temperature_type')) else 'FROZEN',
                    status=row.get('status', '배차대기') if not pd.isna(row.get('status')) else '배차대기',
                    notes=row.get('notes') if not pd.isna(row.get('notes')) else None
                )
                
                if not dry_run:
                    self.db.add(order)
                
                self.result.success_count += 1
                logger.debug(f"Migrated order for client: {client.name}")
                
            except Exception as e:
                logger.error(f"Failed to migrate order at row {idx}: {str(e)}")
                self.result.add_error(str(idx), str(e))
                self.result.failed_count += 1
    
    def _migrate_drivers_from_dataframe(self, df: pd.DataFrame, dry_run: bool):
        """기사 데이터 마이그레이션"""
        required_columns = ['name', 'phone']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        for idx, row in df.iterrows():
            try:
                # 중복 체크
                existing = self.db.query(Driver).filter(
                    Driver.phone == row['phone']
                ).first()
                
                if existing:
                    logger.warning(f"Driver with phone {row['phone']} already exists, skipping")
                    self.result.skipped_count += 1
                    continue
                
                # 기사 생성
                driver = Driver(
                    name=row['name'].strip(),
                    phone=row['phone'].strip(),
                    license_number=row.get('license_number') if not pd.isna(row.get('license_number')) else None,
                    license_type=row.get('license_type') if not pd.isna(row.get('license_type')) else None,
                    status=row.get('status', 'available') if not pd.isna(row.get('status')) else 'available',
                    notes=row.get('notes') if not pd.isna(row.get('notes')) else None
                )
                
                if not dry_run:
                    self.db.add(driver)
                
                self.result.success_count += 1
                logger.debug(f"Migrated driver: {driver.name}")
                
            except Exception as e:
                logger.error(f"Failed to migrate driver at row {idx}: {str(e)}")
                self.result.add_error(str(idx), str(e))
                self.result.failed_count += 1
    
    # ========================================
    # 2. CSV 마이그레이션
    # ========================================
    
    def migrate_from_csv(
        self,
        file_path: str,
        entity_type: str,
        encoding: str = 'utf-8',
        dry_run: bool = False
    ) -> MigrationResult:
        """CSV 파일에서 데이터 마이그레이션"""
        try:
            logger.info(f"Starting CSV migration from {file_path}")
            
            # CSV 파일 읽기
            df = pd.read_csv(file_path, encoding=encoding)
            self.result.total_records = len(df)
            
            logger.info(f"Found {len(df)} records in CSV file")
            
            # Excel과 동일한 로직 사용
            if entity_type == "clients":
                self._migrate_clients_from_dataframe(df, dry_run)
            elif entity_type == "vehicles":
                self._migrate_vehicles_from_dataframe(df, dry_run)
            elif entity_type == "orders":
                self._migrate_orders_from_dataframe(df, dry_run)
            elif entity_type == "drivers":
                self._migrate_drivers_from_dataframe(df, dry_run)
            else:
                raise ValueError(f"Unsupported entity type: {entity_type}")
            
            if not dry_run:
                self.db.commit()
                logger.info("Migration committed to database")
            else:
                logger.info("Dry run completed - no changes committed")
                
            return self.result
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            self.db.rollback()
            raise
    
    # ========================================
    # 3. 마이그레이션 검증
    # ========================================
    
    def validate_migration(self) -> Dict[str, Any]:
        """마이그레이션 결과 검증"""
        validation_result = {
            "total_records": self.result.total_records,
            "success_count": self.result.success_count,
            "failed_count": self.result.failed_count,
            "skipped_count": self.result.skipped_count,
            "success_rate": (self.result.success_count / self.result.total_records * 100) if self.result.total_records > 0 else 0,
            "errors": self.result.errors,
            "warnings": self.result.warnings,
            "is_valid": self.result.failed_count == 0
        }
        
        return validation_result
    
    # ========================================
    # 4. 롤백
    # ========================================
    
    def rollback_migration(self, entity_type: str, batch_id: Optional[str] = None):
        """
        마이그레이션 롤백
        
        Args:
            entity_type: 롤백할 엔티티 타입
            batch_id: 특정 배치 ID (None이면 마지막 마이그레이션)
        """
        try:
            logger.info(f"Rolling back migration for {entity_type}")
            
            # TODO: 배치 ID 기반 롤백 구현
            # 현재는 기본 롤백만 지원
            
            self.db.rollback()
            logger.info("Rollback completed")
            
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            raise


# ========================================
# 유틸리티 함수
# ========================================

def create_excel_template(entity_type: str, output_path: str):
    """
    마이그레이션용 Excel 템플릿 생성
    
    Args:
        entity_type: 엔티티 타입
        output_path: 출력 파일 경로
    """
    templates = {
        "clients": {
            "columns": [
                "name", "phone", "address", "address_detail", 
                "contact_person", "email", "business_number", 
                "client_type", "notes"
            ],
            "sample_data": [{
                "name": "샘플 고객사",
                "phone": "02-1234-5678",
                "address": "서울시 강남구 테헤란로 123",
                "address_detail": "ABC빌딩 5층",
                "contact_person": "홍길동",
                "email": "sample@example.com",
                "business_number": "123-45-67890",
                "client_type": "REGULAR",
                "notes": "메모사항"
            }]
        },
        "vehicles": {
            "columns": [
                "license_plate", "vehicle_type", "model", "year",
                "capacity_kg", "capacity_cbm", "temperature_type",
                "status", "notes"
            ],
            "sample_data": [{
                "license_plate": "12가3456",
                "vehicle_type": "TRUCK",
                "model": "현대 포터",
                "year": 2023,
                "capacity_kg": 1000,
                "capacity_cbm": 10,
                "temperature_type": "FROZEN",
                "status": "available",
                "notes": "메모사항"
            }]
        },
        "orders": {
            "columns": [
                "client_name", "order_number", "pickup_address", 
                "delivery_address", "pickup_datetime", "delivery_datetime",
                "weight_kg", "volume_cbm", "temperature_type", 
                "status", "notes"
            ],
            "sample_data": [{
                "client_name": "샘플 고객사",
                "order_number": "ORD-2024-001",
                "pickup_address": "서울시 강남구 테헤란로 123",
                "delivery_address": "서울시 송파구 올림픽로 456",
                "pickup_datetime": "2024-01-01 09:00:00",
                "delivery_datetime": "2024-01-01 11:00:00",
                "weight_kg": 500,
                "volume_cbm": 5,
                "temperature_type": "FROZEN",
                "status": "배차대기",
                "notes": "메모사항"
            }]
        },
        "drivers": {
            "columns": [
                "name", "phone", "license_number", "license_type",
                "status", "notes"
            ],
            "sample_data": [{
                "name": "김기사",
                "phone": "010-1234-5678",
                "license_number": "12-34-567890-12",
                "license_type": "1종 보통",
                "status": "available",
                "notes": "메모사항"
            }]
        }
    }
    
    if entity_type not in templates:
        raise ValueError(f"Unsupported entity type: {entity_type}")
    
    template = templates[entity_type]
    df = pd.DataFrame(template["sample_data"], columns=template["columns"])
    df.to_excel(output_path, index=False)
    
    logger.info(f"Template created: {output_path}")
