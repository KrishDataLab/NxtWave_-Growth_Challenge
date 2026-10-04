import os
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict

class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./nxtwave_growth.db"
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:5173"]
    API_V1_STR: str = "/api/v1"
    EMAIL_PROVIDER: str = "console"
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@nxtwave.in"
    SMTP_TLS: bool = True

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip().rstrip("/") for origin in v.split(",") if origin.strip()]
        return v

settings = Settings()
