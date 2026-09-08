"""
CAPTAIN AI OS 2.0 — APP STATE MACHINE.
Defines the authoritative state machine for Captain desktop agent:
- STANDBY: Low-power background listening mode (double-clap detector active)
- ACTIVE: Awakened, interactive, ready for interaction
- LISTENING: Audio capture / STT active
- THINKING: Reasoning, planning, LangGraph agent execution
- OBSERVING: Screen frame capture and OCR / vision inspection
- EXECUTING: Tool execution, computer automation, or system action
- SPEAKING: TTS speech synthesis and audio playback
- ERROR: Exception handling and fault recovery
"""

import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from pydantic import BaseModel, Field
from loguru import logger


class AppState(str, Enum):
    """Authoritative Captain AI OS Lifecycle & Operational States."""
    STANDBY = "STANDBY"
    ACTIVE = "ACTIVE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    OBSERVING = "OBSERVING"
    EXECUTING = "EXECUTING"
    SPEAKING = "SPEAKING"
    ERROR = "ERROR"


class StateTransitionEvent(BaseModel):
    """Structured record of a state machine transition."""
    timestamp: float = Field(default_factory=time.time)
    from_state: AppState
    to_state: AppState
    trigger: str = Field(default="system")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class InvalidStateTransitionError(Exception):
    """Raised when an illegal state transition is attempted without force=True."""
    pass


class StateManager:
    """
    Central Coordinator for Captain AI OS State Transitions.
    Enforces valid transition paths, maintains transition history,
    and notifies registered listeners/observers.
    """

    # Formal state transition graph
    VALID_TRANSITIONS: Dict[AppState, Set[AppState]] = {
        AppState.STANDBY: {
            AppState.ACTIVE,
            AppState.ERROR,
        },
        AppState.ACTIVE: {
            AppState.LISTENING,
            AppState.THINKING,
            AppState.OBSERVING,
            AppState.EXECUTING,
            AppState.SPEAKING,
            AppState.STANDBY,
            AppState.ERROR,
        },
        AppState.LISTENING: {
            AppState.THINKING,
            AppState.ACTIVE,
            AppState.STANDBY,
            AppState.ERROR,
        },
        AppState.THINKING: {
            AppState.OBSERVING,
            AppState.EXECUTING,
            AppState.SPEAKING,
            AppState.ACTIVE,
            AppState.STANDBY,
            AppState.ERROR,
        },
        AppState.OBSERVING: {
            AppState.THINKING,
            AppState.EXECUTING,
            AppState.SPEAKING,
            AppState.ACTIVE,
            AppState.STANDBY,
            AppState.ERROR,
        },
        AppState.EXECUTING: {
            AppState.THINKING,
            AppState.OBSERVING,
            AppState.SPEAKING,
            AppState.ACTIVE,
            AppState.STANDBY,
            AppState.ERROR,
        },
        AppState.SPEAKING: {
            AppState.LISTENING,
            AppState.ACTIVE,
            AppState.STANDBY,
            AppState.ERROR,
        },
        AppState.ERROR: {
            AppState.STANDBY,
            AppState.ACTIVE,
        },
    }

    def __init__(self, initial_state: AppState = AppState.STANDBY, max_history: int = 100):
        self._current_state: AppState = initial_state
        self._previous_state: Optional[AppState] = None
        self._max_history: int = max_history
        self._history: List[StateTransitionEvent] = []
        self._listeners: List[Callable[[StateTransitionEvent], None]] = []

    @property
    def current_state(self) -> AppState:
        """Get the current application state."""
        return self._current_state

    @property
    def previous_state(self) -> Optional[AppState]:
        """Get the preceding application state."""
        return self._previous_state

    @property
    def history(self) -> List[StateTransitionEvent]:
        """Get the history of state transitions."""
        return list(self._history)

    def is_state(self, state: AppState) -> bool:
        """Check if current state matches target."""
        return self._current_state == state

    def can_transition_to(self, target_state: AppState) -> bool:
        """Verify if transition from current state to target state is legally allowed."""
        if target_state == AppState.ERROR:
            return True  # Any state can transition to ERROR
        allowed = self.VALID_TRANSITIONS.get(self._current_state, set())
        return target_state in allowed

    def transition_to(
        self,
        target_state: AppState,
        trigger: str = "system",
        metadata: Optional[Dict[str, Any]] = None,
        force: bool = False
    ) -> StateTransitionEvent:
        """
        Transition application state.
        Raises InvalidStateTransitionError if transition is invalid and force=False.
        """
        if not force and not self.can_transition_to(target_state):
            error_msg = (
                f"Illegal state transition: Cannot transition from "
                f"{self._current_state.value} to {target_state.value} (trigger: '{trigger}')."
            )
            logger.error(error_msg)
            raise InvalidStateTransitionError(error_msg)

        event = StateTransitionEvent(
            from_state=self._current_state,
            to_state=target_state,
            trigger=trigger,
            metadata=metadata or {}
        )

        self._previous_state = self._current_state
        self._current_state = target_state

        # Append to history with bounded size
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history.pop(0)

        logger.info(
            f"StateTransition: {event.from_state.value} -> {event.to_state.value} "
            f"[trigger={event.trigger}]"
        )

        # Notify registered listeners
        self._notify_listeners(event)

        return event

    def subscribe(self, listener: Callable[[StateTransitionEvent], None]) -> None:
        """Register a callback listener to receive state transition events."""
        if listener not in self._listeners:
            self._listeners.append(listener)

    def unsubscribe(self, listener: Callable[[StateTransitionEvent], None]) -> None:
        """Remove a registered callback listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _notify_listeners(self, event: StateTransitionEvent) -> None:
        """Notify all subscribers safely without letting subscriber errors crash the state manager."""
        for listener in self._listeners:
            try:
                listener(event)
            except Exception as e:
                logger.warning(f"StateManager: Error in state transition listener callback: {e}")

    def reset(self, state: AppState = AppState.STANDBY) -> None:
        """Hard reset state manager to specified state without validation."""
        self._previous_state = self._current_state
        self._current_state = state
        self._history.clear()
