import re
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from src.agents.state import AgentState
from src.agents.base_agent import BaseAgent, AgentMetadata
from src.backend.core.model_manager import model_manager
from src.backend.config import settings
from tools.system_tools import get_system_metrics, run_terminal_command
from tools.weather import get_live_weather
from utils.text_utils import clean_think_tags
from loguru import logger


class SystemAgent(BaseAgent):
    """Production System Metrics, Weather & Terminal Command Agent."""

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="system_agent",
            description="System Metrics, Weather Reporting, and Terminal Command Agent",
            version="2.0.0",
            capabilities=["system_metrics", "weather", "terminal_commands"]
        )

    def _extract_city(self, query: str) -> str:
        """Extract city name from weather-related queries."""
        stopwords = {"tell", "me", "what", "is", "the", "today", "now", "current", "live", "city", "forecast", "report", "show", "give"}
        patterns = [
            r"weather (?:in|for|at|of) ([A-Za-z\s]+?)(?:\?|$|\.|today|now)",
            r"temperature (?:in|for|at|of) ([A-Za-z\s]+?)(?:\?|$|\.|today|now)",
            r"([A-Za-z\s]+?)(?:city)?\s*(?:today|now)?\s*weather",
            r"weather\s*(?:of|in|for)?\s*([A-Za-z\s]+?)(?:city)?(?:\?|$|\.|\s*today|\s*now)"
        ]
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                raw_city = match.group(1).strip()
                words = [w for w in raw_city.split() if w.lower() not in stopwords]
                if words:
                    return " ".join(words)
        
        words = [w for w in query.split() if w.lower() not in stopwords and w.lower() != "weather"]
        if words:
            return " ".join(words)
        return ""

    def _extract_command(self, query: str) -> str:
        """Extract shell command from terminal-related queries."""
        patterns = [
            r"run[:\s]+[`\"']?(.+?)[`\"']?$",
            r"execute[:\s]+[`\"']?(.+?)[`\"']?$",
            r"command[:\s]+[`\"']?(.+?)[`\"']?$",
        ]
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        user_query = state.get("user_query", "")
        history = state.get("messages", [])  # Full conversation history from LangGraph
        scratchpad = state.get("scratchpad", {})
        query_lower = user_query.lower()

        tool_context = ""

        # --- Branch 1: System Metrics ---
        if any(k in query_lower for k in ["cpu", "ram", "memory", "disk", "battery", "metrics", "performance", "usage", "storage"]):
            metrics = get_system_metrics()
            if metrics.get("status") == "success":
                tool_context = (
                    f"LIVE SYSTEM METRICS:\n"
                    f"- CPU Usage: {metrics['cpu_percent']}%\n"
                    f"- RAM: {metrics['memory_used_gb']} GB used / {metrics['memory_total_gb']} GB total ({metrics['memory_percent']}% used)\n"
                    f"- Disk C:\\: {metrics['disk']['used_gb']} GB used / {metrics['disk']['total_gb']} GB total ({metrics['disk']['percent']}% full)\n"
                    f"- Battery: {metrics['battery']['percent']}% "
                    f"({'Plugged In' if metrics['battery']['power_plugged'] else 'On Battery'})"
                )
                logger.info("SystemAgent: Fetched system metrics successfully.")

        # --- Branch 2: Weather ---
        elif any(k in query_lower for k in ["weather", "temperature", "forecast", "rain", "wind", "climate", "humid"]):
            city = self._extract_city(user_query) or "Karachi"
            weather = get_live_weather(city)
            if weather.get("status") == "success":
                loc_name = weather.get("city") or weather.get("location") or city
                temp_c = weather.get("temperature_celsius") or weather.get("temperature_c", 0.0)
                condition = weather.get("condition", "Clear")
                humidity = weather.get("humidity", 0)
                wind_kph = weather.get("windspeed_kmh") or weather.get("wind_kph", 0.0)
                summary = weather.get("summary", "")

                tool_context = (
                    f"LIVE WEATHER DATA:\n"
                    f"- Location: {loc_name}\n"
                    f"- Temperature: {temp_c}°C\n"
                    f"- Condition: {condition}\n"
                    f"- Humidity: {humidity}%\n"
                    f"- Wind Speed: {wind_kph} km/h\n"
                    f"- Summary: {summary}"
                )
                logger.info(f"SystemAgent: Fetched live weather for {loc_name}.")
            else:
                tool_context = f"Weather fetch failed: {weather.get('error', 'Unknown error')}"

        # --- Branch 3: Terminal Command ---
        elif any(k in query_lower for k in ["run", "execute", "command", "terminal", "shell", "cmd", "ping", "dir", "ls"]):
            cmd = self._extract_command(user_query)
            if cmd:
                result = run_terminal_command(cmd)
                if result.get("status") == "success":
                    tool_context = (
                        f"TERMINAL COMMAND OUTPUT:\n"
                        f"$ {result['command']}\n"
                        f"Return Code: {result['returncode']}\n"
                        f"Output:\n{result['output']}"
                    )
                else:
                    tool_context = f"Command failed: {result.get('error')}"
                logger.info(f"SystemAgent: Executed terminal command: {cmd}")

        # --- Build prompt with tool context ---
        system_prompt = (
            "You are Captain System, an elite assistant specialized in computer hardware metrics, "
            "weather reporting, and system operations. Provide clean, informative, well-formatted responses. "
            "When system data is provided, use it directly and accurately in your response."
        )

        # SystemMessage + optional tool data + full conversation history
        messages_to_send = [SystemMessage(content=system_prompt)]
        if tool_context:
            messages_to_send.append(SystemMessage(content=f"Real-Time Tool Data:\n{tool_context}"))
        # Append full history (includes current HumanMessage injected by main.py)
        messages_to_send.extend(history)
        # Fallback: if history is empty, append user query manually
        if not any(isinstance(m, HumanMessage) for m in history):
            messages_to_send.append(HumanMessage(content=user_query))

        llm = model_manager.get_model(model_name=settings.CHAT_MODEL, temperature=0.3, max_tokens=1024)

        try:
            text_chunks = []
            async for chunk in llm.astream(messages_to_send):
                await self.check_pause()
                chunk_str = chunk.content if hasattr(chunk, "content") else str(chunk)
                text_chunks.append(chunk_str)

            raw_text = "".join(text_chunks)
            clean_text = clean_think_tags(raw_text)

            if not clean_text or len(clean_text) < 3:
                clean_text = tool_context or "System data retrieved. How can I help further?"

            scratchpad["system_output"] = clean_text
            return {
                "messages": [AIMessage(content=clean_text)],
                "scratchpad": scratchpad,
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }

        except Exception as e:
            logger.error(f"SystemAgent error: {e}")
            fallback = tool_context if tool_context else f"System agent encountered an error: {e}"
            return {
                "messages": [AIMessage(content=fallback)],
                "error": str(e),
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }
