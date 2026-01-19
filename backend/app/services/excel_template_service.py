import pandas as pd
from pathlib import Path
from typing import Optional


class ExcelTemplateService:
    """Service for creating and managing Excel templates"""
    
    TEMPLATES_DIR = Path(__file__).parent.parent.parent / "data" / "templates"
    
    @classmethod
    def ensure_templates_dir(cls):
        """Ensure templates directory exists"""
        cls.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def create_clients_template(cls) -> Path:
        """
        Create Excel template for client data upload
        
        Returns:
            Path to created template file
        """
        cls.ensure_templates_dir()
        
        # Header row with examples and empty rows for user to fill
        data = {
            "거래처코드": ["예시-0001", "", "", ""],
            "거래처명": ["(주)서울냉동", "", "", ""],
            "구분": ["상차", "", "", ""],
            "주소": ["서울특별시 송파구 문정동 123", "", "", ""],
            "상세주소": ["1층", "", "", ""],
            "상차가능시작": ["09:00", "09:00", "09:00", "09:00"],
            "상차가능종료": ["17:00", "17:00", "17:00", "17:00"],
            "하차가능시작": ["09:00", "09:00", "09:00", "09:00"],
            "하차가능종료": ["17:00", "17:00", "17:00", "17:00"],
            "지게차유무": ["Y", "Y", "Y", "Y"],
            "상하차소요시간(분)": [30, 30, 30, 30],
            "담당자명": ["홍길동", "", "", ""],
            "전화번호": ["02-1234-5678", "", "", ""],
            "특이사항": ["주차공간 협소", "", "", ""],
        }
        
        df = pd.DataFrame(data)
        
        template_path = cls.TEMPLATES_DIR / "clients_template.xlsx"
        
        # Create Excel with formatting
        with pd.ExcelWriter(template_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='거래처', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['거래처']
            
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
    def create_orders_template(cls) -> Path:
        """
        Create Excel template for order data upload
        
        Returns:
            Path to created template file
        """
        cls.ensure_templates_dir()
        
        # Sample data with Korean headers (example + empty rows for user to fill)
        data = {
            "주문번호": ["예시-ORD-001", "", "", ""],
            "주문일자": ["2026-01-19", "2026-01-19", "2026-01-19", "2026-01-19"],
            "온도대": ["냉동", "", "", ""],
            "상차거래처코드": ["CUST-0001", "", "", ""],
            "하차거래처코드": ["CUST-0002", "", "", ""],
            "팔레트수": [10, 10, 10, 10],
            "중량(kg)": [5000, 5000, 5000, 5000],
            "용적(CBM)": [15.0, 15.0, 15.0, 15.0],
            "품목명": ["냉동식품", "", "", ""],
            "품목코드": ["PROD-001", "", "", ""],
            "상차시작시간": ["09:00", "09:00", "09:00", "09:00"],
            "상차종료시간": ["12:00", "12:00", "12:00", "12:00"],
            "하차시작시간": ["14:00", "14:00", "14:00", "14:00"],
            "하차종료시간": ["17:00", "17:00", "17:00", "17:00"],
            "희망배송일": ["2026-01-19", "2026-01-19", "2026-01-19", "2026-01-19"],
            "우선순위": [5, 5, 5, 5],
            "지게차필요": ["Y", "Y", "Y", "Y"],
            "적재가능": ["Y", "Y", "Y", "Y"],
            "특이사항": ["깨지기 쉬움", "", "", ""],
        }
        
        df = pd.DataFrame(data)
        
        template_path = cls.TEMPLATES_DIR / "orders_template.xlsx"
        
        with pd.ExcelWriter(template_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='주문', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['주문']
            
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
    def create_vehicles_template(cls) -> Path:
        """
        Create Excel template for vehicle data upload
        
        Returns:
            Path to created template file
        """
        cls.ensure_templates_dir()
        
        # Sample data with Korean headers (example + empty rows for user to fill)
        data = {
            "차량코드": ["예시-V001", "", "", ""],
            "차량번호": ["12가3456", "", "", ""],
            "차량타입": ["냉동", "", "", ""],
            "UVIS단말기ID": ["UVIS-DVC-12345", "", "", ""],
            "최대팔레트": [20, 20, 20, 20],
            "최대중량(kg)": [5000, 5000, 5000, 5000],
            "최대용적(CBM)": [30.0, 30.0, 30.0, 30.0],
            "톤수": [5.0, 5.0, 5.0, 5.0],
            "적재함길이(m)": [6.0, 6.0, 6.0, 6.0],
            "적재함너비(m)": [2.4, 2.4, 2.4, 2.4],
            "적재함높이(m)": [2.5, 2.5, 2.5, 2.5],
            "최저온도": [-25, -25, -25, -25],
            "최고온도": [-18, -18, -18, -18],
            "연비(km/L)": [5.0, 5.0, 5.0, 5.0],
            "리터당연료비": [1500, 1500, 1500, 1500],
            "차량상태": ["운행가능", "운행가능", "운행가능", "운행가능"],
            "차고지주소": ["서울특별시 강서구", "", "", ""],
            "특이사항": ["", "", "", ""],
        }
        
        df = pd.DataFrame(data)
        
        template_path = cls.TEMPLATES_DIR / "vehicles_template.xlsx"
        
        with pd.ExcelWriter(template_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='차량', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['차량']
            
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
    def create_drivers_template(cls) -> Path:
        """
        Create Excel template for driver data upload
        
        Returns:
            Path to created template file
        """
        cls.ensure_templates_dir()
        
        # Sample data with Korean headers
        data = {
            "기사코드": ["DRV-001", "DRV-002"],
            "기사명": ["김기사", "이기사"],
            "전화번호": ["010-1234-5678", "010-9876-5432"],
            "비상연락처": ["02-123-4567", "031-987-6543"],
            "근무시작시간": ["08:00", "07:00"],
            "근무종료시간": ["18:00", "17:00"],
            "최대근무시간": [10, 10],
            "운전면허번호": ["12-34-567890-12", "98-76-543210-98"],
            "면허종류": ["1종 대형", "1종 대형"],
            "특이사항": ["", "야간운행 가능"],
        }
        
        df = pd.DataFrame(data)
        
        template_path = cls.TEMPLATES_DIR / "drivers_template.xlsx"
        
        with pd.ExcelWriter(template_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='기사', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['기사']
            
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
    def create_all_templates(cls):
        """Create all Excel templates"""
        cls.create_clients_template()
        cls.create_orders_template()
        cls.create_vehicles_template()
        cls.create_drivers_template()
        return {
            "clients": cls.TEMPLATES_DIR / "clients_template.xlsx",
            "orders": cls.TEMPLATES_DIR / "orders_template.xlsx",
            "vehicles": cls.TEMPLATES_DIR / "vehicles_template.xlsx",
            "drivers": cls.TEMPLATES_DIR / "drivers_template.xlsx",
        }
