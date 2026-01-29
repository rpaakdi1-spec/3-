import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional


class ExcelTemplateService:
    """
    Service for creating and managing Excel templates
    
    This service provides a centralized way to manage Excel templates.
    When you add a new field to a model, update the corresponding COLUMN_MAPPINGS
    and the template will be automatically updated.
    """
    
    TEMPLATES_DIR = Path(__file__).parent.parent.parent / "data" / "templates"
    
    # Column mappings for each entity type
    # Format: "Korean Header": (field_name, example_value, default_value)
    COLUMN_MAPPINGS = {
        "clients": {
            "거래처코드": ("code", "예시-0001", ""),
            "거래처명": ("name", "(주)서울냉동", ""),
            "구분": ("client_type", "상차", ""),
            "주소": ("address", "서울특별시 송파구 문정동 123", ""),
            "상세주소": ("address_detail", "1층", ""),
            "상차가능시작": ("pickup_start_time", "09:00", "09:00"),
            "상차가능종료": ("pickup_end_time", "17:00", "17:00"),
            "하차가능시작": ("delivery_start_time", "09:00", "09:00"),
            "하차가능종료": ("delivery_end_time", "17:00", "17:00"),
            "지게차운전능력": ("forklift_operator_available", "Y", "Y"),
            "상하차소요시간(분)": ("loading_time_minutes", 30, 30),
            "담당자명": ("contact_person", "홍길동", ""),
            "전화번호": ("phone", "02-1234-5678", ""),
            "특이사항": ("notes", "주차공간 협소", ""),
        },
        "orders": {
            "주문번호": ("order_number", "예시-ORD-001", ""),
            "주문일자": ("order_date", "2026-01-29", "2026-01-29"),
            "온도대": ("temperature_zone", "냉동", ""),
            "상차거래처코드": ("pickup_client_code", "CUST-0001", ""),
            "하차거래처코드": ("delivery_client_code", "CUST-0002", ""),
            "팔레트수": ("pallet_count", 10, 10),
            "용적(CBM)": ("volume_cbm", 15.0, 15.0),
            "품목명": ("product_name", "냉동식품", ""),
            "품목코드": ("product_code", "PROD-001", ""),
            "상차시작시간": ("pickup_start_time", "09:00", "09:00"),
            "상차종료시간": ("pickup_end_time", "12:00", "12:00"),
            "하차시작시간": ("delivery_start_time", "14:00", "14:00"),
            "하차종료시간": ("delivery_end_time", "17:00", "17:00"),
            "희망배송일": ("requested_delivery_date", "2026-01-29", "2026-01-29"),
            "우선순위": ("priority", 5, 5),
            "지게차필요": ("requires_forklift", "Y", "Y"),
            "적재가능": ("is_stackable", "Y", "Y"),
            "특이사항": ("notes", "깨지기 쉬움", ""),
        },
        "vehicles": {
            "차량코드": ("code", "예시-V001", ""),
            "차량번호": ("plate_number", "12가3456", ""),
            "차량타입": ("vehicle_type", "냉동", ""),
            "UVIS단말기ID": ("uvis_device_id", "UVIS-DVC-12345", ""),
            "최대팔레트": ("max_pallets", 20, 20),
            "최대중량(kg)": ("max_weight_kg", 5000, 5000),
            "최대용적(CBM)": ("max_volume_cbm", 30.0, 30.0),
            "지게차운전능력": ("forklift_operator_available", "Y", "Y"),
            "톤수": ("tonnage", 5.0, 5.0),
            "적재함길이(m)": ("length_m", 6.0, 6.0),
            "적재함너비(m)": ("width_m", 2.4, 2.4),
            "적재함높이(m)": ("height_m", 2.5, 2.5),
            "최저온도": ("min_temp_celsius", -25, -25),
            "최고온도": ("max_temp_celsius", -18, -18),
            "연비(km/L)": ("fuel_efficiency_km_per_liter", 5.0, 5.0),
            "리터당연료비": ("fuel_cost_per_liter", 1500, 1500),
            "차량상태": ("status", "운행가능", "운행가능"),
            "차고지주소": ("garage_address", "서울특별시 강서구", ""),
            "특이사항": ("notes", "", ""),
        },
        "drivers": {
            "기사코드": ("code", "DRV-001", ""),
            "기사명": ("name", "김기사", ""),
            "전화번호": ("phone", "010-1234-5678", ""),
            "비상연락처": ("emergency_contact", "02-123-4567", ""),
            "근무시작시간": ("work_start_time", "08:00", "08:00"),
            "근무종료시간": ("work_end_time", "18:00", "18:00"),
            "최대근무시간": ("max_work_hours", 10, 10),
            "운전면허번호": ("license_number", "12-34-567890-12", ""),
            "면허종류": ("license_type", "1종 대형", ""),
            "특이사항": ("notes", "", ""),
        }
    }
    
    @classmethod
    def ensure_templates_dir(cls):
        """Ensure templates directory exists"""
        cls.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_korean_to_field_mapping(cls, entity_type: str) -> Dict[str, str]:
        """
        Get Korean header to field name mapping for a given entity type
        
        Args:
            entity_type: One of 'clients', 'orders', 'vehicles', 'drivers'
            
        Returns:
            Dictionary mapping Korean headers to field names
        """
        if entity_type not in cls.COLUMN_MAPPINGS:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        return {
            korean_header: field_info[0]
            for korean_header, field_info in cls.COLUMN_MAPPINGS[entity_type].items()
        }
    
    @classmethod
    def create_template(
        cls,
        entity_type: str,
        sheet_name: str,
        num_example_rows: int = 1,
        num_empty_rows: int = 3
    ) -> Path:
        """
        Create an Excel template dynamically from column mappings
        
        Args:
            entity_type: One of 'clients', 'orders', 'vehicles', 'drivers'
            sheet_name: Name of the Excel sheet
            num_example_rows: Number of example rows with sample data
            num_empty_rows: Number of empty rows for user input
            
        Returns:
            Path to created template file
        """
        cls.ensure_templates_dir()
        
        if entity_type not in cls.COLUMN_MAPPINGS:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        mappings = cls.COLUMN_MAPPINGS[entity_type]
        
        # Build data dictionary
        data = {}
        for korean_header, (field_name, example_value, default_value) in mappings.items():
            column_data = []
            
            # Add example rows
            for i in range(num_example_rows):
                column_data.append(example_value)
            
            # Add empty rows (use default value if available)
            for i in range(num_empty_rows):
                column_data.append(default_value if default_value != "" else "")
            
            data[korean_header] = column_data
        
        df = pd.DataFrame(data)
        
        template_path = cls.TEMPLATES_DIR / f"{entity_type}_template.xlsx"
        
        # Create Excel with formatting
        with pd.ExcelWriter(template_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            
            # Adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return template_path
    
    @classmethod
    def create_clients_template(cls) -> Path:
        """Create Excel template for client data upload"""
        return cls.create_template("clients", "거래처")
    
    @classmethod
    def create_orders_template(cls) -> Path:
        """Create Excel template for order data upload"""
        return cls.create_template("orders", "주문")
    
    @classmethod
    def create_vehicles_template(cls) -> Path:
        """Create Excel template for vehicle data upload"""
        return cls.create_template("vehicles", "차량")
    
    @classmethod
    def create_drivers_template(cls) -> Path:
        """Create Excel template for driver data upload"""
        return cls.create_template("drivers", "기사")
    
    @classmethod
    def create_all_templates(cls) -> Dict[str, Path]:
        """
        Create all Excel templates
        
        Returns:
            Dictionary mapping entity types to template file paths
        """
        return {
            "clients": cls.create_clients_template(),
            "orders": cls.create_orders_template(),
            "vehicles": cls.create_vehicles_template(),
            "drivers": cls.create_drivers_template(),
        }
    
    @classmethod
    def get_template_info(cls, entity_type: str) -> Dict[str, Any]:
        """
        Get information about a template
        
        Args:
            entity_type: One of 'clients', 'orders', 'vehicles', 'drivers'
            
        Returns:
            Dictionary containing template information
        """
        if entity_type not in cls.COLUMN_MAPPINGS:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        mappings = cls.COLUMN_MAPPINGS[entity_type]
        
        return {
            "entity_type": entity_type,
            "num_columns": len(mappings),
            "columns": [
                {
                    "korean_header": korean_header,
                    "field_name": field_info[0],
                    "example_value": field_info[1],
                    "default_value": field_info[2]
                }
                for korean_header, field_info in mappings.items()
            ]
        }
