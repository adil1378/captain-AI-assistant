# Captain AI OS Engineering Bible
## Volume 2 – Complete System Architecture (Part 2B)

### Component Architecture

#### Objective
Define all major components and their exact responsibilities.

#### Core System Components & Responsibilities

1. **Desktop UI:**
   * **Responsibility:** Presentation frontend providing user interaction (chat interface, voice control, system dashboard, tool outputs).
   * **Interfaces:** Communicates with backend exclusively via API Gateway (REST HTTP and WebSockets).

2. **API Gateway:**
   * **Responsibility:** Expose, secure, and route external client requests to core services.
   * **Interfaces:** FastAPI endpoints, WebSocket endpoints, middleware (CORS, auth, rate limiting).

3. **Captain Supervisor:**
   * **Responsibility:** Central agent orchestration graph controller. Manages execution graph state, routes queries to appropriate agents, and enforces task completion.

4. **Planner:**
   * **Responsibility:** Decompose complex user goals into executable multi-step plans and tool invocation sequences.

5. **Agent Registry:**
   * **Responsibility:** Register, discover, instantiate, and manage the lifecycle of all specialized agents in the system.

6. **Agent Router:**
   * **Responsibility:** Intelligently evaluate input intent and route requests to optimal specialized agents based on capability descriptors.

7. **Model Manager:**
   * **Responsibility:** Unified LLM provider abstraction layer. Handles model selection, fallback strategies, prompt formatting, and token management across Ollama local models and Cloud APIs.

8. **Event Bus:**
   * **Responsibility:** Asynchronous publish/subscribe message broker enabling decoupled communication across agents, backend, and UI.

9. **Tool Manager:**
   * **Responsibility:** Tool registration, validation, security/permission checks, and safe execution sandbox.

10. **Memory Manager:**
    * **Responsibility:** Coordinate short-term working context, long-term episodic memory, and semantic RAG retrieval.

11. **Storage:**
    * **Responsibility:** Abstract persistent relational database access (users, sessions, agent state) and vector embeddings storage.

12. **Observability:**
    * **Responsibility:** Centralized structured logging (Loguru), execution metrics, performance tracing, and error telemetry.

#### Architectural Dependency Rules
* Higher layers depend strictly on abstract interfaces, never on concrete lower-layer implementations.
* **Zero Direct Cross-Layer Coupling:** Components must not directly instantiate or bypass neighboring layer abstractions.
* **Zero Hidden Dependencies:** All component dependencies must be explicitly injected via constructors or factory methods.
* **Zero Duplicated Business Logic:** Single Responsibility Principle enforced across all 12 primary components.
