"""
Captain AI OS — Runtime Architecture Fix Regression Test Suite.
Tests:
1. Multi-turn conversation propagation & state management
2. Session clearing & checkpoint invalidation
3. Hybrid intent router (word-boundary regex, no false positives)
4. Vector memory similarity distance thresholding
5. Tool invocation security & permission boundary
"""

import pytest
import asyncio
from langchain_core.messages import HumanMessage, AIMessage
from src.graph.state_graph import classify_intent_hybrid, router_node, reset_thread_checkpoint
from memory.session_memory import save_turn, get_history, clear_session
from memory.vector_memory import store_semantic_memory, query_semantic_memory, clear_session_semantic_memory
from src.tools.tool_invocation_layer import ToolInvocationLayer, ToolExecutionStatus
from src.tools.tool_registry import ToolRegistry, ToolDefinition, ToolMetadata
from src.backend.core.permission_manager import PermissionManager, Permission
from src.backend.core.event_bus import event_bus
from src.backend.config import settings
from pydantic import BaseModel, Field


# --- 1. MANDATORY ROUTING TESTS ---

def test_router_word_boundary_false_positives():
    """Verify router eliminates substring false positives (program != ram, digital marketing != git)."""
    assert classify_intent_hybrid("program") == "chat_agent"
    assert classify_intent_hybrid("digital marketing") == "chat_agent"


def test_router_intent_classification():
    """Verify intent router correctly routes queries based on intent rather than raw substring position."""
    assert classify_intent_hybrid("weather API in Python") == "coder_agent"
    assert classify_intent_hybrid("What is the weather in Mumbai?") == "system_agent"
    assert classify_intent_hybrid("Write a Python function to calculate Fibonacci.") == "coder_agent"
    assert classify_intent_hybrid("Search the latest information about OpenAI.") == "search_agent"
    assert classify_intent_hybrid("Explain this uploaded document.") == "rag_agent"


# --- 2. MANDATORY CURRENT QUERY & STATE PROPAGATION TESTS ---

def test_router_node_query_propagation():
    """Verify router_node updates messages so current user_query is propagated as a fresh HumanMessage."""
    async def _test():
        initial_state = {
            "user_query": "What is FastAPI?",
            "messages": [
                HumanMessage(content="What is Python?"),
                AIMessage(content="Python is a programming language.")
            ],
            "next_agent": ""
        }

        res = await router_node(initial_state)
        assert res["user_query"] == "What is FastAPI?"
        assert "messages" in res
        assert isinstance(res["messages"][0], HumanMessage)
        assert res["messages"][0].content == "What is FastAPI?"

    asyncio.run(_test())


# --- 3. MANDATORY CLEAR-HISTORY & SESSION ISOLATION TESTS ---

def test_session_clear_isolation():
    """Verify clear_session & reset_thread_checkpoint clear session memory without leaking."""
    test_session = "test_clear_session_123"

    save_turn(test_session, "user", "My name is Captain.")
    save_turn(test_session, "assistant", "Hello Captain!")

    history_before = get_history(test_session)
    assert len(history_before) == 2

    # Clear session & reset checkpointer
    deleted = clear_session(test_session)
    reset_thread_checkpoint(test_session)
    assert deleted >= 2

    history_after = get_history(test_session)
    assert len(history_after) == 0


# --- 4. MANDATORY VECTOR MEMORY THRESHOLD TESTS ---

def test_vector_memory_distance_thresholding():
    """Verify semantic memory query filters out items exceeding distance threshold."""
    test_session = "test_vec_threshold_session"
    store_semantic_memory("mem_1", "Python is a programming language", {"session_id": test_session})

    # Query with a very strict distance threshold (0.01) -> should filter out non-exact matches
    matches_strict = query_semantic_memory("restaurants and food", top_k=3, distance_threshold=0.01)
    assert len(matches_strict) == 0

    clear_session_semantic_memory(test_session)


# --- 5. MANDATORY SECURITY & PERMISSION TESTS ---

class MockToolArgs(BaseModel):
    filepath: str = Field(description="Target path")


def test_tool_security_permission_denial():
    """Verify ToolInvocationLayer denies execution when agent lacks permission."""
    async def _test():
        registry = ToolRegistry()
        perm_mgr = PermissionManager()
        # Explicitly deny write files permission
        perm_mgr.revoke_permission(Permission.FS_WRITE)

        async def mock_handler(filepath: str):
            return "written"

        meta = ToolMetadata(
            name="delete_system_file",
            description="Deletes file",
            permissions_required=[Permission.FS_WRITE],
            args_schema=MockToolArgs
        )
        await registry.register_tool(meta, mock_handler)

        layer = ToolInvocationLayer(registry, perm_mgr, event_bus)
        result = await layer.execute_tool("delete_system_file", {"filepath": "/tmp/test"}, caller_agent_name="untrusted_agent")

        assert result.status == ToolExecutionStatus.PERMISSION_DENIED
        assert "lacks required permission" in result.error

    asyncio.run(_test())


# --- 6. SYSTEM AGENT INTENT DISAMBIGUATION TEST ---

def test_system_agent_intent_disambiguation():
    """Verify SystemAgent distinguishes conceptual explanations ('What is RAM?') from live actions."""
    from src.agents.system_agent import SystemAgent
    agent = SystemAgent()

    assert agent._is_conceptual_explanation("what is ram?") is True
    assert agent._is_conceptual_explanation("explain cpu usage") is True
    assert agent._is_conceptual_explanation("what is a weather api?") is True

    assert agent._is_conceptual_explanation("how much ram is my computer using?") is False
    assert agent._is_conceptual_explanation("what is the weather in mumbai?") is False
    assert agent._is_conceptual_explanation("run dir") is False


# --- 7. RAG RELEVANCE SCORE FILTERING TEST ---

def test_rag_relevance_filtering():
    """Verify query_rag handles empty/non-matching index gracefully without throwing exceptions."""
    from tools.rag_tools import query_rag
    res = query_rag("Unmatched random query XYZ 99999", score_threshold=0.0001)
    assert res["status"] in ["no_relevant_docs", "error"]


# --- 8. SESSION ISOLATION (USER A vs USER B) TEST ---

def test_session_uuid_isolation():
    """Verify User A and User B maintain separate isolated conversation histories."""
    user_a = "user_a_session_uuid_101"
    user_b = "user_b_session_uuid_202"

    save_turn(user_a, "user", "My name is Alice.")
    save_turn(user_a, "assistant", "Hello Alice!")

    save_turn(user_b, "user", "My name is Bob.")
    save_turn(user_b, "assistant", "Hello Bob!")

    history_a = get_history(user_a)
    history_b = get_history(user_b)

    assert len(history_a) == 2
    assert len(history_b) == 2
    assert "Alice" in history_a[0]["content"]
    assert "Bob" in history_b[0]["content"]

    clear_session(user_a)
    clear_session(user_b)
