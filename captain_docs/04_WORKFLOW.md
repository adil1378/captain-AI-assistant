# 🔄 Captain AI OS 2.0 — Execution & Operational Workflows

> **Document:** `04_WORKFLOW.md`  
> **Status:** Authoritative Workflow Specifications  
> **Target Audience:** Multi-Agent Engineers & Core System Developers

---

## 1. Primary Voice Workflow (Ambient Desktop Interaction)

Voice is the primary human interface. The voice pipeline operates from physical acoustic trigger through neural transcription to speech feedback.

```mermaid
flowchart TD
    STANDBY[State: STANDBY] -->|Clap Detected| CLAP[Transient Audio Trigger]
    CLAP --> ACTIVE[State: ACTIVE]
    ACTIVE --> VAD[Silero VAD Monitors Audio Buffer]
    VAD -->|Speech Start| LISTEN[State: LISTENING]
    LISTEN --> RECORD[Capture Spoken Utterance]
    RECORD -->|Silence Threshold| STT[Faster-Whisper Local STT]
    STT --> THINK[State: THINKING]
    THINK --> BRAIN[LangGraph Multi-Agent Core]
    BRAIN --> EXEC[State: EXECUTING\nAuthorized Tool Ingestion]
    EXEC --> SPEAK[State: SPEAKING\nNeural TTS Synthesis]
    SPEAK --> EMO_ACT[EMO Speaks & Animates Waveform]
    EMO_ACT --> WAIT_CLAP{Second Clap or Timeout?}
    WAIT_CLAP -- "Second Clap 👏" --> STANDBY
    WAIT_CLAP -- "Follow-up Speech" --> LISTEN
    WAIT_CLAP -- "Inactivity Timeout" --> STANDBY
```

### Steps:
1. **Physical Clap Ingestion:** The background microphone stream detects an acoustic transient matching a handclap profile.
2. **State Transition:** State machine transitions from `STANDBY` to `ACTIVE`. EMO awakens and glows.
3. **VAD Windowing:** Real-time Voice Activity Detection opens an audio buffer on speech onset.
4. **Local Transcription:** Audio segment is transcribed locally via Faster-Whisper.
5. **Reasoning & Planning:** The user query is classified and routed across the multi-agent graph.
6. **Execution:** Required tools execute under zero-trust boundaries.
7. **Spoken Response:** Response text is synthesized into local neural audio stream.
8. **Avatar Sync:** Audio amplitude drives mouth movement in the 3D EMO avatar.
9. **Return to Standby:** A second clap or an inactivity timeout returns Captain to `STANDBY`.

---

## 2. Keyboard & Text Fallback Workflow

Text input is available at all times through the Web Interface or Terminal CLI.

```mermaid
flowchart TD
    USER_TXT[User enters text in CLI or Web UI] --> INGEST[Capture UTF-8 text string]
    INGEST --> RUNTIME[AppRuntime validates State]
    RUNTIME --> SET_THINK[State set to THINKING]
    SET_THINK --> ROUTER[Hybrid Intent Classifier]
    ROUTER --> AGENTS[LangGraph Processing Node]
    AGENTS --> GATEWAY[Tool Invocation Layer]
    GATEWAY --> FORMAT[Synthesize Markdown / JSON Response]
    FORMAT --> RENDER[Render to Terminal Card or Web Workspace]
    RENDER --> STATE_IDLE[State reset to ACTIVE / STANDBY]
```

---

## 3. Autonomous Computer-Use Workflow (Phase 6)

The core autonomous loop allows Captain to observe the desktop, reason about application state, perform actions, and verify the outcome.

```mermaid
flowchart TD
    GOAL[User Task: 'Open VS Code and fix the test failure'] --> UNDERSTAND[Decompose Goal into Task Plan]
    UNDERSTAND --> OBS_PRE[Observe Desktop: Capture Screenshot & Window Tree]
    OBS_PRE --> REASON[Analyze UI Coordinates, Error Text & IDE State]
    REASON --> PLAN_ACT[Select Next Action: Launch App / Click / Edit File]
    PLAN_ACT --> SEC_CHECK{Risk Tier?}
    SEC_CHECK -- "High / Critical" --> CONFIRM[Show Native Confirmation Dialog]
    CONFIRM -- "Rejected" --> ABORT[Abort with User Notification]
    CONFIRM -- "Approved" --> DO_ACT[Execute Action via Tool Gateway]
    SEC_CHECK -- "Low / Medium" --> DO_ACT
    DO_ACT --> OBS_POST[Observe Again: Inspect Screen / Output / Exit Code]
    OBS_POST --> VERIFY{Did Action Achieve Step Goal?}
    VERIFY -- "No (Fix / Retry)" --> REASON
    VERIFY -- "Yes (Steps Remaining)" --> REASON
    VERIFY -- "Yes (Task Finished)" --> COMPLETE[Synthesize Final Report & Speak Result]
```

---

## 4. Software Development & Debugging Workflow

A practical demonstration of the computer-use workflow for developer tasks:

```
Step 1: User Command
        "Captain, my API server tests are failing in this project. Find out why and fix it."

Step 2: Observation & Localization
        • Captain inspects current working directory files.
        • Captures terminal output or runs 'pytest tests/' via SystemAgent.
        • Extracts stack trace and error message (e.g., ImportError: cannot import 'Settings').

Step 3: Root Cause Reasoning
        • CodingAgent inspects imported modules and symbol references.
        • Identifies conflicting package names or missing attributes in config.

Step 4: Tool Confirmation & Remediation
        • CodingAgent generates precise minimal unified diff.
        • Security dialog prompts user: "Allow modification to config.py?"
        • Upon approval, writes fix to disk via file_tools.

Step 5: Verification Phase
        • Re-executes 'pytest tests/' to inspect test suite outcome.
        • Verifies exit code == 0 and 0 failures reported.

Step 6: Completion Report
        • EMO avatar speaks: "Fixed the configuration import error. All tests are now passing."
        • Full diff and execution logs rendered in Web Dashboard.
```

---

## 5. External Communication Workflow (Zero-Trust Dispatch)

Sending external messages or emails has irreversible real-world effects and requires mandatory confirmation.

```mermaid
flowchart LR
    REQ[Agent requests Send Email / Telegram / WhatsApp] --> TIL[Tool Invocation Layer]
    TIL --> PARSE[Validate Payload: Recipient, Subject, Body]
    PARSE --> POPUP[Native PySide6 Security Dialog]
    POPUP -->|User Clicks Cancel| DENY[Return AuthorizationDenied Error to Agent]
    POPUP -->|User Clicks Approve| DISPATCH[Execute Provider Dispatch API]
    DISPATCH --> AUDIT[Write Tamper-Evident Record to AuditComplianceManager]
    AUDIT --> NOTIFY[Notify User of Successful Dispatch]
```
