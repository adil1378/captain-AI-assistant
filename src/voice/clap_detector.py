"""
CAPTAIN AI OS 2.0 — LOCAL DOUBLE-CLAP DETECTOR.
Detects deliberate acoustic DOUBLE-CLAP gestures using transient energy,
crest-factor analysis, and temporal window gating:
- First clap impulse: starts interval window [clap_min_interval_ms, clap_max_interval_ms]
- Second clap impulse: confirms double-clap gesture and triggers state toggle
- Cooldown period: prevents reverberation and echo false-positives
"""

import time
import numpy as np
from typing import Optional
from loguru import logger

from config import settings
from app.state import AppState, StateManager, StateTransitionEvent


class ClapDetector:
    """
    Acoustic Double-Clap Impulse Detector.
    Requires two distinct sharp transients within the configured interval window
    (default: 150ms to 800ms) to trigger activation or standby.
    """

    def __init__(
        self,
        threshold: Optional[float] = None,
        cooldown_sec: Optional[float] = None,
        min_interval_ms: Optional[int] = None,
        max_interval_ms: Optional[int] = None,
        sample_rate: Optional[int] = None,
    ):
        self.threshold = threshold if threshold is not None else settings.clap_threshold
        self.cooldown_sec = cooldown_sec if cooldown_sec is not None else settings.clap_cooldown
        self.min_interval_ms = min_interval_ms if min_interval_ms is not None else settings.clap_min_interval_ms
        self.max_interval_ms = max_interval_ms if max_interval_ms is not None else settings.clap_max_interval_ms
        self.sample_rate = sample_rate or settings.clap_sample_rate

        self._first_clap_time: float = 0.0
        self._last_double_clap_time: float = 0.0
        self._enabled: bool = settings.clap_enabled

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def reset(self) -> None:
        """Reset internal detector state."""
        self._first_clap_time = 0.0
        self._last_double_clap_time = 0.0

    def is_impulse(self, frame: np.ndarray) -> bool:
        """Check if an audio frame represents a sharp acoustic impulse."""
        if frame is None or len(frame) == 0:
            return False

        if frame.dtype == np.int16:
            audio = frame.astype(np.float32) / 32768.0
        elif frame.dtype in (np.float32, np.float64):
            audio = frame.astype(np.float32)
        else:
            audio = np.asarray(frame, dtype=np.float32)

        peak = float(np.max(np.abs(audio)))
        rms = float(np.sqrt(np.mean(audio ** 2))) + 1e-9

        if peak < self.threshold:
            return False

        # Transient / Crest-Factor Analysis
        crest_factor = peak / rms
        return crest_factor >= 2.8 and (rms < 0.35)

    def process_frame(self, frame: np.ndarray, timestamp: Optional[float] = None) -> bool:
        """
        Process a single mono audio frame.
        Returns True ONLY when a complete, valid DOUBLE-CLAP sequence is registered.
        """
        if not self._enabled:
            return False

        if not self.is_impulse(frame):
            return False

        now = timestamp if timestamp is not None else time.time()
        return self.register_impulse(now)

    def register_impulse(self, now: Optional[float] = None) -> bool:
        """
        Register a verified clap impulse into the double-clap temporal state machine.
        Returns True if this impulse successfully completes a valid double-clap.
        """
        now = now if now is not None else time.time()

        # 1. Cooldown guard: must exceed cooldown period since last double-clap
        if (now - self._last_double_clap_time) < self.cooldown_sec:
            logger.debug("ClapDetector: Impulse ignored during post-activation cooldown.")
            return False

        # 2. Check if this is the first clap candidate of a pair
        if self._first_clap_time == 0.0:
            self._first_clap_time = now
            logger.info(
                f"ClapDetector: First clap detected! Awaiting second clap within "
                f"[{self.min_interval_ms}ms, {self.max_interval_ms}ms]..."
            )
            return False

        # 3. An initial clap was already recorded; evaluate interval to second clap
        elapsed_ms = (now - self._first_clap_time) * 1000.0

        if elapsed_ms < self.min_interval_ms:
            # Too fast — likely echo, reverberation, or double bounce of first clap
            logger.debug(f"ClapDetector: Impulse rejected as reverberation ({elapsed_ms:.1f}ms < {self.min_interval_ms}ms).")
            return False

        elif self.min_interval_ms <= elapsed_ms <= self.max_interval_ms:
            # Valid DOUBLE-CLAP gesture registered!
            logger.info(
                f"ClapDetector: Valid DOUBLE-CLAP confirmed! (interval={elapsed_ms:.1f}ms)"
            )
            self._first_clap_time = 0.0
            self._last_double_clap_time = now
            return True

        else:
            # elapsed_ms > max_interval_ms: window expired; treat as a NEW first clap candidate
            logger.info(
                f"ClapDetector: Interval expired ({elapsed_ms:.1f}ms > {self.max_interval_ms}ms). Resetting as new first clap."
            )
            self._first_clap_time = now
            return False

    def handle_state_toggle(self, state_manager: StateManager) -> Optional[StateTransitionEvent]:
        """
        State-aware double-clap toggle logic conforming strictly to StateManager rules:
        - STANDBY + double-clap -> ACTIVE
        - ACTIVE + double-clap -> STANDBY
        - LISTENING, THINKING, SPEAKING, EXECUTING, OBSERVING -> ignored to avoid accidental shutdown.
        """
        current = state_manager.current_state

        if current == AppState.STANDBY:
            logger.info("ClapDetector: Toggling STANDBY -> ACTIVE via double-clap activation.")
            return state_manager.transition_to(AppState.ACTIVE, trigger="double_clap_activation")

        elif current == AppState.ACTIVE:
            logger.info("ClapDetector: Toggling ACTIVE -> STANDBY via double-clap deactivation.")
            return state_manager.transition_to(AppState.STANDBY, trigger="double_clap_deactivation")

        else:
            logger.debug(
                f"ClapDetector: Double-clap ignored during active operational state: {current.value}"
            )
            return None
