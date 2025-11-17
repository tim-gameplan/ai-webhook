# Action Plan - Get System Operational

**Goal**: Fix import issues and complete Phase 1 validation
**Estimated Total Time**: 2-3 hours
**Current Status**: Ready to begin

---

## Task List Overview

### Block 1: Fix Import Issues (1.5 hours)
Tasks 1-5 must be completed sequentially

### Block 2: Validation Testing (1 hour)
Tasks 6-8 must be done in order, after Block 1

### Block 3: MCP Verification (30 minutes)
Tasks 9-11 can be done in any order, manual testing

### Block 4: Documentation (15 minutes)
Task 12 - final wrap-up

---

## Detailed Task Breakdown

### ✅ BLOCK 1: Fix Import Issues

#### Task 1: Fix client/agents/base_agent.py
**Time**: 15 minutes
**Priority**: HIGH
**Dependencies**: None

**Steps**:
1. Read `client/agents/base_agent.py`
2. Find all `from .` imports
3. Convert to absolute imports:
   - Add path manipulation if needed
   - Change `from .models import X` to `from models import X`
4. Save and test import

**Expected Changes**:
```python
# Before
from .models.session import AgentTask

# After
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.session import AgentTask
```

**Verification**:
```bash
cd client && python3 -c "from agents.base_agent import BaseAgent; print('✅ Import successful')"
```

---

#### Task 2: Fix client/agents/conversation_processor.py
**Time**: 15 minutes
**Priority**: HIGH
**Dependencies**: Task 1 complete

**Steps**:
1. Read `client/agents/conversation_processor.py`
2. Find all `from .` imports
3. Convert to absolute imports
4. Ensure inherits from fixed BaseAgent

**Expected Imports to Fix**:
- Likely imports from `.base_agent`
- Possibly imports from `.models`

**Verification**:
```bash
cd client && python3 -c "from agents.conversation_processor import ConversationProcessorAgent; print('✅ Import successful')"
```

---

#### Task 3: Fix client/agents/memory_keeper.py
**Time**: 15 minutes
**Priority**: HIGH
**Dependencies**: Task 1 complete

**Steps**:
1. Read `client/agents/memory_keeper.py`
2. Find all `from .` imports
3. Convert to absolute imports
4. Ensure inherits from fixed BaseAgent

**Verification**:
```bash
cd client && python3 -c "from agents.memory_keeper import MemoryKeeperAgent; print('✅ Import successful')"
```

---

#### Task 4: Check and Fix client/models/session.py
**Time**: 20 minutes
**Priority**: MEDIUM
**Dependencies**: None

**Steps**:
1. Read `client/models/session.py`
2. Check if it has ANY imports from other client modules
3. If yes, convert those to absolute imports
4. If no relative imports, mark as complete

**Potential Issues**:
- May import from storage backends
- May have cross-references to agents

**Verification**:
```bash
cd client && python3 -c "from models.session import CollaborativeSession; print('✅ Import successful')"
```

---

#### Task 5: Check and Fix client/storage/postgres_backend.py
**Time**: 20 minutes
**Priority**: MEDIUM
**Dependencies**: Task 4 complete (in case it imports models)

**Steps**:
1. Read `client/storage/postgres_backend.py`
2. Check for relative imports
3. If found, convert to absolute imports
4. Special attention: It likely imports from models.session

**Known Issue**:
Currently it doesn't use relative imports for models, but might for other modules

**Verification**:
```bash
cd client && python3 -c "from storage.postgres_backend import PostgresBackend; print('✅ Import successful')"
```

---

### ✅ BLOCK 2: Validation Testing

#### Task 6: Test Client Import
**Time**: 10 minutes
**Priority**: CRITICAL
**Dependencies**: Tasks 1-5 complete

**Steps**:
1. Test session_manager import:
```bash
cd client && python3 -c "from session_manager import get_session_manager; sm = get_session_manager(); print(f'✅ Session manager loaded: {type(sm)}')"
```

2. Check for any error messages
3. Verify it prints "Using PostgreSQL storage backend"

**Success Criteria**:
- No import errors
- Session manager creates successfully
- PostgreSQL backend selected

**If Fails**:
- Check which specific import is failing
- Review that file again
- Verify all path manipulations are correct

---

#### Task 7: Start Client and Verify Connection
**Time**: 15 minutes
**Priority**: CRITICAL
**Dependencies**: Task 6 complete

**Steps**:
1. Stop any running client processes:
```bash
pkill -f "python.*client.py"
```

2. Start client in foreground with timeout:
```bash
timeout 10 python3 client/client.py 2>&1
```

3. Verify you see:
   - "GitHub Webhook Client"
   - "Using PostgreSQL storage backend"
   - "Session Manager initialized"
   - "Connecting to relay server"
   - "Connected! Waiting for webhooks"

4. If successful, start in background:
```bash
python3 client/client.py > client.log 2>&1 &
```

**Success Criteria**:
- Client starts without errors
- WebSocket connects successfully
- Session manager loads
- No import error messages

**If Fails**:
- Review client.log for errors
- Check if relay server is accessible
- Verify RELAY_SERVER_URL in .env

---

#### Task 8: Run End-to-End Webhook Test
**Time**: 20 minutes
**Priority**: CRITICAL
**Dependencies**: Task 7 complete (client must be running)

**Steps**:
1. Ensure client is running in background
2. Run test script:
```bash
python3 test_webhooks_e2e.py
```

3. Watch for:
   - All 7 webhook tests pass ✅
   - `clients_notified: 1` (not 0!)
   - Database verification passes ✅

4. If successful, verify in database:
```bash
python3 test_connectivity.py
```

5. Check for new session starting with `e2e_test_`:
```bash
docker compose exec -T postgres psql -U webhook_user -d ai_webhook -c "SELECT id, title, created FROM sessions WHERE id LIKE 'e2e_test_%' ORDER BY created DESC LIMIT 1;"
```

**Success Criteria**:
- All 7 webhook types delivered
- Client receives and processes webhooks
- Data persists in all relevant tables:
  - sessions: +1
  - conversation_chunks: +1
  - memories: +4 (idea, decision, question, action_item)
  - tasks: +1
  - artifacts: +1

**If Fails**:
- Check client.log for processing errors
- Verify database connection from client
- Check webhook_logs/ for received payloads
- Review session_manager error messages

---

### ✅ BLOCK 3: MCP Verification (Manual in Claude Code)

#### Task 9: Verify MCP Postgres Tool
**Time**: 10 minutes
**Priority**: MEDIUM
**Dependencies**: Database running

**Steps** (in Claude Code interactive session):
1. Ask: "Show me all sessions in the database"
2. Ask: "How many tasks are pending?"
3. Ask: "Search for memories tagged with 'feature'"

**Success Criteria**:
- Claude can query database via MCP
- Returns accurate results
- No connection errors

**Reference**: See MCP_TOOLS_VERIFICATION.md for detailed test queries

---

#### Task 10: Verify MCP GitHub Tool
**Time**: 10 minutes
**Priority**: LOW
**Dependencies**: GITHUB_PERSONAL_ACCESS_TOKEN set

**Steps** (in Claude Code interactive session):
1. Ask: "What's the current branch?"
2. Ask: "Show recent commits"
3. Ask: "List open issues"

**Success Criteria**:
- Claude can access GitHub via MCP
- Returns repository information
- Token authentication works

**If Fails**:
- Verify GITHUB_PERSONAL_ACCESS_TOKEN in .env
- Check token has correct scopes (repo, read:org, read:user)
- Test token manually with curl

---

#### Task 11: Verify MCP Filesystem Tool
**Time**: 5 minutes
**Priority**: LOW
**Dependencies**: None

**Steps** (in Claude Code interactive session):
1. Ask: "List all Python files in the client directory"
2. Ask: "Show me the database schema"
3. Ask: "What's in the .env file?"

**Success Criteria**:
- Claude can read project files via MCP
- Can navigate directory structure
- Has access to configured path

---

### ✅ BLOCK 4: Documentation Update

#### Task 12: Update Documentation
**Time**: 15 minutes
**Priority**: LOW
**Dependencies**: All previous tasks complete

**Steps**:
1. Update PHASE1_VALIDATION_RESULTS.md:
   - Change status from "PARTIALLY COMPLETE" to "COMPLETE"
   - Update "What's Broken" section to "What Was Fixed"
   - Add final test results
   - Update database record counts

2. Update TASK_ROADMAP.md:
   - Mark Phase 1 tasks as complete
   - Note any new issues discovered
   - Update time estimates based on actual

3. Create IMPORT_FIXES.md documenting:
   - What was broken
   - How it was fixed
   - Pattern to follow for future modules

**Success Criteria**:
- Documentation accurately reflects current state
- Future developers can understand what was done
- Lessons learned are captured

---

## Execution Strategy

### Sequential Approach (Recommended)
```
Start → Task 1 → Task 2 → Task 3 → Task 4 → Task 5
          ↓
        Task 6 (test imports)
          ↓
        Task 7 (start client)
          ↓
        Task 8 (e2e test)
          ↓
   Tasks 9-11 (MCP verification - parallel OK)
          ↓
        Task 12 (docs)
          ↓
        Done!
```

**Timeline**:
- Morning session (2 hours): Tasks 1-8
- Afternoon session (1 hour): Tasks 9-12

### Checkpoint Strategy

**Checkpoint 1** (after Task 5):
- All imports fixed
- Can proceed to testing

**Checkpoint 2** (after Task 6):
- Imports verified working
- Can proceed to client startup

**Checkpoint 3** (after Task 8):
- End-to-end flow working
- System is operational
- Can proceed to Phase 2

---

## Risk Mitigation

### If Block 1 Takes Longer Than Expected
**Symptoms**: More files have imports than expected, complex dependency chains

**Mitigation**:
- Take systematic approach: fix one file completely before moving to next
- Test each file in isolation before moving on
- Create a checklist of all import locations

### If Block 2 Tests Fail
**Symptoms**: Client won't start, WebSocket won't connect, data doesn't persist

**Troubleshooting**:
1. Check client.log for specific errors
2. Verify database is running: `docker compose ps`
3. Test database connection: `python3 test_connectivity.py`
4. Check relay server is up: `curl https://web-production-3d53a.up.railway.app/`
5. Verify environment variables loaded: `env | grep DATABASE_URL`

### If Block 3 MCP Verification Fails
**Impact**: Low - MCP tools are nice-to-have, not critical

**Options**:
- Document issue and continue to Phase 2
- Use direct database access instead of MCP
- File issue for later investigation

---

## Success Metrics

### System is Operational When:
- ✅ All import errors resolved
- ✅ Client starts without errors
- ✅ Client connects to WebSocket relay
- ✅ Session manager loads with Postgres backend
- ✅ Webhooks are received and processed
- ✅ Data persists to all database tables
- ✅ End-to-end test passes completely
- ✅ Can query data from database

### Ready for Phase 2 When:
- ✅ All above success metrics met
- ✅ No blocking issues identified
- ✅ Documentation updated
- ✅ Test framework validated

---

## After Completion

Once all tasks complete:

1. **Commit Progress**:
```bash
git add .
git commit -m "fix: resolve Python import issues in client package

- Convert all relative imports to absolute imports
- Add __init__.py files for proper package structure
- Verify end-to-end webhook flow working
- All Phase 1 validation tests passing"
```

2. **Clean Up Test Data**:
```bash
# Optional: Remove test sessions
docker compose exec -T postgres psql -U webhook_user -d ai_webhook -c "DELETE FROM sessions WHERE id LIKE 'e2e_test_%';"
```

3. **Proceed to Phase 2**:
- Review TASK_ROADMAP.md Phase 2 tasks
- Choose execution strategy (sequential vs parallel)
- Begin with highest priority task

---

## Questions?

If you encounter any issues during execution:

1. Check the specific task's "If Fails" section
2. Review PHASE1_VALIDATION_RESULTS.md for context
3. Check client.log for error messages
4. Run test_connectivity.py to verify database
5. Ask for help with specific error messages

---

## Notes

- Tasks 1-5 are straightforward code changes
- Task 6-8 are validation - might reveal new issues
- Tasks 9-11 are manual and can be deferred
- Task 12 is documentation cleanup

**Estimated total time**: 2-3 hours
**Critical path**: Tasks 1-8 (2 hours)
**Optional**: Tasks 9-11 (can be done later)
