import time
import asyncio
import inspect
from enum import Enum
from typing import Dict, Any, Optional, List, AsyncGenerator
from pydantic import BaseModel, ValidationError
from src.tools.tool_registry import ToolRegistry, ToolDefinition
from src.backend.core.permission_manager import PermissionManager, Permission
from src.backend.core.event_bus import AsyncEventBus
from loguru import logger


class ToolExecutionStatus(str, Enum):
    SUCCESS = "success"
    PERMISSION_DENIED = "permission_denied"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT = "timeout"
    EXECUTION_ERROR = "execution_error"


class MCPStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    DEGRADED = "DEGRADED"


class ToolExecutionResult(BaseModel):
    """Normalized payload returned by ToolInvocationLayer after tool execution."""
    tool_name: str
    status: ToolExecutionStatus
    result: Any = None
    error: Optional[str] = None
    execution_time_seconds: float = 0.0


class MCPAvailabilityTracker:
    """Tracks availability status for tools originating from external MCP servers."""
    def __init__(self):
        self._status_map: Dict[str, MCPStatus] = {}

    def get_status(self, tool_name: str) -> MCPStatus:
        return self._status_map.get(tool_name, MCPStatus.AVAILABLE)

    def set_status(self, tool_name: str, status: MCPStatus):
        self._status_map[tool_name] = status
        logger.info(f"MCPAvailabilityTracker: Tool '{tool_name}' availability changed to {status.value}")


class ToolInvocationLayer:
    """
    Enterprise Tool Invocation Layer.
    Pure execution engine enforcing PermissionManager policies, Pydantic argument validation,
    execution timeouts, and event-based streaming output.
    """
    def __init__(self, registry: ToolRegistry, permission_manager: PermissionManager, event_bus: AsyncEventBus, default_timeout: float = 30.0):
        self.registry = registry
        self.permission_manager = permission_manager
        self.event_bus = event_bus
        self.default_timeout = default_timeout
        self.mcp_tracker = MCPAvailabilityTracker()

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any], caller_agent_name: str) -> ToolExecutionResult:
        """
        Executes a registered tool under permission, validation, and timeout guards.
        Returns a standardized ToolExecutionResult payload.
        """
        start_time = time.time()

        # Step 1: Check Tool Availability
        if self.mcp_tracker.get_status(tool_name) == MCPStatus.UNAVAILABLE:
            return ToolExecutionResult(
                tool_name=tool_name,
                status=ToolExecutionStatus.EXECUTION_ERROR,
                error=f"Tool '{tool_name}' is currently UNAVAILABLE due to MCP connection failure.",
                execution_time_seconds=time.time() - start_time
            )

        tool_def = self.registry.get_tool(tool_name)
        if not tool_def:
            return ToolExecutionResult(
                tool_name=tool_name,
                status=ToolExecutionStatus.EXECUTION_ERROR,
                error=f"Tool '{tool_name}' not found in ToolRegistry.",
                execution_time_seconds=time.time() - start_time
            )

        meta = tool_def.metadata

        # Step 2: Permission Enforcement
        for perm in meta.permissions_required:
            if not self.permission_manager.check_permission(perm):
                logger.warning(f"ToolInvocationLayer: Permission DENIED for agent '{caller_agent_name}' on tool '{tool_name}' (Required: {perm})")
                return ToolExecutionResult(
                    tool_name=tool_name,
                    status=ToolExecutionStatus.PERMISSION_DENIED,
                    error=f"Agent '{caller_agent_name}' lacks required permission: {perm.value}",
                    execution_time_seconds=time.time() - start_time
                )

        # Step 3: Pydantic Argument Validation
        try:
            validated_args = meta.args_schema(**arguments).model_dump()
        except ValidationError as val_err:
            logger.error(f"ToolInvocationLayer: Argument validation failed for tool '{tool_name}': {val_err}")
            return ToolExecutionResult(
                tool_name=tool_name,
                status=ToolExecutionStatus.VALIDATION_ERROR,
                error=f"Argument validation failed: {val_err}",
                execution_time_seconds=time.time() - start_time
            )

        # Step 4: Execute Under Timeout Boundary
        timeout_sec = meta.timeout_seconds if meta.timeout_seconds > 0 else self.default_timeout
        try:
            if inspect.iscoroutinefunction(tool_def.handler):
                res = await asyncio.wait_for(tool_def.handler(**validated_args), timeout=timeout_sec)
            else:
                res = tool_def.handler(**validated_args)

            return ToolExecutionResult(
                tool_name=tool_name,
                status=ToolExecutionStatus.SUCCESS,
                result=res,
                execution_time_seconds=time.time() - start_time
            )
        except asyncio.TimeoutError:
            logger.error(f"ToolInvocationLayer: Tool '{tool_name}' exceeded timeout boundary of {timeout_sec}s")
            return ToolExecutionResult(
                tool_name=tool_name,
                status=ToolExecutionStatus.TIMEOUT,
                error=f"Tool '{tool_name}' timed out after {timeout_sec} seconds.",
                execution_time_seconds=time.time() - start_time
            )
        except ConnectionRefusedError as conn_err:
            logger.error(f"ToolInvocationLayer: MCP tool '{tool_name}' connection refused: {conn_err}")
            self.mcp_tracker.set_status(tool_name, MCPStatus.UNAVAILABLE)
            return ToolExecutionResult(
                tool_name=tool_name,
                status=ToolExecutionStatus.EXECUTION_ERROR,
                error=f"MCP connection failed: {conn_err}",
                execution_time_seconds=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"ToolInvocationLayer: Execution exception in tool '{tool_name}': {e}")
            return ToolExecutionResult(
                tool_name=tool_name,
                status=ToolExecutionStatus.EXECUTION_ERROR,
                error=str(e),
                execution_time_seconds=time.time() - start_time
            )

    async def stream_tool(self, tool_name: str, arguments: Dict[str, Any], caller_agent_name: str) -> AsyncGenerator[str, None]:
        """
        Streams stdout lines from an AsyncGenerator tool handler.
        Performs permission check BEFORE streaming starts and publishes ToolStdoutChunk events.
        """
        tool_def = self.registry.get_tool(tool_name)
        if not tool_def:
            raise KeyError(f"Tool '{tool_name}' not found in ToolRegistry.")

        meta = tool_def.metadata

        # Permission check BEFORE streaming begins
        for perm in meta.permissions_required:
            if not self.permission_manager.check_permission(perm):
                raise PermissionError(f"Agent '{caller_agent_name}' lacks required permission: {perm.value}")

        validated_args = meta.args_schema(**arguments).model_dump()
        generator = tool_def.handler(**validated_args)

        if not inspect.isasyncgen(generator):
            raise TypeError(f"Handler for tool '{tool_name}' is not an AsyncGenerator.")

        async for chunk in generator:
            line = str(chunk)
            asyncio.create_task(
                self.event_bus.publish(
                    "ToolStdoutChunk",
                    "ToolInvocationLayer",
                    {"tool": tool_name, "chunk": line, "agent": caller_agent_name}
                )
            )
            yield line
