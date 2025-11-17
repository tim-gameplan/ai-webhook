# MVP Context Document for Agent Execution

**Purpose**: Provide complete context to agents working on MVP tasks
**Audience**: AI agents implementing MVP features
**Last Updated**: 2025-01-17

---

## What You Need to Know

### The Big Picture

We're building a system that lets you use voice LLMs on your phone (ChatGPT, Claude, Gemini) to trigger code execution on your local development machine.

**Why**: You're walking your dog and think "I should review that PR" - instead of waiting to get back to your computer, you just tell ChatGPT and it happens.

**How**: ChatGPT sends a webhook → Our relay server → Your local machine → Claude Code reviews the code → You check results later on your phone.

---

## Project History & Evolution

### Original Vision (v1.0)

Built a GitHub webhook relay system that broadcasts GitHub events to local machines via WebSocket.

**What existed**:
- Relay server on Railway (FastAPI + WebSocket)
- Local Python client with auto-reconnect
- GitHub webhook signature verification
- LLM conversation insights capture

**Status**: ✅ Complete and working

### Expansion Attempt (v2.0) - OVER-ENGINEERED

Tried to build comprehensive collaborative session system:
- PostgreSQL database with 6 tables
- Complex session management
- Agent registry and orchestration
- Background task workers
- Memory persistence system

**Status**: ❌ **Abandoned** - Too complex for uncertain value

**What we learned**:
- Built infrastructure before validating the problem
- PostgreSQL + Docker is overkill for personal tool
- Session management unnecessary for MVP
- Need to test if anyone actually wants this first

### Current Pivot (v2.1 MVP) - SIMPLIFIED

Strip everything down to absolute minimum:
- Replace PostgreSQL → SQLite (no Docker)
- Replace session management → Simple task queue
- Replace agent registry → Hardcoded executors
- Add: Simple results viewer (since no real-time notifications yet)

**Goal**: Build in 10 hours, test for 1 week, decide if worth continuing

---

## Current System State

### What's Already Built and Working ✅

**1. Relay Server (Production)**
- URL: `https://web-production-3d53a.up.railway.app`
- Endpoints:
  - `GET /` - Health check
  - `POST /webhook` - Receive webhooks (GitHub signature OR API key auth)
  - `WebSocket /ws` - Client connections
- Authentication: API key in header (`X-API-Key` or `Authorization: Bearer`)
- Status: Deployed on Railway, operational

**2. WebSocket Client**
- File: `client/client.py`
- Features:
  - Connects to relay server via WebSocket
  - Auto-reconnect with retry logic
  - Heartbeat mechanism (30-second intervals)
  - Handles GitHub webhooks
  - Handles LLM conversation insights
  - Logs to `webhook_logs/` directory
  - Uses `python-dotenv` for `.env` loading
- Status: Working, needs integration with new task executor

**3. Environment Configuration**
- `.env` file with variables:
  - `RELAY_SERVER_URL` - WebSocket endpoint
  - `API_KEY` - Authentication key
  - `STORAGE_BACKEND` - (will change to 'sqlite')
  - `GITHUB_WEBHOOK_SECRET` - For GitHub webhooks
- Status: Working, needs SQLite config added

**4. Documentation Infrastructure**
- `ARCHITECTURE.md` - Full system architecture (refers to v2.0)
- `CONTRIBUTING.md` - Onboarding guide
- `CLAUDE.md` - Development patterns
- `CHANGELOG.md` - Change history
- Status: Needs update for MVP pivot

### What's Not Built (Your Job) 🆕

**1. SQLite Backend** - Task 1
- Current: PostgreSQL backend exists at `client/storage/postgres_backend.py`
- Needed: `client/storage/sqlite_backend.py`
- Why: No Docker, simpler, faster iteration

**2. Task Executor** - Task 2
- Current: Session manager exists but too complex
- Needed: `client/task_executor.py`
- Why: Need to actually spawn processes and capture output

**3. Results Viewer** - Task 3
- Current: Nothing exists
- Needed: `client/results_server.py` + HTML template
- Why: Can't push results back to mobile LLM yet (Phase 2)

**4. LLM Integration Docs** - Task 4
- Current: Generic docs exist
- Needed: Specific mobile app setup guides
- Why: Users need to know how to configure ChatGPT/Claude

**5. Testing & Scripts** - Task 5
- Current: Some test files exist (`test_connectivity.py`, `test_webhooks_e2e.py`)
- Needed: MVP-specific tests and startup script
- Why: One-command startup for MVP

---

## Technical Architecture

### Data Flow (MVP)

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: User triggers action via voice                          │
│                                                                  │
│ User: "Hey ChatGPT, what's the status of my repo?"             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: ChatGPT sends webhook (per custom instructions)         │
│                                                                  │
│ POST https://web-production-3d53a.up.railway.app/webhook        │
│ Header: X-API-Key: <key>                                        │
│ Body: {                                                         │
│   "type": "task_command",                                       │
│   "data": {                                                     │
│     "task_id": "git_status_001",                               │
│     "action_type": "git",                                       │
│     "params": {                                                 │
│       "command": ["git", "status"],                            │
│       "working_dir": "/path/to/repo"                           │
│     }                                                           │
│   }                                                             │
│ }                                                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Relay server broadcasts via WebSocket                   │
│                                                                  │
│ Relay wraps in envelope:                                        │
│ {                                                               │
│   "type": "webhook",                                            │
│   "timestamp": "2025-01-17T...",                               │
│   "payload": { <original data> }                               │
│ }                                                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │ WebSocket
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Local client receives and unwraps                       │
│                                                                  │
│ File: client/client.py                                          │
│ Function: handle_webhook(data)                                  │
│                                                                  │
│ Unwraps payload if type == "webhook"                           │
│ Detects type == "task_command"                                 │
│ Routes to task executor                                         │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Task executor processes (NEW - YOU BUILD THIS)          │
│                                                                  │
│ File: client/task_executor.py                                   │
│ Class: TaskExecutor                                             │
│                                                                  │
│ 1. Creates task in SQLite (status='pending')                   │
│ 2. Determines action type (git/shell/claude_code)              │
│ 3. Spawns subprocess:                                           │
│    subprocess.run(['git', 'status'], capture_output=True)      │
│ 4. Captures stdout, stderr, returncode                         │
│ 5. Updates task in SQLite (status='completed', output_data)    │
│ 6. Returns result                                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: Results stored in SQLite (NEW - YOU BUILD THIS)         │
│                                                                  │
│ File: tasks.db (SQLite database)                                │
│ Table: tasks                                                     │
│                                                                  │
│ INSERT INTO tasks VALUES (                                      │
│   'git_status_001',                                             │
│   'git',                                                        │
│   'completed',                                                  │
│   '{"command": ["git", "status"]}',                            │
│   '{"stdout": "On branch main...", "returncode": 0}',          │
│   NULL,                                                         │
│   '2025-01-17 10:30:00',                                       │
│   '2025-01-17 10:30:00',                                       │
│   '2025-01-17 10:30:02'                                        │
│ )                                                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 7: User checks results (NEW - YOU BUILD THIS)              │
│                                                                  │
│ User opens: http://localhost:5001                              │
│                                                                  │
│ Flask app (results_server.py) shows:                            │
│ ┌─────────────────────────────────────────────────────┐        │
│ │ Recent Tasks                                         │        │
│ │                                                      │        │
│ │ git_status_001  [completed]  10:30 AM               │        │
│ │ git                                                  │        │
│ │ ┌─────────────────────────────────────────────┐    │        │
│ │ │ On branch main                               │    │        │
│ │ │ Your branch is up to date with 'origin/main'│    │        │
│ │ │ nothing to commit, working tree clean        │    │        │
│ │ └─────────────────────────────────────────────┘    │        │
│ └─────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### File Structure

```
ai-webhook/
├── app.py                          # Relay server (already deployed)
├── client/
│   ├── client.py                   # WebSocket client (✅ exists, needs update)
│   ├── task_executor.py            # 🆕 YOU BUILD - Task executor
│   ├── results_server.py           # 🆕 YOU BUILD - Flask results viewer
│   ├── storage/
│   │   ├── postgres_backend.py     # ✅ exists (reference for structure)
│   │   └── sqlite_backend.py       # 🆕 YOU BUILD - SQLite backend
│   ├── templates/
│   │   └── tasks.html              # 🆕 YOU BUILD - Results page template
│   ├── session_manager.py          # ❌ ignore (v2.0, too complex)
│   ├── agents/                     # ❌ ignore (v2.0, too complex)
│   └── handlers/                   # ✅ exists (LLM insights)
├── docs/
│   ├── LLM_ACTIONS.md              # 🆕 YOU BUILD - Action reference
│   ├── CHATGPT_SETUP.md            # 🆕 YOU BUILD - ChatGPT guide
│   ├── CLAUDE_SETUP.md             # 🆕 YOU BUILD - Claude guide
│   └── GEMINI_SETUP.md             # 🆕 YOU BUILD - Gemini guide
├── examples/                       # 🆕 YOU BUILD - Example webhooks
├── tasks.db                        # 🆕 GENERATED - SQLite database
├── start_mvp.sh                    # 🆕 YOU BUILD - Startup script
├── test_mvp.py                     # 🆕 YOU BUILD - Test suite
├── .env                            # ✅ exists, needs SQLITE config
└── .env.example                    # ✅ exists, needs update

Files to IGNORE (v2.0 complexity):
- database/ - PostgreSQL schema (not using)
- docker-compose.yml - Not needed for MVP
- client/session_manager.py - Too complex
- client/agents/ - Not needed for MVP
- POSTGRES_IMPLEMENTATION.md - Old plan
- PARALLEL_EXECUTION_PLAN.md - Old plan
```

---

## Code Patterns & Standards

### Import Pattern

**Always use this pattern** at the top of Python files:
```python
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now use absolute imports
from storage.sqlite_backend import SimpleSQLiteBackend
from task_executor import TaskExecutor
```

**Why**: Relative imports break when running files as scripts. This pattern works everywhere.

### Environment Variables

**Always load .env**:
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Must be early in script

DATABASE_PATH = os.getenv("SQLITE_PATH", "./tasks.db")
API_KEY = os.getenv("API_KEY")
```

### Error Handling

**Always handle errors gracefully**:
```python
def execute_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30  # Always set timeout
        )
        return {
            'success': True,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Command timed out after 30s'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

### Subprocess Execution

**Security best practices**:
```python
# Good - list format, no shell=True for git
subprocess.run(['git', 'status'], shell=False)

# Acceptable - shell=True only when necessary, with timeout
subprocess.run('echo test', shell=True, timeout=5)

# Bad - shell=True with user input (injection risk)
subprocess.run(user_input, shell=True)  # DON'T DO THIS
```

### Database Patterns

**Use context managers**:
```python
# SQLite auto-commit
def update_task(self, task_id, status):
    cursor = self.conn.cursor()
    cursor.execute(
        "UPDATE tasks SET status=? WHERE id=?",
        (status, task_id)
    )
    self.conn.commit()  # Explicit commit
```

**Store JSON as TEXT**:
```python
import json

# Storing
input_data_json = json.dumps({"command": ["git", "status"]})
cursor.execute("INSERT INTO tasks (input_data) VALUES (?)", (input_data_json,))

# Retrieving
row = cursor.fetchone()
input_data = json.loads(row[3]) if row[3] else {}
```

---

## Environment Configuration

### Current .env Structure

```bash
# Relay Server
RELAY_SERVER_URL=wss://web-production-3d53a.up.railway.app/ws
API_KEY=qVaBlMjz5GODXoAdpOJs_Hl_y3HolOqSvnCJf-YcZok

# Storage (UPDATE THIS FOR MVP)
STORAGE_BACKEND=sqlite                    # Change from 'postgres'
SQLITE_PATH=./tasks.db                    # Add this

# GitHub (optional)
GITHUB_WEBHOOK_SECRET=xERIgwNMvCWU5B2-K0jWxdjWD4d--tdkSmte_9jHm28
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_REDACTED_FOR_SECURITY

# Old (ignore for MVP)
DATABASE_URL=postgresql://...             # Not using
```

### What Needs to Change

**Update `.env`**:
```bash
STORAGE_BACKEND=sqlite
SQLITE_PATH=./tasks.db
```

**Update `.env.example`**:
```bash
# Add comments for MVP
STORAGE_BACKEND=sqlite  # Use 'sqlite' for MVP (no Docker needed)
SQLITE_PATH=./tasks.db  # Path to SQLite database file
```

---

## Testing Approach

### Manual Testing

**Test each component individually**:

**SQLite Backend**:
```python
from storage.sqlite_backend import SimpleSQLiteBackend

db = SimpleSQLiteBackend("test.db")
db.create_task("test_001", "git", '{"command": ["git", "status"]}')
task = db.get_task("test_001")
print(task)  # Should show task data
db.update_task("test_001", "completed", '{"stdout": "success"}')
```

**Task Executor**:
```python
from task_executor import TaskExecutor

executor = TaskExecutor()
result = executor.handle_task({
    "task_id": "test_git",
    "action_type": "git",
    "params": {"command": ["git", "status"]}
})
print(result)  # Should show success with git output
```

**Results Viewer**:
```bash
python3 client/results_server.py
# Open browser: http://localhost:5001
# Should see task list
```

### End-to-End Testing

**Full flow test**:
```bash
# 1. Start client
python3 -u client/client.py &

# 2. Send webhook
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: qVaBlMjz5GODXoAdpOJs_Hl_y3HolOqSvnCJf-YcZok" \
  -d '{
    "type": "task_command",
    "data": {
      "task_id": "e2e_test",
      "action_type": "git",
      "params": {
        "command": ["git", "log", "--oneline", "-5"],
        "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
      }
    }
  }'

# 3. Check client logs
tail -f client.log
# Should see: ✅ Task executed: e2e_test

# 4. Check database
sqlite3 tasks.db "SELECT * FROM tasks WHERE id='e2e_test';"

# 5. View in browser
open http://localhost:5001
```

---

## Integration Points

### How Client Integrates with Executor

**Current `client/client.py` structure**:
```python
# Line ~60: handle_webhook function
def handle_webhook(data: dict):
    # ... existing code for GitHub webhooks, LLM insights ...

    # ADD THIS: Handle task commands
    if data.get("type") == "task_command":
        if TASK_EXECUTOR_AVAILABLE:
            result = task_executor.handle_task(data.get("data", {}))
            print(f"✅ Task executed: {result.get('task_id')}")
            if result.get('status') == 'error':
                print(f"   Error: {result.get('error')}")
        else:
            print("⚠️  Task executor not available")
        return
```

**Initialization** (add near top of client.py):
```python
# Import task executor
try:
    from task_executor import TaskExecutor
    task_executor = TaskExecutor()
    TASK_EXECUTOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Task executor not available: {e}")
    TASK_EXECUTOR_AVAILABLE = False
```

### How Executor Uses SQLite Backend

**In `task_executor.py`**:
```python
from storage.sqlite_backend import SimpleSQLiteBackend

class TaskExecutor:
    def __init__(self):
        self.db = SimpleSQLiteBackend()

    def handle_task(self, task_data):
        task_id = task_data.get('task_id')

        # Create task
        self.db.create_task(task_id, ...)

        # Execute
        result = self._execute(...)

        # Update task
        self.db.update_task(task_id, 'completed', result)
```

### How Results Viewer Queries Database

**In `results_server.py`**:
```python
from storage.sqlite_backend import SimpleSQLiteBackend

app = Flask(__name__)
db = SimpleSQLiteBackend()

@app.route('/')
def index():
    tasks = db.get_recent_tasks(limit=20)
    return render_template('tasks.html', tasks=tasks)
```

---

## Common Pitfalls to Avoid

### 1. Path Issues

❌ **Bad**:
```python
# Hardcoded paths
db = SimpleSQLiteBackend("/Users/tim/tasks.db")
```

✅ **Good**:
```python
# Use environment variable
db_path = os.getenv("SQLITE_PATH", "./tasks.db")
db = SimpleSQLiteBackend(db_path)
```

### 2. JSON Handling

❌ **Bad**:
```python
# Storing dict directly
cursor.execute("INSERT INTO tasks (input_data) VALUES (?)", ({"cmd": "test"},))
```

✅ **Good**:
```python
# Convert to JSON string
input_json = json.dumps({"cmd": "test"})
cursor.execute("INSERT INTO tasks (input_data) VALUES (?)", (input_json,))
```

### 3. Subprocess Security

❌ **Bad**:
```python
# Shell injection vulnerable
cmd = f"git {user_input}"
subprocess.run(cmd, shell=True)
```

✅ **Good**:
```python
# Safe - no shell injection
subprocess.run(['git'] + validated_args, shell=False)
```

### 4. Missing Timeouts

❌ **Bad**:
```python
# Could hang forever
result = subprocess.run(['git', 'status'])
```

✅ **Good**:
```python
# Timeout after 30 seconds
result = subprocess.run(['git', 'status'], timeout=30)
```

---

## Existing Code References

### Relay Server (app.py)

**Webhook endpoint** (lines 99-159):
```python
@app.post("/webhook")
async def receive_webhook(request: Request):
    # Validates API key or GitHub signature
    # Broadcasts to all connected WebSocket clients
```

**Message format sent to clients**:
```python
message = {
    "type": "webhook",
    "event": event_type,
    "delivery_id": delivery_id,
    "timestamp": datetime.utcnow().isoformat(),
    "payload": payload  # Original webhook data
}
```

### WebSocket Client (client/client.py)

**Connection handling** (lines 180-227):
```python
async def connect_with_retry(max_retries, retry_delay):
    # Auto-reconnect with exponential backoff
    # Maintains heartbeat (30s intervals)
```

**Payload unwrapping** (lines 69-78):
```python
if data.get("type") == "webhook":
    payload = data.get("payload", {})
    if payload.get("type") == "collaborative_session_command":
        data = payload  # Unwrap
```

You'll add similar unwrapping for `task_command`.

---

## Dependencies

### Python Packages Already Installed

```
# Server (requirements.txt)
fastapi==0.104.1
uvicorn==0.24.0
websockets==12.0
python-dotenv==1.0.0

# Client (client/requirements.txt)
websockets==12.0
python-dotenv==1.0.0
requests==2.31.0
psycopg2-binary==2.9.9  # Not using in MVP
```

### Additional Packages Needed for MVP

```bash
# Add to client/requirements.txt
flask==3.0.0  # For results viewer
```

**Install**:
```bash
cd client
pip install flask
```

---

## Decision Log

### Why SQLite Instead of PostgreSQL?

**Decision**: Use SQLite for MVP instead of PostgreSQL

**Rationale**:
- No Docker dependency (faster setup)
- File-based (easy backup, portable)
- Zero configuration
- Perfect for single-user tool
- Can migrate to Postgres later if needed

**Trade-offs**:
- Less concurrent access (fine for MVP)
- No network access (fine, it's local)
- Simpler query features (fine for our needs)

### Why No Real-Time Notifications in MVP?

**Decision**: Results viewer instead of pushing back to LLM

**Rationale**:
- Real-time notifications require:
  - Webhook callback URLs in LLM
  - NOTIFY/LISTEN in database
  - More complex relay server
- MVP should validate if system is useful first
- User can check results manually via web UI
- Can add in Phase 2 if MVP proves valuable

**Trade-offs**:
- Less seamless experience
- User must remember to check results
- But: Much faster to build

### Why Hardcoded Executors Instead of Agent Registry?

**Decision**: Simple executor class with hardcoded action types

**Rationale**:
- Only need 3 action types for MVP: git, shell, claude_code
- Agent registry adds complexity: DB table, registration, discovery
- Can hardcode faster, iterate quicker
- Can refactor to registry later if needed

**Trade-offs**:
- Less extensible
- Adding new action types requires code change
- But: Faster MVP delivery

---

## Success Metrics

### How We'll Know MVP Works

**Technical Metrics**:
- ✅ All unit tests pass
- ✅ End-to-end test completes
- ✅ Results viewer loads
- ✅ Tasks execute within timeout
- ✅ Database stores all fields correctly

**User Metrics** (After 1 week):
- How many tasks executed?
- What % succeeded?
- Which action types most used?
- Average time to complete?
- Did user actually check results?

**Validation Questions**:
1. Is this faster than just SSHing to machine?
2. Is this easier than using Claude Desktop?
3. Do I actually use it or is it novelty?
4. What would make this indispensable?

---

## Next Phase Preview (If MVP Succeeds)

**Phase 2: Real-Time Notifications**
- Add LISTEN/NOTIFY to PostgreSQL
- Push results back to LLM via webhook
- LLM can respond with results in conversation
- Upgrade to PostgreSQL for better notifications

**Phase 3: Advanced Features**
- File operations (read, write, search)
- Multi-step workflows
- Parallel task execution
- Better error recovery

**But**: Only build if MVP proves valuable!

---

## Getting Help

### Resources

1. **MVP_EXECUTION_PLAN.md** - This file's parent, overall plan
2. **Task-specific docs** - In `tasks/` directory
3. **Existing codebase** - Reference implementations
4. **ARCHITECTURE.md** - Original v2.0 architecture (for context)

### Questions to Ask

**Before implementing**:
- "Do I understand the input format?"
- "Do I understand the expected output?"
- "Do I know how this integrates with other components?"
- "What are the edge cases?"

**During implementation**:
- "Am I following the code patterns?"
- "Am I handling errors?"
- "Can I test this in isolation?"

**Before marking complete**:
- "Does it match the acceptance criteria?"
- "Have I tested it?"
- "Did I document any deviations?"

---

## Final Checklist for Agents

Before starting your task:
- [ ] Read MVP_EXECUTION_PLAN.md
- [ ] Read this context document (MVP_CONTEXT.md)
- [ ] Read your specific task document
- [ ] Understand the existing codebase
- [ ] Check dependencies on other tasks
- [ ] Set up local environment
- [ ] Ask any clarifying questions

While implementing:
- [ ] Follow code patterns
- [ ] Handle errors gracefully
- [ ] Set appropriate timeouts
- [ ] Test in isolation
- [ ] Commit frequently

Before marking complete:
- [ ] All acceptance criteria met
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Handoff message written
- [ ] Dependent tasks notified

---

**Document Status**: ✅ Complete
**Questions?**: Ask in shared communication channel
**Ready to build!** 🚀

