import os
import sys
import asyncio
import importlib
import inspect
from typing import Dict, List, Optional, Tuple, Type, Callable
from packaging import version
from src.agents.base_agent import BaseAgent, AgentMetadata, AgentLifecycleState
from loguru import logger


class AgentRegistry:
    """
    Injectable Agent Registry & Auto-Discovery Engine.
    Supports Dependency Injection, Async Lifecycle Initialization, Hot-Reloading,
    Topological Dependency Resolution, Concurrency Lock Protection, and Semver Validation.
    """
    def __init__(self, system_version: str = "2.0.0", agent_factory: Optional[Callable[[Type[BaseAgent]], BaseAgent]] = None):
        self.system_version = system_version
        self.agent_factory = agent_factory or (lambda cls: cls())
        self._agents: Dict[str, BaseAgent] = {}
        self._capabilities: Dict[str, str] = {}  # capability -> agent_name
        self._module_map: Dict[str, str] = {}   # agent_name -> module_name
        self._lock = asyncio.Lock()

    async def register_agent(self, agent_instance: BaseAgent, module_name: Optional[str] = None) -> Tuple[bool, List[str]]:
        """
        Register an agent instance asynchronously under lock.
        Invokes await agent.initialize() and registers ONLY if state reaches READY.
        """
        async with self._lock:
            return await self._register_agent_internal(agent_instance, module_name=module_name)

    async def _register_agent_internal(self, agent_instance: BaseAgent, module_name: Optional[str] = None) -> Tuple[bool, List[str]]:
        errors = []
        meta = agent_instance.metadata

        # 0. Duplicate Agent Name Check
        if meta.name in self._agents:
            errors.append(f"Agent '{meta.name}' is already registered.")

        # 1. Semver Compatibility Check
        try:
            if version.parse(meta.min_system_version) > version.parse(self.system_version):
                errors.append(f"Agent '{meta.name}' requires system version >={meta.min_system_version}, but system version is '{self.system_version}'")
        except Exception as e:
            errors.append(f"Invalid semver version format for agent '{meta.name}': {e}")

        # 2. Capability Collision Check
        for cap in meta.capabilities:
            if cap in self._capabilities:
                errors.append(f"Capability collision: Capability '{cap}' is already registered by agent '{self._capabilities[cap]}'")

        # 3. Dependency Validation
        dep_success, missing_deps = self.validate_dependencies(agent_instance)
        if not dep_success:
            errors.append(f"Agent '{meta.name}' missing required dependencies: {missing_deps}")

        if errors:
            logger.error(f"AgentRegistry: Registration checks failed for '{meta.name}'. Errors: {errors}")
            return False, errors

        # 4. Async Lifecycle Initialization
        if agent_instance.lifecycle_state == AgentLifecycleState.UNINITIALIZED:
            init_ok = await agent_instance.initialize()
            if not init_ok or agent_instance.lifecycle_state != AgentLifecycleState.READY:
                errors.append(f"Agent '{meta.name}' failed initialization and remains in state '{agent_instance.lifecycle_state}'")
                return False, errors

        # Successful Registration (All state mutations strictly inside lock)
        self._agents[meta.name] = agent_instance
        for cap in meta.capabilities:
            self._capabilities[cap] = meta.name
        if module_name:
            self._module_map[meta.name] = module_name

        logger.info(f"AgentRegistry: Registered agent '{meta.name}' v{meta.version} (State: {agent_instance.lifecycle_state})")
        return True, []

    async def unregister_agent(self, name: str):
        """Unregister an agent asynchronously under lock."""
        async with self._lock:
            await self._unregister_agent_internal(name)

    async def _unregister_agent_internal(self, name: str):
        if name in self._agents:
            agent = self._agents[name]
            await agent.shutdown()
            for cap in agent.metadata.capabilities:
                if self._capabilities.get(cap) == name:
                    del self._capabilities[cap]
            del self._agents[name]
            if name in self._module_map:
                del self._module_map[name]
            logger.info(f"AgentRegistry: Unregistered agent '{name}'")

    def validate_dependencies(self, agent: BaseAgent) -> Tuple[bool, List[str]]:
        """Validate if all declared agent dependencies are currently registered."""
        missing = []
        for dep in agent.metadata.dependencies_required:
            if dep not in self._agents:
                missing.append(dep)
        return len(missing) == 0, missing

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Retrieve a registered agent by name."""
        return self._agents.get(name)

    def get_agent_by_capability(self, capability: str) -> Optional[BaseAgent]:
        """Lookup agent instance by registered capability."""
        agent_name = self._capabilities.get(capability)
        return self.get_agent(agent_name) if agent_name else None

    def list_agents(self) -> List[AgentMetadata]:
        """Return metadata for all registered agents."""
        return [agent.metadata for agent in self._agents.values()]

    async def reload_agent(self, agent_name: str) -> Tuple[bool, List[str]]:
        """
        Hot-reload an agent module from disk asynchronously under lock.
        Re-instantiates via agent_factory and invokes initialize().
        """
        async with self._lock:
            if agent_name not in self._module_map:
                return False, [f"Agent '{agent_name}' has no recorded module source for hot reload."]

            module_name = self._module_map[agent_name]
            logger.info(f"AgentRegistry: Hot-reloading agent module '{module_name}' for agent '{agent_name}'...")

            try:
                await self._unregister_agent_internal(agent_name)
                module = importlib.import_module(module_name)
                reloaded_module = importlib.reload(module)

                for item_name, cls in inspect.getmembers(reloaded_module, inspect.isclass):
                    if issubclass(cls, BaseAgent) and cls is not BaseAgent:
                        new_instance = self.agent_factory(cls)
                        return await self._register_agent_internal(new_instance, module_name=module_name)

                return False, [f"No BaseAgent subclass found in reloaded module '{module_name}'"]
            except Exception as e:
                logger.error(f"AgentRegistry: Hot reload failed for '{agent_name}': {e}")
                return False, [str(e)]

    async def discover_agents(self, package_path: str = "src/agents"):
        """
        Auto-discover and register all BaseAgent subclasses in package_path.
        Uses a multi-pass topological dependency resolution loop so discovery succeeds
        regardless of arbitrary file listing order. Uses agent_factory for DI.
        """
        logger.info(f"AgentRegistry: Discovering agents in '{package_path}'...")
        if not os.path.exists(package_path):
            logger.warning(f"AgentRegistry: Path '{package_path}' does not exist.")
            return

        discovered_candidates: List[Tuple[BaseAgent, Type[BaseAgent], str]] = []

        # Step 1: Collect candidate instances using self.agent_factory
        for entry in os.listdir(package_path):
            if entry.endswith(".py") and not entry.startswith("_") and entry != "base_agent.py" and entry != "state.py":
                module_name = f"src.agents.{entry[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for item_name, cls in inspect.getmembers(module, inspect.isclass):
                        if issubclass(cls, BaseAgent) and cls is not BaseAgent:
                            instance = self.agent_factory(cls)
                            discovered_candidates.append((instance, cls, module_name))
                except Exception as e:
                    logger.error(f"AgentRegistry: Discovery import error in '{module_name}': {e}")

        # Step 2: Multi-pass topological resolution loop
        pending = list(discovered_candidates)
        max_passes = len(pending) + 1
        current_pass = 0

        while pending and current_pass < max_passes:
            current_pass += 1
            progress_made = False
            remaining = []

            for instance, cls, module_name in pending:
                success, errors = await self.register_agent(instance, module_name=module_name)
                if success:
                    progress_made = True
                else:
                    remaining.append((instance, cls, module_name))

            pending = remaining
            if not progress_made:
                break

        if pending:
            failed_names = [instance.metadata.name for instance, _, _ in pending]
            logger.warning(f"AgentRegistry: Topological discovery completed with unresolved agents: {failed_names}")
