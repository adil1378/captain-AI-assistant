"""
Unit & Integration Tests for Volume 12 Part 12E Autonomous Optimization Architecture.
Verifies real-time system health analysis, self-healing action execution,
predictive maintenance forecasting, and dynamic resource allocation tuning.
"""

import pytest
from src.backend.core.autonomous_optimization_manager import (
    AutonomousOptimizationManager,
    OptimizationType
)


def test_system_health_analysis_and_auto_self_healing():
    aom = AutonomousOptimizationManager()

    # Normal metrics -> high health score
    status = aom.analyze_system_health(
        cpu_percent=45.0,
        memory_percent=55.0,
        api_latency_ms=120.0,
        error_rate_percent=0.0
    )
    assert status.health_score == 100.0
    assert len(aom.healing_history) == 0

    # Critical degraded metrics -> health score drops below 60.0 & auto-triggers self-healing
    critical_status = aom.analyze_system_health(
        cpu_percent=95.0,
        memory_percent=92.0,
        api_latency_ms=1500.0,
        error_rate_percent=8.0
    )
    assert critical_status.health_score < 60.0
    assert len(aom.healing_history) == 1
    assert aom.healing_history[0].action_type == OptimizationType.SERVICE_RESTART


def test_predictive_maintenance_forecasting():
    aom = AutonomousOptimizationManager()

    # High RAM utilization -> predictive maintenance alert
    aom.analyze_system_health(cpu_percent=50.0, memory_percent=89.0, api_latency_ms=200.0, error_rate_percent=0.0)
    preds = aom.predict_maintenance_needs()

    assert len(preds) == 1
    assert preds[0].bottleneck_subsystem == "MemoryManager"
    assert preds[0].risk_score == 8.5


def test_resource_allocation_tuning():
    aom = AutonomousOptimizationManager()

    alloc = aom.optimize_resource_allocation(
        agent_id="agent_coder",
        target_cpu_share=2.0,
        target_ram_mb=4096
    )

    assert alloc["agent_id"] == "agent_coder"
    assert alloc["target_ram_mb"] == 4096
    assert aom.resource_allocations["agent_coder"]["target_cpu_share"] == 2.0
