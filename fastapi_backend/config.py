from pydantic_settings import BaseSettings
from typing import Optional
from datetime import timedelta


class Settings(BaseSettings):
    # Database Configuration
    # Support both PostgreSQL and SQLite
    DB_ENGINE: str = "postgresql"  # 'postgresql' or 'sqlite'
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    
    # For SQLite (development)
    SQLITE_URL: str = "sqlite:///./iubat_qa.db"
    
    # JWT Configuration
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 24 * 60  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    @property
    def ACCESS_TOKEN_EXPIRE_SECONDS(self) -> int:
        """Convert minutes to seconds for token expiration"""
        return self.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    
    # App Configuration
    DEBUG: bool = False
    ALLOWED_HOSTS: list = ["localhost", "127.0.0.1"]
    
    # CORS Configuration
    CORS_ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
    ]
    
    # Media Files
    MEDIA_URL: str = "/media/"
    MEDIA_ROOT: str = "./media"
    
    # Static Files
    STATIC_URL: str = "/static/"
    STATIC_ROOT: str = "./static"
    
    # Timezone
    TIMEZONE: str = "Asia/Dhaka"
    
    class Config:
        env_file = ".env"
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL based on configuration"""
        if self.DB_ENGINE == "postgresql":
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            return self.SQLITE_URL


settings = Settings()
