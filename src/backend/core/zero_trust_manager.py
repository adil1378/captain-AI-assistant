"""
Captain AI OS - Zero Trust Security System (Volume 11 Part 11A)
Responsible for identity verification, continuous authorization, dynamic risk scoring,
resource isolation, threat monitoring, default-deny security enforcement, and audit logging.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import asyncio
import time
from pydantic import BaseModel, Field
from src.backend.core.permission_manager import PermissionManager, Permission


class IdentityType(str, Enum):
    USER = "USER"
    AGENT = "AGENT"
    SERVICE = "SERVICE"
    DEVICE = "DEVICE"
    API_CLIENT = "API_CLIENT"
    FEDERATION = "FEDERATION"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AccessDecision(str, Enum):
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"
    REQUIRES_REAUTH = "REQUIRES_REAUTH"
    STEP_UP_MFA = "STEP_UP_MFA"


class ProtectedResource(str, Enum):
    MEMORY = "MEMORY"
    KNOWLEDGE_BASE = "KNOWLEDGE_BASE"
    TOOL_EXECUTION = "TOOL_EXECUTION"
    OS_API = "OS_API"
    EXTERNAL_INTEGRATION = "EXTERNAL_INTEGRATION"
    CONFIG = "CONFIG"
    SECRETS = "SECRETS"
    AUDIT_LOGS = "AUDIT_LOGS"


class IdentityRecord(BaseModel):
    identity_id: str
    identity_type: IdentityType
    roles: List[str] = Field(default_factory=lambda: ["user"])
    trust_score: float = 1.0  # 0.0 (untrusted) to 1.0 (fully trusted)
    is_active: bool = True
    created_at: float = Field(default_factory=time.time)


class AccessRequest(BaseModel):
    request_id: str
    identity_id: str
    resource: ProtectedResource
    action: str
    required_permissions: List[Permission] = Field(default_factory=list)
    context_params: Dict[str, Any] = Field(default_factory=dict)


class AccessResult(BaseModel):
    request_id: str
    decision: AccessDecision
    risk_level: RiskLevel
    reasoning: str
    timestamp: float = Field(default_factory=time.time)


class RiskEngine:
    """Calculates real-time dynamic risk scores for inbound access requests."""

    @staticmethod
    def evaluate_risk(identity: IdentityRecord, request: AccessRequest) -> tuple[float, RiskLevel]:
        risk_score = 1.0 - identity.trust_score

        # High-risk resources elevate risk score
        if request.resource in [ProtectedResource.SECRETS, ProtectedResource.OS_API]:
            risk_score += 0.3

        risk_score = max(0.0, min(1.0, risk_score))

        if risk_score >= 0.8:
            level = RiskLevel.CRITICAL
        elif risk_score >= 0.5:
            level = RiskLevel.HIGH
        elif risk_score >= 0.2:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        return round(risk_score, 2), level


class ZeroTrustSecurityManager:
    """Centralized Zero Trust Security Enforcer."""

    def __init__(self, risk_threshold: float = 0.6):
        self.risk_threshold = risk_threshold
        self.identities: Dict[str, IdentityRecord] = {}
        self.permission_manager = PermissionManager()
        self.threat_logs: List[Dict[str, Any]] = []
        self.audit_trail: List[Dict[str, Any]] = []

    def register_identity(self, identity: IdentityRecord) -> bool:
        """Registers a verified identity in the Zero Trust directory."""
        self.identities[identity.identity_id] = identity
        self._audit("IDENTITY_REGISTERED", {"identity_id": identity.identity_id, "type": identity.identity_type})
        return True

    def evaluate_access(self, request: AccessRequest) -> AccessResult:
        """Continuously verifies identity, risk score, and permissions. Defaults to DENIED."""
        # 1. Verify Identity existence & active status
        if request.identity_id not in self.identities:
            self.record_threat(request.identity_id, "UNREGISTERED_IDENTITY_ACCESS", {"resource": request.resource})
            return AccessResult(
                request_id=request.request_id,
                decision=AccessDecision.DENIED,
                risk_level=RiskLevel.CRITICAL,
                reasoning="Identity not recognized. Default Deny policy enforced."
            )

        identity = self.identities[request.identity_id]
        if not identity.is_active:
            return AccessResult(
                request_id=request.request_id,
                decision=AccessDecision.DENIED,
                risk_level=RiskLevel.HIGH,
                reasoning="Identity is inactive or suspended."
            )

        # 2. Risk Assessment
        risk_score, risk_level = RiskEngine.evaluate_risk(identity, request)
        if risk_score > self.risk_threshold:
            self.record_threat(request.identity_id, "HIGH_RISK_ACCESS_ATTEMPT", {"risk_score": risk_score})
            return AccessResult(
                request_id=request.request_id,
                decision=AccessDecision.STEP_UP_MFA if risk_level == RiskLevel.HIGH else AccessDecision.DENIED,
                risk_level=risk_level,
                reasoning=f"Risk score ({risk_score}) exceeds threshold ({self.risk_threshold})."
            )

        # 3. Permission Manager Check
        for perm in request.required_permissions:
            if not self.permission_manager.check_permission(perm):
                return AccessResult(
                    request_id=request.request_id,
                    decision=AccessDecision.DENIED,
                    risk_level=risk_level,
                    reasoning=f"Missing required permission '{perm.value}'."
                )

        # Access Approved
        self._audit("ACCESS_GRANTED", {"request_id": request.request_id, "identity_id": request.identity_id})
        return AccessResult(
            request_id=request.request_id,
            decision=AccessDecision.ALLOWED,
            risk_level=risk_level,
            reasoning="Access verified and authorized under Zero Trust policy."
        )

    def record_threat(self, identity_id: str, threat_type: str, details: Dict[str, Any]):
        """Logs suspicious behavior and degrades identity trust score."""
        if identity_id in self.identities:
            self.identities[identity_id].trust_score = max(0.0, self.identities[identity_id].trust_score - 0.2)

        self.threat_logs.append({
            "identity_id": identity_id,
            "threat_type": threat_type,
            "details": details,
            "timestamp": time.time()
        })

    def _audit(self, event_type: str, details: Dict[str, Any]):
        self.audit_trail.append({
            "event_type": event_type,
            "details": details,
            "timestamp": time.time()
        })
