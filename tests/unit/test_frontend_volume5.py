"""
Unit Tests for Frontend Volume 5 — Intelligence Center & System Architecture.
Verifies Parts 5A (Intelligence Center), 5B (Reasoning Visualization), 5C (Multi-Agent Activity), 5D (Task Execution), 5E (System Awareness), 5F (Human Perception), and 5G (Intelligence Event Stream).
"""

from pathlib import Path
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_FRONTEND_BIBLE_DIR = _PROJECT_ROOT / "docs" / "frontend_engineering_bible"
_UI_WEB_DIR = _PROJECT_ROOT / "ui" / "web"


def test_frontend_volume5_specs_exist():
    """Verify Volume 5 Parts 5A, 5B, 5C, 5D, 5E, 5F, and 5G specifications exist and have approval status."""
    parts = ["5a", "5b", "5c", "5d", "5e", "5f", "5g"]
    for p in parts:
        spec_path = _FRONTEND_BIBLE_DIR / f"volume_5_part_{p}.md"
        assert spec_path.exists(), f"Spec volume_5_part_{p}.md missing"
        content = spec_path.read_text(encoding="utf-8")
        assert "APPROVED SPECIFICATION" in content, f"Spec volume_5_part_{p}.md missing approval status"


def test_intelligence_center_architecture_in_js():
    """Verify Part 5A 6 Intelligence Categories & Progressive Detail API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    categories = ["REASONING", "TASK", "AGENT", "KNOWLEDGE", "MEMORY", "SYSTEM"]
    for cat in categories:
        assert f"{cat}: '{cat}'" in js_content, f"Missing intelligence category {cat} in app.js"

    assert "INTELLIGENCE_CATEGORIES" in js_content
    assert "getIntelligenceCategories" in js_content
    assert "logIntelligenceActivity" in js_content
    assert "getActiveIntelligenceSummary" in js_content


def test_reasoning_visualization_architecture_in_js():
    """Verify Part 5B 6 Reasoning Stages & Visualization State API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    stages = ["UNDERSTANDING", "PLANNING", "GATHERING_INFORMATION", "PROCESSING", "VERIFYING", "RESPONDING"]
    for st in stages:
        assert f"{st}: '{st}'" in js_content, f"Missing reasoning stage {st} in app.js"

    assert "REASONING_STAGES" in js_content
    assert "getReasoningStages" in js_content
    assert "setReasoningStage" in js_content
    assert "getReasoningVisualizationState" in js_content


def test_multi_agent_visualization_architecture_in_js():
    """Verify Part 5C 6 Agent States & Swarm Coordination API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    states = ["WAITING", "ASSIGNED", "WORKING", "WAITING_FOR_DEPENDENCY", "COMPLETED", "UNAVAILABLE"]
    for st in states:
        assert f"{st}: '{st}'" in js_content, f"Missing agent state {st} in app.js"

    assert "AGENT_STATES" in js_content
    assert "getAgentStates" in js_content
    assert "registerSubagent" in js_content
    assert "setAgentState" in js_content
    assert "getAgentSwarmStatus" in js_content


def test_task_execution_visualization_architecture_in_js():
    """Verify Part 5D 7 Task Lifecycle Stages & Task Registry API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    stages = ["QUEUED", "INITIALIZING", "EXECUTING", "WAITING", "VERIFYING", "COMPLETED", "INTERRUPTED"]
    for st in stages:
        assert f"{st}: '{st}'" in js_content, f"Missing task lifecycle stage {st} in app.js"

    assert "TASK_LIFECYCLE" in js_content
    assert "getTaskLifecycleStages" in js_content
    assert "createTaskEntry" in js_content
    assert "updateTaskLifecycle" in js_content
    assert "getTaskRegistrySummary" in js_content


def test_system_awareness_dashboard_architecture_in_js():
    """Verify Part 5E 6 Awareness Categories & System Health Overview API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    categories = ["CAPTAIN_STATUS", "AI_RUNTIME", "DEVICE_RESOURCES", "CONNECTIVITY", "SENSORS", "BACKGROUND_SERVICES"]
    for cat in categories:
        assert f"{cat}: '{cat}'" in js_content, f"Missing awareness category {cat} in app.js"

    assert "AWARENESS_CATEGORIES" in js_content
    assert "getAwarenessCategories" in js_content
    assert "setAwarenessCategoryStatus" in js_content
    assert "getSystemHealthOverview" in js_content


def test_human_perception_visualization_architecture_in_js():
    """Verify Part 5F 5 Perception Categories & Capability Summary API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    categories = ["VOICE_PERCEPTION", "FACE_AWARENESS", "GESTURE_AWARENESS", "PRESENCE_AWARENESS", "ATTENTION_AWARENESS"]
    for cat in categories:
        assert f"{cat}: '{cat}'" in js_content, f"Missing perception category {cat} in app.js"

    assert "PERCEPTION_CATEGORIES" in js_content
    assert "getPerceptionCategories" in js_content
    assert "setPerceptionCategoryStatus" in js_content
    assert "getPerceptionCapabilitySummary" in js_content


def test_intelligence_event_stream_architecture_in_js():
    """Verify Part 5G 7 Event Categories & Event Stream Filter API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    categories = [
        "CONVERSATION_EVENTS", "TASK_EVENTS", "WORKSPACE_EVENTS",
        "MEMORY_EVENTS", "KNOWLEDGE_EVENTS", "AGENT_EVENTS", "SYSTEM_EVENTS"
    ]
    for cat in categories:
        assert f"{cat}: '{cat}'" in js_content, f"Missing event category {cat} in app.js"

    assert "EVENT_CATEGORIES" in js_content
    assert "getEventCategories" in js_content
    assert "emitIntelligenceEvent" in js_content
    assert "getIntelligenceEventStream" in js_content
