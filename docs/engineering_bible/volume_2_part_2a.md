# Captain AI OS Engineering Bible
## Volume 2 – Complete System Architecture (Part 2A)

### High-Level System Architecture

#### Objective
Define the top-level architecture that every future module must follow.

#### Core Architectural Layers
1. **Presentation Layer:** User Interfaces (Desktop UI, Terminal UI, Web UI).
2. **AI Orchestration Layer:** Captain Supervisor, Planner, Event Bus, Model Manager.
3. **Agent Layer:** Agent Registry, Specialized Agents (Conversation, RAG, Search, Coding, System, Comms, etc.).
4. **Tool Layer:** Tool Manager, Tool Registries, System Tools, External API Tools.
5. **Memory Layer:** Memory Manager, Short-term Context, Long-term Vector Memory, Conversation History.
6. **Data Layer:** Relational DB (PostgreSQL/SQLite), Vector DB (pgvector/Chroma), Document Storage.
7. **Infrastructure Layer:** Host OS interfaces, subprocess execution, hardware monitoring, security/permissions.

#### Architectural Design Rules
* Layers communicate strictly through defined, stable interfaces.
* Business logic remains completely independent from UI and infrastructure implementation details.
* Dependency flows unidirectionally from outer layers toward core abstractions.

#### Primary System Components
* **Desktop UI:** Desktop presentation frontend.
* **API Gateway:** FastAPI gateway exposing endpoints & WebSocket communication.
* **Captain Supervisor:** Central agent graph coordinator & task dispatcher.
* **Agent Registry:** Dynamic registry for discovering, instantiating, and managing agent lifecycles.
* **Planner:** Multi-step reasoning and execution planning engine.
* **Model Manager:** Unified provider interface for local (Ollama) and cloud LLMs.
* **Event Bus:** Asynchronous pub/sub event broker for decoupled system signals.
* **Tool Manager:** Tool discovery, permission verification, and execution gateway.
* **Memory Manager:** Dual-memory subsystem managing working memory and semantic RAG storage.
* **Storage:** Persistent relational & vector store.

#### System Goals
* **Scalability**
* **Modularity**
* **Observability**
* **Security**
* **Maintainability**
* **Extensibility**

#### Implementation Policy
No module may bypass the approved architecture. New capabilities must integrate through existing interfaces unless the Engineering Bible is updated.
