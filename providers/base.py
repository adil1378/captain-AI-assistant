"""
Captain AI OS 2.0 — Base Provider Abstractions.
Defines foundational interfaces for LLM, Vision, STT, and TTS providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncGenerator
from pydantic import BaseModel, Field


class ProviderMetadata(BaseModel):
    """Metadata describing a provider."""
    name: str = Field(description="Unique provider identifier")
    provider_type: str = Field(description="llm, vision, stt, or tts")
    version: str = Field(default="1.0.0", description="Provider implementation version")
    is_local: bool = Field(default=True, description="Whether this provider runs on-device without internet")
    description: str = Field(default="", description="Human-readable description")


class BaseProvider(ABC):
    """Abstract base class for all Captain AI OS providers."""

    @property
    @abstractmethod
    def metadata(self) -> ProviderMetadata:
        """Return provider metadata."""
        pass

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize provider resources, models, and connections."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check whether the provider service/engine is healthy and reachable."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Release any acquired resources, connections, or threads."""
        pass


class LLMProvider(BaseProvider):
    """Abstract interface for LLM / Reasoning Providers."""

    @abstractmethod
    async def ainvoke(self, prompt_or_messages: Any, **kwargs: Any) -> Any:
        """Asynchronously invoke the model and return a complete response."""
        pass

    @abstractmethod
    async def astream(self, prompt_or_messages: Any, **kwargs: Any) -> AsyncGenerator[Any, None]:
        """Asynchronously stream response tokens/chunks."""
        pass


class VisionProvider(BaseProvider):
    """Abstract interface for Vision / Screen Analysis Providers."""

    @abstractmethod
    async def analyze_frame(self, image_bytes_or_array: Any, prompt: str, **kwargs: Any) -> str:
        """Analyze a visual frame and return natural language observations."""
        pass


class STTProvider(BaseProvider):
    """Abstract interface for Speech-to-Text Providers."""

    @abstractmethod
    async def transcribe(self, audio_data: bytes, **kwargs: Any) -> str:
        """Transcribe raw audio data to text."""
        pass


class TTSProvider(BaseProvider):
    """Abstract interface for Text-to-Speech Providers."""

    @abstractmethod
    async def speak(self, text: str, **kwargs: Any) -> None:
        """Synthesize and play speech audio."""
        pass
