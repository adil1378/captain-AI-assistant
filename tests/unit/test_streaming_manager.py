"""
Unit & Integration Tests for Volume 10 Part 10E Real-Time Streaming Architecture.
Verifies stream session creation, chunk push, backpressure flow control, live state sync,
heartbeat telemetry, and session closure.
"""

import pytest
from src.backend.core.streaming_manager import (
    RealTimeStreamingManager,
    StreamingProtocol,
    StreamState,
    SyncTarget,
    StreamChunk
)


def test_streaming_session_lifecycle():
    sm = RealTimeStreamingManager()
    session = sm.create_stream_session(
        client_id="WebUI_Client_1",
        protocol=StreamingProtocol.WEBSOCKETS,
        max_buffer_size=10
    )

    assert session.session_id.startswith("stream_")
    assert session.state == StreamState.ACTIVE
    assert sm.telemetry["active_streams"] == 1

    # Heartbeat check
    assert sm.heartbeat(session.session_id) is True
    assert session.heartbeats_count == 1

    # Graceful closure
    assert sm.close_session(session.session_id) is True
    assert session.state == StreamState.CLOSED
    assert sm.telemetry["active_streams"] == 0


def test_push_chunk_and_backpressure():
    sm = RealTimeStreamingManager()
    session = sm.create_stream_session(
        client_id="Agent_Stream_1",
        protocol=StreamingProtocol.SSE,
        max_buffer_size=2  # Very small buffer for testing backpressure
    )

    chunk1 = sm.push_chunk(session.session_id, "frame 1")
    chunk2 = sm.push_chunk(session.session_id, "frame 2")
    assert len(session.buffer_queue) == 2

    # Push 3rd chunk -> triggers backpressure load shedding of oldest frame
    chunk3 = sm.push_chunk(session.session_id, "frame 3")
    assert len(session.buffer_queue) == 2
    assert session.buffer_queue[-1].data == "frame 3"
    assert sm.telemetry["backpressure_drops"] == 1


def test_live_state_synchronization():
    sm = RealTimeStreamingManager()
    session = sm.create_stream_session(client_id="DesktopGUI_1")

    sync_data = {"active_tab": "dashboard", "dark_mode": True}
    success = sm.sync_state(session.session_id, SyncTarget.UI, sync_data)

    assert success is True
    assert sm.sync_engine.synchronized_states[SyncTarget.UI]["active_tab"] == "dashboard"
    assert len(session.buffer_queue) == 1
    assert session.buffer_queue[0].data["sync_target"] == "UI"
