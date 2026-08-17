from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from src.agents.state import AgentState
from src.agents.base_agent import BaseAgent, AgentMetadata
from src.backend.core.model_manager import model_manager
from src.backend.config import settings
from utils.text_utils import clean_think_tags
from tools.github_tools import get_authenticated_user, list_user_repos, create_github_repo
from loguru import logger


class CodingAgent(BaseAgent):
    """Production Pluggable Code Generation & Scripting Agent with Streaming, Pause & GitHub Integration."""

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="coder_agent",
            description="Code Generation, Scripting, GitHub CI/CD & Refactoring Agent",
            version="2.0.0",
            capabilities=["code_generation", "scripting", "refactoring", "github_integration", "ci_cd"]
        )

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        user_query = state.get("user_query", "")
        history = state.get("messages", [])
        scratchpad = state.get("scratchpad", {})
        query_lower = user_query.lower()

        github_context = ""
        # Check if query is about GitHub repositories or CI/CD
        if any(k in query_lower for k in ["github", "repo", "repository", "git commit", "ci/cd", "workflow", "action"]):
            user_info = get_authenticated_user()
            if user_info.get("status") == "success":
                github_context = f"GITHUB AUTHENTICATED USER: @{user_info.get('username')} ({user_info.get('html_url')})"
            else:
                github_context = f"GITHUB STATUS: {user_info.get('error', 'Token not configured')}"
            logger.info("CodingAgent: Prepared GitHub integration context.")

        llm = model_manager.get_model(model_name=settings.CODER_MODEL, temperature=0.2, max_tokens=2048)

        system_prompt = (
            "You are Captain Coder, an expert software engineering agent with full GitHub & CI/CD workflow capabilities. "
            "Write production-quality, clean, well-commented code. "
            "Return complete code blocks with language identifiers. "
            "When helping with GitHub repositories, workflows, or CI/CD pipelines, provide exact instructions or scripts."
        )

        messages = [SystemMessage(content=system_prompt)]
        if github_context:
            messages.append(SystemMessage(content=f"GitHub Integration Context:\n{github_context}"))
        messages.extend(history)

        if not any(isinstance(m, HumanMessage) for m in history):
            messages.append(HumanMessage(content=user_query))

        try:
            text_chunks = []
            try:
                async for chunk in llm.astream(messages):
                    await self.check_pause()
                    chunk_str = chunk.content if hasattr(chunk, "content") else str(chunk)
                    text_chunks.append(chunk_str)
            except Exception as stream_err:
                logger.warning(f"CodingAgent: Model stream failed ({stream_err}), retrying with fallback model '{settings.CHAT_MODEL}'")
                fallback_llm = model_manager.get_model(model_name=settings.CHAT_MODEL, temperature=0.2, max_tokens=2048)
                text_chunks = []
                async for chunk in fallback_llm.astream(messages):
                    await self.check_pause()
                    chunk_str = chunk.content if hasattr(chunk, "content") else str(chunk)
                    text_chunks.append(chunk_str)

            code_out = "".join(text_chunks)
            clean_text = clean_think_tags(code_out)

            scratchpad["coder_output"] = clean_text
            return {
                "messages": [AIMessage(content=clean_text)],
                "scratchpad": scratchpad,
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }

        except Exception as e:
            logger.error(f"CodingAgent error: {e}")
            return {
                "messages": [AIMessage(content=f"[Coding Error]: {e}")],
                "error": str(e),
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }
