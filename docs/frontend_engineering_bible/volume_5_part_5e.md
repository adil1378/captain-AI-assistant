# Captain AI OS — Frontend Engineering Bible
## Frontend Volume 5 — Part 5E
### System Awareness Dashboard Architecture

* **Version:** 1.0.0
* **Status:** APPROVED SPECIFICATION

---

### Objective
Define the architecture of the System Awareness Dashboard. The System Awareness Dashboard provides Captain's operational awareness of the local device, connected services, and AI runtime. It is not intended to function as a developer monitoring console; its purpose is to give users meaningful awareness of Captain's environment.

This specification defines frontend architectural principles only.

---

### Design Philosophy
Awareness is useful. Users understand Captain's operating environment without being overwhelmed by technical metrics. The dashboard answers: "Is Captain healthy? Is everything working? Are required resources available?"

---

### 6 Operational Awareness Categories
1. **CAPTAIN_STATUS:** Operational readiness (`READY`, `BUSY`, `OFFLINE`, `RECOVERY`).
2. **AI_RUNTIME:** Active model selection, inference latency, and AI readiness.
3. **DEVICE_RESOURCES:** High-level health summaries for CPU, GPU, RAM, and Storage.
4. **CONNECTIVITY:** Status of Internet, local services, cloud services, and external APIs.
5. **SENSORS:** Readiness of microphone, audio output, camera, and input peripherals.
6. **BACKGROUND_SERVICES:** Status of Memory Center, search services, and automation engine.

---

### Actionable Health Communication & Progressive Detail
* **Actionable Recommendations:** Surfaces concise, plain-language recommendations when system conditions require attention (e.g. "Microphone permission required").
* **Progressive Detail:** Layered disclosure showing overall system health at a glance, expanding into specific category status upon request.
* **Context-Aware Presentation:** Filters displayed awareness indicators according to active Workspace Mode.
* **Non-Intrusive & Accessible:** Operates as a supporting panel; fully accessible via keyboard navigation and screen readers.

---

### Scope
This specification defines dashboard philosophy, 6 awareness categories, context-aware presentation, health communication, actionable recommendations, progressive detail, scalability, and accessibility. It does not define low-level OS telemetry or hardware driver APIs.

---

### Deliverable
After approval, every operational status interface within Captain AI OS must follow this System Awareness Dashboard Architecture.

---

### End of Frontend Volume 5 – Part 5E
