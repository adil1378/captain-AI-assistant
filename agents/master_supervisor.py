from typing import Dict, Any
from agents.state import AgentState
from loguru import logger


def master_supervisor_node(state: AgentState) -> Dict[str, Any]:
    """
    Master Supervisor Router Node.
    Analyzes intent via heuristics and routes to specialized agent nodes.
    """
    query = state.get("user_query", "").strip()
    q_lower = query.lower()

    logger.info(f"MasterSupervisor routing query: '{query}'")

    # 1. Comms Agent Routing (Email & WhatsApp)
    comms_keywords = ["email", "mail", "whatsapp", "message", "send to", "contact", "save contact", "add contact"]
    if any(k in q_lower for k in comms_keywords):
        return {"next_agent": "comms_agent", "current_agent": "supervisor"}

    # 2. Coder Agent Routing (Code generation & programming)
    coder_keywords = ["code", "python", "script", "function", "refactor", "bug", "write code", "html", "css", "class"]
    if any(k in q_lower for k in coder_keywords):
        return {"next_agent": "coder_agent", "current_agent": "supervisor"}

    # 3. System Agent Routing (Hardware metrics, system status, weather)
    system_keywords = ["cpu", "ram", "memory", "disk", "hardware", "battery", "system", "metrics", "weather", "temperature"]
    if any(k in q_lower for k in system_keywords):
        return {"next_agent": "system_agent", "current_agent": "supervisor"}

    # 4. Scraper Agent Routing (Live search, YouTube, Web pages)
    live_search_keywords = ["search", "google", "youtube", "video", "scrape", "url", "news", "latest", "find web"]
    if any(k in q_lower for k in live_search_keywords):
        return {"next_agent": "scraper_agent", "current_agent": "supervisor"}

    # 5. RAG Agent Routing (Document search, PDF, internal docs)
    rag_keywords = ["pdf", "document", "file", "ingest", "doc", "paper", "book", "search docs"]
    if any(k in q_lower for k in rag_keywords):
        return {"next_agent": "rag_agent", "current_agent": "supervisor"}

    # Default: General Chat Agent
    return {"next_agent": "chat_agent", "current_agent": "supervisor"}
