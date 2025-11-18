# AI Webhook System - LLM Instructions

**Version**: 1.0
**Last Updated**: 2025-11-18

You have access to a powerful webhook system that lets you execute commands on the user's local development machine and manage collaborative sessions with persistent memory.

---

## Quick Start

**Webhook Endpoint**: `https://web-production-3d53a.up.railway.app/webhook`
**API Key**: Check with user (they'll provide it)
**Method**: POST with JSON body

---

## Two Main Capabilities

### 1. Task Execution (Git & Shell Commands)
Execute commands on the user's local machine and get immediate results.

### 2. Collaborative Sessions (Memory & Knowledge Management)
Create sessions to store ideas, decisions, questions, and track learning across conversations.

---

## Task Execution

### Git Commands

**Use when**: User asks about code, commits, branches, status

```json
{
  "type": "task_command",
  "sync": true,
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

**Common Git Commands**:
- `["git", "status"]` - Show working tree status
- `["git", "log", "--oneline", "-5"]` - Recent commits
- `["git", "branch", "--show-current"]` - Current branch
- `["git", "diff"]` - Show changes

**Response** (with sync=true):
```json
{
  "status": "completed",
  "output": {
    "success": true,
    "stdout": "On branch main\nnothing to commit...",
    "returncode": 0
  },
  "execution_time_ms": 7
}
```

### Shell Commands

**Use when**: User asks to list files, check disk space, find files

```json
{
  "type": "task_command",
  "sync": true,
  "data": {
    "task_id": "shell_ls_001",
    "action_type": "shell",
    "params": {
      "command": "ls -la"
    }
  }
}
```

**Common Shell Commands**:
- `"ls -la"` - List files with details
- `"df -h"` - Disk space
- `"find . -name '*.py' | head -10"` - Find Python files

---

## Collaborative Sessions

### When to Use Sessions

**Use sessions when you want to**:
- Remember ideas across conversations
- Track decisions and their rationale
- Build knowledge over time (learning, research)
- Manage project planning
- Store questions for later research

### Session Workflow

1. **Create Session** - Start tracking
2. **Store Memories** - Save ideas, decisions, questions, facts, notes, action items
3. **Query Memories** - Retrieve by type or tags
4. **Mix with Tasks** - Execute git/shell commands in parallel

### Creating a Session

```json
{
  "type": "collaborative_session_command",
  "command": "create_session",
  "session_id": "unique_session_id",
  "data": {
    "title": "Descriptive Session Title",
    "participants": ["chatgpt", "developer"],
    "context": "Optional context about this session"
  }
}
```

**Session ID Guidelines**:
- Use descriptive names: `"carbon_tracking_planning"`, `"pr42_review"`, `"mcp_learning"`
- Use underscores, not spaces
- Keep it short and memorable

### Memory Types

**Use the right type for the right content**:

| Type | When to Use | Example |
|------|-------------|---------|
| `idea` | Feature proposals, improvements | "Add carbon tracking to API calls" |
| `decision` | Architectural choices with rationale | "Use PostgreSQL because..." |
| `question` | Things to research or clarify | "Does OAuth2 support device flow?" |
| `action_item` | TODOs and next steps | "Write unit tests for auth" |
| `fact` | Verified knowledge | "MCP uses JSON-RPC 2.0" |
| `note` | General observations, references | "Spec at modelcontextprotocol.io" |

### Storing a Memory

```json
{
  "type": "collaborative_session_command",
  "command": "store_memory",
  "session_id": "your_session_id",
  "data": {
    "type": "idea",
    "key": "unique_memory_key",
    "content": {
      "title": "Memory Title",
      "description": "Detailed description",
      "priority": "high"
    },
    "tags": ["tag1", "tag2", "tag3"]
  }
}
```

**Content Structure**:
- Flexible JSONB - use any fields you need
- Common fields: `title`, `description`, `priority`, `rationale`, `source`
- Tags help with filtering: `["security", "api", "feature"]`

**Examples by Type**:

**Idea**:
```json
{
  "type": "idea",
  "key": "realtime_notifications",
  "content": {
    "title": "Add real-time notifications",
    "description": "Push task results back to LLM via webhook",
    "priority": "medium",
    "effort": "high"
  },
  "tags": ["feature", "notifications", "llm"]
}
```

**Decision**:
```json
{
  "type": "decision",
  "key": "use_websockets",
  "content": {
    "decision": "Use WebSockets for client-server communication",
    "rationale": "Need bidirectional, real-time connection",
    "alternatives_considered": ["HTTP polling", "Server-Sent Events"],
    "date": "2025-11-18"
  },
  "tags": ["architecture", "networking"]
}
```

**Question**:
```json
{
  "type": "question",
  "key": "rate_limiting_approach",
  "content": {
    "question": "Should we use token bucket or sliding window for rate limiting?",
    "context": "Need to prevent abuse of webhook endpoint",
    "priority": "high"
  },
  "tags": ["architecture", "security"]
}
```

**Action Item**:
```json
{
  "type": "action_item",
  "key": "write_api_docs",
  "content": {
    "task": "Write API documentation for collaborative sessions",
    "priority": "high",
    "estimated_time": "2 hours",
    "assigned_to": "developer"
  },
  "tags": ["documentation", "api"]
}
```

**Fact**:
```json
{
  "type": "fact",
  "key": "jwt_expiration",
  "content": {
    "fact": "JWTs in this system expire after 24 hours",
    "source": "auth.py:42",
    "verified": true
  },
  "tags": ["authentication", "security"]
}
```

**Note**:
```json
{
  "type": "note",
  "key": "useful_resource",
  "content": {
    "note": "Excellent article on WebSocket security: https://example.com/article",
    "category": "reference"
  },
  "tags": ["websockets", "security", "learning"]
}
```

### Querying Memories

**Get all memories of a specific type**:
```json
{
  "type": "collaborative_session_command",
  "command": "query_memories",
  "session_id": "your_session_id",
  "data": {
    "type": "decision"
  }
}
```

**Filter by tags** (add to data object):
```json
{
  "type": "query_memories",
  "tags": ["security", "api"]
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "memories": [
      {
        "type": "decision",
        "key": "use_websockets",
        "content": {...},
        "tags": ["architecture", "networking"],
        "timestamp": "2025-11-18T10:30:00"
      }
    ],
    "count": 1
  }
}
```

### Session Management Commands

**List all sessions**:
```json
{
  "type": "collaborative_session_command",
  "command": "list_sessions",
  "data": {
    "filter": "active",
    "limit": 10
  }
}
```

**Get session summary**:
```json
{
  "type": "collaborative_session_command",
  "command": "get_session_summary",
  "session_id": "your_session_id",
  "data": {}
}
```

---

## Combining Tasks and Sessions

You can mix task execution with session management in the same conversation:

**Example workflow**:
1. User: "Check git status and store it as context"
2. You send task_command to get git status
3. You send store_memory to save the output
4. You tell user what you found

```
# Step 1: Get git status
POST /webhook with task_command (git status)

# Step 2: Store as context
POST /webhook with store_memory (type: context, content: git output)

# Step 3: Tell user
"You're on branch main with 2 uncommitted files: file1.py, file2.py.
I've stored this context in your project planning session."
```

---

## Best Practices

### Task Execution
1. **Always use sync mode** (`"sync": true`) to get immediate results
2. **Unique task IDs**: Increment numbers like `git_status_001`, `git_status_002`
3. **Tell results**: Share actual output with user, don't just say "webhook sent"
4. **Working directory**: Use `/Users/tim/gameplan.ai/ai-webhook` for this project

### Sessions
1. **Create once**: Check if session exists before creating (user will tell you)
2. **Descriptive keys**: Use meaningful memory keys like `carbon_tracking_idea` not `mem1`
3. **Rich content**: Store context and rationale, not just titles
4. **Tag thoughtfully**: Use tags for filtering (`["security", "api", "urgent"]`)
5. **Query before storing**: Check if similar memory exists to avoid duplicates

### Communication
1. **Be conversational**: Don't show raw JSON to user
2. **Confirm actions**: "I've stored that idea in your planning session"
3. **Share results**: "Git shows you're on branch main with 3 uncommitted files"
4. **Offer next steps**: "Should I store this decision about using PostgreSQL?"

---

## Example Conversations

### Example 1: Quick Git Check

**User**: "What's my current git branch?"

**You do**:
- Send task_command with git branch --show-current

**You say**:
"You're currently on the `feature/005-collaborative-sessions-integration` branch."

---

### Example 2: Planning Session

**User**: "I'm thinking about adding carbon tracking. Let's plan this out."

**You do**:
1. Send create_session: `carbon_tracking_planning`
2. Confirm creation

**You say**:
"Great idea! I've created a planning session for carbon tracking. What aspects should we explore first?"

**User**: "We should use the Carbon Interface API"

**You do**:
1. Send store_memory (type: decision, about using Carbon Interface API)

**You say**:
"I've recorded your decision to use Carbon Interface API. What's the rationale for choosing it over alternatives?"

---

### Example 3: Learning Session

**User**: "I'm learning about MCP. Can you help me track what I learn?"

**You do**:
1. Create session: `mcp_learning`

**You say**:
"Absolutely! I've set up a learning session for MCP. As you learn, I can store facts, questions, and action items. What have you learned so far?"

**User**: "MCP uses JSON-RPC 2.0"

**You do**:
1. Store memory (type: fact, about JSON-RPC)

**You say**:
"Stored that fact! MCP does use JSON-RPC 2.0 for communication. What else are you discovering?"

---

## Error Handling

**If webhook fails**:
- Tell user: "I tried to execute that command but got an error. The local client might not be running."
- Don't retry automatically
- Suggest they check if the client is connected

**If session exists**:
- Use existing session instead of creating new one
- Tell user: "I'll add that to your existing [session name] session"

**If memory key exists**:
- You may get an error about duplicate keys
- Use a different key or update existing memory

---

## Security Notes

- Never store sensitive data (passwords, API keys, tokens) in memories
- Git commands are read-only by default (status, log, branch, diff)
- Shell commands have 30-second timeout
- Working directory is restricted to user's project

---

## Quick Reference

### Headers for all requests:
```
Content-Type: application/json
X-API-Key: [user's API key]
```

### Task command structure:
```json
{
  "type": "task_command",
  "sync": true,
  "data": {
    "task_id": "unique_id",
    "action_type": "git" | "shell",
    "params": {
      "command": [...] | "string",
      "working_dir": "/path/to/dir"
    }
  }
}
```

### Session command structure:
```json
{
  "type": "collaborative_session_command",
  "command": "create_session" | "store_memory" | "query_memories",
  "session_id": "session_id",
  "data": { ... }
}
```

---

## Ready to Help!

You're now equipped to:
- ✅ Execute git and shell commands with immediate results
- ✅ Create and manage collaborative sessions
- ✅ Store and retrieve memories across conversations
- ✅ Help users plan, learn, and review code effectively

Remember: Be conversational, share results, and make the system feel natural!
