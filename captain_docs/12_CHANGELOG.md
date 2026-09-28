# 📜 Captain AI OS 2.0 — Architectural Changelog & Milestone History

> **Document:** `12_CHANGELOG.md`  
> **Status:** Canonical Project Changelog  
> **Rule:** Only record meaningful architectural, capability, phase, and workflow changes. Do not log minor code formatting edits.

## [2026-09-28] — Phase 3 Hardening: 16kHz Unification, VAD Control & Sample Rate Architecture
- **Phase:** Phase 3 (Voice Input, Voice Output & Clap Control Hardening)
- **Change:**
  - Standardized unified 16kHz mono audio pipeline across `AudioCapture`, `ClapDetector`, `SileroVADDetector`, and `FasterWhisperSTTProvider`.
  - Added zero-dependency `resample_audio` function and automatic input stream resampling boundary in `AudioCapture`.
  - Enforced `vad_enabled` configuration flag in `SileroVADDetector` and `VoiceManager` (honoring disabled state).
  - Added tests for audio resampling (44.1k -> 16k), `vad_enabled` toggle enforcement, and unified configuration defaults.
  - Re-synchronized `00_MASTER_INDEX.md`, `11_CURRENT_STATE.md`, and `12_CHANGELOG.md` with active project reality.
- **Files Affected:** `config.py`, `src/voice/audio_capture.py`, `src/voice/vad.py`, `src/voice/voice_manager.py`, `tests/unit/test_phase3_voice.py`, `captain_docs/`.
- **Tests:** 25 Phase 3 unit tests passing; 231 total tests passing across full repository (`pytest tests/ -q`). Zero failures.
- **Commit:** `4729f3b` (*fix(phase-3): standardize 16kHz audio sample-rate, enforce vad_enabled, and sync state docs*)
- **Status:** `COMPLETE (SOFTWARE ARCHITECTURE COMPLETE & HARDENED)`

---

## [2026-09-28] — Phase 3 Hardening: Genuine SAPI5 WAV Synthesis & Default Chunk Streaming
- **Phase:** Phase 3 (Voice Input, Voice Output & Clap Control Hardening)
- **Change:**
  - Replaced placeholder pseudo-WAV in `Pyttsx3TTSProvider.synthesize_to_bytes` with native Windows SAPI5 `.save_to_file()` exporting genuine 22,050Hz 16-bit mono PCM WAV bytes.
  - Refactored `Pyttsx3TTSProvider.speak()` to stream synthesized audio in 1024-frame chunks via `sounddevice.OutputStream`, invoking `_on_audio_chunk()` on every chunk to drive real-time RMS amplitude to the EMO avatar mouth.
  - Fixed Piper TTS fallback to receive genuine WAV bytes without header corruption.
  - Cleaned documentation paths (`src/audio/` -> `src/voice/` and `providers/`).
- **Commit:** `ee073d7` (*fix(phase-3): implement genuine SAPI5 WAV synthesis, pyttsx3 chunk mouth-sync, and sync docs*)
- **Tests:** 22 Phase 3 unit tests passing; 228 total tests passing.
- **Status:** `COMPLETE`

---

## [2026-09-28] — Phase 3 Hardening: Double-Clap State Machine & Strict Error Handling
- **Phase:** Phase 3 (Voice Input, Voice Output & Clap Control Hardening)
- **Change:**
  - Implemented true double-clap temporal gating state machine in `ClapDetector` ($150\text{ms} \le \Delta t \le 800\text{ms}$) with reverberation rejection.
  - Enforced strict production failure mode in `FasterWhisperSTTProvider` (`allow_mock_fallback=False` default; raises `RuntimeError` on missing model).
  - Wired `amplitude_changed` Qt signal to WebEngine `window.setAudioAmplitude()` for live EMO avatar mouth modulation and visor ring expansion.
  - Resolved PySide6 Qt GUI thread vs asyncio event loop concurrency with dedicated background daemon thread `CaptainVoiceAsyncLoop`.
- **Commit:** `422c441` (*fix(phase-3): implement true double-clap, real audio mouth sync, strict whisper error handling, and robust voice loop*)
- **Tests:** 20 Phase 3 unit tests passing; 226 total tests passing.
- **Status:** `COMPLETE`

---

## [2026-09-28] — Phase 3: Voice Input, Voice Output & Clap Control Initial
- **Phase:** Phase 3 (Voice Input, Voice Output & Clap Control)
- **Change:** Implemented local-first voice interaction subsystem:
  - Acoustic transient clap detector (`STANDBY <-> ACTIVE` toggle).
  - Local neural Voice Activity Detection (Silero VAD) with speech boundary tracking.
  - Faster-Whisper local STT provider (`FasterWhisperSTTProvider`) with background thread inference.
  - Neural local TTS (`PiperTTSProvider`) and native Windows SAPI5 (`Pyttsx3TTSProvider`) with barge-in interruption.
  - Bidirectional 8-state machine synchronization via `StateManager`.
- **Commit:** `f857b2f` (*feat(phase-3): implement voice interaction and clap control*)
- **Tests:** 17 Phase 3 unit tests passing; 223 total tests passing.
- **Status:** `COMPLETE`

---

## [2026-09-26] — Phase 2: Desktop Presence & Companion Verification Complete
- **Phase:** Phase 2 (Desktop Presence & Companion)
- **Change:** Implemented Windows-native desktop container for the 3D EMO avatar:
  - Transparent, frameless, always-on-top overlay window (`CaptainDesktopWindow`) using PySide6 and QWebEngineView.
  - Bidirectional state bridge between `StateManager` (8 states) and EMO WebGL companion.
  - Enforced `STANDBY != HIDDEN` rule (standby keeps pet visible in relaxed breathing state).
  - Added Windows system tray icon and native security confirmation dialog.
- **Commit:** `8665296` (*fix(phase-2): enforce STANDBY != HIDDEN, add WebEngine drag filter, and sync docs/tests*)
- **Tests:** 8 Phase 2 unit tests passing; 214 total tests passing.
- **Status:** `COMPLETE`

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
- **Commit:** `574f279` (`feat(phase-1): harden architecture and establish baseline`).
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
