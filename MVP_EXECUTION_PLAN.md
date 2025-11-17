# MVP Execution Plan: Voice LLM → Local Action System

**Last Updated**: 2025-01-17
**Status**: Ready for Parallel Execution
**Target Completion**: 10 hours (distributed across agents)

---

## Executive Summary

### What We're Building

Enable mobile voice LLMs (ChatGPT/Claude/Gemini on iPhone) to execute actions on local development machine.

**Example Flow**:
```
User (walking dog) → "Hey ChatGPT, review my latest code"
  ↓
ChatGPT sends webhook → Relay server → Local client
  ↓
Local client spawns Claude Code → Reviews code → Stores result
  ↓
User checks http://localhost:5001 → Sees review results
```

### Why This Matters

**Current Pain**: Can't execute local development tasks while mobile
**Solution**: Voice LLM acts as trigger for local automation
**Value**: Hands-free development task execution

### What Changed from Original Plan

**Before**: Complex PostgreSQL-based session management system with agent orchestration
**Now**: Simple SQLite-based task queue with immediate execution
**Why**: MVP to validate if this is actually useful before building infrastructure

---

## Architecture Overview

### Simplified Stack

```
┌─────────────────────────────────────────────────────────────┐
│                     MOBILE LAYER                             │
│  ChatGPT/Claude/Gemini App (iPhone)                         │
│  - Voice input from user                                     │
│  - Sends webhook via custom instructions                     │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTPS POST
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                     CLOUD LAYER                              │
│  Relay Server (Railway)                                      │
│  - Already deployed: web-production-3d53a.up.railway.app    │
│  - Receives webhooks                                         │
│  - Broadcasts via WebSocket                                  │
└─────────────────┬───────────────────────────────────────────┘
                  │ WebSocket
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                     LOCAL LAYER                              │
│                                                              │
│  ┌────────────────────────────────────────────────┐         │
│  │  Webhook Client (Python)                       │         │
│  │  - Receives task commands                      │         │
│  │  - Routes to task executor                     │         │
│  └────────────────┬───────────────────────────────┘         │
│                   │                                          │
│                   ▼                                          │
│  ┌────────────────────────────────────────────────┐         │
│  │  Task Executor (NEW)                           │         │
│  │  - Spawns: Claude Code, git, shell commands    │         │
│  │  - Captures output                             │         │
│  │  - Stores results in SQLite                    │         │
│  └────────────────┬───────────────────────────────┘         │
│                   │                                          │
│                   ▼                                          │
│  ┌────────────────────────────────────────────────┐         │
│  │  SQLite Database (NEW)                         │         │
│  │  - tasks table                                 │         │
│  │  - Simple, no Docker needed                    │         │
│  └────────────────────────────────────────────────┘         │
│                                                              │
│  ┌────────────────────────────────────────────────┐         │
│  │  Results Viewer (NEW)                          │         │
│  │  - Flask web app on :5001                      │         │
│  │  - Shows recent tasks and outputs              │         │
│  └────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### What We Keep from Existing System

✅ **Keep** (Already working):
- Relay server on Railway
- WebSocket client with auto-reconnect
- Webhook endpoint with API key auth
- Environment variable loading (dotenv)
- Client logging infrastructure

❌ **Remove** (Over-engineered for MVP):
- PostgreSQL database → Use SQLite
- Session manager → Use simple task queue
- Agent registry → Use hardcoded executors
- Collaborative sessions → Defer to Phase 2
- Memory system → Defer to Phase 2
- MCP tools → Not needed for MVP

🆕 **Add** (New for MVP):
- SQLite backend
- Task executor (spawns processes)
- Results web viewer
- LLM integration docs

---

## Task Breakdown

### Task Organization

Tasks are designed for **parallel execution** by multiple agents. Each task is self-contained with full context.

| Task | Agent Type | Dependencies | Estimated Time | Can Run in Parallel |
|------|------------|--------------|----------------|---------------------|
| **Task 1**: SQLite Backend | Backend Engineer | None | 2h | ✅ Yes |
| **Task 2**: Task Executor | Backend Engineer | None | 3h | ✅ Yes (different from T1) |
| **Task 3**: Results Viewer | Frontend Engineer | Task 1 | 2h | ⚠️ After Task 1 |
| **Task 4**: LLM Integration Docs | Documentation | None | 2h | ✅ Yes |
| **Task 5**: Testing & Scripts | DevOps | Tasks 1,2,3 | 1h | ⚠️ After T1,T2,T3 |

**Total Sequential**: 10 hours
**Total Parallel** (3 agents): ~5 hours

### Agent Assignments

**Agent A - Backend Engineer**:
- Task 1: SQLite Backend (2h)
- Task 2: Task Executor (3h)
- Total: 5h

**Agent B - Frontend Engineer**:
- Wait for Task 1 completion (or work on Task 4)
- Task 3: Results Viewer (2h)
- Total: 2h

**Agent C - Technical Writer**:
- Task 4: LLM Integration Documentation (2h)
- Total: 2h

**Agent D - DevOps (or Agent A after completion)**:
- Task 5: Testing & Startup Scripts (1h)
- Total: 1h

---

## Detailed Task Specifications

### Task 1: SQLite Backend Implementation

**Objective**: Create lightweight SQLite backend to replace PostgreSQL for task storage

**Input Requirements**:
- Current project structure in `client/`
- `.env` file with configuration
- Understanding of existing storage pattern

**Output Deliverables**:
1. `client/storage/sqlite_backend.py` - SQLite backend class
2. Updated `.env.example` with SQLite config
3. Database schema automatically created on first run
4. Test script to verify CRUD operations

**Acceptance Criteria**:
- Can create tasks with ID, command, status, input_data, output_data
- Can update task status and results
- Can query task by ID
- Can retrieve recent tasks (last N)
- Database file created at configurable path
- No Docker dependencies

**Technical Specifications**:
```python
# Required methods
class SimpleSQLiteBackend:
    def __init__(self, db_path="tasks.db")
    def create_task(task_id, command, input_data)
    def update_task(task_id, status, output_data=None, error=None)
    def get_task(task_id)
    def get_recent_tasks(limit=10)
```

**Schema**:
```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    command TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    input_data TEXT,
    output_data TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
)
```

**Testing**:
```python
# Must pass these tests
db = SimpleSQLiteBackend("test.db")
db.create_task("test_001", "git", '{"command": ["git", "status"]}')
task = db.get_task("test_001")
assert task is not None
db.update_task("test_001", "completed", '{"stdout": "clean"}')
```

**Reference**: See `MVP_EXECUTION_PLAN.md` Phase 1 for detailed implementation

**Documentation**: `tasks/task1-sqlite-backend.md`

---

### Task 2: Task Executor Implementation

**Objective**: Create task executor that spawns local processes (Claude Code, git, shell) and captures output

**Input Requirements**:
- Understanding of subprocess management in Python
- Knowledge of Claude Code CLI
- Access to test repository for git commands

**Output Deliverables**:
1. `client/task_executor.py` - Task executor class
2. Updated `client/client.py` to integrate executor
3. Error handling for timeouts, failures
4. Security validation for shell commands

**Acceptance Criteria**:
- Can execute git commands and capture output
- Can execute shell commands with timeout
- Can spawn Claude Code (if available)
- Handles process timeouts gracefully
- Captures stdout, stderr, return codes
- Stores results in database via SQLite backend
- Returns structured result format

**Technical Specifications**:
```python
class TaskExecutor:
    def __init__(self)
    def handle_task(task_data) -> dict
    def execute_claude_code(params) -> dict
    def execute_git(params) -> dict
    def execute_shell(params) -> dict
```

**Supported Action Types**:
1. `claude_code` - Spawn Claude Code with prompt
2. `git` - Execute git commands
3. `shell` - Execute shell commands (with safety checks)

**Input Format**:
```json
{
  "type": "task_command",
  "data": {
    "task_id": "unique_id",
    "action_type": "git",
    "params": {
      "command": ["git", "status"],
      "working_dir": "/path/to/repo",
      "timeout": 30
    }
  }
}
```

**Output Format**:
```json
{
  "status": "success",
  "task_id": "unique_id",
  "result": {
    "stdout": "...",
    "stderr": "...",
    "returncode": 0
  }
}
```

**Security Considerations**:
- Validate working_dir exists
- Implement timeout for all commands
- Consider command whitelist for shell execution
- Sanitize inputs

**Testing**:
```python
executor = TaskExecutor()

# Test git
result = executor.handle_task({
    "task_id": "test_git",
    "action_type": "git",
    "params": {"command": ["git", "status"]}
})
assert result["status"] == "success"

# Test shell
result = executor.handle_task({
    "task_id": "test_shell",
    "action_type": "shell",
    "params": {"command": "echo 'test'"}
})
assert "test" in result["result"]["stdout"]
```

**Reference**: See `MVP_EXECUTION_PLAN.md` Phase 2 for detailed implementation

**Documentation**: `tasks/task2-task-executor.md`

---

### Task 3: Results Viewer Implementation

**Objective**: Create simple web UI to view task results (since we can't push back to mobile LLM yet)

**Input Requirements**:
- Task 1 completed (SQLite backend exists)
- Understanding of Flask framework
- Basic HTML/CSS skills

**Output Deliverables**:
1. `client/results_server.py` - Flask app
2. `client/templates/tasks.html` - HTML template
3. API endpoint for individual task details
4. Auto-refresh or manual refresh UI

**Acceptance Criteria**:
- Shows list of recent tasks (last 20)
- Displays task status (pending, completed, failed)
- Shows task output/errors in readable format
- Color-coded status badges
- Responsive design (works on mobile)
- Runs on port 5001
- Can query specific task by ID via API

**Technical Specifications**:
```python
# Flask routes
@app.route('/')  # List tasks
@app.route('/api/task/<task_id>')  # Get task details JSON
```

**UI Requirements**:
- Clean, minimal design
- Monospace font for code output
- Status badges: green (completed), yellow (pending), red (failed)
- Timestamp display
- Pre-wrapped text for long output

**Testing**:
```bash
# Start server
python3 client/results_server.py

# Should be accessible at
curl http://localhost:5001
curl http://localhost:5001/api/task/test_001
```

**Reference**: See `MVP_EXECUTION_PLAN.md` Phase 3 for detailed implementation

**Documentation**: `tasks/task3-results-viewer.md`

---

### Task 4: LLM Integration Documentation

**Objective**: Create comprehensive guides for using the system with ChatGPT/Claude/Gemini mobile apps

**Input Requirements**:
- Understanding of webhook format
- Access to ChatGPT/Claude mobile apps for testing
- Knowledge of custom instructions feature

**Output Deliverables**:
1. `docs/LLM_ACTIONS.md` - Action reference guide
2. `docs/CHATGPT_SETUP.md` - ChatGPT-specific setup
3. `docs/CLAUDE_SETUP.md` - Claude-specific setup
4. `docs/GEMINI_SETUP.md` - Gemini-specific setup
5. `examples/` directory with example webhooks

**Acceptance Criteria**:
- Clear step-by-step setup instructions for each LLM
- Copy-paste ready custom instructions
- Example webhook payloads for all action types
- Troubleshooting section
- Security best practices
- Usage examples with expected outcomes

**Content Requirements**:

**For each LLM app**:
- How to add custom instructions
- What to tell the LLM about the webhook system
- Example conversations
- How to verify it's working

**Action examples**:
- Code review
- Git status/log
- Create new feature
- Run tests
- Deploy

**Example payload format**:
```json
{
  "type": "task_command",
  "data": {
    "task_id": "review_20250117_001",
    "action_type": "claude_code",
    "params": {
      "prompt": "Review latest changes",
      "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
    }
  }
}
```

**Testing**:
- Test each example with curl
- Verify custom instructions work in at least ChatGPT
- Ensure task IDs are unique and trackable

**Reference**: See `MVP_EXECUTION_PLAN.md` Phase 4 for detailed implementation

**Documentation**: `tasks/task4-llm-documentation.md`

---

### Task 5: Testing & Startup Scripts

**Objective**: Create automated tests and startup scripts for easy MVP operation

**Input Requirements**:
- Tasks 1, 2, 3 completed
- Understanding of bash scripting
- Access to test environment

**Output Deliverables**:
1. `start_mvp.sh` - Start all MVP services
2. `stop_mvp.sh` - Stop all services
3. `test_mvp.py` - Automated test suite
4. `MVP_QUICKSTART.md` - User guide
5. Updated `.env.example`

**Acceptance Criteria**:
- One-command startup: `./start_mvp.sh`
- Starts webhook client in background
- Starts results server in background
- Initializes SQLite if needed
- Provides clear status output
- Logs accessible
- Tests verify all functionality
- Graceful shutdown script

**Test Coverage**:
- SQLite backend CRUD operations
- Git command execution
- Shell command execution
- Results viewer accessibility
- Webhook endpoint connectivity
- End-to-end task flow

**Startup Script Requirements**:
```bash
#!/bin/bash
# start_mvp.sh

# Check dependencies
# Initialize SQLite
# Start webhook client (background)
# Start results server (background)
# Display status and URLs
# Show how to view logs
# Show how to stop
```

**Test Script Requirements**:
```python
# test_mvp.py

def test_sqlite_backend()
def test_git_execution()
def test_shell_execution()
def test_results_viewer()
def test_end_to_end_flow()
```

**Testing**:
```bash
# Should work out of box
git clone <repo>
cd ai-webhook
cp .env.example .env
# Edit .env
./start_mvp.sh
python3 test_mvp.py
```

**Reference**: See `MVP_EXECUTION_PLAN.md` Phase 5 for detailed implementation

**Documentation**: `tasks/task5-testing-scripts.md`

---

## Dependencies & Execution Order

### Dependency Graph

```
Task 1 (SQLite Backend)
  ├─→ Task 3 (Results Viewer) - needs DB to query
  └─→ Task 5 (Testing) - needs DB to test

Task 2 (Task Executor)
  └─→ Task 5 (Testing) - needs executor to test

Task 3 (Results Viewer)
  └─→ Task 5 (Testing) - needs viewer to test

Task 4 (LLM Docs)
  └─→ Independent, can run anytime

Task 5 (Testing)
  └─→ Requires Tasks 1, 2, 3 complete
```

### Execution Strategies

**Strategy 1: Sequential (Single Agent)**
```
Day 1: Task 1 (2h) → Task 2 (3h) → Task 3 (2h)
Day 2: Task 4 (2h) → Task 5 (1h)
Total: 10 hours over 2 days
```

**Strategy 2: Parallel (3 Agents)**
```
Hour 0-2:
  Agent A: Task 1 (SQLite Backend)
  Agent B: Task 4 (LLM Docs)
  Agent C: Task 2 (Task Executor) - first 2h

Hour 2-3:
  Agent A: Task 2 (Task Executor) - help finish
  Agent B: Task 3 (Results Viewer)
  Agent C: Task 2 (Task Executor) - final 1h

Hour 3-5:
  Agent A: Task 5 (Testing)
  Agent B: Complete Task 3
  Agent C: Documentation review

Total: ~5 hours with 3 agents
```

**Strategy 3: Hybrid (2 Agents)**
```
Agent A (Backend):
  Task 1 (2h) → Task 2 (3h)
  Total: 5h

Agent B (Frontend/Docs):
  Task 4 (2h) → Wait for Task 1 → Task 3 (2h)
  Total: 4h

Then either agent:
  Task 5 (1h)

Total: ~6 hours with 2 agents
```

---

## Context Documents

Each agent receives:

1. **This document** (`MVP_EXECUTION_PLAN.md`) - Overall context
2. **Specific task document** (`tasks/taskN-*.md`) - Detailed instructions
3. **MVP_CONTEXT.md** - Full system context and decisions
4. **Current codebase** - Existing files to understand
5. **ARCHITECTURE.md** - Original architecture (for reference)

---

## Success Criteria

### MVP Complete When:

- ✅ Can send webhook from ChatGPT mobile
- ✅ Task executes locally (git, shell, or Claude Code)
- ✅ Results stored in SQLite
- ✅ Can view results at http://localhost:5001
- ✅ All tests pass
- ✅ Documentation complete
- ✅ One-command startup works

### Validation Plan (Post-MVP)

**Week 1 of Usage**:
1. Send at least 5 tasks from mobile LLM
2. Track: success rate, latency, usefulness
3. Note: What actions were most valuable?
4. Identify: What didn't work?

**Decision Point**:
- If useful → Build Phase 2 (real-time notifications)
- If not useful → Archive and learn

---

## Risk Mitigation

### Potential Issues

**Risk 1**: Claude Code CLI not available
- **Mitigation**: Test with git and shell first, Claude Code is optional for MVP

**Risk 2**: WebSocket disconnections
- **Mitigation**: Already handled in existing client with auto-reconnect

**Risk 3**: Task takes too long
- **Mitigation**: Implement timeouts in executor (default 300s)

**Risk 4**: LLMs don't send proper webhooks
- **Mitigation**: Test with curl first, iterate on custom instructions

**Risk 5**: Results viewer not accessible on mobile
- **Mitigation**: Use responsive design, test on iPhone

---

## Communication Protocol

### For Agents Working in Parallel

**Before Starting**:
- Announce in shared channel which task you're taking
- Check for dependencies (e.g., don't start Task 3 until Task 1 done)

**During Execution**:
- Commit code frequently to feature branch
- Mark task as "in progress" in tracking
- Ask questions in shared channel

**When Complete**:
- Run basic smoke test
- Document any deviations from spec
- Mark task as "complete"
- Notify dependent tasks

**Handoff Format**:
```
Task N Complete ✅

Deliverables:
- File 1: path/to/file1.py
- File 2: path/to/file2.py

Testing:
- Tested: X, Y, Z
- All passing

Notes:
- Any issues or deviations
- Suggestions for dependent tasks

Ready for: Task M (depends on this)
```

---

## Next Steps

### To Start Execution

1. **Create individual task documents** (in `tasks/` directory)
2. **Create MVP_CONTEXT.md** (full context for agents)
3. **Assign tasks to agents**
4. **Set up communication channel**
5. **Begin parallel execution**

### Agent Onboarding

Each agent should:
1. Read `MVP_EXECUTION_PLAN.md` (this document)
2. Read `MVP_CONTEXT.md` (system context)
3. Read their specific task document
4. Review existing codebase
5. Ask clarifying questions
6. Begin implementation

---

## Questions for Project Lead

Before agents begin, clarify:

1. **Claude Code availability**: Do we have Claude Code CLI installed?
2. **Test repository**: Which repo should be used for testing git commands?
3. **API Key**: Is the production API key available in `.env`?
4. **Timeline**: Is 10-hour total / 5-hour parallel acceptable?
5. **Agent assignments**: Who is working on which tasks?

---

**Document Status**: ✅ Ready for Agent Assignment
**Last Review**: 2025-01-17
**Next Review**: After MVP completion

