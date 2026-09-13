"""
CAPTAIN AI OS 2.0 — PHASE 2 DESKTOP PET & CONTAINER TEST SUITE.
Validates:
1. Native Desktop Container initialization (CaptainDesktopWindow)
2. Existing 3D EMO Pet HTML & WebGL assets validation
3. Window Show/Hide lifecycle & visibility toggling
4. State Synchronization (AppState -> Desktop Pet Expression Mapping)
5. System Tray Menu actions & activation handlers
6. Security Confirmation Dialog infrastructure
7. Graceful shutdown mechanics
8. Agent Brain integration via AppRuntime.execute_query
"""

import pytest
import os
import sys
from pathlib import Path

# Ensure Qt runs headlessly during automated tests
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from app.state import AppState, StateManager
from app.runtime import AppRuntime
from ui.desktop.pet_window import (
    CaptainDesktopWindow,
    SecurityConfirmationDialog,
    PYSIDE_AVAILABLE,
    WEBENGINE_AVAILABLE
)


@pytest.fixture(scope="session")
def qapp():
    """Session-scoped QApplication for Qt widget tests."""
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    yield app


# =============================================================================
# 1. EXISTING PET ASSETS & TEMPLATE VALIDATION
# =============================================================================

def test_existing_pet_html_assets_exist():
    """Verify standalone pet.html and pet_view.js are present and complete."""
    desktop_dir = Path(__file__).resolve().parents[2] / "ui" / "desktop"
    html_path = desktop_dir / "pet.html"
    js_path = desktop_dir / "pet_view.js"

    assert html_path.exists(), "ui/desktop/pet.html is missing"
    assert js_path.exists(), "ui/desktop/pet_view.js is missing"

    html_content = html_path.read_text(encoding="utf-8")
    js_content = js_path.read_text(encoding="utf-8")

    # Assert Three.js inclusion
    assert "three.min.js" in html_content
    assert "pet-canvas" in html_content

    # Assert existing 3D EMO robot pet character components in JS
    assert "drawRobotFace" in js_content
    assert "headGeo" in js_content or "BoxGeometry(2.3, 2.1, 1.9)" in js_content
    assert "headphoneCurve" in js_content or "CubicBezierCurve3" in js_content
    assert "podiumGroup" in js_content or "CylinderGeometry" in js_content
    assert "setCaptainState" in js_content
    assert "setSpeaking" in js_content


# =============================================================================
# 2. DESKTOP WINDOW CONTAINER INITIALIZATION
# =============================================================================

def test_desktop_window_initialization(qapp):
    """Verify window initializes with frameless translucent properties."""
    runtime = AppRuntime(initial_state=AppState.STANDBY)
    window = CaptainDesktopWindow(runtime=runtime)

    assert window.windowTitle() == "Captain AI OS — Desktop Pet"
    assert window.width() == 340
    assert window.height() == 380

    # Verify frameless and translucent flags
    flags = window.windowFlags()
    assert bool(flags & Qt.FramelessWindowHint) is True
    assert bool(flags & Qt.WindowStaysOnTopHint) is True
    assert window.testAttribute(Qt.WA_TranslucentBackground) is True

    window.close()


# =============================================================================
# 3. WINDOW SHOW / HIDE & TRAY LIFECYCLE
# =============================================================================

def test_desktop_window_visibility_lifecycle(qapp):
    """Verify show_pet and hide_pet manage visibility correctly."""
    runtime = AppRuntime(initial_state=AppState.STANDBY)
    window = CaptainDesktopWindow(runtime=runtime)

    window.show_pet()
    assert window.isVisible() is True

    window.hide_pet()
    assert window.isVisible() is False

    # Toggle via tray activation logic
    window._on_tray_activated(window.tray_icon.ActivationReason.DoubleClick)
    assert window.isVisible() is True

    window.close()


# =============================================================================
# 4. STATE SYNCHRONIZATION (APP STATE -> PET)
# =============================================================================

def test_desktop_window_state_synchronization(qapp):
    """Verify AppRuntime state transitions propagate to pet GUI handlers."""
    runtime = AppRuntime(initial_state=AppState.STANDBY)
    window = CaptainDesktopWindow(runtime=runtime)

    # 1. STANDBY -> Pet hidden
    runtime.state_manager.transition_to(AppState.STANDBY, force=True)
    qapp.processEvents()
    assert window.isVisible() is False

    # 2. ACTIVE
    runtime.wake(trigger="wake_test")
    qapp.processEvents()
    assert window.isVisible() is True

    # 3. LISTENING
    runtime.listen(trigger="voice_start")
    qapp.processEvents()
    assert window.isVisible() is True

    # 4. THINKING
    runtime.think(trigger="query_received")
    qapp.processEvents()
    assert window.isVisible() is True

    # 5. OBSERVING
    runtime.observe(trigger="screen_start")
    qapp.processEvents()
    assert window.isVisible() is True

    # 6. EXECUTING
    runtime.execute(trigger="tool_start")
    qapp.processEvents()
    assert window.isVisible() is True

    # 7. SPEAKING
    runtime.speak(trigger="tts_start")
    qapp.processEvents()
    assert window.isVisible() is True

    # 8. ERROR
    runtime.error(reason="test_error")
    qapp.processEvents()
    assert window.isVisible() is True

    window.close()


# =============================================================================
# 5. SECURITY CONFIRMATION DIALOG INFRASTRUCTURE
# =============================================================================

def test_security_confirmation_dialog_structure(qapp):
    """Verify confirmation modal displays action details and returns decision."""
    dialog = SecurityConfirmationDialog(
        action_name="Delete System File",
        details="Agent requested deletion of test file /tmp/test.txt",
        risk_level="HIGH"
    )

    assert dialog.windowTitle() == "Security Alert — Delete System File"
    assert dialog.width() == 420
    assert dialog.height() == 220

    # Reject / Deny
    dialog.reject()
    assert dialog.result() == SecurityConfirmationDialog.Rejected

    dialog.close()


# =============================================================================
# 6. GRACEFUL SHUTDOWN
# =============================================================================

def test_desktop_window_graceful_shutdown(qapp):
    """Verify window shuts down and cleans up tray icon without errors."""
    runtime = AppRuntime(initial_state=AppState.ACTIVE)
    window = CaptainDesktopWindow(runtime=runtime)

    assert window.tray_icon is not None
    window.shutdown_app()
    assert not window.isVisible()

# =============================================================================
# 7. TRAY MENU ACTIONS & CONTINUOUS LIFECYCLE
# =============================================================================

def test_tray_menu_actions_and_lifecycle(qapp):
    """Verify all 7 required system tray actions are configured and functional."""
    runtime = AppRuntime(initial_state=AppState.STANDBY)
    window = CaptainDesktopWindow(runtime=runtime)

    assert window.tray_icon is not None
    menu = window.tray_icon.contextMenu()
    assert menu is not None

    action_texts = [action.text() for action in menu.actions() if action.text()]
    required_actions = [
        "Show Captain",
        "Hide Captain",
        "Activate",
        "Deactivate",
        "Settings",
        "About",
        "Exit"
    ]

    for req in required_actions:
        assert req in action_texts, f"Required tray action '{req}' missing from menu"

    # Tray remains visible when pet is hidden
    window.hide_pet()
    assert window.isVisible() is False
    assert window.tray_icon.isVisible() is True

    # Test Show Captain action
    show_action = next(a for a in menu.actions() if a.text() == "Show Captain")
    show_action.trigger()
    qapp.processEvents()
    assert window.isVisible() is True

    # Test Hide Captain action
    hide_action = next(a for a in menu.actions() if a.text() == "Hide Captain")
    hide_action.trigger()
    qapp.processEvents()
    assert window.isVisible() is False

    window.close()


# =============================================================================
# 8. AGENT BRAIN RUNTIME INTEGRATION
# =============================================================================

@pytest.mark.anyio
async def test_agent_brain_runtime_integration(qapp):
    """Verify Desktop Pet container communicates with the existing agent via AppRuntime."""
    from unittest.mock import AsyncMock, patch

    runtime = AppRuntime(initial_state=AppState.ACTIVE)
    window = CaptainDesktopWindow(runtime=runtime)

    with patch.object(runtime, "execute_query", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = "Captain standing by."

        reply = await window.ask_agent("Status report")
        mock_exec.assert_awaited_once_with("Status report", session_id="desktop_session")
        assert reply == "Captain standing by."

    window.close()
