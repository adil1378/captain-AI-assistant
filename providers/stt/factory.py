"""
CAPTAIN AI OS 2.0 — STT PROVIDER FACTORY.
"""

from typing import Optional
from config import settings
from providers.stt.base import BaseSTTProvider
from providers.stt.faster_whisper import FasterWhisperSTTProvider


def get_stt_provider(provider_name: Optional[str] = None) -> BaseSTTProvider:
    """Instantiate and return the configured STT provider."""
    name = (provider_name or settings.stt_provider).lower()
    if name in ["faster_whisper", "whisper", "local"]:
        return FasterWhisperSTTProvider()
    return FasterWhisperSTTProvider()
