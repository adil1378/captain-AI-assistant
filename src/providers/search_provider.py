"""
Captain AI OS — Production-Grade Search Provider Fallback System.
Implements Strategy Pattern & Fallback Chain across Search Providers (Tavily, SerpAPI, DuckDuckGo).
Extensible for adding future providers (Google CSE, Brave, Bing, Exa, etc.).
"""

import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type
import httpx
from loguru import logger
from src.backend.config import settings


class SearchProvider(ABC):
    """Abstract Base Strategy Interface for Search Providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name identifier of the search provider."""
        pass

    @abstractmethod
    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Execute search query.
        Returns standardized result dictionary:
        {
            "success": True/False,
            "provider": str,
            "query": str,
            "results": [{"title": str, "snippet": str, "url": str}],
            "error": Optional[str]
        }
        """
        pass


class TavilyProvider(SearchProvider):
    """Primary Search Strategy: Tavily Search API."""

    @property
    def name(self) -> str:
        return "tavily"

    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        api_key = getattr(settings, "TAVILY_API_KEY", None) or os.getenv("TAVILY_API_KEY")
        if not api_key:
            logger.warning("Tavily search skipped: TAVILY_API_KEY not configured.")
            return {"success": False, "provider": self.name, "error": "API key missing or empty."}

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "basic"
        }

        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.post(url, json=payload)
                if resp.status_code == 429:
                    logger.warning("Tavily search failed (429 - Rate limit / credits exhausted)")
                    return {"success": False, "provider": self.name, "error": "Rate limit / credits exhausted (429)"}
                resp.raise_for_status()

                data = resp.json()
                raw_results = data.get("results", [])
                if not raw_results:
                    logger.warning("Tavily search returned empty results.")
                    return {"success": False, "provider": self.name, "error": "Empty search response."}

                results = [
                    {
                        "title": r.get("title", "No Title"),
                        "snippet": r.get("content", r.get("snippet", "")),
                        "url": r.get("url", "")
                    }
                    for r in raw_results
                ]
                return {
                    "success": True,
                    "provider": self.name,
                    "query": query,
                    "results": results
                }
        except Exception as e:
            logger.warning(f"Tavily search error: {e}")
            return {"success": False, "provider": self.name, "error": str(e)}


class SerpAPIProvider(SearchProvider):
    """First Fallback Search Strategy: SerpAPI (Google Search Engine API)."""

    @property
    def name(self) -> str:
        return "serpapi"

    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        api_key = getattr(settings, "SERPAPI_API_KEY", None) or os.getenv("SERPAPI_API_KEY")
        if not api_key:
            logger.warning("SerpAPI search skipped: SERPAPI_API_KEY not configured.")
            return {"success": False, "provider": self.name, "error": "API key missing or empty."}

        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": api_key,
            "engine": "google",
            "num": max_results
        }

        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.get(url, params=params)
                if resp.status_code == 429:
                    logger.warning("SerpAPI search failed (429 - Rate limit / credits exhausted)")
                    return {"success": False, "provider": self.name, "error": "Rate limit / credits exhausted (429)"}
                resp.raise_for_status()

                data = resp.json()
                raw_results = data.get("organic_results", [])
                if not raw_results:
                    logger.warning("SerpAPI search returned empty organic_results.")
                    return {"success": False, "provider": self.name, "error": "Empty organic results."}

                results = [
                    {
                        "title": r.get("title", "No Title"),
                        "snippet": r.get("snippet", ""),
                        "url": r.get("link", r.get("url", ""))
                    }
                    for r in raw_results[:max_results]
                ]
                return {
                    "success": True,
                    "provider": self.name,
                    "query": query,
                    "results": results
                }
        except Exception as e:
            logger.warning(f"SerpAPI search error: {e}")
            return {"success": False, "provider": self.name, "error": str(e)}


class DuckDuckGoProvider(SearchProvider):
    """Final Fallback Search Strategy: Free DuckDuckGo Search."""

    @property
    def name(self) -> str:
        return "duckduckgo"

    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Direct HTTP HTML search via httpx & BeautifulSoup (zero external dependencies)."""
        try:
            url = "https://html.duckduckgo.com/html/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            with httpx.Client(timeout=10.0, headers=headers, follow_redirects=True) as client:
                resp = client.post(url, data={"q": query})
                resp.raise_for_status()

                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, "html.parser")
                results = []
                for result in soup.find_all("div", class_="result")[:max_results]:
                    title_tag = result.find("a", class_="result__a")
                    snippet_tag = result.find("a", class_="result__snippet")
                    if title_tag:
                        results.append({
                            "title": title_tag.get_text(strip=True),
                            "snippet": snippet_tag.get_text(strip=True) if snippet_tag else "",
                            "url": title_tag.get("href", "")
                        })

                if results:
                    return {
                        "success": True,
                        "provider": self.name,
                        "query": query,
                        "results": results
                    }
                logger.warning("DuckDuckGo HTML search returned empty results array.")
                return {"success": False, "provider": self.name, "error": "DuckDuckGo returned empty results."}

        except Exception as e:
            logger.warning(f"DuckDuckGo HTTP search error: {e}")
            return {"success": False, "provider": self.name, "error": str(e)}


class SearchManager:
    """
    Production Strategy Orchestrator for Search Providers.
    Iterates dynamically through SEARCH_PROVIDER_PRIORITY with automatic fallback.
    Extensible for registering new search providers seamlessly.
    """

    def __init__(self, custom_providers: Optional[Dict[str, SearchProvider]] = None):
        # Register default strategies
        self._provider_registry: Dict[str, SearchProvider] = {
            "tavily": TavilyProvider(),
            "serpapi": SerpAPIProvider(),
            "duckduckgo": DuckDuckGoProvider()
        }
        if custom_providers:
            self._provider_registry.update(custom_providers)

    def register_provider(self, provider: SearchProvider):
        """Register a new custom search provider strategy at runtime."""
        self._provider_registry[provider.name.lower()] = provider
        logger.info(f"SearchManager: Registered custom provider strategy '{provider.name}'")

    def get_priority_order(self) -> List[str]:
        """Read priority order dynamically from configuration / environment."""
        raw_priority = getattr(settings, "SEARCH_PROVIDER_PRIORITY", "tavily,serpapi,duckduckgo")
        if not raw_priority:
            raw_priority = "tavily,serpapi,duckduckgo"
        
        providers = [p.strip().lower() for p in raw_priority.split(",") if p.strip()]
        return providers if providers else ["tavily", "serpapi", "duckduckgo"]

    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Execute search query across providers in order of priority with automatic fallback.
        Never crashes. Returns structured success dictionary or structured failure report.
        """
        priority_list = self.get_priority_order()
        providers_tried = []

        for provider_name in priority_list:
            provider = self._provider_registry.get(provider_name)
            if not provider:
                logger.warning(f"SearchManager: Unknown provider strategy '{provider_name}' in priority list. Skipping.")
                continue

            providers_tried.append(provider_name)
            logger.info(f"Searching with {provider.name.capitalize()}...")
            
            res = provider.search(query=query, max_results=max_results)
            if res.get("success") and res.get("results"):
                logger.info(f"{provider.name.capitalize()} succeeded. Search completed using {provider.name.capitalize()}.")
                return res
            else:
                err_msg = res.get("error", "Unknown error")
                logger.warning(f"{provider.name.capitalize()} failed ({err_msg}). Switching to next provider...")

        logger.error(f"SearchManager: All search providers failed ({providers_tried}).")
        return {
            "success": False,
            "error": "All search providers failed.",
            "providers_tried": providers_tried,
            "query": query,
            "results": []
        }


# Global Singleton Instance for application-wide Dependency Injection
search_manager = SearchManager()
