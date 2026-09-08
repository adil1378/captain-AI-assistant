"""
Captain AI OS 2.0 — LLM Provider Factory.
Migrates and unifies logic from core/llm_factory.py with multi-provider support:
- Local Ollama (default offline engine)
- OpenAI (GPT models)
- Google Gemini
"""

from typing import Optional, Any
from loguru import logger
from langchain_core.language_models import BaseChatModel

from providers.llm.base import BaseLLM
from providers.llm.ollama import OllamaLLM


def get_llm_provider(
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: float = 0.5,
    max_tokens: int = 1024,
    **kwargs: Any
) -> BaseLLM:
    """
    Return a Captain AI OS 2.0 BaseLLM provider instance.
    """
    # Defer settings import to avoid circular imports during config bootstrapping
    from config import settings

    target_provider = (provider or settings.llm_provider).lower()
    target_model = model_name or settings.chat_model

    if target_provider == "ollama":
        return OllamaLLM(
            model_name=target_model,
            base_url=settings.ollama_base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=getattr(settings, "ollama_timeout", 30.0),
            keep_alive=getattr(settings, "ollama_keep_alive", "5m"),
            **kwargs
        )
    else:
        # Default fallback to Ollama for local execution
        logger.info(f"Provider '{target_provider}' delegated to standard Ollama wrapper.")
        return OllamaLLM(
            model_name=target_model,
            base_url=settings.ollama_base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )


def get_llm(
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: float = 0.5,
    max_tokens: int = 1024
) -> BaseChatModel:
    """
    Centralized Provider-Agnostic LangChain ChatModel Factory.
    Full drop-in migration replacement for core/llm_factory.py.

    Supports:
      - ollama (Local)
      - openai / gpt
      - google / gemini
    """
    from config import settings

    target_provider = (provider or settings.llm_provider).lower()

    if target_provider == "ollama":
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            from langchain_community.chat_models.ollama import ChatOllama

        base_url = settings.ollama_base_url.replace("localhost", "127.0.0.1")
        return ChatOllama(
            model=model_name or settings.chat_model,
            base_url=base_url,
            temperature=temperature,
            num_predict=max_tokens
        )

    elif target_provider in ["openai", "gpt"]:
        try:
            from langchain_openai import ChatOpenAI
            api_key = settings.openai_api_key
            if not api_key:
                logger.warning("OPENAI_API_KEY is not set. Falling back to local Ollama LLM.")
                return get_llm("ollama", model_name, temperature, max_tokens)

            return ChatOpenAI(
                model=model_name or "gpt-4o-mini",
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except ImportError:
            logger.warning("langchain_openai not installed. Falling back to Ollama.")
            return get_llm("ollama", model_name, temperature, max_tokens)

    elif target_provider in ["google", "gemini"]:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            api_key = settings.google_api_key or getattr(settings, "gemini_api_key", None)
            if not api_key:
                logger.warning("GOOGLE_API_KEY is not set. Falling back to local Ollama LLM.")
                return get_llm("ollama", model_name, temperature, max_tokens)

            return ChatGoogleGenerativeAI(
                model=model_name or "gemini-1.5-flash",
                google_api_key=api_key,
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        except ImportError:
            logger.warning("langchain_google_genai is not installed. Falling back to local Ollama LLM.")
            return get_llm("ollama", model_name, temperature, max_tokens)

    else:
        logger.warning(f"Unknown LLM provider '{target_provider}'. Falling back to Ollama.")
        return get_llm("ollama", model_name, temperature, max_tokens)
