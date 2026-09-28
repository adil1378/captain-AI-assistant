"""
CAPTAIN AI OS 2.0 — MICROPHONE AUDIO CAPTURE.
Manages non-blocking asynchronous audio input streaming via sounddevice.
Provides safe error handling for missing/disconnected microphones.
"""

import queue
import threading
import numpy as np
from typing import Optional, Callable
from loguru import logger

from config import settings


def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int = 16000) -> np.ndarray:
    """
    Resample 1D float32 audio numpy array from orig_sr to target_sr using linear interpolation.
    Fast, artifact-free, deterministic, zero extra dependencies.
    Preserves audio duration and spectral pitch for downstream VAD, Clap, and STT pipelines.
    """
    if orig_sr == target_sr or len(audio) == 0:
        return audio
    num_target_samples = int(round(len(audio) * float(target_sr) / float(orig_sr)))
    if num_target_samples == 0:
        return np.zeros(0, dtype=audio.dtype)
    orig_indices = np.linspace(0, len(audio) - 1, len(audio))
    target_indices = np.linspace(0, len(audio) - 1, num_target_samples)
    return np.interp(target_indices, orig_indices, audio).astype(audio.dtype)


class AudioCapture:
    """Microphone audio stream capture using sounddevice with automatic 16kHz resampling."""

    def __init__(
        self,
        sample_rate: int = 16000,
        chunk_size: int = 512,
        target_sample_rate: int = 16000,
        device_index: Optional[int] = None,
        on_amplitude: Optional[Callable[[float], None]] = None,
    ):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.target_sample_rate = target_sample_rate
        self.device_index = device_index if device_index is not None else settings.microphone_device
        self.on_amplitude = on_amplitude

        self._stream = None
        self._is_capturing = False
        self._audio_queue: queue.Queue = queue.Queue(maxsize=100)
        self._lock = threading.Lock()

    @property
    def is_capturing(self) -> bool:
        return self._is_capturing

    def start(self) -> bool:
        """Start capturing audio stream from microphone."""
        with self._lock:
            if self._is_capturing:
                return True

            try:
                import sounddevice as sd

                def _callback(indata, frames, time_info, status):
                    if status:
                        logger.warning(f"AudioCapture stream status: {status}")

                    # Mono float32 copy
                    mono = indata[:, 0].copy() if indata.ndim > 1 else indata.copy()

                    # Resample if microphone stream runs at a device-native non-16k rate (e.g. 44.1k/48k)
                    if self.sample_rate != self.target_sample_rate:
                        mono = resample_audio(mono, orig_sr=self.sample_rate, target_sr=self.target_sample_rate)

                    # Instantaneous amplitude for pet visual feedback
                    if self.on_amplitude:
                        rms = float(np.sqrt(np.mean(mono ** 2)))
                        self.on_amplitude(min(1.0, rms * 5.0))

                    try:
                        self._audio_queue.put_nowait(mono)
                    except queue.Full:
                        pass

                self._stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype="float32",
                    blocksize=self.chunk_size,
                    device=self.device_index,
                    callback=_callback,
                )
                self._stream.start()
                self._is_capturing = True
                logger.info(f"AudioCapture: Microphone stream started at {self.sample_rate}Hz.")
                return True
            except Exception as e:
                logger.warning(f"AudioCapture: Microphone capture unavailable ({e})")
                self._stream = None
                self._is_capturing = False
                return False

    def stop(self) -> None:
        """Stop capturing audio stream."""
        with self._lock:
            if not self._is_capturing:
                return

            if self._stream is not None:
                try:
                    self._stream.stop()
                    self._stream.close()
                except Exception:
                    pass
                self._stream = None

            self._is_capturing = False
            # Clear remaining queue items
            while not self._audio_queue.empty():
                try:
                    self._audio_queue.get_nowait()
                except queue.Empty:
                    break

            logger.info("AudioCapture: Microphone stream stopped.")

    def read_chunk(self, timeout: float = 0.1) -> Optional[np.ndarray]:
        """Read a single chunk from the capture queue."""
        try:
            return self._audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def feed_synthetic_chunk(self, chunk: np.ndarray) -> None:
        """Inject synthetic audio chunk for automated tests and CI environments."""
        try:
            self._audio_queue.put_nowait(chunk)
        except queue.Full:
            pass
