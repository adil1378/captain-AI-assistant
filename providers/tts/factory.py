"""
CAPTAIN AI OS 2.0 — TTS PROVIDER FACTORY.
"""

from typing import Optional
from config import settings
from providers.tts.base import BaseTTSProvider
from providers.tts.piper import PiperTTSProvider
from providers.tts.pyttsx3 import Pyttsx3TTSProvider


def get_tts_provider(provider_name: Optional[str] = None) -> BaseTTSProvider:
    """Instantiate and return the configured TTS provider."""
    name = (provider_name or settings.tts_provider).lower()
    if name in ["piper"]:
        return PiperTTSProvider()
    elif name in ["pyttsx3", "sapi5", "local"]:
        return Pyttsx3TTSProvider()
    return Pyttsx3TTSProvider()
