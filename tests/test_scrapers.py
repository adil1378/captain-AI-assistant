from tools.youtube_scraper import extract_youtube_video_id
from tools.system_tools import get_system_metrics
from tools.weather import get_live_weather
from tools.search import search_web


def test_youtube_id_extraction():
    url1 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    url2 = "https://youtu.be/dQw4w9WgXcQ"
    assert extract_youtube_video_id(url1) == "dQw4w9WgXcQ"
    assert extract_youtube_video_id(url2) == "dQw4w9WgXcQ"


def test_system_metrics():
    res = get_system_metrics()
    assert res["status"] == "success"
    assert "cpu_usage_percent" in res
    assert "memory_percent" in res


def test_live_weather():
    res = get_live_weather("London")
    assert res["status"] in ("success", "error")
    if res["status"] == "success":
        assert "temperature_celsius" in res
    else:
        assert "error" in res


def test_web_search():
    res = search_web("Python programming language")
    assert res["status"] in ("success", "error")
    if res["status"] == "success":
        assert len(res.get("results", [])) >= 1
    else:
        assert "error" in res

