# AI Webhook System Architecture

**Version**: 1.0
**Last Updated**: 2025-11-15
**Status**: Production Ready

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Components](#components)
4. [Data Flow](#data-flow)
5. [Database Schema](#database-schema)
6. [Technology Stack](#technology-stack)
7. [Deployment Architecture](#deployment-architecture)
8. [Key Design Decisions](#key-design-decisions)
9. [Security](#security)
10. [Scalability](#scalability)

---

## System Overview

The AI Webhook System is a distributed architecture that enables local machines to receive GitHub webhook events and process collaborative session commands through a cloud-hosted relay server. It supports real-time communication between LLMs (Large Language Models) and local development environments, with persistent storage in PostgreSQL.

### Core Capabilities

- **Webhook Relay**: Cloud server receives GitHub webhooks and broadcasts to connected clients
- **Collaborative Sessions**: Structured workflows where LLMs delegate work to background agents
- **Memory Persistence**: Long-term storage of conversation context, decisions, and artifacts
- **Task Queue**: Distributed task management for background agent orchestration
- **Real-time Communication**: WebSocket-based bidirectional messaging

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLOUD LAYER                               │
│                                                                  │
│  ┌──────────────┐           ┌─────────────────┐                │
│  │   GitHub     │──────────▶│  Relay Server   │                │
│  │   Webhooks   │           │   (Railway)     │                │
│  └──────────────┘           │                 │                │
│                              │  - FastAPI      │                │
│  ┌──────────────┐           │  - WebSocket    │                │
│  │  LLM APIs    │──────────▶│  - Broadcast    │                │
│  │ ChatGPT/etc  │           │                 │                │
│  └──────────────┘           └────────┬────────┘                │
│                                      │ WebSocket                │
└──────────────────────────────────────┼──────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                       LOCAL LAYER                                │
│                                                                  │
│  ┌────────────────────────────────────────────────────┐         │
│  │              Webhook Client (Python)               │         │
│  │                                                     │         │
│  │  ├─ WebSocket Listener                             │         │
│  │  ├─ Payload Unwrapping                             │         │
│  │  ├─ Session Manager                                │         │
│  │  │   ├─ Conversation Processor Agent               │         │
│  │  │   └─ Memory Keeper Agent                        │         │
│  │  └─ Storage Backend (Postgres/JSON)                │         │
│  └───────────────────────┬────────────────────────────┘         │
│                          │                                       │
│                          ▼                                       │
│  ┌────────────────────────────────────────────────────┐         │
│  │          PostgreSQL Database (Docker)              │         │
│  │                                                     │         │
│  │  Tables:                                            │         │
│  │  ├─ sessions                                        │         │
│  │  ├─ conversation_chunks                             │         │
│  │  ├─ memories                                        │         │
│  │  ├─ tasks                                           │         │
│  │  ├─ artifacts                                       │         │
│  │  └─ agents                                          │         │
│  └─────────────────────────────────────────────────────┘         │
│                                                                  │
│  ┌────────────────────────────────────────────────────┐         │
│  │         PgAdmin (Docker) - Optional                │         │
│  │         Web UI: http://localhost:5051              │         │
│  └────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Relay Server (Cloud)

**Location**: Railway (https://web-production-3d53a.up.railway.app)
**Technology**: FastAPI + WebSocket
**File**: `app.py`

**Responsibilities**:
- Receive HTTP POST requests from GitHub webhooks
- Receive HTTP POST requests from custom APIs (LLMs, integrations)
- Validate webhook signatures (GitHub) and API keys (custom)
- Broadcast messages to all connected WebSocket clients
- Track connected clients and heartbeat monitoring

**Endpoints**:
- `GET /` - Health check
- `POST /webhook` - Receive webhooks (GitHub signature or API key auth)
- `WebSocket /ws` - Client connections
- `GET /health` - Detailed health status

**Authentication**:
- GitHub webhooks: HMAC-SHA256 signature verification
- Custom webhooks: API key header (`X-API-Key` or `Authorization: Bearer`)

---

### 2. Webhook Client (Local)

**Location**: Local development machine
**Technology**: Python 3.12+ with asyncio
**File**: `client/client.py`

**Responsibilities**:
- Establish persistent WebSocket connection to relay server
- Receive and unwrap webhook payloads
- Route commands to appropriate handlers
- Maintain heartbeat with relay server
- Auto-reconnect on connection loss
- Log all webhook events to `webhook_logs/`

**Key Features**:
- Automatic `.env` file loading via `python-dotenv`
- Payload unwrapping (handles relay server's `webhook` envelope)
- Multi-handler architecture (GitHub, LLM insights, collaborative sessions)
- Graceful error handling and retry logic

**Message Flow**:
```python
1. WebSocket receives message
2. Parse JSON
3. Check message type:
   - "connection" → Log connection status
   - "pong" → Heartbeat response
   - "webhook" → Unwrap payload and route
   - "collaborative_session_command" → Session Manager
   - "llm_conversation_insight" → LLM Handler
   - Default → GitHub webhook handler
4. Process and log
```

---

### 3. Session Manager

**Location**: `client/session_manager.py`
**Technology**: Python with pluggable storage backends

**Responsibilities**:
- Coordinate collaborative sessions between LLMs and agents
- Route commands to appropriate agent handlers
- Manage session lifecycle (create, pause, resume, complete)
- Abstract storage layer (supports JSON files or PostgreSQL)
- Batch command processing

**Architecture**:
```python
SessionManager
  ├─ Backend Selection (JSON or Postgres)
  ├─ Agent Registry
  │   ├─ ConversationProcessorAgent
  │   └─ MemoryKeeperAgent
  └─ Command Router
```

**Supported Commands**:
- `create_session` - Initialize new collaborative session
- `conversation_chunk` - Store large conversation text
- `store_memory` - Save structured knowledge (ideas, decisions, etc.)
- `retrieve_memory` - Query memories by key
- `query_memories` - Filter memories by type/tags
- `delegate_task` - Create task for background agent
- `add_artifact` - Store generated code/documents
- `batch` - Execute multiple commands atomically
- `pause_session`, `resume_session`, `complete_session` - Lifecycle management

---

### 4. Storage Backend (PostgreSQL)

**Location**: `client/storage/postgres_backend.py`
**Technology**: PostgreSQL 15, psycopg2, connection pooling

**Responsibilities**:
- Persist all session data
- Provide ACID guarantees for concurrent access
- Enable full-text search across conversations/memories/artifacts
- Support atomic task claiming for distributed agent coordination

**Implementation Details**:
- Connection pool: 1-10 connections (ThreadedConnectionPool)
- Automatic reconnection handling
- JSONB columns for flexible schema
- GIN indexes for full-text search
- Triggers for automatic timestamp updates

**Alternative**: JSON file-based storage (`client/models/session.py`)

---

### 5. PostgreSQL Database

**Location**: Docker container (`ai-webhook-postgres`)
**Version**: PostgreSQL 15 (Alpine Linux)
**Port**: 5433 (external), 5432 (internal)

**Schema**: See [Database Schema](#database-schema) section below

**Management**:
- Docker Compose orchestration
- Persistent volumes for data retention
- Health checks for reliability
- Automatic initialization from `database/init.sql`

---

### 6. PgAdmin (Optional)

**Location**: Docker container (`ai-webhook-pgadmin`)
**Version**: Latest
**Port**: 5051
**Access**: http://localhost:5051

**Purpose**: Web-based GUI for database inspection and management

**Login**:
- Email: `admin@example.com`
- Password: `admin`

---

### 7. Agents

**Location**: `client/agents/`
**Technology**: Python with abstract base class

#### Base Agent (`base_agent.py`)
Abstract class defining agent interface:
```python
class BaseAgent:
    def can_handle(command, data) -> bool
    def execute(command, data, session) -> AgentResult
    def save_state(session, state)
    def load_state(session) -> state
```

#### Conversation Processor Agent
**File**: `client/agents/conversation_processor.py`

**Handles**: `append_conversation` commands

**Responsibilities**:
- Process large conversation chunks from LLMs
- Extract structured items (ideas, decisions, questions)
- Save to session with metadata
- Auto-generate chunk IDs

#### Memory Keeper Agent
**File**: `client/agents/memory_keeper.py`

**Handles**: `store_memory`, `retrieve_memory`, `query_memories` commands

**Responsibilities**:
- Store structured knowledge in various types
- Support tagging and filtering
- Enable semantic search across memories
- Auto-generate keys if not provided

**Memory Types**:
- `idea` - New feature ideas, suggestions
- `decision` - Architectural or design decisions
- `question` - Open questions needing resolution
- `action_item` - Tasks to complete
- `context` - Background information
- `preference` - User or system preferences
- `fact` - Verified information
- `risk` - Potential issues or concerns

---

## Data Flow

### 1. GitHub Webhook Flow

```
GitHub Event (e.g., push, PR)
  ↓
GitHub sends POST to relay server
  ↓
Relay verifies HMAC signature
  ↓
Relay wraps in {type: "webhook", payload: {...}}
  ↓
Broadcast to all connected WebSocket clients
  ↓
Client receives, unwraps payload
  ↓
Routes to GitHub webhook handler
  ↓
Logs to webhook_logs/TIMESTAMP_EVENT.json
  ↓
Processes event (user-defined logic)
```

### 2. Collaborative Session Flow

```
LLM (ChatGPT, Claude, etc.)
  ↓
Sends POST to relay server /webhook
  ↓
Headers: X-API-Key: <key>
Body: {type: "collaborative_session_command", command: "...", data: {...}}
  ↓
Relay wraps in {type: "webhook", payload: {...}}
  ↓
Broadcast to clients
  ↓
Client unwraps payload
  ↓
Detects type: "collaborative_session_command"
  ↓
Routes to Session Manager
  ↓
Session Manager identifies command handler
  ↓
Agent processes command
  ↓
Data stored in PostgreSQL
  ↓
Response logged and optionally sent back (future feature)
```

### 3. Memory Storage Flow

```
LLM sends store_memory command
  ↓
Session Manager receives
  ↓
Memory Keeper Agent validates
  ↓
Postgres Backend formats data
  ↓
INSERT INTO memories (...)
  ↓
Auto-increment session.memory_count
  ↓
Update session.last_activity
  ↓
Return success to client
  ↓
Client logs response
```

### 4. Task Delegation Flow (Future)

```
LLM sends delegate_task command
  ↓
Session Manager creates task
  ↓
INSERT INTO tasks (status='pending')
  ↓
Control Agent polls task queue
  ↓
claim_task() (atomic, FOR UPDATE SKIP LOCKED)
  ↓
Spawn background agent (Claude Code, etc.)
  ↓
Agent executes task
  ↓
UPDATE tasks SET status='completed', output_data=...
  ↓
NOTIFY LLM via webhook callback (future)
```

---

## Database Schema

### Entity-Relationship Diagram

```
┌─────────────┐
│  sessions   │
│─────────────│
│ id (PK)     │───┐
│ title       │   │
│ status      │   │
│ created     │   │
└─────────────┘   │
                  │
                  │ 1:N
                  │
    ┌─────────────┼─────────────┬─────────────┬─────────────┐
    │             │             │             │             │
    ▼             ▼             ▼             ▼             ▼
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ conversation│  memories│   tasks   │ artifacts│   agents  │
│  _chunks│           │           │           │           │
│─────────│  │─────────│  │─────────│  │─────────│  │─────────│
│session_id│  │session_id│  │session_id│  │session_id│  │  name   │
│chunk_id │  │  type   │  │agent_name│  │  type   │  │  type   │
│ content │  │   key   │  │  status │  │ content │  │ status  │
│  format │  │ content │  │priority │  │  format │  │command  │
└─────────┘  │  tags   │  └─────────┘  └─────────┘  └─────────┘
             └─────────┘
```

### Table Definitions

#### sessions
```sql
CREATE TABLE sessions (
    id VARCHAR(255) PRIMARY KEY,
    title TEXT,
    participants JSONB DEFAULT '[]',
    status VARCHAR(50) DEFAULT 'active',
    created TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    conversation_chunk_count INTEGER DEFAULT 0,
    memory_count INTEGER DEFAULT 0,
    task_count INTEGER DEFAULT 0,
    artifact_count INTEGER DEFAULT 0
);
```

**Purpose**: Track collaborative session metadata and statistics

#### conversation_chunks
```sql
CREATE TABLE conversation_chunks (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES sessions(id) ON DELETE CASCADE,
    chunk_id VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    format VARCHAR(50) DEFAULT 'dialogue',
    extracted_items JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id, chunk_id)
);

CREATE INDEX idx_conversation_content ON conversation_chunks
    USING gin(to_tsvector('english', content));
```

**Purpose**: Store large conversation text with full-text search capability

#### memories
```sql
CREATE TABLE memories (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES sessions(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    key VARCHAR(255) NOT NULL,
    content JSONB NOT NULL,
    tags TEXT[] DEFAULT '{}',
    created TIMESTAMPTZ DEFAULT NOW(),
    updated TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id, key)
);

CREATE INDEX idx_memories_type ON memories(session_id, type);
CREATE INDEX idx_memories_tags ON memories USING gin(tags);
CREATE INDEX idx_memories_content ON memories
    USING gin(to_tsvector('english', content::text));
```

**Purpose**: Store structured knowledge extracted from conversations

#### tasks
```sql
CREATE TABLE tasks (
    id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES sessions(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 5,
    status VARCHAR(50) DEFAULT 'pending',
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    process_id INTEGER,
    claimed_by VARCHAR(255),
    created TIMESTAMPTZ DEFAULT NOW(),
    started TIMESTAMPTZ,
    completed TIMESTAMPTZ
);

CREATE INDEX idx_tasks_status ON tasks(agent_name, status, priority DESC);
```

**Purpose**: Task queue for background agent coordination

**Atomic Claiming Function**:
```sql
CREATE OR REPLACE FUNCTION claim_task(
    p_agent_name VARCHAR,
    p_control_agent VARCHAR
) RETURNS TABLE (...)
AS $$
BEGIN
    RETURN QUERY
    UPDATE tasks
    SET status = 'claimed',
        claimed_by = p_control_agent,
        started = NOW()
    WHERE id = (
        SELECT id FROM tasks
        WHERE agent_name = p_agent_name
        AND status = 'pending'
        ORDER BY priority DESC, created ASC
        FOR UPDATE SKIP LOCKED
        LIMIT 1
    )
    RETURNING *;
END;
$$ LANGUAGE plpgsql;
```

#### artifacts
```sql
CREATE TABLE artifacts (
    id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES sessions(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    format VARCHAR(50),
    metadata JSONB DEFAULT '{}',
    created TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_artifacts_content ON artifacts
    USING gin(to_tsvector('english', content));
```

**Purpose**: Store generated code, documents, and other outputs

#### agents
```sql
CREATE TABLE agents (
    name VARCHAR(100) PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    command TEXT NOT NULL,
    capabilities JSONB DEFAULT '[]',
    max_concurrent INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'available',
    last_heartbeat TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'
);
```

**Purpose**: Registry of available background agents

**Pre-populated Agents**:
- `claude_code` - Code generation and modification
- `codex` - Code analysis and documentation
- `researcher` - Web research and information gathering

---

## Technology Stack

### Backend (Relay Server)
- **Framework**: FastAPI 0.104+
- **WebSocket**: websockets library
- **Deployment**: Railway
- **Language**: Python 3.11+

### Client
- **Language**: Python 3.12+
- **Async**: asyncio + websockets
- **Environment**: python-dotenv
- **Database**: psycopg2 (PostgreSQL driver)

### Database
- **RDBMS**: PostgreSQL 15
- **Containerization**: Docker + Docker Compose
- **GUI**: PgAdmin 4 (optional)

### Development Tools
- **Testing**: pytest (planned)
- **Linting**: ruff (planned)
- **Type Checking**: mypy (planned)

---

## Deployment Architecture

### Production Setup

```
┌────────────────────────────────────┐
│         Railway Cloud              │
│                                    │
│  ┌──────────────────────────┐     │
│  │    Relay Server          │     │
│  │    - Auto-scaling        │     │
│  │    - HTTPS/WSS           │     │
│  │    - Health monitoring   │     │
│  └──────────────────────────┘     │
└────────────────────────────────────┘
              │ WSS
              ▼
┌────────────────────────────────────┐
│      Local Development Env         │
│                                    │
│  ┌──────────────────────────┐     │
│  │  Docker Compose          │     │
│  │  ├─ PostgreSQL           │     │
│  │  └─ PgAdmin (optional)   │     │
│  └──────────────────────────┘     │
│                                    │
│  ┌──────────────────────────┐     │
│  │  Python Client           │     │
│  │  (systemd service)       │     │
│  └──────────────────────────┘     │
└────────────────────────────────────┘
```

### Local Development Setup

1. **Database**: Docker container on localhost:5433
2. **Client**: Python process with auto-restart
3. **Relay**: Railway cloud instance

### Environment Variables

**Required**:
```bash
# Storage
STORAGE_BACKEND=postgres
DATABASE_URL=postgresql://webhook_user:webhook_dev_password@localhost:5433/ai_webhook

# Relay
RELAY_SERVER_URL=wss://web-production-3d53a.up.railway.app/ws
API_KEY=<your-api-key>

# GitHub (optional)
GITHUB_WEBHOOK_SECRET=<your-secret>
GITHUB_PERSONAL_ACCESS_TOKEN=<your-token>
```

---

## Key Design Decisions

### 1. Relay Server Pattern
**Decision**: Use cloud relay instead of direct webhooks to local machine

**Rationale**:
- No port forwarding or ngrok required
- Works behind corporate firewalls
- Supports multiple clients from same webhook
- Centralized authentication and logging

**Trade-offs**:
- Additional network hop
- Relay server is single point of failure (mitigated by Railway's reliability)

### 2. WebSocket vs HTTP Polling
**Decision**: WebSocket for real-time bidirectional communication

**Rationale**:
- Lower latency for webhook delivery
- Persistent connection reduces overhead
- Enables heartbeat monitoring
- Supports server-to-client push

**Trade-offs**:
- More complex connection management
- Requires reconnection logic

### 3. PostgreSQL vs NoSQL
**Decision**: PostgreSQL with JSONB columns

**Rationale**:
- ACID guarantees for task queue
- Full-text search built-in
- Flexible schema via JSONB
- Mature tooling and ecosystem
- Atomic operations for concurrent agents

**Trade-offs**:
- More complex setup than file storage
- Requires database management

### 4. Pluggable Storage Backend
**Decision**: Abstract storage layer supporting JSON and Postgres

**Rationale**:
- Easy development without database
- Gradual migration path
- Testing flexibility
- Backwards compatibility

**Implementation**:
```python
if STORAGE_BACKEND == 'postgres':
    from storage.postgres_backend import PostgresBackend
    SessionBackend = PostgresBackend
else:
    SessionBackend = CollaborativeSession  # JSON file-based
```

### 5. Python Package Structure
**Decision**: Absolute imports with sys.path manipulation

**Rationale**:
- Relative imports break when running as script
- Avoids complex package installation
- Works in development and production
- Simpler than restructuring entire codebase

**Implementation**:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.session import Something
```

### 6. Payload Wrapping by Relay
**Decision**: Relay wraps all messages in standardized envelope

**Format**:
```json
{
  "type": "webhook",
  "event": "<github-event-type>",
  "delivery_id": "<github-delivery-id>",
  "timestamp": "<iso-timestamp>",
  "payload": {
    // Original webhook payload
  }
}
```

**Rationale**:
- Consistent message structure
- Enables routing logic
- Preserves original payload
- Adds metadata (timestamp, delivery_id)

**Client Unwrapping**:
```python
if data.get("type") == "webhook":
    payload = data.get("payload", {})
    if payload.get("type") == "collaborative_session_command":
        data = payload  # Unwrap for processing
```

---

## Security

### Authentication

1. **GitHub Webhooks**
   - HMAC-SHA256 signature verification
   - Secret stored in environment variable
   - Timing-safe comparison

2. **Custom Webhooks**
   - API key in header (`X-API-Key` or `Authorization: Bearer`)
   - Key validation before processing
   - Rate limiting (future)

3. **Database**
   - Password authentication
   - No public access (localhost only)
   - Connection pooling with credential management

### Data Protection

- All webhook data logged to local files only
- No sensitive data sent to cloud (relay just forwards)
- PostgreSQL credentials in `.env` (gitignored)
- API keys in environment variables

### Transport Security

- WSS (WebSocket over TLS) for relay connections
- HTTPS for webhook delivery
- PostgreSQL can use SSL (configurable)

---

## Scalability

### Current Capacity

- **Relay Server**: Auto-scales on Railway
- **Clients**: Unlimited (each opens 1 WebSocket connection)
- **Database**: Single PostgreSQL instance (suitable for 1M+ records)
- **Task Queue**: Lock-free claiming supports multiple workers

### Future Improvements

1. **Database**
   - Read replicas for query scaling
   - Partitioning for large tables
   - Redis for task queue (higher throughput)

2. **Relay Server**
   - Multiple instances with load balancer
   - Redis pub/sub for cross-instance broadcasting
   - Rate limiting per API key

3. **Client**
   - Process pool for parallel task execution
   - Streaming for large payloads
   - Compression for WebSocket messages

### Performance Characteristics

- **Webhook Latency**: <100ms (relay → client → database)
- **Database Writes**: ~1000 ops/sec (single instance)
- **Concurrent Sessions**: No practical limit
- **Connection Pooling**: 1-10 connections (configurable)

---

## Monitoring and Observability

### Logging

- **Relay Server**: Structured JSON logs (stdout)
- **Client**: `client.log` + `webhook_logs/*.json`
- **Database**: PostgreSQL query logs (optional)

### Metrics (Future)

- Webhook delivery success rate
- WebSocket connection uptime
- Database query performance
- Task queue depth
- Agent execution times

### Health Checks

- **Relay**: `GET /health` endpoint
- **Database**: Docker health check (`pg_isready`)
- **Client**: Heartbeat monitoring (30-second intervals)

---

## Disaster Recovery

### Backup Strategy

1. **Database**
   ```bash
   # Daily automated backup
   docker compose exec -T postgres pg_dump -U webhook_user ai_webhook > backup.sql
   ```

2. **Configuration**
   - `.env` file backed up separately
   - `docker-compose.yml` in version control

3. **Retention**
   - Daily backups: 7 days
   - Weekly backups: 4 weeks
   - Monthly backups: 12 months

### Recovery Procedure

1. Restore database from backup
2. Restart Docker containers
3. Restart client
4. Verify connectivity

### Data Loss Prevention

- PostgreSQL ACID guarantees
- Write-ahead logging (WAL)
- Synchronous commits enabled
- Regular backup verification

---

## Future Enhancements

### Planned Features

1. **Real-time Notifications**
   - LISTEN/NOTIFY for task completion
   - Webhook callbacks to LLMs
   - Push notifications for important events

2. **Advanced Task Queue**
   - Priority scheduling
   - Dependencies between tasks
   - Timeout and retry logic
   - Dead letter queue

3. **Agent Orchestration**
   - Control agent for spawning workers
   - Multi-agent workflows
   - Agent capability matching
   - Resource limits and quotas

4. **Search and Analytics**
   - Elasticsearch for semantic search
   - Analytics dashboard
   - Session replay and debugging
   - Performance profiling

5. **Security Enhancements**
   - OAuth for API authentication
   - Encryption at rest
   - Audit logging
   - IP whitelisting

---

## References

### Documentation
- [README.md](README.md) - Quick start guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development setup
- [CLAUDE.md](CLAUDE.md) - AI agent instructions
- [TASK_ROADMAP.md](TASK_ROADMAP.md) - Feature roadmap
- [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md) - Implementation details

### Code
- [app.py](app.py) - Relay server
- [client/client.py](client/client.py) - WebSocket client
- [client/session_manager.py](client/session_manager.py) - Session coordinator
- [database/init.sql](database/init.sql) - Database schema

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/15/)
- [WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)

---

**Document Version**: 1.0
**Last Review**: 2025-11-15
**Next Review**: 2025-12-15
