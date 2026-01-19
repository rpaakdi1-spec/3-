import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from io import BytesIO
from sqlalchemy.orm import Session

from app.models.client import Client, ClientType
from app.models.vehicle import Vehicle, VehicleType, VehicleStatus
from app.models.order import Order, TemperatureZone, OrderStatus
from app.services.naver_map_service import NaverMapService
from loguru import logger


class ExcelUploadService:
    """Service for uploading data from Excel files"""
    
    @staticmethod
    def parse_client_excel(file_content: bytes) -> List[Dict[str, Any]]:
        """Parse client data from Excel file"""
        try:
            df = pd.read_excel(BytesIO(file_content))
            
            # Map Korean column names to model fields
            column_mapping = {
                "거래처코드": "code",
                "거래처명": "name",
                "구분": "client_type",
                "주소": "address",
                "상세주소": "address_detail",
                "상차가능시작": "pickup_start_time",
                "상차가능종료": "pickup_end_time",
                "하차가능시작": "delivery_start_time",
                "하차가능종료": "delivery_end_time",
                "지게차유무": "has_forklift",
                "상하차소요시간(분)": "loading_time_minutes",
                "담당자명": "contact_person",
                "전화번호": "phone",
                "특이사항": "notes",
            }
            
            df = df.rename(columns=column_mapping)
            
            # Filter out example rows and empty rows
            df = df[df['code'].notna()]  # Remove rows with empty code
            df = df[~df['code'].astype(str).str.startswith('예시-')]  # Remove example rows
            
            # Convert client_type
            df['client_type'] = df['client_type'].replace({
                '상차': ClientType.PICKUP,
                '하차': ClientType.DELIVERY,
                '양쪽': ClientType.BOTH
            })
            
            # Convert has_forklift
            df['has_forklift'] = df['has_forklift'].fillna('N').str.upper() == 'Y'
            
            # Fill defaults
            df['loading_time_minutes'] = df['loading_time_minutes'].fillna(30).astype(int)
            
            # Convert to list of dicts
            records = df.to_dict(orient='records')
            
            logger.info(f"Parsed {len(records)} client records from Excel")
            return records
            
        except Exception as e:
            logger.error(f"Error parsing client Excel: {e}")
            raise ValueError(f"엑셀 파일 파싱 오류: {str(e)}")
    
    @staticmethod
    async def upload_clients(
        db: Session,
        file_content: bytes,
        auto_geocode: bool = True
    ) -> Dict[str, Any]:
        """Upload clients from Excel file"""
        records = ExcelUploadService.parse_client_excel(file_content)
        
        created = []
        errors = []
        
        for idx, record in enumerate(records):
            try:
                # Check if client already exists
                existing = db.query(Client).filter(Client.code == record['code']).first()
                if existing:
                    errors.append({
                        "row": idx + 2,  # Excel row (header + 1)
                        "code": record['code'],
                        "error": "이미 존재하는 거래처 코드"
                    })
                    continue
                
                # Create client
                client = Client(**record)
                db.add(client)
                db.flush()
                
                # Auto geocode if enabled
                if auto_geocode and record.get('address'):
                    naver_service = NaverMapService()
                    lat, lon, error = await naver_service.geocode_address(record['address'])
                    
                    if lat and lon:
                        client.latitude = lat
                        client.longitude = lon
                        client.geocoded = True
                    else:
                        client.geocode_error = error
                
                created.append(client.code)
                
            except Exception as e:
                errors.append({
                    "row": idx + 2,
                    "code": record.get('code', 'Unknown'),
                    "error": str(e)
                })
        
        db.commit()
        
        return {
            "total": len(records),
            "created": len(created),
            "failed": len(errors),
            "created_codes": created,
            "errors": errors
        }
    
    @staticmethod
    def parse_vehicle_excel(file_content: bytes) -> List[Dict[str, Any]]:
        """Parse vehicle data from Excel file"""
        try:
            df = pd.read_excel(BytesIO(file_content))
            
            # Map Korean column names
            column_mapping = {
                "차량코드": "code",
                "차량번호": "plate_number",
                "차량타입": "vehicle_type",
                "UVIS단말기ID": "uvis_device_id",
                "최대팔레트": "max_pallets",
                "최대중량(kg)": "max_weight_kg",
                "최대용적(CBM)": "max_volume_cbm",
                "톤수": "tonnage",
                "적재함길이(m)": "length_m",
                "적재함너비(m)": "width_m",
                "적재함높이(m)": "height_m",
                "최저온도": "min_temp_celsius",
                "최고온도": "max_temp_celsius",
                "연비(km/L)": "fuel_efficiency_km_per_liter",
                "리터당연료비": "fuel_cost_per_liter",
                "차량상태": "status",
                "차고지주소": "garage_address",
                "특이사항": "notes",
            }
            
            df = df.rename(columns=column_mapping)
            
            # Filter out example rows and empty rows
            df = df[df['code'].notna()]  # Remove rows with empty code
            df = df[~df['code'].astype(str).str.contains('예시-|TRUCK-001', regex=True)]  # Remove example rows
            
            # Convert vehicle_type
            df['vehicle_type'] = df['vehicle_type'].replace({
                '냉동': VehicleType.FROZEN,
                '냉장': VehicleType.REFRIGERATED,
                '겸용': VehicleType.DUAL,
                '상온': VehicleType.AMBIENT
            })
            
            # Convert status
            status_mapping = {
                '운행가능': VehicleStatus.AVAILABLE,
                '운행중': VehicleStatus.IN_USE,
                '정비중': VehicleStatus.MAINTENANCE,
                '운행불가': VehicleStatus.OUT_OF_SERVICE
            }
            df['status'] = df['status'].fillna('운행가능').replace(status_mapping)
            
            # Set UVIS enabled if device ID exists
            df['uvis_enabled'] = df['uvis_device_id'].notna()
            
            records = df.to_dict(orient='records')
            
            logger.info(f"Parsed {len(records)} vehicle records from Excel")
            return records
            
        except Exception as e:
            logger.error(f"Error parsing vehicle Excel: {e}")
            raise ValueError(f"엑셀 파일 파싱 오류: {str(e)}")
    
    @staticmethod
    def upload_vehicles(db: Session, file_content: bytes) -> Dict[str, Any]:
        """Upload vehicles from Excel file"""
        records = ExcelUploadService.parse_vehicle_excel(file_content)
        
        created = []
        errors = []
        
        for idx, record in enumerate(records):
            try:
                # Check if vehicle already exists
                existing = db.query(Vehicle).filter(Vehicle.code == record['code']).first()
                if existing:
                    errors.append({
                        "row": idx + 2,
                        "code": record['code'],
                        "error": "이미 존재하는 차량 코드"
                    })
                    continue
                
                vehicle = Vehicle(**record)
                db.add(vehicle)
                created.append(vehicle.code)
                
            except Exception as e:
                errors.append({
                    "row": idx + 2,
                    "code": record.get('code', 'Unknown'),
                    "error": str(e)
                })
        
        db.commit()
        
        return {
            "total": len(records),
            "created": len(created),
            "failed": len(errors),
            "created_codes": created,
            "errors": errors
        }
    
    @staticmethod
    def parse_order_excel(file_content: bytes) -> List[Dict[str, Any]]:
        """Parse order data from Excel file"""
        try:
            df = pd.read_excel(BytesIO(file_content))
            
            # Map Korean column names
            column_mapping = {
                "주문번호": "order_number",
                "주문일자": "order_date",
                "온도대": "temperature_zone",
                "상차거래처코드": "pickup_client_code",
                "하차거래처코드": "delivery_client_code",
                "팔레트수": "pallet_count",
                "중량(kg)": "weight_kg",
                "용적(CBM)": "volume_cbm",
                "품목명": "product_name",
                "품목코드": "product_code",
                "상차시작시간": "pickup_start_time",
                "상차종료시간": "pickup_end_time",
                "하차시작시간": "delivery_start_time",
                "하차종료시간": "delivery_end_time",
                "희망배송일": "requested_delivery_date",
                "우선순위": "priority",
                "지게차필요": "requires_forklift",
                "적재가능": "is_stackable",
                "특이사항": "notes",
            }
            
            df = df.rename(columns=column_mapping)
            
            # Filter out example rows and empty rows
            df = df[df['order_number'].notna()]  # Remove rows with empty order_number
            df = df[~df['order_number'].astype(str).str.contains('예시-|ORD-', regex=True)]  # Remove example rows
            
            # Convert dates
            df['order_date'] = pd.to_datetime(df['order_date']).dt.date
            if 'requested_delivery_date' in df.columns:
                df['requested_delivery_date'] = pd.to_datetime(df['requested_delivery_date'], errors='coerce').dt.date
            
            # Convert temperature_zone
            df['temperature_zone'] = df['temperature_zone'].replace({
                '냉동': TemperatureZone.FROZEN,
                '냉장': TemperatureZone.REFRIGERATED,
                '상온': TemperatureZone.AMBIENT
            })
            
            # Convert boolean fields
            df['requires_forklift'] = df['requires_forklift'].fillna('N').str.upper() == 'Y'
            df['is_stackable'] = df['is_stackable'].fillna('Y').str.upper() == 'Y'
            
            # Fill defaults
            df['priority'] = df['priority'].fillna(5).astype(int)
            
            records = df.to_dict(orient='records')
            
            logger.info(f"Parsed {len(records)} order records from Excel")
            return records
            
        except Exception as e:
            logger.error(f"Error parsing order Excel: {e}")
            raise ValueError(f"엑셀 파일 파싱 오류: {str(e)}")
    
    @staticmethod
    def upload_orders(db: Session, file_content: bytes) -> Dict[str, Any]:
        """Upload orders from Excel file"""
        records = ExcelUploadService.parse_order_excel(file_content)
        
        created = []
        errors = []
        
        for idx, record in enumerate(records):
            try:
                # Check if order already exists
                existing = db.query(Order).filter(Order.order_number == record['order_number']).first()
                if existing:
                    errors.append({
                        "row": idx + 2,
                        "order_number": record['order_number'],
                        "error": "이미 존재하는 주문번호"
                    })
                    continue
                
                # Find client IDs
                pickup_client = db.query(Client).filter(Client.code == record.pop('pickup_client_code')).first()
                delivery_client = db.query(Client).filter(Client.code == record.pop('delivery_client_code')).first()
                
                if not pickup_client:
                    errors.append({
                        "row": idx + 2,
                        "order_number": record['order_number'],
                        "error": f"상차 거래처를 찾을 수 없음"
                    })
                    continue
                
                if not delivery_client:
                    errors.append({
                        "row": idx + 2,
                        "order_number": record['order_number'],
                        "error": f"하차 거래처를 찾을 수 없음"
                    })
                    continue
                
                record['pickup_client_id'] = pickup_client.id
                record['delivery_client_id'] = delivery_client.id
                record['status'] = OrderStatus.PENDING
                
                order = Order(**record)
                db.add(order)
                created.append(order.order_number)
                
            except Exception as e:
                errors.append({
                    "row": idx + 2,
                    "order_number": record.get('order_number', 'Unknown'),
                    "error": str(e)
                })
        
        db.commit()
        
        return {
            "total": len(records),
            "created": len(created),
            "failed": len(errors),
            "created_codes": created,
            "errors": errors
        }
