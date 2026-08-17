"""
Unit & Integration Tests for Volume 11 Part 11A Zero Trust Security Architecture.
Verifies identity registration, continuous authorization, risk score evaluation,
default-deny enforcement, threat detection, and audit logging.
"""

import pytest
from src.backend.core.zero_trust_manager import (
    ZeroTrustSecurityManager,
    IdentityRecord,
    IdentityType,
    ProtectedResource,
    AccessRequest,
    AccessDecision,
    RiskLevel
)
from src.backend.core.permission_manager import Permission


def test_zero_trust_identity_registration_and_allowed_access():
    zt = ZeroTrustSecurityManager()

    identity = IdentityRecord(
        identity_id="id_agent_coding",
        identity_type=IdentityType.AGENT,
        trust_score=0.9
    )
    zt.register_identity(identity)
    zt.permission_manager.grant_permission(Permission.FS_READ)

    req = AccessRequest(
        request_id="req_1",
        identity_id="id_agent_coding",
        resource=ProtectedResource.MEMORY,
        action="read_context",
        required_permissions=[Permission.FS_READ]
    )

    res = zt.evaluate_access(req)
    assert res.decision == AccessDecision.ALLOWED
    assert res.risk_level == RiskLevel.LOW


def test_unregistered_identity_default_deny():
    zt = ZeroTrustSecurityManager()

    req = AccessRequest(
        request_id="req_unauthorized",
        identity_id="unknown_hacker",
        resource=ProtectedResource.SECRETS,
        action="steal_keys"
    )

    res = zt.evaluate_access(req)
    assert res.decision == AccessDecision.DENIED
    assert res.risk_level == RiskLevel.CRITICAL
    assert len(zt.threat_logs) == 1
    assert zt.threat_logs[0]["threat_type"] == "UNREGISTERED_IDENTITY_ACCESS"


def test_high_risk_and_trust_degradation():
    zt = ZeroTrustSecurityManager(risk_threshold=0.4)

    identity = IdentityRecord(
        identity_id="id_suspicious_device",
        identity_type=IdentityType.DEVICE,
        trust_score=0.5  # Medium trust score
    )
    zt.register_identity(identity)

    # Accessing secrets elevates risk score (0.5 base risk + 0.3 secret risk = 0.8 critical)
    req = AccessRequest(
        request_id="req_high_risk",
        identity_id="id_suspicious_device",
        resource=ProtectedResource.SECRETS,
        action="read_api_keys"
    )

    res = zt.evaluate_access(req)
    assert res.decision in [AccessDecision.DENIED, AccessDecision.STEP_UP_MFA]
    assert zt.identities["id_suspicious_device"].trust_score == 0.3  # Degraded trust score
