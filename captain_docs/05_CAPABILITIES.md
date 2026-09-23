# ⚙️ Captain AI OS 2.0 — Structured Capability Registry

> **Document:** `05_CAPABILITIES.md`  
> **Status:** Canonical Capability Catalog  
> **Scope:** Definitive technical registry covering all system capabilities.

---

## 1. Voice & Audio Sensing Capabilities

### 1.1. Voice Input (Speech Capture)
- **Capability:** Voice Input & Microphone Streaming
- **Purpose:** Ingest human voice from system microphone as primary conversational channel.
- **Why Captain needs it:** Enables natural ambient desktop communication without keyboard dependency.
- **Current status:** `PARTIAL`
- **Current implementation:** `tools/voice.py` uses `SpeechRecognition.Recognizer().listen()` with fixed 5-second blocking timeouts.
- **Target implementation:** Non-blocking async PyAudio/sounddevice ring buffer feeding streaming VAD.
- **Dependencies:** `sounddevice`, `numpy`, `SpeechRecognition`
- **Input:** Raw PCM 16kHz mono audio stream.
- **Output:** Normalized audio chunk byte buffers.
- **Security level:** `LOW` (Local audio capture).
- **User interaction:** Ambient or triggered via clap / microphone icon.
- **Related phase:** Phase 3
- **Tests:** `tests/test_v1_v9_synchronization.py::test_voice_engine`
- **Known limitations:** Current implementation blocks the event loop thread during capture.

---

### 1.2. Clap Activation Detection
- **Capability:** Acoustic Transient Clap Detector
- **Purpose:** Detect double-clap acoustic signatures to toggle Captain between `STANDBY` and `ACTIVE`.
- **Why Captain needs it:** Provides immediate, hands-free physical activation without requiring hotkeys or waking up false positives.
- **Current status:** `PLANNED`
- **Current implementation:** None. Configuration keys exist in `config.py` (`WAKE_WORD`).
- **Target implementation:** Continuous noise-floor estimation, bandpass filter (2kHz-4kHz), rapid rise-time transient envelope detector, and inter-transient timing validation (200ms-600ms).
- **Dependencies:** `sounddevice`, `scipy` / `numpy`
- **Input:** Continuous low-power audio stream.
- **Output:** Boolean event (`on_clap_detected`).
- **Security level:** `LOW`
- **User interaction:** Physical hand clapping 👏.
- **Related phase:** Phase 3
- **Tests:** Pending Phase 3 implementation test suite.
- **Known limitations:** Must guard against typing noises, mouse clicks, and door slams.

---

### 1.3. Voice Activity Detection (VAD)
- **Capability:** Neural Voice Activity Detection
- **Purpose:** Accurately segment speech from background silence and ambient office noise.
- **Why Captain needs it:** Prevents sending blank audio or silence to the speech recognizer, reducing latency.
- **Current status:** `PLANNED`
- **Current implementation:** None (relies on rudimentary energy thresholds in `SpeechRecognition`).
- **Target implementation:** Local Silero VAD model evaluating 30ms audio windows with dynamic silence hang-time.
- **Dependencies:** `onnxruntime` or `torch`
- **Input:** 16kHz PCM audio frames.
- **Output:** Speech presence probability $(0.0 - 1.0)$ and speech start/end boundaries.
- **Security level:** `LOW`
- **User interaction:** Transparent to user.
- **Related phase:** Phase 3
- **Tests:** Pending Phase 3 test suite.
- **Known limitations:** None when configured with proper hang-time window.

---

### 1.4. Speech-to-Text (STT)
- **Capability:** Local Neural Speech-to-Text
- **Purpose:** Transcribe captured speech audio into UTF-8 text.
- **Why Captain needs it:** Understand user spoken instructions completely offline without privacy leakage.
- **Current status:** `PARTIAL`
- **Current implementation:** `tools/voice.py` calls Google Web Speech API (fallback) or local Sphinx.
- **Target implementation:** `Faster-Whisper` (int8/float16 quantized CTranslate2 model) running locally on CPU/GPU.
- **Dependencies:** `faster-whisper`, `ctranslate2`
- **Input:** 16kHz speech WAV/PCM buffer.
- **Output:** Transcribed text string with confidence scores and timestamps.
- **Security level:** `LOW`
- **User interaction:** Spoken user command.
- **Related phase:** Phase 3
- **Tests:** Basic invocation tests in `tests/test_v1_v9_synchronization.py`.
- **Known limitations:** Current Google API fallback requires active internet; Sphinx has poor accuracy.

---

### 1.5. Text-to-Speech (TTS)
- **Capability:** Neural Audio Synthesis & Amplitude Streaming
- **Purpose:** Convert agent response strings into natural speech and stream audio waveform to the EMO avatar.
- **Why Captain needs it:** Provides conversational spoken feedback while synchronizing the 3D companion's mouth movements.
- **Current status:** `PARTIAL`
- **Current implementation:** `tools/voice.py` uses `pyttsx3` (robotic SAPI5 engine on Windows).
- **Target implementation:** Local `Kokoro-82M` or `Piper` neural TTS with async chunk streaming and real-time FFT amplitude output.
- **Dependencies:** `pyttsx3` (current), `sounddevice`
- **Input:** Synthesized response text.
- **Output:** Spoken audio playback + FFT amplitude buffer $(0.0 - 1.0)$ emitted to Qt event loop.
- **Security level:** `LOW`
- **User interaction:** Auditory output.
- **Related phase:** Phase 3
- **Tests:** `tests/test_v1_v9_synchronization.py`
- **Known limitations:** `pyttsx3` speech sounds artificial and cannot stream live phonemes/amplitudes.

---

## 2. Vision & Screen Observation Capabilities

### 2.1. Screen Capture
- **Capability:** Desktop Screen Capture
- **Purpose:** Take high-resolution snapshots of the active monitor or specific application windows.
- **Why Captain needs it:** Serves as the eyes for Captain's "Observe" phase.
- **Current status:** `PARTIAL`
- **Current implementation:** `tools/system_tools.py::take_screenshot()` wraps `pyautogui.screenshot()`.
- **Target implementation:** Windows Desktop Duplication API (DirectX / `mss`) for high-frame rate multi-monitor capture with zero memory copies.
- **Dependencies:** `mss`, `pyautogui`, `PIL`
- **Input:** Monitor index or window handle (HWND).
- **Output:** In-memory RGB image buffer or JPEG artifact.
- **Security level:** `MEDIUM` (Access to visible desktop contents).
- **User interaction:** Automated during observation phase.
- **Related phase:** Phase 4
- **Tests:** Basic file creation in `tests/test_file_tools.py`.
- **Known limitations:** `pyautogui.screenshot()` is slow (~200ms-400ms per frame).

---

### 2.2. OCR & UI Text Extraction
- **Capability:** Desktop Text & Element Recognition
- **Purpose:** Extract visible text, error messages, code lines, and button labels from screen captures.
- **Why Captain needs it:** Allows Captain to read stack traces, IDE text, and browser dialogs without copy-pasting.
- **Current status:** `PLANNED`
- **Current implementation:** None.
- **Target implementation:** Windows Media OCR API (`winocr`) or Tesseract OCR with localized bounding boxes.
- **Dependencies:** `pytesseract` or `winsdk.windows.media.ocr`
- **Input:** RGB image buffer.
- **Output:** Structured bounding boxes: `[{text, x, y, width, height, confidence}]`.
- **Security level:** `MEDIUM`
- **User interaction:** Automated during observation.
- **Related phase:** Phase 4
- **Tests:** Pending Phase 4 test suite.
- **Known limitations:** Low contrast or non-standard fonts can reduce OCR accuracy.

---

### 2.3. Visual UI Understanding
- **Capability:** Multimodal Screen Grounding & Reasoning
- **Purpose:** Map user intent to UI elements (e.g. locate the "Run Tests" button or the failing line of code).
- **Why Captain needs it:** Enables grounding natural language instructions in physical desktop coordinates.
- **Current status:** `PLACEHOLDER`
- **Current implementation:** Config keys exist in `config.py` (`VISION_MODEL=llava`).
- **Target implementation:** Multimodal LLM reasoning over screen screenshot + OCR coordinates to generate $(x, y)$ action targets.
- **Dependencies:** Ollama (Llava/Qwen-VL) or cloud vision APIs.
- **Input:** Screenshot image + User Goal.
- **Output:** Semantic description of state + target $(x, y)$ coordinates.
- **Security level:** `MEDIUM`
- **User interaction:** Automated.
- **Related phase:** Phase 4
- **Tests:** Pending Phase 4 test suite.
- **Known limitations:** Local 7B vision models can produce hallucinated bounding boxes without coordinate validation.

---

## 3. Desktop Automation & OS Control Capabilities

### 3.1. Mouse Control
- **Capability:** Autonomous Mouse Movement & Clicking
- **Purpose:** Position cursor, click, double-click, right-click, and drag on the Windows desktop.
- **Why Captain needs it:** Allows interacting with desktop applications that lack CLI interfaces.
- **Current status:** `PLANNED`
- **Current implementation:** None under canonical Tool Gateway (`pyautogui` installed in venv).
- **Target implementation:** Safe mouse controller under `ToolInvocationLayer` with bounded coordinates, smooth bezier curves, and fail-safe corner aborts.
- **Dependencies:** `pyautogui` or Win32 `SendInput`.
- **Input:** $(x, y)$ coordinate, button (`left`/`right`/`double`), drag vector.
- **Output:** Physical cursor movement and OS click event.
- **Security level:** `HIGH` (Requires human confirmation or explicit session permission).
- **User interaction:** Visual cursor movement on screen.
- **Related phase:** Phase 5
- **Tests:** Pending Phase 5 test suite.
- **Known limitations:** Misaligned coordinates can click unintended UI elements.

---

### 3.2. Keyboard Automation
- **Capability:** Virtual Keystroke & Typing Injection
- **Purpose:** Type text strings and dispatch keyboard shortcuts (e.g. `Ctrl+S`, `Alt+Tab`).
- **Why Captain needs it:** Allows typing into IDEs, search bars, and executing hotkeys.
- **Current status:** `PLANNED`
- **Current implementation:** None under canonical Tool Gateway.
- **Target implementation:** Win32 `SendInput` / `pyautogui.write()` with configurable typing delays and clipboard pasting.
- **Dependencies:** `pyautogui` or `pynput`.
- **Input:** Keystroke sequence or text payload.
- **Output:** Injected OS keyboard events.
- **Security level:** `HIGH` (Can trigger irreversible actions).
- **User interaction:** Text appears in focused window.
- **Related phase:** Phase 5
- **Tests:** Pending Phase 5 test suite.
- **Known limitations:** Window focus loss can result in typing into the wrong application.

---

### 3.3. Application & Window Control
- **Capability:** Windows Process & Window Management
- **Purpose:** Launch desktop applications, switch window focus, minimize, maximize, and query window trees.
- **Why Captain needs it:** Brings required apps (VS Code, Chrome, Terminal) to foreground before acting.
- **Current status:** `PARTIAL`
- **Current implementation:** `subprocess.Popen` in `SystemAgent` and basic process enumeration in `tools/system_tools.py`.
- **Target implementation:** Full Win32 HWND manager via `pywin32` (`SetForegroundWindow`, `EnumWindows`, `ShowWindow`).
- **Dependencies:** `psutil`, `pywin32`
- **Input:** Application name, executable path, or window title regex.
- **Output:** Process ID (PID) and Window Handle (HWND).
- **Security level:** `MEDIUM` / `HIGH`
- **User interaction:** Application opens or gains focus.
- **Related phase:** Phase 5
- **Tests:** `tests/test_backend_core.py`
- **Known limitations:** Elevating permissions (UAC) cannot be automated directly.

---

### 3.4. Terminal & Shell Execution
- **Capability:** Asynchronous Subprocess Shell Execution
- **Purpose:** Execute PowerShell and CMD commands, run compilers, package managers, and test suites.
- **Why Captain needs it:** Core driver for software engineering, running tests, and OS diagnostics.
- **Current status:** `IMPLEMENTED`
- **Current implementation:** `src/agents/system_agent.py` and `tools/system_tools.py::execute_shell_command()` with timeout limits.
- **Target implementation:** Fully integrated into `ToolInvocationLayer` with real-time stream output and zero-trust permission verification.
- **Dependencies:** `asyncio.subprocess`, `shlex`
- **Input:** Shell command string, working directory, timeout.
- **Output:** `{stdout, stderr, exit_code}`.
- **Security level:** `CRITICAL` (Mandatory confirmation for non-whitelisted commands).
- **User interaction:** Confirmation prompt on desktop overlay.
- **Related phase:** Phase 1 / Phase 5
- **Tests:** `tests/unit/test_runtime_architecture_fix.py::test_system_agent_intent_disambiguation`
- **Known limitations:** Long-running daemon processes must be managed via dedicated task handles.

---

### 3.5. File Manipulation
- **Capability:** Secure File System CRUD
- **Purpose:** Read, write, create, search, and edit files on disk.
- **Why Captain needs it:** Allows inspecting project files, applying code diffs, and reading logs.
- **Current status:** `IMPLEMENTED`
- **Current implementation:** `tools/file_tools.py` (`read_file`, `write_file`, `list_directory`, `search_files`).
- **Target implementation:** Preserved under `ToolInvocationLayer` with AST diff validation.
- **Dependencies:** Built-in `pathlib`, `os`.
- **Input:** File path, content string, line offsets.
- **Output:** File contents, status dictionaries.
- **Security level:** `MEDIUM` for read, `HIGH` for write, `CRITICAL` for delete.
- **User interaction:** Notification or confirmation dialog for file edits.
- **Related phase:** Phase 1
- **Tests:** `tests/test_file_tools.py`
- **Known limitations:** Large binary files must be handled with streaming buffers.

---

## 4. Knowledge, Search & Coding Capabilities

### 4.1. Web Search
- **Capability:** Real-Time Internet Search
- **Purpose:** Query search engines to find documentation, bug solutions, and live information.
- **Why Captain needs it:** Augments local LLM knowledge with live internet facts and external references.
- **Current status:** `IMPLEMENTED`
- **Current implementation:** `src/agents/search_agent.py` supporting Tavily, SerpAPI, and DuckDuckGo fallbacks.
- **Target implementation:** Maintain current robust fallback architecture.
- **Dependencies:** `duckduckgo-search`, `requests`, `httpx`
- **Input:** Search query string.
- **Output:** Ranked list of search results: `[{title, snippet, url}]`.
- **Security level:** `LOW`
- **User interaction:** Results synthesized into answer.
- **Related phase:** Phase 1
- **Tests:** `tests/unit/test_providers.py::test_search_manager_*`
- **Known limitations:** Rate limits on free providers (DuckDuckGo).

---

### 4.2. Document RAG (Retrieval-Augmented Generation)
- **Capability:** Local Document Ingestion & Semantic Retrieval
- **Purpose:** Parse PDFs and DOCX files, index into vector database, and provide citation-grounded retrieval.
- **Why Captain needs it:** Allows user to ask questions about local technical documentation and manuals.
- **Current status:** `IMPLEMENTED`
- **Current implementation:** `tools/rag_tools.py` using `pypdf`, `docx2txt`, `langchain-community`, and ChromaDB.
- **Target implementation:** Preserve current pipeline under `RagAgent` with distance thresholding.
- **Dependencies:** `chromadb`, `pypdf`, `docx2txt`, `langchain`
- **Input:** File path to ingest or semantic search query.
- **Output:** Ingest status or grounded context snippets with source citations.
- **Security level:** `LOW`
- **User interaction:** CLI `ingest` command or natural query to RagAgent.
- **Related phase:** Phase 1
- **Tests:** `tests/unit/test_runtime_architecture_fix.py::test_rag_relevance_filtering`
- **Known limitations:** Very large PDFs can take several seconds to chunk and embed.

---

### 4.3. Coding & Syntax Repair
- **Capability:** Polyglot Code Analysis & Synthesis
- **Purpose:** Analyze code syntax, detect bugs, generate unified diffs, and verify code correctness.
- **Why Captain needs it:** Drives software development, debugging, and project repair tasks.
- **Current status:** `IMPLEMENTED`
- **Current implementation:** `src/agents/coding_agent.py` configured with `CODER_MODEL` (`qwen2.5-coder:7b`).
- **Target implementation:** Integrated with terminal test execution in the autonomous loop.
- **Dependencies:** `langchain-ollama`, Ollama / cloud LLMs.
- **Input:** Code snippet, error message, or feature request.
- **Output:** Synthesized code, explanations, and patch diffs.
- **Security level:** `MEDIUM`
- **User interaction:** Code rendered in formatted markdown blocks.
- **Related phase:** Phase 1 / Phase 6
- **Tests:** `tests/unit/test_graph.py::test_conditional_routing_coder_query`
- **Known limitations:** Local 7B models require clear prompts to avoid verbose explanations.

---

## 5. UI, Companion & Runtime Capabilities

### 5.1. 3D EMO Desktop Companion
- **Capability:** Persistent Native Desktop Companion
- **Purpose:** Present an always-available, frameless 3D avatar on the Windows desktop that visually reflects Captain's operational state.
- **Why Captain needs it:** Gives physical, ambient presence to the AI without consuming screen space with heavy window frames.
- **Current status:** `IMPLEMENTED`
- **Current implementation:** PySide6 frameless overlay (`ui/desktop/pet_window.py`) hosting WebGL EMO avatar (`pet.html`) with Qt signal bridge.
- **Target implementation:** Connect audio amplitude output directly to avatar mouth mesh; add mouse gaze tracking.
- **Dependencies:** `PySide6`, `QtWebEngineWidgets`, WebGL/Three.js
- **Input:** `AppState` enum updates, audio amplitude floats.
- **Output:** Animated 3D robot face and body reactions.
- **Security level:** `LOW`
- **User interaction:** Draggable, right-click tray menu, visual feedback.
- **Related phase:** Phase 2
- **Tests:** `tests/unit/test_phase2_desktop_pet.py` (8 automated tests).
- **Known limitations:** Requires GPU WebGL acceleration on host system.

---

### 5.2. Web Workspace Dashboard
- **Capability:** Detailed Analytical Web Workspace
- **Purpose:** Deep cockpit for conversational history, system telemetry, agent activity streams, settings, and memory browsing.
- **Why Captain needs it:** Secondary interface for complex interactions requiring wide visual layouts.
- **Current status:** `IMPLEMENTED`
- **Current implementation:** Glassmorphic client (`ui/web/`) connected to FastAPI backend.
- **Target implementation:** Continuous synchronization with desktop runtime via shared `EventBus`.
- **Dependencies:** `fastapi`, `uvicorn`, HTML5/CSS3/Vanilla JS.
- **Input:** HTTP/WebSocket requests.
- **Output:** Glassmorphic HTML pages and JSON streams.
- **Security level:** `MEDIUM` (Bound to localhost).
- **User interaction:** Browser interaction at `http://127.0.0.1:8000/ui`.
- **Related phase:** Phase 1
- **Tests:** `tests/unit/test_frontend_volume*.py`
- **Known limitations:** Localhost binding only; no remote multi-user authentication.

---

### 5.3. State Machine Engine
- **Capability:** Strict Finite State Machine
- **Purpose:** Enforce deterministic, validated state transitions across the entire system.
- **Why Captain needs it:** Prevents invalid operational conditions (e.g. speaking while listening, executing tools while in standby).
- **Current status:** `IMPLEMENTED`
- **Current implementation:** `app/state.py` defines `AppState` (8 states) with transition validation and asynchronous listeners.
- **Target implementation:** Preserved as single source of state truth.
- **Dependencies:** Standard Python `enum`, `asyncio`.
- **Input:** Transition requests: `transition_to(target_state)`.
- **Output:** State change events broadcast to listeners.
- **Security level:** `LOW`
- **User interaction:** Reflected in EMO eyes and Web status badge.
- **Related phase:** Phase 1
- **Tests:** `tests/unit/test_phase1_foundation.py`
- **Known limitations:** None.
