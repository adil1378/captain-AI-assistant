"""
Unit Tests for Frontend Volume 3 — Layout & Navigation Systems Implementation.
Verifies Part 3A Spatial Interface Architecture, Part 3B Workspace Architecture, Part 3C Workspace Mode System, Part 3D Window & Panel Architecture, Part 3E Navigation Architecture, Part 3F Sidebar & Dock Architecture, Part 3G Notification Architecture, and Part 3H Interface State Management.
"""

from pathlib import Path
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_FRONTEND_BIBLE_DIR = _PROJECT_ROOT / "docs" / "frontend_engineering_bible"
_UI_WEB_DIR = _PROJECT_ROOT / "ui" / "web"


def test_frontend_volume3_all_specs_exist():
    """Verify Volume 3 Parts 3A through 3H specifications exist and have approval status."""
    parts = ["3a", "3b", "3c", "3d", "3e", "3f", "3g", "3h"]
    for part in parts:
        spec_name = f"volume_3_part_{part}.md"
        spec_path = _FRONTEND_BIBLE_DIR / spec_name
        assert spec_path.exists(), f"Spec {spec_name} missing"
        content = spec_path.read_text(encoding="utf-8")
        assert "APPROVED SPECIFICATION" in content, f"Spec {spec_name} missing approval status"


def test_spatial_zones_in_html_css_js():
    """Verify 6 Spatial Zones in HTML, CSS, and JS (Part 3A)."""
    html_path = _UI_WEB_DIR / "index.html"
    css_path = _UI_WEB_DIR / "style.css"
    js_path = _UI_WEB_DIR / "app.js"

    html_content = html_path.read_text(encoding="utf-8")
    css_content = css_path.read_text(encoding="utf-8")
    js_content = js_path.read_text(encoding="utf-8")

    zones = [
        "zone-central-presence",
        "zone-navigation",
        "zone-memory",
        "zone-intelligence",
        "zone-workspace",
        "zone-utility"
    ]

    for zone in zones:
        assert zone in html_content, f"Missing zone {zone} in index.html"
        assert f".{zone}" in css_content, f"Missing .{zone} in style.css"

    assert "SPATIAL_ZONES" in js_content
    assert "getSpatialZones" in js_content
    assert "getZoneElement" in js_content


def test_workspace_architecture_in_js():
    """Verify Part 3B Workspace Contexts and Regions API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    ws_contexts = [
        "CONVERSATION", "CODING", "RESEARCH", "KNOWLEDGE",
        "AUTOMATION", "FILES", "MONITORING", "CREATIVE", "COLLABORATION"
    ]

    for ctx in ws_contexts:
        assert f"{ctx}: '{ctx}'" in js_content, f"Missing workspace context {ctx} in app.js"

    ws_regions = [
        "PRIMARY_WORK_AREA", "SUPPORTING_PANELS", "CONTEXTUAL_INFO",
        "LIVE_OUTPUTS", "TASK_PROGRESS"
    ]

    for reg in ws_regions:
        assert f"{reg}:" in js_content, f"Missing workspace region {reg} in app.js"

    assert "getWorkspaceContext" in js_content
    assert "setWorkspaceContext" in js_content
    assert "getWorkspaceRegions" in js_content


def test_workspace_mode_system_in_js():
    """Verify Part 3C 8 Core Workspace Modes and Intent Recommendation in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    modes = [
        "CONVERSATION", "CODING", "RESEARCH", "KNOWLEDGE",
        "AUTOMATION", "FILES", "SYSTEM", "CREATIVE"
    ]

    for mode in modes:
        assert f"{mode}: '{mode}'" in js_content, f"Missing workspace mode {mode} in app.js"

    assert "WORKSPACE_MODES" in js_content
    assert "getWorkspaceMode" in js_content
    assert "setWorkspaceMode" in js_content
    assert "recommendModeForQuery" in js_content


def test_window_panel_architecture_in_js():
    """Verify Part 3D 4 Component Hierarchy Types & Docking API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    components = [
        "PRIMARY_WORKSPACE", "SECONDARY_PANELS",
        "FLOATING_WINDOWS", "OVERLAY_COMPONENTS"
    ]

    for comp in components:
        assert f"{comp}:" in js_content, f"Missing component hierarchy type {comp} in app.js"

    assert "COMPONENT_HIERARCHY" in js_content
    assert "getComponentHierarchy" in js_content
    assert "toggleSecondaryPanel" in js_content
    assert "openFloatingWindow" in js_content
    assert "showOverlay" in js_content


def test_navigation_architecture_in_js():
    """Verify Part 3E 4 Navigation Hierarchy Levels & Search/Command Navigation API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    levels = ["LEVEL_1_GLOBAL", "LEVEL_2_WORKSPACE", "LEVEL_3_CONTEXT", "LEVEL_4_OBJECT"]
    for lvl in levels:
        assert f"{lvl}:" in js_content, f"Missing navigation level {lvl} in app.js"

    assert "NAVIGATION_HIERARCHY" in js_content
    assert "getNavigationHierarchy" in js_content
    assert "navigateTo" in js_content
    assert "searchNavigate" in js_content


def test_sidebar_dock_architecture_in_js():
    """Verify Part 3F Sidebar Sections, Dock Actions & Visibility API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    sections = ["CONVERSATIONS", "PROJECTS", "MEMORIES", "KNOWLEDGE", "FILES", "AGENTS", "WORKFLOWS", "FAVORITES"]
    for sec in sections:
        assert f"{sec}:" in js_content, f"Missing sidebar section {sec} in app.js"

    dock_actions = ["VOICE", "CHAT", "SEARCH", "TERMINAL", "BROWSER", "FILES", "SETTINGS", "EXTENSIONS"]
    for act in dock_actions:
        assert f"{act}:" in js_content, f"Missing dock action {act} in app.js"

    assert "getSidebarSections" in js_content
    assert "getDockActions" in js_content
    assert "setSidebarVisibility" in js_content
    assert "setDockVisibility" in js_content
    assert "triggerDockAction" in js_content


def test_notification_alert_architecture_in_js():
    """Verify Part 3G 4 Priority Levels, Lifecycle & Dispatch API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    notif_levels = ["LEVEL_1_INFORMATIONAL", "LEVEL_2_ACTIONABLE", "LEVEL_3_WARNING", "LEVEL_4_CRITICAL"]
    for lvl in notif_levels:
        assert f"{lvl}:" in js_content, f"Missing notification level {lvl} in app.js"

    assert "NOTIFICATION_LEVELS" in js_content
    assert "getNotificationLevels" in js_content
    assert "dispatchNotification" in js_content
    assert "acknowledgeNotification" in js_content
    assert "getNotificationHistory" in js_content


def test_interface_state_management_in_js():
    """Verify Part 3H 8 Global State Categories & Single Source of Truth API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    categories = [
        "SYSTEM_STATE", "CAPTAIN_STATE", "WORKSPACE_STATE", "USER_STATE",
        "SESSION_STATE", "NAVIGATION_STATE", "NOTIFICATION_STATE", "PANEL_STATE"
    ]

    for cat in categories:
        assert f"{cat}:" in js_content, f"Missing global state category {cat} in app.js"

    assert "GLOBAL_STATE_CATEGORIES" in js_content
    assert "getGlobalState" in js_content
    assert "serializeState" in js_content
    assert "restoreState" in js_content
