# Synchronous Webhook Mode - Design Document

**Feature Branch**: `feature/004-synchronous-webhook-mode`
**Goal**: Enable LLMs to receive task results immediately in webhook response
**Estimated Time**: 2-3 hours

---

## Problem Statement

**Current MVP (Async)**:
- LLM sends webhook → Gets "received" response
- Task executes locally → Results stored in DB
- User manually checks http://localhost:5001
- **LLM never sees actual results**

**Impact on UX**:
- Breaks conversational flow
- LLM can't help with follow-up questions
- User must context-switch to browser
- Poor mobile experience

**Example Bad Flow**:
```
User: "What's my git status?"
LLM: "I triggered the command. Check http://localhost:5001"
User: [Opens browser, sees "2 files changed"]
User: "It says 2 files changed. Can you help me commit?"
LLM: "I don't know what changed since I didn't see the results"
```

---

## Proposed Solution: Synchronous Mode

Add optional `sync: true` parameter to webhook requests.

**When sync=true**:
1. Relay server receives webhook
2. Broadcasts to client (as normal)
3. **Waits** for client to send results back
4. Returns results to LLM in HTTP response
5. LLM sees actual output and continues conversation

**When sync=false or omitted** (backward compatible):
- Works exactly as MVP does now
- Returns immediately with "received" status

---

## Architecture

### Current Flow (Async)
```
LLM → POST /webhook → Relay Server → WebSocket → Client → Task Executor → SQLite
                           ↓
                    {"status": "received"}
```

### New Flow (Sync)
```
LLM → POST /webhook (sync=true)
         ↓
    Relay Server
         ↓ WebSocket (broadcast task)
    Client receives task
         ↓
    Task Executor
         ↓
    WebSocket (send results back)
         ↓
    Relay Server (collect results)
         ↓
    Return to LLM with actual output
         ↑
LLM sees: {"status": "completed", "output": {...}}
```

---

## Implementation Plan

### 1. Protocol Design

**Request Format** (LLM → Relay):
```json
{
  "type": "task_command",
  "sync": true,  // NEW: optional, default false
  "data": {
    "task_id": "git_status_001",
    "action_type": "git",
    "params": {
      "command": ["git", "status"],
      "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
    }
  }
}
```

**WebSocket Message** (Relay → Client):
```json
{
  "type": "webhook",
  "sync": true,  // NEW: tells client to send results back
  "event": "task_command",
  "payload": {
    "type": "task_command",
    "data": {
      "task_id": "git_status_001",
      "action_type": "git",
      "params": {...}
    }
  }
}
```

**WebSocket Response** (Client → Relay):
```json
{
  "type": "task_result",
  "task_id": "git_status_001",
  "status": "completed",
  "output": {
    "success": true,
    "stdout": "On branch main\nnothing to commit, working tree clean\n",
    "stderr": "",
    "returncode": 0
  }
}
```

**HTTP Response** (Relay → LLM):
```json
{
  "status": "completed",
  "task_id": "git_status_001",
  "output": {
    "success": true,
    "stdout": "On branch main\nnothing to commit, working tree clean\n",
    "stderr": "",
    "returncode": 0
  },
  "execution_time_ms": 234
}
```

---

## File Changes

### 1. Relay Server (`app.py`)

**Current webhook handler** (~line 99-159):
```python
@app.post("/webhook")
async def webhook_endpoint(request: Request):
    # Validate, broadcast to clients
    return {"status": "received", "clients_notified": len(connected_clients)}
```

**New webhook handler**:
```python
@app.post("/webhook")
async def webhook_endpoint(request: Request):
    payload = await request.json()
    sync_mode = payload.get("sync", False)

    if sync_mode:
        # Create result future
        task_id = payload["data"]["task_id"]
        result_future = asyncio.Future()
        pending_tasks[task_id] = result_future

        # Broadcast with sync=true
        message = {
            "type": "webhook",
            "sync": True,
            "event": payload.get("type"),
            "payload": payload
        }
        await broadcast_message(message)

        # Wait for result (max 30 seconds)
        try:
            result = await asyncio.wait_for(result_future, timeout=30.0)
            return result
        except asyncio.TimeoutError:
            del pending_tasks[task_id]
            return {
                "status": "timeout",
                "task_id": task_id,
                "error": "Task execution exceeded 30 second timeout"
            }
    else:
        # Original async behavior
        await broadcast_message({"type": "webhook", ...})
        return {"status": "received", ...}
```

**New WebSocket message handler** (handle task results):
```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # ... existing code ...

    async for message in websocket.iter_text():
        data = json.loads(message)

        if data.get("type") == "task_result":
            # Client sending results back
            task_id = data.get("task_id")
            if task_id in pending_tasks:
                pending_tasks[task_id].set_result(data)
                del pending_tasks[task_id]
        elif data.get("type") == "ping":
            # ... existing ping handler ...
```

**New global state**:
```python
# At top of file
pending_tasks = {}  # task_id -> asyncio.Future
```

### 2. Client (`client/client.py`)

**Current task handler** (~line 31-64):
```python
def handle_webhook(data: dict):
    # Execute task, store in DB
    # No response sent back
```

**New task handler**:
```python
def handle_webhook(data: dict, sync_mode: bool = False):
    # Execute task
    result = task_executor.handle_task(task_data)

    # If sync mode, send result back via WebSocket
    if sync_mode:
        response = {
            "type": "task_result",
            "task_id": task_id,
            "status": result.get("status"),
            "output": result.get("output")
        }
        return response  # Will be sent by WebSocket handler

    # Async mode - no response needed
    return None
```

**WebSocket message handler** (~line 225):
```python
async def handle_message(message: str):
    data = json.loads(message)

    if data.get("type") == "webhook":
        sync_mode = data.get("sync", False)
        payload = data.get("payload", {})

        # Handle webhook (potentially get result)
        result = handle_webhook(payload, sync_mode=sync_mode)

        # If sync mode, send result back
        if sync_mode and result:
            await websocket.send(json.dumps(result))
```

---

## Testing Plan

### Test 1: Sync Mode Success
```bash
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "type": "task_command",
    "sync": true,
    "data": {
      "task_id": "git_status_sync_001",
      "action_type": "git",
      "params": {
        "command": ["git", "status"],
        "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
      }
    }
  }'
```

**Expected**:
- Wait 1-3 seconds
- Return actual git status in response
- Task also stored in DB (both paths work)

### Test 2: Sync Mode Timeout
```bash
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "type": "task_command",
    "sync": true,
    "data": {
      "task_id": "sleep_sync_001",
      "action_type": "shell",
      "params": {
        "command": "sleep 35"
      }
    }
  }'
```

**Expected**:
- Wait 30 seconds
- Return timeout error
- Task may still complete locally (async fallback)

### Test 3: Async Mode Still Works
```bash
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @examples/git_status.json
```

**Expected**:
- Immediate response: `{"status": "received"}`
- Task executes normally
- Backward compatible

### Test 4: LLM Integration
Update LLM instructions to use `"sync": true` and test:

**User**: "What's my git status?"
**LLM**: Sends sync webhook
**LLM Response**: "You're on branch main with no uncommitted changes."

---

## Edge Cases

### 1. Client Not Connected
**Scenario**: Sync webhook sent, but no client connected
**Solution**: Timeout after 30 seconds, return error

### 2. Multiple Clients
**Scenario**: 2 clients connected, which one responds?
**Solution**: First response wins, ignore others

### 3. Client Crashes During Task
**Scenario**: Task starts, client crashes before sending result
**Solution**: Timeout handles it, return error to LLM

### 4. Duplicate Task IDs
**Scenario**: Two sync requests with same task_id
**Solution**: Last request overwrites pending_tasks entry

---

## LLM Instruction Updates

### LLM_SYSTEM_PROMPT.md Changes

Add section:
```markdown
## Synchronous vs Asynchronous Mode

**Synchronous Mode (Recommended)**:
Use `"sync": true` to get immediate results in the response.

{
  "type": "task_command",
  "sync": true,  // <-- Add this
  "data": {...}
}

Response will contain actual task output:
{
  "status": "completed",
  "output": {
    "stdout": "On branch main\n...",
    "returncode": 0
  }
}

**Asynchronous Mode**:
Omit `sync` or set to `false` for fire-and-forget.
Results available at http://localhost:5001.

**When to use each**:
- Sync: Conversational flows where you need results (90% of cases)
- Async: Long-running tasks (>30 seconds) or fire-and-forget
```

---

## Backward Compatibility

✅ **Fully backward compatible**:
- `sync` parameter is optional (defaults to `false`)
- Existing webhooks work unchanged
- Existing LLM instructions work unchanged
- Async mode preserved for long-running tasks

---

## Performance Considerations

**Timeout**: 30 seconds
- Most git/shell commands: <5 seconds
- Acceptable for conversational UX
- Prevents HTTP connection hanging

**Memory**: Minimal
- Only stores pending futures (1 per sync request)
- Auto-cleanup on completion/timeout
- No memory leaks

**Concurrency**: Supported
- Multiple sync requests can be in-flight
- Each tracked independently by task_id

---

## Success Criteria

✅ **Feature complete when**:
1. Sync mode returns actual task output
2. Timeout handling works (30s max)
3. Async mode still works (backward compatible)
4. LLM can see results and continue conversation
5. All tests pass
6. Documentation updated

---

## Rollout Plan

1. **Implement** on feature branch
2. **Test** locally (manual + automated)
3. **Deploy** to Railway (sync mode available)
4. **Update** LLM instructions (opt-in to sync)
5. **Validate** with mobile LLM
6. **Merge** to main

---

## Alternative Considered: Callback URL

**Rejected because**:
- Requires LLM to expose public endpoint (complex)
- Most LLMs can't receive HTTP callbacks
- Polling adds complexity
- Synchronous wait is simpler

---

## Timeline Estimate

| Task | Time |
|------|------|
| Protocol design | 30 min (done) |
| Relay server changes | 1 hour |
| Client changes | 45 min |
| Testing | 30 min |
| Documentation | 30 min |
| **Total** | **~3 hours** |

---

**Created**: 2025-11-17
**Status**: Design Complete, Ready for Implementation
**Branch**: feature/004-synchronous-webhook-mode
