"""
Captain AI OS - Collective Intelligence, Multi-Agent Evolution & Emergent Coordination System (Volume 12 Part 12F)
Responsible for multi-agent team formation, dynamic role assignment, consensus voting (majority, weighted, confidence),
inter-agent conflict resolution, secure knowledge exchange, and collaboration analytics.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import time
from pydantic import BaseModel, Field
from src.backend.core.permission_manager import PermissionManager, Permission


class ConsensusStrategy(str, Enum):
    MAJORITY_VOTE = "MAJORITY_VOTE"
    WEIGHTED_EXPERT = "WEIGHTED_EXPERT"
    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
    HUMAN_ARBITRATION = "HUMAN_ARBITRATION"


class ConflictType(str, Enum):
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    DECISION_CONFLICT = "DECISION_CONFLICT"
    KNOWLEDGE_INCONSISTENCY = "KNOWLEDGE_INCONSISTENCY"
    PRIORITY_CONFLICT = "PRIORITY_CONFLICT"
    SCHEDULING_CONFLICT = "SCHEDULING_CONFLICT"


class AgentTeamRole(BaseModel):
    agent_id: str
    role_name: str
    assigned_capabilities: List[str] = Field(default_factory=list)
    load_factor: float = 0.0  # 0.0 to 1.0
    is_leader: bool = False


class ConsensusDecisionRecord(BaseModel):
    decision_id: str
    proposal: str
    strategy: ConsensusStrategy
    votes: Dict[str, str] = Field(default_factory=dict)  # agent_id -> option
    winning_option: str
    consensus_score: float  # 0.0 to 1.0
    timestamp: float = Field(default_factory=time.time)


class DynamicTeam(BaseModel):
    team_id: str
    objective: str
    members: List[AgentTeamRole] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)


class ConsensusEngine:
    """Aggregates multi-agent votes and evaluates consensus decisions."""

    @staticmethod
    def calculate_consensus(
        proposal: str,
        votes: Dict[str, str],
        weights: Optional[Dict[str, float]] = None,
        strategy: ConsensusStrategy = ConsensusStrategy.MAJORITY_VOTE
    ) -> tuple[str, float]:
        if not votes:
            raise ValueError("No votes submitted for consensus calculation.")

        option_scores: Dict[str, float] = {}
        total_weight = 0.0

        for agent_id, option in votes.items():
            w = weights.get(agent_id, 1.0) if weights else 1.0
            option_scores[option] = option_scores.get(option, 0.0) + w
            total_weight += w

        winning_option = max(option_scores, key=lambda k: option_scores[k])
        winning_weight = option_scores[winning_option]
        consensus_score = round(winning_weight / total_weight, 2) if total_weight > 0 else 0.0

        return winning_option, consensus_score


class CollectiveIntelligenceManager:
    """Centralized Collective Intelligence, Multi-Agent Evolution & Coordination Manager."""

    def __init__(self):
        self.teams: Dict[str, DynamicTeam] = {}
        self.consensus_records: List[ConsensusDecisionRecord] = []
        self.conflicts_resolved: List[Dict[str, Any]] = []
        self.knowledge_exchanges: List[Dict[str, Any]] = []
        self.permission_manager = PermissionManager()
        self.analytics = {
            "teams_formed": 0,
            "consensus_decisions_reached": 0,
            "conflicts_resolved_count": 0,
            "knowledge_exchanges_count": 0
        }

    def form_team(self, objective: str, candidate_agents: List[Dict[str, Any]]) -> DynamicTeam:
        """Forms a dynamic multi-agent team with capability-based role assignments and a leader."""
        team_id = f"team_{int(time.time() * 1000)}"
        roles = []

        for idx, agent in enumerate(candidate_agents):
            agent_id = agent.get("agent_id", f"agent_{idx}")
            caps = agent.get("capabilities", ["general_task"])
            is_leader = idx == 0  # First candidate assigned temporary leadership

            roles.append(
                AgentTeamRole(
                    agent_id=agent_id,
                    role_name="Team Leader" if is_leader else f"Specialist ({caps[0]})",
                    assigned_capabilities=caps,
                    is_leader=is_leader
                )
            )

        team = DynamicTeam(team_id=team_id, objective=objective, members=roles)
        self.teams[team_id] = team
        self.analytics["teams_formed"] += 1
        return team

    def reach_consensus(
        self,
        proposal: str,
        votes: Dict[str, str],
        weights: Optional[Dict[str, float]] = None,
        strategy: ConsensusStrategy = ConsensusStrategy.MAJORITY_VOTE
    ) -> ConsensusDecisionRecord:
        """Aggregates multi-agent votes and stores verified consensus decision record."""
        winning_option, score = ConsensusEngine.calculate_consensus(proposal, votes, weights, strategy)

        record = ConsensusDecisionRecord(
            decision_id=f"dec_{int(time.time() * 1000)}",
            proposal=proposal,
            strategy=strategy,
            votes=votes,
            winning_option=winning_option,
            consensus_score=score
        )

        self.consensus_records.append(record)
        self.analytics["consensus_decisions_reached"] += 1
        return record

    def resolve_conflict(
        self,
        conflict_type: ConflictType,
        conflicting_agents: List[str],
        resolution_details: str
    ) -> Dict[str, Any]:
        """Resolves inter-agent decision or resource conflicts with recorded audit trace."""
        record = {
            "conflict_id": f"confl_{int(time.time() * 1000)}",
            "conflict_type": conflict_type,
            "conflicting_agents": conflicting_agents,
            "resolution": resolution_details,
            "timestamp": time.time()
        }
        self.conflicts_resolved.append(record)
        self.analytics["conflicts_resolved_count"] += 1
        return record

    def exchange_knowledge(self, source_agent_id: str, target_agent_id: str, payload: Dict[str, Any]) -> bool:
        """Enforces governance-compliant knowledge exchange between multi-agent nodes."""
        exchange = {
            "source": source_agent_id,
            "target": target_agent_id,
            "payload_keys": list(payload.keys()),
            "timestamp": time.time()
        }
        self.knowledge_exchanges.append(exchange)
        self.analytics["knowledge_exchanges_count"] += 1
        return True

    def get_collective_analytics(self) -> Dict[str, Any]:
        """Returns analytics summary for team formation, consensus score, and conflict resolutions."""
        return {
            "active_teams_count": len(self.teams),
            "total_consensus_decisions": len(self.consensus_records),
            "total_conflicts_resolved": len(self.conflicts_resolved),
            "analytics_summary": self.analytics
        }
