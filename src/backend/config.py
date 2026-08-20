import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # Application & Environment
    APP_NAME: str = "Captain AI OS"
    APP_VERSION: str = "2.0.0"
    API_V1_PREFIX: str = "/api/v1"
    API_V2_PREFIX: str = "/api/v2"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ALLOWED_HOSTS: List[str] = ["*"]

    # Model Manager Configurations
    CHAT_MODEL: str = "llama3.2"
    CODER_MODEL: str = "qwen3:4b"
    RAG_MODEL: str = "llama3.2"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text-v2-moe:latest"
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    DEFAULT_PROVIDER: str = "ollama"

    # API Credentials & Search Provider Configuration
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Search Engine Provider Settings
    SEARCH_ENGINE: str = "tavily"
    SEARCH_PROVIDER_PRIORITY: str = "tavily,serpapi,duckduckgo"
    TAVILY_API_KEY: Optional[str] = None
    SERPAPI_API_KEY: Optional[str] = None

    # Weather Provider Settings
    WEATHER_PROVIDER_PRIORITY: str = "openmeteo,wttrin,openweather,weatherapi"
    OPENWEATHER_API_KEY: Optional[str] = None
    WEATHERAPI_API_KEY: Optional[str] = None

    # Image Gen & Hugging Face Settings
    IMAGE_GEN_ENGINE: str = "pollinations"
    HF_TOKEN: Optional[str] = None

    # Memory & Database Configurations
    REDIS_URL: str = "redis://localhost:6379/0"
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/captain_ai"
    VECTOR_MEMORY_DISTANCE_THRESHOLD: float = 0.80

    # Comms & Automation Settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_EMAIL: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Permission System Enforcements
    ALLOW_FS_WRITE: bool = True
    ALLOW_FS_DELETE: bool = False  # Requires explicit prompt
    ALLOW_SYS_EXEC: bool = True
    ALLOW_WHATSAPP_AUTO: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
