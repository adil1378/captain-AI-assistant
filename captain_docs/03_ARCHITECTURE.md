# 🏗️ Captain AI OS 2.0 — System Architecture

> **Document:** `03_ARCHITECTURE.md`  
> **Status:** Authoritative Architectural Blueprint  
> **Rule:** Current Architecture and Target Architecture are strictly segregated.

---

## 1. Current Architecture (As of Commit `bdfaf69`)

The repository reflects the completed **Phase 1** and **Phase 2** baselines, currently transitioning away from legacy V1 prototypes toward the unified V2 enterprise architecture.

```mermaid
flowchart TD
    subgraph UI_Surface ["UI & Presentation Layer"]
        CLI["Rich Terminal CLI (main.py / ui/terminal.py)"]
        PET["Native PySide6 Desktop Pet (ui/desktop/pet_window.py + pet.html)"]
        WEB["FastAPI Web Client (ui/web/app.js + index.html)"]
    end

    subgraph Runtime_Core ["Runtime & State Control (app/ & config.py)"]
        CONF["Central Settings (config.py)"]
        RUN["AppRuntime Singleton (app/runtime.py)"]
        STATE["StateManager & AppState (app/state.py)"]
        BUS["Micro-Kernel EventBus (src/backend/core/event_bus.py)"]
    end

    subgraph Multi_Agent_Brain ["LangGraph Multi-Agent Engine (src/graph/ & src/agents/)"]
        ROUTER["Hybrid Intent Router (src/graph/router.py)"]
        LIFECYCLE["AgentLifecycleManager (src/agents/agent_lifecycle_manager.py)"]
        REGISTRY["AgentRegistry (src/agents/agent_registry.py)"]
        AGENTS["Active Agents:\nConversationAgent | CodingAgent | SystemAgent\nRagAgent | SearchAgent | CommsAgent"]
    end

    subgraph Tool_Security ["Execution & Security Layer"]
        TIL["ToolInvocationLayer (src/tools/tool_invocation_layer.py)"]
        PERM["PermissionManager & ZeroTrustManager (src/backend/core/)"]
        SEC_UI["SecurityConfirmationDialog (ui/desktop/pet_window.py)"]
        TOOLS["Tool Catalog (tools/ & src/tools/)\nFiles, Shell, Scrapers, GitHub, Voice, Location, Comms"]
    end

    subgraph Memory_Layer ["Dual Memory & Persistence"]
        SESS["SessionMemory (memory/session_memory.py)"]
        VEC["VectorMemory (memory/vector_memory.py - ChromaDB)"]
        SUPA["Cloud Supabase PostgreSQL (Async background turn sync)"]
    end

    UI_Surface --> RUN
    CONF --> RUN
    RUN --> STATE & BUS
    RUN --> Multi_Agent_Brain
    Multi_Agent_Brain --> Tool_Security
    Tool_Security --> TOOLS
    Multi_Agent_Brain --> Memory_Layer
```

---

### 1.1. Directory Structure & Architectural Roles

| Directory / File | Status | Architectural Role |
| :--- | :--- | :--- |
| [`main.py`](file:///d:/captain/main.py) | **ACTIVE** | Central CLI & server entrypoint (`chat`, `desktop`, `serve`, `ingest`, `metrics`, `weather`). |
| [`config.py`](file:///d:/captain/config.py) | **ACTIVE** | Central Pydantic v2 `Settings` object managing all environment, model, voice, and security configs. |
| [`app/`](file:///d:/captain/app) | **ACTIVE** | Core application foundation: [`app/state.py`](file:///d:/captain/app/state.py) (`AppState` machine) and [`app/runtime.py`](file:///d:/captain/app/runtime.py) (`AppRuntime` lifecycle coordinator). |
| [`src/agents/`](file:///d:/captain/src/agents) | **ACTIVE** | V2 multi-agent implementation inheriting from [`BaseAgent`](file:///d:/captain/src/agents/base_agent.py). Coordinated by `AgentRegistry`. |
| [`src/graph/`](file:///d:/captain/src/graph) | **ACTIVE** | LangGraph state graph ([`state_graph.py`](file:///d:/captain/src/graph/state_graph.py)) and hybrid intent router ([`router.py`](file:///d:/captain/src/graph/router.py)). |
| [`src/backend/`](file:///d:/captain/src/backend) | **ACTIVE** | FastAPI REST/WebSocket router (`api/v1/router.py`), micro-kernel services (`event_bus.py`, `permission_manager.py`, `zero_trust_manager.py`). |
| [`src/tools/`](file:///d:/captain/src/tools) | **ACTIVE** | Standardized tool invocation layer ([`tool_invocation_layer.py`](file:///d:/captain/src/tools/tool_invocation_layer.py)) and tool catalog. |
| [`ui/desktop/`](file:///d:/captain/ui/desktop) | **ACTIVE** | Native PySide6 frameless transparent overlay ([`pet_window.py`](file:///d:/captain/ui/desktop/pet_window.py)), hosting 3D EMO pet ([`pet.html`](file:///d:/captain/ui/desktop/pet.html)). |
| [`ui/web/`](file:///d:/captain/ui/web) | **ACTIVE** | Glassmorphic web workspace ([`index.html`](file:///d:/captain/ui/web/index.html), [`app.js`](file:///d:/captain/ui/web/app.js)). |
| [`ui/terminal.py`](file:///d:/captain/ui/terminal.py) | **ACTIVE** | Rich terminal formatting utilities (banners, response cards, agent status tables). |
| [`memory/`](file:///d:/captain/memory) | **ACTIVE** | In-memory session buffers ([`session_memory.py`](file:///d:/captain/memory/session_memory.py)) and ChromaDB vector search ([`vector_memory.py`](file:///d:/captain/memory/vector_memory.py)). |
| [`providers/`](file:///d:/captain/providers) | **ACTIVE** | Provider abstractions (`base.py`) and implementations (`llm/` for Ollama, OpenAI, Gemini). |
| [`tests/`](file:///d:/captain/tests) | **ACTIVE** | 206 automated tests covering units, integration, managers, frontend bibles, and Phase 1/2 baselines. |
| [`agents/`](file:///d:/captain/agents) | **LEGACY (V1)** | Legacy function-based agent nodes. Kept for backward compatibility while migrating to `src/agents/`. |
| [`core/`](file:///d:/captain/core) | **LEGACY (V1)** | Legacy `core/graph.py` and `core/llm.py`. Superseded by `src/graph/` and `app/runtime.py`. |
| [`tools/`](file:///d:/captain/tools) | **MIGRATING** | Standalone tool implementations (`voice.py`, `weather.py`, `file_tools.py`). Invoked via `src/tools/tool_invocation_layer.py`. |

---

### 1.2. Legacy & Duplicate Architecture Policy

The repository currently maintains dual legacy paths:
1. `agents/` (V1) vs `src/agents/` (V2)
2. `core/graph.py` (V1) vs `src/graph/state_graph.py` (V2)
3. `tools/` (legacy direct calls) vs `src/tools/tool_invocation_layer.py` (secure boundary)

**Policy:** Do NOT delete legacy folders blindly. Legacy code is preserved until tests and active runtime are fully converted to `src/`. No production entrypoint in `main.py` invokes V1 code directly.

---

## 2. Target Architecture (Captain AI OS 2.0 Evolution)

The target architecture unifies voice, screen perception, desktop automation, and multi-agent reasoning into a single cohesive, closed-loop operating system:

```mermaid
flowchart TD
    USER([User]) --> INPUT_LAYER

    subgraph INPUT_LAYER ["Input & Perception Ingestion"]
        MIC["Microphone Audio Stream"]
        CLAP["Transient Clap Detector (Noise Floor + Timing)"]
        VAD["Silero VAD (Voice Activity Detection)"]
        STT["Faster-Whisper Local STT"]
        KEY["Keyboard / Text Input (Terminal / Web)"]
        SCREEN["Desktop Screen Capture & Active Window Info"]
    end

    INPUT_LAYER --> RUNTIME

    subgraph RUNTIME ["Captain Core Runtime"]
        SM["Explicit State Machine (8 States)"]
        EB["Async Micro-Kernel EventBus"]
        CTX["Context & Thread Coordinator"]
    end

    RUNTIME --> ROUTER["Hybrid Router & Intent Classifier"]

    subgraph BRAIN ["LangGraph Multi-Agent Engine"]
        ROUTER --> COORD["Planning & Task Decomposition"]
        COORD --> AG_CONV["Conversation Agent"]
        COORD --> AG_CODE["Coding Agent"]
        COORD --> AG_SYS["System & OS Agent"]
        COORD --> AG_RAG["RAG Document Agent"]
        COORD --> AG_SEARCH["Search Agent"]
        COORD --> AG_COMMS["Comms Agent"]
        COORD --> AG_VIS["Vision & UI Agent (Phase 4)"]
        COORD --> AG_ACT["Computer Use Agent (Phase 5/6)"]
    end

    BRAIN --> GATEWAY

    subgraph GATEWAY ["Canonical Secure Tool Gateway"]
        AUTH["Zero-Trust Permission Manager"]
        DIALOG["Native Security Confirmation Dialog"]
        AUTH --> DIALOG
        DIALOG --> EXEC["Authorized Tool Execution Layer"]
    end

    subgraph CONTROL ["Windows Desktop & System Control (Phase 5)"]
        EXEC --> MOUSE["Mouse Actions (Click, Drag, Move)"]
        EXEC --> KBD["Keyboard Automation (Type, Hotkeys)"]
        EXEC --> WIN["Window & App Manager (Launch, Focus)"]
        EXEC --> SHELL["Terminal / PowerShell Execution"]
        EXEC --> FILES["File & Code Modification"]
        EXEC --> BROWSER["Browser Automation"]
        EXEC --> APIS["External APIs & Messaging"]
    end

    CONTROL --> OBSERVE["Observe Real-World Result (Screen / Logs / AST)"]
    OBSERVE --> VERIFY{"Verify Expected Outcome?"}
    VERIFY -- "No (Iterate)" --> BRAIN
    VERIFY -- "Yes (Complete)" --> RESPONSE

    subgraph RESPONSE ["Dual Presentation & Feedback Surface"]
        TTS["Local Neural TTS (Kokoro / Piper)"]
        EMO["3D EMO Pet (Face Expressions & Eye Glow)"]
        WEB_OUT["Web Dashboard (Detailed Logs, Diffs, History)"]
    end
```

---

## 3. Key Differences Between Current and Target

| Subsystem | Current State (`bdfaf69`) | Target State (End of Phase 8) |
| :--- | :--- | :--- |
| **Voice Ingest** | Basic `SpeechRecognition`, manual `v` hotkey in CLI. | Always-listening Silero VAD, Clap activation, sub-second Faster-Whisper STT. |
| **Speech Output** | Synchronous `pyttsx3` with robotic timbre. | Local neural streaming TTS (Kokoro/Piper) synced to EMO mouth movements. |
| **Screen Perception** | Static `pyautogui.screenshot()` tool. | Real-time multi-monitor OCR, active-window geometry, and vision model context. |
| **OS Control** | Basic shell command execution and file manipulation. | Full GUI automation: mouse clicks, keyboard entry, application switching, window manipulation. |
| **Execution Loop** | Single-turn LangGraph invoke (Input $\rightarrow$ Tool $\rightarrow$ Text). | Iterative multi-turn autonomous loop (Observe $\rightarrow$ Act $\rightarrow$ Observe $\rightarrow$ Verify). |
| **Companion Pet** | Frameless Qt container displaying 3D animations synced to state. | Bi-directional desktop companion reacting to voice amplitude, mouse interactions, and desktop events. |
