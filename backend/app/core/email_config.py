"""
Email Configuration
Settings for SMTP server and email templates
"""
from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from typing import List


class EmailSettings(BaseSettings):
    """Email configuration settings"""
    
    # SMTP Settings
    MAIL_USERNAME: str = "noreply@coldchain.com"
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@coldchain.com"
    MAIL_FROM_NAME: str = "Cold Chain System"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    
    # Template Settings
    TEMPLATE_FOLDER: str = "app/templates/email"
    
    # Email List (for testing/dev)
    ADMIN_EMAILS: List[str] = ["admin@coldchain.com"]
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # 🔥 중요: 다른 환경 변수를 무시
    )


# Singleton instance
email_settings = EmailSettings()
