# AI Webhook - Task Roadmap

## Current State

### ✅ Completed
- [x] GitHub webhook relay system (server + client)
- [x] Collaborative session models and data structures
- [x] Session manager with command routing
- [x] Conversation processor agent
- [x] Memory keeper agent
- [x] PostgreSQL database schema and Docker setup
- [x] PostgreSQL storage backend implementation
- [x] MCP tools configuration (Postgres, GitHub, Filesystem)
- [x] Backend abstraction (JSON/Postgres switching)
- [x] Comprehensive testing of Postgres backend

### 🎯 Current Focus
Building out the full collaborative session workflow with background agent orchestration.

---

## Phase 1: Core Infrastructure Validation (IMMEDIATE)

**Goal**: Verify all infrastructure is working end-to-end

### 1.1 Test MCP Tools Connectivity
**Priority**: HIGH
**Estimated Time**: 30 minutes

**Tasks**:
- Use MCP Postgres tool to query sessions table
- Verify can insert/update/query through MCP
- Test GitHub MCP tool connectivity
- Verify filesystem MCP tool access

**Success Criteria**:
- Can query database using natural language through MCP
- Can create/update sessions via MCP
- All MCP tools listed and functional

**Blockers**: None

---

### 1.2 Data Migration (if needed)
**Priority**: MEDIUM
**Estimated Time**: 1 hour

**Tasks**:
- Check for existing JSON session data in `sessions/` directory
- Create migration script to import JSON → Postgres
- Verify data integrity after migration
- Archive JSON files after successful migration

**Success Criteria**:
- All existing sessions migrated to Postgres
- No data loss
- JSON files backed up

**Blockers**: None

---

### 1.3 Switch to Postgres by Default
**Priority**: HIGH
**Estimated Time**: 15 minutes

**Tasks**:
- Update `.env` to set `STORAGE_BACKEND=postgres`
- Update client startup to verify Postgres connection
- Test client with Postgres backend
- Update documentation

**Success Criteria**:
- Client uses Postgres automatically
- Clear error messages if database unavailable
- Documentation updated

**Blockers**: 1.2 (if migration needed)

---

### 1.4 End-to-End Webhook Testing
**Priority**: HIGH
**Estimated Time**: 1 hour

**Tasks**:
- Start relay server and client
- Send test collaborative session webhooks
- Verify session creation in Postgres
- Test conversation chunks, memories, tasks
- Verify data persists across client restarts

**Success Criteria**:
- Full webhook → session → Postgres flow working
- All command types tested
- Data persists correctly

**Blockers**: 1.3

---

## Phase 2: Core Workflow - Session Management (HIGH PRIORITY)

**Goal**: Make sessions easy to create, view, and manage

### 2.1 Session CLI Tool
**Priority**: HIGH
**Estimated Time**: 2 hours

**Tasks**:
- Build `session_cli.py` with commands:
  - `session create <id> [--title] [--participants]`
  - `session list [--status] [--limit]`
  - `session show <id>`
  - `session summary <id>`
  - `session pause <id>`
  - `session complete <id>`
  - `session delete <id>`
- Add colored output and formatting
- Add JSON export option
- Add search/filter capabilities

**Success Criteria**:
- Can manage all sessions from command line
- User-friendly output
- Works with both JSON and Postgres backends

**Blockers**: 1.3

**Example Usage**:
```bash
python session_cli.py list --status active
python session_cli.py show morning_meeting_001
python session_cli.py create voice_session_123 --title "Product Planning"
```

---

### 2.2 LLM Prompt Guide
**Priority**: HIGH
**Estimated Time**: 2 hours

**Tasks**:
- Create `docs/LLM_SESSION_API.md` with:
  - Overview of collaborative sessions
  - All webhook command formats
  - Example payloads for each command
  - Best practices for LLMs
  - Common workflows
  - Error handling
- Create example prompts for ChatGPT/Claude mobile apps
- Add to CLAUDE.md for this project

**Success Criteria**:
- LLMs can understand how to use the API
- Copy-paste examples work
- Covers all use cases from original vision

**Blockers**: None

---

### 2.3 Webhook Payload Examples
**Priority**: MEDIUM
**Estimated Time**: 1 hour

**Tasks**:
- Create `examples/` directory
- Add example payloads:
  - `create_session.json`
  - `conversation_batch.json`
  - `store_memory.json`
  - `delegate_task.json`
  - `add_artifact.json`
  - `batch_workflow.json`
- Add curl commands for testing
- Document expected responses

**Success Criteria**:
- Can copy-paste examples to test system
- Covers all main use cases
- Includes error cases

**Blockers**: None

---

## Phase 3: Background Agent Orchestration (CRITICAL)

**Goal**: Implement the core vision - LLM delegates work to background agents

### 3.1 Control Agent Implementation
**Priority**: CRITICAL
**Estimated Time**: 4 hours

**Tasks**:
- Create `control_agent.py`:
  - Poll task queue using `claim_task()` function
  - Spawn background agents (Claude Code, Codex, Gemini CLI)
  - Track process IDs in tasks table
  - Monitor agent execution
  - Capture output and update task results
  - Handle agent failures and timeouts
- Add agent-specific spawn logic
- Implement output parsing
- Add task timeout handling

**Success Criteria**:
- Can claim and execute tasks automatically
- Spawns correct agent based on task.agent_name
- Captures output correctly
- Updates task status in database
- Handles failures gracefully

**Blockers**: 2.2 (to understand task format)

**Technical Details**:
```python
# Claim task
task = claim_task('claude_code', 'control_agent_1')

# Spawn agent
process = subprocess.Popen([
    'claude-code',
    '--task', json.dumps(task.input_data)
], stdout=PIPE, stderr=PIPE)

# Track in DB
update_task(task_id, process_id=process.pid, status='running')

# Wait and capture output
stdout, stderr = process.communicate(timeout=300)

# Update result
update_task(task_id,
    status='completed',
    output_data={'result': stdout},
    completed=datetime.utcnow()
)
```

---

### 3.2 Task Queue Worker
**Priority**: CRITICAL
**Estimated Time**: 3 hours

**Tasks**:
- Create `task_worker.py`:
  - Continuous polling loop
  - Priority-based task selection
  - Concurrency limits (max N tasks per agent)
  - Graceful shutdown
  - Heartbeat updates
- Add worker registration in agents table
- Implement worker health checks
- Add retry logic for failed tasks

**Success Criteria**:
- Worker runs continuously
- Respects agent concurrency limits
- Updates heartbeat regularly
- Handles shutdown gracefully
- Retries failed tasks appropriately

**Blockers**: 3.1

---

### 3.3 Agent Registry Configuration
**Priority**: MEDIUM
**Estimated Time**: 1 hour

**Tasks**:
- Update agents table with real configurations:
  - Claude Code: `claude`, max_concurrent: 2
  - Codex: `node codex/cli.js`, max_concurrent: 3
  - Gemini CLI: `gemini`, max_concurrent: 1
  - Researcher: `python agents/researcher.py`, max_concurrent: 3
- Create agent capability definitions
- Document agent input/output formats
- Add agent-specific error handling

**Success Criteria**:
- All agents properly registered
- Correct spawn commands
- Capabilities documented

**Blockers**: None

---

## Phase 4: Real-Time & Production Features (MEDIUM PRIORITY)

### 4.1 Agent Heartbeat System
**Priority**: MEDIUM
**Estimated Time**: 2 hours

**Tasks**:
- Implement heartbeat updates in control agent
- Add last_heartbeat monitoring
- Create cleanup job for stale agents
- Add alerts for offline agents
- Update agents status automatically

**Success Criteria**:
- Can detect when agents go offline
- Stale tasks are released back to queue
- System self-heals from agent crashes

**Blockers**: 3.2

---

### 4.2 LISTEN/NOTIFY for Real-Time Updates
**Priority**: MEDIUM
**Estimated Time**: 3 hours

**Tasks**:
- Add Postgres LISTEN/NOTIFY triggers
- Implement notification listener in client
- Send real-time updates when:
  - Tasks complete
  - Artifacts created
  - Memories stored
- Add webhook callback for task completion

**Success Criteria**:
- LLM gets notified when background work completes
- Can continue conversation with results
- Minimal latency (< 1 second)

**Blockers**: 3.2

---

### 4.3 Structured Logging & Monitoring
**Priority**: MEDIUM
**Estimated Time**: 2 hours

**Tasks**:
- Add structured logging with levels
- Log all webhook commands
- Log all task state changes
- Log agent spawn/completion
- Add performance metrics
- Create log aggregation strategy

**Success Criteria**:
- Easy to debug issues
- Can track performance
- Logs structured (JSON) for parsing

**Blockers**: None

---

## Phase 5: Production Readiness (LOWER PRIORITY)

### 5.1 Production Postgres Deployment
**Priority**: LOW
**Estimated Time**: 2 hours

**Tasks**:
- Choose managed Postgres provider (Railway/Supabase/AWS RDS)
- Set up production database
- Configure connection pooling
- Set up SSL connections
- Update production .env

**Success Criteria**:
- Production database running
- Accessible from deployed services
- Encrypted connections
- Connection pooling configured

**Blockers**: Phase 3 complete

---

### 5.2 Automated Database Backups
**Priority**: LOW
**Estimated Time**: 2 hours

**Tasks**:
- Set up automated pg_dump backups
- Configure backup retention (7 days, 4 weeks, 12 months)
- Add backup verification
- Document restore procedure
- Test restore process

**Success Criteria**:
- Daily backups running
- Can restore from backup
- Backups verified automatically

**Blockers**: 5.1

---

### 5.3 API Documentation
**Priority**: LOW
**Estimated Time**: 3 hours

**Tasks**:
- Document all webhook commands
- Add OpenAPI/Swagger spec
- Create interactive API docs
- Document error codes
- Add rate limiting docs

**Success Criteria**:
- Complete API reference
- Interactive testing available
- Clear error documentation

**Blockers**: None

---

## Phase 6: Future Enhancements (BACKLOG)

### 6.1 Redis Task Queue Migration
- Move task queue from Postgres to Redis
- Use Redis pub/sub for notifications
- Implement Redis Streams for task queue
- Add job scheduling with delays

### 6.2 Elasticsearch Integration
- Add Elasticsearch for advanced search
- Index all conversations, memories, artifacts
- Implement semantic search
- Add search suggestions

### 6.3 Web Dashboard
- Build React dashboard
- View active sessions
- Monitor agent status
- Search conversations
- Task queue visualization

### 6.4 Rate Limiting & Security
- Add rate limiting per API key
- Implement webhook signature verification
- Add IP whitelisting
- Implement authentication/authorization

### 6.5 Agent Plugins
- Plugin system for custom agents
- Agent marketplace
- Custom agent templates
- Agent composition (chain multiple agents)

---

## Recommended Execution Order

### Week 1: Validation & Foundation
1. Test MCP tools (30 min)
2. Switch to Postgres default (15 min)
3. End-to-end testing (1 hour)
4. Session CLI tool (2 hours)
5. LLM prompt guide (2 hours)
6. Webhook examples (1 hour)

**Total**: ~7 hours

### Week 2: Core Agent Orchestration
1. Agent registry configuration (1 hour)
2. Control agent implementation (4 hours)
3. Task queue worker (3 hours)
4. Testing and debugging (2 hours)

**Total**: ~10 hours

### Week 3: Real-Time & Polish
1. Agent heartbeat system (2 hours)
2. LISTEN/NOTIFY implementation (3 hours)
3. Structured logging (2 hours)
4. Integration testing (2 hours)
5. Documentation updates (1 hour)

**Total**: ~10 hours

### Week 4: Production Deployment
1. Production Postgres setup (2 hours)
2. Automated backups (2 hours)
3. Deploy to production (2 hours)
4. Monitoring setup (2 hours)
5. Load testing (2 hours)

**Total**: ~10 hours

---

## Critical Path

To achieve the core vision (LLM in voice conversation delegating work to background agents):

```
Phase 1.3 → Phase 2.2 → Phase 3.1 → Phase 3.2 → Phase 4.2
```

**Minimum Viable Product (MVP)**:
1. ✅ Postgres backend working
2. [ ] LLM prompt guide complete
3. [ ] Control agent spawning background agents
4. [ ] Task queue worker processing tasks
5. [ ] Real-time notifications of task completion

**Estimated Time to MVP**: ~20 hours

---

## Dependencies & Blockers

**Current Blockers**: None - ready to proceed!

**External Dependencies**:
- PostgreSQL running (✅ Complete)
- Claude Code CLI available
- Codex/Gemini CLI available
- Relay server deployed (✅ Complete)

**Risk Mitigation**:
- Can test with mock agents initially
- Postgres can be swapped to managed service later
- Can start with synchronous task execution before real-time

---

## Metrics for Success

### Phase 1-2 Success Metrics
- [ ] Can create session via webhook
- [ ] Can store conversation chunks
- [ ] Can query memories
- [ ] Sessions persist in Postgres
- [ ] Can manage sessions via CLI

### Phase 3 Success Metrics
- [ ] Control agent spawns background agents
- [ ] Tasks execute successfully
- [ ] Results stored in database
- [ ] Multiple agents can run concurrently
- [ ] Failed tasks are retried

### Phase 4 Success Metrics
- [ ] Real-time task completion notifications
- [ ] Agent heartbeat tracking
- [ ] < 1 second latency for notifications
- [ ] System self-heals from failures

### Production Success Metrics
- [ ] 99.9% uptime
- [ ] < 100ms query response time
- [ ] Handle 100+ concurrent sessions
- [ ] Zero data loss
- [ ] Automated backups running
