import pytest
import asyncio
from typing import Dict, Any
from src.agents.base_agent import BaseAgent, AgentMetadata, AgentLifecycleState
from src.agents.agent_registry import AgentRegistry
from src.agents.agent_lifecycle_manager import (
    AgentLifecycleManager,
    AgentInvalidStateTransitionError,
    AgentTimeoutError
)
from src.backend.core.event_bus import AsyncEventBus


class MockLongRunningAgent(BaseAgent):
    """Mock agent executing a multi-step loop with check_pause checkpoints."""
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="mock_long_running",
            description="Mock long running agent",
            version="1.0.0",
            capabilities=["long_task"]
        )

    async def execute(self, state):
        steps_completed = 0
        for i in range(5):
            await self.check_pause()
            await asyncio.sleep(0.04)
            steps_completed += 1
        return {"current_agent": "mock_long_running", "steps": steps_completed}


class MockHangingShutdownAgent(BaseAgent):
    """Mock agent whose _on_shutdown hangs indefinitely."""
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="mock_hanging",
            description="Mock hanging agent",
            version="1.0.0",
            capabilities=["hang"]
        )

    async def _on_shutdown(self):
        await asyncio.sleep(100.0)

    async def execute(self, state):
        return {"current_agent": "mock_hanging"}


class MockFailingAgent(BaseAgent):
    """Mock agent whose execute throws an exception."""
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="mock_failing",
            description="Mock failing agent",
            version="1.0.0",
            capabilities=["fail"]
        )

    async def execute(self, state):
        raise RuntimeError("Simulated agent execution error")


def test_lifecycle_state_transition_enforcement():
    async def _test():
        registry = AgentRegistry()
        event_bus = AsyncEventBus()
        manager = AgentLifecycleManager(registry, event_bus)

        agent = MockLongRunningAgent()
        await registry.register_agent(agent)

        # Initial state should be READY (since register_agent initializes)
        assert manager.get_agent_state("mock_long_running") == AgentLifecycleState.READY

        # Invalid transition: cannot initialize an already READY agent
        with pytest.raises(AgentInvalidStateTransitionError):
            await manager.initialize_agent("mock_long_running")

        # Invalid transition: cannot pause a READY (non-RUNNING) agent
        with pytest.raises(AgentInvalidStateTransitionError):
            await manager.pause_agent("mock_long_running")

    asyncio.run(_test())


def test_pause_mid_execution():
    async def _test():
        registry = AgentRegistry()
        event_bus = AsyncEventBus()
        manager = AgentLifecycleManager(registry, event_bus)

        agent = MockLongRunningAgent()
        await registry.register_agent(agent)

        # Start execution in background task
        exec_task = asyncio.create_task(manager.execute_agent("mock_long_running", {"user_query": "run"}))
        await asyncio.sleep(0.06)  # Allow task to enter RUNNING loop

        # Pause agent mid-execution
        ok = await manager.pause_agent("mock_long_running")
        assert ok is True
        assert manager.get_agent_state("mock_long_running") == AgentLifecycleState.PAUSED

        # Verify task is suspended and has not completed yet
        assert not exec_task.done()

        # Clean up by shutting down
        await manager.shutdown_agent("mock_long_running", timeout=1.0)
        try:
            await exec_task
        except (asyncio.CancelledError, Exception):
            pass

    asyncio.run(_test())


def test_resume_context_restoration():
    async def _test():
        registry = AgentRegistry()
        event_bus = AsyncEventBus()
        manager = AgentLifecycleManager(registry, event_bus)

        agent = MockLongRunningAgent()
        await registry.register_agent(agent)

        exec_task = asyncio.create_task(manager.execute_agent("mock_long_running", {"user_query": "run"}))
        await asyncio.sleep(0.06)

        # Pause agent
        await manager.pause_agent("mock_long_running")
        assert manager.get_agent_state("mock_long_running") == AgentLifecycleState.PAUSED

        # Resume agent
        res_ok = await manager.resume_agent("mock_long_running")
        assert res_ok is True
        assert manager.get_agent_state("mock_long_running") == AgentLifecycleState.RUNNING

        # Task should complete cleanly and return result
        result = await exec_task
        assert result["steps"] == 5
        assert manager.get_agent_state("mock_long_running") == AgentLifecycleState.READY

    asyncio.run(_test())


def test_shutdown_timeout_enforcement():
    async def _test():
        registry = AgentRegistry()
        event_bus = AsyncEventBus()
        manager = AgentLifecycleManager(registry, event_bus)

        hanging_agent = MockHangingShutdownAgent()
        await registry.register_agent(hanging_agent)

        # Enforce shutdown with 0.1s timeout
        ok = await manager.shutdown_agent("mock_hanging", timeout=0.1)
        assert ok is False
        assert manager.get_agent_state("mock_hanging") == AgentLifecycleState.FAILED

    asyncio.run(_test())


def test_failed_recovery_path():
    async def _test():
        registry = AgentRegistry()
        event_bus = AsyncEventBus()
        manager = AgentLifecycleManager(registry, event_bus)

        failing_agent = MockFailingAgent()
        await registry.register_agent(failing_agent)

        # Execution fails and transitions state to FAILED
        res = await manager.execute_agent("mock_failing", {"user_query": "test"})
        assert "error" in res
        assert manager.get_agent_state("mock_failing") == AgentLifecycleState.FAILED

        # Recover agent
        recovered = await manager.recover_agent("mock_failing")
        assert recovered is True
        assert manager.get_agent_state("mock_failing") == AgentLifecycleState.READY

    asyncio.run(_test())


def test_concurrent_pause_and_shutdown_race():
    async def _test():
        registry = AgentRegistry()
        event_bus = AsyncEventBus()
        manager = AgentLifecycleManager(registry, event_bus)

        agent = MockLongRunningAgent()
        await registry.register_agent(agent)

        exec_task = asyncio.create_task(manager.execute_agent("mock_long_running", {"user_query": "run"}))
        await asyncio.sleep(0.06)

        # Fire pause and shutdown concurrently
        pause_task = asyncio.create_task(manager.pause_agent("mock_long_running"))
        shutdown_task = asyncio.create_task(manager.shutdown_agent("mock_long_running", timeout=1.0))

        results = await asyncio.gather(pause_task, shutdown_task, return_exceptions=True)

        # Lock protection ensures no race condition crashes occur
        assert manager.get_agent_state("mock_long_running") in [AgentLifecycleState.STOPPED, AgentLifecycleState.PAUSED, AgentLifecycleState.FAILED]

        try:
            await exec_task
        except (asyncio.CancelledError, Exception):
            pass

    asyncio.run(_test())
