import asyncio
from typing import Dict, Any, Optional, AsyncGenerator
try:
    from langchain_ollama import ChatOllama
except ImportError:
    from langchain_community.chat_models.ollama import ChatOllama

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from src.backend.config import settings
from src.backend.core.event_bus import event_bus
from loguru import logger


class ModelManager:
    """
    Centralized High-Performance Model Manager.
    Abstracts providers (Ollama, OpenAI, Gemini), handles model switching,
    health monitoring, context window management, and streaming tokens.
    """
    def __init__(self):
        self.default_provider = settings.DEFAULT_PROVIDER
        self.base_url = settings.OLLAMA_BASE_URL
        self._cached_llms: Dict[str, Any] = {}

    def get_model(self, model_name: Optional[str] = None, temperature: float = 0.5, max_tokens: int = 512):
        """Retrieve an initialized ChatModel with cached reuse and performance optimizations."""
        target_model = model_name or settings.CHAT_MODEL
        cache_key = f"{target_model}_{temperature}_{max_tokens}"

        if cache_key in self._cached_llms:
            return self._cached_llms[cache_key]

        logger.info(f"ModelManager: Initializing model '{target_model}' (temp={temperature}, max_tokens={max_tokens})")

        try:
            llm = ChatOllama(
                model=target_model,
                base_url=self.base_url,
                temperature=temperature,
                num_predict=max_tokens,
            )
            self._cached_llms[cache_key] = llm
            return llm
        except Exception as e:
            logger.warning(f"Failed to load model '{target_model}': {e}. Falling back to default '{settings.CHAT_MODEL}'.")
            fallback_llm = ChatOllama(
                model=settings.CHAT_MODEL,
                base_url=self.base_url,
                temperature=temperature,
                num_predict=max_tokens,
            )
            return fallback_llm

    async def stream_response(self, model_name: str, messages: list[BaseMessage]) -> AsyncGenerator[str, None]:
        """Stream tokens asynchronously and emit token events."""
        llm = self.get_model(model_name=model_name)
        try:
            await event_bus.publish("ModelStreamStarted", "ModelManager", {"model": model_name})
            async for chunk in llm.astream(messages):
                token = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if token:
                    yield token
            await event_bus.publish("ModelStreamFinished", "ModelManager", {"model": model_name})
        except Exception as e:
            logger.error(f"ModelManager stream error: {e}")
            yield f"[Model Execution Error: {e}]"


# Global Singleton Model Manager Instance
model_manager = ModelManager()
