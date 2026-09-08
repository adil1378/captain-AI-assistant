"""
Captain AI OS — Backend Configuration Re-Export Module.
Maintains backward compatibility with src.backend.config callers by re-exporting
the centralized Pydantic Settings instance from root config.py.
"""

from config import Settings, settings

__all__ = ["Settings", "settings"]
