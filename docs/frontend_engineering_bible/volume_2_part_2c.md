# Captain AI OS — Frontend Engineering Bible
## Frontend Volume 2 — Part 2C
### Captain Core State Machine

* **Version:** 1.0.0
* **Status:** APPROVED SPECIFICATION

---

### Objective
Define the operational state model of the Captain Core. This specification establishes how Captain behaves conceptually during different phases of interaction. It defines what state Captain is in, not how that state is visually rendered.

This document defines behavioral architecture only.

---

### Design Philosophy
Captain should always appear alive. A living intelligence is never completely inactive. Even when waiting, Captain maintains a subtle sense of presence. The user should always understand Captain's current condition without needing explicit status messages.

---

### Primary Operational States (The 10 Operational States)

1. **State 1 — Idle (`IDLE`):** Captain is available and awaiting interaction (default state; calm awareness).
2. **State 2 — Attention (`ATTENTION`):** Detected user presence or interaction focus before command processing.
3. **State 3 — Listening (`LISTENING`):** Actively receiving user input via voice, text, or gestures.
4. **State 4 — Understanding (`UNDERSTANDING`):** Interpreting and parsing the received input.
5. **State 5 — Thinking (`THINKING`):** Reasoning, planning, or deliberating a response strategy.
6. **State 6 — Executing (`EXECUTING`):** Actively performing tools, workflows, or system automation tasks.
7. **State 7 — Responding (`RESPONDING`):** Communicating results back to user (speaking, streaming response).
8. **State 8 — Waiting (`WAITING`):** Completed interaction; awaiting follow-up instructions before returning to Idle.
9. **State 9 — Notification (`NOTIFICATION`):** Brief communication of important system events or alerts.
10. **State 10 — Recovery (`RECOVERY`):** Gracefully handling interruptions, temporary resource failure, or retry recovery.

---

### State Transition & Priority Rules
* **Transition Principles:** Logical, smooth transitions preserving user understanding; no unpredictable jumps.
* **State Priority:** Highest-priority active task determines primary visual presentation.
* **State Persistence:** States remain consistent until triggering activities complete; unnecessary rapid switching is prohibited.
* **Extensibility:** Simple, predictable, human-readable, independent of rendering framework or animation engines.

---

### Scope
This specification defines operational state philosophy, 10 state definitions, transition principles, state priority, persistence rules, and expansion strategy. It does not define visual animations, audio behavior, lighting, or rendering logic.

---

### Deliverable
After approval, every interaction involving the Captain Core must map to one of these 10 operational states.

---

### End of Frontend Volume 2 – Part 2C
