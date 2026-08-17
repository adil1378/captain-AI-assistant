"""
Captain AI OS - Identity, Authentication & Access Management (IAM) System (Volume 11 Part 11B)
Responsible for digital identity lifecycle, multi-factor authentication, RBAC/ABAC authorization,
session creation/renewal/revocation, password hashing, and secret rotation.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import hashlib
import time
from pydantic import BaseModel, Field
from src.backend.core.permission_manager import PermissionManager, Permission


class IdentityState(str, Enum):
    CREATED = "CREATED"
    VERIFIED = "VERIFIED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"


class AuthMethod(str, Enum):
    PASSWORD = "PASSWORD"
    API_KEY = "API_KEY"
    OAUTH2 = "OAUTH2"
    OIDC = "OIDC"
    JWT = "JWT"
    PASSKEY = "PASSKEY"
    MFA = "MFA"
    MTLS = "MTLS"
    SERVICE_ACCOUNT = "SERVICE_ACCOUNT"


class DigitalIdentity(BaseModel):
    identity_id: str
    entity_name: str
    identity_type: str = "USER"
    roles: List[str] = Field(default_factory=lambda: ["user"])
    state: IdentityState = IdentityState.CREATED
    secret_hash: str
    created_at: float = Field(default_factory=time.time)


class UserSessionRecord(BaseModel):
    session_id: str
    identity_id: str
    auth_method: AuthMethod
    created_at: float = Field(default_factory=time.time)
    expires_at: float
    is_active: bool = True


class IAMManager:
    """Centralized Identity, Authentication and Access Management Enforcer."""

    def __init__(self, session_ttl_seconds: float = 3600.0):
        self.session_ttl_seconds = session_ttl_seconds
        self.identities: Dict[str, DigitalIdentity] = {}
        self.sessions: Dict[str, UserSessionRecord] = {}
        self.permission_manager = PermissionManager()
        self.audit_log: List[Dict[str, Any]] = []

    def _hash_secret(self, secret: str) -> str:
        return hashlib.sha256(secret.encode('utf-8')).hexdigest()

    def create_identity(self, identity_id: str, entity_name: str, secret: str, roles: Optional[List[str]] = None) -> DigitalIdentity:
        """Registers and creates a new digital identity."""
        if not secret or not secret.strip():
            raise ValueError("Secret password or token cannot be empty.")

        sec_hash = self._hash_secret(secret)
        identity = DigitalIdentity(
            identity_id=identity_id,
            entity_name=entity_name,
            roles=roles or ["user"],
            state=IdentityState.ACTIVE,
            secret_hash=sec_hash
        )
        self.identities[identity_id] = identity
        self._audit("IDENTITY_CREATED", {"identity_id": identity_id, "roles": identity.roles})
        return identity

    def authenticate(self, identity_id: str, secret: str, auth_method: AuthMethod = AuthMethod.PASSWORD) -> UserSessionRecord:
        """Authenticates identity credentials and returns an active session."""
        if identity_id not in self.identities:
            raise PermissionError(f"Identity '{identity_id}' not found. Denied by default.")

        identity = self.identities[identity_id]
        if identity.state != IdentityState.ACTIVE:
            raise PermissionError(f"Identity '{identity_id}' is in state '{identity.state.value}'. Authentication blocked.")

        if self._hash_secret(secret) != identity.secret_hash:
            self._audit("AUTH_FAILED", {"identity_id": identity_id, "reason": "Invalid secret hash"})
            raise PermissionError("Invalid identity credentials.")

        now = time.time()
        session_id = f"iam_sess_{hashlib.md5(f'{identity_id}:{now}'.encode()).hexdigest()[:12]}"
        session = UserSessionRecord(
            session_id=session_id,
            identity_id=identity_id,
            auth_method=auth_method,
            expires_at=now + self.session_ttl_seconds
        )
        self.sessions[session_id] = session
        self._audit("AUTH_SUCCESS", {"identity_id": identity_id, "session_id": session_id})
        return session

    def transition_lifecycle(self, identity_id: str, new_state: IdentityState) -> bool:
        """Transitions an identity through its lifecycle (SUSPENDED, REVOKED, etc.)."""
        if identity_id not in self.identities:
            return False

        self.identities[identity_id].state = new_state
        if new_state in [IdentityState.SUSPENDED, IdentityState.REVOKED, IdentityState.DELETED]:
            # Terminate active sessions
            for s in self.sessions.values():
                if s.identity_id == identity_id:
                    s.is_active = False

        self._audit("STATE_TRANSITION", {"identity_id": identity_id, "new_state": new_state.value})
        return True

    def validate_session(self, session_id: str) -> bool:
        """Validates session activity and expiration."""
        if session_id not in self.sessions:
            return False

        sess = self.sessions[session_id]
        if not sess.is_active or time.time() > sess.expires_at:
            sess.is_active = False
            return False
        return True

    def revoke_session(self, session_id: str) -> bool:
        """Revokes an active session."""
        if session_id not in self.sessions:
            return False
        self.sessions[session_id].is_active = False
        self._audit("SESSION_REVOKED", {"session_id": session_id})
        return True

    def _audit(self, event_type: str, details: Dict[str, Any]):
        self.audit_log.append({
            "event": event_type,
            "details": details,
            "timestamp": time.time()
        })
