import httpx
from typing import Dict, Any
from loguru import logger

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {
    "User-Agent": "Captain-AI-OS/2.0 (https://github.com/adil1378/captain-AI-assistant)"
}


KNOWN_LOCATIONS = {
    "aurangabad": {"lat": "19.8762", "lon": "75.3433", "display_name": "Aurangabad (Chhatrapati Sambhajinagar), Maharashtra, India", "type": "city"},
    "mumbai": {"lat": "19.0760", "lon": "72.8777", "display_name": "Mumbai, Maharashtra, India", "type": "city"},
    "karachi": {"lat": "24.8607", "lon": "67.0011", "display_name": "Karachi, Sindh, Pakistan", "type": "city"},
    "delhi": {"lat": "28.6139", "lon": "77.2090", "display_name": "New Delhi, Delhi, India", "type": "city"},
}


def _get_fallback_location(clean_query: str) -> Dict[str, Any]:
    q_lower = clean_query.lower()
    for city_key, loc in KNOWN_LOCATIONS.items():
        if city_key in q_lower:
            map_url = f"https://www.openstreetmap.org/?mlat={loc['lat']}&mlon={loc['lon']}#map=12/{loc['lat']}/{loc['lon']}"
            return {
                "status": "success",
                "query": clean_query,
                "display_name": loc["display_name"],
                "latitude": loc["lat"],
                "longitude": loc["lon"],
                "type": loc["type"],
                "map_url": map_url
            }
    return {}


async def get_location_info(location_query: str) -> Dict[str, Any]:
    """
    Fetch structured geographic geocoding data and map URLs using OpenStreetMap Nominatim.
    Strictly handles timeout, user-agent compliance, offline landmark fallback, and empty/error states.
    """
    clean_query = location_query.strip()
    if not clean_query:
        return {"status": "error", "error": "Location query cannot be empty."}

    params = {
        "q": clean_query,
        "format": "json",
        "limit": 1,
        "addressdetails": 1
    }

    try:
        async with httpx.AsyncClient(timeout=5.0, headers=HEADERS) as client:
            response = await client.get(NOMINATIM_URL, params=params)
            
            if response.status_code != 200:
                logger.warning(f"LocationTool: Nominatim API returned HTTP {response.status_code}")
                fallback = _get_fallback_location(clean_query)
                if fallback:
                    return fallback
                return {
                    "status": "error",
                    "error": f"Geocoding service returned status HTTP {response.status_code}"
                }

            results = response.json()
            if not results:
                logger.info(f"LocationTool: No geocoding results found for '{clean_query}'")
                fallback = _get_fallback_location(clean_query)
                if fallback:
                    return fallback
                return {
                    "status": "error",
                    "error": f"No location results found for '{clean_query}'."
                }

            top = results[0]
            lat = top.get("lat", "")
            lon = top.get("lon", "")
            display_name = top.get("display_name", clean_query)
            location_type = top.get("type", "location")

            # Construct OpenStreetMap interactive view URL
            map_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=12/{lat[:7]}/{lon[:7]}"

            logger.info(f"LocationTool: Successfully geocoded '{clean_query}' -> ({lat}, {lon})")

            return {
                "status": "success",
                "query": clean_query,
                "display_name": display_name,
                "latitude": lat,
                "longitude": lon,
                "type": location_type,
                "map_url": map_url
            }

    except (httpx.TimeoutException, httpx.RequestError) as net_err:
        logger.warning(f"LocationTool: Network error/timeout for '{clean_query}': {net_err}")
        fallback = _get_fallback_location(clean_query)
        if fallback:
            return fallback
        return {"status": "error", "error": f"Geocoding request failed: {net_err}"}
    except Exception as e:
        logger.error(f"LocationTool: Exception encountered for '{clean_query}': {e}")
        fallback = _get_fallback_location(clean_query)
        if fallback:
            return fallback
        return {"status": "error", "error": f"Location lookup failed: {str(e)}"}
