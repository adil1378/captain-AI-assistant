from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from agents.state import AgentState
from core.llm_factory import get_llm
from tools.rag_tools import rag_search_tool
from utils.text_utils import clean_think_tags
from loguru import logger


def rag_agent_node(state: AgentState) -> Dict[str, Any]:
    """RAG & Document Knowledge Retrieval Agent Node."""
    user_query = state.get("user_query", "")
    scratchpad = state.get("scratchpad", {})

    context = rag_search_tool(user_query, k=3)
    llm = get_llm(temperature=0.3, max_tokens=1500)

    system_prompt = (
        "You are Captain RAG, a specialized document intelligence agent. "
        "Answer questions based on the retrieved document context below.\n\n"
        f"CONTEXT:\n{context}"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query)
    ]

    try:
        response = llm.invoke(messages)
        raw_text = response.content if hasattr(response, 'content') else str(response)
        clean_text = clean_think_tags(raw_text)

        scratchpad["rag_context"] = context
        return {
            "messages": [AIMessage(content=clean_text)],
            "scratchpad": scratchpad,
            "current_agent": "rag_agent"
        }
    except Exception as e:
        logger.error(f"rag_agent_node error: {e}")
        return {
            "messages": [AIMessage(content=f"[RAG Knowledge Error]: {e}")],
            "error": str(e),
            "current_agent": "rag_agent"
        }
