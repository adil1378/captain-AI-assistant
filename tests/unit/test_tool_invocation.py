import pytest
import asyncio
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from src.agents.base_agent import BaseAgent, AgentMetadata
from src.agents.agent_registry import AgentRegistry
from src.agents.agent_lifecycle_manager import AgentLifecycleManager
from src.backend.core.permission_manager import PermissionManager, Permission
from src.backend.core.event_bus import AsyncEventBus
from src.tools.tool_registry import ToolRegistry, ToolMetadata
from src.tools.tool_invocation_layer import ToolInvocationLayer, ToolExecutionStatus
from src.graph.state_graph import create_captain_graph


class ReadFileInputSchema(BaseModel):
    file_path: str = Field(description="Absolute path to file")


async def mock_read_file_handler(file_path: str) -> str:
    return f"Contents of {file_path}: Hello World"


class SlowToolInputSchema(BaseModel):
    delay: float = 1.0


async def mock_slow_tool_handler(delay: float) -> str:
    await asyncio.sleep(delay)
    return "Slow task finished"


class MCPToolInputSchema(BaseModel):
    query: str


async def mock_failing_mcp_handler(query: str) -> str:
    raise ConnectionRefusedError("MCP Server 127.0.0.1:8080 refused connection")


class MockToolAgent(BaseAgent):
    """Mock agent that calls execute_tool in its execute method."""
    def __init__(self, tool_layer: ToolInvocationLayer):
        super().__init__()
        self.tool_layer = tool_layer

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="coder_agent",
            description="Mock Coder Agent using tools",
            version="1.0.0",
            capabilities=["code"]
        )

    async def execute(self, state):
        res = await self.tool_layer.execute_tool(
            "read_file",
            {"file_path": "test.txt"},
            "coder_agent"
        )
        return {
            "messages": [AIMessage(content=f"[Tool Output]: {res.result}")],
            "current_agent": "coder_agent",
            "next_agent": "END"
        }


def test_tool_registration_and_langchain_conversion():
    async def _test():
        registry = ToolRegistry()
        meta = ToolMetadata(
            name="read_file",
            description="Read file from disk",
            args_schema=ReadFileInputSchema,
            permissions_required=[Permission.FS_READ]
        )
        ok, errors = await registry.register_tool(meta, mock_read_file_handler)
        assert ok is True
        assert len(errors) == 0

        tool_def = registry.get_tool("read_file")
        assert tool_def is not None
        assert tool_def.metadata.name == "read_file"

        lc_tool = registry.to_langchain_tool("read_file")
        assert lc_tool is not None
        assert lc_tool.name == "read_file"
        assert lc_tool.description == "Read file from disk"

    asyncio.run(_test())


def test_permission_enforcement():
    async def _test():
        registry = ToolRegistry()
        perm_mgr = PermissionManager()
        event_bus = AsyncEventBus()

        meta = ToolMetadata(
            name="read_file",
            description="Read file from disk",
            args_schema=ReadFileInputSchema,
            permissions_required=[Permission.FS_READ]
        )
        await registry.register_tool(meta, mock_read_file_handler)
        tool_layer = ToolInvocationLayer(registry, perm_mgr, event_bus)

        # 1. Revoke permission to test Permission Denied case
        perm_mgr.revoke_permission(Permission.FS_READ)
        res_denied = await tool_layer.execute_tool("read_file", {"file_path": "test.txt"}, "coder_agent")
        assert res_denied.status == ToolExecutionStatus.PERMISSION_DENIED
        assert "lacks required permission" in res_denied.error

        # 2. Grant permission back for Permission Granted case
        perm_mgr.grant_permission(Permission.FS_READ)
        res_granted = await tool_layer.execute_tool("read_file", {"file_path": "test.txt"}, "coder_agent")
        assert res_granted.status == ToolExecutionStatus.SUCCESS
        assert "Contents of test.txt" in res_granted.result

    asyncio.run(_test())


def test_execution_timeout_enforcement():
    async def _test():
        registry = ToolRegistry()
        perm_mgr = PermissionManager()
        event_bus = AsyncEventBus()

        meta = ToolMetadata(
            name="slow_tool",
            description="Slow executing tool",
            args_schema=SlowToolInputSchema,
            timeout_seconds=0.1
        )
        await registry.register_tool(meta, mock_slow_tool_handler)
        tool_layer = ToolInvocationLayer(registry, perm_mgr, event_bus)

        res = await tool_layer.execute_tool("slow_tool", {"delay": 1.0}, "chat_agent")
        assert res.status == ToolExecutionStatus.TIMEOUT
        assert "timed out after 0.1 seconds" in res.error

    asyncio.run(_test())


def test_mcp_disconnection_handling():
    async def _test():
        registry = ToolRegistry()
        perm_mgr = PermissionManager()
        event_bus = AsyncEventBus()

        meta = ToolMetadata(
            name="mcp_failing_tool",
            description="MCP tool that fails connection",
            args_schema=MCPToolInputSchema
        )
        await registry.register_tool(meta, mock_failing_mcp_handler)
        tool_layer = ToolInvocationLayer(registry, perm_mgr, event_bus)

        res = await tool_layer.execute_tool("mcp_failing_tool", {"query": "search"}, "chat_agent")
        assert res.status == ToolExecutionStatus.EXECUTION_ERROR
        assert "MCP connection failed" in res.error

    asyncio.run(_test())


def test_argument_validation_error():
    async def _test():
        registry = ToolRegistry()
        perm_mgr = PermissionManager()
        event_bus = AsyncEventBus()

        meta = ToolMetadata(
            name="read_file",
            description="Read file from disk",
            args_schema=ReadFileInputSchema
        )
        await registry.register_tool(meta, mock_read_file_handler)
        tool_layer = ToolInvocationLayer(registry, perm_mgr, event_bus)

        # Missing required parameter 'file_path'
        res = await tool_layer.execute_tool("read_file", {}, "chat_agent")
        assert res.status == ToolExecutionStatus.VALIDATION_ERROR
        assert "Argument validation failed" in res.error

    asyncio.run(_test())


def test_langgraph_integration_worker_invokes_execute_tool():
    async def _test():
        tool_registry = ToolRegistry()
        perm_mgr = PermissionManager()
        event_bus = AsyncEventBus()

        meta = ToolMetadata(
            name="read_file",
            description="Read file from disk",
            args_schema=ReadFileInputSchema,
            permissions_required=[Permission.FS_READ]
        )
        await tool_registry.register_tool(meta, mock_read_file_handler)
        tool_layer = ToolInvocationLayer(tool_registry, perm_mgr, event_bus)

        # Grant permission globally in perm_mgr
        perm_mgr.grant_permission(Permission.FS_READ)

        # Setup Agent Registry & Lifecycle Manager
        agent_registry = AgentRegistry()
        coder_agent = MockToolAgent(tool_layer)
        await agent_registry.register_agent(coder_agent)

        manager = AgentLifecycleManager(agent_registry, event_bus)
        graph = create_captain_graph(agent_registry, manager, checkpointer=MemorySaver())

        config = {"configurable": {"thread_id": "test_tool_session"}}
        initial_state = {
            "messages": [HumanMessage(content="write python script to read file")],
            "user_query": "write python script to read file"
        }

        result = await graph.ainvoke(initial_state, config=config)
        assert result["current_agent"] == "coder_agent"
        assert "[Tool Output]: Contents of test.txt" in result["messages"][-1].content

    asyncio.run(_test())
