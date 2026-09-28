"""
CAPTAIN AI OS 2.0 — STT PROVIDERS MODULE.
"""

from providers.stt.base import BaseSTTProvider, STTResult
from providers.stt.faster_whisper import FasterWhisperSTTProvider
from providers.stt.factory import get_stt_provider

__all__ = [
    "BaseSTTProvider",
    "STTResult",
    "FasterWhisperSTTProvider",
    "get_stt_provider",
]
