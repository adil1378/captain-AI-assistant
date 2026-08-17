"""
Unit & Integration Tests for Volumes 1 through 9 Codebase Synchronization.
Verifies decision engine, embedding engine, voice engine, vision engine, MCP client,
workflow engine, OSAL, window manager, graph memory, RAG engine, learning engine,
and memory lifecycle manager.
"""

import pytest
import asyncio
from src.backend.core.decision_engine import AIDecisionEngine, EvaluationRequest, DecisionOutcome, DecisionRiskLevel
from memory.embedding_engine import EmbeddingEngine
from src.backend.core.voice_engine import VoiceEngine, VoiceConfig
from src.backend.core.vision_engine import VisionEngine
from src.backend.core.mcp_client import MCPClient, MCPServerConfig
from src.backend.core.workflow_engine import WorkflowExecutionEngine, WorkflowDefinition, WorkflowStep, WorkflowState
from src.backend.core.osal import OperatingSystemAbstractionLayer
from src.backend.core.window_manager import WindowManager
from memory.graph_memory import GraphMemory, KnowledgeNode, RelationshipType
from src.backend.core.rag_engine import RAGEngine
from memory.learning_engine import LearningEngine, FeedbackRecord, FeedbackType
from memory.memory_lifecycle_manager import MemoryLifecycleManager


def test_decision_engine():
    engine = AIDecisionEngine()

    req_low = EvaluationRequest(
        request_id="req_1",
        action_type="search_query",
        agent_id="search_agent",
        target_resource="web",
        confidence_score=0.9
    )
    res_low = engine.evaluate_action(req_low)
    assert res_low.outcome == DecisionOutcome.APPROVED
    assert res_low.risk_level == DecisionRiskLevel.LOW

    req_high = EvaluationRequest(
        request_id="req_2",
        action_type="file_delete",
        agent_id="system_agent",
        target_resource="system32",
        confidence_score=0.9
    )
    res_high = engine.evaluate_action(req_high)
    assert res_high.outcome == DecisionOutcome.REQUIRES_USER_APPROVAL
    assert res_high.risk_level == DecisionRiskLevel.HIGH


def test_embedding_engine():
    engine = EmbeddingEngine(dimension=128)
    vec1 = engine.generate_embedding("hello world captain ai")
    vec2 = engine.generate_embedding("hello world captain ai")
    vec3 = engine.generate_embedding("completely different text snippet")

    assert len(vec1) == 128
    sim_same = engine.cosine_similarity(vec1, vec2)
    sim_diff = engine.cosine_similarity(vec1, vec3)

    assert pytest.approx(sim_same, 0.01) == 1.0
    assert sim_diff < sim_same


@pytest.mark.anyio
async def test_voice_engine():
    engine = VoiceEngine()
    transcription = await engine.speech_to_text(b"raw_pcm_audio_data_buffer_sample")
    assert transcription.confidence > 0.8
    assert len(transcription.text) > 0

    audio_bytes = await engine.text_to_speech("Captain OS online")
    assert audio_bytes.startswith(b"RIFF")


def test_vision_engine():
    engine = VisionEngine()
    analysis = engine.analyze_frame(b"sample_frame_bytes", window_title="VSCode")
    assert len(analysis.ui_elements) > 0
    assert analysis.active_window_title == "VSCode"
    assert "Captain AI OS" in analysis.extracted_text


@pytest.mark.anyio
async def test_mcp_client():
    client = MCPClient()
    cfg = MCPServerConfig(server_id="srv_1", name="Filesystem MCP", transport="stdio", endpoint="/bin/mcp")
    client.register_server(cfg)

    caps = await client.discover_capabilities("srv_1")
    assert len(caps) > 0

    result = await client.execute_tool("srv_1", "mcp_file_read", {"path": "/tmp/test.txt"})
    assert result["status"] == "success"


@pytest.mark.anyio
async def test_workflow_engine():
    engine = WorkflowExecutionEngine()
    wf = WorkflowDefinition(
        workflow_id="wf_1",
        name="Test Automation",
        steps=[
            WorkflowStep(step_id="step_1", action="fetch_data"),
            WorkflowStep(step_id="step_2", action="process_data", depends_on=["step_1"])
        ]
    )

    registered = engine.register_workflow(wf)
    assert registered is True

    res = await engine.execute_workflow(wf)
    assert res["state"] == WorkflowState.COMPLETED
    assert "step_1" in res["results"]
    assert "step_2" in res["results"]


def test_osal_and_window_manager():
    platform_info = OperatingSystemAbstractionLayer.get_platform_info()
    assert platform_info.os_name in ["Windows", "Linux", "Darwin"]

    metrics = OperatingSystemAbstractionLayer.get_hardware_metrics()
    assert metrics.cpu_cores >= 1

    wm = WindowManager()
    windows = wm.enumerate_windows()
    assert len(windows) > 0
    assert wm.set_focus(windows[0].window_id) is True


def test_graph_memory():
    gm = GraphMemory()
    n1 = KnowledgeNode(node_id="n1", label="User", category="entity")
    n2 = KnowledgeNode(node_id="n2", label="Preference", category="fact")

    gm.add_node(n1)
    gm.add_node(n2)
    gm.add_edge("n1", "n2", RelationshipType.OWNERSHIP)

    related = gm.get_related_nodes("n1")
    assert len(related) == 1
    assert related[0].node_id == "n2"


def test_rag_engine():
    rag = RAGEngine()
    expanded = rag.expand_query("captain status")
    assert len(expanded) >= 3

    pkg = rag.retrieve_and_rank("captain status")
    assert pkg.query == "captain status"
    assert pkg.context_id.startswith("ctx_")


@pytest.mark.anyio
async def test_learning_and_lifecycle():
    le = LearningEngine()
    fb = FeedbackRecord(feedback_id="f1", user_id="u1", action_type="weather_lookup", feedback_type=FeedbackType.POSITIVE)
    le.record_feedback(fb)

    prof = le.get_or_create_profile("u1")
    assert "weather_lookup" in prof.favorite_tools

    lcm = MemoryLifecycleManager()
    records = [{"id": "m1", "content": "text 1"}, {"id": "m2", "content": "text 1"}]
    deduped = await lcm.consolidate_and_deduplicate(records)
    assert len(deduped) == 1

    archived = await lcm.archive_inactive_memories(deduped)
    assert archived == 1
