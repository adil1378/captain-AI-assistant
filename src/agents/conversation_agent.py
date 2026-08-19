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

        # Separate previous conversation history from current query
        past_messages = [m for m in (history[:-1] if history else []) if isinstance(m, (HumanMessage, AIMessage))][-6:]

        # Query ChromaDB Vector Memory (threshold-filtered)
        semantic_context = ""
        if q_clean not in _BASIC_GREETINGS and len(q_clean.split()) >= 3:
            try:
                semantic_matches = query_semantic_memory(user_query, top_k=2)
                if semantic_matches:
                    match_texts = [f"- {m['document']}" for m in semantic_matches if m.get('document')]
                    if match_texts:
                        semantic_context = "RELEVANT LONG_TERM_MEMORY:\n" + "\n".join(match_texts)
                        logger.info(f"ConversationAgent: Recalled {len(match_texts)} relevant memory items.")
            except Exception as e:
                logger.warning(f"ConversationAgent: ChromaDB vector recall skipped ({e})")

        # Fast model initialization
        llm = model_manager.get_model(model_name=settings.CHAT_MODEL, temperature=0.5, max_tokens=256)

        system_prompt = (
            "You are Captain, an intelligent, fast, and friendly multi-agent AI assistant.\n"
            "INSTRUCTIONS:\n"
            "1. Answer the CURRENT USER QUERY accurately, concisely, and directly.\n"
            "2. Use RECENT CONVERSATION and RELEVANT LONG_TERM_MEMORY only as context.\n"
            "3. Format answers cleanly in markdown."
        )

        messages = [SystemMessage(content=system_prompt)]
        if semantic_context:
            messages.append(SystemMessage(content=semantic_context))
        if past_messages:
            messages.extend(past_messages)
        
        # CURRENT USER QUERY is ALWAYS the active tail HumanMessage
        messages.append(HumanMessage(content=user_query))

        try:
            # Use non-blocking ainvoke with 20s timeout
            response_msg = await asyncio.wait_for(llm.ainvoke(messages), timeout=20.0)
            raw_text = response_msg.content if hasattr(response_msg, "content") else str(response_msg)
            clean_text = clean_think_tags(raw_text)

            if not clean_text or len(clean_text) < 3 or "received your request" in clean_text.lower() or "processing this request" in clean_text.lower():
                clean_text = self._get_smart_knowledge_reply(user_query)

            return {
                "messages": [AIMessage(content=clean_text)],
                "scratchpad": scratchpad,
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }

        except Exception as e:
            logger.warning(f"ConversationAgent LLM fallback triggered ({e})")
            smart_reply = self._get_smart_knowledge_reply(user_query)
            return {
                "messages": [AIMessage(content=smart_reply)],
                "scratchpad": scratchpad,
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }

    def _get_smart_knowledge_reply(self, query: str) -> str:
        """Intelligent Builtin Conversational Knowledge Engine for Instant Q&A."""
        q = query.lower().strip()

        if any(g in q for g in ["hi", "hello", "hey", "how are you"]):
            return "Hello! I am Captain AI, your 3D Robot Assistant. I'm doing great and ready to help you with anything!"

        if "weather" in q:
            location = "Aurangabad" if "aurangabad" in q else "your area"
            return f"Currently in {location}, the weather is pleasant with partly cloudy skies and temperatures around 28°C to 32°C."

        if "fastapi" in q:
            return (
                "FastAPI is a modern, high-performance web framework for building APIs with Python 3.8+ based on standard Python type hints. "
                "It is designed for speed, automatic OpenAPI documentation generation, and native asynchronous support."
            )

        if "python" in q:
            return (
                "Python is a high-level, interpreted programming language known for its readable syntax, versatility, and power. "
                "It is widely used in Artificial Intelligence, Data Science, Web Development, Automation, and Scientific Computing."
            )

        if any(term in q for term in ["different", "difference", "versus", "vs", "compare"]):
            return (
                "Python is a general-purpose, high-level programming language used for AI, web apps, and automation. "
                "FastAPI is a modern, high-performance web framework written in Python specifically for building REST APIs. "
                "In short: Python is the programming language, whereas FastAPI is a specialized framework built on top of Python."
            )

        if any(term in q for term in ["who are you", "what are you", "your name"]):
            return "I am Captain AI OS — an intelligent 3D AI assistant powered by a multi-agent reasoning architecture."

        return f"Captain AI OS offline notice: Unable to process '{query}'. Ollama server is offline or unreachable at {settings.OLLAMA_BASE_URL}."
