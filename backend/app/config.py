from typing import List, Union
import json
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "KreatorBuzz — Create Your Own Buzz"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    DATABASE_URL: str = "sqlite:///./maccall.db"
    
    # JWT Authentication
    SECRET_KEY: str = "maccall-super-secret-jwt-key-2026-lux-creator-platform"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Encryption at rest for messages
    MESSAGE_ENCRYPTION_KEY: str = ""
    
    # AI Integration
    AI_PROVIDER: str = "ollama"  # "ollama", "gemini", or "fallback"
    GEMINI_API_KEY: str = ""
    OLLAMA_API_KEY: str = ""
    OLLAMA_MODEL: str = "glm-5.3-flash"
    OLLAMA_BASE_URL: str = "https://ollama.com"

    
    # CORS Origins
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
