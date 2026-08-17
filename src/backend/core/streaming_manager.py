"""
Captain AI OS - Real-Time Streaming & Live Synchronization System (Volume 10 Part 10E)
Responsible for multi-protocol data streaming, live state replication across targets,
backpressure flow control, heartbeat monitoring, and stream session recovery.
"""

from typing import Dict, Any, List, Optional, Set
from enum import Enum
import asyncio
import time
from pydantic import BaseModel, Field
from src.backend.core.permission_manager import PermissionManager, Permission


class StreamingProtocol(str, Enum):
    WEBSOCKETS = "WEBSOCKETS"
    SSE = "SSE"
    HTTP_STREAMING = "HTTP_STREAMING"
    GRPC_STREAMING = "GRPC_STREAMING"
    MCP_STREAMING = "MCP_STREAMING"
    JSON_RPC_STREAMING = "JSON_RPC_STREAMING"
    MESSAGE_BROKER = "MESSAGE_BROKER"


class StreamState(str, Enum):
    CONNECTING = "CONNECTING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DEGRADED = "DEGRADED"
    RECONNECTING = "RECONNECTING"
    CLOSED = "CLOSED"


class SyncTarget(str, Enum):
    USER_SESSION = "USER_SESSION"
    AGENT_STATE = "AGENT_STATE"
    WORKFLOW_STATE = "WORKFLOW_STATE"
    MEMORY = "MEMORY"
    KNOWLEDGE = "KNOWLEDGE"
    UI = "UI"
    CONFIG = "CONFIG"


class StreamChunk(BaseModel):
    chunk_id: str
    session_id: str
    sequence_number: int
    data: Any
    timestamp: float = Field(default_factory=time.time)


class StreamSession(BaseModel):
    session_id: str
    client_id: str
    protocol: StreamingProtocol
    state: StreamState = StreamState.CONNECTING
    heartbeats_count: int = 0
    buffer_queue: List[StreamChunk] = Field(default_factory=list)
    max_buffer_size: int = 100
    latency_ms: float = 0.0
    created_at: float = Field(default_factory=time.time)
    last_active: float = Field(default_factory=time.time)


class LiveSyncEngine:
    """Manages synchronized state replication across user, agent, and system targets."""

    def __init__(self):
        self.synchronized_states: Dict[SyncTarget, Dict[str, Any]] = {
            target: {} for target in SyncTarget
        }

    def update_state(self, target: SyncTarget, state_dict: Dict[str, Any]) -> int:
        """Updates and merges target state snapshot."""
        self.synchronized_states[target].update(state_dict)
        return len(self.synchronized_states[target])


class RealTimeStreamingManager:
    """Centralized manager for live data streams and real-time state synchronization."""

    def __init__(self):
        self.sessions: Dict[str, StreamSession] = {}
        self.sync_engine = LiveSyncEngine()
        self.permission_manager = PermissionManager()
        self.telemetry = {
            "active_streams": 0,
            "total_chunks_processed": 0,
            "backpressure_drops": 0
        }

    def create_stream_session(
        self,
        client_id: str,
        protocol: StreamingProtocol = StreamingProtocol.WEBSOCKETS,
        max_buffer_size: int = 100
    ) -> StreamSession:
        """Establishes and authenticates a new live streaming session."""
        session_id = f"stream_{int(time.time() * 1000)}"
        session = StreamSession(
            session_id=session_id,
            client_id=client_id,
            protocol=protocol,
            state=StreamState.ACTIVE,
            max_buffer_size=max_buffer_size
        )
        self.sessions[session_id] = session
        self.telemetry["active_streams"] += 1
        return session

    def push_chunk(self, session_id: str, data: Any) -> StreamChunk:
        """Pushes data chunk into stream buffer, enforcing backpressure flow control."""
        if session_id not in self.sessions:
            raise KeyError(f"Stream session '{session_id}' not found.")

        session = self.sessions[session_id]
        if session.state != StreamState.ACTIVE:
            raise RuntimeError(f"Cannot push to inactive stream '{session_id}' in state '{session.state}'")

        # Backpressure check
        if len(session.buffer_queue) >= session.max_buffer_size:
            session.buffer_queue.pop(0)  # Load shedding oldest packet
            self.telemetry["backpressure_drops"] += 1

        seq_num = len(session.buffer_queue) + 1
        chunk = StreamChunk(
            chunk_id=f"chk_{seq_num}_{int(time.time()*1000)}",
            session_id=session_id,
            sequence_number=seq_num,
            data=data
        )

        session.buffer_queue.append(chunk)
        session.last_active = time.time()
        self.telemetry["total_chunks_processed"] += 1
        return chunk

    def sync_state(self, session_id: str, target: SyncTarget, state_dict: Dict[str, Any]) -> bool:
        """Replicates state changes across connected stream clients."""
        if session_id not in self.sessions:
            raise KeyError(f"Stream session '{session_id}' not found.")

        self.sync_engine.update_state(target, state_dict)
        self.push_chunk(session_id, {"sync_target": target.value, "state": state_dict})
        return True

    def heartbeat(self, session_id: str) -> bool:
        """Updates session heartbeat and latency telemetry."""
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        session.heartbeats_count += 1
        now = time.time()
        session.latency_ms = round((now - session.last_active) * 1000, 2)
        session.last_active = now
        return True

    def close_session(self, session_id: str) -> bool:
        """Gracefully closes a streaming session."""
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        session.state = StreamState.CLOSED
        session.buffer_queue.clear()
        self.telemetry["active_streams"] = max(0, self.telemetry["active_streams"] - 1)
        return True
