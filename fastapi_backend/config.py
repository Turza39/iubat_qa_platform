from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # =========================
    # DATABASE
    # =========================
    DATABASE_URL: str

    # =========================
    # SECURITY
    # =========================
    SECRET_KEY: str 
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @property
    def ACCESS_TOKEN_EXPIRE_SECONDS(self) -> int:
        return self.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    # =========================
    # APP
    # =========================
    DEBUG: bool = False
    TIMEZONE: str

    # CORS (comma-separated string → list)
    CORS_ALLOWED_ORIGINS: str

    # =========================
    # REDIS / CELERY
    # =========================
    REDIS_URL: Optional[str]
    REDIS_SSL: bool = False
    CELERY_BROKER_URL: Optional[str]
    CELERY_RESULT_BACKEND: Optional[str]

    # =========================
    # SUPABASE (Optional - for file storage)
    # =========================
    SUPABASE_URL: Optional[str]
    SUPABASE_ACCESS_KEY: Optional[str]
    SUPABASE_SECRET_KEY: Optional[str] 
    SUPABASE_BUCKET: Optional[str] 

    # =========================
    # RATE LIMIT
    # =========================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW: int = 60

    # =========================
    # CACHE TTL (seconds)
    # =========================
    CACHE_TTL_QUESTION_LIST: int = 30
    CACHE_TTL_QUESTION_DETAIL: int = 60
    CACHE_TTL_TAGS: int = 300
    CACHE_TTL_ANSWER_LIST: int = 30
    CACHE_TTL_VOTE_STATS: int = 15
    CACHE_TTL_USER_PUBLIC: int = 60

    class Config:
        env_file = ".env"

    # -------------------------
    # Helpers (IMPORTANT FIX)
    # -------------------------
    @property
    def CORS_ALLOWED_ORIGINS_LIST(self) -> List[str]:
        return [
            origin.strip()
            for origin in self.CORS_ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()