"""
Captain AI OS - Cross-Platform Operating System Abstraction Layer (Volume 8 Part 8F)
Provides unified interfaces for platform detection, process control, file system, hardware metrics,
and window operations across Windows, Linux, and macOS.
"""

import sys
import os
import platform
import psutil
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class OSPlatform(BaseModel):
    os_name: str
    os_version: str
    architecture: str
    processor: str
    is_windows: bool
    is_linux: bool
    is_mac: bool


class HardwareSnapshot(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    cpu_cores: int
    total_memory_gb: float


class OperatingSystemAbstractionLayer:
    """Standardized Hardware & OS Abstraction Layer (OSAL)."""

    @staticmethod
    def get_platform_info() -> OSPlatform:
        """Detects current operating system and hardware architecture details."""
        sys_name = platform.system()
        return OSPlatform(
            os_name=sys_name,
            os_version=platform.version(),
            architecture=platform.machine(),
            processor=platform.processor() or "Unknown",
            is_windows=(sys_name == "Windows"),
            is_linux=(sys_name == "Linux"),
            is_mac=(sys_name == "Darwin")
        )

    @staticmethod
    def get_hardware_metrics() -> HardwareSnapshot:
        """Fetches live hardware telemetry for CPU, RAM, and Storage."""
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return HardwareSnapshot(
            cpu_percent=psutil.cpu_percent(interval=None),
            memory_percent=mem.percent,
            disk_percent=disk.percent,
            cpu_cores=os.cpu_count() or 1,
            total_memory_gb=round(mem.total / (1024 ** 3), 2)
        )

    @staticmethod
    def list_running_processes(limit: int = 50) -> List[Dict[str, Any]]:
        """Returns a unified list of active OS processes."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
                if len(processes) >= limit:
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes
