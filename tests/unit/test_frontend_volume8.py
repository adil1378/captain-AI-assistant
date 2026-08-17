"""
Unit Tests for Frontend Volume 8 — Design System & Visual Component Architecture.
Verifies Part 8A (Design System Foundation), Part 8B (Color & Visual Identity), Part 8C (Typography), Part 8D (Component Design), Part 8E (Layout & Spatial Grid), Part 8F (Iconography & Visual Language), Part 8G (Accessibility & Inclusive Design), and Part 8H (Unified Design Experience).
"""

from pathlib import Path
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_FRONTEND_BIBLE_DIR = _PROJECT_ROOT / "docs" / "frontend_engineering_bible"
_UI_WEB_DIR = _PROJECT_ROOT / "ui" / "web"


def test_frontend_volume8_specs_exist():
    """Verify Volume 8 Parts 8A, 8B, 8C, 8D, 8E, 8F, 8G, and 8H specifications exist and have approval status."""
    parts = ["8a", "8b", "8c", "8d", "8e", "8f", "8g", "8h"]
    for p in parts:
        spec_path = _FRONTEND_BIBLE_DIR / f"volume_8_part_{p}.md"
        assert spec_path.exists(), f"Spec volume_8_part_{p}.md missing"
        content = spec_path.read_text(encoding="utf-8")
        assert "APPROVED SPECIFICATION" in content, f"Spec volume_8_part_{p}.md missing approval status"


def test_design_system_foundation_architecture_in_js():
    """Verify Part 8A 6 Design System Pillars, Identity Traits, & Summary API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    pillars = ["FOUNDATION", "LAYOUT", "COMPONENTS", "INTERACTION", "MOTION", "ACCESSIBILITY"]
    for p in pillars:
        assert f"{p}: '{p}'" in js_content, f"Missing design pillar {p} in app.js"

    identity_traits = [
        "CALM_SOPHISTICATION", "SPATIAL_DEPTH", "PRECISION",
        "CLARITY", "TECHNOLOGICAL_ELEGANCE"
    ]
    for trait in identity_traits:
        assert f"{trait}: '{trait}'" in js_content, f"Missing identity trait {trait} in app.js"

    assert "DESIGN_SYSTEM_FOUNDATION_PILLARS" in js_content
    assert "DESIGN_IDENTITY_TRAITS" in js_content
    assert "getDesignSystemFoundationPillars" in js_content
    assert "getDesignIdentityTraits" in js_content
    assert "getDesignSystemFoundationSummary" in js_content


def test_color_and_visual_identity_architecture_in_js():
    """Verify Part 8B 7 Color Hierarchy Categories, 8 State Mappings, & Summary API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    categories = [
        "FOUNDATION_COLORS", "SURFACE_COLORS", "PRIMARY_ACCENT_COLORS",
        "SECONDARY_ACCENT_COLORS", "SEMANTIC_COLORS", "INTERACTIVE_COLORS", "AMBIENT_COLORS"
    ]
    for cat in categories:
        assert f"{cat}: '{cat}'" in js_content, f"Missing color category {cat} in app.js"

    states = [
        "READY", "ACTIVE", "PROCESSING", "COMPLETED",
        "WAITING", "WARNING", "ERROR", "DISABLED"
    ]
    for st in states:
        assert f"{st}: '{st}'" in js_content, f"Missing color state {st} in app.js"

    assert "COLOR_HIERARCHY_CATEGORIES" in js_content
    assert "COLOR_STATE_MAPPINGS" in js_content
    assert "getColorHierarchyCategories" in js_content
    assert "getColorStateMappings" in js_content
    assert "getColorSystemSummary" in js_content


def test_typography_and_information_hierarchy_architecture_in_js():
    """Verify Part 8C 8 Typography Hierarchy Levels & Summary API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    levels = [
        "DISPLAY", "PRIMARY_HEADINGS", "SECONDARY_HEADINGS", "SECTION_LABELS",
        "BODY_CONTENT", "SUPPORTING_CONTENT", "METADATA", "STATUS_INDICATORS"
    ]
    for lvl in levels:
        assert f"{lvl}: '{lvl}'" in js_content, f"Missing typography level {lvl} in app.js"

    assert "TYPOGRAPHY_HIERARCHY_LEVELS" in js_content
    assert "getTypographyHierarchyLevels" in js_content
    assert "getTypographySystemSummary" in js_content


def test_component_design_architecture_in_js():
    """Verify Part 8D 7 Component Categories & Summary API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    categories = [
        "NAVIGATION_COMPONENTS", "INPUT_COMPONENTS", "DISPLAY_COMPONENTS",
        "WORKSPACE_COMPONENTS", "FEEDBACK_COMPONENTS", "OVERLAY_COMPONENTS", "UTILITY_COMPONENTS"
    ]
    for cat in categories:
        assert f"{cat}: '{cat}'" in js_content, f"Missing component category {cat} in app.js"

    assert "COMPONENT_DESIGN_CATEGORIES" in js_content
    assert "getComponentDesignCategories" in js_content
    assert "getComponentDesignSummary" in js_content


def test_layout_and_spatial_grid_architecture_in_js():
    """Verify Part 8E 5 Spatial Layout Zones & Summary API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    zones = [
        "CAPTAIN_ZONE", "NAVIGATION_ZONE", "WORKSPACE_ZONE",
        "INFORMATION_ZONE", "UTILITY_ZONE"
    ]
    for z in zones:
        assert f"{z}: '{z}'" in js_content, f"Missing spatial zone {z} in app.js"

    assert "SPATIAL_LAYOUT_ZONES" in js_content
    assert "getSpatialLayoutZones" in js_content
    assert "getSpatialLayoutSummary" in js_content


def test_iconography_and_visual_language_architecture_in_js():
    """Verify Part 8F 7 Visual Language Categories & Summary API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    categories = [
        "NAVIGATION_ICONS", "ACTION_ICONS", "SYSTEM_ICONS", "WORKSPACE_ICONS",
        "STATUS_INDICATORS", "CAPTAIN_SYMBOLS", "INFORMATIONAL_GRAPHICS"
    ]
    for cat in categories:
        assert f"{cat}: '{cat}'" in js_content, f"Missing visual language category {cat} in app.js"

    assert "VISUAL_LANGUAGE_CATEGORIES" in js_content
    assert "getVisualLanguageCategories" in js_content
    assert "getIconographySummary" in js_content


def test_accessibility_and_inclusive_design_architecture_in_js():
    """Verify Part 8G 6 Accessibility Categories & Summary API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    categories = [
        "VISUAL_ACCESSIBILITY", "MOTOR_ACCESSIBILITY", "AUDITORY_ACCESSIBILITY",
        "COGNITIVE_ACCESSIBILITY", "INTERACTION_ACCESSIBILITY", "ENVIRONMENTAL_ACCESSIBILITY"
    ]
    for cat in categories:
        assert f"{cat}: '{cat}'" in js_content, f"Missing accessibility category {cat} in app.js"

    assert "ACCESSIBILITY_CATEGORIES" in js_content
    assert "getAccessibilityCategories" in js_content
    assert "getAccessibilitySystemSummary" in js_content


def test_unified_design_experience_architecture_in_js():
    """Verify Part 8H 8 Integrated Design Subsystems, 7 Visual Hierarchy Levels, & Master API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    subsystems = [
        "LAYOUT_SYSTEM", "COLOR_SYSTEM", "TYPOGRAPHY_SYSTEM", "COMPONENT_SYSTEM",
        "MOTION_SYSTEM", "SPATIAL_SYSTEM", "VISUAL_LANGUAGE", "ACCESSIBILITY_SYSTEM"
    ]
    for sub in subsystems:
        assert f"{sub}: '{sub}'" in js_content, f"Missing design subsystem {sub} in app.js"

    hierarchy_levels = [
        "CAPTAIN_CORE", "ACTIVE_WORKSPACE", "USER_INTERACTION",
        "PRIMARY_INFORMATION", "SUPPORTING_INFORMATION", "UTILITIES", "ENVIRONMENTAL_EFFECTS"
    ]
    for lvl in hierarchy_levels:
        assert f"'{lvl}'" in js_content, f"Missing hierarchy level {lvl} in app.js"

    assert "UNIFIED_DESIGN_SUBSYSTEMS" in js_content
    assert "UNIFIED_VISUAL_HIERARCHY" in js_content
    assert "getUnifiedDesignSubsystems" in js_content
    assert "getUnifiedVisualHierarchy" in js_content
    assert "getMasterDesignExperienceStatus" in js_content
