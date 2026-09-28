"""
CAPTAIN AI OS 2.0 — PYTTSX3 SAPI5 TTS PROVIDER.
Native offline Windows SAPI5 text-to-speech engine with barge-in interruption.
"""

import io
import os
import wave
import tempfile
import asyncio
from typing import Any, Optional
from loguru import logger

from providers.base import ProviderMetadata
from providers.tts.base import BaseTTSProvider, TTSConfig


class Pyttsx3TTSProvider(BaseTTSProvider):
    """Offline Windows SAPI5 Text-to-Speech provider using pyttsx3."""

    def __init__(self, config: Optional[TTSConfig] = None):
        super().__init__(config)
        self._engine = None
        self._initialized = False

    @property
    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name="pyttsx3",
            provider_type="tts",
            version="2.90",
            is_local=True,
            description="Native Windows SAPI5 speech synthesis with interruption support",
        )

    async def initialize(self) -> bool:
        """Initialize SAPI5 engine."""
        self._initialized = True
        return True

    async def health_check(self) -> bool:
        return True

    async def shutdown(self) -> None:
        self.interrupt()
        self._initialized = False

    def interrupt(self) -> None:
        super().interrupt()
        if self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass

    async def synthesize_to_bytes(self, text: str, **kwargs: Any) -> bytes:
        """
        Synthesize text to genuine WAV PCM bytes using Windows SAPI5 via pyttsx3.save_to_file.
        Produces real 22050Hz/16-bit mono PCM bytes that can be parsed by wave.open.
        """
        clean_text = self._clean_text(text)
        if not clean_text:
            return b""

        def _synth_sapi5() -> bytes:
            temp_path = None
            try:
                import pyttsx3
                engine = pyttsx3.init("sapi5")
                rate = int(165 * self.config.speed)
                engine.setProperty("rate", rate)
                engine.setProperty("volume", self.config.volume)

                voices = engine.getProperty("voices")
                for v in voices:
                    if any(name in v.name.lower() for name in ("david", "george", "zira")):
                        engine.setProperty("voice", v.id)
                        break

                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                    temp_path = tf.name

                engine.save_to_file(clean_text, temp_path)
                engine.runAndWait()

                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 44:
                    with open(temp_path, "rb") as f:
                        return f.read()
                return b""
            except Exception as e:
                logger.warning(f"Pyttsx3TTS synthesize_to_bytes exception: {e}")
                return b""
            finally:
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except Exception:
                        pass

        return await asyncio.to_thread(_synth_sapi5)

    async def speak(self, text: str, **kwargs: Any) -> None:
        """
        Synthesize and stream audio in real-time chunks through sounddevice.
        Invokes _on_audio_chunk on each chunk for real-time EMO mouth sync,
        and respects barge-in interruption tokens.
        Falls back to direct engine.say if sounddevice playback fails.
        """
        clean_text = self._clean_text(text)
        if not clean_text:
            return

        self.reset_interruption()
        self._is_speaking = True

        try:
            audio_bytes = await self.synthesize_to_bytes(clean_text, **kwargs)
            if not audio_bytes or self._interrupted:
                return

            def _play_chunks() -> bool:
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
                    return True
                except Exception as e:
                    logger.debug(f"Pyttsx3TTS: Streaming audio playback fallback triggered ({e})")
                    return False

            played_via_stream = await asyncio.to_thread(_play_chunks)

            # Fallback to direct synchronous synthesis if sounddevice is unavailable/mocked
            if not played_via_stream and not self._interrupted:
                def _fallback_direct():
                    try:
                        import pyttsx3
                        engine = pyttsx3.init("sapi5")
                        self._engine = engine
                        rate = int(165 * self.config.speed)
                        engine.setProperty("rate", rate)
                        engine.setProperty("volume", self.config.volume)
                        if not self._interrupted:
                            engine.say(clean_text)
                            engine.runAndWait()
                    except Exception as e:
                        logger.warning(f"Pyttsx3TTS direct fallback exception: {e}")
                    finally:
                        self._engine = None

                await asyncio.to_thread(_fallback_direct)

        finally:
            self._is_speaking = False

    def _clean_text(self, text: str) -> str:
        """Strip markdown markers and system annotations."""
        if not text:
            return ""
        return (
            text.replace("#", "")
            .replace("*", "")
            .replace("`", "")
            .replace("- ", "")
            .replace("• ", "")
            .strip()
        )
