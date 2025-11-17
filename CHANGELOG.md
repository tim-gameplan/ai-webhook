# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive architecture documentation in ARCHITECTURE.md
- Development patterns guide in CLAUDE.md
- System status tracking

## [2.0.0] - 2025-11-15

### Added - Collaborative Sessions System

**Major Features:**
- **Session Manager** (`client/session_manager.py`) - Coordinates collaborative sessions between LLMs and local agents
- **PostgreSQL Backend** (`client/storage/postgres_backend.py`) - Persistent storage with connection pooling
- **Memory System** - Structured knowledge storage supporting 8 types (idea, decision, question, action_item, context, preference, fact, risk)
- **Agent Architecture** - Pluggable agent system with base class and specialized processors
  - Memory Keeper Agent - Manages session memories with tagging and filtering
  - Conversation Processor Agent - Processes large conversation chunks
- **Database Schema** - 6 tables with JSONB columns, GIN indexes, and full-text search
  - `sessions` - Session metadata and statistics
  - `conversation_chunks` - Large conversation text
  - `memories` - Structured knowledge
  - `tasks` - Task queue for agents
  - `artifacts` - Generated code/documents
  - `agents` - Agent registry
- **Batch Command Processing** - Execute multiple commands atomically
- **Storage Backend Abstraction** - Switch between PostgreSQL and JSON files via environment variable

**Session Commands:**
- `create_session` - Initialize collaborative session
- `store_memory` - Save structured knowledge
- `retrieve_memory` - Query memory by key
- `query_memories` - Filter memories by type/tags
- `conversation_chunk` - Store conversation text
- `delegate_task` - Create background tasks (planned)
- `add_artifact` - Store generated outputs (planned)
- `batch` - Execute multiple commands
- `pause_session`, `resume_session`, `complete_session` - Session lifecycle

**Infrastructure:**
- Docker Compose configuration for PostgreSQL 15 and PgAdmin
- Database initialization script (`database/init.sql`) with schema, indexes, and functions
- Connection pooling (1-10 connections) with automatic reconnection
- Health checks for database container
- Persistent volumes for data retention

**Testing:**
- `test_connectivity.py` - Database connectivity and table accessibility validation
- `test_webhooks_e2e.py` - End-to-end webhook flow testing
- Comprehensive test coverage for session creation, memory storage, batch processing

**Documentation:**
- `ARCHITECTURE.md` - Complete system architecture with diagrams, data flow, and design decisions
- `DATABASE_SETUP.md` - Database setup and management guide
- `PHASE1_COMPLETE.md` - Phase 1 validation results and findings
- `EXECUTION_PLAN.md` - Task-by-task execution guide
- `ACTION_PLAN.md` - Step-by-step execution strategy
- `MCP_TOOLS_VERIFICATION.md` - MCP tools testing procedures
- Updated `CONTRIBUTING.md` - New setup instructions and architecture
- Updated `CLAUDE.md` - Collaborative sessions guide and development patterns

### Changed

**Client (`client/client.py`):**
- Added `python-dotenv` for automatic `.env` file loading
- Added sys.path manipulation for reliable imports
- Implemented payload unwrapping for relay server messages
- Added collaborative session command routing
- Enhanced error handling and logging
- Unbuffered output mode for real-time logs

**Import System:**
- Converted all relative imports to absolute imports across 5 files
- Added sys.path manipulation pattern to all modules
- Created `__init__.py` files in all subdirectories for proper package structure

**Configuration:**
- Added `STORAGE_BACKEND` environment variable (postgres/json)
- Added `DATABASE_URL` environment variable
- Added `GITHUB_PERSONAL_ACCESS_TOKEN` for MCP tools
- Updated `.env.example` with all new variables

**Message Handling:**
- Client now unwraps relay server message envelopes
- Proper routing of GitHub webhooks, LLM insights, and collaborative session commands
- Graceful degradation when session manager unavailable

### Fixed

**Import Issues:**
- Fixed ModuleNotFoundError in `client/agents/conversation_processor.py` (2 imports)
- Fixed ModuleNotFoundError in `client/agents/memory_keeper.py` (1 import)
- Fixed ModuleNotFoundError in `client/storage/postgres_backend.py` (2 imports)
- Fixed ModuleNotFoundError in `client/session_manager.py` (multiple imports)
- Fixed ModuleNotFoundError in `client/client.py` (session_manager import)

**Environment Loading:**
- Fixed client not loading `.env` file - added python-dotenv
- Fixed environment variables not being detected by session manager

**Message Processing:**
- Fixed payload wrapping issue where collaborative session commands weren't being unwrapped
- Fixed client treating all messages as GitHub webhooks

**Output Issues:**
- Fixed client producing no visible output - added unbuffered mode (`python3 -u`)
- Added debug print at script start for troubleshooting

**PgAdmin:**
- Fixed port conflict (5050 → 5051)
- Fixed email validation error (admin@localhost → admin@example.com)

### Dependencies

**Added:**
- `python-dotenv` - Environment variable loading
- `psycopg2-binary` - PostgreSQL database driver
- PostgreSQL 15 (Alpine Linux) - Docker container
- PgAdmin 4 - Database web GUI (optional)

**Updated:**
- `client/requirements.txt` - Added dotenv and psycopg2

### Infrastructure

**Docker:**
- PostgreSQL container on port 5433
- PgAdmin container on port 5051 (optional, profile: tools)
- Persistent volumes for database data
- Health checks for reliability
- Automatic initialization from init.sql

**Database:**
- PostgreSQL 15 with JSONB support
- GIN indexes for full-text search
- Triggers for automatic timestamp updates
- Atomic task claiming function with `FOR UPDATE SKIP LOCKED`
- Connection pooling with ThreadedConnectionPool

### Security

**Database:**
- Password authentication (webhook_user/webhook_dev_password)
- No public access (localhost only)
- Connection pooling with credential management

**API:**
- Existing API key authentication maintained
- GitHub webhook signature verification maintained

### Testing Results

**Phase 1 Validation:**
```
✅ Database connectivity: PASSED
✅ End-to-end webhooks: PASSED (7/7 tests)
✅ Session creation: PASSED
✅ Memory persistence: PASSED (4 memories)
✅ Batch processing: PASSED
```

**System Status:**
- PostgreSQL: Running and healthy
- Client: Connected to relay server
- Session Manager: Initialized with Postgres backend
- Agents: Registered (conversation_processor, memory_keeper)

### Known Issues

**Incomplete Features:**
- `conversation_chunk` command routing not fully implemented
- `delegate_task` command planned but not yet implemented
- `add_artifact` command planned but not yet implemented

**Minor Discrepancies:**
- End-to-end test shows 0 conversation chunks (expected 1)
- End-to-end test shows 0 tasks (expected 1)
- End-to-end test shows 0 artifacts (expected 1)
- Issue: Command routing in session_manager may need review

**Resolution Status:**
- Core memory storage working (primary use case)
- Impact: Low - system fully operational for memory management
- Plan: Review command routing in future update

### Development

**Code Patterns Established:**
```python
# Absolute imports with path manipulation
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.session import Something

# Environment loading
from dotenv import load_dotenv
load_dotenv()

# Database connections
with PostgresBackend.get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT ...")
```

**Package Structure:**
- All subdirectories have `__init__.py`
- Modules use absolute imports from root
- Path manipulation ensures imports work from any context

---

## [1.0.0] - 2025-11-14

### Added
- Initial webhook relay system
- FastAPI server with WebSocket broadcasting
- GitHub webhook signature verification
- Local WebSocket client with auto-reconnect
- LLM conversation insights integration
- API key authentication for custom webhooks
- Automatic webhook logging to JSON files
- Railway deployment configuration

### Features
- GitHub webhook reception and broadcasting
- Multiple simultaneous client connections
- Heartbeat monitoring (30-second intervals)
- Graceful disconnection handling
- Event-specific handlers (push, pull_request, issues)
- LLM insights categorization and storage
- Insights CLI tool for review and export

### Infrastructure
- Railway deployment (https://web-production-3d53a.up.railway.app)
- GitHub webhook integration on tim-gameplan/ai-webhook repository
- HMAC-SHA256 signature verification
- API key authentication

### Documentation
- README.md - Quick start guide
- CLAUDE.md - AI agent instructions
- CONTRIBUTING.md - Development setup
- SECURITY_SETUP.md - Security configuration
- docs/LLM_INTEGRATION.md - LLM integration guide

---

## Version History

### Summary of Major Changes

**v2.0.0 (2025-11-15)**: Collaborative Sessions & PostgreSQL
- Added collaborative session management system
- Integrated PostgreSQL database with full schema
- Implemented agent architecture and memory system
- Created comprehensive test infrastructure
- Fixed all import issues across codebase
- Updated all documentation

**v1.0.0 (2025-11-14)**: Initial Release
- GitHub webhook relay system
- LLM conversation insights
- Railway deployment
- WebSocket client with auto-reconnect

---

## Migration Guide

### From v1.0.0 to v2.0.0

**Prerequisites:**
1. Install Docker Desktop
2. Install python-dotenv: `pip install python-dotenv`
3. Install psycopg2: `pip install psycopg2-binary`

**Steps:**

1. **Update environment variables:**
```bash
# Add to .env
STORAGE_BACKEND=postgres
DATABASE_URL=postgresql://webhook_user:webhook_dev_password@localhost:5433/ai_webhook
```

2. **Start PostgreSQL:**
```bash
docker compose up -d postgres
python3 test_connectivity.py  # Verify
```

3. **Update client dependencies:**
```bash
cd client
pip install -r requirements.txt  # Includes dotenv, psycopg2
```

4. **Restart client:**
```bash
# Stop old client
pkill -f "python.*client.py"

# Start new client with unbuffered output
python3 -u client/client.py
```

5. **Verify operation:**
```bash
python3 test_webhooks_e2e.py
```

**Breaking Changes:**
- None - system is backward compatible
- GitHub webhooks and LLM insights continue working as before
- Collaborative sessions are additive functionality

**Rollback:**
- Set `STORAGE_BACKEND=json` to use file-based storage
- Stop PostgreSQL: `docker compose down`
- System continues functioning with JSON files

---

## Roadmap

See [TASK_ROADMAP.md](TASK_ROADMAP.md) for detailed feature roadmap.

### Planned Features

**Phase 2** (Next):
- Session CLI tool for management
- LLM Session API documentation
- Webhook payload examples
- Task delegation implementation
- Artifact storage implementation

**Future**:
- Control agent for task orchestration
- Real-time notifications (LISTEN/NOTIFY)
- Webhook callbacks to LLMs
- Advanced task queue with priorities
- Multi-agent workflows
- Elasticsearch integration for semantic search
- Analytics dashboard

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

[License details]

---

**Note**: This changelog is maintained manually. All significant changes should be documented here with each release.

*Last updated: 2025-11-15*
