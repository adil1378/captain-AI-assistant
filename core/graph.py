from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.master_supervisor import master_supervisor_node
from agents.chat_agent import chat_agent_node
from agents.coder_agent import coder_agent_node
from agents.rag_agent import rag_agent_node
from agents.comms_agent import comms_agent_node
from agents.scraper_agent import scraper_agent_node
from agents.system_agent import system_agent_node
from langgraph.checkpoint.memory import MemorySaver


def route_supervisor(state: AgentState) -> str:
    """Conditional edge routing for LangGraph Master Supervisor."""
    next_agent = state.get("next_agent", "FINISH")
    current_agent = state.get("current_agent", "")

    # If supervisor signals finish or sub-agent has set current_agent, end execution
    if next_agent in ["FINISH", "finish", "END", "end"] or (current_agent and next_agent == "supervisor"):
        return END

    valid_agents = ["chat_agent", "coder_agent", "rag_agent", "comms_agent", "scraper_agent", "system_agent"]
    if next_agent in valid_agents:
        return next_agent

    return END


def create_captain_graph():
    """Build and compile the Captain AI Multi-Agent StateGraph."""
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("supervisor", master_supervisor_node)
    workflow.add_node("chat_agent", chat_agent_node)
    workflow.add_node("coder_agent", coder_agent_node)
    workflow.add_node("rag_agent", rag_agent_node)
    workflow.add_node("comms_agent", comms_agent_node)
    workflow.add_node("scraper_agent", scraper_agent_node)
    workflow.add_node("system_agent", system_agent_node)

    # Set Entry Point
    workflow.set_entry_point("supervisor")

    # Add Conditional Routing Edges from Supervisor
    workflow.add_conditional_edges("supervisor", route_supervisor)

    # Connect all sub-agent nodes to END directly to prevent infinite re-routing loops
    workflow.add_edge("chat_agent", END)
    workflow.add_edge("coder_agent", END)
    workflow.add_edge("rag_agent", END)
    workflow.add_edge("comms_agent", END)
    workflow.add_edge("scraper_agent", END)
    workflow.add_edge("system_agent", END)

    # Compile with Memory Checkpointer
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app
