# MVP Test Plan - Voice LLM to Local Action System

**Purpose**: Prove the complete MVP works end-to-end
**Duration**: 15 minutes
**Status**: Ready to Execute

---

## Overview

This test plan validates all components of the MVP:
1. ✅ SQLite backend stores tasks
2. ✅ Task executor runs git/shell commands
3. ✅ Results viewer displays output
4. ✅ Webhook endpoint receives commands
5. ✅ End-to-end flow from webhook → execution → results

---

## Prerequisites

Before starting:
```bash
# 1. Ensure you're on main branch with latest merge
git branch
# Should show: * main

# 2. Verify all MVP files present
ls -la start_mvp.sh stop_mvp.sh test_mvp.py
# All should exist

# 3. Check environment configuration
cat .env | grep -E 'API_KEY|STORAGE_BACKEND|SQLITE_PATH'
# Should show your API key and STORAGE_BACKEND=sqlite
```

If `.env` doesn't have `STORAGE_BACKEND=sqlite`, update it:
```bash
# Open .env and change:
STORAGE_BACKEND=sqlite
SQLITE_PATH=./tasks.db
```

---

## Test 1: Automated Test Suite (2 minutes)

**Purpose**: Verify all components pass unit tests

```bash
# Run comprehensive test suite
python3 tests/test_mvp.py
```

**Expected Output**:
```
============================================================
MVP COMPREHENSIVE TEST SUITE
============================================================
Working Directory: /Users/tim/gameplan.ai/ai-webhook
Webhook URL: https://web-production-3d53a.up.railway.app/webhook
API Key: Set
============================================================

============================================================
TEST: SQLite Backend
============================================================
✅ Task created
✅ Task retrieved
✅ Task updated
✅ Recent tasks retrieved
✅ SQLite Backend: PASSED

============================================================
TEST: Task Executor
============================================================
✅ Git command executed
✅ Shell command executed
✅ Error handling works
✅ Task Executor: PASSED

============================================================
TEST: Webhook Endpoint Connectivity
============================================================
✅ Webhook endpoint reachable
✅ Webhook Endpoint: PASSED

============================================================
TEST: File Structure
============================================================
✅ client/storage/sqlite_backend.py
✅ client/task_executor.py
✅ client/results_server.py
[... all files listed ...]
✅ File Structure: PASSED

============================================================
TEST: Environment Configuration
============================================================
✅ RELAY_SERVER_URL defined in .env.example
✅ API_KEY defined in .env.example
✅ STORAGE_BACKEND defined in .env.example
✅ SQLITE_PATH defined in .env.example
✅ Environment Config: PASSED

============================================================
TEST SUMMARY
============================================================
SQLite Backend.......................... ✅ PASSED
Task Executor........................... ✅ PASSED
Webhook Endpoint........................ ✅ PASSED
File Structure.......................... ✅ PASSED
Environment Config...................... ✅ PASSED
============================================================
Results: 5/5 tests passed
============================================================

🎉 ALL TESTS PASSED - MVP IS READY!
```

**✅ PASS CRITERIA**: All 5 tests show ✅ PASSED

---

## Test 2: Start MVP Services (1 minute)

**Purpose**: Verify startup script launches all services

```bash
# Start MVP
./start_mvp.sh
```

**Expected Output**:
```
========================================
Starting MVP: Voice LLM → Local Actions
========================================

✅ Configuration loaded

📦 Checking dependencies...
✅ All dependencies present

🚀 Starting webhook client...
   PID: 12345
   Logs: client_output.log

🌐 Starting results viewer...
   PID: 12346
   URL: http://localhost:5001
   Logs: results_server.log

========================================
✅ MVP is running!
========================================

📊 Services:
   • Webhook Client: PID 12345
   • Results Viewer: http://localhost:5001
```

**Verify services running**:
```bash
# Check processes
ps aux | grep -E 'client.py|results_server.py'
```

**Expected**: Should see 2 Python processes running

**✅ PASS CRITERIA**:
- No errors during startup
- Both PIDs shown
- Processes are running

---

## Test 3: Verify Results Viewer (1 minute)

**Purpose**: Confirm web UI is accessible

```bash
# Open results viewer
open http://localhost:5001

# Or use curl
curl -s http://localhost:5001 | head -20
```

**Expected in browser**:
- Clean web interface with header "📋 Task Results Viewer"
- Empty state message: "No tasks yet"
- Mobile-responsive design

**Expected from curl**:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Results Viewer</title>
```

**✅ PASS CRITERIA**: Web page loads successfully (status 200)

---

## Test 4: Send Test Webhook - Git Status (2 minutes)

**Purpose**: Validate end-to-end flow (webhook → execution → storage)

```bash
# Load API key from environment
source .env

# Send git status webhook
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @examples/git_status.json
```

**Expected Response**:
```json
{
  "status": "received",
  "event": null,
  "delivery_id": null,
  "clients_notified": 1
}
```

**Check client logs**:
```bash
tail -20 client_output.log
```

**Expected in logs**:
```
📬 Received task command
   Task ID: git_status_001
   Action: git
✅ Task completed: git_status_001
   Output: On branch main...
```

**✅ PASS CRITERIA**:
- HTTP 200 response
- `clients_notified: 1`
- Task appears in client logs as completed

---

## Test 5: Verify Task in Results Viewer (1 minute)

**Purpose**: Confirm task results are displayed

**Refresh results viewer**:
```bash
open http://localhost:5001
```

**Expected**:
- Task card showing `git_status_001`
- Status badge: **COMPLETED** (green)
- Action type: `git`
- Output showing git status results

**Or check via API**:
```bash
curl http://localhost:5001/api/task/git_status_001 | jq
```

**Expected JSON**:
```json
{
  "id": "git_status_001",
  "command": "git",
  "status": "completed",
  "input_data": {
    "action_type": "git",
    "params": {
      "command": ["git", "status"],
      "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
    }
  },
  "output_data": {
    "success": true,
    "stdout": "On branch main\n...",
    "stderr": "",
    "returncode": 0
  },
  "error_message": null,
  "created_at": "2025-01-17 ...",
  "completed_at": "2025-01-17 ..."
}
```

**✅ PASS CRITERIA**:
- Task visible in web UI
- Status is "completed"
- Output shows git status results

---

## Test 6: Send Multiple Tasks (3 minutes)

**Purpose**: Test different action types and parallel execution

```bash
# Load API key
source .env

# Test 1: Git log
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @examples/git_log.json

# Wait 2 seconds
sleep 2

# Test 2: Shell ls
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @examples/shell_ls.json

# Wait 2 seconds
sleep 2

# Test 3: Shell echo
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @examples/shell_echo.json
```

**Check results viewer**:
```bash
open http://localhost:5001
```

**Expected**:
- 4 total tasks visible (including git_status_001 from earlier)
- All showing "completed" status
- Each with different outputs:
  - `git_log_001`: Recent commit history
  - `shell_ls_001`: Directory listing
  - `shell_echo_001`: "Hello from voice LLM!"

**✅ PASS CRITERIA**: All 4 tasks completed successfully

---

## Test 7: Test Error Handling (2 minutes)

**Purpose**: Verify system handles invalid requests gracefully

```bash
source .env

# Send task with invalid directory
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "type": "task_command",
    "data": {
      "task_id": "error_test_001",
      "action_type": "git",
      "params": {
        "command": ["git", "status"],
        "working_dir": "/nonexistent/directory"
      }
    }
  }'
```

**Check results**:
```bash
curl http://localhost:5001/api/task/error_test_001 | jq .status
```

**Expected**: `"failed"`

**Check error message**:
```bash
curl http://localhost:5001/api/task/error_test_001 | jq .error_message
```

**Expected**: Contains "does not exist"

**✅ PASS CRITERIA**:
- Task status is "failed"
- Error message explains the issue
- System didn't crash

---

## Test 8: Database Verification (2 minutes)

**Purpose**: Confirm SQLite database stores data correctly

```bash
# Check database exists
ls -lh tasks.db

# Query database directly
sqlite3 tasks.db "SELECT id, command, status FROM tasks ORDER BY created_at DESC LIMIT 5;"
```

**Expected Output**:
```
error_test_001|git|failed
shell_echo_001|shell|completed
shell_ls_001|shell|completed
git_log_001|git|completed
git_status_001|git|completed
```

**Count total tasks**:
```bash
sqlite3 tasks.db "SELECT COUNT(*) FROM tasks;"
```

**Expected**: 5 (or more if you ran additional tests)

**✅ PASS CRITERIA**:
- Database file exists
- Tasks are stored with correct status
- Data persists across queries

---

## Test 9: Stop and Restart (2 minutes)

**Purpose**: Verify graceful shutdown and data persistence

```bash
# Stop MVP
./stop_mvp.sh
```

**Expected Output**:
```
========================================
Stopping MVP Services
========================================

🛑 Stopping webhook client (PID: 12345)...
✅ Webhook client stopped
🛑 Stopping results viewer (PID: 12346)...
✅ Results viewer stopped

========================================
✅ All services stopped
========================================
```

**Verify processes stopped**:
```bash
ps aux | grep -E 'client.py|results_server.py'
# Should show no results (except grep itself)
```

**Restart and verify data persists**:
```bash
# Start again
./start_mvp.sh

# Wait 3 seconds
sleep 3

# Check results viewer
open http://localhost:5001
```

**Expected**: All 5 tasks from previous tests are still visible

**✅ PASS CRITERIA**:
- Clean shutdown with no errors
- Processes terminated
- Data persists after restart
- All previous tasks visible

---

## Test 10: End-to-End Performance (3 minutes)

**Purpose**: Measure typical task execution time

```bash
source .env

# Time a git status command
time curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "type": "task_command",
    "data": {
      "task_id": "perf_test_001",
      "action_type": "git",
      "params": {
        "command": ["git", "status"],
        "working_dir": "'"$PWD"'"
      }
    }
  }'
```

**Expected**:
```
real    0m0.XXXs
user    0m0.XXXs
sys     0m0.XXXs
```

**Check task completion time**:
```bash
sqlite3 tasks.db "SELECT id, created_at, completed_at FROM tasks WHERE id='perf_test_001';"
```

**Calculate duration** (difference between created_at and completed_at)

**✅ PASS CRITERIA**:
- Webhook response < 1 second
- Task execution < 5 seconds
- Total end-to-end < 10 seconds

---

## Summary Checklist

After completing all tests, verify:

- [ ] **Test 1**: All automated tests passed (5/5)
- [ ] **Test 2**: MVP services started successfully
- [ ] **Test 3**: Results viewer accessible at :5001
- [ ] **Test 4**: Git status webhook executed
- [ ] **Test 5**: Task visible in results viewer
- [ ] **Test 6**: Multiple tasks executed (4 total)
- [ ] **Test 7**: Error handling works (failed task)
- [ ] **Test 8**: SQLite database stores data
- [ ] **Test 9**: Stop/restart works, data persists
- [ ] **Test 10**: Performance acceptable (<10s end-to-end)

---

## Success Criteria

**MVP is validated when**:
- ✅ All 10 tests pass
- ✅ Can send webhook from command line
- ✅ Tasks execute locally
- ✅ Results appear in viewer
- ✅ Data persists in SQLite
- ✅ Clean startup/shutdown

---

## Next Steps After Testing

### If All Tests Pass:

1. **Mobile LLM Setup** (15 minutes)
   - Follow `docs/CLAUDE_SETUP.md` for Claude Projects setup
   - Or `docs/CHATGPT_SETUP.md` for ChatGPT custom instructions
   - Test from mobile device

2. **Daily Usage** (1 week)
   - Use for real tasks: checking git status, viewing commits, etc.
   - Track usage: How many times? What actions? Was it useful?

3. **Validation Decision** (End of week)
   - If used 10+ times: Build Phase 2 (real-time notifications)
   - If used 3-5 times: Maybe useful, iterate
   - If used <3 times: Probably not worth it, archive

### If Tests Fail:

Check logs and troubleshoot:
```bash
# Client logs
tail -f client_output.log

# Results server logs
tail -f results_server.log

# Webhook logs
ls -la webhook_logs/

# Database state
sqlite3 tasks.db "SELECT * FROM tasks;"
```

Common issues:
- `.env` not configured with `STORAGE_BACKEND=sqlite`
- API_KEY not set or incorrect
- Webhook client not running
- Port 5001 already in use

---

## Test Environment Info

**System**: macOS (Darwin 24.6.0)
**Python**: 3.7+
**Dependencies**: websockets, python-dotenv, flask
**Database**: SQLite 3
**Relay Server**: https://web-production-3d53a.up.railway.app

---

## Test Results Log

Document your test run:

**Date**: _____________
**Tester**: _____________
**Duration**: _____________

**Results**:
- Test 1 (Automated): ☐ Pass ☐ Fail
- Test 2 (Startup): ☐ Pass ☐ Fail
- Test 3 (Viewer): ☐ Pass ☐ Fail
- Test 4 (Git Status): ☐ Pass ☐ Fail
- Test 5 (Results): ☐ Pass ☐ Fail
- Test 6 (Multiple): ☐ Pass ☐ Fail
- Test 7 (Errors): ☐ Pass ☐ Fail
- Test 8 (Database): ☐ Pass ☐ Fail
- Test 9 (Restart): ☐ Pass ☐ Fail
- Test 10 (Performance): ☐ Pass ☐ Fail

**Overall**: ☐ PASS ☐ FAIL

**Notes**:
_______________________________________________________
_______________________________________________________
_______________________________________________________

---

**Created**: 2025-01-17
**Last Updated**: 2025-01-17
**Version**: 1.0
**Status**: Ready for Execution
