"""
CAPTAIN AI OS 2.0 — TTS PROVIDERS MODULE.
"""

from providers.tts.base import BaseTTSProvider, TTSConfig
from providers.tts.piper import PiperTTSProvider
from providers.tts.pyttsx3 import Pyttsx3TTSProvider
from providers.tts.factory import get_tts_provider

__all__ = [
    "BaseTTSProvider",
    "TTSConfig",
    "PiperTTSProvider",
    "Pyttsx3TTSProvider",
    "get_tts_provider",
]
