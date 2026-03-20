"""
Driver Mileage PDF Report Service
운전자 주행거리 PDF 리포트 생성 서비스
"""
from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from io import BytesIO
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.models.driver_daily_mileage import DriverDailyMileage
from loguru import logger


class DriverMileagePDFService:
    """운전자 주행거리 PDF 생성 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # 한글 폰트 등록 시도 (없으면 기본 폰트 사용)
        try:
            # 나눔고딕 폰트 경로 (Docker 환경에서는 설치 필요)
            pdfmetrics.registerFont(TTFont('NanumGothic', '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'))
            self.font_name = 'NanumGothic'
            self.font_name_bold = 'NanumGothic'
        except:
            # 폰트 없으면 기본 폰트 사용
            self.font_name = 'Helvetica'
            self.font_name_bold = 'Helvetica-Bold'
            logger.warning("NanumGothic font not found, using Helvetica")
        
        # 스타일 정의
        self.styles = getSampleStyleSheet()
        
        # 제목 스타일
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontName=self.font_name_bold,
            fontSize=18,
            textColor=colors.HexColor('#1F4E78'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        # 부제목 스타일
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontName=self.font_name,
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
    
    def _create_summary_section(self, stats: Dict) -> List:
        """요약 섹션 생성"""
        elements = []
        
        # 요약 제목
        summary_title = Paragraph(
            "<b>Summary Statistics</b>",
            ParagraphStyle(
                'SummaryTitle',
                fontName=self.font_name_bold,
                fontSize=14,
                textColor=colors.HexColor('#1F4E78'),
                spaceAfter=10
            )
        )
        elements.append(summary_title)
        
        # 요약 테이블
        summary_data = [
            ['Total Drivers', f"{stats.get('total_drivers', 0)}"],
            ['Total Distance (km)', f"{stats.get('total_distance', 0):.2f}"],
            ['Average Distance per Driver (km)', f"{stats.get('avg_distance', 0):.2f}"],
            ['Total Driving Hours', f"{stats.get('total_hours', 0):.1f}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F0F0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def generate_monthly_report(
        self,
        year: int,
        month: int,
        driver_name: Optional[str] = None
    ) -> BytesIO:
        """월간 운전자 주행거리 PDF 리포트 생성"""
        from calendar import monthrange
        
        start_date = date(year, month, 1)
        last_day = monthrange(year, month)[1]
        end_date = date(year, month, last_day)
        
        logger.info(f"Generating monthly PDF report for {year}-{month:02d}")
        
        # PDF 문서 생성
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        elements = []
        
        # 제목
        title = Paragraph(
            f"Driver Mileage Monthly Report - {year}/{month:02d}",
            self.title_style
        )
        elements.append(title)
        
        subtitle = Paragraph(
            f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            self.subtitle_style
        )
        elements.append(subtitle)
        
        # 데이터 조회
        query = self.db.query(
            DriverDailyMileage.notes,
            func.sum(DriverDailyMileage.total_distance_km).label('total_distance'),
            func.sum(DriverDailyMileage.total_driving_minutes).label('total_minutes'),
            func.sum(DriverDailyMileage.idle_minutes).label('total_idle'),
            func.avg(DriverDailyMileage.avg_speed_kmh).label('avg_speed'),
            func.max(DriverDailyMileage.max_speed_kmh).label('max_speed'),
            func.count(DriverDailyMileage.id).label('driving_days')
        ).filter(
            and_(
                DriverDailyMileage.date >= start_date,
                DriverDailyMileage.date <= end_date,
                DriverDailyMileage.calculation_method == 'vehicle_based'
            )
        ).group_by(DriverDailyMileage.notes)
        
        if driver_name:
            query = query.filter(DriverDailyMileage.notes.like(f'%{driver_name}%'))
        
        results = query.order_by(func.sum(DriverDailyMileage.total_distance_km).desc()).all()
        
        # 통계 계산
        total_distance = sum(r.total_distance for r in results)
        total_minutes = sum(r.total_minutes for r in results)
        avg_distance = total_distance / len(results) if results else 0
        
        stats = {
            'total_drivers': len(results),
            'total_distance': total_distance,
            'avg_distance': avg_distance,
            'total_hours': total_minutes / 60 if total_minutes else 0
        }
        
        # 요약 섹션
        elements.extend(self._create_summary_section(stats))
        
        # 데이터 테이블
        table_data = [
            ['Rank', 'Driver Name', 'Distance\n(km)', 'Driving\nHours', 'Idle\nHours', 
             'Avg Speed\n(km/h)', 'Max Speed\n(km/h)', 'Days', 'Avg/Day\n(km)']
        ]
        
        for rank, record in enumerate(results, 1):
            driver_name_val = record.notes.replace("차량기반:", "") if record.notes else "Unknown"
            total_hours = record.total_minutes / 60 if record.total_minutes else 0
            idle_hours = record.total_idle / 60 if record.total_idle else 0
            avg_daily = record.total_distance / record.driving_days if record.driving_days else 0
            
            table_data.append([
                str(rank),
                driver_name_val,
                f"{record.total_distance:.2f}",
                f"{total_hours:.1f}",
                f"{idle_hours:.1f}",
                f"{record.avg_speed or 0:.1f}",
                f"{record.max_speed or 0:.1f}",
                str(record.driving_days),
                f"{avg_daily:.2f}"
            ])
        
        # 합계 행
        table_data.append([
            'Total',
            f"{len(results)} drivers",
            f"{total_distance:.2f}",
            f"{total_minutes/60:.1f}" if total_minutes else "0.0",
            '',
            '',
            '',
            '',
            f"{avg_distance:.2f}"
        ])
        
        # 테이블 생성
        table = Table(table_data, colWidths=[
            0.6*inch, 1.5*inch, 1*inch, 0.9*inch, 0.9*inch, 
            0.9*inch, 0.9*inch, 0.7*inch, 1*inch
        ])
        
        # 테이블 스타일
        table.setStyle(TableStyle([
            # 헤더
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.font_name_bold),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            # 데이터
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Rank
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Driver Name
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'), # Numbers
            ('FONTNAME', (0, 1), (-1, -2), self.font_name),
            ('FONTSIZE', (0, 1), (-1, -2), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -2), 6),
            ('TOPPADDING', (0, 1), (-1, -2), 6),
            
            # 합계 행
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E7E6E6')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
            ('FONTNAME', (0, -1), (-1, -1), self.font_name_bold),
            ('FONTSIZE', (0, -1), (-1, -1), 9),
            
            # 그리드
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # 교대 행 색상
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F9F9F9')])
        ]))
        
        elements.append(table)
        
        # 푸터 정보
        elements.append(Spacer(1, 30))
        footer = Paragraph(
            f"Generated on {date.today().strftime('%Y-%m-%d')} | UVIS Cold Chain Management System",
            ParagraphStyle(
                'Footer',
                fontName=self.font_name,
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        )
        elements.append(footer)
        
        # PDF 빌드
        doc.build(elements)
        buffer.seek(0)
        
        logger.info(f"Monthly PDF report generated: {len(results)} drivers")
        return buffer
    
    def generate_annual_summary(
        self,
        year: int,
        driver_name: Optional[str] = None
    ) -> BytesIO:
        """연간 요약 PDF 리포트 생성"""
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        logger.info(f"Generating annual PDF summary for {year}")
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        elements = []
        
        # 제목
        title = Paragraph(
            f"Driver Mileage Annual Summary - {year}",
            self.title_style
        )
        elements.append(title)
        
        subtitle = Paragraph(
            f"Full Year Report: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            self.subtitle_style
        )
        elements.append(subtitle)
        
        # 월별 데이터 조회
        monthly_stats = []
        for month in range(1, 13):
            month_start = date(year, month, 1)
            from calendar import monthrange
            last_day = monthrange(year, month)[1]
            month_end = date(year, month, last_day)
            
            query = self.db.query(
                func.sum(DriverDailyMileage.total_distance_km).label('total_distance'),
                func.count(func.distinct(DriverDailyMileage.notes)).label('driver_count')
            ).filter(
                and_(
                    DriverDailyMileage.date >= month_start,
                    DriverDailyMileage.date <= month_end,
                    DriverDailyMileage.calculation_method == 'vehicle_based'
                )
            )
            
            if driver_name:
                query = query.filter(DriverDailyMileage.notes.like(f'%{driver_name}%'))
            
            result = query.first()
            monthly_stats.append({
                'month': month,
                'distance': result.total_distance or 0,
                'drivers': result.driver_count or 0
            })
        
        # 연간 통계
        total_distance = sum(m['distance'] for m in monthly_stats)
        avg_monthly_distance = total_distance / 12
        
        stats = {
            'total_drivers': max(m['drivers'] for m in monthly_stats) if monthly_stats else 0,
            'total_distance': total_distance,
            'avg_distance': avg_monthly_distance,
            'total_hours': 0  # 연간 시간은 별도 계산 필요
        }
        
        # 요약 섹션
        elements.extend(self._create_summary_section(stats))
        
        # 월별 데이터 테이블
        table_data = [
            ['Month', 'Total Distance (km)', 'Active Drivers', 'Avg per Driver (km)']
        ]
        
        for stat in monthly_stats:
            avg_per_driver = stat['distance'] / stat['drivers'] if stat['drivers'] > 0 else 0
            table_data.append([
                f"{year}-{stat['month']:02d}",
                f"{stat['distance']:.2f}",
                str(stat['drivers']),
                f"{avg_per_driver:.2f}"
            ])
        
        # 합계 행
        table_data.append([
            'Annual Total',
            f"{total_distance:.2f}",
            '',
            f"{avg_monthly_distance:.2f}"
        ])
        
        table = Table(table_data, colWidths=[2*inch, 2*inch, 2*inch, 2*inch])
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.font_name_bold),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E7E6E6')),
            ('FONTNAME', (0, -1), (-1, -1), self.font_name_bold),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F9F9F9')])
        ]))
        
        elements.append(table)
        
        # 푸터
        elements.append(Spacer(1, 30))
        footer = Paragraph(
            f"Generated on {date.today().strftime('%Y-%m-%d')} | UVIS Cold Chain Management System",
            ParagraphStyle('Footer', fontName=self.font_name, fontSize=8, 
                          textColor=colors.grey, alignment=TA_CENTER)
        )
        elements.append(footer)
        
        doc.build(elements)
        buffer.seek(0)
        
        logger.info(f"Annual PDF summary generated for {year}")
        return buffer
    
    def generate_custom_report(
        self,
        records: List[DriverDailyMileage],
        driver_name: str,
        period: str
    ) -> bytes:
        """
        커스텀 리포트 생성 (모바일용)
        
        Args:
            records: 주행거리 기록 리스트
            driver_name: 운전자명
            period: 기간 표시 문자열
        
        Returns:
            bytes: PDF 파일 바이트
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )
        
        elements = []
        
        # 제목
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontName=self.font_name_bold,
            fontSize=18,
            textColor=colors.HexColor('#1F4E78'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        elements.append(Paragraph(f"{driver_name} 주행거리 리포트", title_style))
        
        # 기간
        period_style = ParagraphStyle(
            'Period',
            fontName=self.font_name,
            fontSize=12,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        elements.append(Paragraph(f"조회 기간: {period}", period_style))
        
        # 통계 요약
        total_distance = sum(r.total_distance_km or 0 for r in records)
        total_driving_minutes = sum(r.total_driving_minutes or 0 for r in records)
        driving_days = len(records)
        avg_distance = total_distance / driving_days if driving_days > 0 else 0
        
        summary_data = [
            ['총 주행거리', f"{total_distance:.2f} km"],
            ['총 주행시간', f"{total_driving_minutes / 60:.1f} 시간"],
            ['운행 일수', f"{driving_days} 일"],
            ['일평균 주행거리', f"{avg_distance:.2f} km"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E7E6E6')),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name_bold),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(summary_table)
        
        elements.append(Spacer(1, 30))
        
        # 일별 상세 내역
        detail_header = Paragraph(
            "일별 상세 내역",
            ParagraphStyle('DetailHeader', fontName=self.font_name_bold, fontSize=14,
                          textColor=colors.HexColor('#1F4E78'), spaceAfter=15)
        )
        elements.append(detail_header)
        
        # 테이블 헤더
        table_data = [
            ['날짜', '주행거리', '주행시간', '평균속도', '차량수']
        ]
        
        # 데이터 행
        for record in records:
            driving_hours = (record.total_driving_minutes or 0) / 60
            table_data.append([
                str(record.date),
                f"{record.total_distance_km or 0:.2f} km",
                f"{driving_hours:.1f}h",
                f"{record.avg_speed_kmh or 0:.1f} km/h",
                str(record.vehicle_count or 0)
            ])
        
        detail_table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 1.2*inch, 1.2*inch, 1*inch])
        
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.font_name_bold),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTNAME', (0, 1), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')])
        ]))
        
        elements.append(detail_table)
        
        # 푸터
        elements.append(Spacer(1, 30))
        footer = Paragraph(
            f"Generated on {date.today().strftime('%Y-%m-%d')} | UVIS Cold Chain Management System",
            ParagraphStyle('Footer', fontName=self.font_name, fontSize=8,
                          textColor=colors.grey, alignment=TA_CENTER)
        )
        elements.append(footer)
        
        doc.build(elements)
        buffer.seek(0)
        
        logger.info(f"Custom PDF report generated for {driver_name}: {len(records)} records")
        return buffer.getvalue()
