# Execution Plan - Collaborative Sessions Implementation

**Date**: 2025-11-15
**Current Branch**: feature/002-collaborative-sessions
**Goal**: Complete Phase 1 validation and Phase 2 foundation tasks

---

## Current State Assessment

### ✅ What's Already Complete

1. **Infrastructure**
   - Postgres 15 running in Docker (port 5433)
   - Database schema fully initialized (6 tables)
   - Connection pooling implemented
   - Full-text search indexes created
   - Sample agent data loaded

2. **Backend Implementation**
   - `postgres_backend.py` fully implemented (22KB)
   - Backend abstraction in `session_manager.py`
   - Environment configured: `STORAGE_BACKEND=postgres`
   - Tests passing (`test_postgres_backend.py`)

3. **Configuration**
   - MCP tools configured (Postgres, GitHub, Filesystem)
   - `.env` file complete with all settings
   - Docker Compose setup with health checks
   - Relay server deployed and operational

4. **Data**
   - 3 test sessions already in Postgres
   - No JSON files to migrate (clean slate)
   - Agents table pre-populated

### ⏭ What Remains

**Phase 1**: Validation and testing (2 hours)
**Phase 2**: Tools and documentation (5 hours if sequential, 2 hours if parallel)

---

## Phase 1: Infrastructure Validation (IMMEDIATE)

### Task 1.1: Test MCP Tools Connectivity (30 min)

**Objective**: Verify MCP tools can access database and perform operations

**Steps**:
1. List available MCP tools
2. Test Postgres MCP tool:
   - Query active sessions
   - Insert a test session
   - Search conversations (full-text)
   - Claim a task atomically
3. Test GitHub MCP tool:
   - List repositories
   - Get current repo info
4. Test Filesystem MCP tool:
   - Read project files
   - List directories

**Success Criteria**:
- [ ] Can query database using natural language through MCP
- [ ] Can insert/update/delete via MCP
- [ ] All 3 MCP tools respond correctly
- [ ] No connection errors

**Potential Concerns**:
- ⚠️ MCP Postgres tool might need DATABASE_URL in different format
- ⚠️ GitHub token might not be set (`GITHUB_TOKEN` env var)
- ⚠️ MCP tools might not be installed/configured in Claude Code

**Mitigation**:
- Check MCP tool configuration in `mcp-config.json`
- Verify environment variables are accessible to MCP servers
- Test with direct SQL queries if MCP fails, to isolate issue

---

### Task 1.2: End-to-End Webhook Testing (1 hour)

**Objective**: Verify full webhook → session → Postgres flow works

**Steps**:
1. Start client with Postgres backend
2. Send test webhooks for each command type:
   - `create_session`
   - `conversation_chunk`
   - `store_memory`
   - `delegate_task`
   - `add_artifact`
   - `batch` command
3. Verify data persists in Postgres
4. Test session retrieval after client restart
5. Test error handling (invalid session, missing fields)

**Success Criteria**:
- [ ] All command types work correctly
- [ ] Data persists in correct tables
- [ ] Foreign key relationships maintained
- [ ] Timestamps auto-update
- [ ] Client can restart and resume sessions
- [ ] Error messages are clear and helpful

**Potential Concerns**:
- ⚠️ Client might not connect to relay server
- ⚠️ Database connection might fail with actual load
- ⚠️ JSON serialization issues with complex data
- ⚠️ Race conditions if multiple webhooks arrive simultaneously
- ⚠️ Large conversation chunks might exceed limits
- ⚠️ Webhook signature verification might block test payloads

**Mitigation**:
- Use curl to test each endpoint independently first
- Add verbose logging to track data flow
- Test with both small and large payloads
- Use API key authentication for test webhooks
- Monitor Postgres logs during testing

**Test Payload Examples Needed**:
```json
// 1. Create session
{
  "type": "collaborative_session_command",
  "command": "create_session",
  "session_id": "test_001",
  "data": {
    "title": "Test Session",
    "participants": ["claude", "user"]
  }
}

// 2. Store conversation
{
  "type": "collaborative_session_command",
  "command": "conversation_chunk",
  "session_id": "test_001",
  "data": {
    "chunk_id": "chunk_001",
    "content": "Large conversation transcript...",
    "format": "dialogue"
  }
}

// 3. Store memory
{
  "type": "collaborative_session_command",
  "command": "store_memory",
  "session_id": "test_001",
  "data": {
    "type": "idea",
    "key": "carbon_tracking",
    "content": {"description": "Track carbon footprint", "priority": "high"},
    "tags": ["sustainability", "feature"]
  }
}

// 4. Delegate task
{
  "type": "collaborative_session_command",
  "command": "delegate_task",
  "session_id": "test_001",
  "data": {
    "task_id": "task_001",
    "agent_name": "claude_code",
    "task_type": "code",
    "description": "Implement carbon tracking API",
    "priority": 1
  }
}

// 5. Batch commands
{
  "type": "collaborative_session_command",
  "command": "batch",
  "session_id": "test_001",
  "data": {
    "commands": [
      {"command": "store_memory", "data": {...}},
      {"command": "delegate_task", "data": {...}}
    ]
  }
}
```

---

## Phase 2: Tools & Documentation (HIGH PRIORITY)

### Overview

These three tasks are **completely independent** and can run in parallel:
1. CLI Tool (creates `session_cli.py`)
2. LLM Guide (creates `docs/LLM_SESSION_API.md`)
3. Webhook Examples (creates `examples/*.json`)

**No file conflicts** - Safe for parallel execution

---

### Task 2.1: Session CLI Tool (2 hours)

**Objective**: Build command-line tool for managing sessions

**Files to Create**:
- `session_cli.py` or `client/session_cli.py`

**Dependencies to Install**:
```bash
pip install rich click
```

**Commands to Implement**:
```bash
# Session management
session-cli create <id> [--title] [--participants]
session-cli list [--status active|paused|completed] [--limit N]
session-cli show <id>
session-cli summary <id>
session-cli pause <id>
session-cli resume <id>
session-cli complete <id>
session-cli delete <id>

# Query operations
session-cli search-conversations <query>
session-cli search-memories <query> [--type] [--tags]
session-cli list-tasks [--status] [--agent]
session-cli list-artifacts [--type]

# Export
session-cli export <id> [--format json|markdown]
```

**Technical Implementation**:
1. Use Click for CLI framework
2. Use Rich for colored output and tables
3. Connect to Postgres backend via `session_manager`
4. Support both JSON and Postgres backends
5. Add input validation
6. Add confirmation prompts for destructive operations

**Success Criteria**:
- [ ] All commands work correctly
- [ ] Colored, user-friendly output
- [ ] Works with both backends
- [ ] Handles errors gracefully
- [ ] Help text is comprehensive
- [ ] Can pipe output for scripting

**Potential Concerns**:
- ⚠️ CLI dependencies might conflict with existing packages
- ⚠️ Output formatting might break with large datasets
- ⚠️ Direct database access might bypass session_manager logic
- ⚠️ Delete operation might leave orphaned records
- ⚠️ Large session summaries might be slow to generate

**Mitigation**:
- Use virtual environment for isolation
- Add pagination for large result sets
- Use session_manager methods instead of direct DB access
- Implement cascade delete or clear warnings
- Add --limit flags and lazy loading

**Testing Checklist**:
- [ ] Create session with minimal args
- [ ] Create session with all optional args
- [ ] List sessions with various filters
- [ ] Show non-existent session (error handling)
- [ ] Delete session with confirmation
- [ ] Search with complex queries
- [ ] Export in both formats
- [ ] Test with empty database

---

### Task 2.2: LLM Session API Guide (2 hours)

**Objective**: Comprehensive documentation for LLMs using the API

**Files to Create**:
- `docs/LLM_SESSION_API.md` (main guide)
- `docs/CHATGPT_INTEGRATION.md` (ChatGPT-specific)
- `docs/CLAUDE_MOBILE_INTEGRATION.md` (Claude mobile-specific)

**Content Outline**:

#### `LLM_SESSION_API.md`
1. **Introduction**
   - What are collaborative sessions
   - Use cases and workflows
   - Architecture overview

2. **Getting Started**
   - Prerequisites
   - Webhook endpoint URL
   - Authentication (API key)
   - Basic example

3. **Command Reference**
   - `create_session` - Full spec with all fields
   - `conversation_chunk` - How to batch large conversations
   - `store_memory` - All memory types with examples
   - `delegate_task` - Task delegation with agent selection
   - `add_artifact` - Artifact creation
   - `batch` - Combining multiple commands
   - `pause_session`, `resume_session`, `complete_session`
   - `get_session_summary` - Retrieving session state

4. **Data Models**
   - Session structure
   - Memory types (idea, decision, question, etc.)
   - Task structure
   - Artifact types

5. **Best Practices**
   - When to create chunks vs memories
   - How to structure task delegation
   - Naming conventions for IDs
   - Error handling
   - Performance tips

6. **Common Workflows**
   - Voice conversation with background research
   - Collaborative design session
   - Code review with automated fixes
   - Product planning with documentation

7. **Error Handling**
   - Common errors and solutions
   - Validation rules
   - Retry strategies

8. **Response Format**
   - Success responses
   - Error responses
   - Async vs sync feedback

#### `CHATGPT_INTEGRATION.md`
1. **Setup Instructions**
   - Using GPT actions
   - Custom webhook configuration
   - Authentication setup

2. **Example Prompts**
   - System prompt for collaborative sessions
   - User prompts for common tasks

3. **Limitations**
   - What ChatGPT can/can't do
   - Workarounds

#### `CLAUDE_MOBILE_INTEGRATION.md`
1. **Setup Instructions**
   - Using Claude mobile app
   - Webhook integration via shortcuts

2. **Voice Mode Integration**
   - How to trigger during voice conversations
   - Example voice commands

3. **Example Conversations**
   - Full example dialogues

**Success Criteria**:
- [ ] LLM can understand how to use API from docs alone
- [ ] All command formats documented with examples
- [ ] Copy-paste examples work without modification
- [ ] Covers all use cases from original vision
- [ ] Clear, beginner-friendly language
- [ ] Code examples are tested and valid

**Potential Concerns**:
- ⚠️ Documentation might become outdated as code evolves
- ⚠️ Examples might contain invalid JSON
- ⚠️ Might miss edge cases or error scenarios
- ⚠️ Platform-specific integrations might change
- ⚠️ Security considerations might be overlooked

**Mitigation**:
- Include version numbers in docs
- Validate all JSON examples with a linter
- Add comprehensive error examples
- Link to official platform docs
- Add security best practices section
- Include disclaimer about API stability

**Quality Checklist**:
- [ ] All JSON examples are valid
- [ ] All URLs are correct
- [ ] All commands tested
- [ ] No typos or grammar errors
- [ ] Markdown renders correctly
- [ ] Links work
- [ ] Code blocks have syntax highlighting

---

### Task 2.3: Webhook Payload Examples (1 hour)

**Objective**: Ready-to-use example payloads for testing

**Files to Create**:
```
examples/
├── README.md                    # How to use examples
├── create_session.json          # Session creation
├── conversation_batch.json      # Large conversation
├── store_memory_idea.json       # Idea memory
├── store_memory_decision.json   # Decision memory
├── store_memory_question.json   # Question memory
├── delegate_task_code.json      # Code task
├── delegate_task_research.json  # Research task
├── add_artifact_code.json       # Code artifact
├── add_artifact_document.json   # Document artifact
├── batch_workflow.json          # Multiple commands
├── complete_workflow.json       # Full session lifecycle
├── error_examples.json          # Invalid payloads
└── test_all.sh                  # Script to test all examples
```

**Content for Each File**:
1. Complete, valid JSON payload
2. Comments explaining each field
3. Realistic example data
4. Curl command to test it

**`test_all.sh` Script**:
```bash
#!/bin/bash
# Test all webhook examples

RELAY_URL="https://web-production-3d53a.up.railway.app/webhook"
API_KEY="your-api-key-here"

echo "Testing webhook examples..."

for file in *.json; do
  echo ""
  echo "Testing: $file"
  curl -X POST "$RELAY_URL" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d @"$file" \
    --silent | jq '.'
done
```

**Success Criteria**:
- [ ] All JSON files are valid
- [ ] Examples cover all main use cases
- [ ] Curl commands work without modification
- [ ] Includes both success and error cases
- [ ] README explains how to customize
- [ ] Test script runs successfully

**Potential Concerns**:
- ⚠️ Examples might contain sensitive data (API keys, etc.)
- ⚠️ JSON might become invalid as schema changes
- ⚠️ Test script might need environment-specific URLs
- ⚠️ Large payloads might be too big for git
- ⚠️ Examples might not cover edge cases

**Mitigation**:
- Use placeholder values (your-api-key-here)
- Add JSON schema validation
- Use environment variables in test script
- Keep examples reasonably sized
- Add comprehensive error examples

---

## Execution Strategy

### Option A: Sequential Execution (5 hours total)
```
Phase 1 Validation (2 hours)
  └─> Task 2.1: CLI Tool (2 hours)
      └─> Task 2.2: LLM Guide (2 hours)
          └─> Task 2.3: Examples (1 hour)
```

**Pros**: Simple, no coordination needed
**Cons**: Slower, 5 hours total for Phase 2

---

### Option B: Parallel Execution (2 hours max)
```
Phase 1 Validation (2 hours)
  └─> ┌─ Task 2.1: CLI Tool (2 hours)        [Claude Code Agent 1]
      ├─ Task 2.2: LLM Guide (2 hours)        [Claude Code Agent 2]
      └─ Task 2.3: Examples (1 hour)          [Claude Code Agent 3]
```

**Pros**: 60% faster, completes all of Phase 2 in 2 hours
**Cons**: Requires coordination, 3 terminal sessions

**Git Strategy for Parallel Execution**:
```bash
# Before starting
git add .
git commit -m "chore: ready for Phase 2 parallel execution"

# Create branches
git checkout -b feature/session-cli
git checkout feature/002-collaborative-sessions
git checkout -b feature/llm-guide
git checkout feature/002-collaborative-sessions
git checkout -b feature/webhook-examples

# Terminal 1
git checkout feature/session-cli
# Run Agent 1

# Terminal 2
git checkout feature/llm-guide
# Run Agent 2

# Terminal 3
git checkout feature/webhook-examples
# Run Agent 3

# After completion
git checkout feature/002-collaborative-sessions
git merge feature/session-cli
git merge feature/llm-guide
git merge feature/webhook-examples
```

---

## Risk Assessment

### HIGH RISK
1. **Database connection failures under load**
   - Impact: System unusable
   - Mitigation: Test with concurrent connections, add connection pooling limits
   - Detection: Monitor connection pool stats

2. **MCP tools not working**
   - Impact: Can't use database through Claude Code
   - Mitigation: Test early, have fallback to direct SQL
   - Detection: Run MCP test immediately

3. **Race conditions in task claiming**
   - Impact: Tasks assigned to multiple agents
   - Mitigation: Already using `FOR UPDATE SKIP LOCKED`
   - Detection: Test with concurrent task claims

### MEDIUM RISK
1. **Large payloads causing timeouts**
   - Impact: Some webhooks fail
   - Mitigation: Add chunking, test with large data
   - Detection: Monitor response times

2. **Documentation drift from implementation**
   - Impact: Examples don't work
   - Mitigation: Generate examples from actual tests
   - Detection: Automated testing of examples

3. **CLI tool performance with large datasets**
   - Impact: Slow user experience
   - Mitigation: Add pagination, lazy loading
   - Detection: Test with 1000+ sessions

### LOW RISK
1. **Merge conflicts in parallel execution**
   - Impact: Manual merge needed
   - Mitigation: Tasks touch different files
   - Detection: Git will flag conflicts

2. **Missing error cases in docs**
   - Impact: Users confused by errors
   - Mitigation: Comprehensive error documentation
   - Detection: User feedback

---

## Testing Strategy

### Phase 1 Testing
1. **MCP Tools Test**
   - Run queries through MCP
   - Verify results match direct SQL
   - Test error handling

2. **End-to-End Test**
   - Send all webhook types
   - Verify database state
   - Test client restart
   - Check error messages

### Phase 2 Testing
1. **CLI Tool Test**
   - Unit tests for each command
   - Integration tests with database
   - Error handling tests
   - Performance tests with large datasets

2. **Documentation Test**
   - Validate all JSON examples
   - Test all curl commands
   - Verify links work
   - Run through spell checker

3. **Examples Test**
   - Run `test_all.sh`
   - Verify all payloads accepted
   - Check database state after each
   - Test error examples fail correctly

---

## Success Metrics

### Phase 1 Complete When:
- [ ] All MCP tools tested and working
- [ ] End-to-end webhook flow verified
- [ ] Data persists correctly in Postgres
- [ ] No blocking issues identified
- [ ] Performance is acceptable

### Phase 2 Complete When:
- [ ] CLI tool works for all operations
- [ ] Documentation is comprehensive and accurate
- [ ] Examples all test successfully
- [ ] LLMs can use API from docs alone
- [ ] No critical concerns unresolved

---

## Timeline

### Conservative (Sequential)
- **Today**: Phase 1 validation (2 hours)
- **Tomorrow**: Tasks 2.1 + 2.2 (4 hours)
- **Day 3**: Task 2.3 + testing (2 hours)
- **Total**: 3 days, 8 hours

### Aggressive (Parallel)
- **Today Session 1**: Phase 1 validation (2 hours)
- **Today Session 2**: All Phase 2 tasks in parallel (2 hours)
- **Tomorrow**: Testing and refinement (1 hour)
- **Total**: 2 days, 5 hours

---

## Open Questions

1. **MCP Tools Configuration**
   - Are MCP servers already installed and running?
   - Do we need to configure DATABASE_URL for MCP differently?
   - Is GITHUB_TOKEN set for GitHub MCP?

2. **Client Deployment**
   - Should client auto-start on system boot?
   - How to handle client crashes and restarts?
   - Where should logs be stored?

3. **API Design**
   - Should we version the API (v1, v2)?
   - What's the rate limit for webhooks?
   - Should we add webhook retry logic?

4. **Error Handling**
   - What happens if database is down?
   - Should we queue webhooks when client offline?
   - How to handle malformed payloads?

5. **Security**
   - Should API keys have different permissions?
   - Do we need IP whitelisting?
   - Should we log all webhook payloads?

6. **Performance**
   - What's the expected load (webhooks/sec)?
   - Should we add caching?
   - Do we need Redis for task queue?

---

## Next Steps

1. **Review this plan** - Identify any missing concerns
2. **Choose execution strategy** - Sequential or parallel?
3. **Resolve open questions** - Get clarity before starting
4. **Execute Phase 1** - Validation and testing
5. **Execute Phase 2** - Tools and documentation
6. **Test everything** - Comprehensive verification
7. **Update roadmap** - Mark completed tasks
8. **Plan Phase 3** - Agent orchestration (the big one)

---

## Notes

- All timestamps are in UTC
- Database backups should be taken before major changes
- Git commits should be atomic and well-documented
- Each phase should be tested before moving to next
- Documentation should be updated as we go
