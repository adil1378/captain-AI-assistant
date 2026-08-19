"""
Global Tool Execution Security Boundary Singleton & System Tool Registration.
All privileged tools across Captain AI OS must register and execute through this layer.
"""

import asyncio
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from src.tools.tool_registry import ToolRegistry, ToolMetadata
from src.tools.tool_invocation_layer import ToolInvocationLayer
from src.backend.core.permission_manager import permission_manager, Permission
from src.backend.core.event_bus import event_bus
from tools.system_tools import get_system_metrics, run_terminal_command
from tools.weather import get_live_weather
from loguru import logger


class EmptyToolArgs(BaseModel):
    pass


class WeatherArgs(BaseModel):
    city: str = Field(default="Karachi", description="Target city for weather report")


class TerminalCmdArgs(BaseModel):
    command: str = Field(..., description="Terminal shell command string to execute")
    timeout: int = Field(default=30, description="Execution timeout in seconds")


# Global Singleton Instances
global_tool_registry = ToolRegistry()
tool_invocation_layer = ToolInvocationLayer(
    registry=global_tool_registry,
    permission_manager=permission_manager,
    event_bus=event_bus
)

_tools_initialized = False


async def init_global_tools():
    """Register all core system tools into the global ToolRegistry under permission control."""
    global _tools_initialized
    if _tools_initialized:
        return

    # 1. System Metrics Tool
    meta_metrics = ToolMetadata(
        name="get_system_metrics",
        description="Retrieves live CPU, RAM, Disk, and Battery metrics",
        category="system",
        args_schema=EmptyToolArgs,
        permissions_required=[Permission.SYS_EXEC]
    )

    async def _metrics_handler():
        return get_system_metrics()

    await global_tool_registry.register_tool(meta_metrics, _metrics_handler)

    # 2. Weather Reporting Tool
    meta_weather = ToolMetadata(
        name="get_live_weather",
        description="Fetches live weather report for a city",
        category="network",
        args_schema=WeatherArgs,
        permissions_required=[Permission.SYS_EXEC]
    )

    async def _weather_handler(city: str = "Karachi"):
        return get_live_weather(city)

    await global_tool_registry.register_tool(meta_weather, _weather_handler)

    # 3. Terminal Command Tool
    meta_terminal = ToolMetadata(
        name="run_terminal_command",
        description="Executes a shell command safely",
        category="system",
        args_schema=TerminalCmdArgs,
        permissions_required=[Permission.SYS_EXEC],
        is_dangerous=True
    )

    async def _terminal_handler(command: str, timeout: int = 30):
        return run_terminal_command(command, timeout=timeout)

    await global_tool_registry.register_tool(meta_terminal, _terminal_handler)

    _tools_initialized = True
    logger.info("Global Tools initialized and registered in ToolRegistry.")
