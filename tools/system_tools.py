import sys
import subprocess
import psutil
from typing import Dict, Any
from loguru import logger


def get_system_metrics() -> Dict[str, Any]:
    """Retrieve real-time system hardware performance metrics (CPU, RAM, Disk, Battery)."""
    cpu_percent = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()

    disk_path = 'C:\\' if sys.platform == 'win32' else '/'
    try:
        disk = psutil.disk_usage(disk_path)
        disk_info = {
            "total_gb": round(disk.total / (1024 ** 3), 2),
            "used_gb": round(disk.used / (1024 ** 3), 2),
            "free_gb": round(disk.free / (1024 ** 3), 2),
            "percent": disk.percent
        }
    except Exception:
        disk_info = {"total_gb": 0, "used_gb": 0, "free_gb": 0, "percent": 0}

    battery = psutil.sensors_battery()
    battery_info = {
        "percent": battery.percent if battery else 100,
        "power_plugged": battery.power_plugged if battery else True
    }

    ram_used = round(memory.used / (1024 ** 3), 2)
    ram_total = round(memory.total / (1024 ** 3), 2)
    ram_avail = round(memory.available / (1024 ** 3), 2)

    return {
        "status": "success",
        "cpu_percent": cpu_percent,
        "cpu_usage_percent": cpu_percent,
        "memory_percent": memory.percent,
        "memory_used_gb": ram_used,
        "memory_total_gb": ram_total,
        "memory_available_gb": ram_avail,
        "ram": {
            "total_gb": ram_total,
            "used_gb": ram_used,
            "available_gb": ram_avail,
            "percent": memory.percent
        },
        "disk": disk_info,
        "battery": battery_info
    }


def run_terminal_command(command: str, timeout: int = 30) -> Dict[str, Any]:
    """Execute a shell/terminal command safely with timeout enforcement."""
    try:
        logger.info(f"Executing terminal command: {command}")
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            "status": "success",
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output": result.stdout if result.returncode == 0 else result.stderr
        }
    except subprocess.TimeoutExpired:
        logger.error(f"Terminal command timed out after {timeout}s: {command}")
        return {"status": "error", "command": command, "error": f"Command timed out after {timeout} seconds."}
    except Exception as e:
        logger.error(f"Terminal command execution error: {e}")
        return {"status": "error", "command": command, "error": str(e)}
