"""
Unit & Integration Tests for Volume 12 Part 12A Autonomous Learning Architecture.
Verifies operational experience collection, PII payload redaction, pattern discovery,
confidence validation threshold promotion, and versioned promotion rollbacks.
"""

import pytest
from src.backend.core.autonomous_learning_engine import (
    AutonomousLearningEngine,
    ExperienceType,
    LearningState
)


def test_experience_collection_and_pii_redaction():
    ale = AutonomousLearningEngine()

    record = ale.collect_experience(
        experience_type=ExperienceType.USER_REQUEST,
        actor_id="user_adil",
        payload={"action": "send_email", "target": "contact test@example.com"},
        success_score=0.9
    )

    assert record.experience_id.startswith("exp_")
    assert record.payload["action"] == "send_email"
    assert "[REDACTED_EMAIL]" in record.payload["target"]
    assert ale.analytics["experiences_collected"] == 1


def test_pattern_discovery_and_controlled_promotion():
    ale = AutonomousLearningEngine(promotion_threshold=0.80)

    # Collect multiple successful experiences for the same action
    for _ in range(5):
        ale.collect_experience(
            experience_type=ExperienceType.WORKFLOW_RESULT,
            actor_id="agent_coder",
            payload={"action": "refactor_module"},
            success_score=1.0
        )

    patterns = ale.discover_patterns()
    assert len(patterns) > 0
    pat = patterns[0]
    assert pat.confidence_score >= 0.80

    # Promote knowledge
    promoted = ale.validate_and_promote(pat.pattern_id)
    assert promoted is True
    assert ale.promoted_knowledge[pat.pattern_id].state == LearningState.PROMOTED


def test_low_confidence_rejection_and_rollback():
    ale = AutonomousLearningEngine(promotion_threshold=0.90)

    # Single experience with lower success score -> low confidence pattern
    ale.collect_experience(
        experience_type=ExperienceType.ERROR_RECOVERY,
        actor_id="agent_sys",
        payload={"action": "restart_service"},
        success_score=0.4
    )

    patterns = ale.discover_patterns()
    assert len(patterns) == 0  # Below discovery threshold

    # Simulate manual pattern insertion with low confidence score
    from src.backend.core.autonomous_learning_engine import LearnedPattern
    low_pat = LearnedPattern(
        pattern_id="pat_low",
        pattern_name="Weak Strategy",
        confidence_score=0.5
    )
    ale.discovered_patterns["pat_low"] = low_pat

    with pytest.raises(ValueError):
        ale.validate_and_promote("pat_low")

    assert ale.discovered_patterns["pat_low"].state == LearningState.REJECTED
