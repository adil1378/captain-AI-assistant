# Captain AI OS — Frontend Engineering Bible
## Frontend Volume 3 — Part 3F
### Sidebar & Dock Architecture

* **Version:** 1.0.0
* **Status:** APPROVED SPECIFICATION

---

### Objective
Define the architecture of the Sidebar and Dock systems within Captain AI OS. These interface elements provide persistent access to user information, tools, and system functions while preserving Captain as the primary focal point.

This specification defines architectural principles only.

---

### Design Philosophy & Information Hierarchy
The Sidebar and Dock are support systems that never compete visually with Captain Core.

**Visual Information Hierarchy:**
1. **Captain Core** (Central Focus)
2. **Active Workspace** (Primary Task Surface)
3. **Sidebar Information** (Persistent Organizational Resources)
4. **Dock Actions** (Quick-Action Launcher)

---

### System Architecture
* **Sidebar System (Persistent Organizational Space):** Structured access to long-lived resources including Conversations, Projects, RAG Memories, Knowledge Spaces, Files, Agents, Workflows, and Favorites.
* **Dock System (Quick-Action Launcher):** Immediate one-click access to high-frequency actions including Voice Interaction, Chat Stream, Search Palette, Terminal, Browser, File Explorer, Settings, and Extensions.
* **Adaptive Visibility & State Persistence:** Supports `VISIBLE`, `COLLAPSED`, `EXPANDED`, and `AUTO_HIDE` modes with layout state saved across user sessions.
* **Accessibility:** Full mouse, keyboard, touch, and voice control for all sidebar sections and dock launchers.

---

### Scope
This specification defines sidebar philosophy, dock philosophy, sidebar/dock architecture, adaptive behavior, visibility, persistence, relationship with Captain, information hierarchy, scalability, and accessibility. It does not define specific CSS animations or icon SVGs.

---

### Deliverable
After approval, every Sidebar and Dock feature within Captain AI OS must follow this architecture.

---

### End of Frontend Volume 3 – Part 3F
### Frontend Volume 3 Complete
