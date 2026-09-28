"""
CAPTAIN AI OS 2.0 — VOICE INTERACTION MANAGER.
Central coordinator for:
- Acoustic Clap Detection (STANDBY <-> ACTIVE toggle)
- Local Silero Voice Activity Detection (VAD)
- Speech-to-Text (Faster-Whisper)
- Text-to-Speech (Piper / PyTTSX3) with Barge-in Interruption
- 8-State StateManager lifecycle synchronization
- Desktop companion visual bridge integration
"""

import time
import queue
import asyncio
import threading
import numpy as np
from typing import Optional, Callable, Dict, Any
from loguru import logger

from config import settings
from app.state import AppState, StateManager, StateTransitionEvent
from app.runtime import AppRuntime, runtime as global_runtime
from providers.stt.base import BaseSTTProvider
from providers.stt.factory import get_stt_provider
from providers.tts.base import BaseTTSProvider
from providers.tts.factory import get_tts_provider
from src.voice.clap_detector import ClapDetector
from src.voice.vad import SileroVADDetector, VADState
from src.voice.audio_capture import AudioCapture, resample_audio


class VoiceManager:
    """
    Central Coordinator for Captain AI OS 2.0 Voice Capabilities.
    Orchestrates continuous background microphone processing, clap toggle,
    voice query execution, and speech synthesis without blocking the UI or runtime.
    """

    def __init__(
        self,
        runtime: Optional[AppRuntime] = None,
        stt_provider: Optional[BaseSTTProvider] = None,
        tts_provider: Optional[BaseTTSProvider] = None,
        clap_detector: Optional[ClapDetector] = None,
        vad_detector: Optional[SileroVADDetector] = None,
        desktop_window: Optional[Any] = None,
        vad_enabled: Optional[bool] = None,
    ):
        self.runtime = runtime or global_runtime
        self.state_manager: StateManager = self.runtime.state_manager

        # Provider components
        self.stt_provider: BaseSTTProvider = stt_provider or get_stt_provider()
        self.tts_provider: BaseTTSProvider = tts_provider or get_tts_provider()
        self.clap_detector: ClapDetector = clap_detector or ClapDetector()
        self.vad_detector: SileroVADDetector = vad_detector or SileroVADDetector()
        self.vad_enabled: bool = vad_enabled if vad_enabled is not None else getattr(settings, "vad_enabled", True)

        # Audio capture engine strictly standardized to 16kHz mono PCM
        sample_rate = getattr(settings, "voice_sample_rate", 16000)
        self.audio_capture = AudioCapture(
            sample_rate=sample_rate,
            chunk_size=512,
            target_sample_rate=16000,
            on_amplitude=self._handle_mic_amplitude,
        )

        # Worker thread and task synchronization
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._async_loop: Optional[asyncio.AbstractEventLoop] = None
        self._speech_buffer: list = []
        self._pet_window = None

        if desktop_window is not None:
            self.attach_pet_window(desktop_window)

        # Wire state manager subscriber
        self.state_manager.subscribe(self._on_state_transition)

    def attach_pet_window(self, pet_window) -> None:
        """Connect desktop pet overlay window for visual mouth synchronization."""
        self._pet_window = pet_window
        if hasattr(self.tts_provider, "set_audio_chunk_callback"):
            self.tts_provider.set_audio_chunk_callback(self._handle_tts_audio_chunk)

    def _handle_mic_amplitude(self, amplitude: float) -> None:
        """Forward real-time microphone energy to EMO pet while in LISTENING state."""
        if self._pet_window and hasattr(self._pet_window, "_emitter"):
            if self.state_manager.current_state == AppState.LISTENING:
                try:
                    self._pet_window._emitter.amplitude_changed.emit(amplitude)
                except Exception:
                    pass

    def _handle_tts_audio_chunk(self, chunk_bytes: bytes) -> None:
        """Calculate audio chunk RMS and drive EMO pet mouth lip-sync animation."""
        if not chunk_bytes or len(chunk_bytes) < 4:
            return
        if self._pet_window and hasattr(self._pet_window, "_emitter"):
            try:
                audio_data = np.frombuffer(chunk_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                rms = float(np.sqrt(np.mean(audio_data ** 2)))
                is_speaking = rms > 0.015
                self._pet_window._emitter.speech_changed.emit(is_speaking)
                self._pet_window._emitter.amplitude_changed.emit(min(1.0, rms * 4.0))
            except Exception:
                pass

    def _on_state_transition(self, event: StateTransitionEvent) -> None:
        """Handle application state changes."""
        logger.debug(f"VoiceManager: Received state transition -> {event.to_state.value}")
        if event.to_state == AppState.STANDBY:
            self._speech_buffer.clear()
            self.vad_detector.reset()
        elif event.to_state == AppState.ACTIVE:
            self.vad_detector.reset()

    def start(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> bool:
        """Start the background voice loop with a guaranteed running event loop."""
        if self._running:
            return True

        self._running = True
        self._owns_loop = False

        # Ensure a reliable running background event loop for async voice query dispatching
        if loop is not None and loop.is_running():
            self._async_loop = loop
        else:
            try:
                running = asyncio.get_running_loop()
                if running.is_running():
                    self._async_loop = running
            except RuntimeError:
                # No running event loop in current thread (e.g. Qt GUI main thread)
                self._async_loop = asyncio.new_event_loop()
                self._owns_loop = True
                self._loop_thread = threading.Thread(
                    target=self._run_async_event_loop,
                    name="CaptainVoiceAsyncLoop",
                    daemon=True,
                )
                self._loop_thread.start()

        # Start microphone hardware capture
        if settings.voice_enabled:
            self.audio_capture.start()

        self._worker_thread = threading.Thread(
            target=self._voice_processing_worker,
            name="CaptainVoiceWorker",
            daemon=True,
        )
        self._worker_thread.start()
        logger.info("VoiceManager: Background audio and gesture processing started.")
        return True

    def _run_async_event_loop(self) -> None:
        """Dedicated background event loop for async voice query dispatching."""
        asyncio.set_event_loop(self._async_loop)
        self._async_loop.run_forever()

    def stop(self) -> None:
        """Stop background voice loop."""
        self._running = False
        self.audio_capture.stop()
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=1.0)
        if getattr(self, "_owns_loop", False) and self._async_loop and self._async_loop.is_running():
            self._async_loop.call_soon_threadsafe(self._async_loop.stop)
        logger.info("VoiceManager: Stopped.")


    def set_vad_enabled(self, enabled: bool) -> None:
        """Enable or disable voice activity detection at runtime."""
        self.vad_enabled = enabled
        if hasattr(self.vad_detector, "set_enabled"):
            self.vad_detector.set_enabled(enabled)

    def process_audio_frame(self, frame: np.ndarray, sample_rate: int = 16000) -> None:
        """
        Process a single audio frame synchronously.
        Enforces standard 16kHz mono float32 pipeline by resampling if required.
        Used both in production background worker and in automated unit tests.
        """
        if frame is None or len(frame) == 0:
            return

        # Resample to 16kHz if frame arrives at a different sampling rate (e.g. 44.1k/48k)
        if sample_rate != 16000:
            frame = resample_audio(frame, orig_sr=sample_rate, target_sr=16000)

        current_state = self.state_manager.current_state

        # =====================================================================
        # 1. CLAP DETECTION PIPELINE
        # =====================================================================
        if settings.clap_enabled and self.clap_detector.is_enabled:
            if self.clap_detector.process_frame(frame):
                # Valid deliberate clap recognized
                self.clap_detector.handle_state_toggle(self.state_manager)
                return

        # =====================================================================
        # 2. VOICE ACTIVITY DETECTION & SPEECH PIPELINE
        # =====================================================================
        if current_state == AppState.STANDBY:
            # Standby mode: only clap detection is active; discard speech buffers
            return

        # Enforce VAD enabled configuration contract
        if not (self.vad_enabled and getattr(settings, "vad_enabled", True)):
            return

        # Handle Barge-in / Interruption while Captain is SPEAKING
        if current_state == AppState.SPEAKING:
            vad_state = self.vad_detector.process_chunk(frame)
            if vad_state in (VADState.SPEECH_START, VADState.SPEECH_CONTINUE):
                logger.info("VoiceManager: User barge-in speech detected! Interrupting TTS.")
                self.tts_provider.interrupt()
                # Legal state transition: SPEAKING -> LISTENING
                self.state_manager.transition_to(AppState.LISTENING, trigger="user_barge_in")
                self._speech_buffer = [frame.copy()]
            return

        # Auto-activate to LISTENING when user starts speaking while ACTIVE
        if current_state == AppState.ACTIVE:
            vad_state = self.vad_detector.process_chunk(frame)
            if vad_state in (VADState.SPEECH_START, VADState.SPEECH_CONTINUE):
                logger.info("VoiceManager: User speech commenced; transitioning ACTIVE -> LISTENING.")
                self.state_manager.transition_to(AppState.LISTENING, trigger="speech_detected")
                self._speech_buffer = [frame.copy()]
            return

        # Accumulate speech while in LISTENING state
        if current_state == AppState.LISTENING:
            vad_state = self.vad_detector.process_chunk(frame)
            if vad_state in (VADState.SPEECH_START, VADState.SPEECH_CONTINUE):
                self._speech_buffer.append(frame.copy())
            elif vad_state == VADState.SPEECH_END:
                logger.info("VoiceManager: Speech endpoint detected. Finalizing utterance...")
                self._dispatch_speech_recognition()

    def _dispatch_speech_recognition(self) -> None:
        """Assemble accumulated audio chunks and dispatch STT and agent execution."""
        if not self._speech_buffer:
            self.state_manager.transition_to(AppState.ACTIVE, trigger="empty_audio")
            return

        # Concatenate audio chunks
        full_audio = np.concatenate(self._speech_buffer)
        self._speech_buffer.clear()
        self.vad_detector.reset()

        # Convert float32 [-1.0, 1.0] to int16 PCM bytes for STT
        int16_audio = (np.clip(full_audio, -1.0, 1.0) * 32767).astype(np.int16)
        pcm_bytes = int16_audio.tobytes()

        # Transition LISTENING -> THINKING
        self.state_manager.transition_to(AppState.THINKING, trigger="speech_ended")

        # Schedule async query processing
        try:
            running_loop = asyncio.get_running_loop()
            running_loop.create_task(self._process_voice_query_async(pcm_bytes))
        except RuntimeError:
            if self._async_loop and self._async_loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    self._process_voice_query_async(pcm_bytes),
                    self._async_loop,
                )
            else:
                try:
                    asyncio.run(self._process_voice_query_async(pcm_bytes))
                except Exception as e:
                    logger.error(f"VoiceManager: Query execution error: {e}")
                    self.state_manager.transition_to(AppState.ERROR, trigger=f"query_error: {e}")


    async def _process_voice_query_async(self, pcm_bytes: bytes) -> None:
        """Transcribe audio, query agent, and speak response."""
        try:
            # 1. Speech-to-Text Transcription
            text = await self.stt_provider.transcribe(pcm_bytes)
            clean_query = text.strip() if text else ""
            logger.info(f"VoiceManager: Transcribed text: '{clean_query}'")

            if not clean_query or clean_query == "[voice input]":
                logger.info("VoiceManager: No meaningful speech transcribed. Returning to ACTIVE.")
                self.state_manager.transition_to(AppState.ACTIVE, trigger="no_transcription")
                return

            # 2. Existing Captain AI OS Core Execution (LangGraph / StateManager)
            # runtime.execute_query internally transitions: THINKING -> SPEAKING -> ACTIVE
            response = await self.runtime.execute_query(clean_query, session_id="voice_session")
            logger.info(f"VoiceManager: Agent response received ({len(response)} chars).")

            # 3. Text-to-Speech Synthesis and Audio Playback
            if response and self.state_manager.current_state in (AppState.SPEAKING, AppState.ACTIVE):
                if self.state_manager.current_state != AppState.SPEAKING:
                    self.state_manager.transition_to(AppState.SPEAKING, trigger="tts_playback_started")
                await self.tts_provider.speak(response)

            # Return to ACTIVE state after successful voice interaction
            if self.state_manager.current_state == AppState.SPEAKING:
                self.state_manager.transition_to(AppState.ACTIVE, trigger="voice_interaction_completed")

        except Exception as e:
            logger.error(f"VoiceManager: Exception during voice processing: {e}")
            if self.state_manager.current_state != AppState.ERROR:
                self.state_manager.transition_to(AppState.ERROR, trigger=f"voice_error: {e}")
            # Recover to ACTIVE
            self.state_manager.transition_to(AppState.ACTIVE, trigger="voice_error_recovered")

    def _voice_processing_worker(self) -> None:
        """Background thread continuously polling microphone audio queue."""
        while self._running:
            try:
                chunk = self.audio_capture.read_chunk(timeout=0.05)
                if chunk is not None:
                    self.process_audio_frame(chunk)
            except Exception as e:
                logger.warning(f"VoiceManager worker exception: {e}")
                time.sleep(0.05)


# Global VoiceManager Singleton
voice_manager = VoiceManager()
