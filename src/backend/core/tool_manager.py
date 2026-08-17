import asyncio
import inspect
from typing import Dict, Any, Callable, List, Optional
from src.backend.core.permission_manager import permission_manager, Permission
from src.backend.core.event_bus import event_bus
from loguru import logger


class ToolMetadata:
    def __init__(self, name: str, description: str, permissions: List[Permission], requires_user_confirm: bool = False):
        self.name = name
        self.description = description
        self.permissions = permissions
        self.requires_user_confirm = requires_user_confirm


class MCPToolManager:
    """Model Context Protocol (MCP) Tool Manager & Execution Sandbox."""
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._metadata: Dict[str, ToolMetadata] = {}

    def register_tool(self, name: str, description: str, permissions: List[Permission], handler: Callable, requires_user_confirm: bool = False):
        """Register a tool with its metadata and permission constraints."""
        self._tools[name] = handler
        self._metadata[name] = ToolMetadata(name, description, permissions, requires_user_confirm)
        logger.info(f"MCPToolManager: Registered tool '{name}' (Permissions: {[p.value for p in permissions]})")

    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Validate permissions and execute tool safely."""
        if tool_name not in self._tools:
            return {"status": "error", "error": f"Tool '{tool_name}' is not registered."}

        meta = self._metadata[tool_name]

        # Permission check
        for perm in meta.permissions:
            if not permission_manager.check_permission(perm):
                return {
                    "status": "error",
                    "error": f"Permission DENIED for tool '{tool_name}'. Missing permission: {perm.value}"
                }

        await event_bus.publish("ToolStarted", "MCPToolManager", {"tool": tool_name, "args": kwargs})

        try:
            handler = self._tools[tool_name]
            if inspect.iscoroutinefunction(handler):
                result = await handler(**kwargs)
            else:
                result = handler(**kwargs)

            await event_bus.publish("ToolFinished", "MCPToolManager", {"tool": tool_name, "status": "success"})
            return {"status": "success", "result": result}
        except Exception as e:
            logger.error(f"MCPToolManager: Tool '{tool_name}' execution error: {e}")
            await event_bus.publish("ToolFinished", "MCPToolManager", {"tool": tool_name, "status": "error", "error": str(e)})
            return {"status": "error", "error": str(e)}


# Global Singleton Tool Manager Instance
tool_manager = MCPToolManager()
