from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from agents.state import AgentState
from core.llm_factory import get_llm
from tools.search import multi_search
from tools.web_scraper import scrape_webpage
from utils.text_utils import clean_think_tags
from loguru import logger


def scraper_agent_node(state: AgentState) -> Dict[str, Any]:
    """Web Search & Live Scraper Agent Node."""
    user_query = state.get("user_query", "")
    scratchpad = state.get("scratchpad", {})

    search_results = multi_search(user_query, max_results=3)

    scraped_data = []
    sources_summary = []

    for r in search_results:
        url = r.get("url")
        if url:
            sources_summary.append(url)
            content = scrape_webpage(url, max_chars=1000)
            scraped_data.append(f"Source ({url}):\n{content}")

    combined_context = "\n\n".join(scraped_data) if scraped_data else "No live web content retrieved."

    llm = get_llm(temperature=0.3, max_tokens=1500)

    system_prompt = (
        "You are Captain Web Scraper. Synthesize an answer based on the live web search results below.\n\n"
        f"WEB CONTEXT:\n{combined_context}"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query)
    ]

    try:
        response = llm.invoke(messages)
        raw_text = response.content if hasattr(response, 'content') else str(response)
        clean_text = clean_think_tags(raw_text)

        # Include sources in output text if available
        if sources_summary:
            sources_str = "\n\n**Sources:**\n" + "\n".join([f"- {url}" for url in sources_summary])
            clean_text = clean_text + sources_str

        scratchpad["web_sources"] = sources_summary
        return {
            "messages": [AIMessage(content=clean_text)],
            "scratchpad": scratchpad,
            "current_agent": "scraper_agent"
        }
    except Exception as e:
        logger.error(f"scraper_agent_node error: {e}")
        return {
            "messages": [AIMessage(content=f"[Web Search Error]: {e}")],
            "error": str(e),
            "current_agent": "scraper_agent"
        }
