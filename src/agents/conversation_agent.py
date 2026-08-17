import asyncio
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from src.agents.state import AgentState
from src.agents.base_agent import BaseAgent, AgentMetadata
from src.backend.core.model_manager import model_manager
from src.backend.config import settings
from utils.text_utils import clean_think_tags
from memory.vector_memory import query_semantic_memory
from loguru import logger

_BASIC_GREETINGS = {"hi", "hello", "hey", "how are you", "how r u", "hola", "sup"}


class ConversationAgent(BaseAgent):
    """Production High-Speed Conversation Agent with Truncated Active Context Window & Fast Execution Timeout."""

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="chat_agent",
            description="General Q&A and Conversational Reasoning Agent",
            version="2.0.0",
            capabilities=["conversation", "general_qa", "reasoning"]
        )

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        user_query = state.get("user_query", "").strip()
        history = state.get("messages", [])
        scratchpad = state.get("scratchpad", {})
        q_clean = user_query.lower().strip("?!.,")

        # Keep active conversation prompt context lightweight (last 4 messages max) for fast CPU speed
        recent_history = history[-4:] if history else []

        # Query ChromaDB Vector Memory only for substantial non-greeting queries
        semantic_context = ""
        if q_clean not in _BASIC_GREETINGS and len(q_clean.split()) >= 4:
            try:
                semantic_matches = query_semantic_memory(user_query, top_k=2)
                if semantic_matches:
                    match_texts = [f"- {m['document']}" for m in semantic_matches if m.get('document')]
                    if match_texts:
                        semantic_context = "BACKGROUND CONTEXT:\n" + "\n".join(match_texts)
                        logger.info(f"ConversationAgent: Recalled {len(match_texts)} memory items.")
            except Exception as e:
                logger.warning(f"ConversationAgent: ChromaDB vector recall skipped ({e})")

        # Fast model initialization (256 max tokens for ultra-fast generation)
        llm = model_manager.get_model(model_name=settings.CHAT_MODEL, temperature=0.5, max_tokens=256)

        system_prompt = (
            "You are Captain, a fast, smart, and friendly multi-agent AI assistant.\n"
            "INSTRUCTIONS:\n"
            "1. Give concise, direct, helpful answers formatted cleanly in markdown.\n"
            "2. Respond warmly and naturally to greetings.\n"
            "3. Use any BACKGROUND CONTEXT quietly without explicitly reciting past conversations."
        )

        messages = [SystemMessage(content=system_prompt)]
        if semantic_context:
            messages.append(SystemMessage(content=semantic_context))
        messages.extend(recent_history)

        if not any(isinstance(m, HumanMessage) for m in recent_history):
            messages.append(HumanMessage(content=user_query))

        try:
            # Use non-blocking ainvoke with 25s timeout to allow model cold-start
            response_msg = await asyncio.wait_for(llm.ainvoke(messages), timeout=25.0)
            raw_text = response_msg.content if hasattr(response_msg, "content") else str(response_msg)
            clean_text = clean_think_tags(raw_text)

            if not clean_text or len(clean_text) < 3:
                clean_text = "I am Captain, your AI assistant. How can I help you today?"

            return {
                "messages": [AIMessage(content=clean_text)],
                "scratchpad": scratchpad,
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }

        except Exception as e:
            logger.error(f"ConversationAgent error / timeout: {e}")
            fallback_text = f"Hello! I am Captain AI OS. I received your request: '{user_query}'. How can I assist you?"
            return {
                "messages": [AIMessage(content=fallback_text)],
                "scratchpad": scratchpad,
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }
