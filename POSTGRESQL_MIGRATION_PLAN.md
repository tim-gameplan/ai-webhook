# PostgreSQL Migration Plan - Enable Full Collaborative Features

**Date**: 2025-11-17
**Goal**: Switch from SQLite to PostgreSQL to enable memory storage, sessions, and agent capabilities
**Estimated Time**: 2-3 hours

---

## Current State Assessment

### What's Working ✅
- **PostgreSQL Database**: Running and healthy (port 5433)
- **All Tables Created**: sessions, memories, conversation_chunks, tasks, artifacts, agents
- **Client Code**: Supports both task execution AND collaborative sessions
- **Session Manager**: Built and previously tested (PHASE1_COMPLETE.md)
- **Agents**: memory_keeper, conversation_processor
- **Sync Mode**: Task execution with immediate results (127ms response)
- **Relay Server**: Production-ready on Railway

### What's Currently Disabled ❌
- **Storage Backend**: Set to `sqlite` instead of `postgres`
- **Session Manager**: Not loading (because sqlite backend doesn't support sessions)
- **Memory Storage**: Not available
- **Collaborative Features**: Not accessible from LLM

### Why SQLite Was Used (MVP Phase)
- Simplified initial deployment (no Docker requirement)
- Faster iteration for task execution feature
- Testing sync mode independently

### Why Switch to PostgreSQL Now
- **Full Feature Set**: Memory storage, sessions, conversation chunks
- **Better Structure**: JSONB fields for flexible data
- **Full-Text Search**: Search across conversations and memories
- **Concurrent Access**: Multiple clients/agents can work together
- **Already Built**: All code exists and was validated in Phase 1

---

## Architecture Overview

### PostgreSQL Schema (Already Exists)

**sessions** - Session metadata
```sql
- id (TEXT PRIMARY KEY)
- title (TEXT)
- status (TEXT) - active, paused, completed
- created (TIMESTAMP)
- updated (TIMESTAMP)
- participants (TEXT[])
- memory_count (INTEGER)
- task_count (INTEGER)
- metadata (JSONB)
```

**memories** - Structured knowledge storage
```sql
- id (SERIAL PRIMARY KEY)
- session_id (TEXT FK -> sessions.id)
- type (TEXT) - idea, decision, question, action_item, context, preference, fact, risk
- key (TEXT) - unique identifier
- content (JSONB) - flexible structure
- tags (TEXT[])
- created (TIMESTAMP)
- updated (TIMESTAMP)
```

**conversation_chunks** - Large conversation text
```sql
- id (SERIAL PRIMARY KEY)
- session_id (TEXT FK -> sessions.id)
- chunk_number (INTEGER)
- content (TEXT)
- created (TIMESTAMP)
- search_vector (TSVECTOR) - full-text search
```

**tasks** - Background agent tasks
```sql
- id (TEXT PRIMARY KEY)
- session_id (TEXT FK -> sessions.id)
- assigned_agent (TEXT)
- status (TEXT)
- input_data (JSONB)
- output_data (JSONB)
- created, started, completed (TIMESTAMPS)
```

**artifacts** - Generated code/documents
```sql
- id (SERIAL PRIMARY KEY)
- session_id (TEXT FK -> sessions.id)
- artifact_type (TEXT)
- name (TEXT)
- content (TEXT)
- metadata (JSONB)
```

**agents** - Agent registry
```sql
- id (TEXT PRIMARY KEY)
- name (TEXT)
- capabilities (TEXT[])
- status (TEXT)
- metadata (JSONB)
```

---

## Available Commands (Already Implemented)

### Session Management
- `create_session` - Initialize new collaborative session
- `resume_session` - Resume paused session
- `pause_session` - Pause active session
- `complete_session` - Mark session as complete
- `list_sessions` - List all sessions
- `get_session_summary` - Get session statistics

### Memory Operations
- `store_memory` - Save structured knowledge (ideas, decisions, questions, etc.)
- `retrieve_memory` - Get specific memory by key
- `query_memories` - Filter memories by type/tags
- `list_memories` - List all memories in session

### Conversation Storage
- `conversation_chunk` - Store large conversation text with full-text search

### Task Management
- `delegate_task` - Create task for background agent (future)
- `add_artifact` - Store generated code/documents (future)

### Batch Operations
- `batch` - Execute multiple commands atomically

---

## Migration Steps

### Phase 1: Switch Backend (15 minutes)

**Task 1.1: Update Environment Configuration**
```bash
# Edit .env
STORAGE_BACKEND=postgres  # Change from 'sqlite'
DATABASE_URL=postgresql://webhook_user:webhook_dev_password@localhost:5433/ai_webhook
```

**Task 1.2: Verify PostgreSQL Running**
```bash
docker compose ps
# Should show postgres as "Up (healthy)"
```

**Task 1.3: Test Database Connection**
```bash
python3 test_connectivity.py
# Should show: ✅ ALL TESTS PASSED
```

**Task 1.4: Restart Client**
```bash
# Stop current client
pkill -f "client.py"

# Start with PostgreSQL backend
python3 -u client/client.py

# Should see:
# 🗄️  Using PostgreSQL storage backend
# 📋 Session Manager initialized
#    Registered agents: ['conversation_processor', 'memory_keeper']
```

**Validation**: Client startup logs should show session manager loaded

---

### Phase 2: Test Collaborative Features (30 minutes)

**Task 2.1: Create Test Session**
```bash
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: qVaBlMjz5GODXoAdpOJs_Hl_y3HolOqSvnCJf-YcZok" \
  -d '{
    "type": "collaborative_session_command",
    "command": "create_session",
    "data": {
      "session_id": "mobile_test_001",
      "title": "Mobile LLM Test Session",
      "participants": ["chatgpt", "developer"]
    }
  }'
```

Expected response:
```json
{
  "status": "success",
  "message": "Session created: mobile_test_001"
}
```

**Task 2.2: Store Memory (Idea)**
```bash
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: qVaBlMjz5GODXoAdpOJs_Hl_y3HolOqSvnCJf-YcZok" \
  -d '{
    "type": "collaborative_session_command",
    "command": "store_memory",
    "data": {
      "session_id": "mobile_test_001",
      "type": "idea",
      "key": "feature_carbon_tracking",
      "content": {
        "title": "Add carbon emissions tracking",
        "description": "Track CO2 emissions for all API calls",
        "priority": "medium"
      },
      "tags": ["sustainability", "feature", "api"]
    }
  }'
```

**Task 2.3: Store Memory (Decision)**
```bash
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: qVaBlMjz5GODXoAdpOJs_Hl_y3HolOqSvnCJf-YcZok" \
  -d '{
    "type": "collaborative_session_command",
    "command": "store_memory",
    "data": {
      "session_id": "mobile_test_001",
      "type": "decision",
      "key": "use_opentelemetry",
      "content": {
        "decision": "Use OpenTelemetry for observability",
        "rationale": "Industry standard with good LLM integration",
        "alternatives_considered": ["Datadog", "Custom solution"]
      },
      "tags": ["architecture", "observability"]
    }
  }'
```

**Task 2.4: Query Memories**
```bash
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: qVaBlMjz5GODXoAdpOJs_Hl_y3HolOqSvnCJf-YcZok" \
  -d '{
    "type": "collaborative_session_command",
    "command": "query_memories",
    "data": {
      "session_id": "mobile_test_001",
      "type": "idea",
      "tags": ["feature"]
    }
  }'
```

**Task 2.5: Verify in Database**
```bash
docker compose exec -T postgres psql -U webhook_user -d ai_webhook -c \
  "SELECT id, title, memory_count FROM sessions WHERE id = 'mobile_test_001';"

docker compose exec -T postgres psql -U webhook_user -d ai_webhook -c \
  "SELECT type, key, tags FROM memories WHERE session_id = 'mobile_test_001';"
```

**Validation**: Should see session created with 2 memories stored

---

### Phase 3: Create Example Webhooks (20 minutes)

**Task 3.1: Create Session Examples**
- `examples/session_create.json`
- `examples/session_list.json`

**Task 3.2: Create Memory Examples**
- `examples/memory_store_idea.json`
- `examples/memory_store_decision.json`
- `examples/memory_store_question.json`
- `examples/memory_query.json`

**Task 3.3: Create Batch Example**
- `examples/batch_session_setup.json` - Create session + store multiple memories

**Task 3.4: Create Conversation Example**
- `examples/conversation_store.json`

---

### Phase 4: Update LLM Instructions (45 minutes)

**Task 4.1: Create Comprehensive Mobile Prompt**

Create `MOBILE_LLM_INSTRUCTIONS.md` with sections:
- Task Execution (git, shell)
- Session Management (create, resume)
- Memory Storage (ideas, decisions, questions)
- Memory Retrieval (query by type/tags)
- Conversation Storage
- Batch Operations

**Task 4.2: Create Compact Version**

Optimize for mobile character limits:
- Core features only
- Condensed syntax examples
- Focus on most common operations

**Task 4.3: Create Use Case Examples**

Document real-world scenarios:
- "Remember this architectural decision"
- "Store this idea for later"
- "What decisions did we make about X?"
- "Add this to the project plan"

---

### Phase 5: End-to-End Validation (30 minutes)

**Test Scenario 1: Project Planning Session**
1. Create session: "Feature X Planning"
2. Store idea: "Add user authentication"
3. Store decision: "Use JWT tokens"
4. Store question: "Which OAuth provider?"
5. Query all decisions
6. Verify data persists across client restarts

**Test Scenario 2: Code Review Session**
1. Create session: "Code Review - PR #123"
2. Store conversation chunk (review comments)
3. Store action items found
4. Query action items
5. Verify full-text search works

**Test Scenario 3: Combined Operations**
1. Create session
2. Execute git status (task command)
3. Store git output as context memory
4. Store action item based on git status
5. Query memories
6. Batch command to update multiple memories

**Validation Criteria**:
- ✅ All commands return success
- ✅ Data persists in PostgreSQL
- ✅ Client logs show session manager activity
- ✅ Memories queryable by type/tags
- ✅ Sessions show correct counts
- ✅ Full-text search returns results

---

## Updated Mobile LLM Prompt Structure

### Core Sections

**1. Task Execution** (Already working)
- Git commands with sync mode
- Shell commands with sync mode
- Immediate results in response

**2. Session Management** (New)
- Create/resume/list sessions
- Session context for related work
- Organize conversations by project/feature

**3. Memory Storage** (New)
- Store ideas, decisions, questions
- Tag and categorize knowledge
- Flexible JSONB content

**4. Memory Retrieval** (New)
- Query by type: "Show all decisions"
- Query by tags: "Show all security-related items"
- Full-text search across memories

**5. Conversation Storage** (New)
- Store large conversation chunks
- Full-text search capability
- Preserve context for later reference

**6. Batch Operations** (New)
- Multiple commands in one request
- Atomic execution
- Efficient for setup workflows

---

## Prompt Length Optimization

### Tier 1: Full Version (~2500 chars)
- All features documented
- Multiple examples per feature
- Use for: Claude Projects, desktop LLMs

### Tier 2: Medium Version (~1500 chars)
- Core features with 1 example each
- Abbreviated syntax
- Use for: ChatGPT Custom Instructions

### Tier 3: Minimal Version (~800 chars)
- Task execution + basic memory storage
- Ultra-compact syntax
- Use for: Strict character limits

---

## Risk Mitigation

### Risk 1: Session Manager Import Failure
**Mitigation**: Test session manager import before client startup
```python
try:
    from session_manager import get_session_manager
    session_manager = get_session_manager()
except Exception as e:
    print(f"Failed to load session manager: {e}")
    # Fallback to task-only mode
```

### Risk 2: PostgreSQL Connection Issues
**Mitigation**: Connection pooling already implemented
- Min connections: 1
- Max connections: 10
- Auto-reconnect on failure

### Risk 3: Client Already Running with SQLite
**Mitigation**: Kill existing client before switching
```bash
pkill -f "client.py"
# Wait 2 seconds
sleep 2
# Start new client
python3 -u client/client.py
```

### Risk 4: Memory Overload from Large Sessions
**Mitigation**:
- Use conversation_chunks for large text (PostgreSQL handles it)
- Pagination for memory queries (limit parameter)
- Session archival for completed sessions

---

## Success Metrics

### Technical Metrics
- ✅ Client starts with PostgreSQL backend
- ✅ Session manager loads successfully
- ✅ All agents registered (memory_keeper, conversation_processor)
- ✅ Database operations complete without errors
- ✅ Full-text search returns results
- ✅ Memory queries filter correctly by type/tags

### User Experience Metrics
- ✅ LLM can create sessions from mobile
- ✅ LLM can store memories in natural conversation
- ✅ LLM can retrieve stored knowledge on demand
- ✅ Memories persist across conversations
- ✅ Task execution + memory storage work together seamlessly

### Performance Metrics
- Session creation: < 100ms
- Memory storage: < 50ms
- Memory query: < 100ms
- Batch operations: < 500ms for 10 commands
- Full-text search: < 200ms

---

## Rollback Plan

If PostgreSQL migration fails, revert to SQLite:

```bash
# 1. Stop client
pkill -f "client.py"

# 2. Revert .env
STORAGE_BACKEND=sqlite

# 3. Restart client
python3 -u client/client.py

# 4. Task execution still works (SQLite mode)
```

---

## Timeline

**Total Estimated Time**: 2-3 hours

- Phase 1 (Backend Switch): 15 minutes
- Phase 2 (Feature Testing): 30 minutes
- Phase 3 (Examples): 20 minutes
- Phase 4 (LLM Instructions): 45 minutes
- Phase 5 (Validation): 30 minutes
- Buffer: 30 minutes

**Can be parallelized**:
- Testing (Phase 2) while creating examples (Phase 3)
- Writing instructions (Phase 4) while system stabilizes

---

## Next Steps After Migration

1. **Test from Mobile LLM**: Real-world validation with ChatGPT/Claude
2. **Add More Agents**: Research agent, code analysis agent
3. **Advanced Features**:
   - Conversation summarization
   - Automatic knowledge extraction
   - Cross-session memory search
4. **UI Improvements**: Web dashboard for sessions/memories (beyond current results viewer)

---

## Documentation to Create

1. **MOBILE_LLM_INSTRUCTIONS.md** - Comprehensive guide for LLM
2. **COLLABORATIVE_SESSIONS_GUIDE.md** - User guide with examples
3. **SESSION_API_REFERENCE.md** - Complete API documentation
4. **MEMORY_TYPES_GUIDE.md** - When to use each memory type

---

## Key Differences: SQLite vs PostgreSQL Mode

| Feature | SQLite Mode | PostgreSQL Mode |
|---------|-------------|-----------------|
| Task Execution | ✅ Full support | ✅ Full support |
| Sync Mode | ✅ Works | ✅ Works |
| Session Management | ❌ Not available | ✅ Full support |
| Memory Storage | ❌ Not available | ✅ Full support |
| Conversation Chunks | ❌ Not available | ✅ Full support |
| Full-Text Search | ❌ No | ✅ Yes |
| Concurrent Clients | ⚠️  Limited | ✅ Full support |
| Agent Coordination | ❌ No | ✅ Yes |
| JSONB Queries | ❌ No | ✅ Yes |
| Setup Complexity | ✅ Simple (no Docker) | ⚠️  Requires Docker |

---

## Questions to Answer Before Starting

1. ✅ Is PostgreSQL running? **YES** - Up 7 hours, healthy
2. ✅ Are all tables created? **YES** - All 6 tables exist
3. ✅ Is client code ready? **YES** - Supports both modes
4. ✅ Are agents implemented? **YES** - memory_keeper, conversation_processor
5. ✅ Has this been tested before? **YES** - PHASE1_COMPLETE.md shows full validation

**Conclusion**: All infrastructure is ready. Just need to flip the switch!

---

**Status**: READY TO EXECUTE
**Confidence**: High (90%) - Infrastructure already validated
**Blocker**: None
**Ready**: Now
