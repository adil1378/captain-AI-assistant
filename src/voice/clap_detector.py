"""
CAPTAIN AI OS 2.0 — LOCAL CLAP DETECTOR.
Detects deliberate acoustic clap gestures using transient energy and peak-to-average
duration analysis with debounce cooldown.
Safeguards against false triggers from speech and ambient noise.
"""

import time
import numpy as np
from typing import Optional
from loguru import logger

from config import settings
from app.state import AppState, StateManager, StateTransitionEvent


class ClapDetector:
    """
    Acoustic clap impulse detector.
    Analyzes short audio frames for high-energy transients with sharp rise and rapid decay.
    """

    def __init__(
        self,
        threshold: Optional[float] = None,
        cooldown_sec: Optional[float] = None,
        sample_rate: Optional[int] = None,
    ):
        self.threshold = threshold if threshold is not None else settings.clap_threshold
        self.cooldown_sec = cooldown_sec if cooldown_sec is not None else settings.clap_cooldown
        self.sample_rate = sample_rate or settings.clap_sample_rate

        self._last_clap_time: float = 0.0
        self._consecutive_silent_frames: int = 0
        self._enabled: bool = settings.clap_enabled

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def reset(self) -> None:
        """Reset internal detector state."""
        self._last_clap_time = 0.0
        self._consecutive_silent_frames = 0

    def process_frame(self, frame: np.ndarray) -> bool:
        """
        Process a single mono audio frame (np.float32 or np.int16).
        Returns True if a valid deliberate clap transient is registered.
        """
        if not self._enabled or frame is None or len(frame) == 0:
            return False

        # Convert int16 to float32 normalized [-1.0, 1.0] if necessary
        if frame.dtype == np.int16:
            audio = frame.astype(np.float32) / 32768.0
        elif frame.dtype in (np.float32, np.float64):
            audio = frame.astype(np.float32)
        else:
            audio = np.asarray(frame, dtype=np.float32)

        peak = float(np.max(np.abs(audio)))
        rms = float(np.sqrt(np.mean(audio ** 2))) + 1e-9

        # Check peak threshold
        if peak < self.threshold:
            self._consecutive_silent_frames += 1
            return False

        now = time.time()
        # Cooldown guard: must exceed cooldown period since last clap
        if (now - self._last_clap_time) < self.cooldown_sec:
            return False

        # Transient / Crest-Factor Analysis:
        # Claps have an abrupt, sharp impulse (crest factor > 3.0) and very low sustained RMS.
        # Continuous loud speech or screaming has a high RMS and lower crest factor.
        crest_factor = peak / rms
        is_impulsive = crest_factor >= 2.8 and (rms < 0.35)

        if not is_impulsive:
            # Likely speech or background noise, not a sharp clap
            return False

        self._last_clap_time = now
        self._consecutive_silent_frames = 0
        logger.info(f"ClapDetector: Deliberate clap detected! (peak={peak:.3f}, crest={crest_factor:.2f})")
        return True

    def handle_state_toggle(self, state_manager: StateManager) -> Optional[StateTransitionEvent]:
        """
        State-aware clap toggle logic conforming strictly to StateManager rules:
        - STANDBY + clap -> ACTIVE
        - ACTIVE + clap -> STANDBY
        - LISTENING, THINKING, SPEAKING, EXECUTING, OBSERVING -> ignored to avoid accidental shutdown.
        """
        current = state_manager.current_state

        if current == AppState.STANDBY:
            logger.info("ClapDetector: Toggling STANDBY -> ACTIVE via clap activation.")
            return state_manager.transition_to(AppState.ACTIVE, trigger="clap_activation")

        elif current == AppState.ACTIVE:
            logger.info("ClapDetector: Toggling ACTIVE -> STANDBY via clap deactivation.")
            return state_manager.transition_to(AppState.STANDBY, trigger="clap_deactivation")

        else:
            logger.debug(
                f"ClapDetector: Transient ignored during active operation state: {current.value}"
            )
            return None
