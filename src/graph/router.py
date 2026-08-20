import re
from enum import Enum
from pydantic import BaseModel
from loguru import logger


class Intent(str, Enum):
    GREETING = "GREETING"
    GENERAL_QA = "GENERAL_QA"
    LOCATION = "LOCATION"
    WEB_SEARCH = "WEB_SEARCH"
    WEATHER = "WEATHER"
    CODING = "CODING"
    RAG = "RAG"
    COMMS = "COMMS"


class IntentResult(BaseModel):
    intent: Intent
    confidence: float
    query: str


def _has_word(query: str, word: str) -> bool:
    """Word-boundary regex match helper to prevent substring false positives."""
    return bool(re.search(r'\b' + re.escape(word) + r'\b', query, re.IGNORECASE))


def classify_intent_hybrid(user_query: str) -> IntentResult:
    """
    Enterprise Intent Classifier.
    Returns a validated IntentResult Pydantic object with intent type, confidence, and query.
    """
    q_raw = user_query.strip()
    q = q_raw.lower()

    if not q:
        return IntentResult(intent=Intent.GREETING, confidence=1.0, query=q_raw)

    # 1. GREETING
    greetings = ["hi", "hello", "hey", "howdy", "greetings", "good morning", "good evening", "good afternoon"]
    if q in greetings or any(q.startswith(g + " ") for g in greetings) or q == "hi captain":
        return IntentResult(intent=Intent.GREETING, confidence=0.98, query=q_raw)

    # 2. LOCATION Intent (Distinct from generic search)
    location_triggers = ["where is", "location of", "show on map", "coordinates of", "map of", "where located", "where in the world is"]
    if any(trigger in q for trigger in location_triggers):
        return IntentResult(intent=Intent.LOCATION, confidence=0.96, query=q_raw)

    # 3. CODING Intent (Evaluated before WEATHER to handle 'weather API in Python' properly)
    coding_exact = ["def ", "class ", "import ", "syntax error", "refactor", "debug", "github", "git commit", "ci/cd", "pipeline", "fibonacci", "api in python", "weather api", "rest api"]
    coding_combinations = (
        ("write" in q or "build" in q or "create" in q or "how to" in q or "use" in q or "generate" in q)
        and ("code" in q or "function" in q or "script" in q or "python" in q or "api" in q or "endpoint" in q)
    ) or ("api" in q and "python" in q)
    if any(kw in q for kw in coding_exact) or coding_combinations:
        return IntentResult(intent=Intent.CODING, confidence=0.95, query=q_raw)

    # 4. WEATHER / SYSTEM Intent
    weather_words = ["weather", "temperature", "forecast", "rain", "climate", "humid"]
    live_weather_indicators = [" in ", " for ", " at ", " of ", "today", "now", "current", "live", "city", "forecast"]
    has_weather_word = any(_has_word(q, w) for w in weather_words)
    has_live_indicator = any(ind in q for ind in live_weather_indicators)
    system_phrases = ["system metrics", "memory usage", "cpu usage", "disk space", "os info", "battery status", "hardware metrics"]

    if (has_weather_word and has_live_indicator) or any(kw in q for kw in system_phrases):
        return IntentResult(intent=Intent.WEATHER, confidence=0.95, query=q_raw)

    # 5. RAG / DOCUMENT Intent
    rag_phrases = ["document", "uploaded file", "my notes", "pdf", "knowledge base", "from the doc", "explain this uploaded"]
    if any(kw in q for kw in rag_phrases):
        return IntentResult(intent=Intent.RAG, confidence=0.94, query=q_raw)

    # 6. COMMS Intent
    comms_phrases = ["send email", "send mail", "whatsapp", "send message", "save contact", "add contact"]
    if any(kw in q for kw in comms_phrases):
        return IntentResult(intent=Intent.COMMS, confidence=0.94, query=q_raw)

    # 7. WEB_SEARCH Intent
    if q.startswith("search") or "search the latest" in q or "find online" in q or "google" in q or "latest news" in q or "latest ai news" in q:
        return IntentResult(intent=Intent.WEB_SEARCH, confidence=0.93, query=q_raw)

    # Default: GENERAL_QA
    return IntentResult(intent=Intent.GENERAL_QA, confidence=0.90, query=q_raw)
