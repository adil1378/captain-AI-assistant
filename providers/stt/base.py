"""
CAPTAIN AI OS 2.0 — STT BASE PROVIDER.
Defines foundational abstractions for Speech-to-Text inference providers.
"""

from abc import abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from providers.base import STTProvider, ProviderMetadata


class STTResult(BaseModel):
    """Result of speech recognition."""
    text: str
    confidence: float = 1.0
    language: str = "en"
    duration_seconds: float = 0.0
    segments: list = Field(default_factory=list)


class BaseSTTProvider(STTProvider):
    """Base class for all Captain STT providers."""

    @abstractmethod
    async def transcribe(self, audio_data: bytes, **kwargs: Any) -> str:
        """Transcribe raw audio PCM bytes (16kHz, 16-bit mono) into text."""
        pass

    async def transcribe_with_metadata(self, audio_data: bytes, **kwargs: Any) -> STTResult:
        """Transcribe audio with detailed metadata."""
        text = await self.transcribe(audio_data, **kwargs)
        return STTResult(text=text)
