"""
Captain AI OS - Autonomous Learning Engine (Volume 12 Part 12A)
Responsible for operational experience collection, explainable pattern discovery,
confidence validation, controlled knowledge promotion, feedback tuning, and versioned rollbacks.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import time
from pydantic import BaseModel, Field
from src.backend.core.permission_manager import PermissionManager, Permission
from src.backend.core.privacy_manager import PrivacyGovernanceManager


class ExperienceType(str, Enum):
    USER_REQUEST = "USER_REQUEST"
    WORKFLOW_RESULT = "WORKFLOW_RESULT"
    TOOL_USAGE = "TOOL_USAGE"
    AGENT_COLLAB = "AGENT_COLLAB"
    ERROR_RECOVERY = "ERROR_RECOVERY"
    FEEDBACK_SIGNAL = "FEEDBACK_SIGNAL"


class LearningState(str, Enum):
    CAPTURED = "CAPTURED"
    PATTERN_DISCOVERED = "PATTERN_DISCOVERED"
    VALIDATING = "VALIDATING"
    PROMOTED = "PROMOTED"
    REJECTED = "REJECTED"
    ROLLED_BACK = "ROLLED_BACK"


class ExperienceRecord(BaseModel):
    experience_id: str
    experience_type: ExperienceType
    actor_id: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    success_score: float = 1.0  # 0.0 to 1.0
    timestamp: float = Field(default_factory=time.time)


class LearnedPattern(BaseModel):
    pattern_id: str
    pattern_name: str
    confidence_score: float  # 0.0 to 1.0
    frequency_count: int = 1
    template_payload: Dict[str, Any] = Field(default_factory=dict)
    state: LearningState = LearningState.PATTERN_DISCOVERED
    version: int = 1
    created_at: float = Field(default_factory=time.time)


class PatternAnalyzer:
    """Discovers reusable execution patterns and strategies from collected experiences."""

    @staticmethod
    def analyze(experiences: List[ExperienceRecord]) -> List[LearnedPattern]:
        patterns = []
        action_counts: Dict[str, List[float]] = {}

        for exp in experiences:
            action = exp.payload.get("action", "unknown_action")
            if action not in action_counts:
                action_counts[action] = []
            action_counts[action].append(exp.success_score)

        for action, scores in action_counts.items():
            freq = len(scores)
            avg_success = sum(scores) / freq if freq > 0 else 0.0
            confidence = round(min(1.0, (avg_success * 0.7) + (min(freq, 10) / 10.0 * 0.3)), 2)

            if confidence >= 0.75:
                patterns.append(
                    LearnedPattern(
                        pattern_id=f"pat_{hash(action) & 0xffffff}",
                        pattern_name=f"Optimized Strategy for {action}",
                        confidence_score=confidence,
                        frequency_count=freq,
                        template_payload={"action": action, "recommended_strategy": "fast_path"}
                    )
                )

        return patterns


class AutonomousLearningEngine:
    """Centralized Autonomous Learning & Controlled Knowledge Promotion Manager."""

    def __init__(self, promotion_threshold: float = 0.85):
        self.promotion_threshold = promotion_threshold
        self.experiences: List[ExperienceRecord] = []
        self.discovered_patterns: Dict[str, LearnedPattern] = {}
        self.promoted_knowledge: Dict[str, LearnedPattern] = {}
        self.privacy_manager = PrivacyGovernanceManager()
        self.permission_manager = PermissionManager()
        self.analytics = {
            "experiences_collected": 0,
            "patterns_discovered": 0,
            "promotions_count": 0,
            "rejections_count": 0
        }

    def collect_experience(
        self,
        experience_type: ExperienceType,
        actor_id: str,
        payload: Dict[str, Any],
        success_score: float = 1.0
    ) -> ExperienceRecord:
        """Captures operational experience, redacting sensitive PII from payload fields."""
        masked_payload = {}
        for k, v in payload.items():
            if isinstance(v, str):
                masked_payload[k] = self.privacy_manager.mask_sensitive_data(v)
            else:
                masked_payload[k] = v

        exp_id = f"exp_{int(time.time() * 1000)}"
        record = ExperienceRecord(
            experience_id=exp_id,
            experience_type=experience_type,
            actor_id=actor_id,
            payload=masked_payload,
            success_score=max(0.0, min(1.0, success_score))
        )
        self.experiences.append(record)
        self.analytics["experiences_collected"] += 1
        return record

    def discover_patterns(self) -> List[LearnedPattern]:
        """Discovers candidates for knowledge promotion from operational history."""
        patterns = PatternAnalyzer.analyze(self.experiences)
        for pat in patterns:
            self.discovered_patterns[pat.pattern_id] = pat
        self.analytics["patterns_discovered"] = len(self.discovered_patterns)
        return patterns

    def validate_and_promote(self, pattern_id: str) -> bool:
        """Evaluates pattern confidence against governance rules and promotes knowledge."""
        if pattern_id not in self.discovered_patterns:
            raise KeyError(f"Learned pattern '{pattern_id}' not found.")

        pattern = self.discovered_patterns[pattern_id]
        if pattern.confidence_score < self.promotion_threshold:
            pattern.state = LearningState.REJECTED
            self.analytics["rejections_count"] += 1
            raise ValueError(f"Pattern confidence ({pattern.confidence_score}) is below promotion threshold ({self.promotion_threshold}).")

        pattern.state = LearningState.PROMOTED
        self.promoted_knowledge[pattern_id] = pattern
        self.analytics["promotions_count"] += 1
        return True

    def rollback_promotion(self, pattern_id: str) -> bool:
        """Rolls back a promoted knowledge insight in case of negative feedback or regression."""
        if pattern_id not in self.promoted_knowledge:
            return False

        pat = self.promoted_knowledge[pattern_id]
        pat.state = LearningState.ROLLED_BACK
        del self.promoted_knowledge[pattern_id]
        return True

    def get_learning_analytics(self) -> Dict[str, Any]:
        """Returns analytics summary for learning events and promotion accuracy."""
        return {
            "experiences_count": len(self.experiences),
            "patterns_discovered_count": len(self.discovered_patterns),
            "promoted_knowledge_count": len(self.promoted_knowledge),
            "analytics_summary": self.analytics
        }
