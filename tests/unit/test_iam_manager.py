"""
Unit & Integration Tests for Volume 11 Part 11B IAM Architecture.
Verifies digital identity creation, authentication, password hashing, session creation & revocation,
and identity lifecycle state transitions.
"""

import pytest
from src.backend.core.iam_manager import (
    IAMManager,
    IdentityState,
    AuthMethod
)


def test_iam_identity_creation_and_authentication():
    iam = IAMManager(session_ttl_seconds=3600.0)

    identity = iam.create_identity(
        identity_id="usr_adil",
        entity_name="Adil Admin",
        secret="SuperSecretPass123!",
        roles=["admin", "developer"]
    )

    assert identity.identity_id == "usr_adil"
    assert identity.state == IdentityState.ACTIVE
    assert identity.secret_hash != "SuperSecretPass123!"

    # Authenticate successfully
    session = iam.authenticate("usr_adil", "SuperSecretPass123!", AuthMethod.PASSWORD)
    assert session.session_id.startswith("iam_sess_")
    assert session.is_active is True
    assert iam.validate_session(session.session_id) is True

    # Authenticate failure with wrong password
    with pytest.raises(PermissionError):
        iam.authenticate("usr_adil", "WrongPassword", AuthMethod.PASSWORD)


def test_iam_lifecycle_transition_and_revocation():
    iam = IAMManager()

    iam.create_identity("usr_dev", "Developer", "DevPass")
    sess = iam.authenticate("usr_dev", "DevPass")

    # Transition identity state to SUSPENDED
    assert iam.transition_lifecycle("usr_dev", IdentityState.SUSPENDED) is True
    assert iam.identities["usr_dev"].state == IdentityState.SUSPENDED

    # Active session must automatically be terminated upon suspension
    assert iam.validate_session(sess.session_id) is False

    # Block authentication when suspended
    with pytest.raises(PermissionError):
        iam.authenticate("usr_dev", "DevPass")
