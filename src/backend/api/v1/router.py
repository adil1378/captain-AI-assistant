import sys
from pathlib import Path

# Ensure project root (D:\captain) is in sys.path
_PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import time
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from src.backend.core.task_queue import task_queue
from src.backend.core.event_bus import event_bus
from src.tools.system_tools import get_system_metrics
from memory.session_memory import save_turn, get_history, clear_session
from memory.vector_memory import store_semantic_memory
from loguru import logger

api_v1_router = APIRouter()

# Lazy-initialized graph singleton (built once on first request)
_graph = None
_manager = None


async def _get_graph():
    """Lazily build the full 6-agent V2 LangGraph engine on first API request."""
    global _graph, _manager
    if _graph is not None:
        return _graph

    from src.agents.agent_registry import AgentRegistry
    from src.agents.agent_lifecycle_manager import AgentLifecycleManager
    from src.agents.conversation_agent import ConversationAgent
    from src.agents.coding_agent import CodingAgent
    from src.agents.system_agent import SystemAgent
    from src.agents.rag_agent import RagAgent
    from src.agents.search_agent import SearchAgent
    from src.agents.comms_agent import CommsAgent
    from src.graph.state_graph import create_captain_graph

    registry = AgentRegistry()
    agents = [
        ConversationAgent(), CodingAgent(), SystemAgent(),
        RagAgent(), SearchAgent(), CommsAgent()
    ]
    for agent in agents:
        ok, errs = await registry.register_agent(agent)
        if not ok:
            logger.error(f"Failed to register {agent.metadata.name}: {errs}")

    _manager = AgentLifecycleManager(registry, event_bus)
    _graph = create_captain_graph(registry, _manager)
    logger.info("V2 LangGraph engine (6 agents) initialized for API server.")
    return _graph


def _make_state(user_query: str) -> dict:
    return {
        "messages": [],
        "user_query": user_query,
        "current_agent": "",
        "next_agent": "",
        "task_plan": [],
        "scratchpad": {},
        "error": None,
    }


def _async_store_semantic_memory(turn_id: str, text: str, meta: dict):
    """Non-blocking background thread worker for ChromaDB semantic memory indexing."""
    try:
        store_semantic_memory(turn_id, text, meta)
    except Exception as e:
        logger.warning(f"Background vector memory storage skipped: {e}")


# --- Pydantic Data Transfer Objects ---

class ChatRequest(BaseModel):
    query: str
    thread_id: str = "captain_api_session"


class ChatResponse(BaseModel):
    reply: str
    agent: str
    status: str = "success"


class ClearHistoryRequest(BaseModel):
    thread_id: str = "captain_api_session"


# --- REST Endpoints ---

@api_v1_router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """Non-blocking async REST chat endpoint with Supabase/SQLite persistence & ChromaDB memory."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    graph = await _get_graph()
    config = {"configurable": {"thread_id": req.thread_id}}

    try:
        final_state = await graph.ainvoke(_make_state(req.query), config=config)
        messages = final_state.get("messages", [])
        agent = final_state.get("current_agent", "Captain")
        reply = messages[-1].content if messages else "I am processing your request."

        # Persist conversation turn to Supabase PostgreSQL / SQLite
        turn_id = f"turn_{int(time.time() * 1000)}"
        save_turn(req.thread_id, "user", req.query)
        save_turn(req.thread_id, "assistant", reply)

        # Offload ChromaDB vector store indexing to background non-blocking thread
        asyncio.create_task(
            asyncio.to_thread(_async_store_semantic_memory, turn_id, f"User asked: {req.query} | Captain responded: {reply}", {"session_id": req.thread_id})
        )

        return ChatResponse(reply=reply, agent=agent)
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.get("/history")
async def get_history_endpoint(thread_id: str = "captain_api_session", limit: int = 50):
    """Retrieve historical conversation turns for a given session thread."""
    try:
        history = get_history(session_id=thread_id, limit=limit)
        return {"session_id": thread_id, "turns": history}
    except Exception as e:
        logger.error(f"History API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.post("/clear-history")
async def clear_history_endpoint(req: ClearHistoryRequest):
    """Clear conversation history for a given session."""
    try:
        deleted = clear_session(session_id=req.thread_id)
        return {"status": "success", "session_id": req.thread_id, "deleted_turns": deleted}
    except Exception as e:
        logger.error(f"Clear history API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.get("/metrics")
async def metrics_endpoint():
    """Return live system hardware metrics."""
    return get_system_metrics()


@api_v1_router.get("/tasks/{task_id}")
async def task_status_endpoint(task_id: str):
    """Check status of a background queued task."""
    status = task_queue.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task ID not found.")
    return status


# --- WebSocket Endpoint ---

@api_v1_router.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """Real-time WebSocket chat endpoint streaming agent replies with persistence."""
    await websocket.accept()
    logger.info("WebSocket client connected to /api/v1/ws/chat")

    graph = await _get_graph()

    try:
        while True:
            data = await websocket.receive_json()
            query = (data.get("query") or data.get("message") or "").strip()
            thread_id = data.get("thread_id", "ws_session")

            if not query:
                logger.warning(f"WebSocket received empty query from payload: {data}")
                continue

            await websocket.send_json({"event": "AgentStarted", "agent": "router"})

            config = {"configurable": {"thread_id": thread_id}}
            final_state = await graph.ainvoke(_make_state(query), config=config)
            messages = final_state.get("messages", [])
            reply = messages[-1].content if messages else "Done."
            agent = final_state.get("current_agent", "Captain")

            # Persist WebSocket conversation turn
            turn_id = f"turn_{int(time.time() * 1000)}"
            save_turn(thread_id, "user", query)
            save_turn(thread_id, "assistant", reply)

            # Offload ChromaDB vector store indexing to background non-blocking thread
            asyncio.create_task(
                asyncio.to_thread(_async_store_semantic_memory, turn_id, f"User asked: {query} | Captain responded: {reply}", {"session_id": thread_id})
            )

            await websocket.send_json({
                "event": "AgentFinished",
                "agent": agent,
                "reply": reply,
            })

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"event": "Error", "detail": str(e)})
        except Exception:
            pass
