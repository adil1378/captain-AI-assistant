import re
from typing import Dict, Any, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.agents.state import AgentState
from src.agents.agent_registry import AgentRegistry
from src.agents.agent_lifecycle_manager import AgentLifecycleManager
from src.graph.router import classify_intent_hybrid, Intent, IntentResult
from src.tools.location_tool import get_location_info
from src.backend.core.model_manager import model_manager
from src.backend.config import settings
from utils.text_utils import clean_think_tags
from loguru import logger

# Deterministic mapping from Intent to StateGraph Node
INTENT_TO_NODE: Dict[Intent, str] = {
    Intent.GREETING: "chat_agent",
    Intent.GENERAL_QA: "chat_agent",
    Intent.LOCATION: "location_node",
    Intent.WEB_SEARCH: "search_agent",
    Intent.WEATHER: "system_agent",
    Intent.CODING: "coder_agent",
    Intent.RAG: "rag_agent",
    Intent.COMMS: "comms_agent",
}

_VALID_NODES = list(set(INTENT_TO_NODE.values()))

# Global Checkpointer singleton handle for clearing session state
_checkpointer_instance = None


async def router_node(state: AgentState) -> Dict[str, Any]:
    """
    Validated Intent Router Node.
    Returns structured IntentResult and deterministically maps to target node.
    """
    user_query = state.get("user_query", "").strip()
    messages = state.get("messages", [])

    intent_result: IntentResult = classify_intent_hybrid(user_query)
    next_node = INTENT_TO_NODE.get(intent_result.intent, "chat_agent")

    logger.info(
        f"RouterNode: Query '{user_query}' -> Intent: {intent_result.intent.value} "
        f"(confidence={intent_result.confidence:.2f}) -> Node: '{next_node}'"
    )

    scratchpad = state.get("scratchpad", {})
    scratchpad["intent_result"] = intent_result.model_dump()

    res: Dict[str, Any] = {
        "user_query": user_query,
        "next_agent": next_node,
        "scratchpad": scratchpad
    }

    # Propagate HumanMessage cleanly
    if user_query:
        if not messages or not (isinstance(messages[-1], HumanMessage) and messages[-1].content == user_query):
            res["messages"] = [HumanMessage(content=user_query)]

    return res


async def location_node(state: AgentState) -> Dict[str, Any]:
    """
    Standalone Location Node executing LocationTool geocoding.
    Extracts location query and returns structured coordinates & interactive map URL.
    """
    user_query = state.get("user_query", "").strip()
    scratchpad = state.get("scratchpad", {})
    logger.info(f"LocationNode: Executing LocationTool for query '{user_query}'")

    # Extract location name (e.g., "where is Aurangabad" -> "Aurangabad")
    q_clean = user_query
    for trigger in ["where is", "location of", "show on map", "coordinates of", "map of", "where located", "where in the world is"]:
        if trigger in q_clean.lower():
            pattern = re.compile(re.escape(trigger), re.IGNORECASE)
            q_clean = pattern.sub("", q_clean).strip(" ?!.")
            break

    loc_res = await get_location_info(q_clean or user_query)
    scratchpad["location_result"] = loc_res

    if loc_res.get("status") == "success":
        reply = (
            f"📍 **Geographic Location Information for {loc_res['display_name']}**\n\n"
            f"- **Coordinates:** Latitude `{loc_res['latitude']}`, Longitude `{loc_res['longitude']}`\n"
            f"- **Type:** `{loc_res['type'].capitalize()}`\n\n"
            f"🗺️ [View on Interactive OpenStreetMap]({loc_res['map_url']})"
        )
    else:
        err_msg = loc_res.get("error", "Location lookup failed.")
        reply = f"❌ Location lookup for '{user_query}' was unsuccessful: {err_msg}"

    return {
        "messages": [AIMessage(content=reply)],
        "scratchpad": scratchpad,
        "current_agent": "location_node",
        "next_agent": "END"
    }


def create_captain_graph(registry: AgentRegistry, manager: AgentLifecycleManager, checkpointer: Any = None):
    """
    Builds the production V2 LangGraph StateGraph engine.
    Integrates agents & location_node with validated IntentResult router.
    """
    global _checkpointer_instance
    if checkpointer is None:
        checkpointer = MemorySaver()
    _checkpointer_instance = checkpointer

    builder = StateGraph(AgentState)

    # 1. Add Router Node & Location Node
    builder.add_node("router_node", router_node)
    builder.add_node("location_node", location_node)

    # 2. Wrap Agent Nodes
    def make_agent_node(agent_name: str):
        async def agent_node_fn(state: AgentState) -> Dict[str, Any]:
            logger.info(f"LangGraph Node: invoking manager.execute_agent('{agent_name}')")
            res = await manager.execute_agent(agent_name, state)
            return res
        return agent_node_fn

    for agent_name in ["chat_agent", "coder_agent", "system_agent", "rag_agent", "search_agent", "comms_agent"]:
        builder.add_node(agent_name, make_agent_node(agent_name))

    # 3. Add Error Recovery Node (No hardcoded fake answers!)
    async def error_node_fn(state: AgentState) -> Dict[str, Any]:
        err = state.get("error", "Unknown service disruption")
        user_query = state.get("user_query", "")
        logger.warning(f"ErrorNode fallback triggered for query '{user_query}': {err}")

        reply = f"⚠️ Captain AI OS encountered a service error while processing '{user_query}': {err}"

        return {
            "messages": [AIMessage(content=reply)],
            "next_agent": "END"
        }
    builder.add_node("error_node", error_node_fn)

    # 4. Connect Edges
    builder.add_edge(START, "router_node")

    # Conditional Routing from router_node using valid node dictionary
    builder.add_conditional_edges(
        "router_node",
        lambda s: s.get("next_agent", "chat_agent"),
        {node: node for node in _VALID_NODES}
    )

    # Output conditional edges from execution nodes
    def route_execution_output(state: AgentState) -> str:
        if state.get("error"):
            return "error_node"
        next_a = state.get("next_agent", "END")
        return next_a if next_a in _VALID_NODES else END

    for node_name in _VALID_NODES:
        builder.add_conditional_edges(
            node_name,
            route_execution_output,
            {**{n: n for n in _VALID_NODES}, "error_node": "error_node", END: END}
        )

    builder.add_edge("error_node", END)

    compiled_graph = builder.compile(checkpointer=checkpointer)
    logger.info("Captain AI OS V2 LangGraph StateGraph engine compiled successfully with IntentResult routing.")
    return compiled_graph
