# Captain AI OS Engineering Bible

## Volume 2 – Complete System Architecture
### Part 2E – Event Bus & Signal Architecture

* **Version:** 1.0.0
* **Status:** APPROVED SPECIFICATION

---

### Purpose
Part 2E defines the asynchronous message broker and signal distribution engine for Captain AI OS. The Event Bus acts as the central nerve system of the operating system, facilitating decoupled, thread-safe, and asynchronous communication across agents, tool supervisors, memory subsystems, and presentation interfaces without direct component coupling.

---

### Objectives
1. Establish a standardized, asynchronous pub/sub messaging backbone across all 6 architectural layers.
2. Eliminate direct inter-component dependencies by enforcing event-driven state propagation.
3. Guarantee event delivery order, event schema validation, and complete audit logging for every system transition.
4. Support prioritized system signals (e.g. user interrupts, emergency halts, state synchronization).

---

### Core Responsibilities
* **Message Brokerage:** Ingest, route, and broadcast typed system events to registered subscriber channels.
* **Topic Taxonomy Management:** Maintain hierarchical, structured topic names (e.g. `system.lifecycle.*`, `agent.execution.*`, `tool.invocation.*`).
* **Schema Validation:** Enforce strict Pydantic/JSON payload schema validation prior to event dispatch.
* **Prioritization:** Maintain priority queues allowing emergency signals (e.g., interrupt requests) to bypass normal task message queues.
* **Audit & Tracing:** Attach trace IDs to all events to enable end-to-end observability across multi-agent workflows.

---

### High-Level Architecture (ASCII Diagram)

```
+-----------------------------------------------------------------------------------+
|                                PRESENTATION LAYER                                 |
|                      (Desktop UI / WebSockets / Terminal)                         |
+----------------------------------------+------------------------------------------+
                                         | (Publish / Subscribe)
                                         v
+-----------------------------------------------------------------------------------+
|                                    EVENT BUS                                      |
|                                                                                   |
|  +---------------------+   +---------------------+   +-------------------------+  |
|  |   Ingestion Engine  |-->|  Schema Validator   |-->| Priority Queue Dispatch |  |
|  +---------------------+   +---------------------+   +-------------------------+  |
|                                                                 |                 |
|                                                                 v                 |
|                            +-----------------------------------------+            |
|                            |         Topic Router & Middleware       |            |
|                            +-----------------------------------------+            |
|                                       /               \                           |
+--------------------------------------/-----------------\--------------------------+
                                      /                   \
                                     v                     v
+---------------------------------------+   +---------------------------------------+
|            APPLICATION LAYER          |   |              AGENT LAYER              |
| (Captain Supervisor / Agent Router)   |   |    (Specialized Multi-Agent Nodes)    |
+---------------------------------------+   +---------------------------------------+
```

---

### Processing / Execution Pipeline

```
[Event Source]
      |
      v
1. Event Emission (Typed Payload + Event Metadata)
      |
      v
2. Schema Validation (Pydantic Contract Check)
      |
      v
3. Queue Injection (High-Priority / Standard Queue)
      |
      v
4. Topic Routing (Wildcard & Exact Match Dispatch)
      |
      v
5. Asynchronous Subscriber Notification (Non-blocking Handlers)
      |
      v
6. Audit Logging & State Synchronization
```

---

### Components

1. **Event Broker Core:**
   * Central coordinator managing active topics, subscriber registrations, and thread-safe dispatch loops.
2. **Topic Registry:**
   * Catalog of all valid system topic patterns, ensuring type safety and preventing unregistered event emission.
3. **Queue Manager:**
   * Dual-queue dispatcher separating real-time control signals (interrupts, user pause) from background data signals (logs, metrics).
4. **Subscription Manager:**
   * Tracks active listener callbacks, handling subscriber lifetime, dynamic registration, and clean unsubscription.
5. **Event Middleware Stack:**
   * Extensible interceptor pipeline for tracing, logging, metrics collection, and security auditing.

---

### Metadata Structures

```json
{
  "event_id": "uuid-v4-string",
  "topic": "agent.execution.started",
  "timestamp": "ISO-8601-UTC-Timestamp",
  "source_component": "CaptainSupervisor",
  "trace_id": "correlation-uuid",
  "priority": "HIGH | NORMAL | LOW",
  "payload": {
    "agent_id": "rag_agent_01",
    "task_id": "task_9921",
    "parameters": {}
  }
}
```

---

### State Management
* The Event Bus itself is strictly **stateless** regarding domain data, storing only transient, unacknowledged queue messages in memory.
* Subscriber registration states are maintained in a thread-safe registry with read-write locks (`RWLock`).
* Dead-letter queues (DLQ) temporarily hold failed event deliveries for inspection and retry attempts.

---

### Lifecycle
1. **Initialization:** Instantiated during application boot lifecycle; registers system-level middleware and core topic trees.
2. **Operational Phase:** Accepts registrations, ingests emitted events, routes messages to handlers concurrently.
3. **Graceful Shutdown:** Flushes pending queue items, notifies subscribers of `system.lifecycle.shutdown`, and cancels active handler tasks within a 5-second timeout window.

---

### Security Rules
* **Payload Sanitation:** Sensitive data (credentials, API keys) must be scrubbed before event creation.
* **Subscriber Isolation:** Handlers execute in isolated async tasks to prevent a single failing subscriber from blocking the dispatch loop.
* **Permission Validation:** High-privilege control topics (e.g. `system.shutdown`, `tool.execute_root`) require explicit caller identity validation.

---

### Failure Recovery
* **Handler Exception Isolation:** Unhandled exceptions inside subscriber callbacks are caught, logged via Loguru, and isolated without crashing the broker loop.
* **Retry Policy:** Transient handler errors undergo exponential backoff retries up to 3 attempts.
* **Dead-Letter Queue (DLQ):** Messages exceeding max retry limits are routed to DLQ for diagnostic inspection.

---

### Engineering Rules
1. Never perform blocking sync IO inside event handler callbacks; all handlers must be native `async` routines.
2. Every event payload must derive from the base `SystemEvent` Pydantic model.
3. Direct component-to-component invocation for notification purposes is strictly prohibited; emit an event instead.

---

### Completion Checklist
- [x] Purpose, Objectives, and Core Responsibilities defined
- [x] High-Level ASCII Architecture Diagram included
- [x] End-to-end Processing Pipeline documented
- [x] Metadata structures and Event schema specified
- [x] State, Lifecycle, Security, and Failure Recovery established
- [x] Clean Architecture and Engineering Rules enforced

---

### End of Part 2E
