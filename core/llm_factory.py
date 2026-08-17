from typing import Optional
from langchain_core.language_models import BaseChatModel
from config import settings
from loguru import logger


def get_llm(
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: float = 0.5,
    max_tokens: int = 1024
) -> BaseChatModel:
    """
    Centralized Provider-Agnostic LLM Factory.
    Instantiates ChatModels for Ollama (local), OpenAI, or Gemini based on configuration.

    Uses config.py field names (lowercase):
        settings.llm_provider, settings.chat_model, settings.ollama_base_url,
        settings.openai_api_key, settings.google_api_key
    """
    target_provider = (provider or settings.llm_provider).lower()

    if target_provider == "ollama":
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            from langchain_community.chat_models.ollama import ChatOllama

        return ChatOllama(
            model=model_name or settings.chat_model,
            base_url=settings.ollama_base_url,
            temperature=temperature,
            num_predict=max_tokens
        )

    elif target_provider in ["openai", "gpt"]:
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

    elif target_provider in ["google", "gemini"]:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            api_key = settings.google_api_key
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