"""
Captain AI OS - AI Decision Engine (Volume 3 Part 3H)
Responsible for multi-criteria evaluation, risk assessment, tool execution approval,
confidence scoring, and autonomous decision routing.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
import time


class DecisionRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DecisionOutcome(str, Enum):
    APPROVED = "APPROVED"
    REQUIRES_USER_APPROVAL = "REQUIRES_USER_APPROVAL"
    REJECTED = "REJECTED"


class EvaluationRequest(BaseModel):
    request_id: str
    action_type: str
    agent_id: str
    target_resource: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = 1.0


class DecisionResult(BaseModel):
    request_id: str
    outcome: DecisionOutcome
    risk_level: DecisionRiskLevel
    reasoning: str
    confidence: float
    timestamp: float = Field(default_factory=time.time)


class AIDecisionEngine:
    def __init__(self, risk_threshold: float = 0.7):
        self.risk_threshold = risk_threshold
        self.high_risk_actions = {
            "file_delete", "system_reboot", "process_terminate",
            "shell_execute", "credential_access", "database_drop"
        }

    def evaluate_action(self, request: EvaluationRequest) -> DecisionResult:
        """Evaluates an action request against risk policies and confidence thresholds."""
        action = request.action_type.lower()
        confidence = max(0.0, min(1.0, request.confidence_score))
        
        # High-risk action detection
        if any(h in action for h in self.high_risk_actions):
            risk = DecisionRiskLevel.HIGH
            outcome = DecisionOutcome.REQUIRES_USER_APPROVAL
            reason = f"Action '{action}' is classified as high-risk and requires explicit user authorization."
        elif confidence < self.risk_threshold:
            risk = DecisionRiskLevel.MEDIUM
            outcome = DecisionOutcome.REQUIRES_USER_APPROVAL
            reason = f"Confidence score ({confidence:.2f}) is below approval threshold ({self.risk_threshold:.2f})."
        else:
            risk = DecisionRiskLevel.LOW
            outcome = DecisionOutcome.APPROVED
            reason = "Action approved automatically under low-risk policy."

        return DecisionResult(
            request_id=request.request_id,
            outcome=outcome,
            risk_level=risk,
            reasoning=reason,
            confidence=confidence
        )

    def rank_options(self, options: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ranks multiple candidate execution strategies based on confidence and cost."""
        return sorted(
            options,
            key=lambda x: (x.get("confidence", 0.0), -x.get("latency_estimate", 100)),
            reverse=True
        )
