"""
Unit & Integration Tests for Volume 10 Part 10A Unified Communication System.
Verifies session creation, authentication, rate limiting, message routing, session termination,
and security audit logging.
"""

import pytest
import asyncio
from src.backend.core.communication_system import (
    UnifiedCommunicationGateway,
    ChannelType,
    CommunicationMessage,
    CommSession
)
from src.backend.core.permission_manager import Permission


def test_session_lifecycle():
    gateway = UnifiedCommunicationGateway(max_requests_per_minute=10)
    session = gateway.create_session(
        user_id="user_admin",
        channel=ChannelType.REST,
        permissions=[Permission.FS_READ, Permission.SYS_EXEC]
    )

    assert session.session_id.startswith("sess_")
    assert session.is_active is True
    assert gateway.validate_session(session.session_id) is True

    # Test termination
    assert gateway.terminate_session(session.session_id) is True
    assert gateway.validate_session(session.session_id) is False


def test_rate_limiting():
    gateway = UnifiedCommunicationGateway(max_requests_per_minute=3)
    session = gateway.create_session(user_id="user_dev", channel=ChannelType.WEBSOCKET)

    # 3 requests allowed
    assert gateway.check_rate_limit(session.session_id) is True
    assert gateway.check_rate_limit(session.session_id) is True
    assert gateway.check_rate_limit(session.session_id) is True

    # 4th request rejected by rate limiter
    assert gateway.check_rate_limit(session.session_id) is False


@pytest.mark.anyio
async def test_message_routing_and_audit():
    gateway = UnifiedCommunicationGateway(max_requests_per_minute=50)
    session = gateway.create_session(user_id="user_agent", channel=ChannelType.IPC)

    msg = CommunicationMessage(
        message_id="msg_1001",
        session_id=session.session_id,
        channel=ChannelType.IPC,
        sender="AgentRouter",
        recipient="CaptainSupervisor",
        payload={"query": "execute_task"}
    )

    res = await gateway.route_message(msg)
    assert res["status"] == "delivered"
    assert res["message_id"] == "msg_1001"

    # Verify security audit logs
    assert len(gateway.audit_logs) >= 2
    event_types = [log["event_type"] for log in gateway.audit_logs]
    assert "SESSION_CREATED" in event_types
    assert "MESSAGE_ROUTED" in event_types


@pytest.mark.anyio
async def test_invalid_session_rejection():
    gateway = UnifiedCommunicationGateway()
    msg = CommunicationMessage(
        message_id="msg_invalid",
        session_id="sess_nonexistent",
        channel=ChannelType.REST,
        sender="Hacker",
        recipient="System",
        payload={}
    )

    with pytest.raises(PermissionError):
        await gateway.route_message(msg)
