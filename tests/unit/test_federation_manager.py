"""
Unit & Integration Tests for Volume 10 Part 10F Distributed Systems & Federation Architecture.
Verifies node registration, capability-based task scheduling, heartbeat tracking,
unhealthy node isolation, and task failover re-assignment.
"""

import pytest
import time
from src.backend.core.federation_manager import (
    FederationManager,
    FederationNode,
    NodeRole,
    NodeStatus,
    DistributedTask
)


def test_federation_node_registration_and_heartbeat():
    fm = FederationManager(heartbeat_timeout_seconds=5.0)

    node1 = FederationNode(
        node_id="node_leader_1",
        hostname="captain-leader",
        ip_address="192.168.1.10",
        role=NodeRole.LEADER,
        capabilities=["gpu_processing", "web_scraping"]
    )

    assert fm.register_node(node1) is True
    assert len(fm.nodes) == 1

    # Heartbeat update
    assert fm.update_heartbeat("node_leader_1", cpu_usage=25.5, memory_usage=40.0, active_tasks_count=2) is True
    assert fm.nodes["node_leader_1"].cpu_usage == 25.5


def test_distributed_task_scheduling():
    fm = FederationManager()

    node_gpu = FederationNode(
        node_id="node_gpu",
        hostname="gpu-worker",
        ip_address="192.168.1.20",
        capabilities=["cuda_inference", "vision_ocr"],
        cpu_usage=10.0
    )
    node_cpu = FederationNode(
        node_id="node_cpu",
        hostname="cpu-worker",
        ip_address="192.168.1.21",
        capabilities=["vision_ocr"],
        cpu_usage=5.0
    )

    fm.register_node(node_gpu)
    fm.register_node(node_cpu)

    # Schedule task requiring cuda_inference -> should pick node_gpu
    task1 = fm.schedule_task("deep_inference", required_capabilities=["cuda_inference"])
    assert task1.status == "ASSIGNED"
    assert task1.assigned_node_id == "node_gpu"

    # Schedule task requiring vision_ocr -> node_cpu has lower CPU usage (5.0 vs 10.0)
    task2 = fm.schedule_task("ocr_parse", required_capabilities=["vision_ocr"])
    assert task2.assigned_node_id == "node_cpu"


def test_unhealthy_node_isolation_and_failover():
    fm = FederationManager(heartbeat_timeout_seconds=0.1)  # 100ms timeout for testing

    node = FederationNode(
        node_id="node_temp",
        hostname="temp-worker",
        ip_address="10.0.0.5",
        capabilities=["search"]
    )
    fm.register_node(node)

    task = fm.schedule_task("search_web", required_capabilities=["search"])
    assert task.assigned_node_id == "node_temp"

    # Simulate heartbeat timeout by setting past timestamp
    fm.nodes["node_temp"].last_heartbeat = time.time() - 1.0

    isolated = fm.isolate_unhealthy_nodes()
    assert "node_temp" in isolated
    assert fm.nodes["node_temp"].status == NodeStatus.FAILED
    assert task.status == "PENDING"  # Task reassigned back to PENDING queue
