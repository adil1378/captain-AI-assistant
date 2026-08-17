import pytest
import asyncio
from src.agents.base_agent import BaseAgent, AgentMetadata, AgentLifecycleState
from src.agents.state import AgentState


class SampleTestAgent(BaseAgent):
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="sample_test_agent",
            description="Sample agent for unit testing",
            version="1.0.0",
            capabilities=["testing_capability"]
        )

    async def execute(self, state: AgentState):
        return {"current_agent": "sample_test_agent", "output": "success"}


def test_base_agent_metadata_and_initial_state():
    agent = SampleTestAgent()
    assert agent.metadata.name == "sample_test_agent"
    assert agent.metadata.version == "1.0.0"
    assert agent.lifecycle_state == AgentLifecycleState.UNINITIALIZED


def test_base_agent_lifecycle_transitions():
    async def _test():
        agent = SampleTestAgent()

        # Test Initialize
        init_ok = await agent.initialize()
        assert init_ok is True
        assert agent.lifecycle_state == AgentLifecycleState.READY
        assert await agent.health_check() is True

        # Test Execution pass-through
        state = {"user_query": "hello"}
        res = await agent(state)
        assert res["current_agent"] == "sample_test_agent"
        assert res["output"] == "success"

        # Test Shutdown
        shutdown_ok = await agent.shutdown()
        assert shutdown_ok is True
        assert agent.lifecycle_state == AgentLifecycleState.STOPPED
        assert await agent.health_check() is False

    asyncio.run(_test())


def test_base_agent_passthrough_call():
    async def _test():
        agent = SampleTestAgent()
        # Direct __call__ is a pure pass-through stub to execute()
        res = await agent({"user_query": "test"})
        assert res["output"] == "success"

    asyncio.run(_test())
