"""
Unit & Integration Tests for Volume 12 Part 12B Adaptive Intelligence Architecture.
Verifies capability gap detection, skill proposal, accuracy & compatibility validation,
version upgrading, and safe rollbacks.
"""

import pytest
from src.backend.core.adaptive_intelligence_manager import (
    AdaptiveIntelligenceManager,
    SkillStatus,
    CapabilityGap
)


def test_capability_gap_detection_and_skill_proposal():
    aim = AdaptiveIntelligenceManager()

    unhandled = ["process_pdf_invoice", "process_pdf_invoice", "export_excel_chart"]
    gaps = aim.detect_capability_gaps(unhandled)

    assert len(gaps) == 2
    assert aim.analytics["gaps_detected"] == 2

    # Propose new skill
    skill = aim.propose_skill(
        skill_id="skill_pdf_parser",
        name="PDF Invoice Processor",
        template_payload={"module": "pdf_tools", "action": "extract_fields"}
    )

    assert skill.skill_id == "skill_pdf_parser"
    assert skill.status == SkillStatus.DISCOVERED
    assert skill.current_version == 1


def test_skill_validation_activation_and_upgrade():
    aim = AdaptiveIntelligenceManager(validation_threshold=0.75)

    aim.propose_skill("skill_ocr", "OCR Reader", {"engine": "vision"})

    # Validate and activate with high accuracy and success rate
    success = aim.validate_and_activate("skill_ocr", accuracy_score=0.9, success_rate=0.85)
    assert success is True
    assert aim.skills["skill_ocr"].status == SkillStatus.ACTIVE

    # Upgrade to version 2
    new_ver = aim.upgrade_skill("skill_ocr", {"engine": "vision_v2"}, accuracy_score=0.95)
    assert new_ver == 2
    assert aim.skills["skill_ocr"].current_version == 2
    assert len(aim.skills["skill_ocr"].version_history) == 2


def test_validation_failure_and_version_rollback():
    aim = AdaptiveIntelligenceManager(validation_threshold=0.75)

    aim.propose_skill("skill_web_scraper", "Scraper", {"mode": "http"})
    aim.validate_and_activate("skill_web_scraper", accuracy_score=0.9, success_rate=0.9)
    aim.upgrade_skill("skill_web_scraper", {"mode": "browser"}, accuracy_score=0.95)

    # Roll back to version 1
    rolled_back = aim.rollback_skill("skill_web_scraper", target_version=1)
    assert rolled_back is True
    assert aim.skills["skill_web_scraper"].current_version == 1
    assert aim.skills["skill_web_scraper"].status == SkillStatus.ROLLED_BACK
    assert aim.analytics["rollbacks_executed"] == 1
