"""
CAPTAIN AI OS 2.0 — CENTRALIZED CONFIGURATION SYSTEM.
Built with Pydantic Settings (v2) with full support for:
- Local & Cloud LLM Providers (Ollama, OpenAI, Gemini, Anthropic)
- Vision Providers (Local Ollama / LLaVA, Gemini)
- Speech-to-Text (STT) & Text-to-Speech (TTS) Providers
- Real-time Clap Detection Audio Windows & Energy Thresholds
- Screen Observation, FPS, and Vision Capture Resolution
- Desktop Execution Security & User Confirmation Policies
- Local Storage, Scratchpads, Vectorstores, and Telemetry Paths
- Full backward-compatibility for both lowercase and UPPERCASE legacy callers
"""

from pathlib import Path
from typing import Any, List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Unified Application Settings for Captain AI OS 2.0.
    Loads from .env with fallback defaults and transparent casing tolerance.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    # =========================================================================
    # 1. CORE APPLICATION & ENVIRONMENT
    # =========================================================================
    app_name: str = Field(default="Captain AI OS", description="Application Title")
    app_version: str = Field(default="2.0.0", description="Semantic Version")
    api_v1_prefix: str = Field(default="/api/v1", description="FastAPI V1 prefix")
    api_v2_prefix: str = Field(default="/api/v2", description="FastAPI V2 prefix")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Log level: DEBUG, INFO, WARNING, ERROR")
    allowed_hosts: List[str] = Field(default=["*"], description="CORS allowed hosts")

    # =========================================================================
    # 2. PROVIDER CONFIGURATIONS (LLM, VISION, STT, TTS)
    # =========================================================================
    llm_provider: str = Field(default="ollama", description="Primary LLM provider: ollama, openai, gemini, anthropic")
    default_provider: str = Field(default="ollama", description="Default provider alias")
    vision_provider: str = Field(default="ollama", description="Vision provider: ollama, gemini, mock")
    stt_provider: str = Field(default="local", description="Speech-to-text provider: local, faster_whisper, whisper, mock")
    stt_model: str = Field(default="base.en", description="Whisper / STT model size or path")
    stt_device: str = Field(default="cpu", description="STT compute device: cpu, cuda")
    stt_compute_type: str = Field(default="int8", description="STT compute type: int8, float16, float32")
    tts_provider: str = Field(default="pyttsx3", description="Text-to-speech provider: pyttsx3, piper, kokoro, mock")
    tts_model: str = Field(default="en_US-lessac-medium", description="TTS model identifier or voice file")
    tts_voice: str = Field(default="en-US", description="TTS voice language / profile")
    tts_speed: float = Field(default=1.0, description="TTS speech playback speed rate")

    # =========================================================================
    # 2.1 VOICE, CLAP & VAD SETTINGS (PHASE 3)
    # =========================================================================
    voice_enabled: bool = Field(default=True, description="Enable audio microphone capture and voice loop")
    voice_sample_rate: int = Field(default=16000, description="Standard unified audio sample rate in Hz (16kHz)")
    microphone_device: Optional[int] = Field(default=None, description="Index of default audio input device (None = system default)")
    vad_enabled: bool = Field(default=True, description="Enable local Silero Voice Activity Detection")
    vad_sensitivity: float = Field(default=0.5, description="VAD confidence threshold for speech (0.0 - 1.0)")
    clap_enabled: bool = Field(default=True, description="Enable acoustic clap detection toggle")
    clap_threshold: float = Field(default=0.65, description="Audio energy threshold for impulse detection (0.0 - 1.0)")
    clap_cooldown: float = Field(default=1.0, description="Cooldown interval in seconds between valid clap triggers")
    clap_min_interval_ms: int = Field(default=150, description="Minimum milliseconds between two valid claps")
    clap_max_interval_ms: int = Field(default=800, description="Maximum milliseconds window to register double clap")
    clap_sample_rate: int = Field(default=16000, description="Audio input sampling rate in Hz (unified 16kHz standard)")
    clap_chunk_size: int = Field(default=512, description="Audio stream buffer frame chunk size")

    # =========================================================================
    # 3. OLLAMA & LOCAL MODEL SETTINGS
    # =========================================================================
    ollama_base_url: str = Field(default="http://127.0.0.1:11434", description="Ollama API base URL")
    ollama_model: str = Field(default="llama3.1", description="Default general model")
    chat_model: str = Field(default="llama3.2", description="Conversational reasoning model")
    coder_model: str = Field(default="qwen3:4b", description="Coding / automation model")
    rag_model: str = Field(default="llama3.2", description="RAG synthesis model")
    vision_model: str = Field(default="llava", description="Vision understanding model")
    ollama_embed_model: str = Field(default="nomic-embed-text-v2-moe:latest", description="Vector embedding model")
    ollama_timeout: float = Field(default=30.0, description="Ollama HTTP timeout in seconds")
    ollama_keep_alive: str = Field(default="5m", description="Model memory retention keep-alive duration")

    # =========================================================================
    # 4. EXTERNAL API KEYS & CLOUD PROVIDERS
    # =========================================================================
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    google_api_key: Optional[str] = Field(default=None, description="Google Gemini API key")
    gemini_api_key: Optional[str] = Field(default=None, description="Gemini API key alias")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    github_token: Optional[str] = Field(default=None, description="GitHub personal access token")

    # =========================================================================
    # 6. SCREEN OBSERVATION & VISION SETTINGS
    # =========================================================================
    screen_monitor_index: int = Field(default=1, description="Primary monitor index for screen observation (1 = primary)")
    screen_capture_interval_sec: float = Field(default=2.0, description="Seconds between periodic screen frames")
    screen_resize_factor: float = Field(default=0.5, description="Image scale down factor for high-speed inference")
    screen_capture_quality: int = Field(default=80, description="JPEG compression quality (1-100)")
    screen_enable_ocr: bool = Field(default=True, description="Enable local UI element text OCR extraction")

    # =========================================================================
    # 7. SECURITY, CONFIRMATION & PERMISSION POLICIES
    # =========================================================================
    allow_fs_write: bool = Field(default=True, description="Allow agent to write to workspace files")
    allow_fs_delete: bool = Field(default=False, description="Allow agent to delete files without confirmation")
    allow_sys_exec: bool = Field(default=True, description="Allow agent to execute shell commands")
    allow_whatsapp_auto: bool = Field(default=True, description="Allow automated WhatsApp messaging")
    require_confirmation_for_fs_delete: bool = Field(default=True, description="Require prompt before file deletion")
    require_confirmation_for_sys_exec: bool = Field(default=True, description="Require prompt before destructive commands")
    require_confirmation_for_mouse_keyboard: bool = Field(default=True, description="Require prompt before OS input automation")
    security_risk_threshold: str = Field(default="MEDIUM", description="Threshold triggering confirmation: LOW, MEDIUM, HIGH, CRITICAL")
    allowed_fs_paths: List[str] = Field(default=["./data", "./workspace"], description="Paths permitted for file operations")

    # =========================================================================
    # 8. SEARCH & WEATHER PROVIDERS
    # =========================================================================
    search_engine: str = Field(default="tavily", description="Primary search engine: tavily, duckduckgo, serpapi, google")
    search_provider_priority: str = Field(default="tavily,serpapi,duckduckgo", description="Fallback chain")
    tavily_api_key: Optional[str] = Field(default=None, description="Tavily API key")
    serpapi_api_key: Optional[str] = Field(default=None, description="SerpAPI API key")
    google_search_api_key: Optional[str] = Field(default=None, description="Google Custom Search API key")
    google_search_cx: Optional[str] = Field(default=None, description="Google Custom Search Engine CX ID")

    weather_provider_priority: str = Field(default="openmeteo,wttrin,openweather,weatherapi", description="Weather fallback priority")
    openweather_api_key: Optional[str] = Field(default=None, description="OpenWeatherMap API key")
    weatherapi_api_key: Optional[str] = Field(default=None, description="WeatherAPI key")

    # =========================================================================
    # 9. IMAGE GENERATION (HUGGING FACE / POLLINATIONS)
    # =========================================================================
    image_gen_engine: str = Field(default="pollinations", description="Image gen provider: pollinations, huggingface")
    hf_token: Optional[str] = Field(default=None, description="Hugging Face user token")
    hf_api_key: Optional[str] = Field(default=None, description="Hugging Face API key alias")
    hf_image_model: str = Field(default="black-forest-labs/FLUX.1-schnell", description="Hugging Face diffusion model")

    # =========================================================================
    # 10. COMMUNICATIONS & MESSAGING INTEGRATIONS
    # =========================================================================
    telegram_bot_token: Optional[str] = Field(default=None, description="Telegram bot token")
    telegram_chat_id: Optional[str] = Field(default=None, description="Telegram default chat ID")

    twilio_account_sid: Optional[str] = Field(default=None, description="Twilio Account SID")
    twilio_auth_token: Optional[str] = Field(default=None, description="Twilio Auth Token")
    twilio_whatsapp_from: str = Field(default="whatsapp:+14155238886", description="Twilio sandbox WhatsApp sender")

    smtp_server: str = Field(default="smtp.gmail.com", description="SMTP server host")
    smtp_port: int = Field(default=587, description="SMTP port")
    smtp_email: Optional[str] = Field(default=None, description="SMTP authenticated sender email")
    smtp_password: Optional[str] = Field(default=None, description="SMTP app password")

    # =========================================================================
    # 11. DATABASES & MEMORY
    # =========================================================================
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    supabase_url: Optional[str] = Field(default=None, description="Supabase endpoint URL")
    supabase_key: Optional[str] = Field(default=None, description="Supabase service role / anon key")
    database_url: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/captain_ai", description="Primary PostgreSQL URL")
    vector_memory_distance_threshold: float = Field(default=0.80, description="ChromaDB semantic distance cutoff")

    # =========================================================================
    # 12. LOCAL PATHS & STORAGE DIRECTORIES
    # =========================================================================
    data_dir: Path = Field(default=Path("./data"), description="Primary data root")
    logs_dir: Path = Field(default=Path("./logs"), description="Log storage directory")
    scratch_dir: Path = Field(default=Path("./data/scratch"), description="Temporary execution scratchpad")
    memory_dir: Path = Field(default=Path("./data/memory"), description="Local SQLite / memory persistence")
    vectorstore_dir: Path = Field(default=Path("./data/vectorstore"), description="ChromaDB vector persistence")
    docs_dir: Path = Field(default=Path("./data/docs"), description="User document store for RAG")
    outputs_dir: Path = Field(default=Path("./data/outputs"), description="Agent-generated outputs and files")

    def ensure_directories(self) -> None:
        """Create all standard data directories if they do not exist."""
        for path_field in [
            self.data_dir,
            self.logs_dir,
            self.scratch_dir,
            self.memory_dir,
            self.vectorstore_dir,
            self.docs_dir,
            self.outputs_dir,
        ]:
            Path(path_field).mkdir(parents=True, exist_ok=True)

    def __getattr__(self, name: str) -> Any:
        """
        Transparent case-insensitive attribute access for backward compatibility.
        Allows legacy uppercase access (e.g. settings.CHAT_MODEL, settings.OLLAMA_BASE_URL)
        and field aliases seamlessly.
        """
        lower = name.lower()
        if lower in type(self).model_fields:
            return getattr(self, lower)

        # Explicit aliases
        alias_map = {
            "default_provider": "llm_provider",
            "hf_token": "hf_api_key",
            "gemini_api_key": "google_api_key",
            "google_api_key": "gemini_api_key",
        }
        if lower in alias_map and alias_map[lower] in type(self).model_fields:
            return getattr(self, alias_map[lower])

        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


# Central Singleton Settings Instance
settings = Settings()
settings.ensure_directories()
