"""
Captain AI OS — Weather Tool Integration.
Delegates weather requests to WeatherManager strategy pattern fallback system.
"""

from typing import Dict, Any
from src.providers.weather_provider import weather_manager
from loguru import logger


def get_live_weather(city: str) -> Dict[str, Any]:
    """
    Fetch live weather data using WeatherManager strategy pattern fallback system.
    Tries configured priority order (e.g. Open-Meteo -> OpenWeather -> WeatherAPI).
    """
    res = weather_manager.get_weather(location=city)
    if res.get("success"):
        return {
            "status": "success",
            "provider": res.get("provider", "weather_manager"),
            "city": res.get("location", city),
            "temperature_celsius": res.get("temperature_c", 0.0),
            "condition": res.get("condition", "Unknown"),
            "humidity": res.get("humidity", 0),
            "windspeed_kmh": res.get("wind_kph", 0.0),
            "summary": res.get("summary", "")
        }
    else:
        return {
            "status": "error",
            "error": res.get("error", "Weather fetch failed."),
            "providers_tried": res.get("providers_tried", []),
            "summary": res.get("summary", f"Could not retrieve weather for {city}.")
        }
