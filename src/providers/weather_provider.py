"""
Captain AI OS — Production-Grade Weather Provider Fallback System.
Implements Strategy Pattern & Fallback Chain across Weather Providers (Open-Meteo, Wttr.in, OpenWeather, WeatherAPI).
Extensible for adding future weather providers (Tomorrow.io, Visual Crossing, AccuWeather, etc.).
"""

import os
import urllib.parse
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type
import httpx
from loguru import logger
from src.backend.config import settings


class WeatherProvider(ABC):
    """Abstract Base Strategy Interface for Weather Providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name identifier of the weather provider."""
        pass

    @abstractmethod
    def get_weather(self, location: str) -> Dict[str, Any]:
        """
        Fetch weather for location.
        Returns standardized result dictionary:
        {
            "success": True/False,
            "provider": str,
            "location": str,
            "temperature_c": float,
            "condition": str,
            "humidity": Optional[int],
            "wind_kph": Optional[float],
            "summary": str,
            "error": Optional[str]
        }
        """
        pass


class OpenMeteoProvider(WeatherProvider):
    """Primary Weather Strategy: Open-Meteo (Free, No API Key Required)."""

    @property
    def name(self) -> str:
        return "openmeteo"

    def get_weather(self, location: str) -> Dict[str, Any]:
        logger.info(f"Trying Open-Meteo for '{location}'...")
        try:
            # 1. Geocode location using Open-Meteo Geocoding API
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            with httpx.Client(timeout=12.0, headers=headers, follow_redirects=True) as client:
                geo_resp = client.get(geo_url, params={"name": location, "count": 1})
                if geo_resp.status_code == 429:
                    logger.warning("Open-Meteo geocoding rate limited (429).")
                    return {"success": False, "provider": self.name, "error": "Rate limited (429)"}
                geo_resp.raise_for_status()

                geo_data = geo_resp.json()
                results = geo_data.get("results", [])
                if not results:
                    logger.warning(f"Open-Meteo geocoding found no results for '{location}'.")
                    return {"success": False, "provider": self.name, "error": f"Location '{location}' not found."}

                lat = results[0]["latitude"]
                lon = results[0]["longitude"]
                resolved_name = results[0].get("name", location)
                country = results[0].get("country", "")

                # 2. Fetch forecast metrics
                forecast_url = "https://api.open-meteo.com/v1/forecast"
                forecast_params = {
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
                }
                f_resp = client.get(forecast_url, params=forecast_params)
                f_resp.raise_for_status()

                f_data = f_resp.json()
                current = f_data.get("current", {})
                if not current:
                    return {"success": False, "provider": self.name, "error": "Empty current weather data."}

                temp_c = current.get("temperature_2m", 0.0)
                humidity = current.get("relative_humidity_2m", 0)
                wind_kph = current.get("wind_speed_10m", 0.0)
                weather_code = current.get("weather_code", 0)

                # Weather code interpretation
                weather_map = {
                    0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
                    45: "Foggy", 51: "Light Drizzle", 61: "Rain Showers", 71: "Snow", 95: "Thunderstorm"
                }
                condition = weather_map.get(weather_code, "Clear/Cloudy")

                loc_str = f"{resolved_name}, {country}" if country else resolved_name
                summary = f"Weather in {loc_str}: {temp_c}°C, {condition}, Humidity: {humidity}%, Wind: {wind_kph} km/h"

                return {
                    "success": True,
                    "provider": self.name,
                    "location": loc_str,
                    "temperature_c": temp_c,
                    "condition": condition,
                    "humidity": humidity,
                    "wind_kph": wind_kph,
                    "summary": summary
                }
        except Exception as e:
            logger.warning(f"Open-Meteo weather error: {e}")
            return {"success": False, "provider": self.name, "error": str(e)}


class WttrInProvider(WeatherProvider):
    """Secondary Free Weather Strategy: Wttr.in Global Weather API (Zero API Key)."""

    @property
    def name(self) -> str:
        return "wttrin"

    def get_weather(self, location: str) -> Dict[str, Any]:
        logger.info(f"Trying Wttr.in for '{location}'...")
        try:
            encoded_loc = urllib.parse.quote(location)
            url = f"https://wttr.in/{encoded_loc}?format=j1"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            with httpx.Client(timeout=10.0, headers=headers, follow_redirects=True) as client:
                resp = client.get(url)
                resp.raise_for_status()

                data = resp.json()
                current_arr = data.get("current_condition", [])
                nearest_arr = data.get("nearest_area", [])

                if not current_arr:
                    return {"success": False, "provider": self.name, "error": "Empty current_condition from wttr.in"}

                current = current_arr[0]
                temp_c = float(current.get("temp_C", 0.0))
                humidity = int(current.get("humidity", 0))
                wind_kph = float(current.get("windspeedKmph", 0.0))
                weather_desc = current.get("weatherDesc", [{}])[0].get("value", "Clear")

                resolved_city = location
                country = ""
                if nearest_arr:
                    area_names = nearest_arr[0].get("areaName", [{}])
                    country_names = nearest_arr[0].get("country", [{}])
                    if area_names:
                        resolved_city = area_names[0].get("value", location)
                    if country_names:
                        country = country_names[0].get("value", "")

                loc_str = f"{resolved_city}, {country}" if country else resolved_city
                summary = f"Weather in {loc_str}: {temp_c}°C, {weather_desc}, Humidity: {humidity}%, Wind: {wind_kph} km/h"

                return {
                    "success": True,
                    "provider": self.name,
                    "location": loc_str,
                    "temperature_c": temp_c,
                    "condition": weather_desc,
                    "humidity": humidity,
                    "wind_kph": wind_kph,
                    "summary": summary
                }
        except Exception as e:
            logger.warning(f"Wttr.in weather error: {e}")
            return {"success": False, "provider": self.name, "error": str(e)}


class OpenWeatherProvider(WeatherProvider):
    """First Fallback Weather Strategy: OpenWeatherMap API."""

    @property
    def name(self) -> str:
        return "openweather"

    def get_weather(self, location: str) -> Dict[str, Any]:
        api_key = getattr(settings, "OPENWEATHER_API_KEY", None) or os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            logger.warning("OpenWeather skipped: OPENWEATHER_API_KEY not configured.")
            return {"success": False, "provider": self.name, "error": "API key missing or empty."}

        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": api_key,
            "units": "metric"
        }

        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.get(url, params=params)
                if resp.status_code == 429:
                    logger.warning("OpenWeather rate limit exceeded (429).")
                    return {"success": False, "provider": self.name, "error": "Rate limit exceeded (429)"}
                if resp.status_code in [401, 403]:
                    logger.warning("OpenWeather authentication failure (invalid key).")
                    return {"success": False, "provider": self.name, "error": "Invalid API key."}
                resp.raise_for_status()

                data = resp.json()
                main = data.get("main", {})
                weather_arr = data.get("weather", [{}])
                wind = data.get("wind", {})

                if not main:
                    return {"success": False, "provider": self.name, "error": "Empty weather data object."}

                temp_c = main.get("temp", 0.0)
                humidity = main.get("humidity", 0)
                wind_kph = round(wind.get("speed", 0.0) * 3.6, 1)
                condition = weather_arr[0].get("description", "Clear").title() if weather_arr else "Clear"
                city_name = data.get("name", location)
                country = data.get("sys", {}).get("country", "")

                loc_str = f"{city_name}, {country}" if country else city_name
                summary = f"Weather in {loc_str}: {temp_c}°C, {condition}, Humidity: {humidity}%, Wind: {wind_kph} km/h"

                return {
                    "success": True,
                    "provider": self.name,
                    "location": loc_str,
                    "temperature_c": temp_c,
                    "condition": condition,
                    "humidity": humidity,
                    "wind_kph": wind_kph,
                    "summary": summary
                }
        except Exception as e:
            logger.warning(f"OpenWeather error: {e}")
            return {"success": False, "provider": self.name, "error": str(e)}


class WeatherAPIProvider(WeatherProvider):
    """Final Fallback Weather Strategy: WeatherAPI.com."""

    @property
    def name(self) -> str:
        return "weatherapi"

    def get_weather(self, location: str) -> Dict[str, Any]:
        api_key = getattr(settings, "WEATHERAPI_API_KEY", None) or os.getenv("WEATHERAPI_API_KEY")
        if not api_key:
            logger.warning("WeatherAPI skipped: WEATHERAPI_API_KEY not configured.")
            return {"success": False, "provider": self.name, "error": "API key missing or empty."}

        url = "http://api.weatherapi.com/v1/current.json"
        params = {
            "key": api_key,
            "q": location
        }

        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.get(url, params=params)
                if resp.status_code == 429:
                    logger.warning("WeatherAPI rate limit / credits exhausted (429).")
                    return {"success": False, "provider": self.name, "error": "Rate limit / credits exhausted (429)"}
                if resp.status_code in [401, 403]:
                    logger.warning("WeatherAPI authentication error.")
                    return {"success": False, "provider": self.name, "error": "Invalid API key."}
                resp.raise_for_status()

                data = resp.json()
                current = data.get("current", {})
                loc = data.get("location", {})

                if not current:
                    return {"success": False, "provider": self.name, "error": "Empty weather object."}

                temp_c = current.get("temp_c", 0.0)
                humidity = current.get("humidity", 0)
                wind_kph = current.get("wind_kph", 0.0)
                condition = current.get("condition", {}).get("text", "Clear")
                loc_name = loc.get("name", location)
                country = loc.get("country", "")

                loc_str = f"{loc_name}, {country}" if country else loc_name
                summary = f"Weather in {loc_str}: {temp_c}°C, {condition}, Humidity: {humidity}%, Wind: {wind_kph} km/h"

                return {
                    "success": True,
                    "provider": self.name,
                    "location": loc_str,
                    "temperature_c": temp_c,
                    "condition": condition,
                    "humidity": humidity,
                    "wind_kph": wind_kph,
                    "summary": summary
                }
        except Exception as e:
            logger.warning(f"WeatherAPI error: {e}")
            return {"success": False, "provider": self.name, "error": str(e)}


class WeatherManager:
    """
    Production Strategy Orchestrator for Weather Providers.
    Iterates dynamically through WEATHER_PROVIDER_PRIORITY with automatic fallback.
    Extensible for registering new weather providers seamlessly.
    """

    def __init__(self, custom_providers: Optional[Dict[str, WeatherProvider]] = None):
        # Register default strategies
        self._provider_registry: Dict[str, WeatherProvider] = {
            "openmeteo": OpenMeteoProvider(),
            "wttrin": WttrInProvider(),
            "openweather": OpenWeatherProvider(),
            "weatherapi": WeatherAPIProvider()
        }
        if custom_providers:
            self._provider_registry.update(custom_providers)

    def register_provider(self, provider: WeatherProvider):
        """Register a new custom weather provider strategy at runtime."""
        self._provider_registry[provider.name.lower()] = provider
        logger.info(f"WeatherManager: Registered custom weather strategy '{provider.name}'")

    def get_priority_order(self) -> List[str]:
        """Read priority order dynamically from configuration / environment."""
        raw_priority = getattr(settings, "WEATHER_PROVIDER_PRIORITY", "openmeteo,wttrin,openweather,weatherapi")
        if not raw_priority:
            raw_priority = "openmeteo,wttrin,openweather,weatherapi"
        
        providers = [p.strip().lower() for p in raw_priority.split(",") if p.strip()]
        return providers if providers else ["openmeteo", "wttrin", "openweather", "weatherapi"]

    def get_weather(self, location: str) -> Dict[str, Any]:
        """
        Fetch weather for location across providers in order of priority with automatic fallback.
        Never crashes. Returns structured success dictionary or structured failure report.
        """
        priority_list = self.get_priority_order()
        providers_tried = []

        logger.info(f"Getting weather for: {location}")

        for provider_name in priority_list:
            provider = self._provider_registry.get(provider_name)
            if not provider:
                logger.warning(f"WeatherManager: Unknown provider strategy '{provider_name}' in priority list. Skipping.")
                continue

            providers_tried.append(provider_name)
            logger.info(f"Trying {provider.name.capitalize()}...")

            res = provider.get_weather(location=location)
            if res.get("success"):
                logger.info(f"{provider.name.capitalize()} succeeded. Weather returned successfully.")
                return res
            else:
                err_msg = res.get("error", "Unknown error")
                logger.warning(f"{provider.name.capitalize()} unavailable ({err_msg}). Switching to next provider...")

        logger.error(f"WeatherManager: All weather providers failed ({providers_tried}).")
        return {
            "success": False,
            "error": "All weather providers failed.",
            "providers_tried": providers_tried,
            "location": location,
            "summary": f"Could not retrieve weather for {location}. All weather providers failed."
        }


# Global Singleton Instance for application-wide Dependency Injection
weather_manager = WeatherManager()
