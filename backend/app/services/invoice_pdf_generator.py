"""
Invoice PDF Generator Service
청구서 PDF 생성 서비스
Phase 3-B Week 1: 청구/정산 자동화
"""
from datetime import datetime
from typing import Optional
from io import BytesIO
import logging

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from app.models.billing import Invoice

logger = logging.getLogger(__name__)


class InvoicePDFGenerator:
    """청구서 PDF 생성기"""
    
    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            logger.warning("ReportLab이 설치되지 않았습니다. PDF 생성 기능이 제한됩니다.")
    
    def generate_invoice_pdf(self, invoice: Invoice) -> Optional[BytesIO]:
        """
        청구서 PDF 생성
        
        Args:
            invoice: Invoice 객체
            
        Returns:
            PDF 바이너리 데이터 (BytesIO)
        """
        if not REPORTLAB_AVAILABLE:
            logger.error("ReportLab이 설치되지 않아 PDF를 생성할 수 없습니다.")
            return None
        
        try:
            buffer = BytesIO()
            
            # PDF 문서 생성
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # 스타일 설정
            styles = getSampleStyleSheet()
            
            # 커스텀 스타일
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1e40af'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#1e40af'),
                spaceAfter=12
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6
            )
            
            # 문서 요소 리스트
            elements = []
            
            # 제목
            title = Paragraph("세금 계산서", title_style)
            elements.append(title)
            elements.append(Spacer(1, 0.5*cm))
            
            # 청구서 정보
            invoice_info = [
                [
                    Paragraph(f"<b>청구서 번호:</b> {invoice.invoice_number}", normal_style),
                    Paragraph(f"<b>발행일:</b> {invoice.issue_date.strftime('%Y-%m-%d')}", normal_style)
                ],
                [
                    Paragraph(f"<b>청구 기간:</b> {invoice.billing_period_start.strftime('%Y-%m-%d')} ~ {invoice.billing_period_end.strftime('%Y-%m-%d')}", normal_style),
                    Paragraph(f"<b>납기일:</b> {invoice.due_date.strftime('%Y-%m-%d')}", normal_style)
                ]
            ]
            
            info_table = Table(invoice_info, colWidths=[9*cm, 8*cm])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.white)
            ]))
            
            elements.append(info_table)
            elements.append(Spacer(1, 1*cm))
            
            # 거래처 정보
            client_header = Paragraph("거래처 정보", header_style)
            elements.append(client_header)
            
            client = invoice.client
            client_info = [
                [
                    Paragraph(f"<b>상호:</b> {client.name}", normal_style),
                    Paragraph(f"<b>거래처 코드:</b> {client.code}", normal_style)
                ],
                [
                    Paragraph(f"<b>주소:</b> {client.address}", normal_style),
                    Paragraph(f"<b>연락처:</b> {client.phone or 'N/A'}", normal_style)
                ]
            ]
            
            client_table = Table(client_info, colWidths=[9*cm, 8*cm])
            client_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8)
            ]))
            
            elements.append(client_table)
            elements.append(Spacer(1, 1*cm))
            
            # 청구 항목 테이블
            items_header = Paragraph("청구 항목", header_style)
            elements.append(items_header)
            
            # 테이블 헤더
            table_data = [
                ['No.', '내역', '수량', '단가', '금액']
            ]
            
            # 청구 항목
            for idx, item in enumerate(invoice.line_items, 1):
                table_data.append([
                    str(idx),
                    Paragraph(item.description, normal_style),
                    f"{item.quantity:.1f}",
                    f"{item.unit_price:,.0f}원",
                    f"{item.amount:,.0f}원"
                ])
            
            # 합계 행
            table_data.append(['', '', '', '소계', f"{invoice.subtotal:,.0f}원"])
            table_data.append(['', '', '', '부가세 (10%)', f"{invoice.tax_amount:,.0f}원"])
            table_data.append(['', '', '', '총액', f"{invoice.total_amount:,.0f}원"])
            
            items_table = Table(
                table_data,
                colWidths=[1.5*cm, 8*cm, 2*cm, 2.5*cm, 3*cm]
            )
            
            items_table.setStyle(TableStyle([
                # 헤더 스타일
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # 데이터 스타일
                ('BACKGROUND', (0, 1), (-1, -4), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -4), colors.black),
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -4), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -4), [colors.white, colors.HexColor('#f9fafb')]),
                
                # 합계 행 스타일
                ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor('#e5e7eb')),
                ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -3), (-1, -1), 11),
                
                # 총액 행 강조
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
                
                # 테두리
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e40af')),
                
                # 패딩
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8)
            ]))
            
            elements.append(items_table)
            elements.append(Spacer(1, 1*cm))
            
            # 결제 정보
            payment_header = Paragraph("결제 정보", header_style)
            elements.append(payment_header)
            
            billing_policy = invoice.billing_policy
            if billing_policy:
                payment_info = [
                    [
                        Paragraph(f"<b>결제 조건:</b> {billing_policy.payment_terms_days}일 이내", normal_style),
                        Paragraph(f"<b>청구 주기:</b> {billing_policy.billing_cycle.value}", normal_style)
                    ]
                ]
                
                payment_table = Table(payment_info, colWidths=[9*cm, 8*cm])
                payment_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 8)
                ]))
                
                elements.append(payment_table)
            
            elements.append(Spacer(1, 1*cm))
            
            # 푸터
            footer_text = Paragraph(
                f"<i>본 세금계산서는 {datetime.now().strftime('%Y-%m-%d %H:%M')}에 자동 생성되었습니다.</i>",
                ParagraphStyle(
                    'Footer',
                    parent=styles['Normal'],
                    fontSize=8,
                    textColor=colors.grey,
                    alignment=TA_CENTER
                )
            )
            elements.append(footer_text)
            
            # PDF 생성
            doc.build(elements)
            
            buffer.seek(0)
            
            logger.info(f"청구서 PDF 생성 완료: {invoice.invoice_number}")
            
            return buffer
            
        except Exception as e:
            logger.error(f"청구서 PDF 생성 실패: {invoice.invoice_number}, error={e}")
            return None
    
    def save_invoice_pdf(self, invoice: Invoice, file_path: str) -> bool:
        """
        청구서 PDF를 파일로 저장
        
        Args:
            invoice: Invoice 객체
            file_path: 저장할 파일 경로
            
        Returns:
            성공 여부
        """
        pdf_buffer = self.generate_invoice_pdf(invoice)
        
        if not pdf_buffer:
            return False
        
        try:
            with open(file_path, 'wb') as f:
                f.write(pdf_buffer.getvalue())
            
            logger.info(f"청구서 PDF 저장 완료: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"청구서 PDF 저장 실패: {file_path}, error={e}")
            return False
