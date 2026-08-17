import asyncio
import inspect
from typing import Dict, List, Optional, Tuple, Type, Callable, Any
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool, StructuredTool
from src.backend.core.permission_manager import Permission
from loguru import logger


class ToolMetadata(BaseModel):
    """Metadata schema defining tool attributes and required system permissions."""
    name: str
    description: str
    category: str = "system"  # "system", "file", "network", "mcp"
    args_schema: Type[BaseModel]
    permissions_required: List[Permission] = Field(default_factory=list)
    timeout_seconds: float = 30.0
    is_dangerous: bool = False


class ToolDefinition:
    """Pairing of tool metadata and its executable async handler callable."""
    def __init__(self, metadata: ToolMetadata, handler: Callable[..., Any]):
        self.metadata = metadata
        self.handler = handler


class ToolRegistry:
    """
    Injectable Tool Registry Container.
    Indexes local tools, native system utilities, and dynamic MCP tools.
    Provides schema normalization and conversion to LangChain BaseTool objects.
    """
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._pending: List[Tuple[ToolMetadata, Callable[..., Any]]] = []
        self._lock = asyncio.Lock()

    async def register_tool(self, metadata: ToolMetadata, handler: Callable[..., Any]) -> Tuple[bool, List[str]]:
        """
        Register a tool instance asynchronously under lock.
        Validates metadata and indexes the handler callable.
        """
        async with self._lock:
            return await self._register_tool_internal(metadata, handler)

    async def _register_tool_internal(self, metadata: ToolMetadata, handler: Callable[..., Any]) -> Tuple[bool, List[str]]:
        errors = []

        if metadata.name in self._tools:
            errors.append(f"Tool '{metadata.name}' is already registered.")

        if not callable(handler):
            errors.append(f"Handler for tool '{metadata.name}' is not callable.")

        if errors:
            logger.error(f"ToolRegistry: Registration checks failed for '{metadata.name}': {errors}")
            return False, errors

        self._tools[metadata.name] = ToolDefinition(metadata=metadata, handler=handler)
        logger.info(f"ToolRegistry: Registered tool '{metadata.name}' (Category: {metadata.category})")
        return True, []

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Retrieve registered ToolDefinition by tool name."""
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """Return names of all registered tools."""
        return list(self._tools.keys())

    def to_langchain_tool(self, name: str) -> Optional[BaseTool]:
        """Convert a registered tool into a LangChain StructuredTool instance."""
        tool_def = self.get_tool(name)
        if not tool_def:
            return None

        # StructuredTool handles coroutines natively
        return StructuredTool.from_function(
            name=tool_def.metadata.name,
            description=tool_def.metadata.description,
            args_schema=tool_def.metadata.args_schema,
            coroutine=tool_def.handler
        )

    def tool(self, name: str, description: str, args_schema: Type[BaseModel], permissions: List[Permission] = None, timeout: float = 30.0, category: str = "system", is_dangerous: bool = False):
        """Sync decorator shortcut storing registrations in a pending queue."""
        def decorator(func: Callable[..., Any]):
            meta = ToolMetadata(
                name=name,
                description=description,
                category=category,
                args_schema=args_schema,
                permissions_required=permissions or [],
                timeout_seconds=timeout,
                is_dangerous=is_dangerous
            )
            self._pending.append((meta, func))
            return func
        return decorator

    async def flush_pending(self) -> Tuple[int, List[str]]:
        """Asynchronously register all tools queued via the @tool decorator."""
        async with self._lock:
            flushed = 0
            all_errors = []
            for meta, func in self._pending:
                success, errors = await self._register_tool_internal(meta, func)
                if success:
                    flushed += 1
                else:
                    all_errors.extend(errors)
            self._pending.clear()
            return flushed, all_errors
