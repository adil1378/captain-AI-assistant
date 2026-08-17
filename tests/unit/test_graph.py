import pytest
import asyncio
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from src.agents.base_agent import BaseAgent, AgentMetadata, AgentLifecycleState
from src.agents.agent_registry import AgentRegistry
from src.agents.agent_lifecycle_manager import AgentLifecycleManager
from src.backend.core.event_bus import AsyncEventBus
from src.graph.state_graph import create_captain_graph


class MockGraphChatAgent(BaseAgent):
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="chat_agent",
            description="Mock chat agent",
            version="1.0.0",
            capabilities=["chat"]
        )

    async def execute(self, state):
        return {
            "messages": [AIMessage(content="Hello from Mock Chat Agent!")],
            "current_agent": "chat_agent",
            "next_agent": "END"
        }


class MockGraphCoderAgent(BaseAgent):
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="coder_agent",
            description="Mock coder agent",
            version="1.0.0",
            capabilities=["code"]
        )

    async def execute(self, state):
        return {
            "messages": [AIMessage(content="```python\nprint('Hello World')\n```")],
            "current_agent": "coder_agent",
            "next_agent": "END"
        }


class MockGraphSystemAgent(BaseAgent):
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="system_agent",
            description="Mock system agent",
            version="1.0.0",
            capabilities=["system"]
        )

    async def execute(self, state):
        return {
            "messages": [AIMessage(content="CPU Usage: 15% | RAM: 40%")],
            "current_agent": "system_agent",
            "next_agent": "END"
        }


async def setup_test_graph():
    registry = AgentRegistry()
    event_bus = AsyncEventBus()

    chat_agent = MockGraphChatAgent()
    coder_agent = MockGraphCoderAgent()
    system_agent = MockGraphSystemAgent()

    await registry.register_agent(chat_agent)
    await registry.register_agent(coder_agent)
    await registry.register_agent(system_agent)

    manager = AgentLifecycleManager(registry, event_bus)
    graph = create_captain_graph(registry, manager, checkpointer=MemorySaver())
    return graph, manager


def test_graph_compilation_structure():
    async def _test():
        graph, _ = await setup_test_graph()
        nodes = graph.nodes
        assert "router_node" in nodes
        assert "chat_agent" in nodes
        assert "coder_agent" in nodes
        assert "system_agent" in nodes
        assert "error_node" in nodes

    asyncio.run(_test())


def test_conditional_routing_coder_query():
    async def _test():
        graph, _ = await setup_test_graph()
        config = {"configurable": {"thread_id": "test_coder_session"}}
        initial_state = {
            "messages": [HumanMessage(content="write python script to sort a list")],
            "user_query": "write python script to sort a list"
        }

        result = await graph.ainvoke(initial_state, config=config)
        assert result["current_agent"] == "coder_agent"
        assert "print('Hello World')" in result["messages"][-1].content

    asyncio.run(_test())


def test_conditional_routing_chat_query():
    async def _test():
        graph, _ = await setup_test_graph()
        config = {"configurable": {"thread_id": "test_chat_session"}}
        initial_state = {
            "messages": [HumanMessage(content="hello, how are you?")],
            "user_query": "hello, how are you?"
        }

        result = await graph.ainvoke(initial_state, config=config)
        assert result["current_agent"] == "chat_agent"
        assert "Mock Chat Agent" in result["messages"][-1].content

    asyncio.run(_test())


def test_message_accumulation_add_messages_reducer():
    async def _test():
        graph, _ = await setup_test_graph()
        config = {"configurable": {"thread_id": "test_reducer_session"}}

        # Turn 1
        res1 = await graph.ainvoke({"messages": [HumanMessage(content="hello")], "user_query": "hello"}, config=config)
        assert len(res1["messages"]) == 2  # HumanMessage + AIMessage

        # Turn 2 on same thread_id
        res2 = await graph.ainvoke({"messages": [HumanMessage(content="write python script")], "user_query": "write python script"}, config=config)
        assert len(res2["messages"]) == 4  # Accumulated 2 HumanMessages + 2 AIMessages

    asyncio.run(_test())


def test_lifecycle_manager_integration_state_transitions():
    async def _test():
        graph, manager = await setup_test_graph()
        config = {"configurable": {"thread_id": "test_lifecycle_session"}}

        assert manager.get_agent_state("coder_agent") == AgentLifecycleState.READY

        initial_state = {
            "messages": [HumanMessage(content="write python script")],
            "user_query": "write python script"
        }
        await graph.ainvoke(initial_state, config=config)

        # After execution completes, agent should return to READY state
        assert manager.get_agent_state("coder_agent") == AgentLifecycleState.READY

    asyncio.run(_test())


def test_thread_id_session_continuity():
    async def _test():
        graph, _ = await setup_test_graph()
        session_config = {"configurable": {"thread_id": "user_session_42"}}

        # Invoke turn 1
        await graph.ainvoke({"messages": [HumanMessage(content="My name is Alice")], "user_query": "My name is Alice"}, config=session_config)

        # Invoke turn 2 on same thread
        res2 = await graph.ainvoke({"messages": [HumanMessage(content="hello")], "user_query": "hello"}, config=session_config)

        # Verify thread_id retrieved turn 1 messages automatically
        messages_text = [m.content for m in res2["messages"]]
        assert "My name is Alice" in messages_text

    asyncio.run(_test())
