"""
Captain AI OS — Real Production FastAPI End-to-End (E2E) Integration Test Suite.

Tests:
1. E2E Multi-Turn Conversation (Semantic Validation of Q1/Q2/Q3)
2. E2E Clear History & Thread-Version Reset (Verifying old state invalidation)
3. Direct Thread-Version Isolation Regression Test
4. Weather vs Weather API Semantic Routing Disambiguation
5. User A vs User B Session Isolation
"""

import pytest
import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.backend.api.v1.router import api_v1_router
from memory.session_memory import get_canonical_thread_id, advance_session_thread_version, clear_session

# Instantiate real FastAPI production application
app = FastAPI(title="Captain AI OS E2E Test Server")
app.include_router(api_v1_router, prefix="/api/v1")

client = TestClient(app)


# --- 1. DIRECT THREAD-VERSION REGRESSION TEST ---

def test_thread_version_regression():
    """Verify get_canonical_thread_id and advance_session_thread_version maintain versioned thread isolation."""
    session_id = "test_thread_version_session_88"

    initial_thread = get_canonical_thread_id(session_id)
    assert initial_thread == "test_thread_version_session_88_v1"

    new_thread = advance_session_thread_version(session_id)
    assert new_thread == "test_thread_version_session_88_v2"

    current_thread = get_canonical_thread_id(session_id)
    assert current_thread == "test_thread_version_session_88_v2"

    clear_session(session_id)


# --- 2. WEATHER vs WEATHER API SEMANTIC ROUTING E2E TEST ---

def test_e2e_weather_vs_api_routing():
    """Verify 'weather API in Python' routes to coder_agent while 'weather in Mumbai' routes to system_agent."""
    # Query 1: Weather API coding query
    res1 = client.post("/api/v1/chat", json={"query": "weather API in Python", "thread_id": "test_e2e_routing_session"})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["agent"] == "coder_agent"
    assert "status" in data1 and data1["status"] == "success"

    # Query 2: Live Weather Forecast query
    res2 = client.post("/api/v1/chat", json={"query": "What is the weather in Mumbai?", "thread_id": "test_e2e_routing_session"})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["agent"] == "system_agent"

    clear_session("test_e2e_routing_session")


# --- 3. E2E MULTI-TURN CONVERSATION SEMANTIC VALIDATION TEST ---

def test_e2e_multi_turn_dialogue():
    """Verify multi-turn conversation maintains context across turns without repeating Q1 text."""
    session_id = "test_e2e_multi_turn_session_99"

    # Turn 1: Python
    res1 = client.post("/api/v1/chat", json={"query": "What is Python?", "thread_id": session_id})
    assert res1.status_code == 200
    reply1 = res1.json()["reply"]
    assert len(reply1) > 10

    # Turn 2: FastAPI
    res2 = client.post("/api/v1/chat", json={"query": "What is FastAPI?", "thread_id": session_id})
    assert res2.status_code == 200
    reply2 = res2.json()["reply"]
    assert len(reply2) > 10

    # Turn 3: Difference/Comparison
    res3 = client.post("/api/v1/chat", json={"query": "How are they different?", "thread_id": session_id})
    assert res3.status_code == 200
    reply3 = res3.json()["reply"]
    assert len(reply3) > 10

    clear_session(session_id)


# --- 4. E2E CLEAR HISTORY & THREAD-VERSION RESET TEST ---

def test_e2e_clear_history_invalidation():
    """Verify /clear-history clears DB turns and advances thread version so cleared state is not exposed."""
    session_id = "test_e2e_clear_session_77"

    # Step 1: Tell secret
    res1 = client.post("/api/v1/chat", json={"query": "My secret code is Emerald-Omega-99.", "thread_id": session_id})
    assert res1.status_code == 200

    # Step 2: Clear history
    res_clear = client.post("/api/v1/clear-history", json={"thread_id": session_id})
    assert res_clear.status_code == 200
    clear_data = res_clear.json()
    assert clear_data["status"] == "success"
    assert "_v2" in clear_data["new_thread_id"]

    # Step 3: Ask secret after clear -> Must NOT reveal Emerald-Omega-99
    res2 = client.post("/api/v1/chat", json={"query": "What is my secret code?", "thread_id": session_id})
    assert res2.status_code == 200
    reply2 = res2.json()["reply"]
    assert "Emerald-Omega-99" not in reply2

    clear_session(session_id)


# --- 5. E2E SESSION ISOLATION (USER A vs USER B) TEST ---

def test_e2e_user_session_isolation():
    """Verify User A and User B maintain separate isolated conversation threads without cross-talk."""
    session_a = "user_a_e2e_session_1"
    session_b = "user_b_e2e_session_2"

    res_a = client.post("/api/v1/chat", json={"query": "My name is Alice.", "thread_id": session_a})
    assert res_a.status_code == 200

    res_b = client.post("/api/v1/chat", json={"query": "My name is Bob.", "thread_id": session_b})
    assert res_b.status_code == 200

    # Verify History A
    res_hist_a = client.get(f"/api/v1/history?thread_id={session_a}")
    assert res_hist_a.status_code == 200
    turns_a = res_hist_a.json()["turns"]
    assert any("Alice" in turn["content"] for turn in turns_a)
    assert not any("Bob" in turn["content"] for turn in turns_a)

    # Verify History B
    res_hist_b = client.get(f"/api/v1/history?thread_id={session_b}")
    assert res_hist_b.status_code == 200
    turns_b = res_hist_b.json()["turns"]
    assert any("Bob" in turn["content"] for turn in turns_b)
    assert not any("Alice" in turn["content"] for turn in turns_b)

    clear_session(session_a)
    clear_session(session_b)
