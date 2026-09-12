# CAPTAIN AI OS 2.0 — ARCHITECTURE MIGRATION & DEPENDENCY MAP

**Document Version:** 1.0.0  
**Status:** Approved for Phase 1 Execution  
**Scope:** Foundation migration mapping covering OLD → NEW → TEST pathways.

---

## 1. Executive Summary

This document governs the safe transition from the legacy dual-architecture codebase (Captain V1 + V2 web hybrid) to **Captain AI OS 2.0 (Windows-Native Voice, Vision, Desktop Autonomous Agent)**.

Per Phase 1 safety constraints:
1. No destructive deletion occurs without a verified migration target and dependency check.
2. Web UI is preserved in Phase 1; desktop-native components run alongside during transition.
3. Plaintext credentials must never be committed; `.gitignore` and `.env.example` maintain strict hygiene.
4. Legacy tests must have their behavioral coverage audited and migrated before removal.
5. All 180 baseline tests must remain green or be mapped to explicit upgraded suites.

---

## 2. File-by-File Migration Matrix

| Legacy / Source Path | Proposed Action | Target Architecture Path | Key Functionality & Rationale | Test Coverage |
| :--- | :--- | :--- | :--- | :--- |
| `supabase captain password.txt` | **DELETED** | Environment Variable `SUPABASE_KEY` / `.env` | Plaintext database password stored in working tree. Verified removed; never committed to git history. | Manual / Git verification |
| `captain-AI-assistant/` (nested) | **DELETED** | Root Repository (`/`) | Redundant recursive clone causing pytest collection collisions. Verified not tracked in HEAD. | `pytest tests/` |
| `core/llm_factory.py` | **MIGRATE & DELETE** | `providers/llm/` & `src/backend/core/model_manager.py` | Multi-provider fallback (Ollama, OpenAI, Gemini). Migrate to unified provider abstraction `providers/llm/` before removing. | `tests/unit/test_providers.py` + `tests/unit/test_new_providers.py` |
| `config.py` | **CONSOLIDATE** | Centralized `config.py` | Central Pydantic Settings unifying legacy lowercase and backend uppercase keys, adding Phase 1 desktop settings. | `tests/test_backend_core.py`, `tests/integration/test_e2e_api.py` |
| `src/backend/config.py` | **CONSOLIDATE** | Re-exports centralized `config.py` | Alias layer for backward compatibility across all 180 existing tests. | `tests/unit/*`, `tests/integration/*` |
| `tests/unit/test_voice_listening_engine.py` | **AUDITED / RETAINED FOR PHASE 3** | Not in origin/main HEAD; target is `tests/unit/test_voice_engine.py` | Was a scratch assertion checking web speech removal. Web UI preserved for now; native STT/VAD tests slated for Phase 3. | `tests/unit/test_v1_v9_synchronization.py` |
| `core/graph.py` | **DEPRECATED / RETIRE LATER** | `src/graph/state_graph.py` | Legacy V1 LangGraph supervisor graph. Unreferenced by main runtime. Retained in Phase 1 to prevent breaking old imports. | `tests/unit/test_graph.py` (already uses `src.graph.state_graph`) |
| `agents/` (`chat_agent.py`, `coder_agent.py`, etc.) | **MAINTAIN FOR PHASE 1** | `src/agents/` | V1 function-based agent nodes. Updated to import from `providers.llm` to decouple from `core/llm_factory.py`. | Legacy compatibility |
| `src/backend/core/model_manager.py` | **UPGRADE** | Integrated with `providers/llm/` | High-performance model manager with IPv4 fallback and streaming tokens. Retained and augmented. | `tests/test_backend_core.py`, `tests/unit/test_runtime_architecture_fix.py` |
| `src/backend/core/voice_engine.py` | **PRESERVE / UPGRADE IN PHASE 3** | Native STT/TTS Provider | Currently contains mock/placeholder sound logic. Kept for Phase 1; replaces in Phase 3. | `tests/unit/test_v1_v9_synchronization.py` |
| `src/backend/core/vision_engine.py` | **PRESERVE / UPGRADE IN PHASE 4** | Native Screen Observation Provider | Currently contains mock screenshot logic. Kept for Phase 1; replaces in Phase 4. | `tests/unit/test_v1_v9_synchronization.py` |
| `main.py` | **PRESERVE IN PHASE 1** | Future unified entrypoint | Runs FastAPI web backend currently. Do not replace until desktop runtime is validated. | End-to-end API integration suite |
| `ui/web/` | **PRESERVE IN PHASE 1** | Dual Web/Desktop UI | Preserved completely during Phase 1 foundation rebuild. | `test_frontend_volume1.py` through `test_frontend_volume8.py` |

---

## 3. Phase 1 Foundation: New Architecture Additions

```mermaid
graph TD
    subgraph Config Layer
        C[config.py (Central Pydantic Settings)]
        BC[src/backend/config.py (Re-export Alias)]
        C --> BC
    end

    subgraph State & Lifecycle Layer
        AS[app/state.py (CaptainState Machine)]
        AR[app/runtime.py (AppRuntime Coordinator)]
        AS --> AR
    end

    subgraph Provider Abstraction Layer
        PB[providers/base.py]
        PLLM[providers/llm/base.py]
        POL[providers/llm/ollama.py]
        PGEN[providers/llm/factory.py]
        PB --> PLLM
        PLLM --> POL
        PLLM --> PGEN
    end

    C --> AR
    PGEN --> AR
    AR --> MM[src/backend/core/model_manager.py]
```

### New Modules Introduced in Phase 1:
1. `config.py` (Centralized Rebuild):
   - LLM, Vision, STT, TTS configurations.
   - Ollama connection & fallback parameters.
   - Double-clap audio threshold & timing window (for Phase 2 prep).
   - Screen observation resolution, FPS, monitor index (for Phase 4 prep).
   - Security/confirmation policies & risk boundaries.
   - Local directory management (`./data/`, `./logs/`, `./data/scratch/`, `./data/memory/`).
2. `app/state.py`:
   - `AppState` Enum: `STANDBY`, `ACTIVE`, `LISTENING`, `THINKING`, `OBSERVING`, `EXECUTING`, `SPEAKING`, `ERROR`.
   - `StateTransitionEvent`: Captures timestamp, old state, new state, trigger reason, and metadata.
   - `StateManager`: Validates allowed state transitions, broadcasts state changes via subscribers/event bus, and logs telemetry.
3. `app/runtime.py`:
   - `AppRuntime`: Lifecycle coordinator managing initialization, component health, state manager, provider registrations, and graceful shutdown.
4. `providers/base.py`:
   - Abstract base classes: `BaseProvider`, `LLMProvider`, `VisionProvider`, `STTProvider`, `TTSProvider`.
5. `providers/llm/`:
   - `base.py`: Chat message structures, token stream chunks, and abstract `BaseLLM`.
   - `ollama.py`: Robust local Ollama provider preserving existing IPv4 retry & streaming logic.
   - `factory.py`: Unified provider factory migrating `core/llm_factory.py` functionality with graceful fallbacks.

---

## 4. Verification & Validation Protocol

Each modification must strictly satisfy:
1. **Zero Regression**: All 180 existing baseline tests must pass.
2. **Phase 1 Test Suite**: New unit tests covering `app/state.py`, `app/runtime.py`, `config.py`, and `providers/` must pass 100%.
3. **Clean Environment**: No plaintext secrets in repository or history.

---

## 5. Phase 2: Existing Pet → Current Rendering → PySide6 Integration Approach

### A. Existing Pet Identification
- **Visual Identity**: 3D EMO Desktop AI Robot Pet Character.
- **Source Location**: `ui/web/app.js` & `ui/web/app_v33.js` (lines 872–1266).
- **DOM & Stage Canvas**: `ui/web/index.html` (`<canvas id="three-webgl-canvas">` and `.jarvis-core-container`).
- **Styling & Shaders**: `ui/web/style.css` (lines 42–55).

### B. Current Rendering Technology
- **3D Geometry & Meshes**: Three.js (r128) WebGL scene.
  - Head Shell: Dark charcoal matte chassis (`BoxGeometry(2.3, 2.1, 1.9)`, `#1c1d22`).
  - Silver Visor Bezel: Metal rim (`PlaneGeometry(1.85, 1.45)`, `#4a4d5a`).
  - Visor Screen: Canvas-backed texture (`CanvasTexture`, `#00f2fe` neon glow, `shadowBlur: 20`).
  - Headphones: Smooth cubic Bezier arch (`TubeGeometry`, `#4e2a84` purple), earcups (`#22242e`), glowing cyan LED rings (`#00f2fe`).
  - Robot Feet: Dual rounded foot pods (`BoxGeometry(0.85, 0.38, 1.25)`, `#16171d`).
  - Table Stage Podium: Grounding contact shadow, dark stage disk, metallic ring edge, and skirt.
- **Dynamic LED Facial Expressions**: 18+ expressions (`happy`, `blinking`, `speaking` with 4-frame lip-sync mouth engine, `thinking` monocle, `cool`, `laughing`, `angry`, `shy`, `salute`, `love`, `star`, etc.).
- **Animations**: Idle floating harmonic bob, foot stepping motion, natural blinking timer (150ms every 3.2s), rotational tracking.

### C. PySide6 Desktop Integration Approach
- **Core Principle**: SAME CAPTAIN AGENT + SAME CAPTAIN PET + NEW WINDOWS DESKTOP CONTAINER.
- **Native Container (`ui/desktop/pet_window.py`)**:
  - PySide6 frameless, transparent, always-on-top desktop overlay window (`Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WA_TranslucentBackground`).
  - Draggable across Windows desktop with persistent coordinate saving.
  - System Tray integration with background state persistence.
  - Security confirmation modal infrastructure.
- **Pet WebGL Host (`ui/desktop/pet.html` & `ui/desktop/pet_view.js`)**:
  - Embedded `QWebEngineView` with transparent background.
  - Hosts the EXACT existing Three.js 3D EMO pet scene, geometries, materials, LED face expressions, and lip-sync mouth engine.
  - Zero redesign, zero asset loss, 100% pixel-perfect preservation.
- **State Machine Bridge (`app/state.py` ↔ Pet)**:
  - `STANDBY` → Pet hidden (low power mode).
  - `ACTIVE` → Pet visible (`happy`).
  - `LISTENING` → Pet alert / perked ears (`cool` / attentive).
  - `THINKING` → Monocle thinking eye (`thinking`).
  - `OBSERVING` → Screen observation inspection posture.
  - `EXECUTING` → Action / focused expression.
  - `SPEAKING` → Real-time lip-sync mouth animation flap.
  - `ERROR` → Alert expression (`angry`).

