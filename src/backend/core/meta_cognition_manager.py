"""
Captain AI OS - Meta-Cognition, Self-Evaluation & Reflective Intelligence System (Volume 12 Part 12D)
Responsible for quantitative self-evaluation, execution reflection, error categorization,
confidence calibration, knowledge gap detection, and explainable improvement recommendations.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import time
from pydantic import BaseModel, Field
from src.backend.core.permission_manager import PermissionManager, Permission


class EvaluationMetric(str, Enum):
    GOAL_ACHIEVEMENT = "GOAL_ACHIEVEMENT"
    PLANNING_ACCURACY = "PLANNING_ACCURACY"
    TOOL_SELECTION = "TOOL_SELECTION"
    RESOURCE_EFFICIENCY = "RESOURCE_EFFICIENCY"
    EXECUTION_RELIABILITY = "EXECUTION_RELIABILITY"
    USER_SATISFACTION = "USER_SATISFACTION"
    GOVERNANCE_COMPLIANCE = "GOVERNANCE_COMPLIANCE"
    OPERATIONAL_STABILITY = "OPERATIONAL_STABILITY"


class ErrorCategory(str, Enum):
    PLANNING_ERROR = "PLANNING_ERROR"
    REASONING_ERROR = "REASONING_ERROR"
    TOOL_FAILURE = "TOOL_FAILURE"
    KNOWLEDGE_GAP = "KNOWLEDGE_GAP"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    INTEGRATION_FAILURE = "INTEGRATION_FAILURE"
    UNEXPECTED_OUTCOME = "UNEXPECTED_OUTCOME"


class ReflectionReport(BaseModel):
    report_id: str
    execution_id: str
    expected_outcome: str
    actual_outcome: str
    decision_quality_score: float  # 0.0 to 100.0
    errors_detected: List[ErrorCategory] = Field(default_factory=list)
    predicted_confidence: float = 0.0
    actual_success_score: float = 0.0
    confidence_delta: float = 0.0  # abs(predicted - actual)
    recommendations: List[str] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)


class ConfidenceManager:
    """Evaluates confidence calibration errors to correct overconfidence or underconfidence."""

    @staticmethod
    def calculate_calibration(predicted_confidence: float, actual_success_score: float) -> float:
        pred = max(0.0, min(1.0, predicted_confidence))
        act = max(0.0, min(1.0, actual_success_score))
        return round(abs(pred - act), 4)


class SelfEvaluator:
    """Computes composite multi-metric decision quality scores."""

    @staticmethod
    def evaluate_quality(
        goal_achieved: bool,
        planning_accuracy: float,
        tool_success: float,
        governance_compliant: bool
    ) -> float:
        if not governance_compliant:
            return 0.0  # Governance violation invalidates decision score

        achieve_score = 40.0 if goal_achieved else 0.0
        plan_score = round(max(0.0, min(1.0, planning_accuracy)) * 30.0, 2)
        tool_score = round(max(0.0, min(1.0, tool_success)) * 30.0, 2)
        return round(achieve_score + plan_score + tool_score, 2)


class MetaCognitionManager:
    """Centralized Manager for Meta-Cognition, Self-Evaluation & Reflection."""

    def __init__(self):
        self.reflection_reports: Dict[str, ReflectionReport] = {}
        self.permission_manager = PermissionManager()
        self.analytics = {
            "reflections_conducted": 0,
            "errors_identified": 0,
            "recommendations_generated": 0,
            "average_quality_score": 0.0
        }

    def observe_and_reflect(
        self,
        execution_id: str,
        expected_outcome: str,
        actual_outcome: str,
        predicted_confidence: float,
        actual_success_score: float,
        execution_logs: Dict[str, Any]
    ) -> ReflectionReport:
        """Analyzes completed execution, generates quality score, and extracts reflection report."""
        goal_achieved = expected_outcome.strip().lower() == actual_outcome.strip().lower() or actual_success_score >= 0.8
        governance_compliant = execution_logs.get("governance_compliant", True)
        planning_acc = execution_logs.get("planning_accuracy", 0.9)
        tool_succ = execution_logs.get("tool_success_rate", 0.95)

        quality_score = SelfEvaluator.evaluate_quality(
            goal_achieved=goal_achieved,
            planning_accuracy=planning_acc,
            tool_success=tool_succ,
            governance_compliant=governance_compliant
        )

        conf_delta = ConfidenceManager.calculate_calibration(predicted_confidence, actual_success_score)

        detected_errors = []
        recommendations = []

        if not goal_achieved:
            detected_errors.append(ErrorCategory.UNEXPECTED_OUTCOME)
            recommendations.append("Re-evaluate goal decomposition and strategy candidates.")

        if tool_succ < 0.8:
            detected_errors.append(ErrorCategory.TOOL_FAILURE)
            recommendations.append("Perform tool parameter sanity check before execution.")

        if conf_delta > 0.3:
            recommendations.append(f"Adjust confidence calibration model (delta={conf_delta}).")

        report_id = f"refl_{int(time.time() * 1000)}"
        report = ReflectionReport(
            report_id=report_id,
            execution_id=execution_id,
            expected_outcome=expected_outcome,
            actual_outcome=actual_outcome,
            decision_quality_score=quality_score,
            errors_detected=detected_errors,
            predicted_confidence=predicted_confidence,
            actual_success_score=actual_success_score,
            confidence_delta=conf_delta,
            recommendations=recommendations
        )

        self.reflection_reports[report_id] = report
        self.analytics["reflections_conducted"] += 1
        self.analytics["errors_identified"] += len(detected_errors)
        self.analytics["recommendations_generated"] += len(recommendations)
        self._update_avg_score()

        return report

    def detect_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """Scans historical reflection reports to isolate recurring error categories and knowledge gaps."""
        error_counts: Dict[str, int] = {}
        for r in self.reflection_reports.values():
            for err in r.errors_detected:
                error_counts[err.value] = error_counts.get(err.value, 0) + 1

        gaps = []
        for err_type, count in error_counts.items():
            gaps.append({
                "gap_category": err_type,
                "occurrences": count,
                "recommended_action": f"Acquire targeted skills or knowledge to resolve {err_type}."
            })
        return gaps

    def get_meta_cognition_analytics(self) -> Dict[str, Any]:
        """Returns analytics summary for self-evaluation accuracy and reflection metrics."""
        return {
            "total_reflections": len(self.reflection_reports),
            "analytics_summary": self.analytics
        }

    def _update_avg_score(self):
        if self.reflection_reports:
            total = sum(r.decision_quality_score for r in self.reflection_reports.values())
            self.analytics["average_quality_score"] = round(total / len(self.reflection_reports), 2)
