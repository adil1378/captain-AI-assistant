"""
CAPTAIN AI OS 2.0 — VOICE ACTIVITY DETECTION (VAD).
Local Voice Activity Detection using Silero VAD with speech lifecycle state tracking:
- SPEECH_START: User commenced speaking
- SPEECH_CONTINUE: Ongoing vocalization
- SPEECH_END: Natural speech pause / endpointing reached
"""

import time
import numpy as np
from enum import Enum
from typing import Optional
from loguru import logger

from config import settings


class VADState(str, Enum):
    SILENCE = "silence"
    SPEECH_START = "speech_start"
    SPEECH_CONTINUE = "speech_continue"
    SPEECH_END = "speech_end"


class SileroVADDetector:
    """
    Local Voice Activity Detector utilizing Silero VAD neural network.
    Includes hangover endpointing logic to detect speech boundary accurately.
    """

    def __init__(
        self,
        sensitivity: Optional[float] = None,
        sample_rate: int = 16000,
        silence_hangover_sec: float = 0.6,
    ):
        self.sensitivity = sensitivity if sensitivity is not None else settings.vad_sensitivity
        self.sample_rate = sample_rate
        self.silence_hangover_sec = silence_hangover_sec

        self._model = None
        self._in_speech = False
        self._last_speech_time = 0.0
        self._initialized = False
        self._load_model()

    def _load_model(self) -> None:
        """Attempt to load local Silero VAD model."""
        try:
            import silero_vad
            self._model = silero_vad.load_silero_vad()
            self._initialized = True
            logger.info("SileroVADDetector: Neural VAD model loaded successfully.")
        except Exception as e:
            logger.warning(f"SileroVADDetector: Neural model load deferred ({e}); using acoustic fallback.")
            self._model = None
            self._initialized = True

    def reset(self) -> None:
        """Reset conversation speech state."""
        self._in_speech = False
        self._last_speech_time = 0.0
        if self._model and hasattr(self._model, "reset_states"):
            try:
                self._model.reset_states()
            except Exception:
                pass

    def get_speech_confidence(self, audio_chunk: np.ndarray) -> float:
        """Calculate speech probability for a 512-sample (32ms at 16kHz) frame."""
        if audio_chunk is None or len(audio_chunk) == 0:
            return 0.0

        if audio_chunk.dtype == np.int16:
            audio = audio_chunk.astype(np.float32) / 32768.0
        else:
            audio = audio_chunk.astype(np.float32)

        if self._model is not None:
            try:
                import torch
                # Silero VAD expects 512 samples for 16kHz
                if len(audio) != 512:
                    if len(audio) > 512:
                        audio = audio[:512]
                    else:
                        audio = np.pad(audio, (0, 512 - len(audio)))
                tensor = torch.from_numpy(audio).float()
                prob = self._model(tensor, self.sample_rate).item()
                return float(prob)
            except Exception:
                pass

        # Robust energy-based fallback when neural inference is unavailable
        rms = float(np.sqrt(np.mean(audio ** 2)))
        return min(1.0, rms * 15.0)

    def process_chunk(self, audio_chunk: np.ndarray) -> VADState:
        """
        Evaluate frame and return VAD state transition:
        SILENCE, SPEECH_START, SPEECH_CONTINUE, or SPEECH_END.
        """
        prob = self.get_speech_confidence(audio_chunk)
        is_speech = prob >= self.sensitivity
        now = time.time()

        if is_speech:
            self._last_speech_time = now
            if not self._in_speech:
                self._in_speech = True
                return VADState.SPEECH_START
            else:
                return VADState.SPEECH_CONTINUE
        else:
            if self._in_speech:
                # Check hangover duration
                if (now - self._last_speech_time) >= self.silence_hangover_sec:
                    self._in_speech = False
                    return VADState.SPEECH_END
                else:
                    # Still within natural pause between words
                    return VADState.SPEECH_CONTINUE
            return VADState.SILENCE
