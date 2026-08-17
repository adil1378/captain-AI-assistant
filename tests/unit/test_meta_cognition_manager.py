"""
Unit & Integration Tests for Volume 12 Part 12D Meta-Cognition Architecture.
Verifies quantitative self-evaluation, execution reflection reports, error categorization,
confidence calibration delta, and knowledge gap detection.
"""

import pytest
from src.backend.core.meta_cognition_manager import (
    MetaCognitionManager,
    ErrorCategory
)


def test_reflection_and_confidence_calibration():
    mcm = MetaCognitionManager()

    report = mcm.observe_and_reflect(
        execution_id="exec_001",
        expected_outcome="SUCCESS",
        actual_outcome="SUCCESS",
        predicted_confidence=0.9,
        actual_success_score=0.95,
        execution_logs={"governance_compliant": True, "planning_accuracy": 0.9, "tool_success_rate": 0.95}
    )

    assert report.report_id.startswith("refl_")
    assert report.decision_quality_score == 95.5  # 40 + 27 + 28.5
    assert report.confidence_delta == 0.05
    assert len(report.errors_detected) == 0
    assert mcm.analytics["reflections_conducted"] == 1


def test_error_detection_and_knowledge_gap_scans():
    mcm = MetaCognitionManager()

    # Reflect on failed tool execution
    mcm.observe_and_reflect(
        execution_id="exec_failed",
        expected_outcome="FILE_PARSED",
        actual_outcome="PARSING_FAILED",
        predicted_confidence=0.95,
        actual_success_score=0.2,
        execution_logs={"governance_compliant": True, "planning_accuracy": 0.5, "tool_success_rate": 0.3}
    )

    gaps = mcm.detect_knowledge_gaps()
    assert len(gaps) > 0
    categories = [g["gap_category"] for g in gaps]
    assert ErrorCategory.UNEXPECTED_OUTCOME.value in categories
    assert ErrorCategory.TOOL_FAILURE.value in categories
