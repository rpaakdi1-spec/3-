from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Application
    APP_ENV: str = "development"
    APP_NAME: str = "Cold Chain Dispatch System"
    SECRET_KEY: str
    
    # Database
    DATABASE_URL: str = "sqlite:///./backend/dispatch.db"
    
    # Naver Map API
    NAVER_MAP_CLIENT_ID: str
    NAVER_MAP_CLIENT_SECRET: str
    
    # Samsung UVIS API
    UVIS_API_URL: str = "https://api.s1.co.kr/uvis/v1"
    UVIS_API_KEY: str = ""
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    # API Settings
    API_PREFIX: str = "/api/v1"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
