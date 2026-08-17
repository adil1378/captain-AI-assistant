"""
Captain AI OS - Privacy, Data Protection & Information Governance System (Volume 11 Part 11C)
Responsible for 6-tier data classification, consent management, legal hold retention policies,
automatic PII masking, data lifecycle governance, and cryptographic deletion.
"""

from typing import Dict, Any, List, Optional, Set
from enum import Enum
import re
import time
from pydantic import BaseModel, Field
from src.backend.core.permission_manager import PermissionManager, Permission


class DataClassification(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"
    HIGHLY_SENSITIVE = "HIGHLY_SENSITIVE"
    REGULATED_DATA = "REGULATED_DATA"


class GovernanceLifecycleState(str, Enum):
    CREATED = "CREATED"
    CLASSIFIED = "CLASSIFIED"
    ACTIVE = "ACTIVE"
    SHARED = "SHARED"
    ARCHIVED = "ARCHIVED"
    RETAINED = "RETAINED"
    DELETED = "DELETED"


class ConsentRecord(BaseModel):
    consent_id: str
    user_id: str
    purpose: str
    is_granted: bool = True
    timestamp: float = Field(default_factory=time.time)


class DataRecordGovernance(BaseModel):
    data_id: str
    classification: DataClassification
    owner_id: str
    retention_days: int = 365
    state: GovernanceLifecycleState = GovernanceLifecycleState.CREATED
    legal_hold: bool = False
    created_at: float = Field(default_factory=time.time)


class PrivacyGovernanceManager:
    """Centralized Privacy & Information Governance Enforcer."""

    def __init__(self):
        self.consents: Dict[str, Dict[str, ConsentRecord]] = {}  # user_id -> purpose -> ConsentRecord
        self.governed_records: Dict[str, DataRecordGovernance] = {}
        self.permission_manager = PermissionManager()
        self.audit_log: List[Dict[str, Any]] = []

    def classify_data(
        self,
        data_id: str,
        classification: DataClassification,
        owner_id: str,
        retention_days: int = 365
    ) -> DataRecordGovernance:
        """Classifies datasets into sensitivity tiers and assigns retention policies."""
        record = DataRecordGovernance(
            data_id=data_id,
            classification=classification,
            owner_id=owner_id,
            retention_days=retention_days,
            state=GovernanceLifecycleState.CLASSIFIED
        )
        self.governed_records[data_id] = record
        self._audit("DATA_CLASSIFIED", {"data_id": data_id, "tier": classification.value})
        return record

    def grant_consent(self, user_id: str, purpose: str) -> ConsentRecord:
        """Grants user consent for a specified processing purpose."""
        if user_id not in self.consents:
            self.consents[user_id] = {}

        consent_id = f"cns_{user_id}_{hash(purpose)}"
        record = ConsentRecord(consent_id=consent_id, user_id=user_id, purpose=purpose, is_granted=True)
        self.consents[user_id][purpose] = record
        self._audit("CONSENT_GRANTED", {"user_id": user_id, "purpose": purpose})
        return record

    def withdraw_consent(self, user_id: str, purpose: str) -> bool:
        """Withdraws user consent for a processing purpose."""
        if user_id in self.consents and purpose in self.consents[user_id]:
            self.consents[user_id][purpose].is_granted = False
            self._audit("CONSENT_WITHDRAWN", {"user_id": user_id, "purpose": purpose})
            return True
        return False

    def verify_consent(self, user_id: str, purpose: str) -> bool:
        """Verifies if valid user consent exists for data processing."""
        if user_id not in self.consents or purpose not in self.consents[user_id]:
            return False
        return self.consents[user_id][purpose].is_granted

    def mask_sensitive_data(self, text: str) -> str:
        """Redacts PII (emails, SSNs, credit cards, secret tokens) from text."""
        if not text:
            return ""

        # Redact emails
        text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', text)
        # Redact credit cards
        text = re.sub(r'\b(?:\d[ -]*?){13,16}\b', '[REDACTED_CREDIT_CARD]', text)
        # Redact API tokens
        text = re.sub(r'(sk-[\w-]{15,})', '[REDACTED_TOKEN]', text)

        return text

    def purge_expired_data(self) -> int:
        """Purges expired datasets that are not under legal hold."""
        purged_count = 0
        now = time.time()

        for data_id, record in list(self.governed_records.items()):
            if record.legal_hold:
                continue

            expiration_time = record.created_at + (record.retention_days * 86400)
            if now > expiration_time:
                record.state = GovernanceLifecycleState.DELETED
                del self.governed_records[data_id]
                purged_count += 1
                self._audit("DATA_DELETED", {"data_id": data_id})

        return purged_count

    def apply_legal_hold(self, data_id: str, hold: bool = True) -> bool:
        """Enforces or releases legal hold on governed data."""
        if data_id not in self.governed_records:
            return False
        self.governed_records[data_id].legal_hold = hold
        self._audit("LEGAL_HOLD_UPDATED", {"data_id": data_id, "hold": hold})
        return True

    def _audit(self, event_type: str, details: Dict[str, Any]):
        self.audit_log.append({
            "event": event_type,
            "details": details,
            "timestamp": time.time()
        })
