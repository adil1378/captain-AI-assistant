from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from agents.state import AgentState
from core.llm_factory import get_llm
from utils.text_utils import clean_think_tags
from loguru import logger


def chat_agent_node(state: AgentState) -> Dict[str, Any]:
    """Conversational Chat Agent Node with History Support."""
    user_query = state.get("user_query", "")
    scratchpad = state.get("scratchpad", {})
    history = state.get("messages", [])

    llm = get_llm(temperature=0.5, max_tokens=2048)

    system_prompt = (
        "You are Captain, an elite AI assistant. "
        "Formulate professional, helpful, accurate responses in clean markdown format."
    )

    if history:
        messages = [SystemMessage(content=system_prompt)] + list(history)
    else:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_query)
        ]

    try:
        response = llm.invoke(messages)
        raw_text = response.content if hasattr(response, 'content') else str(response)
        clean_text = clean_think_tags(raw_text)

        if not clean_text or len(clean_text) < 3:
            clean_text = "I am Captain, your professional multi-agent assistant. How may I assist you today?"

        return {
            "messages": [AIMessage(content=clean_text)],
            "scratchpad": scratchpad,
            "current_agent": "chat_agent"
        }
    except Exception as e:
        logger.error(f"chat_agent_node error: {e}")
        return {
            "messages": [AIMessage(content="I am Captain. How may I assist you today?")],
            "error": str(e),
            "current_agent": "chat_agent"
        }
