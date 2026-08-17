"""
Captain AI OS - Audit Logging, Compliance & Digital Forensics System (Volume 11 Part 11D)
Responsible for tamper-evident SHA-256 hash-chained audit logging, compliance rule enforcement,
digital forensics evidence collection, timeline reconstruction, and chain of custody tracking.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import hashlib
import time
import json
from pydantic import BaseModel, Field
from src.backend.core.permission_manager import PermissionManager, Permission


class AuditEventCategory(str, Enum):
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    TOOL_EXECUTION = "TOOL_EXECUTION"
    AGENT_ACTIVITY = "AGENT_ACTIVITY"
    CONFIG_CHANGE = "CONFIG_CHANGE"
    DATA_ACCESS = "DATA_ACCESS"
    MEMORY_OP = "MEMORY_OP"
    EXTERNAL_INTEGRATION = "EXTERNAL_INTEGRATION"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    ADMIN_ACTION = "ADMIN_ACTION"
    SECURITY_INCIDENT = "SECURITY_INCIDENT"
    COMPLIANCE_EVENT = "COMPLIANCE_EVENT"


class AuditRecord(BaseModel):
    audit_id: str
    event_id: str
    timestamp: float = Field(default_factory=time.time)
    actor_id: str
    resource: str
    action: str
    outcome: str
    risk_level: str = "LOW"
    category: AuditEventCategory
    correlation_id: Optional[str] = None
    previous_hash: str = "0000000000000000000000000000000000000000000000000000000000000000"
    integrity_hash: str = ""


class ChainOfCustodyRecord(BaseModel):
    custody_id: str
    investigation_id: str
    investigator_id: str
    exported_at: float = Field(default_factory=time.time)
    evidence_hash: str
    total_records_exported: int


class ComplianceRule(BaseModel):
    rule_id: str
    category: AuditEventCategory
    description: str
    is_mandatory: bool = True
    is_compliant: bool = True


class AuditComplianceManager:
    """Centralized Cryptographic Audit Logging, Compliance & Digital Forensics Manager."""

    def __init__(self):
        self.audit_chain: List[AuditRecord] = []
        self.last_hash: str = "0000000000000000000000000000000000000000000000000000000000000000"
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.custody_records: List[ChainOfCustodyRecord] = []
        self.permission_manager = PermissionManager()
        self._init_default_rules()

    def _init_default_rules(self):
        self.compliance_rules["COMP_AUTH"] = ComplianceRule(
            rule_id="COMP_AUTH",
            category=AuditEventCategory.AUTHENTICATION,
            description="All authentication events must be logged with MFA verification."
        )
        self.compliance_rules["COMP_DATA"] = ComplianceRule(
            rule_id="COMP_DATA",
            category=AuditEventCategory.DATA_ACCESS,
            description="Restricted PII access must record actor identity and timestamp."
        )

    def _compute_hash(self, record: AuditRecord, prev_hash: str) -> str:
        payload = f"{record.audit_id}:{record.event_id}:{record.timestamp}:{record.actor_id}:{record.resource}:{record.action}:{record.outcome}:{prev_hash}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def log_event(
        self,
        actor_id: str,
        action: str,
        resource: str,
        outcome: str,
        category: AuditEventCategory = AuditEventCategory.AGENT_ACTIVITY,
        risk_level: str = "LOW",
        correlation_id: Optional[str] = None
    ) -> AuditRecord:
        """Generates an immutable, cryptographic hash-chained audit record."""
        audit_id = f"audit_{len(self.audit_chain) + 1}"
        event_id = f"evt_{int(time.time() * 1000)}"

        record = AuditRecord(
            audit_id=audit_id,
            event_id=event_id,
            actor_id=actor_id,
            resource=resource,
            action=action,
            outcome=outcome,
            risk_level=risk_level,
            category=category,
            correlation_id=correlation_id,
            previous_hash=self.last_hash
        )

        integrity_hash = self._compute_hash(record, self.last_hash)
        record.integrity_hash = integrity_hash

        self.last_hash = integrity_hash
        self.audit_chain.append(record)
        return record

    def verify_chain_integrity(self) -> bool:
        """Re-computes and verifies the complete cryptographic hash chain for tamper evidence."""
        prev_hash = "0000000000000000000000000000000000000000000000000000000000000000"
        for record in self.audit_chain:
            expected_hash = self._compute_hash(record, prev_hash)
            if record.integrity_hash != expected_hash or record.previous_hash != prev_hash:
                return False  # Chain tampering detected!
            prev_hash = record.integrity_hash
        return True

    def export_forensic_evidence(
        self,
        investigation_id: str,
        investigator_id: str,
        filter_actor: Optional[str] = None
    ) -> Dict[str, Any]:
        """Exports forensically sound audit timeline records with a verifiable Chain of Custody signature."""
        matching_records = [
            r for r in self.audit_chain
            if filter_actor is None or r.actor_id == filter_actor
        ]

        serialized = json.dumps([r.model_dump() for r in matching_records])
        evidence_hash = hashlib.sha256(serialized.encode('utf-8')).hexdigest()

        custody = ChainOfCustodyRecord(
            custody_id=f"custody_{int(time.time())}",
            investigation_id=investigation_id,
            investigator_id=investigator_id,
            evidence_hash=evidence_hash,
            total_records_exported=len(matching_records)
        )
        self.custody_records.append(custody)

        return {
            "investigation_id": investigation_id,
            "custody_record": custody,
            "chain_valid": self.verify_chain_integrity(),
            "evidence": matching_records
        }

    def evaluate_compliance_score(self) -> Dict[str, Any]:
        """Evaluates system compliance score across active governance rules."""
        total_rules = len(self.compliance_rules)
        compliant_rules = sum(1 for r in self.compliance_rules.values() if r.is_compliant)
        score = round((compliant_rules / total_rules) * 100, 2) if total_rules > 0 else 100.0

        return {
            "compliance_score": score,
            "total_rules": total_rules,
            "compliant_count": compliant_rules,
            "chain_integrity_verified": self.verify_chain_integrity()
        }
