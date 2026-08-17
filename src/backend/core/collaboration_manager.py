"""
Captain AI OS - Collaboration & Multi-Agent Communication System (Volume 10 Part 10C)
Responsible for multi-agent session coordination, shared context synchronization,
task delegation, consensus building, conflict resolution, and collaboration analytics.
"""

from typing import Dict, Any, List, Optional, Set
from enum import Enum
import asyncio
import time
from pydantic import BaseModel, Field
from src.backend.core.permission_manager import PermissionManager, Permission


class CollaborationType(str, Enum):
    AGENT_TO_AGENT = "AGENT_TO_AGENT"
    MULTI_AGENT_WORKFLOW = "MULTI_AGENT_WORKFLOW"
    PARALLEL = "PARALLEL"
    SEQUENTIAL = "SEQUENTIAL"
    HUMAN_IN_LOOP = "HUMAN_IN_LOOP"
    EXTERNAL_AI = "EXTERNAL_AI"


class ConsensusPolicy(str, Enum):
    MAJORITY = "MAJORITY"
    WEIGHTED = "WEIGHTED"
    SUPERVISOR_APPROVAL = "SUPERVISOR_APPROVAL"
    CONFIDENCE_BASED = "CONFIDENCE_BASED"


class AgentProposal(BaseModel):
    proposal_id: str
    agent_id: str
    content: Any
    confidence_score: float = 1.0
    timestamp: float = Field(default_factory=time.time)


class SharedContext(BaseModel):
    goal: str
    task_states: Dict[str, str] = Field(default_factory=dict)
    intermediate_results: Dict[str, Any] = Field(default_factory=dict)
    knowledge_references: List[str] = Field(default_factory=list)
    resource_locks: Set[str] = Field(default_factory=set)
    version: int = 1


class CollaborationSession(BaseModel):
    session_id: str
    initiator_agent_id: str
    participating_agents: List[str]
    collaboration_type: CollaborationType
    shared_context: SharedContext
    is_active: bool = True
    created_at: float = Field(default_factory=time.time)
    history: List[Dict[str, Any]] = Field(default_factory=list)


class ConsensusEngine:
    """Evaluates multi-agent proposals and resolves conflicts using configured policies."""

    @staticmethod
    def resolve(proposals: List[AgentProposal], policy: ConsensusPolicy = ConsensusPolicy.CONFIDENCE_BASED) -> AgentProposal:
        if not proposals:
            raise ValueError("Cannot resolve consensus on empty proposal list.")

        if policy == ConsensusPolicy.CONFIDENCE_BASED:
            return max(proposals, key=lambda p: p.confidence_score)
        
        elif policy == ConsensusPolicy.MAJORITY:
            # Group proposals by string representation of content
            counts: Dict[str, int] = {}
            for p in proposals:
                key = str(p.content)
                counts[key] = counts.get(key, 0) + 1
            best_key = max(counts, key=counts.get) # type: ignore
            for p in proposals:
                if str(p.content) == best_key:
                    return p
            return proposals[0]

        # Default fallback
        return max(proposals, key=lambda p: p.confidence_score)


class CollaborationManager:
    """Centralized Multi-Agent Collaboration & Coordination Manager."""

    def __init__(self):
        self.sessions: Dict[str, CollaborationSession] = {}
        self.permission_manager = PermissionManager()
        self.analytics = {
            "total_sessions": 0,
            "conflicts_resolved": 0,
            "delegations_count": 0
        }

    def create_session(
        self,
        initiator_agent_id: str,
        participating_agents: List[str],
        goal: str,
        collaboration_type: CollaborationType = CollaborationType.MULTI_AGENT_WORKFLOW
    ) -> CollaborationSession:
        """Initializes a new multi-agent collaboration session with synchronized shared context."""
        session_id = f"collab_{int(time.time() * 1000)}"
        all_agents = list(set([initiator_agent_id] + participating_agents))

        context = SharedContext(goal=goal)
        session = CollaborationSession(
            session_id=session_id,
            initiator_agent_id=initiator_agent_id,
            participating_agents=all_agents,
            collaboration_type=collaboration_type,
            shared_context=context
        )

        self.sessions[session_id] = session
        self.analytics["total_sessions"] += 1
        return session

    def delegate_task(
        self,
        session_id: str,
        from_agent_id: str,
        target_agent_id: str,
        task_name: str,
        sub_task_params: Dict[str, Any]
    ) -> bool:
        """Delegates a sub-task from one agent to another within an active session."""
        if session_id not in self.sessions:
            raise KeyError(f"Collaboration session '{session_id}' not found.")

        session = self.sessions[session_id]
        if from_agent_id not in session.participating_agents or target_agent_id not in session.participating_agents:
            raise PermissionError("Unauthorized agent participation in delegation.")

        session.shared_context.task_states[task_name] = f"DELEGATED_TO_{target_agent_id}"
        session.history.append({
            "event": "TASK_DELEGATED",
            "from": from_agent_id,
            "to": target_agent_id,
            "task": task_name,
            "timestamp": time.time()
        })
        self.analytics["delegations_count"] += 1
        return True

    def update_shared_context(self, session_id: str, agent_id: str, key: str, value: Any) -> bool:
        """Synchronizes intermediate execution results into the shared context."""
        if session_id not in self.sessions:
            raise KeyError(f"Collaboration session '{session_id}' not found.")

        session = self.sessions[session_id]
        if agent_id not in session.participating_agents:
            raise PermissionError(f"Agent '{agent_id}' is not authorized in session '{session_id}'")

        session.shared_context.intermediate_results[key] = value
        session.shared_context.version += 1
        return True

    def resolve_agent_conflict(
        self,
        session_id: str,
        proposals: List[AgentProposal],
        policy: ConsensusPolicy = ConsensusPolicy.CONFIDENCE_BASED
    ) -> AgentProposal:
        """Resolves multi-agent proposal conflicts using consensus policies."""
        if session_id not in self.sessions:
            raise KeyError(f"Collaboration session '{session_id}' not found.")

        winning_proposal = ConsensusEngine.resolve(proposals, policy=policy)
        self.analytics["conflicts_resolved"] += 1

        self.sessions[session_id].history.append({
            "event": "CONFLICT_RESOLVED",
            "winner": winning_proposal.agent_id,
            "policy": policy.value,
            "timestamp": time.time()
        })
        return winning_proposal

    def terminate_session(self, session_id: str) -> bool:
        """Closes an active collaboration session."""
        if session_id not in self.sessions:
            return False
        self.sessions[session_id].is_active = False
        return True
