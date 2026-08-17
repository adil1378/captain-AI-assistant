"""
Unit Tests for Frontend Volume 7 — Intelligence Visualization & Motion Architecture.
Verifies Part 7A (Motion Design Philosophy), Part 7B (Captain Core Motion), Part 7C (Spatial Environment), Part 7E (Interactive Feedback), Part 7F (Environmental Effects), Part 7G (Adaptive Motion), and Part 7H (Unified Motion Experience Architecture).
"""

from pathlib import Path
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_FRONTEND_BIBLE_DIR = _PROJECT_ROOT / "docs" / "frontend_engineering_bible"
_UI_WEB_DIR = _PROJECT_ROOT / "ui" / "web"


def test_frontend_volume7_specs_exist():
    """Verify Volume 7 Parts 7A, 7B, 7C, 7E, 7F, 7G, and 7H specifications exist and have approval status."""
    parts = ["7a", "7b", "7c", "7e", "7f", "7g", "7h"]
    for p in parts:
        spec_path = _FRONTEND_BIBLE_DIR / f"volume_7_part_{p}.md"
        assert spec_path.exists(), f"Spec volume_7_part_{p}.md missing"
        content = spec_path.read_text(encoding="utf-8")
        assert "APPROVED SPECIFICATION" in content, f"Spec volume_7_part_{p}.md missing approval status"


def test_motion_design_philosophy_architecture_in_js():
    """Verify Part 7A 6 Motion Categories, Hierarchy, & State Summary API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    categories = [
        "SYSTEM_MOTION", "CAPTAIN_MOTION", "INTERACTION_MOTION",
        "WORKSPACE_MOTION", "NOTIFICATION_MOTION", "BACKGROUND_MOTION"
    ]
    for cat in categories:
        assert f"{cat}: '{cat}'" in js_content, f"Missing motion category {cat} in app.js"

    assert "MOTION_CATEGORIES" in js_content
    assert "MOTION_HIERARCHY" in js_content
    assert "getMotionCategories" in js_content
    assert "getMotionHierarchy" in js_content
    assert "getMotionStateSummary" in js_content


def test_captain_core_motion_architecture_in_js():
    """Verify Part 7B 7 Core Motion Layers & Core Motion Summary API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    layers = [
        "AMBIENT_MOTION", "ATTENTION_MOTION", "LISTENING_MOTION",
        "THINKING_MOTION", "SPEAKING_MOTION", "INTERACTION_MOTION", "COMPLETION_MOTION"
    ]
    for l in layers:
        assert f"{l}: '{l}'" in js_content, f"Missing core motion layer {l} in app.js"

    assert "CORE_MOTION_LAYERS" in js_content
    assert "getCoreMotionLayers" in js_content
    assert "getCaptainCoreMotionStateSummary" in js_content


def test_spatial_interaction_and_3d_environment_architecture_in_js():
    """Verify Part 7C 6 Spatial Hierarchy Layers & Single Virtual Camera API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    layers = [
        "ENVIRONMENT_LAYER", "AMBIENT_LAYER", "CAPTAIN_LAYER",
        "WORKSPACE_LAYER", "INTERFACE_LAYER", "OVERLAY_LAYER"
    ]
    for l in layers:
        assert f"{l}: '{l}'" in js_content, f"Missing spatial layer {l} in app.js"

    assert "SPATIAL_ENVIRONMENT_LAYERS" in js_content
    assert "getSpatialEnvironmentLayers" in js_content
    assert "getSpatialEnvironmentSummary" in js_content


def test_interactive_feedback_animation_architecture_in_js():
    """Verify Part 7E 8 Interactive Feedback Types & Immediate Timing API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    types = [
        "SELECTION_FEEDBACK", "HOVER_FEEDBACK", "FOCUS_FEEDBACK", "PRESS_FEEDBACK",
        "DRAG_FEEDBACK", "DROP_FEEDBACK", "COMPLETION_FEEDBACK", "REJECTION_FEEDBACK"
    ]
    for t in types:
        assert f"{t}: '{t}'" in js_content, f"Missing interactive feedback type {t} in app.js"

    assert "INTERACTION_FEEDBACK_TYPES" in js_content
    assert "getInteractionFeedbackTypes" in js_content
    assert "triggerInteractionFeedback" in js_content
    assert "getInteractionFeedbackSummary" in js_content


def test_environmental_effects_architecture_in_js():
    """Verify Part 7F 7 Environmental Effect Categories & Quality Scaling API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    categories = [
        "AMBIENT_BACKGROUND", "PARTICLE_ENVIRONMENT", "ATMOSPHERIC_LIGHTING",
        "DEPTH_ATMOSPHERE", "ENERGY_ENVIRONMENT", "ENVIRONMENTAL_GLOW", "ENVIRONMENTAL_REFLECTION"
    ]
    for cat in categories:
        assert f"{cat}: '{cat}'" in js_content, f"Missing environmental category {cat} in app.js"

    assert "ENVIRONMENTAL_EFFECT_CATEGORIES" in js_content
    assert "getEnvironmentalEffectCategories" in js_content
    assert "getEnvironmentalEffectsSummary" in js_content


def test_adaptive_motion_and_performance_architecture_in_js():
    """Verify Part 7G 5 Quality Levels, Prioritization API, & Summary in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    levels = ["MAXIMUM", "HIGH", "BALANCED", "PERFORMANCE", "MINIMAL"]
    for lvl in levels:
        assert f"{lvl}: '{lvl}'" in js_content, f"Missing motion quality level {lvl} in app.js"

    assert "MOTION_QUALITY_LEVELS" in js_content
    assert "MOTION_PRIORITIZATION" in js_content
    assert "getMotionQualityLevels" in js_content
    assert "getMotionPrioritization" in js_content
    assert "getAdaptiveMotionSummary" in js_content


def test_unified_motion_experience_architecture_in_js():
    """Verify Part 7H 8 Motion Subsystems, Hierarchy, & Master Status API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    subsystems = [
        "CAPTAIN_CORE_MOTION", "WORKSPACE_MOTION", "INTERFACE_MOTION", "NAVIGATION_MOTION",
        "TRANSITION_MOTION", "FEEDBACK_MOTION", "ENVIRONMENTAL_MOTION", "NOTIFICATION_MOTION"
    ]
    for s in subsystems:
        assert f"{s}: '{s}'" in js_content, f"Missing motion subsystem {s} in app.js"

    assert "UNIFIED_MOTION_SUBSYSTEMS" in js_content
    assert "UNIFIED_MOTION_HIERARCHY" in js_content
    assert "getUnifiedMotionSubsystems" in js_content
    assert "getUnifiedMotionHierarchy" in js_content
    assert "getMasterMotionExperienceStatus" in js_content
