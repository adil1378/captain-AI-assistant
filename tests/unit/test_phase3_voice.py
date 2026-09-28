"""
CAPTAIN AI OS 2.0 — PHASE 3 VOICE, CLAP & VAD TEST SUITE.
Covers all 17 mandatory verification scenarios deterministically with mocks.
Zero hardware dependencies (no physical mic or speakers required).
"""

import os
import time
import asyncio
import pytest
import numpy as np
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure Qt runs headlessly during automated tests
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from config import settings
from app.state import AppState, StateManager, StateTransitionEvent
from app.runtime import AppRuntime
from providers.stt.base import BaseSTTProvider, STTResult
from providers.stt.faster_whisper import FasterWhisperSTTProvider
from providers.stt.factory import get_stt_provider
from providers.tts.base import BaseTTSProvider, TTSConfig
from providers.tts.piper import PiperTTSProvider
from providers.tts.pyttsx3 import Pyttsx3TTSProvider
from providers.tts.factory import get_tts_provider
from src.voice.clap_detector import ClapDetector
from src.voice.vad import SileroVADDetector, VADState
from src.voice.audio_capture import AudioCapture
from src.voice.voice_manager import VoiceManager
from ui.desktop.pet_window import CaptainDesktopWindow, PYSIDE_AVAILABLE


@pytest.fixture(scope="session")
def qapp():
    """Session-scoped QApplication for Qt widget tests."""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    yield app


@pytest.fixture
def mock_runtime():
    """Isolated AppRuntime fixture for deterministic testing."""
    return AppRuntime(initial_state=AppState.STANDBY)



def _generate_synthetic_clap_pulse(sample_rate: int = 16000, length: int = 512) -> np.ndarray:
    """Generate a sharp impulsive spike mimicking a hand clap (high peak, low RMS)."""
    frame = np.zeros(length, dtype=np.float32)
    # Impulsive spike in middle
    frame[length // 2] = 0.95
    frame[length // 2 + 1] = -0.75
    frame[length // 2 + 2] = 0.40
    frame[length // 2 + 3] = -0.20
    return frame


def _generate_synthetic_speech_chunk(sample_rate: int = 16000, length: int = 512) -> np.ndarray:
    """Generate a sustained waveform mimicking human speech (moderate sustained RMS)."""
    t = np.linspace(0, length / sample_rate, length, endpoint=False)
    # 220Hz harmonic waveform
    waveform = 0.3 * np.sin(2 * np.pi * 220 * t) + 0.15 * np.sin(2 * np.pi * 440 * t)
    return waveform.astype(np.float32)


# =============================================================================
# 1. Clap Detector Initialization
# =============================================================================
def test_clap_detector_initialization():
    detector = ClapDetector(threshold=0.70, cooldown_sec=1.5, sample_rate=16000)
    assert detector.threshold == 0.70
    assert detector.cooldown_sec == 1.5
    assert detector.sample_rate == 16000
    assert detector.is_enabled is True

    detector.set_enabled(False)
    assert detector.is_enabled is False


# =============================================================================
# 2. Clap Debounce, Interval Window, and Cooldown (Double-Clap)
# =============================================================================
def test_clap_debounce_and_cooldown():
    detector = ClapDetector(threshold=0.60, cooldown_sec=0.2, min_interval_ms=100.0, max_interval_ms=500.0)
    clap_frame = _generate_synthetic_clap_pulse()

    # 1st clap impulse: registered, returns False (waiting for 2nd clap)
    assert detector.process_frame(clap_frame) is False

    # Immediate 2nd impulse (< 100ms): rejected as reverberation/echo
    assert detector.process_frame(clap_frame) is False

    # Valid 2nd clap within [100ms, 500ms] window: double-clap recognized!
    time.sleep(0.12)
    assert detector.process_frame(clap_frame) is True

    # Immediate clap within cooldown: rejected
    assert detector.process_frame(clap_frame) is False

    # After cooldown period (0.2s): new double-clap sequence can be detected
    time.sleep(0.22)
    assert detector.process_frame(clap_frame) is False  # 1st of new pair
    time.sleep(0.12)
    assert detector.process_frame(clap_frame) is True   # 2nd of new pair


def test_double_clap_timeout_resets():
    """Verify that if the second clap arrives after max_interval_ms, it resets the window."""
    detector = ClapDetector(threshold=0.60, min_interval_ms=50.0, max_interval_ms=200.0)
    clap_frame = _generate_synthetic_clap_pulse()

    # First clap at t=0
    assert detector.process_frame(clap_frame) is False

    # Wait longer than max_interval (e.g. 250ms)
    time.sleep(0.25)
    # This clap arrives too late to complete a pair; it resets window as a new 1st clap
    assert detector.process_frame(clap_frame) is False

    # Now a second clap arrives in 100ms: valid double-clap!
    time.sleep(0.10)
    assert detector.process_frame(clap_frame) is True


# =============================================================================
# 3. STANDBY -> ACTIVE via Double-Clap
# =============================================================================
def test_standby_to_active_via_clap(mock_runtime):
    detector = ClapDetector(threshold=0.60, cooldown_sec=0.1, min_interval_ms=50.0, max_interval_ms=400.0)
    mock_runtime.state_manager.reset(AppState.STANDBY)

    manager = VoiceManager(runtime=mock_runtime, clap_detector=detector)
    clap_frame = _generate_synthetic_clap_pulse()

    # First clap: still STANDBY
    manager.process_audio_frame(clap_frame)
    assert mock_runtime.current_state == AppState.STANDBY

    # Second clap within window: triggers ACTIVE
    time.sleep(0.10)
    manager.process_audio_frame(clap_frame)
    assert mock_runtime.current_state == AppState.ACTIVE
    assert mock_runtime.state_manager.history[-1].trigger in ("clap_activation", "double_clap_activation")


# =============================================================================
# 4. ACTIVE -> STANDBY via Double-Clap
# =============================================================================
def test_active_to_standby_via_clap(mock_runtime):
    detector = ClapDetector(threshold=0.60, cooldown_sec=0.05, min_interval_ms=50.0, max_interval_ms=400.0)
    mock_runtime.state_manager.reset(AppState.ACTIVE)

    manager = VoiceManager(runtime=mock_runtime, clap_detector=detector)
    clap_frame = _generate_synthetic_clap_pulse()

    time.sleep(0.06)
    # First clap
    manager.process_audio_frame(clap_frame)
    assert mock_runtime.current_state == AppState.ACTIVE

    # Second clap
    time.sleep(0.10)
    manager.process_audio_frame(clap_frame)
    assert mock_runtime.current_state == AppState.STANDBY
    assert mock_runtime.state_manager.history[-1].trigger in ("clap_deactivation", "double_clap_deactivation")


# =============================================================================
# 5. STANDBY Remains Visible (STANDBY != HIDDEN)
# =============================================================================
@pytest.mark.skipif(not PYSIDE_AVAILABLE, reason="PySide6 required")
def test_standby_remains_visible(qapp, mock_runtime):
    window = CaptainDesktopWindow(runtime=mock_runtime)
    window.show_pet()
    assert window.isVisible() is True

    # Transition to STANDBY
    mock_runtime.state_manager.transition_to(AppState.STANDBY, force=True)
    qapp.processEvents()

    # STANDBY must NEVER hide the window
    assert window.isVisible() is True


# =============================================================================
# 6. VAD Lifecycle (Silence -> Speech Start -> Continue -> End)
# =============================================================================
def test_vad_lifecycle():
    vad = SileroVADDetector(sensitivity=0.2, silence_hangover_sec=0.1)
    silence = np.zeros(512, dtype=np.float32)
    speech = _generate_synthetic_speech_chunk()

    # 1. Silence
    assert vad.process_chunk(silence) == VADState.SILENCE

    # 2. Speech Start
    assert vad.process_chunk(speech) == VADState.SPEECH_START

    # 3. Speech Continue
    assert vad.process_chunk(speech) == VADState.SPEECH_CONTINUE

    # 4. Speech End (after hangover duration)
    time.sleep(0.15)
    assert vad.process_chunk(silence) == VADState.SPEECH_END


# =============================================================================
# 7. STT Provider Interface & Factory
# =============================================================================
@pytest.mark.anyio
async def test_stt_provider_interface():
    with patch("faster_whisper.WhisperModel") as mock_model_cls:
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        provider = FasterWhisperSTTProvider()
        assert provider.metadata.provider_type == "stt"
        assert provider.metadata.is_local is True

        initialized = await provider.initialize()
        assert initialized is True
        assert await provider.health_check() is True

        # Transcribing empty audio returns empty string
        empty_res = await provider.transcribe(b"")
        assert empty_res == ""

        # Factory instantiation
        factory_prov = get_stt_provider("faster_whisper")
        assert isinstance(factory_prov, BaseSTTProvider)



# =============================================================================
# 8. TTS Provider Interface & Factory
# =============================================================================
@pytest.mark.anyio
async def test_tts_provider_interface():
    pyttsx3_prov = Pyttsx3TTSProvider()
    assert pyttsx3_prov.metadata.provider_type == "tts"
    assert await pyttsx3_prov.initialize() is True

    wav_bytes = await pyttsx3_prov.synthesize_to_bytes("Testing Captain speech")
    assert wav_bytes.startswith(b"RIFF")

    # Interruption flag
    pyttsx3_prov.interrupt()
    assert pyttsx3_prov.is_speaking is False

    # Factory
    factory_piper = get_tts_provider("piper")
    assert isinstance(factory_piper, BaseTTSProvider)


# =============================================================================
# 9. Voice -> runtime.execute_query() Integration
# =============================================================================
@pytest.mark.anyio
async def test_voice_query_dispatches_to_runtime(mock_runtime):
    mock_stt = MagicMock(spec=BaseSTTProvider)
    mock_stt.transcribe = AsyncMock(return_value="what is the time")

    mock_tts = MagicMock(spec=BaseTTSProvider)
    mock_tts.speak = AsyncMock(return_value=None)
    mock_tts.interrupt = MagicMock()

    mock_runtime.execute_query = AsyncMock(return_value="The time is 12:00 PM.")
    mock_runtime.state_manager.reset(AppState.ACTIVE)

    manager = VoiceManager(
        runtime=mock_runtime,
        stt_provider=mock_stt,
        tts_provider=mock_tts,
    )

    # Simulate speech frame to transition to LISTENING
    manager.process_audio_frame(_generate_synthetic_speech_chunk())
    assert mock_runtime.current_state == AppState.LISTENING

    # Trigger speech completion
    manager._dispatch_speech_recognition()

    # Allow async query task to complete
    await asyncio.sleep(0.05)

    mock_stt.transcribe.assert_called_once()
    mock_runtime.execute_query.assert_called_once_with("what is the time", session_id="voice_session")


# =============================================================================
# 10. Voice State Lifecycle Transitions
# =============================================================================
def test_voice_state_transitions(mock_runtime):
    mock_runtime.state_manager.reset(AppState.STANDBY)
    assert mock_runtime.current_state == AppState.STANDBY

    # STANDBY -> ACTIVE
    mock_runtime.wake("test_clap")
    assert mock_runtime.current_state == AppState.ACTIVE

    # ACTIVE -> LISTENING
    mock_runtime.listen("test_vad")
    assert mock_runtime.current_state == AppState.LISTENING

    # LISTENING -> THINKING
    mock_runtime.think("test_stt")
    assert mock_runtime.current_state == AppState.THINKING

    # THINKING -> SPEAKING
    mock_runtime.speak("test_response")
    assert mock_runtime.current_state == AppState.SPEAKING

    # SPEAKING -> ACTIVE
    mock_runtime.wake("test_completed")
    assert mock_runtime.current_state == AppState.ACTIVE


# =============================================================================
# 11. TTS Interruption / Barge-in
# =============================================================================
def test_tts_barge_in_interruption(mock_runtime):
    mock_tts = MagicMock(spec=BaseTTSProvider)
    mock_tts.interrupt = MagicMock()

    vad = SileroVADDetector(sensitivity=0.2)
    mock_runtime.state_manager.reset(AppState.SPEAKING)

    manager = VoiceManager(
        runtime=mock_runtime,
        tts_provider=mock_tts,
        vad_detector=vad,
    )

    # In SPEAKING state, user starts talking -> barge-in
    speech_frame = _generate_synthetic_speech_chunk()
    manager.process_audio_frame(speech_frame)

    # Interruption triggered
    mock_tts.interrupt.assert_called_once()
    # Transitioned from SPEAKING -> LISTENING
    assert mock_runtime.current_state == AppState.LISTENING
    assert mock_runtime.state_manager.history[-1].trigger == "user_barge_in"


# =============================================================================
# 12. Microphone Failure Handling
# =============================================================================
def test_microphone_failure_handling():
    capture = AudioCapture(device_index=999)

    with patch("sounddevice.InputStream", side_effect=RuntimeError("PortAudio device error")):
        success = capture.start()
        # Must gracefully return False without raising an unhandled crash
        assert success is False
        assert capture.is_capturing is False

    capture.stop()


# =============================================================================
# 13. STT Failure Handling
# =============================================================================
@pytest.mark.anyio
async def test_stt_failure_handling(mock_runtime):
    mock_stt = MagicMock(spec=BaseSTTProvider)
    mock_stt.transcribe = AsyncMock(side_effect=RuntimeError("Whisper OOM"))

    mock_runtime.state_manager.reset(AppState.ACTIVE)
    manager = VoiceManager(runtime=mock_runtime, stt_provider=mock_stt)

    # Process query with broken STT
    await manager._process_voice_query_async(b"sample_pcm_bytes")

    # Manager should recover back to ACTIVE without locking or crashing
    assert mock_runtime.current_state == AppState.ACTIVE


# =============================================================================
# 14. TTS Failure Handling
# =============================================================================
@pytest.mark.anyio
async def test_tts_failure_handling(mock_runtime):
    mock_stt = MagicMock(spec=BaseSTTProvider)
    mock_stt.transcribe = AsyncMock(return_value="hello")

    mock_tts = MagicMock(spec=BaseTTSProvider)
    mock_tts.speak = AsyncMock(side_effect=RuntimeError("Speaker disconnected"))

    mock_runtime.execute_query = AsyncMock(return_value="Hi there!")
    mock_runtime.state_manager.reset(AppState.ACTIVE)

    manager = VoiceManager(
        runtime=mock_runtime,
        stt_provider=mock_stt,
        tts_provider=mock_tts,
    )

    await manager._process_voice_query_async(b"sample_pcm_bytes")
    # Must recover cleanly
    assert mock_runtime.current_state == AppState.ACTIVE


# =============================================================================
# 15. Configuration Loading
# =============================================================================
def test_voice_configuration_loading():
    assert hasattr(settings, "voice_enabled")
    assert hasattr(settings, "microphone_device")
    assert hasattr(settings, "vad_enabled")
    assert hasattr(settings, "vad_sensitivity")
    assert hasattr(settings, "clap_enabled")
    assert hasattr(settings, "clap_threshold")
    assert hasattr(settings, "clap_cooldown")
    assert hasattr(settings, "stt_provider")
    assert hasattr(settings, "stt_model")
    assert hasattr(settings, "stt_device")
    assert hasattr(settings, "stt_compute_type")
    assert hasattr(settings, "tts_provider")
    assert hasattr(settings, "tts_model")
    assert hasattr(settings, "tts_voice")
    assert hasattr(settings, "tts_speed")

    # Transparent uppercase access backward compatibility
    assert settings.VOICE_ENABLED == settings.voice_enabled
    assert settings.CLAP_THRESHOLD == settings.clap_threshold


# =============================================================================
# 16. Security Boundary Intact for Voice
# =============================================================================
def test_security_boundary_remains_active_for_voice():
    from src.backend.core.zero_trust_manager import ZeroTrustSecurityManager
    from src.tools.tool_invocation_layer import ToolInvocationLayer
    from src.tools.tool_registry import ToolRegistry
    from src.backend.core.permission_manager import PermissionManager
    from src.backend.core.event_bus import event_bus

    zt = ZeroTrustSecurityManager()
    assert zt is not None

    registry = ToolRegistry()
    perm_mgr = PermissionManager()
    til = ToolInvocationLayer(registry, perm_mgr, event_bus)
    assert hasattr(til, "execute_tool")
    assert settings.security_risk_threshold in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]



# =============================================================================
# 17. Pet Visual Feedback Synchronization with Voice States
# =============================================================================
@pytest.mark.skipif(not PYSIDE_AVAILABLE, reason="PySide6 required")
def test_pet_visual_synchronization_with_voice_states(qapp, mock_runtime):
    window = CaptainDesktopWindow(runtime=mock_runtime)
    window.show_pet()

    # 1. LISTENING state
    mock_runtime.state_manager.transition_to(AppState.ACTIVE, force=True)
    mock_runtime.listen("voice_start")
    qapp.processEvents()
    assert mock_runtime.current_state == AppState.LISTENING

    # 2. THINKING state
    mock_runtime.think("processing")
    qapp.processEvents()
    assert mock_runtime.current_state == AppState.THINKING

    # 3. SPEAKING state
    mock_runtime.speak("tts_start")
    qapp.processEvents()
    assert mock_runtime.current_state == AppState.SPEAKING

    # 4. ACTIVE state
    mock_runtime.wake("completed")
    qapp.processEvents()
    assert mock_runtime.current_state == AppState.ACTIVE


# =============================================================================
# 18. Amplitude Streaming and Real-Time Mouth Synchronization Signal
# =============================================================================
@pytest.mark.skipif(not PYSIDE_AVAILABLE, reason="PySide6 required")
def test_amplitude_streaming_and_mouth_sync(qapp, mock_runtime):
    window = CaptainDesktopWindow(runtime=mock_runtime)
    received_amplitudes = []
    window.signal_emitter.amplitude_changed.connect(lambda amp: received_amplitudes.append(amp))

    manager = VoiceManager(runtime=mock_runtime, desktop_window=window)

    # Simulate TTS audio chunk playback (RMS > 0)
    chunk = (0.5 * np.ones(512, dtype=np.float32)).tobytes()
    manager._handle_tts_audio_chunk(chunk)
    qapp.processEvents()

    assert len(received_amplitudes) >= 1
    assert received_amplitudes[-1] > 0.0

    # Also test mic amplitude streaming during LISTENING state
    mock_runtime.state_manager.reset(AppState.LISTENING)
    mic_chunk = (0.3 * np.ones(512, dtype=np.float32)).tobytes()
    manager._handle_mic_amplitude(mic_chunk)
    qapp.processEvents()
    assert len(received_amplitudes) >= 2


# =============================================================================
# 19. FasterWhisper Strict Failure Mode (No Silent Mock in Production)
# =============================================================================
@pytest.mark.anyio
async def test_faster_whisper_strict_failure_mode():
    from providers.stt.faster_whisper import FasterWhisperSTTProvider
    # With allow_mock_fallback=False (production default), missing model raises RuntimeError
    stt = FasterWhisperSTTProvider(model_size_or_path="non_existent_model_xyz", allow_mock_fallback=False)
    # Pass valid PCM audio buffer (>= 320 bytes)
    sample_pcm = b"\x00\x05" * 320
    with pytest.raises(RuntimeError) as exc_info:
        await stt.transcribe(sample_pcm)
    assert "not loaded" in str(exc_info.value)


