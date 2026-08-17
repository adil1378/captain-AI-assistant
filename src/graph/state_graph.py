import re
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.agents.state import AgentState
from src.agents.agent_registry import AgentRegistry
from src.agents.agent_lifecycle_manager import AgentLifecycleManager
from src.backend.core.model_manager import model_manager
from src.backend.config import settings
from utils.text_utils import clean_think_tags
from loguru import logger

# All valid agent routing keys
_VALID_AGENTS = ["chat_agent", "coder_agent", "system_agent", "rag_agent", "search_agent", "comms_agent"]

# Keyword routing tables — ordered by specificity (most specific first)
_CODE_KEYWORDS = ["code", "def ", "function", "python", "bug", "class ", "script",
                  "refactor", "import ", "syntax", "debug", "compile", "algorithm",
                  "github", "git", "ci/cd", "pipeline", "workflow"]
_SYSTEM_KEYWORDS = ["cpu", "ram", "disk", "process", "system metrics", "memory usage",
                    "battery", "performance", "os info", "hardware",
                    "weather", "temperature", "forecast", "rain", "climate", "humid", "wind"]
_RAG_KEYWORDS = ["document", "pdf", "file", "my notes", "uploaded", "knowledge base",
                 "rag", "ingest", "search my", "find in", "from the doc"]
_SEARCH_KEYWORDS = ["search", "google", "web", "browse", "find online", "youtube",
                    "news", "latest", "current events", "website", "internet",
                    "image", "picture", "generate image", "genrate image", "genrate", "draw", "scrape", "http://", "https://"]
_COMMS_KEYWORDS = ["email", "mail", "whatsapp", "send message", "contact",
                   "save contact", "add contact", "phone", "call"]


async def router_node(state: AgentState) -> Dict[str, Any]:
    """
    Ultra-fast Deterministic & Keyword Intent Router.
    Zero-delay classification to eliminate latency before agent execution.
    """
    user_query = state.get("user_query", "").strip().lower()

    # Phase 1: Fast Deterministic Keyword Matching
    if any(k in user_query for k in _CODE_KEYWORDS):
        logger.info("RouterNode: keyword → coder_agent")
        return {"next_agent": "coder_agent"}
    if any(k in user_query for k in _SYSTEM_KEYWORDS):
        logger.info("RouterNode: keyword → system_agent")
        return {"next_agent": "system_agent"}
    if any(k in user_query for k in _RAG_KEYWORDS):
        logger.info("RouterNode: keyword → rag_agent")
        return {"next_agent": "rag_agent"}
    if any(k in user_query for k in _COMMS_KEYWORDS):
        logger.info("RouterNode: keyword → comms_agent")
        return {"next_agent": "comms_agent"}
    if any(k in user_query for k in _SEARCH_KEYWORDS):
        logger.info("RouterNode: keyword → search_agent")
        return {"next_agent": "search_agent"}

    # Default directly to chat_agent instantly without extra LLM delay
    logger.info("RouterNode: default → chat_agent")
    return {"next_agent": "chat_agent"}


def create_captain_graph(registry: AgentRegistry, manager: AgentLifecycleManager, checkpointer: Any = None):
    """
    Builds the production V2 LangGraph StateGraph engine.
    Integrates 6 pluggable agents with router_node and lifecycle manager execution.
    """
    if checkpointer is None:
        checkpointer = MemorySaver()
    builder = StateGraph(AgentState)

    # 1. Add Router Node
    builder.add_node("router_node", router_node)

    # 2. Wrap Agent Execution inside Lifecycle Manager Enforcement
    def make_agent_node(agent_name: str):
        async def agent_node_fn(state: AgentState) -> Dict[str, Any]:
            logger.info(f"LangGraph Node: invoking manager.execute_agent('{agent_name}')")
            res = await manager.execute_agent(agent_name, state)
            return res
        return agent_node_fn

    for agent_name in _VALID_AGENTS:
        builder.add_node(agent_name, make_agent_node(agent_name))

    # 3. Add Error Recovery Node
    async def error_node_fn(state: AgentState) -> Dict[str, Any]:
        err = state.get("error", "Unknown execution error")
        logger.error(f"ErrorNode: {err}")
        return {
            "messages": [AIMessage(content=f"I encountered an issue while processing your request: {err}")],
            "next_agent": "END"
        }
    builder.add_node("error_node", error_node_fn)

    # 4. Connect Edges
    builder.add_edge(START, "router_node")

    # Conditional Routing from router_node
    builder.add_conditional_edges(
        "router_node",
        lambda s: s.get("next_agent", "chat_agent"),
        {agent: agent for agent in _VALID_AGENTS}
    )

    # Agent output conditional edges
    def route_agent_output(state: AgentState) -> str:
        if state.get("error"):
            return "error_node"
        next_a = state.get("next_agent", "END")
        return next_a if next_a in _VALID_AGENTS else END

    for agent_name in _VALID_AGENTS:
        builder.add_conditional_edges(
            agent_name,
            route_agent_output,
            {**{a: a for a in _VALID_AGENTS}, "error_node": "error_node", END: END}
        )

    builder.add_edge("error_node", END)

    # Compile with checkpointer for state persistence across turns
    compiled_graph = builder.compile(checkpointer=checkpointer)
    logger.info("Captain AI OS V2 LangGraph StateGraph engine compiled successfully.")
    return compiled_graph
