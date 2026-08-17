import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from src.agents.state import AgentState
from src.backend.core.permission_manager import Permission
from loguru import logger


class AgentLifecycleState(str, Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


class AgentMetadata(BaseModel):
    name: str
    description: str
    version: str = "1.0.0"
    min_system_version: str = "2.0.0"
    author: str = "Captain AI OS"
    capabilities: List[str] = Field(default_factory=list)
    permissions_required: List[Permission] = Field(default_factory=list)
    dependencies_required: List[str] = Field(default_factory=list)


class BaseAgent(ABC):
    """
    Abstract Base Class for all pluggable sub-agents in Captain AI OS.
    Enforces standardized metadata, lifecycle state management, and error handling.
    """
    def __init__(self):
        self._state: AgentLifecycleState = AgentLifecycleState.UNINITIALIZED
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # Default state = SET (Running/Unpaused)

    @property
    def lifecycle_state(self) -> AgentLifecycleState:
        return self._state

    @property
    @abstractmethod
    def metadata(self) -> AgentMetadata:
        pass

    async def check_pause(self):
        """Cooperative pause checkpoint called inside agent execute() loops or streams."""
        await self._pause_event.wait()

    async def initialize(self) -> bool:
        """Lifecycle hook: Initialize agent resources."""
        self._state = AgentLifecycleState.INITIALIZING
        logger.info(f"Agent [{self.metadata.name}] initializing...")
        try:
            success = await self._on_initialize()
            if success:
                self._state = AgentLifecycleState.READY
                logger.info(f"Agent [{self.metadata.name}] initialized successfully.")
                return True
            else:
                self._state = AgentLifecycleState.FAILED
                logger.error(f"Agent [{self.metadata.name}] initialization returned False.")
                return False
        except Exception as e:
            logger.error(f"Agent [{self.metadata.name}] initialization exception: {e}")
            self._state = AgentLifecycleState.FAILED
            return False

    async def _on_initialize(self) -> bool:
        """Custom agent initialization logic to be overridden by subclasses."""
        return True

    @abstractmethod
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute agent task. Must be implemented by subclasses."""
        pass

    async def shutdown(self) -> bool:
        """Lifecycle hook: Clean up agent resources."""
        logger.info(f"Agent [{self.metadata.name}] shutting down...")
        try:
            await self._on_shutdown()
            self._state = AgentLifecycleState.STOPPED
            return True
        except Exception as e:
            logger.error(f"Agent [{self.metadata.name}] shutdown error: {e}")
            self._state = AgentLifecycleState.FAILED
            return False

    async def _on_shutdown(self):
        """Custom agent shutdown logic to be overridden by subclasses."""
        pass

    async def health_check(self) -> bool:
        """Health check indicator."""
        return self._state in [AgentLifecycleState.READY, AgentLifecycleState.RUNNING]

    async def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Pure pass-through execution stub. All state management is owned by AgentLifecycleManager."""
        return await self.execute(state)
