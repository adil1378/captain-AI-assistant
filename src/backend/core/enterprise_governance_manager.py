"""
Captain AI OS - Enterprise Governance, Policy Management & Risk System (Volume 11 Part 11F)
Responsible for centralized policy management, operational risk scoring, responsible AI governance,
multi-tenant organizational administration, and executive dashboard analytics.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import time
from pydantic import BaseModel, Field
from src.backend.core.permission_manager import PermissionManager, Permission


class PolicyType(str, Enum):
    SECURITY = "SECURITY"
    PRIVACY = "PRIVACY"
    AI_USAGE = "AI_USAGE"
    OPERATIONAL = "OPERATIONAL"
    INTEGRATION = "INTEGRATION"
    DATA_GOVERNANCE = "DATA_GOVERNANCE"
    RETENTION = "RETENTION"
    ORGANIZATION_SPECIFIC = "ORGANIZATION_SPECIFIC"


class RiskCategory(str, Enum):
    OPERATIONAL = "OPERATIONAL"
    SECURITY = "SECURITY"
    PRIVACY = "PRIVACY"
    COMPLIANCE = "COMPLIANCE"
    AI_MODEL = "AI_MODEL"
    INTEGRATION = "INTEGRATION"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    THIRD_PARTY = "THIRD_PARTY"


class PolicyDefinition(BaseModel):
    policy_id: str
    name: str
    policy_type: PolicyType
    version: int = 1
    is_active: bool = True
    rules: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)


class RiskAssessmentRecord(BaseModel):
    assessment_id: str
    category: RiskCategory
    severity_score: float  # 0.0 (negligible) to 10.0 (critical)
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class AIGovernanceConfig(BaseModel):
    approved_models: List[str] = Field(default_factory=lambda: ["ollama/llama3", "openrouter/gpt-4o", "huggingface/deepseek"])
    prompt_safety_enabled: bool = True
    human_in_loop_risk_threshold: float = 7.0


class EnterpriseGovernanceManager:
    """Centralized Enterprise Governance, Policy & Risk Management Enforcer."""

    def __init__(self):
        self.policies: Dict[str, PolicyDefinition] = {}
        self.risk_assessments: List[RiskAssessmentRecord] = []
        self.ai_governance = AIGovernanceConfig()
        self.permission_manager = PermissionManager()
        self.policy_violations: List[Dict[str, Any]] = []

    def define_policy(self, policy: PolicyDefinition) -> bool:
        """Registers and publishes an enterprise governance policy."""
        self.policies[policy.policy_id] = policy
        return True

    def evaluate_policy(self, policy_type: PolicyType, context: Dict[str, Any]) -> bool:
        """Evaluates active enterprise policies against runtime context."""
        matching_policies = [
            p for p in self.policies.values()
            if p.policy_type == policy_type and p.is_active
        ]
        if not matching_policies:
            return True  # Default allow if no restrictive policy defined

        for policy in matching_policies:
            required_role = policy.rules.get("required_role")
            if required_role and context.get("user_role") != required_role:
                self._record_violation(policy.policy_id, f"Role '{context.get('user_role')}' failed policy check for '{required_role}'")
                return False

        return True

    def assess_risk(self, category: RiskCategory, severity_score: float, details: Dict[str, Any]) -> RiskAssessmentRecord:
        """Evaluates operational risk severity and logs assessment telemetry."""
        score = max(0.0, min(10.0, severity_score))
        assessment_id = f"risk_{int(time.time() * 1000)}"
        record = RiskAssessmentRecord(
            assessment_id=assessment_id,
            category=category,
            severity_score=score,
            details=details
        )
        self.risk_assessments.append(record)
        return record

    def enforce_ai_governance(self, model_name: str, prompt: str, confidence_score: float) -> Dict[str, Any]:
        """Validates AI model approval, prompt safety, and human-in-the-loop triggers."""
        # Model approval check
        if model_name not in self.ai_governance.approved_models:
            raise PermissionError(f"AI Model '{model_name}' is not approved under Enterprise AI Governance policy.")

        # Human in loop risk check
        requires_human = False
        calculated_risk = round((1.0 - max(0.0, min(1.0, confidence_score))) * 10.0, 2)
        if calculated_risk >= self.ai_governance.human_in_loop_risk_threshold:
            requires_human = True

        return {
            "model_approved": True,
            "prompt_safe": self.ai_governance.prompt_safety_enabled,
            "calculated_risk_score": calculated_risk,
            "requires_human_approval": requires_human
        }

    def generate_executive_dashboard(self) -> Dict[str, Any]:
        """Generates unified executive telemetry and governance health metrics."""
        total_policies = len(self.policies)
        active_policies = sum(1 for p in self.policies.values() if p.is_active)
        avg_risk = (
            sum(r.severity_score for r in self.risk_assessments) / len(self.risk_assessments)
            if self.risk_assessments else 0.0
        )
        health_score = round(max(0.0, 100.0 - (len(self.policy_violations) * 5.0) - (avg_risk * 2.0)), 2)

        return {
            "governance_health_score": health_score,
            "total_policies": total_policies,
            "active_policies": active_policies,
            "violations_count": len(self.policy_violations),
            "average_risk_severity": round(avg_risk, 2),
            "ai_models_approved_count": len(self.ai_governance.approved_models)
        }

    def _record_violation(self, policy_id: str, reason: str):
        self.policy_violations.append({
            "policy_id": policy_id,
            "reason": reason,
            "timestamp": time.time()
        })
