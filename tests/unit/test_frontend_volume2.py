"""
Unit Tests for Frontend Volume 2 — Captain Core Implementation.
Verifies Part 2A Architecture, Part 2B Layer System, Part 2C State Machine, Part 2D Lighting, Part 2E Audio-Reactive, Part 2F Interaction, Part 2G Rendering Rules & Part 2H Performance Rules.
"""

from pathlib import Path
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_FRONTEND_BIBLE_DIR = _PROJECT_ROOT / "docs" / "frontend_engineering_bible"
_UI_WEB_DIR = _PROJECT_ROOT / "ui" / "web"


def test_frontend_volume2_all_specs_exist():
    """Verify Volume 2 Parts 2A through 2H specifications exist and have approval status."""
    parts = ["2a", "2b", "2c", "2d", "2e", "2f", "2g", "2h"]
    for part in parts:
        spec_name = f"volume_2_part_{part}.md"
        spec_path = _FRONTEND_BIBLE_DIR / spec_name
        assert spec_path.exists(), f"Spec {spec_name} missing"
        content = spec_path.read_text(encoding="utf-8")
        assert "APPROVED SPECIFICATION" in content, f"Spec {spec_name} missing approval status"


def test_captain_core_8_layers_html_css_js():
    """Verify 8-layer Captain Core Architecture in HTML, CSS, and JS."""
    html_path = _UI_WEB_DIR / "index.html"
    css_path = _UI_WEB_DIR / "style.css"
    js_path = _UI_WEB_DIR / "app.js"

    html_content = html_path.read_text(encoding="utf-8")
    css_content = css_path.read_text(encoding="utf-8")
    js_content = js_path.read_text(encoding="utf-8")

    layers = [
        "layer-1-neural-core",
        "layer-2-energy-shell",
        "layer-3-orbital-structure",
        "layer-4-ambient-field",
        "layer-5-communication",
        "layer-6-intelligence",
        "layer-7-interaction",
        "layer-8-environmental"
    ]

    for layer in layers:
        assert layer in html_content, f"Missing {layer} in index.html"
        assert f".{layer}" in css_content, f"Missing .{layer} in style.css"

    assert "LAYERS" in js_content
    assert "getLayerVisibility" in js_content
    assert "setLayerVisibility" in js_content


def test_captain_core_10_operational_states():
    """Verify 10 Operational States & Priority Rules in app.js (Part 2C)."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    states = [
        "IDLE", "ATTENTION", "LISTENING", "UNDERSTANDING",
        "THINKING", "EXECUTING", "RESPONDING", "WAITING",
        "NOTIFICATION", "RECOVERY"
    ]

    for state in states:
        assert f"{state}: '{state}'" in js_content, f"Missing state {state} in app.js"

    assert "STATE_PRIORITIES" in js_content
    assert "transitionTo" in js_content
    assert "getStateHistory" in js_content


def test_captain_core_lighting_profiles():
    """Verify Part 2D State-Aware Lighting Profiles & Tokens in style.css."""
    css_path = _UI_WEB_DIR / "style.css"
    css_content = css_path.read_text(encoding="utf-8")

    assert "--glow-thinking:" in css_content
    assert "--glow-executing:" in css_content
    assert "--glow-notification:" in css_content
    assert "--glow-recovery:" in css_content

    for state_cls in [
        "state-idle", "state-attention", "state-listening", "state-understanding",
        "state-thinking", "state-executing", "state-responding", "state-waiting",
        "state-notification", "state-recovery"
    ]:
        assert f".orb-wrapper.{state_cls}" in css_content, f"Missing lighting profile for {state_cls}"


def test_captain_core_7_communication_phases():
    """Verify Part 2E 7 Communication Phases API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    phases = [
        "USER_SPEAKING_START", "USER_SPEAKING_ACTIVE", "USER_PAUSE",
        "USER_SPEAKING_END", "CAPTAIN_RESPONDING_START",
        "CAPTAIN_RESPONDING_ACTIVE", "CAPTAIN_RESPONDING_END"
    ]

    for phase in phases:
        assert f"{phase}: '{phase}'" in js_content, f"Missing communication phase {phase} in app.js"

    assert "setCommunicationPhase" in js_content
    assert "handleSilence" in js_content


def test_captain_core_rendering_and_performance_rules():
    """Verify Part 2G & 2H Quality Scaling Profiles, Performance Telemetry & Throttling in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    profiles = ["HIGH", "BALANCED", "LOW_POWER"]
    for profile in profiles:
        assert f"{profile}: '{profile}'" in js_content, f"Missing quality profile {profile} in app.js"

    assert "getQualityProfile" in js_content
    assert "setQualityProfile" in js_content
    assert "setPageVisibility" in js_content
    assert "getPerformanceMetrics" in js_content
    assert "reportFrameFired" in js_content
