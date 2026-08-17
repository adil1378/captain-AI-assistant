from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Self-Contained LangGraph Shared Multi-Agent State Schema.
    Fully independent with zero dependency on legacy root packages.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    user_query: str
    current_agent: str
    next_agent: str
    task_plan: List[str]
    scratchpad: Dict[str, Any]
    error: Optional[str]


class InputState(TypedDict):
    """Input State Schema for API / UI entrypoints."""
    user_query: str
