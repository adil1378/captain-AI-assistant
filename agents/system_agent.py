from typing import Dict, Any
from langchain_core.messages import AIMessage
from agents.state import AgentState
from tools.system_tools import get_system_metrics, run_terminal_command
from tools.weather import get_live_weather
from core.llm_factory import get_llm
from loguru import logger


def system_agent_node(state: AgentState) -> Dict[str, Any]:
    """SystemAgent node: Hardware metrics, safe terminal command execution, and live weather."""
    logger.info("--- [Node: SystemAgent] Processing system/weather task ---")
    user_query = state.get("user_query", "").lower()
    scratchpad = state.get("scratchpad", {})

    output_str = ""

    if "weather" in user_query:
        # Extract city or default to New York
        words = user_query.split()
        city = "New York"
        if "in" in words:
            idx = words.index("in")
            if idx + 1 < len(words):
                city = words[idx + 1].strip("?.!")
        
        w_res = get_live_weather(city)
        if w_res.get("status") == "success":
            output_str = f"Live Weather in {w_res['city']}, {w_res['country']}:\nTemperature: {w_res['temperature_celsius']}°C | Windspeed: {w_res['windspeed_kmh']} km/h"
        else:
            output_str = f"Weather lookup error: {w_res.get('error')}"

    elif any(k in user_query for k in ["cpu", "ram", "memory", "hardware", "system", "metrics", "stats"]):
        m_res = get_system_metrics()
        if m_res.get("status") == "success":
            output_str = f"System Hardware Metrics:\nCPU Usage: {m_res['cpu_usage_percent']}%\nMemory (RAM): {m_res['memory_used_gb']} GB / {m_res['memory_total_gb']} GB ({m_res['memory_percent']}%)\nDisk: {m_res['disk_used_gb']} GB / {m_res['disk_total_gb']} GB ({m_res['disk_percent']}%)\nBattery: {m_res['battery_percent']}%"
        else:
            output_str = f"Failed to retrieve hardware metrics: {m_res.get('error')}"

    elif "run" in user_query or "command" in user_query or "terminal" in user_query:
        # Simple extraction or run command
        cmd_str = scratchpad.get("command_to_run")
        if not cmd_str:
            cmd_str = user_query.replace("run command", "").replace("run", "").strip()
        
        c_res = run_terminal_command(cmd_str)
        output_str = f"Terminal Execution ({c_res['status']}):\nSTDOUT: {c_res.get('stdout', '')}\nSTDERR: {c_res.get('stderr', '')}"
    else:
        m_res = get_system_metrics()
        output_str = f"System Overview: CPU {m_res.get('cpu_usage_percent')}% | RAM {m_res.get('memory_percent')}%"

    return {
        "messages": [AIMessage(content=f"[SystemAgent]: {output_str}")],
        "scratchpad": scratchpad,
        "current_agent": "system_agent"
    }
