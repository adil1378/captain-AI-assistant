"""
CAPTAIN AI OS 2.0 — PIPER TTS PROVIDER.
Local neural text-to-speech synthesis using Piper.
Supports chunked streaming playback and instantaneous barge-in interruption.
"""

import io
import wave
import asyncio
from pathlib import Path
from typing import Any, Optional
from loguru import logger

from providers.base import ProviderMetadata
from providers.tts.base import BaseTTSProvider, TTSConfig
from config import settings


class PiperTTSProvider(BaseTTSProvider):
    """Local Neural Text-to-Speech provider using Piper."""

    def __init__(self, model_name: Optional[str] = None, config: Optional[TTSConfig] = None):
        super().__init__(config)
        self.model_name = model_name or settings.tts_model
        self._voice = None
        self._initialized = False

    @property
    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name="piper",
            provider_type="tts",
            version="1.8.0",
            is_local=True,
            description="Local Piper neural text-to-speech with interruption support",
        )

    async def initialize(self) -> bool:
        """Initialize Piper voice model."""
        if self._initialized and self._voice is not None:
            return True

        def _load():
            try:
                import piper
                model_dir = settings.data_dir / "models" / "piper"
                model_dir.mkdir(parents=True, exist_ok=True)
                onnx_path = model_dir / f"{self.model_name}.onnx"
                if onnx_path.exists():
                    voice = piper.PiperVoice.load(str(onnx_path))
                    logger.info(f"PiperTTS: Loaded voice model from {onnx_path}")
                    return voice
                else:
                    logger.info(f"PiperTTS: Model {onnx_path} not found locally; fallback available.")
                    return None
            except Exception as e:
                logger.warning(f"PiperTTS: Initialization deferred ({e})")
                return None

        self._voice = await asyncio.to_thread(_load)
        self._initialized = True
        return True

    async def health_check(self) -> bool:
        return self._initialized

    async def shutdown(self) -> None:
        self.interrupt()
        self._voice = None
        self._initialized = False

    async def synthesize_to_bytes(self, text: str, **kwargs: Any) -> bytes:
        """Synthesize text into WAV bytes."""
        if not text or not text.strip():
            return b""

        if not self._initialized:
            await self.initialize()

        if self._voice is None:
            # Fallback to in-memory wave generator or pyttsx3 fallback
            from providers.tts.pyttsx3 import Pyttsx3TTSProvider
            fallback = Pyttsx3TTSProvider(config=self.config)
            return await fallback.synthesize_to_bytes(text, **kwargs)

        def _synth() -> bytes:
            wav_io = io.BytesIO()
            with wave.open(wav_io, "wb") as wav_file:
                self._voice.synthesize(text, wav_file)
            return wav_io.getvalue()

        return await asyncio.to_thread(_synth)

    async def speak(self, text: str, **kwargs: Any) -> None:
        """
        Synthesize and play audio in streaming chunks with interruption / barge-in detection.
        """
        if not text or not text.strip():
            return

        self.reset_interruption()
        self._is_speaking = True

        try:
            audio_bytes = await self.synthesize_to_bytes(text, **kwargs)
            if not audio_bytes or self._interrupted:
                return

            def _play_chunks():
                import sounddevice as sd
                import numpy as np

                try:
                    wav_io = io.BytesIO(audio_bytes)
                    with wave.open(wav_io, "rb") as wf:
                        channels = wf.getnchannels()
                        sample_rate = wf.getframerate()
                        sampwidth = wf.getsampwidth()
                        dtype = np.int16 if sampwidth == 2 else np.int32

                        chunk_frames = 1024
                        stream = sd.OutputStream(
                            samplerate=sample_rate,
                            channels=channels,
                            dtype=dtype,
                        )
                        with stream:
                            while not self._interrupted:
                                frames = wf.readframes(chunk_frames)
                                if not frames:
                                    break
                                data = np.frombuffer(frames, dtype=dtype)
                                stream.write(data)
                                if self._on_audio_chunk:
                                    self._on_audio_chunk(frames)
                except Exception as e:
                    logger.warning(f"PiperTTS: Audio playback exception ({e})")

            await asyncio.to_thread(_play_chunks)
        finally:
            self._is_speaking = False
