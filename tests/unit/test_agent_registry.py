import pytest
import asyncio
from src.agents.base_agent import BaseAgent, AgentMetadata, AgentLifecycleState
from src.agents.agent_registry import AgentRegistry


class AgentA(BaseAgent):
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="agent_a",
            description="Agent A",
            version="1.0.0",
            capabilities=["cap_a"]
        )

    async def execute(self, state):
        return {"current_agent": "agent_a", "result": "processed_by_a"}


class SlowInitializingAgent(BaseAgent):
    """Agent with artificial delay in _on_initialize to test real async lock contention."""
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="slow_agent",
            description="Slow initializing agent",
            version="1.0.0",
            capabilities=["slow_cap"]
        )

    async def _on_initialize(self) -> bool:
        await asyncio.sleep(0.05)  # Artificial async IO delay
        return True

    async def execute(self, state):
        return {"current_agent": "slow_agent"}


class AgentBCollision(BaseAgent):
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="agent_b_collision",
            description="Agent B with duplicate capability",
            version="1.0.0",
            capabilities=["cap_a"]
        )

    async def execute(self, state):
        return {"current_agent": "agent_b_collision"}


class AgentWithDep(BaseAgent):
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="agent_with_dep",
            description="Agent requiring Agent A",
            version="1.0.0",
            capabilities=["cap_dep"],
            dependencies_required=["agent_a"]
        )

    async def execute(self, state):
        return {"current_agent": "agent_with_dep", "result": "dep_satisfied"}


class AgentIncompatibleVersion(BaseAgent):
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="incompatible_agent",
            description="Requires system 3.0.0",
            version="1.0.0",
            min_system_version="3.0.0"
        )

    async def execute(self, state):
        return {}


def test_agent_registry_async_initialize_and_state_ready():
    async def _test():
        registry = AgentRegistry(system_version="2.0.0")
        agent_a = AgentA()

        assert agent_a.lifecycle_state == AgentLifecycleState.UNINITIALIZED

        ok, errors = await registry.register_agent(agent_a)
        assert ok is True
        assert len(errors) == 0

        assert agent_a.lifecycle_state == AgentLifecycleState.READY
        assert await agent_a.health_check() is True

        res = await agent_a({"user_query": "test"})
        assert res["result"] == "processed_by_a"

    asyncio.run(_test())


def test_capability_collision_detection():
    async def _test():
        registry = AgentRegistry(system_version="2.0.0")
        agent_a = AgentA()
        agent_b = AgentBCollision()

        await registry.register_agent(agent_a)
        ok, errors = await registry.register_agent(agent_b)

        assert ok is False
        assert any("Capability collision" in err for err in errors)

    asyncio.run(_test())


def test_topological_dependency_resolution_order_independence():
    async def _test():
        registry = AgentRegistry(system_version="2.0.0")
        dep_agent = AgentWithDep()
        agent_a = AgentA()

        ok_fail, errors_fail = await registry.register_agent(dep_agent)
        assert ok_fail is False
        assert any("missing required dependencies" in err for err in errors_fail)

        ok_a, _ = await registry.register_agent(agent_a)
        assert ok_a is True

        ok_dep, _ = await registry.register_agent(dep_agent)
        assert ok_dep is True
        assert dep_agent.lifecycle_state == AgentLifecycleState.READY

    asyncio.run(_test())


def test_semver_compatibility_enforcement():
    async def _test():
        registry = AgentRegistry(system_version="2.0.0")
        incompat_agent = AgentIncompatibleVersion()

        ok, errors = await registry.register_agent(incompat_agent)
        assert ok is False
        assert any("requires system version >=3.0.0" in err for err in errors)

    asyncio.run(_test())


def test_constructor_dependency_injection_factory():
    async def _test():
        factory_instantiated_classes = []

        def tracking_factory(cls):
            instance = cls()
            factory_instantiated_classes.append(cls)
            return instance

        registry = AgentRegistry(system_version="2.0.0", agent_factory=tracking_factory)

        # Execute discover_agents to exercise factory container instantiation
        await registry.discover_agents(package_path="src/agents")

        # Explicitly assert that the tracking DI factory was invoked by discovery
        assert len(factory_instantiated_classes) > 0
        assert len(registry.list_agents()) > 0
        assert registry.get_agent("chat_agent").lifecycle_state == AgentLifecycleState.READY

    asyncio.run(_test())


def test_concurrency_lock_real_overlapping_execution():
    async def _test():
        registry = AgentRegistry(system_version="2.0.0")
        slow_agent1 = SlowInitializingAgent()
        slow_agent2 = SlowInitializingAgent()

        # Fire 2 registration tasks overlapping concurrently
        t1 = asyncio.create_task(registry.register_agent(slow_agent1))
        t2 = asyncio.create_task(registry.register_agent(slow_agent2))

        r1, r2 = await asyncio.gather(t1, t2, return_exceptions=True)

        results = [r1, r2]
        successes = [r for r in results if isinstance(r, tuple) and r[0] is True]
        failures = [r for r in results if isinstance(r, tuple) and r[0] is False]

        assert len(successes) == 1
        assert len(failures) == 1
        assert registry.get_agent("slow_agent").lifecycle_state == AgentLifecycleState.READY

    asyncio.run(_test())
