"""
Unit & Integration Tests for Volume 12 Part 12F Collective Intelligence Architecture.
Verifies multi-agent team formation, consensus voting algorithms, conflict resolution audit traces,
and secure inter-agent knowledge exchange.
"""

import pytest
from src.backend.core.collective_intelligence_manager import (
    CollectiveIntelligenceManager,
    ConsensusStrategy,
    ConflictType
)


def test_team_formation_and_leadership_assignment():
    cim = CollectiveIntelligenceManager()

    candidates = [
        {"agent_id": "agent_coder", "capabilities": ["python_dev", "unit_test"]},
        {"agent_id": "agent_search", "capabilities": ["web_search", "rag_retrieval"]}
    ]

    team = cim.form_team(objective="Build Authentication Service", candidate_agents=candidates)

    assert team.team_id.startswith("team_")
    assert len(team.members) == 2
    assert team.members[0].is_leader is True
    assert team.members[0].role_name == "Team Leader"
    assert cim.analytics["teams_formed"] == 1


def test_consensus_voting_mechanisms():
    cim = CollectiveIntelligenceManager()

    votes = {
        "agent_1": "APPROVE_PLAN",
        "agent_2": "APPROVE_PLAN",
        "agent_3": "REJECT_PLAN"
    }

    record = cim.reach_consensus(
        proposal="Deploy to Production",
        votes=votes,
        strategy=ConsensusStrategy.MAJORITY_VOTE
    )

    assert record.winning_option == "APPROVE_PLAN"
    assert record.consensus_score == 0.67  # 2 out of 3 votes
    assert cim.analytics["consensus_decisions_reached"] == 1


def test_conflict_resolution_and_knowledge_exchange():
    cim = CollectiveIntelligenceManager()

    res = cim.resolve_conflict(
        conflict_type=ConflictType.RESOURCE_CONFLICT,
        conflicting_agents=["agent_coder", "agent_search"],
        resolution_details="Allocated secondary GPU instance to agent_search."
    )

    assert res["conflict_id"].startswith("confl_")
    assert res["conflict_type"] == ConflictType.RESOURCE_CONFLICT
    assert len(cim.conflicts_resolved) == 1

    # Inter-agent knowledge exchange
    exchanged = cim.exchange_knowledge("agent_coder", "agent_search", {"shared_context": "auth_tokens"})
    assert exchanged is True
    assert cim.analytics["knowledge_exchanges_count"] == 1
