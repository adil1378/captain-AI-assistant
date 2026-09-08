"""
Captain AI OS 2.0 — Local Ollama LLM Provider.
Preserves and unifies existing high-performance Ollama connectivity with IPv4 retry,
health monitoring, streaming token delivery, and LangChain model compatibility.
"""

import asyncio
from typing import Any, AsyncGenerator, Dict, List, Optional
from loguru import logger

try:
    from langchain_ollama import ChatOllama
except ImportError:
    from langchain_community.chat_models.ollama import ChatOllama

from langchain_core.messages import BaseMessage, AIMessage
from providers.base import ProviderMetadata
from providers.llm.base import BaseLLM


class OllamaLLM(BaseLLM):
    """
    Local Ollama LLM Provider.
    Runs completely offline against local Ollama instance with automated IPv4 resolution.
    """

    def __init__(
        self,
        model_name: str = "llama3.2",
        base_url: str = "http://127.0.0.1:11434",
        temperature: float = 0.5,
        max_tokens: int = 1024,
        timeout: float = 30.0,
        keep_alive: str = "5m",
        **kwargs: Any
    ):
        super().__init__(model_name=model_name, temperature=temperature, max_tokens=max_tokens, **kwargs)
        # Normalize localhost to 127.0.0.1 to avoid Windows IPv6 dual-stack resolution delays
        self.base_url = (base_url or "http://127.0.0.1:11434").replace("localhost", "127.0.0.1")
        self.timeout = timeout
        self.keep_alive = keep_alive
        self._model_instance: Optional[ChatOllama] = None

    @property
    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name="ollama",
            provider_type="llm",
            version="2.0.0",
            is_local=True,
            description=f"Local Ollama inference engine ({self.model_name}) at {self.base_url}"
        )

    def _create_instance(self) -> ChatOllama:
        """Instantiate a ChatOllama model client."""
        return ChatOllama(
            model=self.model_name,
            base_url=self.base_url,
            temperature=self.temperature,
            num_predict=self.max_tokens,
            keep_alive=self.keep_alive,
        )

    async def initialize(self) -> bool:
        """Initialize the model client and verify reachability."""
        try:
            self._model_instance = self._create_instance()
            self._initialized = await self.health_check()
            return self._initialized
        except Exception as e:
            logger.warning(f"OllamaLLM: Initialization warning ({e}). Fallback client created.")
            self._model_instance = self._create_instance()
            self._initialized = False
            return False

    async def health_check(self) -> bool:
        """Verify that the Ollama server is responding."""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            # Fallback check using urllib if httpx is unavailable
            try:
                import urllib.request
                with urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=2.0) as response:
                    return response.status == 200
            except Exception:
                return False

    async def shutdown(self) -> None:
        """Shutdown provider and release client references."""
        self._model_instance = None
        self._initialized = False

    def get_langchain_model(self) -> ChatOllama:
        """Return the LangChain model for graph/agent execution."""
        if not self._model_instance:
            self._model_instance = self._create_instance()
        return self._model_instance

    async def ainvoke(self, prompt_or_messages: Any, **kwargs: Any) -> Any:
        """Execute async inference with automatic IPv4 retry."""
        llm = self.get_langchain_model()
        try:
            return await llm.ainvoke(prompt_or_messages, **kwargs)
        except Exception as e:
            logger.warning(f"OllamaLLM: Primary invocation failed ({e}). Retrying on explicit 127.0.0.1...")
            retry_base = self.base_url.replace("localhost", "127.0.0.1")
            retry_llm = ChatOllama(
                model=self.model_name,
                base_url=retry_base,
                temperature=self.temperature,
                num_predict=self.max_tokens,
            )
            try:
                return await retry_llm.ainvoke(prompt_or_messages, **kwargs)
            except Exception as e2:
                logger.error(f"OllamaLLM: Retry invocation failed ({e2}). Returning service error message.")
                return AIMessage(content=f"⚠️ Local Ollama service at {self.base_url} is currently unreachable.")

    async def astream(self, prompt_or_messages: Any, **kwargs: Any) -> AsyncGenerator[Any, None]:
        """Stream chunks asynchronously with error recovery."""
        llm = self.get_langchain_model()
        try:
            async for chunk in llm.astream(prompt_or_messages, **kwargs):
                yield chunk
        except Exception as e:
            logger.warning(f"OllamaLLM: Primary stream failed ({e}). Retrying on explicit 127.0.0.1...")
            retry_base = self.base_url.replace("localhost", "127.0.0.1")
            retry_llm = ChatOllama(
                model=self.model_name,
                base_url=retry_base,
                temperature=self.temperature,
                num_predict=self.max_tokens,
            )
            try:
                async for chunk in retry_llm.astream(prompt_or_messages, **kwargs):
                    yield chunk
            except Exception as e2:
                logger.error(f"OllamaLLM: Stream failed after retry ({e2}).")
                yield AIMessage(content=f"⚠️ Local Ollama service at {self.base_url} is unreachable.")
