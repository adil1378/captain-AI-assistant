"""
CAPTAIN AI OS 2.0 — APPLICATION RUNTIME COORDINATOR.
Orchestrates application lifecycle, provider registrations, state transitions,
health diagnostics, and safe shutdown.
"""

import asyncio
from typing import Any, Dict, List, Optional
from loguru import logger

from config import settings
from app.state import AppState, StateManager, StateTransitionEvent
from providers.base import BaseProvider, LLMProvider, VisionProvider, STTProvider, TTSProvider
from providers.llm.factory import get_llm_provider


class AppRuntime:
    """
    Central Runtime Engine for Captain AI OS 2.0.
    Coordinates the agent state machine, providers, local storage,
    and event telemetry.
    """

    def __init__(self, initial_state: AppState = AppState.STANDBY):
        self.state_manager = StateManager(initial_state=initial_state)
        self._providers: Dict[str, BaseProvider] = {}
        self._is_running: bool = False
        self._wire_internal_event_bus()

    @property
    def current_state(self) -> AppState:
        """Return the current operational state."""
        return self.state_manager.current_state

    @property
    def is_running(self) -> bool:
        """Return whether runtime is active and initialized."""
        return self._is_running

    def _wire_internal_event_bus(self) -> None:
        """Forward state machine transitions to event bus if available."""
        def _on_state_transition(event: StateTransitionEvent):
            try:
                import asyncio
                from src.backend.core.event_bus import event_bus
                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        loop.create_task(
                            event_bus.publish(
                                "AppStateChanged",
                                "AppRuntime",
                                {
                                    "from_state": event.from_state.value,
                                    "to_state": event.to_state.value,
                                    "trigger": event.trigger,
                                    "timestamp": event.timestamp,
                                }
                            )
                        )
                except RuntimeError:
                    # No running event loop in current thread/context
                    pass
            except Exception:
                pass

        self.state_manager.subscribe(_on_state_transition)

    def register_provider(self, provider: BaseProvider) -> None:
        """Register a provider instance (LLM, Vision, STT, TTS)."""
        ptype = provider.metadata.provider_type.lower()
        self._providers[ptype] = provider
        logger.info(f"AppRuntime: Registered {ptype.upper()} provider '{provider.metadata.name}' (v{provider.metadata.version})")

    def get_provider(self, provider_type: str) -> Optional[BaseProvider]:
        """Retrieve a registered provider by type."""
        return self._providers.get(provider_type.lower())

    async def initialize(self) -> bool:
        """
        Initialize runtime, ensure file directories exist,
        and bootstrap the default LLM provider.
        """
        logger.info(f"AppRuntime: Initializing Captain AI OS 2.0 (state: {self.current_state.value})...")

        # 1. Guarantee standard storage directories exist
        settings.ensure_directories()

        # 2. Register default LLM provider if not already registered
        if "llm" not in self._providers:
            try:
                default_llm = get_llm_provider()
                self.register_provider(default_llm)
            except Exception as e:
                logger.warning(f"AppRuntime: Default LLM provider registration deferred: {e}")

        # 3. Initialize all registered providers
        for ptype, prov in self._providers.items():
            try:
                await prov.initialize()
            except Exception as e:
                logger.warning(f"AppRuntime: Provider '{ptype}' initialization returned: {e}")

        self._is_running = True
        logger.info("AppRuntime: Initialization complete.")
        return True

    async def health_status(self) -> Dict[str, Any]:
        """Collect diagnostic health metrics across runtime and registered providers."""
        provider_health: Dict[str, bool] = {}
        for ptype, prov in self._providers.items():
            try:
                provider_health[ptype] = await prov.health_check()
            except Exception:
                provider_health[ptype] = False

        return {
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "runtime_active": self._is_running,
            "current_state": self.current_state.value,
            "providers": provider_health,
            "data_directories": {
                "data_dir": str(settings.data_dir),
                "data_dir_exists": settings.data_dir.exists(),
                "logs_dir_exists": settings.logs_dir.exists(),
                "vectorstore_dir_exists": settings.vectorstore_dir.exists(),
            }
        }

    # =========================================================================
    # STATE TRANSITION HELPERS
    # =========================================================================
    def wake(self, trigger: str = "wake_trigger", metadata: Optional[Dict[str, Any]] = None) -> None:
        """Transition from STANDBY to ACTIVE."""
        self.state_manager.transition_to(AppState.ACTIVE, trigger=trigger, metadata=metadata)

    def sleep(self, trigger: str = "sleep_trigger", metadata: Optional[Dict[str, Any]] = None) -> None:
        """Transition from ACTIVE to STANDBY."""
        self.state_manager.transition_to(AppState.STANDBY, trigger=trigger, metadata=metadata)

    def listen(self, trigger: str = "voice_input_started") -> None:
        """Transition to LISTENING state."""
        self.state_manager.transition_to(AppState.LISTENING, trigger=trigger)

    def think(self, trigger: str = "reasoning_started") -> None:
        """Transition to THINKING state."""
        self.state_manager.transition_to(AppState.THINKING, trigger=trigger)

    def observe(self, trigger: str = "screen_observation_started") -> None:
        """Transition to OBSERVING state."""
        self.state_manager.transition_to(AppState.OBSERVING, trigger=trigger)

    def execute(self, trigger: str = "tool_execution_started") -> None:
        """Transition to EXECUTING state."""
        self.state_manager.transition_to(AppState.EXECUTING, trigger=trigger)

    def speak(self, trigger: str = "tts_speech_started") -> None:
        """Transition to SPEAKING state."""
        self.state_manager.transition_to(AppState.SPEAKING, trigger=trigger)

    def error(self, reason: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Transition to ERROR state from any current state."""
        self.state_manager.transition_to(AppState.ERROR, trigger=reason, metadata=metadata)

    def recover(self, target: AppState = AppState.ACTIVE) -> None:
        """Recover from ERROR back to ACTIVE or STANDBY."""
        self.state_manager.transition_to(target, trigger="error_recovered")

    async def shutdown(self) -> None:
        """Gracefully release providers and reset state to STANDBY."""
        logger.info("AppRuntime: Shutting down Captain AI OS 2.0...")
        for ptype, prov in self._providers.items():
            try:
                await prov.shutdown()
            except Exception as e:
                logger.warning(f"AppRuntime: Provider '{ptype}' shutdown error: {e}")

        self._providers.clear()
        self._is_running = False
        self.state_manager.reset(AppState.STANDBY)
        logger.info("AppRuntime: Shutdown complete.")


# Global Application Runtime Singleton
runtime = AppRuntime()
