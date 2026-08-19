from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM Provider & Default Model
    llm_provider: str = Field(default="ollama", description="ollama, google, or openai")
    ollama_base_url: str = Field(default="http://127.0.0.1:11434")
    ollama_model: str = Field(default="llama3.1")
    
    # Task-Specialized Model Mapping
    chat_model: str = Field(default="llama3.2")
    coder_model: str = Field(default="qwen2.5-coder:7b")
    rag_model: str = Field(default="llama3.1")
    ollama_embed_model: str = Field(default="nomic-embed-text-v2-moe:latest")
    
    # Search Engine Settings (duckduckgo, tavily, google, or serpapi)
    search_engine: str = Field(default="duckduckgo")
    tavily_api_key: Optional[str] = Field(default=None)
    serpapi_api_key: Optional[str] = Field(default=None)
    google_search_api_key: Optional[str] = Field(default=None)
    google_search_cx: Optional[str] = Field(default=None)

    google_api_key: Optional[str] = Field(default=None)
    openai_api_key: Optional[str] = Field(default=None)

    # Hugging Face (Image Generation — FLUX.1-schnell)
    hf_api_key: Optional[str] = Field(default=None)
    hf_image_model: str = Field(default="black-forest-labs/FLUX.1-schnell")

    # Telegram Bot API
    telegram_bot_token: Optional[str] = Field(default=None)

    # Twilio WhatsApp API
    twilio_account_sid: Optional[str] = Field(default=None)
    twilio_auth_token: Optional[str] = Field(default=None)
    twilio_whatsapp_from: str = Field(default="whatsapp:+14155238886")  # Twilio sandbox number

    # SMTP Configuration
    smtp_server: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    smtp_email: Optional[str] = Field(default=None)
    smtp_password: Optional[str] = Field(default=None)

    # Image Generation Engine
    image_gen_engine: str = Field(default="pollinations")

    # Logging & Paths
    log_level: str = Field(default="WARNING")
    vectorstore_dir: Path = Field(default=Path("./data/vectorstore"))
    docs_dir: Path = Field(default=Path("./data/docs"))
    outputs_dir: Path = Field(default=Path("./data/outputs"))

    def ensure_directories(self) -> None:
        """Create standard data directories if they do not exist."""
        self.vectorstore_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        Path("./logs").mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
