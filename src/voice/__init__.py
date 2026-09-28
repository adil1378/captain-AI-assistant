"""
CAPTAIN AI OS 2.0 — VOICE INTERACTION SUBSYSTEM.
"""

from src.voice.clap_detector import ClapDetector
from src.voice.vad import SileroVADDetector, VADState
from src.voice.audio_capture import AudioCapture
from src.voice.voice_manager import VoiceManager, voice_manager

__all__ = [
    "ClapDetector",
    "SileroVADDetector",
    "VADState",
    "AudioCapture",
    "VoiceManager",
    "voice_manager",
]
