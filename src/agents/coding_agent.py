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
        if not user_query and history:
            last_msg = history[-1]
            if isinstance(last_msg, dict):
                user_query = last_msg.get("content", "")
            elif hasattr(last_msg, "content"):
                user_query = last_msg.content
            else:
                user_query = str(last_msg)

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

        coder_model = getattr(settings, "CHAT_MODEL", "llama3.2:latest")
        llm = model_manager.get_model(model_name=coder_model, temperature=0.1, max_tokens=512)

        system_prompt = (
            "You are Captain Coder, an expert software engineering agent.\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. DO NOT output internal reasoning or <think> tags.\n"
            "2. Always return your solution IMMEDIATELY as runnable code inside a markdown code block (e.g. ```python ... ```).\n"
            "3. Provide clean, concise, runnable code."
        )

        messages = [SystemMessage(content=system_prompt)]
        if github_context:
            messages.append(SystemMessage(content=f"GitHub Integration Context:\n{github_context}"))
        
        # Pass active user_query with clean prompt context to ensure precise code generation
        messages.append(HumanMessage(content=f"Task: Write code for the following request.\n\nUser Request: {user_query}"))

        try:
            text_chunks = []
            try:
                async for chunk in llm.astream(messages):
                    await self.check_pause()
                    chunk_str = chunk.content if hasattr(chunk, "content") else str(chunk)
                    text_chunks.append(chunk_str)
            except Exception as stream_err:
                logger.error(f"CodingAgent: Model stream failed with error: {type(stream_err).__name__}: {stream_err}")
                logger.exception("CodingAgent Exception Traceback:")
                fallback_llm = model_manager.get_model(model_name=settings.CHAT_MODEL, temperature=0.2, max_tokens=1024)
                text_chunks = []
                async for chunk in fallback_llm.astream(messages):
                    await self.check_pause()
                    chunk_str = chunk.content if hasattr(chunk, "content") else str(chunk)
                    text_chunks.append(chunk_str)

            code_out = "".join(text_chunks)
            clean_text = clean_think_tags(code_out)
            if not clean_text or len(clean_text) < 5:
                clean_text = code_out.replace("<think>", "").replace("</think>", "").strip()

            scratchpad["coder_output"] = clean_text
            return {
                "messages": [AIMessage(content=clean_text)],
                "scratchpad": scratchpad,
                "current_agent": self.metadata.name,
                "next_agent": "END"
            }

        except Exception as e:
            logger.warning(f"CodingAgent execution error ({e})")
            error_reply = f"⚠️ CodingAgent Error: Failed to generate code block via model '{settings.CODER_MODEL}'. Error: {e}"
            return {
                "messages": [AIMessage(content=error_reply)],
                "scratchpad": scratchpad,
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }
