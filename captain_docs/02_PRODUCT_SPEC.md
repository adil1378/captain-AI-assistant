# 📋 Captain AI OS 2.0 — Product Specification & Capability Matrix

> **Document:** `02_PRODUCT_SPEC.md`  
> **Status:** Authoritative Capability Audit  
> **Truthfulness Rule:** Statuses strictly reflect actual code in `D:\captain`, not aspirational claims.

---

## 1. Status Classification Definitions

- `IMPLEMENTED`: Fully written, integrated with the runtime, and validated with automated tests.
- `PARTIAL`: Functional in code but missing production refinement, edge-case handling, or complete subsystem integration.
- `PLACEHOLDER`: Exists as a stub, mock, simulated response, or wrapper with hardcoded/minimal functionality.
- `PLANNED`: Specifically scoped and designed within the 8-phase roadmap; implementation has not yet begun.
- `FUTURE`: Long-term evolutionary goal beyond the initial 8-phase scope.

---

## 2. Master Capability Matrix

| Capability | Category | Current Status | Description & Actual Code State | Target Phase |
| :--- | :--- | :--- | :--- | :--- |
| **Voice Input (STT)** | Voice & Audio | `PARTIAL` | Uses basic `SpeechRecognition` with Google/Sphinx in `tools/voice.py`. Latency is high, requires manual trigger, lacks local neural model. | Phase 3 |
| **Voice Output (TTS)** | Voice & Audio | `PARTIAL` | Uses basic `pyttsx3` in `tools/voice.py`. Synchronous, robotic speech; no real-time phoneme or amplitude streaming to avatar. | Phase 3 |
| **Clap Activation** | Audio Sensing | `PLANNED` | Scoped for Phase 3. Config keys exist in `config.py` (`WAKE_WORD`), but transient audio clap detector is not yet implemented. | Phase 3 |
| **Voice Activity (VAD)** | Audio Sensing | `PLANNED` | Config keys exist in `config.py` (`VAD_AGGRESSIVENESS`, `VAD_SILENCE_MS`), but Silero/WebRTC VAD loop is not yet integrated. | Phase 3 |
| **Keyboard Input** | Input Surface | `IMPLEMENTED` | Terminal CLI loop in `main.py` and Web UI chat input fully accept text instructions. | Phase 1 |
| **Desktop Companion (EMO)** | Presentation | `IMPLEMENTED` | PySide6 frameless transparent window (`ui/desktop/pet_window.py`) hosting 3D WebGL avatar (`pet.html`) with Qt state synchronization. | Phase 2 |
| **Web Dashboard UI** | Presentation | `IMPLEMENTED` | Glassmorphic web dashboard in `ui/web/` connected via FastAPI REST and WebSockets (`/api/v1/chat`). | Phase 1 |
| **State Machine Engine** | Runtime Core | `IMPLEMENTED` | Strict 8-state transition machine (`app/state.py`) with listener callbacks and validation. | Phase 1 |
| **Runtime Coordinator** | Runtime Core | `IMPLEMENTED` | Singleton `AppRuntime` in `app/runtime.py` managing lifecycle, signals, and providers. | Phase 1 |
| **Micro-Kernel EventBus** | Core Messaging | `IMPLEMENTED` | Async Pub/Sub `EventBus` in `src/backend/core/event_bus.py`. | Phase 1 |
| **Multi-Agent Engine** | LangGraph | `IMPLEMENTED` | 6 specialized agents (`ConversationAgent`, `CodingAgent`, `SystemAgent`, `RagAgent`, `SearchAgent`, `CommsAgent`) registered and managed in `src/graph/state_graph.py`. | Phase 1 |
| **Hybrid Intent Routing** | Routing | `IMPLEMENTED` | Regex/keyword fast-path with fallback to LLM intent classification in `src/graph/router.py`. | Phase 1 |
| **Screen Capture** | Vision | `PARTIAL` | Basic `pyautogui.screenshot()` wrapper exists in `tools/system_tools.py`. No multi-monitor awareness, no visual diffing, no real-time stream. | Phase 4 |
| **OCR & Text Extraction** | Vision | `PLANNED` | Scoped for Phase 4. Needs Tesseract / Windows Media OCR integration for active window text extraction. | Phase 4 |
| **Visual Understanding** | Vision | `PLACEHOLDER` | LLM vision config (`VISION_MODEL=llava`) exists, but closed-loop visual reasoning on desktop UI elements is not yet active. | Phase 4 |
| **Active Window Awareness** | Desktop Control | `PARTIAL` | Window title detection exists via Win32 / psutil in `src/backend/`, but lacks UI tree parsing and coordinate bounding boxes. | Phase 4 / 5 |
| **Mouse Control** | Desktop Control | `PLANNED` | `pyautogui` is in `requirements.txt`, but canonical safe mouse movement and click tools under the Tool Gateway are not yet built. | Phase 5 |
| **Keyboard Automation** | Desktop Control | `PLANNED` | Low-level hotkey/typing automation under the Tool Gateway is scoped for Phase 5. | Phase 5 |
| **Application Launching** | Desktop Control | `PARTIAL` | `subprocess` execution in `SystemAgent`, but lacks structured desktop app registry and window focus management. | Phase 5 |
| **Terminal / CLI Tool** | Desktop Control | `IMPLEMENTED` | `SystemAgent` executes system commands with timeout and permission checks. | Phase 1 |
| **File Operations** | Storage & OS | `IMPLEMENTED` | Read, write, list, and search files via `tools/file_tools.py` under `ToolInvocationLayer`. | Phase 1 |
| **Web Search** | Knowledge | `IMPLEMENTED` | DuckDuckGo, Tavily, and SerpAPI multi-provider fallback in `src/agents/search_agent.py` and `providers/`. | Phase 1 |
| **RAG Document Search** | Knowledge | `IMPLEMENTED` | Ingestion and semantic retrieval of PDF/DOCX via ChromaDB in `src/agents/rag_agent.py` and `tools/rag_tools.py`. | Phase 1 |
| **Short-Term Session Memory** | Memory | `IMPLEMENTED` | Sliding-window memory buffer in `memory/session_memory.py`. | Phase 1 |
| **Long-Term Vector Memory** | Memory | `IMPLEMENTED` | ChromaDB vector store with sentence transformers and distance thresholding in `memory/vector_memory.py`. | Phase 1 |
| **External Comms** | Integration | `IMPLEMENTED` | Email (SMTP), Telegram bot, and WhatsApp (Twilio) dispatchers in `src/agents/comms_agent.py`. | Phase 1 |
| **Tool Gateway & Security** | Security | `IMPLEMENTED` | `ToolInvocationLayer` enforcing schema validation, permission checks, timeouts, and native confirmation dialogs. | Phase 1 / 2 |
| **Autonomous Control Loop** | Reasoning | `PLANNED` | Multi-step Observe $\rightarrow$ Reason $\rightarrow$ Act $\rightarrow$ Observe $\rightarrow$ Verify iterative planning loop is scoped for Phase 6. | Phase 6 |
| **Task Continuation** | Memory & Tasks | `PLANNED` | Long-running task resumption across app restarts scoped for Phase 7. | Phase 7 |

---

## 3. High-Risk Capabilities Requiring Human Confirmation

The following actions are formally classified as `HIGH_RISK` or `CRITICAL` in `config.py` and require explicit human approval via the native PySide6 `SecurityConfirmationDialog` before execution:
1. **Arbitrary Shell Execution:** Running terminal scripts, powershell commands, or external binaries.
2. **Destructive File Manipulation:** File deletion, overwriting existing non-scratch files, or directory tree removal.
3. **External Communication Dispatch:** Sending WhatsApp messages, Telegram messages, or emails to real recipients.
4. **Desktop Automation (Autonomous Mouse/Keyboard):** Submitting forms, clicking external application dialogs, or entering credentials.
5. **System Process Modification:** Killing external processes or changing Windows system settings.
