import re
from pathlib import Path
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from src.agents.state import AgentState
from src.agents.base_agent import BaseAgent, AgentMetadata
from src.backend.core.model_manager import model_manager
from src.backend.config import settings
from tools.search import search_web
from tools.web_scraper import scrape_webpage
from tools.image_gen import generate_image
from utils.text_utils import clean_think_tags
from loguru import logger


class SearchAgent(BaseAgent):
    """
    Production V2 Web Search, Web Scraper & AI Image Generation Agent.
    Handles web search, URL scraping, and AI image generation with in-chat rendering & download.
    """

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="search_agent",
            description="Web Search, Web Scraping and AI Image Generation Agent",
            version="2.0.0",
            capabilities=["web_search", "web_scraping", "image_generation", "online_lookup"]
        )

    def _format_results(self, results: list) -> str:
        """Format search result list into a readable context block."""
        if not results:
            return "[No results returned from search engine]"
        lines = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "No Title")
            snippet = r.get("snippet", "")
            url = r.get("url", "")
            lines.append(f"[Result {i}] {title}\n{snippet}\nURL: {url}")
        return "\n\n".join(lines)

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        user_query = state.get("user_query", "").strip()
        history = state.get("messages", [])
        scratchpad = state.get("scratchpad", {})
        query_lower = user_query.lower()

        # 1. Handle Image Generation Requests
        image_keywords = ["image", "picture", "draw", "photo", "illustration", "painting", "artwork"]
        action_keywords = ["generate", "genrate", "create", "make", "show", "draw", "render"]
        
        is_image_req = (
            any(k in query_lower for k in ["generate image", "genrate image", "create image", "draw", "make image", "picture of", "image of", "photo of"]) or
            (any(a in query_lower for a in action_keywords) and any(i in query_lower for i in image_keywords))
        )

        if is_image_req:
            logger.info(f"SearchAgent: Routing to image generation for '{user_query}'")
            res = generate_image(user_query)
            if res.get("status") == "success":
                img_path = res.get("image_path")
                filename = Path(img_path).name
                web_url = f"/outputs/{filename}"
                msg_text = (
                    f"🎨 **Image Generated Successfully!**\n\n"
                    f"![{user_query}]({web_url})\n\n"
                    f"<a href=\"{web_url}\" download=\"{filename}\" class=\"download-img-btn\" target=\"_blank\">"
                    f"<i class=\"fa-solid fa-download\"></i> Download Image ({filename})</a>"
                )
            else:
                msg_text = f"❌ Image generation failed: {res.get('error', 'Unknown error')}"

            scratchpad["image_gen_output"] = res
            return {
                "messages": [AIMessage(content=msg_text)],
                "scratchpad": scratchpad,
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }

        # 2. Handle Direct URL Web Scraping Requests
        url_match = re.search(r'https?://[^\s]+', user_query)
        if url_match or "scrape" in query_lower:
            target_url = url_match.group(0) if url_match else user_query
            logger.info(f"SearchAgent: Scraping webpage URL '{target_url}'")
            scrape_res = scrape_webpage(target_url)
            if scrape_res.get("status") == "success":
                title = scrape_res.get("title", "")
                text_content = scrape_res.get("text", "")[:1500]
                msg_text = f"🌐 **Webpage Scraped Successfully**\n\n**Title**: {title}\n\n**Content Summary**:\n{text_content}"
            else:
                msg_text = f"❌ Web scraping failed: {scrape_res.get('error', 'Unknown error')}"

            scratchpad["scrape_output"] = scrape_res
            return {
                "messages": [AIMessage(content=msg_text)],
                "scratchpad": scratchpad,
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }

        # 3. Handle Standard Web Search
        search_result = search_web(user_query, max_results=5)
        context_text = ""

        if search_result.get("status") == "success":
            results = search_result.get("results", [])
            engine = search_result.get("engine", "unknown")
            context_text = self._format_results(results)
            logger.info(f"SearchAgent: Got {len(results)} results from '{engine}' for '{user_query}'")
        else:
            error = search_result.get("error", "Search failed.")
            logger.warning(f"SearchAgent: Search failed — {error}")
            context_text = f"[Search error: {error}]"

        system_prompt = (
            "You are Captain Search, an expert research agent. "
            "Using the web search results provided below as your primary source, "
            "synthesize a clear, accurate, and well-structured answer to the user's query. "
            "Cite specific results where relevant."
        )

        messages_to_send = [
            SystemMessage(content=system_prompt),
            SystemMessage(content=f"Web Search Results:\n\n{context_text}"),
        ] + history[-4:]
        if not any(isinstance(m, HumanMessage) for m in history[-4:]):
            messages_to_send.append(HumanMessage(content=user_query))

        llm = model_manager.get_model(
            model_name=settings.CHAT_MODEL,
            temperature=0.3,
            max_tokens=512
        )

        try:
            response_msg = await llm.ainvoke(messages_to_send)
            raw_text = response_msg.content if hasattr(response_msg, "content") else str(response_msg)
            clean_text = clean_think_tags(raw_text)

            if not clean_text or len(clean_text) < 3:
                clean_text = context_text or "No search results were available for your query."

            scratchpad["search_results"] = context_text
            scratchpad["search_output"] = clean_text

            return {
                "messages": [AIMessage(content=clean_text)],
                "scratchpad": scratchpad,
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }

        except Exception as e:
            logger.error(f"SearchAgent LLM error: {e}")
            fallback = context_text if context_text else f"Search agent encountered an error: {e}"
            return {
                "messages": [AIMessage(content=fallback)],
                "error": str(e),
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }
