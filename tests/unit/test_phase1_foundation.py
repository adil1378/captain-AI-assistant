"""
CAPTAIN AI OS 2.0 — PHASE 1 FOUNDATION TEST SUITE.
Validates:
1. Centralized Pydantic Settings (config.py & src/backend/config.py backward compatibility)
2. Desktop State Machine (app/state.py: STANDBY, ACTIVE, LISTENING, etc.)
3. App Runtime Coordinator (app/runtime.py: lifecycle, providers, health)
4. Provider Abstractions (providers/base.py, providers/llm/)
5. Decoupling from legacy core/llm_factory.py
"""

import pytest
import asyncio
from pathlib import Path

from config import Settings, settings
from app.state import AppState, StateManager, StateTransitionEvent, InvalidStateTransitionError
from app.runtime import AppRuntime
from providers.base import ProviderMetadata, BaseProvider, LLMProvider, VisionProvider, STTProvider, TTSProvider
from providers.llm.base import BaseLLM
from providers.llm.ollama import OllamaLLM
from providers.llm.factory import get_llm, get_llm_provider


# =============================================================================
# 1. CENTRALIZED CONFIGURATION TESTS
# =============================================================================

def test_central_config_defaults():
    """Verify default configurations for Phase 1 Desktop Native specifications."""
    assert settings.app_name == "Captain AI OS"
    assert settings.app_version == "2.0.0"
    assert settings.llm_provider == "ollama"
    assert settings.vision_provider == "ollama"
    assert settings.stt_provider == "local"
    assert settings.tts_provider == "pyttsx3"


def test_central_config_ollama_and_audio():
    """Verify Ollama settings and double-clap acoustic parameters."""
    assert "11434" in settings.ollama_base_url
    assert settings.clap_threshold == 0.65
    assert settings.clap_min_interval_ms == 150
    assert settings.clap_max_interval_ms == 800
    assert settings.clap_sample_rate in (16000, 44100)
    assert settings.clap_chunk_size in (512, 1024)


def test_central_config_screen_and_security():
    """Verify screen observation parameters and security confirmation policies."""
    assert settings.screen_monitor_index == 1
    assert settings.screen_capture_interval_sec == 2.0
    assert settings.screen_resize_factor == 0.5
    assert settings.screen_enable_ocr is True

    assert settings.require_confirmation_for_fs_delete is True
    assert settings.require_confirmation_for_sys_exec is True
    assert settings.require_confirmation_for_mouse_keyboard is True
    assert settings.security_risk_threshold == "MEDIUM"


def test_central_config_directories_ensure():
    """Verify standard directories are properly instantiated."""
    settings.ensure_directories()
    assert settings.data_dir.exists()
    assert settings.logs_dir.exists()
    assert settings.scratch_dir.exists()
    assert settings.memory_dir.exists()
    assert settings.vectorstore_dir.exists()


def test_central_config_backward_compatibility_casing():
    """Verify case-insensitivity allows both lowercase and legacy uppercase access."""
    assert settings.chat_model == settings.CHAT_MODEL
    assert settings.ollama_base_url == settings.OLLAMA_BASE_URL
    assert settings.default_provider == settings.DEFAULT_PROVIDER


def test_backend_config_reexport_transparency():
    """Verify src.backend.config re-exports identical centralized settings instance."""
    from src.backend.config import settings as backend_settings
    assert backend_settings is settings
    assert backend_settings.CHAT_MODEL == settings.chat_model


# =============================================================================
# 2. STATE MACHINE (app/state.py) TESTS
# =============================================================================

def test_state_machine_initial_standby():
    """Verify state machine initializes in low-power STANDBY state."""
    sm = StateManager()
    assert sm.current_state == AppState.STANDBY
    assert sm.previous_state is None
    assert len(sm.history) == 0


def test_state_machine_valid_full_lifecycle():
    """Verify full legal operational cycle: STANDBY -> ACTIVE -> LISTENING -> THINKING -> EXECUTING -> SPEAKING -> STANDBY."""
    sm = StateManager()

    # 1. Wake via clap
    ev1 = sm.transition_to(AppState.ACTIVE, trigger="double_clap")
    assert sm.current_state == AppState.ACTIVE
    assert ev1.from_state == AppState.STANDBY
    assert ev1.to_state == AppState.ACTIVE
    assert ev1.trigger == "double_clap"

    # 2. Voice input starts
    sm.transition_to(AppState.LISTENING, trigger="user_voice")
    assert sm.current_state == AppState.LISTENING

    # 3. Speech ended, agent begins thinking
    sm.transition_to(AppState.THINKING, trigger="stt_completed")
    assert sm.current_state == AppState.THINKING

    # 4. Agent decides to execute tool
    sm.transition_to(AppState.EXECUTING, trigger="tool_call")
    assert sm.current_state == AppState.EXECUTING

    # 5. Tool completed, agent speaks output
    sm.transition_to(AppState.SPEAKING, trigger="tts_start")
    assert sm.current_state == AppState.SPEAKING

    # 6. Speech finished, returns to active
    sm.transition_to(AppState.ACTIVE, trigger="tts_end")
    assert sm.current_state == AppState.ACTIVE

    # 7. Inactivity timeout returns to standby
    sm.transition_to(AppState.STANDBY, trigger="inactivity_timeout")
    assert sm.current_state == AppState.STANDBY

    assert len(sm.history) == 7


def test_state_machine_observing_cycle():
    """Verify screen vision OBSERVING transition path."""
    sm = StateManager(initial_state=AppState.ACTIVE)

    sm.transition_to(AppState.OBSERVING, trigger="screen_inspect")
    assert sm.current_state == AppState.OBSERVING

    sm.transition_to(AppState.THINKING, trigger="frame_analyzed")
    assert sm.current_state == AppState.THINKING


def test_state_machine_illegal_transition_rejection():
    """Verify illegal transition (e.g. STANDBY directly to EXECUTING) raises InvalidStateTransitionError."""
    sm = StateManager(initial_state=AppState.STANDBY)

    with pytest.raises(InvalidStateTransitionError):
        sm.transition_to(AppState.EXECUTING, trigger="unauthorized_jump")

    # Current state must remain unchanged
    assert sm.current_state == AppState.STANDBY


def test_state_machine_force_transition():
    """Verify force=True bypasses transition constraints for emergency recovery."""
    sm = StateManager(initial_state=AppState.STANDBY)
    sm.transition_to(AppState.EXECUTING, trigger="emergency_force", force=True)
    assert sm.current_state == AppState.EXECUTING


def test_state_machine_error_transition_and_recovery():
    """Verify any state can jump to ERROR, and ERROR can recover to ACTIVE or STANDBY."""
    sm = StateManager(initial_state=AppState.THINKING)
    sm.transition_to(AppState.ERROR, trigger="llm_timeout")
    assert sm.current_state == AppState.ERROR

    # Recover to ACTIVE
    sm.transition_to(AppState.ACTIVE, trigger="error_dismissed")
    assert sm.current_state == AppState.ACTIVE


def test_state_machine_listener_callback():
    """Verify subscriber callbacks are invoked synchronously on transition."""
    sm = StateManager()
    captured_events = []

    def callback(event: StateTransitionEvent):
        captured_events.append(event)

    sm.subscribe(callback)
    sm.transition_to(AppState.ACTIVE, trigger="wake")

    assert len(captured_events) == 1
    assert captured_events[0].from_state == AppState.STANDBY
    assert captured_events[0].to_state == AppState.ACTIVE


# =============================================================================
# 3. APPLICATION RUNTIME (app/runtime.py) TESTS
# =============================================================================

def test_app_runtime_lifecycle():
    async def _test():
        runtime = AppRuntime(initial_state=AppState.STANDBY)
        assert runtime.current_state == AppState.STANDBY

        # Initialize
        ok = await runtime.initialize()
        assert ok is True
        assert runtime.is_running is True

        # State transition helpers
        runtime.wake(trigger="test_wake")
        assert runtime.current_state == AppState.ACTIVE

        runtime.listen()
        assert runtime.current_state == AppState.LISTENING

        runtime.think()
        assert runtime.current_state == AppState.THINKING

        runtime.observe()
        assert runtime.current_state == AppState.OBSERVING

        runtime.execute()
        assert runtime.current_state == AppState.EXECUTING

        runtime.speak()
        assert runtime.current_state == AppState.SPEAKING

        runtime.sleep()
        assert runtime.current_state == AppState.STANDBY

        # Health status check
        health = await runtime.health_status()
        assert health["runtime_active"] is True
        assert health["app_name"] == "Captain AI OS"
        assert "providers" in health

        # Graceful shutdown
        await runtime.shutdown()
        assert runtime.is_running is False
        assert runtime.current_state == AppState.STANDBY

    asyncio.run(_test())


# =============================================================================
# 4. PROVIDER ABSTRACTION & FACTORY TESTS
# =============================================================================

class MockProvider(BaseProvider):
    @property
    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name="mock_vision",
            provider_type="vision",
            version="1.0.0",
            is_local=True
        )

    async def initialize(self) -> bool:
        return True

    async def health_check(self) -> bool:
        return True

    async def shutdown(self) -> None:
        pass


def test_provider_registration_in_runtime():
    runtime = AppRuntime()
    mock_prov = MockProvider()
    runtime.register_provider(mock_prov)

    retrieved = runtime.get_provider("vision")
    assert retrieved is not None
    assert retrieved.metadata.name == "mock_vision"


def test_ollama_llm_provider_instantiation():
    """Verify OllamaLLM creates valid instance with IPv4 normalization."""
    prov = OllamaLLM(model_name="llama3.2", base_url="http://localhost:11434")
    assert "127.0.0.1" in prov.base_url
    assert prov.metadata.name == "ollama"
    assert prov.metadata.is_local is True

    langchain_model = prov.get_langchain_model()
    assert langchain_model is not None


def test_llm_factory_migrated_functions():
    """Verify get_llm and get_llm_provider drop-in compatibility."""
    # Test factory returns BaseLLM
    prov = get_llm_provider(provider="ollama", model_name="llama3.2")
    assert isinstance(prov, BaseLLM)

    # Test get_llm returns LangChain ChatModel
    chat_model = get_llm(provider="ollama", model_name="llama3.2")
    assert chat_model is not None

    # Test unknown provider falls back gracefully to Ollama
    fallback_model = get_llm(provider="unknown_provider_xyz")
    assert fallback_model is not None


def test_legacy_agent_import_compatibility():
    """Verify legacy agent files can import get_llm from providers.llm without core.llm_factory."""
    from agents.chat_agent import chat_agent_node
    from agents.coder_agent import coder_agent_node
    from agents.system_agent import system_agent_node

    assert callable(chat_agent_node)
    assert callable(coder_agent_node)
    assert callable(system_agent_node)
