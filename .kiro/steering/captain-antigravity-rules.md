---
inclusion: always
---

# Captain AI Project — Antigravity Rules & Structured Development Plan

**Status:** Architecture Loop Detected & Exit Plan Active  
**Date:** August 1, 2026  
**Purpose:** Break the circular rewrite pattern and deliver a stable, working system

---

## The Core Problem: The Antigravity Loop

You are building **upward without a foundation** — adding enterprise-grade infrastructure (async agents, lifecycle management, event buses) while the basic system still crashes on import. This creates an **architecture loop**:

```
v1 works partially → "too simple, rebuild properly"
→ v2 half-built → "need something working"
→ patch v1 → "v1 still messy"
→ add more v2 → nothing connects → back to v1
```

**Result:** Two complete, disconnected codebases. Neither runs end-to-end.

---

## Project Inventory

### Working Components ✅
- **CLI Entry** (`main.py`) — boots v1 pipeline
- **Voice Pipeline** (`tools/voice.py`) — in-memory TTS/STT, zero disk writes
- **Contacts** (`tools/contacts.py`) — fuzzy matching with difflib, stop word filtering
- **RAG Tools** (`tools/rag_tools.py`) — PDF/TXT/DOCX/MD ingestion, FAISS vectorstore
- **Web Scraper** (`tools/web_scraper.py`) — clean BeautifulSoup scraping
- **Search** (`tools/search.py`) — DuckDuckGo/Google/Tavily with fallbacks
- **Email** (`tools/email_tool.py`) — SMTP with attachments
- **WhatsApp** (`tools/whatsapp_tool.py`) — PyWhatKit automation + web link fallback
- **Config** (`config.py`) — pydantic-settings, environment-driven

### Crash-Level Bugs ❌
1. **`core/llm_factory.py` field name mismatch** — calls `settings.DEFAULT_PROVIDER` (uppercase) but `config.py` defines `settings.llm_provider` (lowercase). Every LLM call crashes.
2. **`rag_agent.py` imports missing `rag_search_tool`** — exists now as alias in `tools/rag_tools.py`
3. **`scraper_agent.py` imports missing `multi_search`** — exists now as alias in `tools/search.py`
4. **`system_agent.py` imports missing `run_terminal_command`** — exists now in `tools/system_tools.py`
5. **`ui/terminal.py` reads wrong key names** — `print_system_table` expects top-level keys

### Disconnected v2 Infrastructure 🚫
- **`src/agents/base_agent.py`** — Enterprise BaseAgent with lifecycle states (UNINITIALIZED→INITIALIZING→READY→RUNNING→PAUSED→STOPPED→FAILED)
- **`src/agents/agent_registry.py`** — Semver validation, capability collision checks, dependency resolution, hot-reload, topological discovery
- **`src/agents/agent_lifecycle_manager.py`** — 3-phase lock execution pattern, pause/resume via asyncio.Event, recovery with max attempts
- **`src/backend/core/event_bus.py`** — Async pub/sub with wildcard subscriptions
- **`src/backend/core/task_queue.py`** — Background task worker with cancellation
- **`src/graph/state_graph.py`** — Hybrid keyword + LLM intent router
- **`src/backend/main.py`** — FastAPI server that is never started

**These are exceptionally well-designed components that are never instantiated or wired to anything.**

---

## Cardinal Rules — The Antigravity Countermeasures

### Rule 1: No New Architecture Until Current Works
- Do NOT create new abstraction layers, base classes, or registries
- Do NOT refactor working code "to make it cleaner"
- Do NOT add async wrappers around sync code
- Fix crashes first, then stabilize, then enhance

### Rule 2: One Codebase, One Truth
- `agents/` (v1) and `src/agents/` (v2) cannot coexist indefinitely
- After Phase 1 fixes, choose v2 and commit fully
- Delete `agents/`, `core/graph.py` once v2 is wired and confirmed working
- No parallel development — finish migration completely

### Rule 3: Exact Version Pinning
- Replace ALL `>=` version ranges in `requirements.txt` with `==` pins
- LangChain has breaking changes between minor versions
- Lock to versions that are currently working on your machine
- Update deliberately, not accidentally

### Rule 4: Conversation History Must Be Used
- `AgentState.messages` accumulates but agents only see `user_query` (a string)
- Multi-turn memory exists in checkpointer but is never injected into prompts
- Fix: Pass the full `messages` list into agent LLM calls, not just the latest query

### Rule 5: No Heuristic-Only Routing
- Keyword matching fails on ambiguous queries
- "what's the temperature today?" → system_agent (wrong, should be scraper_agent)
- Fix: Use `src/graph/state_graph.py` hybrid router (keywords + LLM fallback)

### Rule 6: Document Decisions
- Every time you choose NOT to implement something, write why in comments or docs
- Every time you delete code, explain what it did and why it is gone
- Every time you wire two systems together, document the integration point

---

## The Exit Plan — Four Phases

### Phase 1: Stop the Crashes (Priority: CRITICAL | ETA: 1-2 hours)

**Goal:** Make the app boot and run without import errors.

Tasks:
1. Fix `core/llm_factory.py` settings field names
   - `settings.DEFAULT_PROVIDER` → `settings.llm_provider`
   - `settings.CHAT_MODEL` → `settings.chat_model`
   - `settings.OLLAMA_BASE_URL` → `settings.ollama_base_url`
   - `settings.OPENAI_API_KEY` → `settings.openai_api_key`
   - `settings.GEMINI_API_KEY` → `settings.google_api_key`

2. Already fixed: `tools/rag_tools.py` — `rag_search_tool` alias exists
3. Already fixed: `tools/search.py` — `multi_search` function exists
4. Already fixed: `tools/system_tools.py` — `run_terminal_command` exists
5. Review `ui/terminal.py` key names in `print_system_table`
6. Delete `agents/media_agent.py` — unreachable code, not wired anywhere

Acceptance Criteria:
- `python main.py chat` runs without import errors
- User can send a query and receive a response
- No AttributeError, ImportError, or KeyError on startup

---

### Phase 2: Wire Conversation Memory (Priority: HIGH | ETA: 2-4 hours)

**Goal:** Enable multi-turn conversations with context.

Current Behavior:
- `AgentState.messages` accumulates with each turn via `add_messages`
- `MemorySaver` checkpointer persists messages across sessions
- But each agent node only receives `state.get("user_query")` — a plain string
- Agents rebuild their prompt as [SystemMessage, HumanMessage(user_query)] — prior turns are lost

Fix Strategy:
- Update all agent nodes (chat_agent.py, coder_agent.py, etc.)
- Read `state.get("messages", [])` instead of only `user_query`
- Append the new HumanMessage(user_query) to the existing messages list
- Pass the full accumulated messages list to llm.invoke(messages)

Acceptance Criteria:
- User can say "my name is John" → Captain remembers → later "what's my name?" → Captain answers "John"
- Conversation context persists across turns within a session

---

### Phase 3: Migrate to v2 Architecture (Priority: MEDIUM | ETA: 1-2 days)

**Goal:** Replace v1 heuristic agents with v2 lifecycle-managed async agents.

Why v2 is Better:
- Lifecycle management: READY→RUNNING→PAUSED→STOPPED with state transitions
- Pause/resume: Cooperative cancellation via asyncio.Event
- Recovery: Automatic retry with max attempts on FAILED state
- Hot-reload: Runtime agent module reloading without restart
- Hybrid routing: Keyword + LLM fallback instead of keyword-only
- Event bus: Decoupled pub/sub for monitoring, logging, webhooks
- Task queue: Background job execution with cancellation support

Migration Steps:
1. Implement 3 BaseAgent subclasses in src/agents/:
   - chat_agent_v2.py — implements BaseAgent, reuses core/llm_factory.py
   - coder_agent_v2.py — implements BaseAgent, reuses core/llm_factory.py
   - system_agent_v2.py — implements BaseAgent, imports from tools/system_tools.py
2. Wire the v2 Pipeline in main.py:
   - Instantiate AgentRegistry
   - Call `await registry.discover_agents("src/agents")` to auto-register agents
   - Instantiate AgentLifecycleManager(registry, event_bus)
   - Call `create_captain_graph(registry, manager)` from src/graph/state_graph.py
   - Replace v1 graph invocation with v2 graph invocation
3. Start FastAPI Server (Optional via new CLI command)
4. Delete all v1 code once v2 is confirmed working:
   - Delete agents/ directory
   - Delete core/graph.py
   - Delete agents/state.py

Acceptance Criteria:
- CLI chat works with v2 agents
- All 3 agents registered in AgentRegistry in READY state
- agents/ directory deleted, src/agents/ is sole agent source

---

### Phase 4: Stabilize and Pin Dependencies (Priority: LOW | ETA: 1 hour)

**Goal:** Lock dependency versions to prevent future breakage.

Tasks:
1. Run `pip freeze > requirements-pinned.txt`
2. Build clean requirements.txt with == pins for all direct dependencies
3. Add comments documenting version choices and why they were pinned

Acceptance Criteria:
- requirements.txt has == pins only (no >=)
- Fresh install produces working environment

---

## File Reference Map

### Core Entry Points
- main.py — CLI entry, boots graph, voice loop
- config.py — pydantic-settings config (lowercase field names)

### v1 — Current Active (Delete After Phase 3)
- agents/master_supervisor.py — keyword-based intent router
- agents/chat_agent.py — conversational agent node
- agents/coder_agent.py — code generation agent node
- agents/rag_agent.py — document retrieval agent node
- agents/scraper_agent.py — web search + scraping agent node
- agents/comms_agent.py — email/WhatsApp automation agent node
- agents/system_agent.py — hardware metrics + weather agent node
- agents/media_agent.py — unreachable, delete in Phase 1
- agents/state.py — v1 AgentState TypedDict
- core/graph.py — v1 LangGraph StateGraph definition
- core/llm_factory.py — provider-agnostic LLM factory (HAS BUGS — fix in Phase 1)

### v2 — Target Architecture (Will Replace v1 in Phase 3)
- src/agents/base_agent.py — BaseAgent ABC, AgentMetadata, AgentLifecycleState enum
- src/agents/agent_registry.py — AgentRegistry with DI, hot-reload, semver validation
- src/agents/agent_lifecycle_manager.py — AgentLifecycleManager with pause/resume/recovery
- src/agents/state.py — v2 AgentState TypedDict (will be sole survivor)
- src/graph/state_graph.py — v2 LangGraph with hybrid keyword+LLM router
- src/backend/main.py — FastAPI server (never started, wire in Phase 3)
- src/backend/api/v1/router.py — REST + WebSocket endpoints
- src/backend/core/event_bus.py — AsyncEventBus pub/sub
- src/backend/core/task_queue.py — BackgroundTaskQueue async worker
- src/backend/config.py — v2 config (uppercase field names)

### Shared Tools (Used by Both v1 and v2)
- tools/voice.py — speak_text(), listen_to_speech() — in-memory TTS/STT
- tools/rag_tools.py — ingest_document(), query_rag(), rag_search_tool() alias
- tools/search.py — search_web(), multi_search() alias, DuckDuckGo/Google/Tavily
- tools/web_scraper.py — scrape_webpage()
- tools/system_tools.py — get_system_metrics(), run_terminal_command()
- tools/contacts.py — load_contacts(), save_contact(), get_contact_value() fuzzy matching
- tools/email_tool.py — send_email() via SMTP
- tools/whatsapp_tool.py — send_whatsapp_message() via PyWhatKit
- tools/weather.py — get_live_weather()
- tools/image_gen.py — generate_image()

### UI and Utilities
- ui/terminal.py — Rich console rendering: print_banner, render_response, print_system_table
- ui/desktop_gui.py — Animated voice desktop window
- utils/text_utils.py — clean_think_tags() strips LLM reasoning tags

---

## Decision Log

### Why Delete agents/media_agent.py?
- Not registered in core/graph.py as a node
- Not routed to by master_supervisor.py
- Unreachable code adds maintenance burden
- Decision: Delete in Phase 1

### Why Choose v2 Over v1?
- v2 has lifecycle management — v1 does not
- v2 has hot-reload — v1 requires full restart
- v2 has hybrid routing (keyword + LLM) — v1 is keyword-only
- v2 has event bus for observability — v1 has no instrumentation
- v2 is async-first and scales to parallel agent execution
- Decision: Migrate to v2 in Phase 3, delete v1 entirely

### Why Not Keep Both?
- Two competing state schemas
- Two competing graph definitions
- Two competing config files
- Impossible to reason about which code path is active
- Decision: One codebase only — v2 wins

### Why Flatten Before Scaling?
- Current system cannot handle 10 concurrent users
- Adding Redis/Kubernetes/Celery now would hide import errors under infrastructure
- Decision: Make it work on one machine first, scale later

---

## Success Metrics

Phase 1 Complete When:
- python main.py chat runs without crashes
- User query receives a valid response
- No import errors in logs

Phase 2 Complete When:
- Multi-turn conversation works
- Conversation persists within same thread_id

Phase 3 Complete When:
- v2 graph active, v1 graph deleted
- All 3 agents in AgentRegistry in READY state
- agents/ directory deleted

Phase 4 Complete When:
- requirements.txt has == pins only
- Fresh install produces working environment

---

## Anti-Patterns to Avoid

1. "Just one more abstraction" — No. Finish what exists first.
2. "Let me refactor this while I'm here" — No. Fix bugs only, no drive-by refactors.
3. "The new design is better, let me start over" — No. Migrate incrementally.
4. "I'll fix it after I add this feature" — No. Fix crashes before adding features.
5. "It works on my machine" — Not good enough. Pin dependencies.

---

## The Antigravity Manifesto

1. Gravity pulls downward. Start at the ground.
   - Fix import errors before architecting systems.
   - Make the CLI work before building the API.
   - Stabilize one agent before designing six.

2. Build upward only when the foundation holds.
   - Phase 1 must complete before Phase 2 starts.
   - Phase 2 must complete before Phase 3 starts.
   - No skipping phases.

3. Delete the old only after the new works.
   - Keep agents/ until src/agents/ is fully wired and tested.
   - One commit deletes all v1 code at once, not piecemeal.

4. Complexity is earned, not assumed.
   - Async agents, hot-reload, event buses are valuable — but only if basic system works.
   - If basic system does not run, advanced features are technical debt.

5. The loop ends when you stop rewriting and start finishing.
   - Finish Phase 1. Finish Phase 2. Finish Phase 3.
   - Then and only then consider Phase 4+.

---

## Instructions for AI Agents Working on This Project

1. Always check which phase is active.
   - Phase 1 incomplete: only fix crashes, do not add features.
   - Phase 2 incomplete: only wire conversation memory, do not refactor agents.
   - Phase 3 incomplete: only migrate to v2, do not add new tools.

2. Reference this file for architectural decisions.
   - Before creating a new file, check if it already exists in src/.
   - Before proposing a new abstraction, confirm current abstraction is wired and working.

3. Update the Decision Log when making choices.
   - If you delete code, document what it did and why it is gone.
   - If you choose between two approaches, document the reasoning.
   - If you defer a feature, document when it should be revisited.

4. Respect the phase boundaries.
   - Do not implement Phase 3 tasks while Phase 1 is incomplete.
   - The phases are sequenced to minimize risk and maximize learning.

---

## Final Note

This project is not failing because of bad code. The v2 infrastructure is legitimately excellent.
It is failing because two excellent systems exist in parallel and neither is finished.

The antigravity loop happens when you build upward without ensuring the foundation holds.
The exit path: stop building upward, finish the foundation, then build upward once.

Phase 1 fixes take 1-2 hours. After that, Captain will boot and respond to queries.
That is the milestone that breaks the loop. Everything else is downstream from that.