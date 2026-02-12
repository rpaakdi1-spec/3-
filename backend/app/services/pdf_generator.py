"""
PDF 생성 서비스
WeasyPrint를 사용하여 HTML 템플릿을 PDF로 변환
"""

from io import BytesIO
from pathlib import Path
from typing import Dict, Any, Optional
import base64
from datetime import datetime

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
except ImportError:
    # 개발 환경에서 weasyprint가 없을 경우 대체
    HTML = None
    CSS = None
    FontConfiguration = None

from jinja2 import Environment, FileSystemLoader
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager


class PDFGenerator:
    """PDF 리포트 생성기"""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "templates" / "reports"
        self.font_dir = Path(__file__).parent.parent / "static" / "fonts"
        self.jinja_env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        
        # 한글 폰트 설정 (matplotlib용)
        self._setup_korean_font()
    
    def _setup_korean_font(self):
        """
        한글 폰트 설정
        """
        # 시스템 폰트 경로 확인
        font_paths = [
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
            "/usr/share/fonts/nanum/NanumGothic.ttf",
            str(self.font_dir / "NanumGothic.ttf"),
        ]
        
        for font_path in font_paths:
            if Path(font_path).exists():
                font_manager.fontManager.addfont(font_path)
                plt.rcParams['font.family'] = 'NanumGothic'
                plt.rcParams['axes.unicode_minus'] = False
                break
    
    def generate_chart_image(self, chart_data: Dict[str, Any], chart_type: str = "line") -> str:
        """
        차트 이미지 생성 (Base64 인코딩)
        
        Args:
            chart_data: 차트 데이터 (labels, values)
            chart_type: 차트 종류 (line, bar, pie)
        
        Returns:
            Base64 인코딩된 PNG 이미지
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if chart_type == "line":
            ax.plot(chart_data.get("labels", []), chart_data.get("values", []), marker='o')
            ax.set_xlabel(chart_data.get("xlabel", ""))
            ax.set_ylabel(chart_data.get("ylabel", ""))
            ax.set_title(chart_data.get("title", ""))
            ax.grid(True, alpha=0.3)
        
        elif chart_type == "bar":
            ax.bar(chart_data.get("labels", []), chart_data.get("values", []))
            ax.set_xlabel(chart_data.get("xlabel", ""))
            ax.set_ylabel(chart_data.get("ylabel", ""))
            ax.set_title(chart_data.get("title", ""))
            ax.grid(True, alpha=0.3, axis='y')
        
        elif chart_type == "pie":
            ax.pie(
                chart_data.get("values", []),
                labels=chart_data.get("labels", []),
                autopct='%1.1f%%',
                startangle=90
            )
            ax.set_title(chart_data.get("title", ""))
        
        # 이미지를 BytesIO에 저장
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        # Base64 인코딩
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return f"data:image/png;base64,{image_base64}"
    
    def generate_pdf_from_html(
        self,
        template_name: str,
        context: Dict[str, Any],
        custom_css: Optional[str] = None
    ) -> bytes:
        """
        HTML 템플릿을 PDF로 변환
        
        Args:
            template_name: 템플릿 파일명 (예: "financial_dashboard.html")
            context: 템플릿 변수
            custom_css: 커스텀 CSS (옵션)
        
        Returns:
            PDF 바이너리 데이터
        """
        if HTML is None:
            raise ImportError("WeasyPrint is not installed. Please install it: pip install weasyprint")
        
        # Jinja2 템플릿 렌더링
        template = self.jinja_env.get_template(template_name)
        html_content = template.render(**context)
        
        # CSS 설정
        font_config = FontConfiguration()
        css_list = []
        
        if custom_css:
            css_list.append(CSS(string=custom_css, font_config=font_config))
        
        # HTML → PDF 변환
        html = HTML(string=html_content)
        pdf_bytes = html.write_pdf(stylesheets=css_list, font_config=font_config)
        
        return pdf_bytes
    
    def generate_financial_dashboard_pdf(
        self,
        summary: Dict[str, Any],
        monthly_trends: list,
        top_clients: list,
        start_date: str,
        end_date: str
    ) -> bytes:
        """
        재무 대시보드 PDF 생성
        
        Args:
            summary: 재무 요약 (14개 지표)
            monthly_trends: 월별 추이 데이터
            top_clients: Top 10 고객 목록
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
        
        Returns:
            PDF 바이너리 데이터
        """
        # 차트 생성
        chart_data = {
            "labels": [trend["month"] for trend in monthly_trends],
            "values": [trend["revenue"] for trend in monthly_trends],
            "xlabel": "월",
            "ylabel": "수익 (원)",
            "title": "월별 수익 추이"
        }
        chart_image = self.generate_chart_image(chart_data, "line")
        
        # 템플릿 컨텍스트
        context = {
            "title": "재무 대시보드 리포트",
            "start_date": start_date,
            "end_date": end_date,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": summary,
            "monthly_trends": monthly_trends,
            "top_clients": top_clients,
            "chart_image": chart_image,
        }
        
        # PDF 생성
        return self.generate_pdf_from_html("financial_dashboard.html", context)


# Singleton 인스턴스
pdf_generator = PDFGenerator()
