"""
Captain AI OS 2.0 — Base LLM Provider.
Provides standard message formats, token chunking, and abstract LLM contract.
"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional, AsyncGenerator
from providers.base import LLMProvider, ProviderMetadata


class BaseLLM(LLMProvider):
    """Abstract Base Class for LLM Providers in Captain AI OS."""

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.5,
        max_tokens: int = 1024,
        **kwargs: Any
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.extra_kwargs = kwargs
        self._initialized = False

    @property
    @abstractmethod
    def metadata(self) -> ProviderMetadata:
        pass

    @abstractmethod
    def get_langchain_model(self) -> Any:
        """Return an underlying LangChain-compatible chat model for Graph/Agent integration."""
        pass
