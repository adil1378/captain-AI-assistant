"""
Unit tests for SearchManager and WeatherManager strategy pattern fallback systems.
"""

import pytest
from src.providers.search_provider import (
    SearchProvider,
    TavilyProvider,
    SerpAPIProvider,
    DuckDuckGoProvider,
    SearchManager
)
from src.providers.weather_provider import (
    WeatherProvider,
    OpenMeteoProvider,
    OpenWeatherProvider,
    WeatherAPIProvider,
    WeatherManager
)


class FailingSearchProvider(SearchProvider):
    def __init__(self, name: str, err: str = "Simulated failure"):
        self._name = name
        self._err = err

    @property
    def name(self) -> str:
        return self._name

    def search(self, query: str, max_results: int = 5):
        return {"success": False, "provider": self._name, "error": self._err}


class SuccessSearchProvider(SearchProvider):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def search(self, query: str, max_results: int = 5):
        return {
            "success": True,
            "provider": self._name,
            "query": query,
            "results": [{"title": f"Result from {self._name}", "snippet": "Test snippet", "url": "https://example.com"}]
        }


class FailingWeatherProvider(WeatherProvider):
    def __init__(self, name: str, err: str = "Simulated weather failure"):
        self._name = name
        self._err = err

    @property
    def name(self) -> str:
        return self._name

    def get_weather(self, location: str):
        return {"success": False, "provider": self._name, "error": self._err}


class SuccessWeatherProvider(WeatherProvider):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def get_weather(self, location: str):
        return {
            "success": True,
            "provider": self._name,
            "location": location,
            "temperature_c": 25.0,
            "condition": "Sunny",
            "summary": f"Weather in {location}: 25°C, Sunny"
        }


def test_search_manager_primary_success():
    manager = SearchManager({
        "tavily": SuccessSearchProvider("tavily"),
        "serpapi": FailingSearchProvider("serpapi"),
        "duckduckgo": FailingSearchProvider("duckduckgo")
    })
    res = manager.search("python tutorials")
    assert res["success"] is True
    assert res["provider"] == "tavily"
    assert len(res["results"]) > 0


def test_search_manager_fallback_to_second():
    manager = SearchManager({
        "tavily": FailingSearchProvider("tavily", "429 Rate limit"),
        "serpapi": SuccessSearchProvider("serpapi"),
        "duckduckgo": FailingSearchProvider("duckduckgo")
    })
    res = manager.search("python tutorials")
    assert res["success"] is True
    assert res["provider"] == "serpapi"


def test_search_manager_all_failed_structured_error():
    manager = SearchManager({
        "tavily": FailingSearchProvider("tavily"),
        "serpapi": FailingSearchProvider("serpapi"),
        "duckduckgo": FailingSearchProvider("duckduckgo")
    })
    res = manager.search("python tutorials")
    assert res["success"] is False
    assert res["error"] == "All search providers failed."
    assert "tavily" in res["providers_tried"]
    assert "serpapi" in res["providers_tried"]
    assert "duckduckgo" in res["providers_tried"]


def test_weather_manager_primary_success():
    manager = WeatherManager({
        "openmeteo": SuccessWeatherProvider("openmeteo"),
        "wttrin": FailingWeatherProvider("wttrin"),
        "openweather": FailingWeatherProvider("openweather"),
        "weatherapi": FailingWeatherProvider("weatherapi")
    })
    res = manager.get_weather("Mumbai")
    assert res["success"] is True
    assert res["provider"] == "openmeteo"
    assert res["temperature_c"] == 25.0


def test_weather_manager_fallback_to_second():
    manager = WeatherManager({
        "openmeteo": FailingWeatherProvider("openmeteo", "Timeout"),
        "wttrin": SuccessWeatherProvider("wttrin"),
        "openweather": FailingWeatherProvider("openweather"),
        "weatherapi": FailingWeatherProvider("weatherapi")
    })
    res = manager.get_weather("Mumbai")
    assert res["success"] is True
    assert res["provider"] == "wttrin"


def test_weather_manager_all_failed_structured_error():
    manager = WeatherManager({
        "openmeteo": FailingWeatherProvider("openmeteo"),
        "wttrin": FailingWeatherProvider("wttrin"),
        "openweather": FailingWeatherProvider("openweather"),
        "weatherapi": FailingWeatherProvider("weatherapi")
    })
    res = manager.get_weather("Mumbai")
    assert res["success"] is False
    assert res["error"] == "All weather providers failed."
    assert "openmeteo" in res["providers_tried"]
    assert "wttrin" in res["providers_tried"]
    assert "openweather" in res["providers_tried"]
    assert "weatherapi" in res["providers_tried"]
