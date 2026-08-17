"""
Captain AI OS - Distributed Systems & Federation System (Volume 10 Part 10F)
Responsible for inter-instance discovery, node registration, cluster health monitoring,
capability-based distributed scheduling, workload rebalancing, and failover isolation.
"""

from typing import Dict, Any, List, Optional, Set
from enum import Enum
import asyncio
import time
from pydantic import BaseModel, Field
from src.backend.core.permission_manager import PermissionManager, Permission


class NodeRole(str, Enum):
    LEADER = "LEADER"
    WORKER = "WORKER"
    STANDBY = "STANDBY"
    ISOLATED = "ISOLATED"


class NodeStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNREACHABLE = "UNREACHABLE"
    FAILED = "FAILED"


class FederationNode(BaseModel):
    node_id: str
    hostname: str
    ip_address: str
    role: NodeRole = NodeRole.WORKER
    status: NodeStatus = NodeStatus.HEALTHY
    capabilities: List[str] = Field(default_factory=list)
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    active_tasks_count: int = 0
    last_heartbeat: float = Field(default_factory=time.time)


class DistributedTask(BaseModel):
    task_id: str
    task_name: str
    required_capabilities: List[str] = Field(default_factory=list)
    assigned_node_id: Optional[str] = None
    status: str = "PENDING"
    created_at: float = Field(default_factory=time.time)


class DistributedScheduler:
    """Selects optimal target nodes for task execution based on capability and load metrics."""

    @staticmethod
    def select_node(nodes: List[FederationNode], required_capabilities: List[str]) -> Optional[FederationNode]:
        healthy_nodes = [
            n for n in nodes
            if n.status == NodeStatus.HEALTHY and n.role != NodeRole.ISOLATED
        ]
        if not healthy_nodes:
            return None

        # Filter by required capabilities
        candidates = []
        for n in healthy_nodes:
            if all(cap in n.capabilities for cap in required_capabilities):
                candidates.append(n)

        if not candidates:
            return None

        # Select candidate with lowest CPU usage and task count
        return min(candidates, key=lambda n: (n.cpu_usage, n.active_tasks_count))


class FederationManager:
    """Centralized Cluster Coordination and Multi-Instance Federation Gateway."""

    def __init__(self, heartbeat_timeout_seconds: float = 30.0):
        self.heartbeat_timeout_seconds = heartbeat_timeout_seconds
        self.nodes: Dict[str, FederationNode] = {}
        self.active_tasks: Dict[str, DistributedTask] = {}
        self.permission_manager = PermissionManager()
        self.cluster_events: List[Dict[str, Any]] = []

    def register_node(self, node: FederationNode) -> bool:
        """Registers a new node into the federation cluster."""
        self.nodes[node.node_id] = node
        self._log_event("NODE_REGISTERED", {"node_id": node.node_id, "role": node.role.value})
        return True

    def update_heartbeat(self, node_id: str, cpu_usage: float, memory_usage: float, active_tasks_count: int) -> bool:
        """Updates live health telemetry for a cluster node."""
        if node_id not in self.nodes:
            return False

        node = self.nodes[node_id]
        node.cpu_usage = max(0.0, min(100.0, cpu_usage))
        node.memory_usage = max(0.0, min(100.0, memory_usage))
        node.active_tasks_count = active_tasks_count
        node.last_heartbeat = time.time()
        if node.status == NodeStatus.UNREACHABLE:
            node.status = NodeStatus.HEALTHY
        return True

    def schedule_task(self, task_name: str, required_capabilities: List[str]) -> DistributedTask:
        """Schedules a distributed task across candidate nodes."""
        node_list = list(self.nodes.values())
        target_node = DistributedScheduler.select_node(node_list, required_capabilities)

        task_id = f"dist_task_{int(time.time() * 1000)}"
        assigned_id = target_node.node_id if target_node else None
        status = "ASSIGNED" if target_node else "PENDING"

        if target_node:
            target_node.active_tasks_count += 1

        task = DistributedTask(
            task_id=task_id,
            task_name=task_name,
            required_capabilities=required_capabilities,
            assigned_node_id=assigned_id,
            status=status
        )

        self.active_tasks[task_id] = task
        self._log_event("TASK_SCHEDULED", {"task_id": task_id, "node_id": assigned_id})
        return task

    def isolate_unhealthy_nodes(self) -> List[str]:
        """Detects heartbeat timeouts and isolates failed nodes, triggering failover reassignments."""
        isolated_ids = []
        now = time.time()

        for node_id, node in self.nodes.items():
            if now - node.last_heartbeat > self.heartbeat_timeout_seconds:
                if node.status != NodeStatus.FAILED:
                    node.status = NodeStatus.FAILED
                    node.role = NodeRole.ISOLATED
                    isolated_ids.append(node_id)
                    self._log_event("NODE_ISOLATED", {"node_id": node_id})

                    # Reassign orphaned tasks
                    for task in self.active_tasks.values():
                        if task.assigned_node_id == node_id and task.status == "ASSIGNED":
                            task.status = "PENDING"
                            task.assigned_node_id = None

        return isolated_ids

    def get_cluster_status(self) -> Dict[str, Any]:
        """Returns unified telemetry summary for the federated cluster."""
        self.isolate_unhealthy_nodes()
        total_nodes = len(self.nodes)
        healthy_nodes = sum(1 for n in self.nodes.values() if n.status == NodeStatus.HEALTHY)
        return {
            "total_nodes": total_nodes,
            "healthy_nodes": healthy_nodes,
            "failed_nodes": total_nodes - healthy_nodes,
            "active_tasks_count": len(self.active_tasks)
        }

    def _log_event(self, event_type: str, details: Dict[str, Any]):
        self.cluster_events.append({
            "event_type": event_type,
            "details": details,
            "timestamp": time.time()
        })
