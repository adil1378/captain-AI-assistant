"""
Unit Tests for Frontend Volume 4 — Intelligence & Memory Center Architecture.
Verifies Part 4A Captain Memory Center Architecture, Part 4B Memory Timeline Architecture, Part 4C Memory Search Architecture, Part 4D Memory Relationship Graph Architecture, Part 4E Memory Visualization Architecture, Part 4F Memory Workspace Integration, and Part 4H Memory Experience Architecture.
"""

from pathlib import Path
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_FRONTEND_BIBLE_DIR = _PROJECT_ROOT / "docs" / "frontend_engineering_bible"
_UI_WEB_DIR = _PROJECT_ROOT / "ui" / "web"


def test_frontend_volume4_all_specs_exist():
    """Verify Volume 4 Parts 4A, 4B, 4C, 4D, 4E, 4F, and 4H specifications exist and have approval status."""
    parts = ["4a", "4b", "4c", "4d", "4e", "4f", "4h"]
    for part in parts:
        spec_name = f"volume_4_part_{part}.md"
        spec_path = _FRONTEND_BIBLE_DIR / spec_name
        assert spec_path.exists(), f"Spec {spec_name} missing"
        content = spec_path.read_text(encoding="utf-8")
        assert "APPROVED SPECIFICATION" in content, f"Spec {spec_name} missing approval status"


def test_memory_center_architecture_in_js():
    """Verify Part 4A 6 Core Memory Categories & Memory Store API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    categories = ["CONVERSATION", "PROJECT", "KNOWLEDGE", "PERSONAL", "WORKFLOW", "RESOURCE"]
    for cat in categories:
        assert f"{cat}: '{cat}'" in js_content, f"Missing memory category {cat} in app.js"

    assert "MEMORY_CATEGORIES" in js_content
    assert "getMemoryCategories" in js_content
    assert "addMemoryEntry" in js_content
    assert "searchMemory" in js_content
    assert "deleteMemoryEntry" in js_content


def test_memory_timeline_architecture_in_js():
    """Verify Part 4B 6 Time Scales & Timeline Retrieval API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    scales = ["TODAY", "YESTERDAY", "THIS_WEEK", "THIS_MONTH", "THIS_YEAR", "HISTORICAL"]
    for sc in scales:
        assert f"{sc}: '{sc}'" in js_content, f"Missing timeline scale {sc} in app.js"

    assert "TIMELINE_SCALES" in js_content
    assert "getTimelineScales" in js_content
    assert "getTimeline" in js_content
    assert "restoreMemoryContext" in js_content


def test_memory_search_architecture_in_js():
    """Verify Part 4C 4 Conceptual Search Methods & Execution API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    methods = ["NATURAL_LANGUAGE", "KEYWORD", "CONTEXT", "RELATIONSHIP"]
    for m in methods:
        assert f"{m}: '{m}'" in js_content, f"Missing search method {m} in app.js"

    assert "SEARCH_METHODS" in js_content
    assert "getSearchMethods" in js_content
    assert "executeMemorySearch" in js_content


def test_memory_relationship_graph_architecture_in_js():
    """Verify Part 4D 6 Relationship Categories & Subgraph API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    rel_types = ["CONVERSATION", "PROJECT", "KNOWLEDGE", "FILE", "WORKFLOW", "DECISION"]
    for rel in rel_types:
        assert f"{rel}: '{rel}'" in js_content, f"Missing relationship type {rel} in app.js"

    assert "RELATIONSHIP_TYPES" in js_content
    assert "getRelationshipTypes" in js_content
    assert "addMemoryRelationship" in js_content
    assert "getMemoryGraph" in js_content


def test_memory_visualization_architecture_in_js():
    """Verify Part 4E 6 Visualization Layers & Perspective API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    layers = ["TIMELINE", "RELATIONSHIP", "PROJECT", "KNOWLEDGE", "CONVERSATION", "RESOURCE"]
    for l in layers:
        assert f"{l}: '{l}'" in js_content, f"Missing visualization layer {l} in app.js"

    assert "VISUALIZATION_LAYERS" in js_content
    assert "getVisualizationLayers" in js_content
    assert "setVisualizationLayer" in js_content
    assert "renderMemoryPerspective" in js_content


def test_memory_workspace_integration_in_js():
    """Verify Part 4F Workspace Memory Binding & Context Retrieval API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    assert "bindMemoryToWorkspace" in js_content
    assert "getWorkspaceMemoryContext" in js_content
    assert "workspaceMemoryBindings" in js_content


def test_memory_experience_architecture_in_js():
    """Verify Part 4H Natural Recall & Uncertainty Threshold API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    assert "getNaturalMemoryRecall" in js_content
    assert "memoryRecallConfidenceThreshold" in js_content
