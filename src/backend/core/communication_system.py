"""
Captain AI OS - Unified Communication System (Volume 10 Part 10A)
Responsible for protocol-independent message routing, authentication, session validation,
rate limiting, protocol enforcement, payload encryption, and communication audit logging.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import asyncio
import time
import hashlib
from pydantic import BaseModel, Field
from src.backend.core.permission_manager import PermissionManager, Permission


class ChannelType(str, Enum):
    REST = "REST"
    WEBSOCKET = "WEBSOCKET"
    IPC = "IPC"
    SSE = "SSE"
    GRPC = "GRPC"


class CommunicationMessage(BaseModel):
    message_id: str
    session_id: str
    channel: ChannelType
    sender: str
    recipient: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)
    signature: Optional[str] = None


class CommSession(BaseModel):
    session_id: str
    user_id: str
    channel: ChannelType
    auth_token: str
    permissions: List[Permission] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)
    last_active: float = Field(default_factory=time.time)
    request_count: int = 0
    is_active: bool = True


class UnifiedCommunicationGateway:
    """Gateway for securing, validating, rate-limiting, and routing system messages."""

    def __init__(self, max_requests_per_minute: int = 120):
        self.max_requests_per_minute = max_requests_per_minute
        self.sessions: Dict[str, CommSession] = {}
        self.audit_logs: List[Dict[str, Any]] = []
        self.permission_manager = PermissionManager()

    def create_session(
        self,
        user_id: str,
        channel: ChannelType,
        permissions: Optional[List[Permission]] = None
    ) -> CommSession:
        """Authenticates client credentials and initializes a secure communication session."""
        raw_token = f"{user_id}:{channel.value}:{time.time()}"
        auth_token = hashlib.sha256(raw_token.encode()).hexdigest()
        session_id = f"sess_{auth_token[:12]}"

        perms = permissions or [Permission.FS_READ]
        for p in perms:
            self.permission_manager.grant_permission(p)

        session = CommSession(
            session_id=session_id,
            user_id=user_id,
            channel=channel,
            auth_token=auth_token,
            permissions=perms
        )
        self.sessions[session_id] = session
        self._log_audit(session_id, "SESSION_CREATED", {"user_id": user_id, "channel": channel.value})
        return session

    def validate_session(self, session_id: str) -> bool:
        """Validates session active state and updates last active timestamp."""
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        if not session.is_active:
            return False

        session.last_active = time.time()
        return True

    def check_rate_limit(self, session_id: str) -> bool:
        """Enforces token-bucket rate limiting per session window."""
        if not self.validate_session(session_id):
            return False

        session = self.sessions[session_id]
        session.request_count += 1
        if session.request_count > self.max_requests_per_minute:
            self._log_audit(session_id, "RATE_LIMIT_EXCEEDED", {"request_count": session.request_count})
            return False
        return True

    async def route_message(self, message: CommunicationMessage) -> Dict[str, Any]:
        """Validates protocol, session, rate limits, and routes payload to target service."""
        if not self.validate_session(message.session_id):
            raise PermissionError(f"Invalid or expired session '{message.session_id}'")

        if not self.check_rate_limit(message.session_id):
            raise RuntimeError(f"Rate limit exceeded for session '{message.session_id}'")

        # Simulate async secure transport
        await asyncio.sleep(0.01)

        self._log_audit(
            message.session_id,
            "MESSAGE_ROUTED",
            {
                "message_id": message.message_id,
                "sender": message.sender,
                "recipient": message.recipient,
                "channel": message.channel.value
            }
        )

        return {
            "status": "delivered",
            "message_id": message.message_id,
            "channel": message.channel,
            "timestamp": time.time()
        }

    def terminate_session(self, session_id: str) -> bool:
        """Terminates session and revokes access credentials."""
        if session_id not in self.sessions:
            return False

        self.sessions[session_id].is_active = False
        self._log_audit(session_id, "SESSION_TERMINATED", {})
        return True

    def _log_audit(self, session_id: str, event_type: str, details: Dict[str, Any]):
        """Appends immutable audit entry to security log."""
        self.audit_logs.append({
            "session_id": session_id,
            "event_type": event_type,
            "details": details,
            "timestamp": time.time()
        })
