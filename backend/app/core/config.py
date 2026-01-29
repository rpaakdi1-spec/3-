from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Application
    APP_ENV: str = Field(default="production", alias="ENVIRONMENT")
    APP_NAME: str = "Cold Chain Dispatch System"
    SECRET_KEY: str
    
    # JWT Authentication
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Database
    DATABASE_URL: str
    
    # Redis (parse from URL or use separate fields)
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # Naver Map API
    NAVER_MAP_CLIENT_ID: str
    NAVER_MAP_CLIENT_SECRET: str
    
    # Kakao API (Optional - for traffic information)
    KAKAO_REST_API_KEY: str = ""
    
    # Samsung UVIS API
    UVIS_API_URL: str = "https://api.s1.co.kr/uvis"
    UVIS_API_KEY: str = "your_uvis_api_key_here"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    # API Settings
    API_PREFIX: str = "/api/v1"
    
    # Monitoring & Alerts
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SLACK_WEBHOOK_URL: str = ""
    ALIGO_API_KEY: str = ""
    ALIGO_USER_ID: str = ""
    
    # Error Tracking
    SENTRY_DSN: str = ""  # Sentry DSN (선택사항)
    ALIGO_SENDER: str = ""
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  # Ignore extra fields from environment
    }


def get_settings() -> Settings:
    """Get application settings - lazy load to allow env vars to be set"""
    return Settings()


# Create singleton instance
settings = get_settings()
