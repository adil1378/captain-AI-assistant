"""
CAPTAIN AI OS 2.0 — TTS BASE PROVIDER.
Defines foundational abstractions for Text-to-Speech synthesis and playback.
"""

from abc import abstractmethod
from typing import Any, Dict, Optional, Callable
from pydantic import BaseModel, Field

from providers.base import TTSProvider, ProviderMetadata


class TTSConfig(BaseModel):
    """Configuration options for speech synthesis."""
    voice: str = "en-US"
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0


class BaseTTSProvider(TTSProvider):
    """Base class for all Captain TTS providers."""

    def __init__(self, config: Optional[TTSConfig] = None):
        self.config = config or TTSConfig()
        self._is_speaking = False
        self._interrupted = False
        self._on_audio_chunk: Optional[Callable[[bytes], None]] = None

    @property
    def is_speaking(self) -> bool:
        """Return True if audio playback is currently in progress."""
        return self._is_speaking

    def interrupt(self) -> None:
        """Interrupt and cancel ongoing audio playback immediately (barge-in support)."""
        self._interrupted = True
        self._is_speaking = False

    def reset_interruption(self) -> None:
        """Reset interruption flag prior to new synthesis."""
        self._interrupted = False

    def set_audio_chunk_callback(self, callback: Optional[Callable[[bytes], None]]) -> None:
        """Register callback for audio streaming (e.g. For visualizer / pet mouth lip-sync)."""
        self._on_audio_chunk = callback

    @abstractmethod
    async def speak(self, text: str, **kwargs: Any) -> None:
        """Synthesize text and play audio directly through speakers."""
        pass

    @abstractmethod
    async def synthesize_to_bytes(self, text: str, **kwargs: Any) -> bytes:
        """Synthesize text into WAV / PCM audio bytes without immediate playback."""
        pass
