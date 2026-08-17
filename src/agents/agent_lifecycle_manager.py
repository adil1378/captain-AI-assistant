import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from src.agents.base_agent import BaseAgent, AgentLifecycleState
from src.agents.agent_registry import AgentRegistry
from src.backend.core.event_bus import AsyncEventBus
from src.agents.state import AgentState
from loguru import logger


class AgentInvalidStateTransitionError(Exception):
    """Raised when an invalid state transition is requested."""
    pass


class AgentTimeoutError(Exception):
    """Raised when an agent lifecycle operation exceeds timeout boundary."""
    pass


class AgentLifecycleManager:
    """
    Enterprise Agent Lifecycle Manager.
    Sole, authoritative owner of agent lifecycle states, task handles,
    pause/resume checkpoints, and recovery policies.
    """
    MAX_RECOVERY_ATTEMPTS = 3

    def __init__(self, registry: AgentRegistry, event_bus: AsyncEventBus, default_shutdown_timeout: float = 10.0):
        self.registry = registry
        self.event_bus = event_bus
        self.default_shutdown_timeout = default_shutdown_timeout

        self._states: Dict[str, AgentLifecycleState] = {}
        self._task_handles: Dict[str, asyncio.Task] = {}
        self._recovery_attempts: Dict[str, int] = {}
        self._lock = asyncio.Lock()

    def get_agent_state(self, agent_name: str) -> AgentLifecycleState:
        """Returns current lifecycle state for specified agent."""
        agent = self.registry.get_agent(agent_name)
        if not agent:
            raise KeyError(f"Agent '{agent_name}' not found in registry.")
        return self._states.get(agent_name, agent.lifecycle_state)

    async def _set_state(self, agent_name: str, new_state: AgentLifecycleState):
        """Internal helper to update state dictionary and publish EventBus state change non-blockingly."""
        old_state = self._states.get(agent_name, AgentLifecycleState.UNINITIALIZED)
        self._states[agent_name] = new_state
        
        # Synchronize BaseAgent._state read-only view
        agent = self.registry.get_agent(agent_name)
        if agent:
            agent._state = new_state

        logger.info(f"LifecycleManager: Agent '{agent_name}' state transition: {old_state} -> {new_state}")
        # Publish outside lock via background task to prevent event handler deadlocks
        asyncio.create_task(
            self.event_bus.publish(
                "AgentStateChanged",
                "AgentLifecycleManager",
                {"agent": agent_name, "from_state": old_state.value, "to_state": new_state.value}
            )
        )

    async def initialize_agent(self, agent_name: str) -> bool:
        """Transitions agent UNINITIALIZED -> INITIALIZING -> READY."""
        async with self._lock:
            agent = self.registry.get_agent(agent_name)
            if not agent:
                raise KeyError(f"Agent '{agent_name}' not found in registry.")

            curr_state = self._states.get(agent_name, agent.lifecycle_state)
            if curr_state not in [AgentLifecycleState.UNINITIALIZED, AgentLifecycleState.FAILED]:
                raise AgentInvalidStateTransitionError(f"Cannot initialize agent '{agent_name}' from state '{curr_state}'")

            await self._set_state(agent_name, AgentLifecycleState.INITIALIZING)

        # Execute initialization hooks
        try:
            success = await agent.initialize()
            async with self._lock:
                if success:
                    await self._set_state(agent_name, AgentLifecycleState.READY)
                    self._recovery_attempts[agent_name] = 0
                    return True
                else:
                    await self._set_state(agent_name, AgentLifecycleState.FAILED)
                    return False
        except Exception as e:
            logger.error(f"LifecycleManager: Initialization error for '{agent_name}': {e}")
            async with self._lock:
                await self._set_state(agent_name, AgentLifecycleState.FAILED)
            return False

    async def execute_agent(self, agent_name: str, state: AgentState) -> Dict[str, Any]:
        """
        Executes agent task using 3-phase lock pattern.
        Wraps execution inside asyncio.create_task handle for cancellation safety.
        """
        # Phase 1: LOCKED — Validate READY state & transition to RUNNING
        async with self._lock:
            agent = self.registry.get_agent(agent_name)
            if not agent:
                raise KeyError(f"Agent '{agent_name}' not found in registry.")

            curr_state = self._states.get(agent_name, agent.lifecycle_state)
            if curr_state != AgentLifecycleState.READY:
                raise AgentInvalidStateTransitionError(f"Cannot execute agent '{agent_name}' in state '{curr_state}'")

            await self._set_state(agent_name, AgentLifecycleState.RUNNING)

        # Phase 2: UNLOCKED — Execute agent task in background asyncio.Task
        task = asyncio.create_task(agent.execute(state))
        self._task_handles[agent_name] = task

        try:
            result = await task
            # Phase 3a: LOCKED — Successful completion -> transition to READY
            async with self._lock:
                self._task_handles.pop(agent_name, None)
                curr = self._states.get(agent_name)
                if curr == AgentLifecycleState.RUNNING:
                    await self._set_state(agent_name, AgentLifecycleState.READY)
            return result
        except asyncio.CancelledError:
            logger.warning(f"LifecycleManager: Execution task for '{agent_name}' was cancelled.")
            async with self._lock:
                self._task_handles.pop(agent_name, None)
            raise
        except Exception as e:
            logger.error(f"LifecycleManager: Execution error in agent '{agent_name}': {e}")
            # Phase 3b: LOCKED — Exception -> transition to FAILED
            async with self._lock:
                self._task_handles.pop(agent_name, None)
                await self._set_state(agent_name, AgentLifecycleState.FAILED)
            return {"error": str(e), "current_agent": agent_name}

    async def pause_agent(self, agent_name: str) -> bool:
        """Pauses an active RUNNING agent by clearing its _pause_event."""
        async with self._lock:
            agent = self.registry.get_agent(agent_name)
            if not agent:
                raise KeyError(f"Agent '{agent_name}' not found in registry.")

            curr_state = self._states.get(agent_name, agent.lifecycle_state)
            if curr_state != AgentLifecycleState.RUNNING:
                raise AgentInvalidStateTransitionError(f"Cannot pause agent '{agent_name}' in state '{curr_state}'")

            agent._pause_event.clear()
            await self._set_state(agent_name, AgentLifecycleState.PAUSED)
            asyncio.create_task(
                self.event_bus.publish("AgentPaused", "AgentLifecycleManager", {"agent": agent_name, "timestamp": datetime.now(timezone.utc).isoformat()})
            )
            return True

    async def resume_agent(self, agent_name: str) -> bool:
        """Resumes a PAUSED agent by setting its _pause_event."""
        async with self._lock:
            agent = self.registry.get_agent(agent_name)
            if not agent:
                raise KeyError(f"Agent '{agent_name}' not found in registry.")

            curr_state = self._states.get(agent_name, agent.lifecycle_state)
            if curr_state != AgentLifecycleState.PAUSED:
                raise AgentInvalidStateTransitionError(f"Cannot resume agent '{agent_name}' in state '{curr_state}'")

            agent._pause_event.set()
            await self._set_state(agent_name, AgentLifecycleState.RUNNING)
            asyncio.create_task(
                self.event_bus.publish("AgentResumed", "AgentLifecycleManager", {"agent": agent_name, "timestamp": datetime.now(timezone.utc).isoformat()})
            )
            return True

    async def shutdown_agent(self, agent_name: str, timeout: Optional[float] = None) -> bool:
        """
        Cancels active execution task handle and executes BaseAgent.shutdown() under timeout.
        Transitions state -> STOPPED (or FAILED if timed out).
        """
        shutdown_timeout = timeout if timeout is not None else self.default_shutdown_timeout

        async with self._lock:
            agent = self.registry.get_agent(agent_name)
            if not agent:
                raise KeyError(f"Agent '{agent_name}' not found in registry.")

            # Ensure pause_event is unblocked so shutdown doesn't wait on pause
            agent._pause_event.set()

            # Cancel active running task handle if present
            task = self._task_handles.pop(agent_name, None)
            if task and not task.done():
                task.cancel()

        # Await task cancellation if task existed
        if task:
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass

        # Execute shutdown hook under timeout boundary
        try:
            success = await asyncio.wait_for(agent.shutdown(), timeout=shutdown_timeout)
            async with self._lock:
                if success:
                    await self._set_state(agent_name, AgentLifecycleState.STOPPED)
                    return True
                else:
                    await self._set_state(agent_name, AgentLifecycleState.FAILED)
                    return False
        except asyncio.TimeoutError:
            logger.error(f"LifecycleManager: Shutdown timeout ({shutdown_timeout}s) exceeded for '{agent_name}'")
            asyncio.create_task(
                self.event_bus.publish("AgentExecutionTimeout", "AgentLifecycleManager", {"agent": agent_name, "timeout_seconds": shutdown_timeout})
            )
            async with self._lock:
                await self._set_state(agent_name, AgentLifecycleState.FAILED)
            return False
        except Exception as e:
            logger.error(f"LifecycleManager: Shutdown exception for '{agent_name}': {e}")
            async with self._lock:
                await self._set_state(agent_name, AgentLifecycleState.FAILED)
            return False

    async def recover_agent(self, agent_name: str) -> bool:
        """Attempts recovery of FAILED agent by executing teardown and re-initialization."""
        async with self._lock:
            agent = self.registry.get_agent(agent_name)
            if not agent:
                raise KeyError(f"Agent '{agent_name}' not found in registry.")

            attempts = self._recovery_attempts.get(agent_name, 0)
            if attempts >= self.MAX_RECOVERY_ATTEMPTS:
                logger.error(f"LifecycleManager: Max recovery attempts ({self.MAX_RECOVERY_ATTEMPTS}) exceeded for '{agent_name}'")
                return False

            self._recovery_attempts[agent_name] = attempts + 1

        # Teardown current state
        try:
            await agent.shutdown()
        except Exception:
            pass

        # Re-initialize agent cleanly
        async with self._lock:
            await self._set_state(agent_name, AgentLifecycleState.UNINITIALIZED)

        success = await self.initialize_agent(agent_name)
        asyncio.create_task(
            self.event_bus.publish("AgentRecovered", "AgentLifecycleManager", {"agent": agent_name, "success": success})
        )
        return success
