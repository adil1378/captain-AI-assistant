"""
Unit Tests for Frontend Volume 6 — Voice & Multimodal Experience Architecture.
Verifies Part 6A (Voice Experience), Part 6B (Voice State & Feedback), Part 6C (Conversation Flow), Part 6D (Proactive Interaction), Part 6E (Voice Personality & Communication), Part 6F (Multimodal Interaction), Part 6G (Conversation Memory & Continuity), and Part 6H (Voice & Conversation Experience).
"""

from pathlib import Path
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_FRONTEND_BIBLE_DIR = _PROJECT_ROOT / "docs" / "frontend_engineering_bible"
_UI_WEB_DIR = _PROJECT_ROOT / "ui" / "web"


def test_frontend_volume6_specs_exist():
    """Verify Volume 6 Parts 6A, 6B, 6C, 6D, 6E, 6F, 6G, and 6H specifications exist and have approval status."""
    parts = ["6a", "6b", "6c", "6d", "6e", "6f", "6g", "6h"]
    for p in parts:
        spec_path = _FRONTEND_BIBLE_DIR / f"volume_6_part_{p}.md"
        assert spec_path.exists(), f"Spec volume_6_part_{p}.md missing"
        content = spec_path.read_text(encoding="utf-8")
        assert "APPROVED SPECIFICATION" in content, f"Spec volume_6_part_{p}.md missing approval status"


def test_voice_experience_architecture_in_js():
    """Verify Part 6A 6 Voice Presence States & Conversational Experience API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    states = ["READY", "LISTENING", "UNDERSTANDING", "PROCESSING", "RESPONDING", "WAITING"]
    for st in states:
        assert f"{st}: '{st}'" in js_content, f"Missing voice presence state {st} in app.js"

    assert "VOICE_PRESENCE_STATES" in js_content
    assert "getVoicePresenceStates" in js_content
    assert "setVoicePresenceState" in js_content
    assert "getVoiceExperienceStatus" in js_content


def test_voice_state_and_feedback_architecture_in_js():
    """Verify Part 6B 8 Voice Feedback States & Orb Integration API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    states = ["READY", "LISTENING", "UNDERSTANDING", "THINKING", "SPEAKING", "INTERRUPTED", "PAUSED", "UNAVAILABLE"]
    for st in states:
        assert f"{st}: '{st}'" in js_content, f"Missing voice feedback state {st} in app.js"

    assert "VOICE_FEEDBACK_STATES" in js_content
    assert "getVoiceFeedbackStates" in js_content
    assert "setVoiceFeedbackState" in js_content
    assert "getVoiceFeedbackStateSummary" in js_content


def test_conversation_flow_architecture_in_js():
    """Verify Part 6C 6 Conversation Stages & Flow Summary API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    stages = ["GREETING", "UNDERSTANDING", "DISCUSSION", "CLARIFICATION", "RESOLUTION", "CONTINUATION"]
    for st in stages:
        assert f"{st}: '{st}'" in js_content, f"Missing conversation stage {st} in app.js"

    assert "CONVERSATION_STAGES" in js_content
    assert "getConversationStages" in js_content
    assert "setConversationStage" in js_content
    assert "getConversationFlowSummary" in js_content


def test_proactive_interaction_architecture_in_js():
    """Verify Part 6D 6 Proactive Assistance Types & Non-Intrusive Suggestion API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    types = [
        "CONTEXT_REMINDERS", "MEMORY_SUGGESTIONS", "KNOWLEDGE_RECOMMENDATIONS",
        "WORKFLOW_ASSISTANCE", "SYSTEM_AWARENESS", "COLLABORATION_SUPPORT"
    ]
    for t in types:
        assert f"{t}: '{t}'" in js_content, f"Missing proactive assistance type {t} in app.js"

    assert "PROACTIVE_ASSISTANCE_TYPES" in js_content
    assert "getProactiveAssistanceTypes" in js_content
    assert "triggerProactiveSuggestion" in js_content
    assert "dismissProactiveSuggestion" in js_content
    assert "getProactiveSuggestionsSummary" in js_content


def test_voice_personality_and_communication_architecture_in_js():
    """Verify Part 6E 6 Identity Traits & Response Formatting API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    traits = ["KNOWLEDGEABLE", "RELIABLE", "TRANSPARENT", "RESPECTFUL", "PATIENT", "FOCUSED"]
    for tr in traits:
        assert f"{tr}: '{tr}'" in js_content, f"Missing identity trait {tr} in app.js"

    assert "COMMUNICATION_IDENTITY_TRAITS" in js_content
    assert "getCommunicationIdentityTraits" in js_content
    assert "formatResponseWithPersonality" in js_content
    assert "getCommunicationPersonalitySummary" in js_content


def test_multimodal_interaction_architecture_in_js():
    """Verify Part 6F 7 Supported Interaction Methods & Cross-Modal Continuity API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    methods = ["VOICE", "TEXT", "TOUCH", "KEYBOARD", "MOUSE_POINTER", "HAND_GESTURES", "VISION_PRESENCE"]
    for m in methods:
        assert f"{m}: '{m}'" in js_content, f"Missing interaction method {m} in app.js"

    assert "getSupportedMultimodalMethods" in js_content
    assert "switchInteractionModality" in js_content
    assert "getMultimodalInteractionSummary" in js_content


def test_conversation_memory_and_continuity_architecture_in_js():
    """Verify Part 6G 5 Context Layers & Thread Restoration API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    layers = ["CURRENT_CONVERSATION", "CURRENT_WORKSPACE", "ACTIVE_PROJECT", "RELATED_DISCUSSIONS", "LONG_TERM_MEMORY"]
    for l in layers:
        assert f"{l}: '{l}'" in js_content, f"Missing conversation context layer {l} in app.js"

    assert "CONVERSATION_CONTEXT_LAYERS" in js_content
    assert "getConversationContextLayers" in js_content
    assert "restoreConversationContext" in js_content
    assert "resetConversationContext" in js_content
    assert "getConversationContinuitySummary" in js_content


def test_voice_and_conversation_experience_architecture_in_js():
    """Verify Part 6H 7 Master Experience Pillars & Master Status Integration API in app.js."""
    js_path = _UI_WEB_DIR / "app.js"
    js_content = js_path.read_text(encoding="utf-8")

    pillars = [
        "UNIFIED_CONVERSATION", "INTERACTION_RHYTHM", "RELATIONSHIP_BUILDING",
        "CONTEXTUAL_INTELLIGENCE", "USER_CONFIDENCE", "ABSOLUTE_USER_CONTROL", "UNIVERSAL_ACCESSIBILITY"
    ]
    for p in pillars:
        assert f"{p}: '{p}'" in js_content, f"Missing voice experience pillar {p} in app.js"

    assert "VOICE_EXPERIENCE_PILLARS" in js_content
    assert "getVoiceExperiencePillars" in js_content
    assert "getMasterVoiceExperienceStatus" in js_content
