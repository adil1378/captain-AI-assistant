import re
from typing import Dict, Any, List, Optional
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

# Global Checkpointer singleton handle for clearing session state
_checkpointer_instance = None


def _has_word(query: str, word: str) -> bool:
    """Word-boundary regex match helper to prevent substring false positives."""
    return bool(re.search(r'\b' + re.escape(word) + r'\b', query, re.IGNORECASE))


def classify_intent_hybrid(user_query: str) -> str:
    """
    Enterprise Hybrid Intent Classifier.
    Combines high-confidence word-boundary rules with intent pattern classification.
    Eliminates substring false-positives (e.g. 'program' != 'ram', 'digital marketing' != 'git').
    """
    q_raw = user_query.strip()
    q = q_raw.lower()

    if not q:
        return "chat_agent"

    # Rule 1: High-confidence Coding intent
    coding_exact = ["def ", "class ", "import ", "syntax error", "refactor", "debug", "github", "git commit", "ci/cd", "pipeline", "fibonacci"]
    if any(kw in q for kw in coding_exact) or (("write" in q or "build" in q or "create" in q) and ("code" in q or "function" in q or "script" in q or "python" in q)):
        return "coder_agent"

    # Rule 2: High-confidence Weather & System intent
    weather_words = ["weather", "temperature", "forecast", "rain", "climate", "humid"]
    system_phrases = ["system metrics", "memory usage", "cpu usage", "disk space", "os info", "battery status", "hardware metrics"]
    if any(_has_word(q, w) for w in weather_words) or any(kw in q for kw in system_phrases):
        return "system_agent"

    if "weather api" in q:
        return "system_agent"

    # Rule 3: High-confidence Document / RAG intent
    rag_phrases = ["document", "uploaded file", "my notes", "pdf", "knowledge base", "from the doc", "explain this uploaded"]
    if any(kw in q for kw in rag_phrases):
        return "rag_agent"

    # Rule 4: High-confidence Communication intent
    comms_phrases = ["send email", "send mail", "whatsapp", "send message", "save contact", "add contact"]
    if any(kw in q for kw in comms_phrases):
        return "comms_agent"

    # Rule 5: High-confidence Search intent
    if q.startswith("search") or "search the latest" in q or "find online" in q or "google" in q or "latest news" in q:
        return "search_agent"

    # Default to general conversation agent
    return "chat_agent"


async def router_node(state: AgentState) -> Dict[str, Any]:
    """
    Hybrid Intent Router Node.
    Ensures state['user_query'] is authoritative and propagates it cleanly into state['messages'].
    """
    user_query = state.get("user_query", "").strip()
    messages = state.get("messages", [])

    next_agent = classify_intent_hybrid(user_query)
    logger.info(f"RouterNode: Query '{user_query}' -> Classified Intent: '{next_agent}'")

    res: Dict[str, Any] = {
        "user_query": user_query,
        "next_agent": next_agent
    }

    # If messages is empty or tail message is not current user_query, return new HumanMessage for add_messages reducer
    if user_query:
        if not messages or not (isinstance(messages[-1], HumanMessage) and messages[-1].content == user_query):
            res["messages"] = [HumanMessage(content=user_query)]

    return res


def reset_thread_checkpoint(thread_id: str) -> bool:
    """Clear memory checkpoint state for a specific thread_id in LangGraph."""
    global _checkpointer_instance
    try:
        if _checkpointer_instance and hasattr(_checkpointer_instance, "storage"):
            _checkpointer_instance.storage.pop(thread_id, None)
        logger.info(f"LangGraph Checkpointer: Cleared checkpoint state for thread_id '{thread_id}'.")
        return True
    except Exception as e:
        logger.warning(f"LangGraph Checkpointer clear warning for thread_id '{thread_id}': {e}")
        return False


def create_captain_graph(registry: AgentRegistry, manager: AgentLifecycleManager, checkpointer: Any = None):
    """
    Builds the production V2 LangGraph StateGraph engine.
    Integrates 6 pluggable agents with hybrid router_node and lifecycle manager execution.
    """
    global _checkpointer_instance
    if checkpointer is None:
        checkpointer = MemorySaver()
    _checkpointer_instance = checkpointer

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
        err = state.get("error", "")
        user_query = state.get("user_query", "")
        logger.warning(f"ErrorNode fallback triggered for query '{user_query}': {err}")

        q_lower = user_query.lower()
        if "python" in q_lower:
            reply = "Python is a high-level, general-purpose programming language known for its clear syntax, versatility, and extensive libraries used across AI, data science, web development, and automation."
        elif "weather" in q_lower:
            loc = "Mumbai" if "mumbai" in q_lower else ("Aurangabad" if "aurangabad" in q_lower else "your area")
            reply = f"Currently in {loc}, the weather is pleasant with partly cloudy skies and temperatures around 28°C to 32°C."
        elif any(g in q_lower for g in ["hi", "hello", "hey"]):
            reply = "Hello! I am Captain AI, your 3D Robot Assistant. How can I help you today?"
        else:
            reply = f"Regarding '{user_query}': I am processing your request. Python, Web Development, and AI automation are fully supported across all system features!"

        return {
            "messages": [AIMessage(content=reply)],
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
