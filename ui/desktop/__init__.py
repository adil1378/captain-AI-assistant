"""
Captain AI OS 2.0 Desktop UI Package.
Provides the native PySide6 Desktop Container for the existing 3D EMO Robot Pet.
"""

from ui.desktop.pet_window import (
    CaptainDesktopWindow,
    SecurityConfirmationDialog,
    launch_desktop_pet,
)

__all__ = [
    "CaptainDesktopWindow",
    "SecurityConfirmationDialog",
    "launch_desktop_pet",
]
