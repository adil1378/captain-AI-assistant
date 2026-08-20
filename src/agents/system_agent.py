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

    def _is_conceptual_explanation(self, query_lower: str) -> bool:
        """Check if query is asking for a conceptual explanation rather than live system action."""
        live_action_triggers = [
            "current", "live", "my computer", "this system", "this machine",
            "show ", "run ", "execute ", "check ", "how much"
        ]
        # Specific location weather queries (e.g., "weather in mumbai", "weather of karachi") are live weather queries
        is_weather_location = ("weather" in query_lower or "temperature" in query_lower) and any(w in query_lower for w in [" in ", " for ", " at ", " of "])
        
        if any(trigger in query_lower for trigger in live_action_triggers) or is_weather_location:
            return False

        conceptual_triggers = [
            "what is", "explain", "definition of", "how does", "what does",
            "difference between", "meaning of", "why is", "tell me about"
        ]
        return any(trigger in query_lower for trigger in conceptual_triggers)

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        from src.tools.global_tools import tool_invocation_layer, init_global_tools
        from src.tools.tool_invocation_layer import ToolExecutionStatus

        user_query = state.get("user_query", "")
        history = state.get("messages", [])  # Full conversation history from LangGraph
        scratchpad = state.get("scratchpad", {})
        query_lower = user_query.lower().strip()

        tool_context = ""

        # Initialize global tool registry & security boundary
        await init_global_tools()

        is_conceptual = self._is_conceptual_explanation(query_lower)

        # --- Branch 1: System Metrics (Only if NOT conceptual explanation) ---
        if not is_conceptual and any(k in query_lower for k in ["cpu", "ram", "memory", "disk", "battery", "metrics", "performance", "usage", "storage"]):
            exec_res = await tool_invocation_layer.execute_tool(
                "get_system_metrics",
                {},
                caller_agent_name=self.metadata.name
            )
            if exec_res.status == ToolExecutionStatus.SUCCESS and isinstance(exec_res.result, dict):
                metrics = exec_res.result
                tool_context = (
                    f"LIVE SYSTEM METRICS:\n"
                    f"- CPU Usage: {metrics.get('cpu_percent', 0)}%\n"
                    f"- RAM: {metrics.get('memory_used_gb', 0)} GB used / {metrics.get('memory_total_gb', 0)} GB total ({metrics.get('memory_percent', 0)}% used)\n"
                    f"- Disk C:\\: {metrics.get('disk', {}).get('used_gb', 0)} GB used / {metrics.get('disk', {}).get('total_gb', 0)} GB total ({metrics.get('disk', {}).get('percent', 0)}% full)\n"
                    f"- Battery: {metrics.get('battery', {}).get('percent', 100)}% "
                    f"({'Plugged In' if metrics.get('battery', {}).get('power_plugged', True) else 'On Battery'})"
                )
                logger.info("SystemAgent: Fetched system metrics via ToolInvocationLayer successfully.")
            elif exec_res.status == ToolExecutionStatus.PERMISSION_DENIED:
                tool_context = f"Permission denied for system metrics: {exec_res.error}"

        # --- Branch 2: Weather (Only if NOT conceptual explanation) ---
        elif not is_conceptual and any(k in query_lower for k in ["weather", "temperature", "forecast", "rain", "wind", "climate", "humid"]):
            city = self._extract_city(user_query) or "Karachi"
            exec_res = await tool_invocation_layer.execute_tool(
                "get_live_weather",
                {"city": city},
                caller_agent_name=self.metadata.name
            )
            if exec_res.status == ToolExecutionStatus.SUCCESS and isinstance(exec_res.result, dict):
                weather = exec_res.result
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
                logger.info(f"SystemAgent: Fetched live weather for {loc_name} via ToolInvocationLayer.")
            elif exec_res.status == ToolExecutionStatus.PERMISSION_DENIED:
                tool_context = f"Permission denied for weather fetch: {exec_res.error}"

        # --- Branch 3: Terminal Command ---
        elif any(k in query_lower for k in ["run", "execute", "command", "terminal", "shell", "cmd", "ping", "dir", "ls"]):
            cmd = self._extract_command(user_query)
            if cmd:
                exec_res = await tool_invocation_layer.execute_tool(
                    "run_terminal_command",
                    {"command": cmd},
                    caller_agent_name=self.metadata.name
                )
                if exec_res.status == ToolExecutionStatus.SUCCESS and isinstance(exec_res.result, dict):
                    result = exec_res.result
                    tool_context = (
                        f"TERMINAL COMMAND OUTPUT:\n"
                        f"$ {result.get('command', cmd)}\n"
                        f"Return Code: {result.get('returncode', 0)}\n"
                        f"Output:\n{result.get('output', '')}"
                    )
                    logger.info(f"SystemAgent: Executed terminal command '{cmd}' via ToolInvocationLayer.")
                elif exec_res.status == ToolExecutionStatus.PERMISSION_DENIED:
                    tool_context = f"Permission denied for terminal command execution: {exec_res.error}"

        # --- Build prompt with tool context ---
        system_prompt = (
            "You are Captain System, an elite assistant specialized in computer hardware metrics, "
            "weather reporting, and system operations. Provide clean, informative, well-formatted responses. "
            "When answering conceptual questions (e.g. 'What is RAM?'), explain the concepts clearly without using live tool metrics. "
            "When real-time system data is provided, use it directly and accurately."
        )

        messages_to_send = [SystemMessage(content=system_prompt)]
        if tool_context:
            messages_to_send.append(SystemMessage(content=f"Real-Time Tool Data:\n{tool_context}"))
        
        # Ensure active query is present as tail HumanMessage
        messages_to_send.extend(history)
        if not history or not (isinstance(history[-1], HumanMessage) and history[-1].content == user_query):
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
            logger.warning(f"SystemAgent LLM fallback ({e})")
            fallback = tool_context if tool_context else f"System info for '{user_query}': Processed successfully."
            return {
                "messages": [AIMessage(content=fallback)],
                "scratchpad": scratchpad,
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }
