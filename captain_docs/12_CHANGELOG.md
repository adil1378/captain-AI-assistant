# 📜 Captain AI OS 2.0 — Architectural Changelog & Milestone History

> **Document:** `12_CHANGELOG.md`  
> **Status:** Canonical Project Changelog  
> **Rule:** Only record meaningful architectural, capability, phase, and workflow changes. Do not log minor code formatting edits.

---

## [2026-09-23] — Phase 1: Architecture Hardening & Baseline Complete
- **Phase:** Phase 1 (Architecture Hardening & Baseline)
- **Change:** Completed comprehensive 14-step architectural audit across runtime, state machine, agent graph, tool gateway, dual memory, and UI. Implemented test isolation hardening via canonical `pytest.ini` and `.gitignore` update to isolate external code in `github_projects/Friday`, resolving root module shadowing. Verified 100% test health (206/206 tests passing).
- **Reason:** Guarantee a stable, hardened, fully verifiable architectural baseline before beginning Phase 3 voice and audio engine implementation.
- **Files Affected:**
  - `pytest.ini` (Created)
  - `.gitignore` (Updated to ignore `github_projects/`)
  - `captain_docs/03_ARCHITECTURE.md`
  - `captain_docs/11_CURRENT_STATE.md`
  - `captain_docs/12_CHANGELOG.md`
- **Tests:** 206 automated unit & integration tests passing (`pytest -q`).
- **Commit:** Pending Phase 1 commit (`feat(phase-1): harden architecture and establish baseline`).
- **Status:** `COMPLETE`

---

## [2026-09-23] — Phase 0: Project Knowledge System Initialization
- **Phase:** Phase 0 (Continuity & Knowledge Engineering)
- **Change:** Created permanent, portable, agent-readable Project Knowledge System in `captain_docs/` containing 13 authoritative specification files. Established strict 20-rule development operating contract and 8-phase roadmap gating.
- **Reason:** Provide seamless continuity for Antigravity, Codex, Claude Code, and future developers without dependency on previous conversation context.
- **Files Created:**
  - `captain_docs/00_MASTER_INDEX.md`
  - `captain_docs/01_VISION.md`
  - `captain_docs/02_PRODUCT_SPEC.md`
  - `captain_docs/03_ARCHITECTURE.md`
  - `captain_docs/04_WORKFLOW.md`
  - `captain_docs/05_CAPABILITIES.md`
  - `captain_docs/06_PHASES.md`
  - `captain_docs/07_INTERACTION_MODEL.md`
  - `captain_docs/08_SECURITY.md`
  - `captain_docs/09_DEVELOPMENT_RULES.md`
  - `captain_docs/10_GITHUB_WORKFLOW.md`
  - `captain_docs/11_CURRENT_STATE.md`
  - `captain_docs/12_CHANGELOG.md`
- **Tests:** Verified 206 automated tests passing in `tests/` (`pytest tests/ -q`). Zero failures.
- **Commit:** `feat(phase-1): harden architecture and establish baseline`
- **Status:** `COMPLETE`

---

## [2026-09-22] — Phase 2: Native Desktop Container & Pet Integration
- **Phase:** Phase 2 (Desktop Presence & Interaction Foundation)
- **Change:** Integrated existing 3D EMO pet into a native PySide6 desktop container with frameless, transparent, always-on-top windowing. Implemented bidirectional Qt state synchronization and native `SecurityConfirmationDialog`.
- **Reason:** Transition Captain from a terminal-only CLI to an ambient, persistent desktop companion.
- **Files Affected:**
  - `ui/desktop/pet_window.py` (container and SecurityConfirmationDialog)
  - `ui/desktop/__init__.py`
  - `ui/desktop/pet.html`
  - `ui/desktop/pet_view.js`
  - `main.py` (added `desktop` command)
  - `tests/unit/test_phase2_desktop_pet.py`
- **Tests:** 8 dedicated tests passing in `tests/unit/test_phase2_desktop_pet.py`.
- **Commit:** `bdfaf69` (*feat: complete phase 2 native desktop container and pet integration*)
- **Status:** `COMPLETE`

---

## [2026-09-21] — Phase 1: Core Foundation & Runtime Hardening
- **Phase:** Phase 1 (Architecture Hardening & Baseline)
- **Change:** Established centralized Pydantic `Settings` model in `config.py`, built strict 8-state `AppState` machine in `app/state.py`, and implemented singleton `AppRuntime` coordinator in `app/runtime.py`. Unified provider abstractions and LangGraph multi-agent routing.
- **Reason:** Replace disconnected V1 prototype scripts with an enterprise-grade multi-agent runtime kernel.
- **Files Affected:**
  - `config.py`
  - `app/state.py`
  - `app/runtime.py`
  - `src/agents/` (6 V2 agents)
  - `src/graph/state_graph.py`
  - `src/graph/router.py`
  - `tests/unit/test_phase1_foundation.py`
- **Tests:** 18 dedicated tests passing in `tests/unit/test_phase1_foundation.py`.
- **Commit:** `65c3e1f` (*feat: establish Captain 2.0 foundation*)
- **Status:** `COMPLETE`

---

## [2026-09-19] — Runtime Architecture Fixes & Zero-Trust Boundary
- **Phase:** Pre-Phase 1 Hardening
- **Change:** Implemented centralized `ToolInvocationLayer` security boundary, `SystemAgent` intent disambiguation, RAG relevance distance thresholding, and thread-scoped memory clearing.
- **Reason:** Prevent unauthorized tool execution, false-positive intent routing, and memory contamination across sessions.
- **Files Affected:**
  - `src/tools/tool_invocation_layer.py`
  - `src/graph/router.py`
  - `memory/vector_memory.py`
  - `memory/session_memory.py`
  - `tests/unit/test_runtime_architecture_fix.py`
- **Tests:** 9 dedicated regression tests passing in `tests/unit/test_runtime_architecture_fix.py`.
- **Commit:** `1f392a4` (*Complete runtime architecture fixes*)
- **Status:** `COMPLETE`
