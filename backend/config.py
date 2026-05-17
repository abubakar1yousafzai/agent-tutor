from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

# Always load .env from the backend/ directory, regardless of CWD
_ENV_FILE = Path(__file__).parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), extra="ignore")

    DATABASE_URL: str
    APP_ENV: str = "development"
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @field_validator("DATABASE_URL")
    @classmethod
    def coerce_asyncpg_url(cls, v: str) -> str:
        # Ensure async driver prefix for SQLAlchemy
        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        # asyncpg uses ?ssl=require, not ?sslmode=require
        v = v.replace("sslmode=require", "ssl=require")
        # asyncpg does not support channel_binding parameter
        v = v.replace("&channel_binding=require", "").replace("channel_binding=require&", "").replace("channel_binding=require", "")
        return v

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
