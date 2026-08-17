"""
Unit & Integration Tests for Volume 11 Part 11C Privacy & Governance Architecture.
Verifies data classification, user consent verification & withdrawal, PII data masking,
retention expiration, and legal hold enforcement.
"""

import pytest
import time
from src.backend.core.privacy_manager import (
    PrivacyGovernanceManager,
    DataClassification,
    GovernanceLifecycleState
)


def test_data_classification_and_consent():
    pm = PrivacyGovernanceManager()

    # Data classification
    rec = pm.classify_data(
        data_id="ds_user_analytics",
        classification=DataClassification.RESTRICTED,
        owner_id="usr_adil",
        retention_days=30
    )
    assert rec.data_id == "ds_user_analytics"
    assert rec.classification == DataClassification.RESTRICTED

    # Consent verification
    pm.grant_consent("usr_adil", "telemetry_analytics")
    assert pm.verify_consent("usr_adil", "telemetry_analytics") is True

    # Withdraw consent
    pm.withdraw_consent("usr_adil", "telemetry_analytics")
    assert pm.verify_consent("usr_adil", "telemetry_analytics") is False


def test_sensitive_data_masking():
    pm = PrivacyGovernanceManager()

    raw_text = "Contact user at test@example.com using credit card 4111-2222-3333-4444 and key sk-proj-1234567890abcdef."
    masked = pm.mask_sensitive_data(raw_text)

    assert "[REDACTED_EMAIL]" in masked
    assert "[REDACTED_CREDIT_CARD]" in masked
    assert "[REDACTED_TOKEN]" in masked
    assert "test@example.com" not in masked


def test_retention_and_legal_hold():
    pm = PrivacyGovernanceManager()

    rec1 = pm.classify_data("ds_1", DataClassification.INTERNAL, "usr_1", retention_days=0)
    rec2 = pm.classify_data("ds_2", DataClassification.INTERNAL, "usr_1", retention_days=0)

    # Apply legal hold to ds_2
    pm.apply_legal_hold("ds_2", hold=True)

    # Force expiration calculation
    rec1.created_at = time.time() - 100000
    rec2.created_at = time.time() - 100000

    purged = pm.purge_expired_data()
    assert purged == 1  # ds_1 purged, ds_2 retained under legal hold
    assert "ds_1" not in pm.governed_records
    assert "ds_2" in pm.governed_records
