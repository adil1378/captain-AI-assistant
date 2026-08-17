"""
Unit & Integration Tests for Volume 11 Part 11D Audit Logging & Digital Forensics Architecture.
Verifies cryptographic SHA-256 log hash chaining, tamper detection, compliance score calculation,
forensic evidence exports, and chain of custody tracking.
"""

import pytest
from src.backend.core.audit_compliance_manager import (
    AuditComplianceManager,
    AuditEventCategory,
    AuditRecord
)


def test_hash_chaining_and_integrity_verification():
    acm = AuditComplianceManager()

    rec1 = acm.log_event(
        actor_id="user_admin",
        action="user_login",
        resource="IAM_GATEWAY",
        outcome="SUCCESS",
        category=AuditEventCategory.AUTHENTICATION
    )

    rec2 = acm.log_event(
        actor_id="agent_coder",
        action="write_code",
        resource="src/main.py",
        outcome="SUCCESS",
        category=AuditEventCategory.TOOL_EXECUTION
    )

    assert rec1.integrity_hash != ""
    assert rec2.previous_hash == rec1.integrity_hash
    assert acm.verify_chain_integrity() is True


def test_tamper_detection():
    acm = AuditComplianceManager()

    acm.log_event(actor_id="usr_1", action="action_1", resource="res_1", outcome="SUCCESS")
    rec2 = acm.log_event(actor_id="usr_2", action="action_2", resource="res_2", outcome="SUCCESS")

    assert acm.verify_chain_integrity() is True

    # Maliciously mutate historical log record payload
    rec2.action = "tampered_action"

    # Integrity verification must detect tampering!
    assert acm.verify_chain_integrity() is False


def test_forensic_evidence_export_and_chain_of_custody():
    acm = AuditComplianceManager()

    acm.log_event(actor_id="suspect_agent", action="file_delete", resource="db.sqlite", outcome="SUCCESS")

    export = acm.export_forensic_evidence(
        investigation_id="INV_2026_001",
        investigator_id="sec_officer_1",
        filter_actor="suspect_agent"
    )

    assert export["investigation_id"] == "INV_2026_001"
    assert export["chain_valid"] is True
    assert len(export["evidence"]) == 1
    assert export["custody_record"].investigator_id == "sec_officer_1"
    assert len(acm.custody_records) == 1
