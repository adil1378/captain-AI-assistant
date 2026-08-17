"""
Unit & Integration Tests for Volume 11 Part 11F Enterprise Governance Architecture.
Verifies policy definition & evaluation, risk assessment scoring, AI model governance checks,
and executive dashboard analytics.
"""

import pytest
from src.backend.core.enterprise_governance_manager import (
    EnterpriseGovernanceManager,
    PolicyDefinition,
    PolicyType,
    RiskCategory
)


def test_policy_definition_and_evaluation():
    egm = EnterpriseGovernanceManager()

    policy = PolicyDefinition(
        policy_id="pol_sec_01",
        name="Strict Admin Access",
        policy_type=PolicyType.SECURITY,
        rules={"required_role": "admin"}
    )
    assert egm.define_policy(policy) is True

    # Evaluates true for admin role
    assert egm.evaluate_policy(PolicyType.SECURITY, {"user_role": "admin"}) is True

    # Evaluates false for developer role
    assert egm.evaluate_policy(PolicyType.SECURITY, {"user_role": "developer"}) is False
    assert len(egm.policy_violations) == 1


def test_ai_governance_enforcement():
    egm = EnterpriseGovernanceManager()

    # Approved model with high confidence
    res_ok = egm.enforce_ai_governance("ollama/llama3", "Generate code", confidence_score=0.9)
    assert res_ok["model_approved"] is True
    assert res_ok["requires_human_approval"] is False

    # Low confidence model call triggers human approval (risk score = (1 - 0.2) * 10 = 8.0 >= 7.0 threshold)
    res_human = egm.enforce_ai_governance("ollama/llama3", "Execute root command", confidence_score=0.2)
    assert res_human["requires_human_approval"] is True

    # Unapproved model triggers rejection
    with pytest.raises(PermissionError):
        egm.enforce_ai_governance("unapproved_hacked_model", "test prompt", 0.9)


def test_risk_assessment_and_executive_dashboard():
    egm = EnterpriseGovernanceManager()

    egm.assess_risk(RiskCategory.SECURITY, severity_score=3.5, details={"event": "minor_scan"})
    egm.assess_risk(RiskCategory.AI_MODEL, severity_score=2.0, details={"event": "model_switch"})

    dashboard = egm.generate_executive_dashboard()
    assert dashboard["governance_health_score"] > 90.0
    assert dashboard["average_risk_severity"] == 2.75
    assert dashboard["ai_models_approved_count"] == 3
