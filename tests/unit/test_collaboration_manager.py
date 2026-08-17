"""
Unit & Integration Tests for Volume 10 Part 10C Collaboration Architecture.
Verifies collaboration session initialization, task delegation, shared context updates,
consensus resolution policies, and conflict management.
"""

import pytest
from src.backend.core.collaboration_manager import (
    CollaborationManager,
    CollaborationType,
    ConsensusPolicy,
    AgentProposal,
    CollaborationSession
)


def test_collaboration_session_lifecycle():
    cm = CollaborationManager()
    session = cm.create_session(
        initiator_agent_id="SearchAgent",
        participating_agents=["CodingAgent", "SystemAgent"],
        goal="Build and verify web microservice",
        collaboration_type=CollaborationType.MULTI_AGENT_WORKFLOW
    )

    assert session.session_id.startswith("collab_")
    assert session.is_active is True
    assert "CodingAgent" in session.participating_agents
    assert session.shared_context.goal == "Build and verify web microservice"

    # Terminate session
    assert cm.terminate_session(session.session_id) is True
    assert cm.sessions[session.session_id].is_active is False


def test_task_delegation_and_shared_context():
    cm = CollaborationManager()
    session = cm.create_session(
        initiator_agent_id="MasterSupervisor",
        participating_agents=["SearchAgent", "CodingAgent"],
        goal="Automate scraper module"
    )

    # Delegate sub-task
    success = cm.delegate_task(
        session_id=session.session_id,
        from_agent_id="MasterSupervisor",
        target_agent_id="CodingAgent",
        task_name="generate_parser",
        sub_task_params={"target_url": "https://example.com"}
    )
    assert success is True
    assert session.shared_context.task_states["generate_parser"] == "DELEGATED_TO_CodingAgent"

    # Update shared context
    cm.update_shared_context(
        session_id=session.session_id,
        agent_id="CodingAgent",
        key="parser_code",
        value="def parse(): pass"
    )
    assert session.shared_context.intermediate_results["parser_code"] == "def parse(): pass"
    assert session.shared_context.version == 2


def test_consensus_resolution_confidence():
    cm = CollaborationManager()
    session = cm.create_session(
        initiator_agent_id="SearchAgent",
        participating_agents=["AgentA", "AgentB"],
        goal="Resolve optimal execution path"
    )

    proposals = [
        AgentProposal(proposal_id="p1", agent_id="AgentA", content="Path A", confidence_score=0.75),
        AgentProposal(proposal_id="p2", agent_id="AgentB", content="Path B", confidence_score=0.95)
    ]

    winner = cm.resolve_agent_conflict(
        session_id=session.session_id,
        proposals=proposals,
        policy=ConsensusPolicy.CONFIDENCE_BASED
    )

    assert winner.agent_id == "AgentB"
    assert winner.confidence_score == 0.95
    assert cm.analytics["conflicts_resolved"] == 1


def test_consensus_resolution_majority():
    cm = CollaborationManager()
    session = cm.create_session(
        initiator_agent_id="Supervisor",
        participating_agents=["Agent1", "Agent2", "Agent3"],
        goal="Vote on strategy"
    )

    proposals = [
        AgentProposal(proposal_id="p1", agent_id="Agent1", content="Option X"),
        AgentProposal(proposal_id="p2", agent_id="Agent2", content="Option Y"),
        AgentProposal(proposal_id="p3", agent_id="Agent3", content="Option X")
    ]

    winner = cm.resolve_agent_conflict(
        session_id=session.session_id,
        proposals=proposals,
        policy=ConsensusPolicy.MAJORITY
    )

    assert winner.content == "Option X"
