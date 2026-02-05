"""
Invoice Email Service
청구서 이메일 발송 서비스
Phase 3-B Week 1: 청구/정산 자동화
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
from typing import Optional, List
import logging
import os

from app.models.billing import Invoice
from app.services.invoice_pdf_generator import InvoicePDFGenerator

logger = logging.getLogger(__name__)


class InvoiceEmailService:
    """청구서 이메일 발송 서비스"""
    
    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None
    ):
        """
        이메일 서비스 초기화
        
        Args:
            smtp_host: SMTP 서버 호스트
            smtp_port: SMTP 서버 포트
            smtp_user: SMTP 사용자명
            smtp_password: SMTP 비밀번호
            from_email: 발신 이메일 주소
        """
        self.smtp_host = smtp_host or os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = smtp_user or os.getenv('SMTP_USER', '')
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD', '')
        self.from_email = from_email or os.getenv('FROM_EMAIL', self.smtp_user)
        
        self.pdf_generator = InvoicePDFGenerator()
    
    def send_invoice_email(
        self,
        invoice: Invoice,
        to_email: str,
        cc_emails: Optional[List[str]] = None,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        attach_pdf: bool = True
    ) -> bool:
        """
        청구서 이메일 발송
        
        Args:
            invoice: Invoice 객체
            to_email: 수신 이메일
            cc_emails: 참조 이메일 리스트
            subject: 이메일 제목
            body: 이메일 본문
            attach_pdf: PDF 첨부 여부
            
        Returns:
            발송 성공 여부
        """
        if not self.smtp_user or not self.smtp_password:
            logger.error("SMTP 자격 증명이 설정되지 않았습니다.")
            return False
        
        try:
            # 이메일 메시지 생성
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # 제목 설정
            if not subject:
                subject = f"[청구서] {invoice.invoice_number} - {invoice.client.name}"
            msg['Subject'] = subject
            
            # 본문 설정
            if not body:
                body = self._generate_default_body(invoice)
            
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # PDF 첨부
            if attach_pdf:
                pdf_buffer = self.pdf_generator.generate_invoice_pdf(invoice)
                
                if pdf_buffer:
                    pdf_attachment = MIMEApplication(pdf_buffer.getvalue(), _subtype='pdf')
                    pdf_attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=f"{invoice.invoice_number}.pdf"
                    )
                    msg.attach(pdf_attachment)
                else:
                    logger.warning(f"PDF 생성 실패: {invoice.invoice_number}")
            
            # SMTP 서버 연결 및 발송
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                
                recipients = [to_email]
                if cc_emails:
                    recipients.extend(cc_emails)
                
                server.send_message(msg, from_addr=self.from_email, to_addrs=recipients)
            
            logger.info(f"청구서 이메일 발송 완료: {invoice.invoice_number} -> {to_email}")
            
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP 인증 실패: 사용자명 또는 비밀번호를 확인하세요.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP 오류: {e}")
            return False
        except Exception as e:
            logger.error(f"이메일 발송 실패: {invoice.invoice_number}, error={e}")
            return False
    
    def _generate_default_body(self, invoice: Invoice) -> str:
        """
        기본 이메일 본문 생성
        
        Args:
            invoice: Invoice 객체
            
        Returns:
            HTML 형식의 이메일 본문
        """
        client = invoice.client
        
        # 결제 상태에 따른 메시지
        if invoice.paid_amount > 0:
            payment_status = f"""
            <p style="color: #059669; font-weight: bold;">
                부분 결제 완료: {invoice.paid_amount:,.0f}원 / {invoice.total_amount:,.0f}원
            </p>
            """
        else:
            payment_status = ""
        
        # 연체 경고
        overdue_warning = ""
        if invoice.status.value == 'OVERDUE':
            overdue_warning = f"""
            <div style="background-color: #fee2e2; border-left: 4px solid #ef4444; padding: 12px; margin: 20px 0;">
                <p style="color: #991b1b; font-weight: bold; margin: 0;">
                    ⚠️ 연체 청구서
                </p>
                <p style="color: #991b1b; margin: 8px 0 0 0;">
                    납기일({invoice.due_date.strftime('%Y-%m-%d')})이 경과되었습니다. 
                    빠른 시일 내에 결제 부탁드립니다.
                </p>
            </div>
            """
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Malgun Gothic', sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #1e40af;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background-color: #ffffff;
                    padding: 30px;
                    border: 1px solid #e5e7eb;
                    border-top: none;
                    border-radius: 0 0 8px 8px;
                }}
                .info-box {{
                    background-color: #f3f4f6;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
                .info-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid #e5e7eb;
                }}
                .info-row:last-child {{
                    border-bottom: none;
                }}
                .label {{
                    font-weight: bold;
                    color: #6b7280;
                }}
                .value {{
                    color: #111827;
                }}
                .total {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #1e40af;
                    text-align: center;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #6b7280;
                    font-size: 12px;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                }}
                .button {{
                    display: inline-block;
                    background-color: #1e40af;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">청구서 발행 안내</h1>
                </div>
                
                <div class="content">
                    <p>안녕하세요, <strong>{client.name}</strong> 담당자님</p>
                    
                    <p>
                        {invoice.billing_period_start.strftime('%Y년 %m월 %d일')} ~ 
                        {invoice.billing_period_end.strftime('%Y년 %m월 %d일')} 기간의 
                        운송 서비스에 대한 청구서를 발행하였습니다.
                    </p>
                    
                    {overdue_warning}
                    
                    <div class="info-box">
                        <div class="info-row">
                            <span class="label">청구서 번호</span>
                            <span class="value">{invoice.invoice_number}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">발행일</span>
                            <span class="value">{invoice.issue_date.strftime('%Y-%m-%d')}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">납기일</span>
                            <span class="value" style="color: #dc2626; font-weight: bold;">
                                {invoice.due_date.strftime('%Y-%m-%d')}
                            </span>
                        </div>
                        <div class="info-row">
                            <span class="label">청구 기간</span>
                            <span class="value">
                                {invoice.billing_period_start.strftime('%Y-%m-%d')} ~ 
                                {invoice.billing_period_end.strftime('%Y-%m-%d')}
                            </span>
                        </div>
                        <div class="info-row">
                            <span class="label">배차 건수</span>
                            <span class="value">{len(invoice.line_items)}건</span>
                        </div>
                    </div>
                    
                    <div class="total">
                        청구 금액: {invoice.total_amount:,.0f}원
                    </div>
                    
                    {payment_status}
                    
                    <p style="margin-top: 30px;">
                        상세 내역은 첨부된 PDF 파일을 확인해 주시기 바랍니다.
                    </p>
                    
                    <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
                        <strong>결제 안내:</strong><br>
                        · 납기일까지 결제 부탁드립니다.<br>
                        · 문의사항이 있으시면 언제든지 연락 주시기 바랍니다.<br>
                        · 결제 완료 후 영수증이 필요하신 경우 요청해 주세요.
                    </p>
                    
                    <div class="footer">
                        <p>본 메일은 자동 발송되었습니다.</p>
                        <p>발송 시각: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                        <p style="margin-top: 10px;">
                            © 2026 물류관리시스템 | 
                            문의: {self.from_email}
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return body
    
    def send_payment_reminder(
        self,
        invoice: Invoice,
        to_email: str,
        days_overdue: int
    ) -> bool:
        """
        결제 독촉 이메일 발송
        
        Args:
            invoice: Invoice 객체
            to_email: 수신 이메일
            days_overdue: 연체 일수
            
        Returns:
            발송 성공 여부
        """
        subject = f"[결제 요청] {invoice.invoice_number} - 연체 {days_overdue}일"
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Malgun Gothic', sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .alert {{
                    background-color: #fee2e2;
                    border-left: 4px solid #ef4444;
                    padding: 20px;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
                .urgent {{
                    color: #991b1b;
                    font-weight: bold;
                    font-size: 18px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="alert">
                    <p class="urgent">⚠️ 결제 요청 알림</p>
                    <p>
                        청구서 번호: <strong>{invoice.invoice_number}</strong><br>
                        납기일: <strong>{invoice.due_date.strftime('%Y-%m-%d')}</strong><br>
                        연체 일수: <strong style="color: #dc2626;">{days_overdue}일</strong><br>
                        청구 금액: <strong>{invoice.total_amount:,.0f}원</strong>
                    </p>
                    <p style="margin-top: 20px;">
                        납기일이 {days_overdue}일 경과하였습니다.<br>
                        빠른 시일 내에 결제 부탁드립니다.
                    </p>
                </div>
                
                <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
                    문의사항이 있으시면 언제든지 연락 주시기 바랍니다.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_invoice_email(
            invoice=invoice,
            to_email=to_email,
            subject=subject,
            body=body,
            attach_pdf=True
        )
    
    def send_payment_confirmation(
        self,
        invoice: Invoice,
        to_email: str,
        payment_amount: float,
        payment_date: str
    ) -> bool:
        """
        결제 확인 이메일 발송
        
        Args:
            invoice: Invoice 객체
            to_email: 수신 이메일
            payment_amount: 결제 금액
            payment_date: 결제 날짜
            
        Returns:
            발송 성공 여부
        """
        subject = f"[결제 완료] {invoice.invoice_number} - 결제 확인"
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Malgun Gothic', sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .success {{
                    background-color: #d1fae5;
                    border-left: 4px solid #10b981;
                    padding: 20px;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2 style="color: #10b981;">✓ 결제가 완료되었습니다</h2>
                
                <div class="success">
                    <p>
                        청구서 번호: <strong>{invoice.invoice_number}</strong><br>
                        결제 금액: <strong>{payment_amount:,.0f}원</strong><br>
                        결제 날짜: <strong>{payment_date}</strong><br>
                        청구서 상태: <strong>결제 완료</strong>
                    </p>
                </div>
                
                <p>
                    결제해 주셔서 감사합니다.<br>
                    영수증이 필요하신 경우 요청해 주시기 바랍니다.
                </p>
                
                <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                    항상 이용해 주셔서 감사합니다.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg, from_addr=self.from_email, to_addrs=[to_email])
            
            logger.info(f"결제 확인 이메일 발송 완료: {invoice.invoice_number}")
            return True
            
        except Exception as e:
            logger.error(f"결제 확인 이메일 발송 실패: {e}")
            return False
