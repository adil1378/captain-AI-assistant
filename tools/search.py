"""
Captain AI OS — Search Tool Integration.
Delegates search execution to SearchManager strategy pattern fallback system.
"""

from typing import Dict, Any, List
from src.providers.search_provider import search_manager
from loguru import logger


def search_web(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Search the internet using SearchManager strategy pattern fallback system.
    Tries configured priority order (e.g. Tavily -> SerpAPI -> DuckDuckGo).
    """
    res = search_manager.search(query=query, max_results=max_results)
    if res.get("success"):
        return {
            "status": "success",
            "engine": res.get("provider", "search_manager"),
            "query": query,
            "results": res.get("results", [])
        }
    else:
        return {
            "status": "error",
            "error": res.get("error", "Search failed."),
            "providers_tried": res.get("providers_tried", []),
            "results": []
        }


def multi_search(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Alias for search_web compatibility."""
    return search_web(query, max_results=max_results)
