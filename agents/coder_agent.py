from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from agents.state import AgentState
from core.llm_factory import get_llm
from utils.text_utils import clean_think_tags
from loguru import logger


def coder_agent_node(state: AgentState) -> Dict[str, Any]:
    """Code Generation & Refactoring Agent Node with History Support."""
    user_query = state.get("user_query", "")
    scratchpad = state.get("scratchpad", {})
    history = state.get("messages", [])

    llm = get_llm(temperature=0.2, max_tokens=2048)

    system_prompt = (
        "You are Captain Coder, an expert software engineering agent. "
        "Write clean, production-grade, well-commented code blocks."
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

        scratchpad["coder_output"] = clean_text
        return {
            "messages": [AIMessage(content=clean_text)],
            "scratchpad": scratchpad,
            "current_agent": "coder_agent"
        }
    except Exception as e:
        logger.error(f"coder_agent_node error: {e}")
        return {
            "messages": [AIMessage(content=f"[Coding Error]: {e}")],
            "error": str(e),
            "current_agent": "coder_agent"
        }
